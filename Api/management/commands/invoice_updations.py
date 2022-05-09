import requests
import json

from django.core.management.base import BaseCommand

from order.models import Order,OrderScheduler,XeroInvoice
from Api.models import XeroConnection
from accountant.models import PaymentHistory

from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch

class Command(BaseCommand):
    help = 'Automatic Updations'
    def handle(self, *args, **kwargs):
        #Xero Integration
        xero          = XeroConnection.objects.first()
        #Update Access Token and Refresh Token
        header                      = {
                                        'Authorization': 'Basic '+xero.client_encoded,
                                        'Content-Type': 'application/x-www-form-urlencoded'
                                            }
        body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
        token_response              = requests.post('https://identity.xero.com/connect/token',
                                                data=body,
                                                headers=header 
                                            ).json()
        access_token                = token_response['access_token']
        refresh_token               = token_response['refresh_token']

        xero.access_token  = access_token
        xero.refresh_token = refresh_token
        xero.save()

        header                      = {
                                        'xero-tenant-id': xero.tenant_id,
                                        'Authorization': 'Bearer '+access_token,
                                        'Accept': 'application/json',
                                        'Content-Type': 'application/json'
                                            }

        # #SUBSCRIPTION Invoices
        # subscriptions = Order.objects.select_related('evaluation__customer').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False,evaluation__payment_method='SUBSCRIPTION',payment_status='PENDING',subscription_topay__gt=0).exclude(order_status='ORDER_CANCELLED').filter(~Q(callback_status='LEGAL_ACTION'))
                
        # for subscription in subscriptions:
        #     ##Xero Contact
        #     if not subscription.evaluation.customer.xero_account_id:
        #         ##Xero Create Customer ID and Save
        #         contact_data                = {
        #                                         "Name":subscription.evaluation.customer.name,
        #                                         "ContactNumber":subscription.evaluation.customer.mobile_number,
        #                                         "EmailAddress":subscription.evaluation.customer.email,
        #                                         "ContactStatus":"ACTIVE",
        #                                         "IsCustomer":True,
        #                                         "DefaultCurrency":"KWD"
        #                                                     }
                                                
        #         header                      = {
        #                                     'xero-tenant-id': xero.tenant_id,
        #                                     'Authorization': 'Bearer '+access_token,
        #                                     'Accept': 'application/json',
        #                                     'Content-Type': 'application/json'
        #                                         }

        #         create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
        #                                                 json=contact_data,
        #                                                 headers=header 
        #                                             ).json()

        #         subscription.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
        #         subscription.evaluation.customer.save()

        #     Amount = subscription.evaluation.total_cost 
        #     ##Invoice Line Item 
        #     LineItems                 = []
        #     LineItems.append({
        #         "Description":"SUBSCRIPTION",
        #         "Quantity":"1",
        #         "UnitAmount":Amount,
        #         "AccountCode":1002,
        #         "TaxType":"NONE"
        #                     }
        #         )

        #     try:
        #         last_unpaid_invoice = XeroInvoice.objects.filter(is_paid=False,order=subscription).last()
        #     except:
        #         last_unpaid_invoice = None

        #     if last_unpaid_invoice:
        #         InvoiceNumber      = last_unpaid_invoice.invoice_no
        #     else:
        #         try:
        #             last_paid_invoice = XeroInvoice.objects.filter(is_paid=True,order=subscription).last()
        #         except:
        #             last_paid_invoice = None
                
        #         if last_paid_invoice:
        #             last_paid_invoice_no    = last_paid_invoice.invoice_no
        #             last_paid_invoice_no    = last_paid_invoice_no.replace(last_paid_invoice_no[len(last_paid_invoice_no) - 1:], chr(ord(last_paid_invoice_no[-1])+1))
        #             InvoiceNumber           = last_paid_invoice_no
        #         else:
        #             try:
        #                 payments_count          = PaymentHistory.objects.filter(order=subscription).count()
        #             except:
        #                 payments_count          = 0
        #             InvoiceNumber               = subscription.invoice_no+chr(ord('A')+payments_count)

        #     payment_policy            = 'SUBSCRIPTION'

        #     invoice_data              = 	{
        #                                             "Type":"ACCREC",
        #                                             "Contact":{
        #                                                 "ContactID":subscription.evaluation.customer.xero_account_id
        #                                             },
        #                                             "Date":timezone.now().strftime('%Y-%m-%d'),
        #                                             "DueDate":(timezone.now()+timedelta(days=14)).strftime('%Y-%m-%d'),
        #                                             "LineAmountTypes":"NoTax",
        #                                             "InvoiceNumber":InvoiceNumber,
        #                                             "Reference":subscription.order_no,
        #                                             "Status":"AUTHORISED",
        #                                             "LineItems":LineItems
        #                                             }

        #     create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
		# 											json=invoice_data,
		# 											headers=header 
		# 										).json()
        #     try:
        #         created_invoice = create_invoice['Status']
        #     except:
        #         created_invoice = None


        #     if created_invoice == 'OK':
        #         try:
        #             update_xero_invoice                  = XeroInvoice.objects.get(order=subscription,invoice_no=InvoiceNumber)
        #             update_xero_invoice.amount           = Amount
        #             update_xero_invoice.xero_marked_date = timezone.now().date()
        #             update_xero_invoice.payment_policy   = payment_policy
        #             update_xero_invoice.save()
        #         except:
        #             XeroInvoice.objects.create(order=subscription,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

        # #PREPAID, CLEANING BEFORE Invoices
        # before_orders = Order.objects.select_related('evaluation__customer').filter(evaluation__quatation_status='APPROVED',payment_status='PENDING',order_status__isnull=False).exclude(order_status='ORDER_CANCELLED').filter(Q(evaluation__payment_method='PREPAID')|Q(Q(evaluation__payment_method='BREAKDOWN')&Q(preamount_paid__gt=0))).filter(~Q(callback_status='LEGAL_ACTION'))
                
        # for before_order in before_orders:
        #     ##Xero Contact
        #     if not before_order.evaluation.customer.xero_account_id:
        #         ##Xero Create Customer ID and Save
        #         contact_data                = {
        #                                         "Name":before_order.evaluation.customer.name,
        #                                         "ContactNumber":before_order.evaluation.customer.mobile_number,
        #                                         "EmailAddress":before_order.evaluation.customer.email,
        #                                         "ContactStatus":"ACTIVE",
        #                                         "IsCustomer":True,
        #                                         "DefaultCurrency":"KWD"
        #                                                     }
                                                
        #         header                      = {
        #                                     'xero-tenant-id': xero.tenant_id,
        #                                     'Authorization': 'Bearer '+access_token,
        #                                     'Accept': 'application/json',
        #                                     'Content-Type': 'application/json'
        #                                         }

        #         create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
        #                                                 json=contact_data,
        #                                                 headers=header 
        #                                             ).json()

        #         before_order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
        #         before_order.evaluation.customer.save()

        #     if before_order.evaluation.payment_method == 'PREPAID':
        #         Amount = before_order.evaluation.total_cost 
        #         ##Invoice Line Item 
        #         LineItems                 = []
        #         LineItems.append({
        #             "Description":"ONE TIME SERVICE",
        #             "Quantity":"1",
        #             "UnitAmount":Amount,
        #             "AccountCode":1002,
        #             "TaxType":"NONE"
        #                         }
        #             )
        #         InvoiceNumber  = before_order.invoice_no

        #         payment_policy = 'PREPAID'

        #     if before_order.evaluation.payment_method == 'BREAKDOWN':
        #         Amount = before_order.evaluation.before_cleaning_amount 
        #         ##Invoice Line Item 
        #         LineItems                 = []
        #         LineItems.append({
        #             "Description":"ONE TIME SERVICE",
        #             "Quantity":"1",
        #             "UnitAmount":Amount,
        #             "AccountCode":1002,
        #             "TaxType":"NONE"
        #                         }
        #             )
        #         InvoiceNumber  = before_order.invoice_no+'A'
                
        #         payment_policy = 'BEFORE CLEANING'

        #     invoice_data              = 	{
		# 											"Type":"ACCREC",
		# 											"Contact":{
		# 												"ContactID":before_order.evaluation.customer.xero_account_id
		# 											},

		# 											"Date":before_order.created.strftime('%Y-%m-%d'),
		# 											"DueDate":(before_order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
		# 											"LineAmountTypes":"NoTax",
		# 											"InvoiceNumber":InvoiceNumber,
		# 											"Reference":before_order.order_no,
		# 											"Status":"AUTHORISED",
		# 											"LineItems":LineItems
		# 											}

        #     ##xero Create Invoice
        #     header                      = {
        #                                     'xero-tenant-id': xero.tenant_id,
        #                                     'Authorization': 'Bearer '+access_token,
        #                                     'Accept': 'application/json',
        #                                     'Content-Type': 'application/json'
        #                                         }

        #     create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
        #                                             json=invoice_data,
        #                                             headers=header 
        #                                         ).json()
        #     try:
        #         created_invoice = create_invoice['Status']
        #     except:
        #         created_invoice = None
            
        #     if created_invoice == 'OK':
        #         try:
        #             update_xero_invoice                  = XeroInvoice.objects.get(order=before_order,invoice_no=InvoiceNumber)
        #             update_xero_invoice.amount           = Amount
        #             update_xero_invoice.xero_marked_date = timezone.now().date()
        #             update_xero_invoice.payment_policy   = payment_policy
        #             update_xero_invoice.save()
        #         except:
        #             XeroInvoice.objects.create(order=before_order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

        #POSTPAID, CLEANING AFTER Invoices
        after_orders  = Order.objects.select_related('evaluation__customer').prefetch_related('order_scheduler_order').filter(evaluation__quatation_status='APPROVED',payment_status='PENDING',order_status__isnull=False).exclude(order_status='ORDER_CANCELLED').filter(Q(evaluation__payment_method='POSTPAID')|Q(Q(evaluation__payment_method='BREAKDOWN')&Q(postamount_paid__gt=0))).filter(~Q(callback_status='LEGAL_ACTION')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count')).filter(remaining_cleanings_count=0).prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))
        for after_order in after_orders:
            ##Xero Contact
            if not after_order.evaluation.customer.xero_account_id:
                ##Xero Create Customer ID and Save
                contact_data                = {
                                                "Name":after_order.evaluation.customer.name,
                                                "ContactNumber":after_order.evaluation.customer.mobile_number,
                                                "EmailAddress":after_order.evaluation.customer.email,
                                                "ContactStatus":"ACTIVE",
                                                "IsCustomer":True,
                                                "DefaultCurrency":"KWD"
                                                            }
                                                
                header                      = {
                                            'xero-tenant-id': xero.tenant_id,
                                            'Authorization': 'Bearer '+access_token,
                                            'Accept': 'application/json',
                                            'Content-Type': 'application/json'
                                                }

                create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
                                                        json=contact_data,
                                                        headers=header 
                                                    ).json()

                after_order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
                after_order.evaluation.customer.save()

            if after_order.evaluation.payment_method == 'POSTPAID':
                Amount = after_order.evaluation.total_cost 
                ##Invoice Line Item 
                LineItems                 = []
                LineItems.append({
                    "Description":"ONE TIME SERVICE",
                    "Quantity":"1",
                    "UnitAmount":Amount,
                    "AccountCode":1002,
                    "TaxType":"NONE"
                                }
                    )
                InvoiceNumber  = after_order.invoice_no

                payment_policy = 'POSTPAID'

            if after_order.evaluation.payment_method == 'BREAKDOWN':
                Amount = after_order.evaluation.after_cleaning_amount 
                ##Invoice Line Item 
                LineItems                 = []
                LineItems.append({
                    "Description":"ONE TIME SERVICE",
                    "Quantity":"1",
                    "UnitAmount":Amount,
                    "AccountCode":1002,
                    "TaxType":"NONE"
                                }
                    )
                InvoiceNumber  = after_order.invoice_no+'B'
                
                payment_policy = 'AFTER CLEANING'

            invoice_data              = 	{
													"Type":"ACCREC",
													"Contact":{
														"ContactID":after_order.evaluation.customer.xero_account_id
													},
													"Date":after_order.orderschedules[after_order.total_cleanings_count-1].start_at.strftime('%Y-%m-%d'),
													"DueDate":(after_order.orderschedules[after_order.total_cleanings_count-1].start_at+timedelta(days=14)).strftime('%Y-%m-%d'),
													"LineAmountTypes":"NoTax",
													"InvoiceNumber":InvoiceNumber,
													"Reference":after_order.order_no,
													"Status":"AUTHORISED",
													"LineItems":LineItems
													}

            ##xero Create Invoice
            header                      = {
                                            'xero-tenant-id': xero.tenant_id,
                                            'Authorization': 'Bearer '+access_token,
                                            'Accept': 'application/json',
                                            'Content-Type': 'application/json'
                                                }

            print(invoice_data,"data")
            create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                    json=invoice_data,
                                                    headers=header 
                                                ).json()
            try:
                created_invoice = create_invoice['Status']
            except:
                created_invoice = None
            
            if created_invoice == 'OK':
                try:
                    update_xero_invoice                  = XeroInvoice.objects.get(order=after_order,invoice_no=InvoiceNumber)
                    update_xero_invoice.amount           = Amount
                    update_xero_invoice.xero_marked_date = timezone.now().date()
                    update_xero_invoice.payment_policy   = payment_policy
                    update_xero_invoice.save()
                except:
                    XeroInvoice.objects.create(order=after_order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)