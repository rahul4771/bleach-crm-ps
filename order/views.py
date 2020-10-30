from django.shortcuts import render
from .models import Order
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook
from datetime import datetime,date,timedelta,timezone
from django.http import JsonResponse
import pandas as pd
#from django.db.models.functions import TruncMonth as Month, TruncYear as Year
from django.db.models import Count
# from django.db.models.functions import Extract
from dateutil.relativedelta import relativedelta
import requests
# Create your views here.

def quotation_data(request):
    data = []
    dom = request.GET.get('dom',None)
    prevdate  = request.GET.get('fromdate', None)
    todate  = request.GET.get('todate', None)
    print(prevdate,todate,"pop")
    
    if dom == 'Month':
        month,year = prevdate.split("/")
        month2,year2 = todate.split("/")

        monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
        monthdate2 = datetime(day=1,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
        print(monthdate1,monthdate2,"mod")

        quotes = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,created__range=(monthdate1,monthdate2))
        quotations = quotes.dates('created','month').distinct() #.values('created').annotate(month=Month('created')).values('month').annotate(count=Count('pk'))

        for month in quotations:
            month_start = datetime(day=1,month=month.month,year=month.year,hour=0,minute=0,second=0,microsecond=0)
            month_end = datetime(day=1,month=month.month,year=month.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
            submitted_quotes = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,created__range=(month_start,month_end)).count()
            approved_quotes = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(month_start,month_end)).count()
            # submitted_total = submitted_quotes.aggregate(total=Count("pk")).get("total")
            # approved_total = approved_quotes.aggregate(total2=Count("pk")).get("total2")
            print(month.month, submitted_quotes, approved_quotes,'dats')
            qt_dict = {
            "date" : month.month,
            "submitted_qt" : submitted_quotes,
            "approved_qt" : approved_quotes
            }
            data.append(qt_dict)

    else:
        print("kab")
        try:
            prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
            todate = datetime.strptime(todate, '%Y-%m-%d')
        except:
            todate = date.today() - timedelta(days=1)
            prevdate = todate - timedelta(days=30)
        print(prevdate,todate,"testdt")
        daterange = pd.date_range(prevdate, todate)

        for single_date in daterange:
            quotation_date_start  = single_date.replace(hour=0,minute=0,second=0,microsecond=0)
            quotation_date_end    = single_date+timedelta(1)	
            
            submitted_qtns = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,created__range=(quotation_date_start,quotation_date_end)).count()
            approved_qtns = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(quotation_date_start,quotation_date_end)).count()
            print(submitted_qtns,approved_qtns,"qtc")

            qt_dict = {
                "date" : single_date,
                "submitted_qt" : submitted_qtns,
                "approved_qt" : approved_qtns
            }
            data.append(qt_dict)

    return JsonResponse(data,safe=False)

def sendinvoice(request):
    order_no = request.GET.get('order_no')
    order = Order.objects.filter(order_no=order_no).first()

    language = order.evaluation.customer.sms_preference

    evaluation = order.evaluation

    url = "https://smsapi.future-club.com/fccsms.aspx"

    print("kaboonm",url)

    if language == 'ENGLISH':

        message = "Dear Customer, Please find the Invoice against the order number "+str(evaluation.evaluation_id)+"  here http://127.0.0.1:8000/customer/invoice/"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on [Customer Service Number]. Thank you for choosing Bleach Kuwait."

        querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"918848953520","M":message,"IID":"1468","L":"L"}
    
    else:

        message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط http://127.0.0.1:8000/customer/invoice/"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على (Customer Service Number).  شكراً لاختياركم بليتش لخدمات التنظيف"

        querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"918848953520","M":message,"IID":"1468","L":"A"}
    
    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(message,"respo")
    print(response.text,"respo")
    print(response.url,"respo")
    print(order_no)
    data=True
    return JsonResponse(data,safe=False)

def sendquotation(request):
    order_no = request.GET.get('order_no')
    order = Order.objects.filter(order_no=order_no).first()

    language = order.evaluation.customer.sms_preference

    evaluation = order.evaluation

    evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
    evaluationbook = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).first()

    url = "https://smsapi.future-club.com/fccsms.aspx"

    if language == 'ENGLISH':
        print(str(evaluation.id),str(evaluation.evaluation_id),str(evaluation.total_cost),str(evaluation.quatation_expiry_date),str(evaluation.customer.username),str(evaluation.tracking_no),"trerr")

        message = "Dear Customer, Please find the Quotation against the cleaning at "+evaluationdetails.address.apartment+","+evaluationdetails.address.floor+","+evaluationdetails.address.street+","+evaluationdetails.address.building+","+evaluationdetails.address.avenue+","+evaluationdetails.address.block+","+evaluationdetails.address.area.name+","+evaluationdetails.address.governorate.name+" here http://127.0.0.1:8000/customer/quatation/"+str(evaluation.id)+" Order Number : "+str(evaluation.evaluation_id)+" Service Type(s) : "+evaluationbook.service_type.name+" Address(s) : "+evaluationdetails.address.apartment+","+evaluationdetails.address.floor+","+evaluationdetails.address.street+","+evaluationdetails.address.building+","+evaluationdetails.address.avenue+","+evaluationdetails.address.block+","+evaluationdetails.address.area.name+","+evaluationdetails.address.governorate.name+" Cost : "+ str(evaluation.total_cost) +" KD Due Date : "+ str(evaluation.quatation_expiry_date) +" For any assistance please contact us on 996545845. Thank you for choosing Bleach Kuwait"

        querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"918848953520","M":message,"IID":"1468","L":"L"}
    
    else:
        message = "عزيزنا العميل نرجوا الاطلاع على عرض سعر خدمات التنظيف المطلوبة في "+evaluationdetails.address.apartment+","+evaluationdetails.address.floor+","+evaluationdetails.address.street+","+evaluationdetails.address.building+","+evaluationdetails.address.avenue+","+evaluationdetails.address.block+","+evaluationdetails.address.area.name+","+evaluationdetails.address.governorate.name+" في هذا الرابط http://127.0.0.1:8000/customer/quatation/"+str(evaluation.id)+". رقم الطلب: "+str(evaluation.evaluation_id)+" الخدمة: "+evaluationbook.service_type.name+" العنوان: "+evaluationdetails.address.apartment+","+evaluationdetails.address.floor+","+evaluationdetails.address.street+","+evaluationdetails.address.building+","+evaluationdetails.address.avenue+","+evaluationdetails.address.block+","+evaluationdetails.address.area.name+","+evaluationdetails.address.governorate.name+" السعر: "+ str(evaluation.total_cost) +" KD تاريخ الخدمة: "+ str(evaluation.quatation_expiry_date) +" لأي استفسارات يمكنكم التواصل معنا على (Customer Service Number).  شكراً لاختياركم بليتش لخدمات التنظيف"

        querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"918848953520","M":message,"IID":"1468","L":"A"}

    headers = {
        'cache-control': "no-cache"
    }
    
    response = requests.request("GET", url, headers=headers, params=querystring)

    print(message,"respo")
    print(order_no)
    data=True
    return JsonResponse(data,safe=False)