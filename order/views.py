from django.shortcuts import render
from .models import Order
from datetime import datetime,date,timedelta
from django.http import JsonResponse
import pandas as pd
# Create your views here.

def quotation_data(request):
    data = []
    prevdate  = '17/06/2020' #request.GET.get('fromdate', None)
    todate  = '12/07/2020' #request.GET.get('todate', None)
    print(prevdate,todate,"pop")
    
    try:
        prevdate = datetime.strptime(prevdate, '%d/%m/%Y')
        todate = datetime.strptime(todate, '%d/%m/%Y')
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