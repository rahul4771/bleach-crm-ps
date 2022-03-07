from django.core.management.base import BaseCommand

from django.utils import timezone
from datetime import timedelta,date,datetime
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch

import requests
import json

from order.models import OrderScheduler,Order
from Api.models import XeroConnection
from evaluator.models import EvaluationDetails,EvaluationBook
from accountant.models import PaymentHistory
from user.models import UserProfile

class Command(BaseCommand):
    help = 'Automatic Updations'

    def handle(self, *args, **kwargs): 
        transaction_start_date      = datetime.strptime("01-01-2022","%d-%m-%Y").date()
        PaymentHistory.objects.select_related('order__evaluation__customer').filter(paid_date__date__gte=transaction_start_date).update(is_xero_marked=False)
        UserProfile.objects.all().update(xero_account_id='')
        # schedule_start_date     = datetime.strptime("01-01-2022","%d-%m-%Y").date()
        # orders_ids              = list(OrderScheduler.objects.select_related('order').filter(Q(Q(start_at__date__gte=schedule_start_date)|Q(end_at__date__gte=schedule_start_date))).values_list('order__id',flat=True))
        # orders                  = Order.objects.filter(id__in=orders_ids).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(Q(Q(start_at__date__gte=schedule_start_date)|Q(end_at__date__gte=schedule_start_date))&Q(is_xero_marked=False)).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(customerbooking=Sum(Case(When(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING',then=1),default=0,output_field=IntegerField())))
        
        # for order in orders:
        #     total_cleanings            = len(order.orderschedules)
            
        #     cleaning_cost_sum          = 0
        #     discount_cost_sum          = 0
        #     additional_charge_cost_sum = 0
        #     count                      = 0
        #     if order.orderschedules:
        #         for scheduler in order.orderschedules:
        #             count                                += 1

        #             #service cost update
        #             if count == len(scheduler.order_scheduler_book.bookschedules):
        #                 scheduler.cleaning_cost           = round(scheduler.order_scheduler_book.total_cost-cleaning_cost_sum,2)
        #                 cleaning_cost_sum                 = 0
        #             else:
        #                 scheduler.cleaning_cost           = round(scheduler.order_scheduler_book.total_cost/len(scheduler.order_scheduler_book.bookschedules),2)
        #                 cleaning_cost_sum                += scheduler.cleaning_cost
        #             #discount and additional cost update	
        #             if total_cleanings != count:
        #                 scheduler.discount_cost           = round(order.evaluation.discount/total_cleanings,2)
        #                 scheduler.additional_charge_cost  = round(order.evaluation.additional_charge/total_cleanings,2)
        #                 discount_cost_sum                += scheduler.discount_cost
        #                 additional_charge_cost_sum       += scheduler.additional_charge_cost
        #             else:	
        #                 scheduler.discount_cost           = round(order.evaluation.discount-discount_cost_sum,2)
        #                 scheduler.additional_charge_cost  = round(order.evaluation.additional_charge-additional_charge_cost_sum,2)

        #             scheduler.save()

        #             if scheduler.work_status == 'CLEANING_FULFILLED':
        #                 #Xero Integration
        #                 xero                        = XeroConnection.objects.first()
        #                 ##xero Update Access Token and Refresh Token
        #                 header                      = {
        #                                                 'Authorization': 'Basic '+xero.client_encoded,
        #                                                 'Content-Type': 'application/x-www-form-urlencoded'
        #                                                     }
        #                 body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
        #                 token_response              = requests.post('https://identity.xero.com/connect/token',
        #                                                         data=body,
        #                                                         headers=header 
        #                                                     ).json()
        #                 access_token                = token_response['access_token']
        #                 refresh_token               = token_response['refresh_token']

        #                 xero.access_token  = access_token
        #                 xero.refresh_token = refresh_token
        #                 xero.save()

        #                 ##Xero Contact
        #                 if not order.evaluation.customer.xero_account_id:
        #                     ##Xero Create Customer ID and Save
        #                     contact_data                = {
        #                                                     "Name":order.evaluation.customer.name,
        #                                                     "ContactNumber":order.evaluation.customer.mobile_number,
        #                                                     "EmailAddress":order.evaluation.customer.email,
        #                                                     "ContactStatus":"ACTIVE",
        #                                                     "IsCustomer":True,
        #                                                     "DefaultCurrency":"KWD"
        #                                                                 }
                                                            
        #                     header                      = {
        #                                                 'xero-tenant-id': xero.tenant_id,
        #                                                 'Authorization': 'Bearer '+access_token,
        #                                                 'Accept': 'application/json',
        #                                                 'Content-Type': 'application/json'
        #                                                     }

        #                     create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
        #                                                             json=contact_data,
        #                                                             headers=header 
        #                                                         ).json()

        #                     order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
        #                     order.evaluation.customer.save()

                        
        #                 ##Invoice Data
        #                 order_evaluation_books    = EvaluationBook.objects.filter(evaluation_details__evaluation=scheduler.order.evaluation)
        #                 evaluation_book_schedules = OrderScheduler.objects.filter(order_scheduler_book=scheduler.order_scheduler_book)
        #                 book_no                   = 0
        #                 cleaning_no               = 0
        #                 for order_evaluation_book in order_evaluation_books:
        #                     book_no     += 1
        #                     if order_evaluation_book == scheduler.order_scheduler_book:
        #                         break
        #                 for evaluation_book_schedule in evaluation_book_schedules:
        #                     cleaning_no += 1
        #                     if evaluation_book_schedule == scheduler:
        #                         break
        #                 InvoiceNumber               = str(order.invoice_no)+'-'+str(book_no)+'V'+str(cleaning_no)
                                
        #                 invoice_data                = 	{
        #                                                 "Type":"ACCREC",
        #                                                 "Contact":{
        #                                                     "ContactID":order.evaluation.customer.xero_account_id
        #                                                 },
        #                                                 "Date":scheduler.start_at.strftime('%Y-%m-%d'),
        #                                                 "DueDate":scheduler.start_at.strftime('%Y-%m-%d'),
        #                                                 "LineAmountTypes":"NoTax",
        #                                                 "InvoiceNumber":InvoiceNumber,
        #                                                 "Reference":order.order_no,
        #                                                 "CurrencyCode":"KWD",
        #                                                 "Status":"AUTHORISED",
        #                                                 "LineItems":[
        #                                                     {
        #                                                         "Description":scheduler.order_scheduler_book.service_type.name,
        #                                                         "Quantity":"1",
        #                                                         "UnitAmount":scheduler.cleaning_cost,
        #                                                         "AccountCode":scheduler.order_scheduler_book.service_type.xero_account,
        #                                                         "TaxType":"NONE"
        #                                                     },
        #                                                     {
        #                                                         "Description":"Additional Charge",
        #                                                         "Quantity":"1",
        #                                                         "UnitAmount":scheduler.additional_charge_cost,
        #                                                         "AccountCode":scheduler.order_scheduler_book.service_type.xero_account,
        #                                                         "TaxType":"NONE"
        #                                                     },
        #                                                     {
        #                                                         "Description":"Discount",
        #                                                         "Quantity":"1",
        #                                                         "UnitAmount":-scheduler.discount_cost,
        #                                                         "AccountCode":scheduler.order_scheduler_book.service_type.xero_account,
        #                                                         "TaxType":"NONE"
        #                                                     }
        #                                                 ]
        #                                                 }

        #                 ##xero Create Invoice
        #                 header                      = {
        #                                                 'xero-tenant-id': xero.tenant_id,
        #                                                 'Authorization': 'Bearer '+access_token,
        #                                                 'Accept': 'application/json',
        #                                                 'Content-Type': 'application/json'
        #                                                     }

        #                 create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
        #                                                         json=invoice_data,
        #                                                         headers=header 
        #                                                     )
        #                 print(scheduler)
        #                 print(scheduler.start_at.strftime('%Y-%m-%d'))
        #                 print(create_invoice.json())
                    
                    # scheduler.is_xero_marked = True
                    # scheduler.save()

        