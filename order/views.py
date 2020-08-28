from django.shortcuts import render
from .models import Order
from datetime import datetime,date,timedelta
from django.http import JsonResponse
import pandas as pd
# Create your views here.

def quotation_data(request):
    data = []
    dom = request.GET.get('dom', None)
    prevdate  = request.GET.get('fromdate', None)
    todate  = request.GET.get('todate', None)
    print(dom,prevdate,todate,"pop")
    if dom == 'Month':
        print("kabir")
        month,year = prevdate.split("/")
        month2,year2 = todate.split("/")
        
        quotations = Order.objects.filter(evaluation__quatation_approved_date__year__gte=year, 
                              evaluation__quatation_approved_date__month__gte=month,
                              evaluation__quatation_approved_date__year__lte=year2,
                              evaluation__quatation_approved_date__month__lte=month2).values('evaluation__quatation_approved_date').distinct().order_by('evaluation__quatation_approved_date')
        
        for qt in quotations:
            submitted_qtns = Order.objects.filter(evaluation__quatation_approved_date=qt['evaluation__quatation_approved_date']).count()
            approved_qtns = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date=qt['evaluation__quatation_approved_date']).count()
            print(submitted_qtns,approved_qtns,"huy")
            qt_dict = {
            "date" : qt['evaluation__quatation_approved_date'],
            "sub_qt" : submitted_qtns,
            "app_qt" : approved_qtns
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
            submitted_qtns = Order.objects.filter(evaluation__quatation_approved_date=sdate).count()
            approved_qtns = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date=sdate).count()
            print(sdate,submitted_qtns,approved_qtns,"qtc")
            qt_dict = {
                "date" : sdate,
                "sub_qt" : submitted_qtns,
                "app_qt" : approved_qtns
            }
            data.append(qt_dict)
    return JsonResponse(data,safe=False)