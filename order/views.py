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
        monthdate1 = datetime(day=1,month=int(month),year=int(year))
        monthdate2 = datetime(day=28,month=int(month2),year=int(year2))

        quotations = Order.objects.filter(is_active=True,created__range=(monthdate1,monthdate2)).values('created').annotate(month=Month('created')).values('month').annotate(count=Count('pk'))

        for qt in quotations:
            quotations_approved = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(monthdate1,monthdate2)).values('evaluation__quatation_approved_date').annotate(month=Month('evaluation__quatation_approved_date')).values('month').annotate(count=Count('pk'))
            print(qt['month'],quotations_approved,"huuh") 

            approved_count = 0
            for qts in quotations_approved:
                print(qts['month'],"pop")
                if qts['month'] == qt['month']:
                    approved_count = qts['count']

            qt_dict = {
            "date" : qt['month'],
            "submitted_qt" : qt['count'],
            "approved_qt" : approved_count
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
            print(single_date,sdate,"date")
            submitted_qtns = Order.objects.filter(is_active=True,created__date=single_date).count()
            approved_qtns = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__date=single_date).count()
            print(sdate,submitted_qtns,approved_qtns,"qtc")
            qt_dict = {
                "date" : sdate,
                "submitted_qt" : submitted_qtns,
                "approved_qt" : approved_qtns
            }
            data.append(qt_dict)
    return JsonResponse(data,safe=False)