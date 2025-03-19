from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Order,OrderScheduler,EvaluationBook
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionAddons
from datetime import datetime,date,timedelta,timezone
from django.http import JsonResponse
import pandas as pd
#from django.db.models.functions import TruncMonth as Month, TruncYear as Year
from django.db.models import Count
# from django.db.models.functions import Extract
from dateutil.relativedelta import relativedelta
import requests
from django.core.mail import send_mail,EmailMultiAlternatives
from accountant.models import PaymentHistory
from django.db.models import Prefetch
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
# Create your views here.

# def quotation_data(request):
#     data = []
#     dom = request.GET.get('dom',None)
#     prevdate  = request.GET.get('fromdate', None)
#     todate  = request.GET.get('todate', None)
#     print(prevdate,todate,"pop")
    
#     if dom == 'Month':
#         month,year = prevdate.split("/")
#         month2,year2 = todate.split("/")

#         monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
#         monthdate2 = datetime(day=1,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
#         print(monthdate1,monthdate2,"mod")

#         quotes = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,created__range=(monthdate1,monthdate2))
#         quotations = quotes.dates('created','month').distinct() #.values('created').annotate(month=Month('created')).values('month').annotate(count=Count('pk'))

#         for month in quotations:
#             month_start = datetime(day=1,month=month.month,year=month.year,hour=0,minute=0,second=0,microsecond=0)
#             month_end = datetime(day=1,month=month.month,year=month.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
#             submitted_quotes = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,created__range=(month_start,month_end)).count()
#             approved_quotes = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(month_start,month_end)).count()
#             # submitted_total = submitted_quotes.aggregate(total=Count("pk")).get("total")
#             # approved_total = approved_quotes.aggregate(total2=Count("pk")).get("total2")
#             print(month.month, submitted_quotes, approved_quotes,'dats')
#             qt_dict = {
#             "date" : month.month,
#             "submitted_qt" : submitted_quotes,
#             "approved_qt" : approved_quotes
#             }
#             data.append(qt_dict)

#     else:
#         print("kab")
#         try:
#             prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
#             todate = datetime.strptime(todate, '%Y-%m-%d')
#         except:
#             todate = date.today() - timedelta(days=1)
#             prevdate = todate - timedelta(days=30)
#         print(prevdate,todate,"testdt")
#         daterange = pd.date_range(prevdate, todate)

#         for single_date in daterange:
#             quotation_date_start  = single_date.replace(hour=0,minute=0,second=0,microsecond=0)
#             quotation_date_end    = single_date+timedelta(1)	
            
#             submitted_qtns = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,created__range=(quotation_date_start,quotation_date_end)).count()
#             approved_qtns = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(quotation_date_start,quotation_date_end)).count()
#             print(submitted_qtns,approved_qtns,"qtc")

#             qt_dict = {
#                 "date" : single_date,
#                 "submitted_qt" : submitted_qtns,
#                 "approved_qt" : approved_qtns
#             }
#             data.append(qt_dict)

#     return JsonResponse(data,safe=False)

def quotation_data(request):
    data = []
    dom = request.GET.get('dom', None)
    prevdate = request.GET.get('fromdate', None)
    todate = request.GET.get('todate', None)
   
    if dom == 'Month':
        month, year = prevdate.split("/")
        month2, year2 = todate.split("/")
 
        monthdate1 = datetime(day=1, month=int(month), year=int(year), hour=0, minute=0, second=0, microsecond=0)
        monthdate2 = datetime(day=1, month=int(month2), year=int(year2), hour=0, minute=0, second=0, microsecond=0) + relativedelta(months=1)
 
        quotes = Order.objects.filter(is_active=True, evaluation__quatation_status__isnull=False, created__range=(monthdate1, monthdate2))
        quotations = quotes.dates('created', 'month').distinct()
 
        for month in quotations:
            month_start = datetime(day=1, month=month.month, year=month.year, hour=0, minute=0, second=0, microsecond=0)
            month_end = datetime(day=1, month=month.month, year=month.year, hour=0, minute=0, second=0, microsecond=0) + relativedelta(months=1)
           
            submitted_quotes = quotes.filter(created__range=(month_start, month_end)).count()
            approved_quotes = quotes.filter(evaluation__quatation_status='APPROVED', created__range=(month_start, month_end)).count()
 
            qt_dict = {
                "date": month.month,
                "submitted_qt": submitted_quotes,
                "approved_qt": approved_quotes
            }
            data.append(qt_dict)
 
    else:
        try:
            prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
            todate = datetime.strptime(todate, '%Y-%m-%d')
        except:
            todate = date.today() - timedelta(days=1)
            prevdate = todate - timedelta(days=30)
 
        daterange = pd.date_range(prevdate, todate)
 
        # Fetch all relevant orders in a single query
        orders = Order.objects.filter(is_active=True, evaluation__quatation_status__isnull=False, created__range=(prevdate, todate + timedelta(days=1)))
        orders_approved = orders.filter(evaluation__quatation_status='APPROVED')
 
        for single_date in daterange:
            quotation_date_start = single_date.replace(hour=0, minute=0, second=0, microsecond=0)
            quotation_date_end = single_date + timedelta(1)
           
            submitted_qtns = orders.filter(created__range=(quotation_date_start, quotation_date_end)).count()
            approved_qtns = orders_approved.filter(created__range=(quotation_date_start, quotation_date_end)).count()
 
            qt_dict = {
                "date": single_date,
                "submitted_qt": submitted_qtns,
                "approved_qt": approved_qtns
            }
            data.append(qt_dict)
 
    return JsonResponse(data, safe=False)
#for onetime , subscription based charts
def quotation_data_policy(request):
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

        orderschedules = OrderScheduler.objects.filter(is_active=True,start_at__range=(monthdate1,monthdate2))
        schedules = orderschedules.dates('start_at','month').distinct() #.values('created').annotate(month=Month('created')).values('month').annotate(count=Count('pk'))

        for month in schedules:
            month_start = datetime(day=1,month=month.month,year=month.year,hour=0,minute=0,second=0,microsecond=0)
            month_end = datetime(day=1,month=month.month,year=month.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
            onetimeservices = OrderScheduler.objects.filter(is_active=True,order_scheduler_book__cleaning_policy='ONE TIME SERVICE',work_status='CLEANING_FULFILLED',start_at__range=(month_start,month_end)).count()
            subscriptions = OrderScheduler.objects.filter(is_active=True,order_scheduler_book__cleaning_policy='SUBSCRIPTION',work_status='CLEANING_FULFILLED',start_at__range=(month_start,month_end)).count()
            
            print(month.month, onetimeservices, subscriptions,'dats')
            qt_dict = {
            "date" : month.month,
            "onetime_qt" : onetimeservices,
            "subscription_qt" : subscriptions
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
            
            onetime_qtns = OrderScheduler.objects.filter(is_active=True,order_scheduler_book__cleaning_policy='ONE TIME SERVICE',work_status='CLEANING_FULFILLED',start_at__range=(quotation_date_start,quotation_date_end)).count()
            subscription_qtns = OrderScheduler.objects.filter(is_active=True,order_scheduler_book__cleaning_policy='SUBSCRIPTION',work_status='CLEANING_FULFILLED',start_at__range=(quotation_date_start,quotation_date_end)).count()
            print(onetime_qtns,subscription_qtns,"qtc")

            qt_dict = {
                "date" : single_date,
                "onetime_qt" : onetime_qtns,
                "subscription_qt" : subscription_qtns
            }
            data.append(qt_dict)

    return JsonResponse(data,safe=False)


def sendinvoice(request):
    order_no = request.GET.get('order_no')
    order = Order.objects.filter(order_no=order_no).annotate(customerbooking=Sum(Case(When(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING',then=1),default=0,output_field=IntegerField()))).first()

    selected_options = request.GET.get('selected_options')
    print(selected_options,"opr")
    options = selected_options.split(",")

    language = order.evaluation.customer.sms_preference

    evaluation = order.evaluation

    evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
    
    address = evaluationdetails.address

    evaluationbooks = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections'))
    evaluationbook = evaluationbooks.first()

    if address.floor == None and address.avenue == None:
        address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
    
    elif address.floor == None:
        address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
    
    elif address.avenue == None:
        address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
    
    else:
        address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

    separator = ", "

    data = False
    
    if evaluation.customer.is_sms == True or 'SMS' in options:

        url = "https://smsapi.future-club.com/fccsms.aspx"

        if language == 'ENGLISH':

            if evaluation.payment_method == 'SUBSCRIPTION':

                message = "Dear Customer, Please find the Invoice against the order number "+str(evaluation.evaluation_id)+"  here https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on [Customer Service Number]. Thank you for choosing Bleach Kuwait."

            else:

                message = "Dear Customer, Please find the Invoice against the order number "+str(evaluation.evaluation_id)+"  here https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on [Customer Service Number]. Thank you for choosing Bleach Kuwait."

            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
        
        else:
            if evaluation.payment_method == 'SUBSCRIPTION':

                message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على (Customer Service Number).  شكراً لاختياركم بليتش لخدمات التنظيف"

            else:

                message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على (Customer Service Number).  شكراً لاختياركم بليتش لخدمات التنظيف"

            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
        
        headers = {
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        print(message,response.text,"respo")
        print(order_no)
        data=True
    

    if evaluation.customer.is_email == True or 'EMAIL' in options:
        #send mail
        msg_html = render_to_string('email/invoice.html',{"invoice":order,"address_list":separator.join(address_list),"evaluationbooks":evaluationbooks})
        msg = EmailMultiAlternatives('Bleach Invoice', '', 'notification@bleach-kw.com', [evaluation.customer.email])
        msg.attach_alternative(msg_html, "text/html")
        msg.send(fail_silently=False)
        data=True
        

    return JsonResponse(data,safe=False)

def sendquotation(request):
    order_no = request.GET.get('order_no')
    order = Order.objects.filter(order_no=order_no).first()

    selected_options = request.GET.get('selected_options')
    print(selected_options,"opr")
    options = selected_options.split(",")

    print(options,"op")

    language = order.evaluation.customer.sms_preference

    evaluation = order.evaluation

    evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
    
    address = evaluationdetails.address

    if evaluationdetails.evaluator:
        evaluator = evaluationdetails.evaluator.name
    else:
        evaluator = evaluation.call_attender.name

    evaluationbooks = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections'))

    evaluationbook = evaluationbooks.first()

    if address.floor == None and address.avenue == None:
        address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
    
    elif address.floor == None:
        address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
    
    elif address.avenue == None:
        address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
    
    else:
        address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

    separator = ", "

    data = False

    if evaluation.customer.is_sms == True or 'SMS' in options:
    
        url = "https://smsapi.future-club.com/fccsms.aspx"

        if language == 'ENGLISH':
            # print(str(evaluation.id),str(evaluation.evaluation_id),str(evaluation.total_cost),str(evaluation.quatation_expiry_date),str(evaluation.customer.username),str(evaluation.tracking_no),"trerr")

            message = "Dear Customer, Please find the Quotation against the cleaning at "+separator.join(address_list)+" here https://my.bleachkw.com/customer/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"

            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
        
        else:
            message = "عزيزنا العميل نرجوا الاطلاع على عرض سعر خدمات التنظيف المطلوبة في "+separator.join(address_list)+" https://my.bleachkw.com/customer/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+"  لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"

            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

        headers = {
            'cache-control': "no-cache"
        }
        
        response = requests.request("GET", url, headers=headers, params=querystring)

        print(message,"respo")
        print(order_no)
        data=True

    if evaluation.customer.is_email == True or 'EMAIL' in options:
        #send mail
        msg_html = render_to_string('email/quatation.html',{"evaluator":evaluator,"evaluation":evaluation,"evaluationbooks":evaluationbooks,"address_list":separator.join(address_list)})
        msg = EmailMultiAlternatives('Bleach Quotation', '', 'notification@bleach-kw.com', [evaluation.customer.email])
        msg.attach_alternative(msg_html, "text/html")
        msg.send(fail_silently=False)
        print(msg,"msg")
        data=True
    
        

    return JsonResponse(data,safe=False)

def sendreceipt(request):
    order_no = request.GET.get('order_no')
    order = Order.objects.filter(order_no=order_no).first()

    language = order.evaluation.customer.sms_preference

    evaluation = order.evaluation

    payment_history = PaymentHistory.objects.filter(order=order).last()

    if payment_history != None and order.evaluation.customer.is_sms == True:

        url = "https://smsapi.future-club.com/fccsms.aspx"

        if order.evaluation.customer.sms_preference == 'ENGLISH':

            message = "Dear Customer, We have successfully received your payment of amount "+ str(payment_history.amount_paid) +" KD, (Transaction ID: "+ str(payment_history.transaction_id) +", Ref ID: "+ str(payment_history.ref) +") against the order number "+ str(order.order_no) +". Please find the Payment receipt here https://my.bleachkw.com/customer/payment/receipt/pvw"+ str(order.evaluation.tracking_no) +""+str(payment_history.id)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
        
        else:
            message = "عزيزي العميل، لقد تلقينا مدفوعاتك بنجاح مقابل رقم الطلب "+ order.order_no +". يرجى العثور على إيصال الدفع هنا https://my.bleachkw.com/customer/payment/receipt/pvw"+request.GET.get('paymentid')+". لأي مساعدة يرجى الاتصال بنا على9651882707 شكرا لاختيارك بليتش الكويت"


            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

        headers = {
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        print(response.text,"receipt")
        data=True
        
    else:
        data=False
    
    return JsonResponse(data,safe=False)

def sendfeedbacklink(request):
    order_no = request.GET.get('order_no')
    order = Order.objects.filter(order_no=order_no).first()

    language = order.evaluation.customer.sms_preference

    evaluation = order.evaluation

    if evaluation.customer.is_sms == True:

        url = "https://smsapi.future-club.com/fccsms.aspx"

        if evaluation.customer.sms_preference == 'ENGLISH':

            message = "Dear Customer, Thank you for choosing Bleach Kuwait. Kindly share your feedback for the order number "+ order.order_no +" here https://my.bleachkw.com/customer/feedback-page/"+str(order.id)+". For any assistance please contact us on +9651882707."
        
            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

        else:
            message = "عزيزينا العميل نرجوا أن تكون خدماتنا خازت على رضاكم و شكراً لاختياركم بليتش لخدمات التنظيف.  نرجوا التكرم بإنجاز الاستبيان الخاص بالطلب رقم "+ order.order_no +" https://my.bleachkw.com/customer/feedback-page/"+str(order.id)+" وذلك لضمان جودة الخدمة. لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"

            querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

        headers = {
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        data=True
        
    else:
        data=False
    
    return JsonResponse(data,safe=False)