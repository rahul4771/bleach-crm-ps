from django.shortcuts import render
from .models import Order
from datetime import datetime,date,timedelta
from django.http import JsonResponse
import pandas as pd
from django.db.models.functions import TruncMonth as Month, TruncYear as Year
from django.db.models import Count
# Create your views here.

def quotation_data(request):
    data = []
    dom = request.GET.get('dom',None)
    prevdate  = request.GET.get('fromdate', None)
    todate  = request.GET.get('todate', None)
    print(prevdate,todate,"pop")
    
    if dom == 'Month':
        print("kabir")
        month,year = prevdate.split("/")
        month2,year2 = todate.split("/")
        
        quotations = Order.objects.filter(is_active=True,evaluation__quatation_approved_date__year__range=(year,year2), evaluation__quatation_approved_date__month__range=(month,month2)).values('evaluation__quatation_approved_date').annotate(month=Month('evaluation__quatation_approved_date'),).values('month').annotate(count=Count('pk'))

        for qt in quotations:
            quotations_approved = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__year__range=(year,year2), evaluation__quatation_approved_date__month__range=(month,month2)).values('evaluation__quatation_approved_date').annotate(month=Month('evaluation__quatation_approved_date'),).values('month').annotate(count=Count('pk'))
            print(quotations_approved,"huuh")

            quotations22 = Order.objects.filter(is_active=True,evaluation__quatation_approved_date__year__range=(year,year2), evaluation__quatation_approved_date__month__range=(month,month2)).count()
            print(quotations22,"qt22")

            approved_count = 0
            for qts in quotations_approved:
                if qts['month'] == qt['month']:
                    approved_count = qts['count']

            qt_dict = {
            "date" : qt['month'],
            "submitted_qt" : qt['count'],
            "approved_qt" : approved_count,
            "qt22" :quotations22
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
            sdate = single_date.strftime("%Y-%m-%d")
            submitted_qtns = Order.objects.filter(is_active=True,evaluation__quatation_approved_date__date=sdate).count()
            approved_qtns = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__date=sdate).count()
            print(sdate,submitted_qtns,approved_qtns,"qtc")
            qt_dict = {
                "date" : sdate,
                "submitted_qt" : submitted_qtns,
                "approved_qt" : approved_qtns
            }
            data.append(qt_dict)
    return JsonResponse(data,safe=False)