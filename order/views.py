from django.shortcuts import render
from .models import Order
from datetime import datetime,date,timedelta,timezone
from django.http import JsonResponse
import pandas as pd
#from django.db.models.functions import TruncMonth as Month, TruncYear as Year
from django.db.models import Count
from django.db.models.functions import Extract
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
        monthdate2 = datetime(day=28,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+timedelta(1)
        print(monthdate1,monthdate2,"mod")

        quotations = Order.objects.filter(is_active=True,created__range=(monthdate1,monthdate2)).annotate(month_stamp=Extract('created','month')).distinct().values_list('month_stamp',flat=True) #.values('created').annotate(month=Month('created')).values('month').annotate(count=Count('pk'))
        print(quotations,"poppp")
        # months = quotations.datetimes("created", kind="month")

        for month in quotations:
            submitted_quotes = Order.objects.filter(is_active=True,created__range=(monthdate1,monthdate2),created__month=month)
            approved_quotes = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(monthdate1,monthdate2),created__month=month)
            submitted_total = submitted_quotes.aggregate(total=Count("pk")).get("total")
            approved_total = approved_quotes.aggregate(total2=Count("pk")).get("total2")
            print(month, submitted_total, approved_total,'dats')
            qt_dict = {
            "date" : month,
            "submitted_qt" : submitted_total,
            "approved_qt" : approved_total
            }
            data.append(qt_dict)

        # for qt in quotations:
        #     quotations_approved = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(monthdate1,monthdate2)).values('created').annotate(month=Month('created')).values('month').annotate(count=Count('pk'))
        #     print(qt['month'],quotations_approved,"huuh") 

        #     approved_count = 0
        #     for qts in quotations_approved:
        #         print(qts['month'],"pop")
        #         if qts['month'] == qt['month']:
        #             approved_count = qts['count']

        #     qt_dict = {
        #     "date" : qt['month'],
        #     "submitted_qt" : qt['count'],
        #     "approved_qt" : approved_count
        #     }
        #     data.append(qt_dict)
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
            
            submitted_qtns = Order.objects.filter(is_active=True,created__range=(quotation_date_start,quotation_date_end)).count()
            approved_qtns = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(quotation_date_start,quotation_date_end)).count()
            print(submitted_qtns,approved_qtns,"qtc")

            qt_dict = {
                "date" : single_date,
                "submitted_qt" : submitted_qtns,
                "approved_qt" : approved_qtns
            }
            data.append(qt_dict)

    return JsonResponse(data,safe=False)