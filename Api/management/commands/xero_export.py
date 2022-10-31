import requests
import json
import xlwt
from django.core.management.base import BaseCommand
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from order.models import Order,OrderScheduler,XeroInvoice
from Api.models import XeroConnection
from accountant.models import PaymentHistory
from user.models import UserProfile

from django.utils import timezone
from datetime import timedelta,date,datetime

class Command(BaseCommand):
    help = 'xero export'

    def handle(self, *args, **kwargs):

        prevdate          = datetime.strptime("01-08-2022", '%d-%m-%Y')
        todate            = datetime.strptime("30-08-2022", '%d-%m-%Y')

        prev_date_start   = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
        prev_date_end     = prev_date_start+timedelta(1)
        todate_date_start = todate.replace(hour=0,minute=0,second=0,microsecond=0)   #single_date+timedelta(1)
        todate_date_end   = todate_date_start+timedelta(1)

        response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="System xeroInvoices.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('XeroInvoices')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','BLC','Invoice No.','Payment Policy','Paid Amount']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		xeroinvoices = XeoInvoice.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end),is_paid=True).values_list('paid_date','order__order_no', 'payment_policy','paid_amount').order_by('-id')

		xeroinvoices = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in xeroinvoices ]
	
		for row in xeroinvoices:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)

	    return response