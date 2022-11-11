import pytz
import requests
import json

from django.core.management.base import BaseCommand

from order.models import Order,OrderScheduler,XeroInvoice
from Api.models import XeroConnection
from accountant.models import PaymentHistory
from user.models import UserProfile

import time

from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch

class Command(BaseCommand):
    help = 'Xero Invoice Load'

    # def add_arguments(self,parser):
    #     parser.add_argument('start_date',type=str, help="start date")
    #     parser.add_argument('day_count',type=int, help="number of days")

    def handle(self, *args, **kwargs):
        
        # start_date = kwargs['start_date']
        # day_count = kwargs['day_count']

        #getting crm payments
        # paymentdate = datetime.now()
        # paymentdate_start = paymentdate.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=pytz.UTC) - timedelta(7)
        # paymentdate_end = paymentdate.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=pytz.UTC) - timedelta(1)
        
        paymentdate = datetime.strptime("01-01-2022","%d-%m-%Y")
        paymentdate_start = paymentdate.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=pytz.UTC)
        paymentdate_end = paymentdate_start + timedelta(10)

        # paymentdate = datetime.strptime(start_date,"%d-%m-%Y")
        # paymentdate_start = paymentdate.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=pytz.UTC)
        # paymentdate_end = paymentdate_start + timedelta(day_count)     

        payment_histories = PaymentHistory.objects.filter(is_active=True,paid_date__range=(paymentdate_start,paymentdate_end))
        payment_histories      = PaymentHistory.objects.select_related('order__evaluation__customer').prefetch_related('order__order_scheduler_order').filter(Q( Q(is_active=True) & Q(paid_date__gte=paymentdate_start) & Q(paid_date__lte=paymentdate_end) )).annotate(total_cleanings_count=Count('order__order_scheduler_order')).prefetch_related(Prefetch('order__order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))

        #ITERATING SYSTEM PAYMENTS
        for payment_history in payment_histories:
            
            time.sleep(5)

            print(payment_history.paid_date.day,payment_history.paid_date.month,payment_history.paid_date.year,"transaction date")

            #Xero Integration
            xero          = XeroConnection.objects.first()

            print(xero,"xero")
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

            print(access_token,refresh_token,"rfr")

            ##xero Create Invoice
            header                     = {
                                            'xero-tenant-id': xero.tenant_id,
                                            'Authorization': 'Bearer '+access_token,
                                            "Accept": "application/json",
                                                }

            invoices =  requests.request("GET", 'https://api.xero.com/api.xro/2.0/Invoices/?where=Date=DateTime('+str(payment_history.paid_date.year)+', '+str(payment_history.paid_date.month)+', '+str(payment_history.paid_date.day)+') AND Reference="'+str(payment_history.order.order_no)+'"', headers=header).json()
            
            payment_method    = payment_history.order.evaluation.payment_method

            #CASE 1

            #if invoice exists in xero
            if invoices['Invoices']:
                for invoice in invoices['Invoices']:

                    #CASE 1A

                    #paid invoices bank charge adding
                    if invoice['Status'] == 'PAID' and float(payment_history.amount_paid) == float(invoice['SubTotal']) and payment_history.payment_mode == 'ONLINECREDIT':

                        #Payment Removal

                        header                      = {
                                                                        'xero-tenant-id': xero.tenant_id,
                                                                        'Authorization': 'Bearer '+access_token,
                                                                        'Accept': 'application/json',
                                                                        'Content-Type': 'application/json'
                                                                            }

                        if payment_history.transaction_id:
                            data     = requests.get('https://api.xero.com/api.xro/2.0/Payments?where=Reference=="'+str(payment_history.transaction_id)+'"',
                                                                            headers=header 
                                                                        ).json()

                            payments = data['Payments']
                            for payment in payments:
                                body = {"Status":"DELETED"}
                                delete_payment = requests.post('https://api.xero.com/api.xro/2.0/Payments/'+payment['PaymentID'],
                                                                                json=body,
                                                                                headers=header 
                                                                            ).json()
                        else:
                            print(payment_history.order.order_no,"no transaction id")
                            pass
                        
                        if delete_payment['Status'] == 'OK':
                            payment_history.is_xero_marked = False
                            payment_history.save()
                            print(payment_history.order.order_no,"payment deleted")

                            ##Xero Contact
                            if not payment_history.order.evaluation.customer.xero_account_id:
                                ##Xero Create Customer ID and Save
                                contact_data                = {
                                                                "Name":payment_history.order.evaluation.customer.name,
                                                                "ContactNumber":payment_history.order.evaluation.customer.mobile_number,
                                                                "EmailAddress":payment_history.order.evaluation.customer.email,
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

                                payment_history.order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
                                payment_history.order.evaluation.customer.save()
                            
                            
                            if payment_method == 'PREPAID':

                                if payment_history.payment_gateway == 'DEBITCARD':
                                    BankCharge = .250
                                if payment_history.payment_gateway == 'CREDITCARD':
                                    BankCharge = float(payment_history.order.evaluation.total_cost)*.025

                                Amount = payment_history.order.evaluation.total_cost

                                ##Invoice Line Item 
                                LineItems                 = []
                                LineItems.append({
                                    "Description":"ONE TIME SERVICE",
                                    "Quantity":"1",
                                    "UnitAmount":Amount,
                                    "AccountCode":1207004,
                                    "TaxType":"NONE"
                                                }
                                    )
                                LineItems.append({
                                    "Description":"BANK CHARGE",
                                    "Quantity":"1",
                                    "UnitAmount":-BankCharge,
                                    "AccountCode":3202014,
                                    "TaxType":"NONE"
                                                }
                                    )

                                payment_policy = 'PREPAID'

                                invoice_data              = 	{
                                                                    "Type":"ACCREC",
                                                                    "Contact":{
                                                                        "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                                    },
                                                                    "Date":payment_history.order.created.strftime('%Y-%m-%d'),
                                                                    "DueDate":(payment_history.order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
                                                                    "LineAmountTypes":"NoTax",
                                                                    "InvoiceNumber":invoice['InvoiceNumber'],
                                                                    "Reference":payment_history.order.order_no,
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

                                create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                        json=invoice_data,
                                                                        headers=header 
                                                                    ).json()
                                
                                try:
                                    created_invoice = create_invoice['Status']
                                except:
                                    created_invoice = None   

                                if created_invoice == 'OK':
                                    print(payment_history.order.order_no,"invoice updated with bank charge")
                                    try: 
                                        update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                        update_xero_invoice.amount           = Amount
                                        update_xero_invoice.xero_marked_date = timezone.now().date()
                                        update_xero_invoice.payment_policy   = payment_policy
                                        update_xero_invoice.save()
                                    except:
                                        XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

                            if payment_method == 'POSTPAID':

                                if payment_history.payment_gateway == 'DEBITCARD':
                                    BankCharge = .250
                                if payment_history.payment_gateway == 'CREDITCARD':
                                    BankCharge = float(payment_history.order.evaluation.total_cost)*.025

                                Amount = payment_history.order.evaluation.total_cost

                                ##Invoice Line Item 
                                LineItems                 = []
                                LineItems.append({
                                    "Description":"ONE TIME SERVICE",
                                    "Quantity":"1",
                                    "UnitAmount":Amount,
                                    "AccountCode":1207004,
                                    "TaxType":"NONE"
                                                }
                                    )
                                LineItems.append({
                                    "Description":"BANK CHARGE",
                                    "Quantity":"1",
                                    "UnitAmount":-BankCharge,
                                    "AccountCode":3202014,
                                    "TaxType":"NONE"
                                                }
                                    )

                                payment_policy = 'POSTPAID'

                                invoice_data              = 	{
                                                                    "Type":"ACCREC",
                                                                    "Contact":{
                                                                        "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                                    },
                                                                    "Date":payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at.strftime('%Y-%m-%d'),
                                                                    "DueDate":(payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at+timedelta(days=14)).strftime('%Y-%m-%d'),
                                                                    "LineAmountTypes":"NoTax",
                                                                    "InvoiceNumber":invoice['InvoiceNumber'],
                                                                    "Reference":payment_history.order.order_no,
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

                                create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                        json=invoice_data,
                                                                        headers=header 
                                                                    ).json()
                                try:
                                    created_invoice = create_invoice['Status']
                                except:
                                    created_invoice = None
                                
                                if created_invoice == 'OK':
                                    print(payment_history.order.order_no,"invoice updated with bank charge")
                                    try:
                                        update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                        update_xero_invoice.amount           = Amount
                                        update_xero_invoice.xero_marked_date = timezone.now().date()
                                        update_xero_invoice.payment_policy   = payment_policy
                                        update_xero_invoice.save()
                                    except:
                                        XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

                            if payment_method == 'BREAKDOWN':

                                if invoice['InvoiceNumber'][-1] == 'A':
                                    Amount = payment_history.order.evaluation.before_cleaning_amount
                                    DueDate= payment_history.order.orderschedules[0].start_at+timedelta(days=14)
                                    payment_policy = 'BEFORE CLEANING'

                                    if payment_history.payment_gateway == 'DEBITCARD':
                                        BankCharge = .250
                                    if payment_history.payment_gateway == 'CREDITCARD':
                                        BankCharge = float(payment_history.order.evaluation.before_cleaning_amount)*.025
                                else:
                                    Amount = payment_history.order.evaluation.after_cleaning_amount
                                    DueDate= payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at+timedelta(days=14)
                                    payment_policy = 'AFTER CLEANING'

                                    if payment_history.payment_gateway == 'DEBITCARD':
                                        BankCharge = .250
                                    if payment_history.payment_gateway == 'CREDITCARD':
                                        BankCharge = float(payment_history.order.evaluation.after_cleaning_amount)*.025

                                ##Invoice Line Item 
                                LineItems                 = []
                                LineItems.append({
                                    "Description":"ONE TIME SERVICE",
                                    "Quantity":"1",
                                    "UnitAmount":Amount,
                                    "AccountCode":1207004,
                                    "TaxType":"NONE"
                                                }
                                    )
                                LineItems.append({
                                    "Description":"BANK CHARGE",
                                    "Quantity":"1",
                                    "UnitAmount":-BankCharge,
                                    "AccountCode":3202014,
                                    "TaxType":"NONE"
                                                }
                                    )                       

                                invoice_data              = 	{
                                                            "Type":"ACCREC",
                                                            "Contact":{
                                                                "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                            },
                                                            "Date":DueDate.strftime('%Y-%m-%d'),
                                                            "DueDate":DueDate.strftime('%Y-%m-%d'),
                                                            "LineAmountTypes":"NoTax",
                                                            "InvoiceNumber":invoice['InvoiceNumber'],
                                                            "Reference":payment_history.order.order_no,
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

                                create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                        json=invoice_data,
                                                                        headers=header 
                                                                    ).json()
                                try:
                                    created_invoice = create_invoice['Status']
                                except:
                                    created_invoice = None
                                
                                if created_invoice == 'OK':
                                    print(payment_history.order.order_no,"invoice updated with bank charge")
                                    try:
                                        update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                        update_xero_invoice.amount           = Amount
                                        update_xero_invoice.xero_marked_date = timezone.now().date()
                                        update_xero_invoice.payment_policy   = payment_policy
                                        update_xero_invoice.save()
                                    except:
                                        XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
                        
                            if payment_method == 'SUBSCRIPTION':

                                if payment_history.payment_gateway == 'DEBITCARD':
                                    BankCharge = .250
                                if payment_history.payment_gateway == 'CREDITCARD':
                                    BankCharge = float(payment_history.amount_paid)*.025

                                Amount = payment_history.amount_paid 
                                ##Invoice Line Item 
                                LineItems                 = []
                                LineItems.append({
                                    "Description":"SUBSCRIPTION",
                                    "Quantity":"1",
                                    "UnitAmount":Amount,
                                    "AccountCode":1207004,
                                    "TaxType":"NONE"
                                                }
                                    )
                                LineItems.append({
                                        "Description":"BANK CHARGE",
                                        "Quantity":"1",
                                        "UnitAmount":-BankCharge,
                                        "AccountCode":3202014,
                                        "TaxType":"NONE"
                                                    }
                                        )
                                
                                payment_policy = 'SUBSCRIPTION'

                                invoice_data              = 	{
                                                            "Type":"ACCREC",
                                                            "Contact":{
                                                                "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                            },
                                                            "Date":payment_history.paid_date.strftime('%Y-%m-%d'),
                                                            "DueDate":payment_history.paid_date.strftime('%Y-%m-%d'),
                                                            "LineAmountTypes":"NoTax",
                                                            "InvoiceNumber":invoice['InvoiceNumber'],
                                                            "Reference":payment_history.order.order_no,
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

                                create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                        json=invoice_data,
                                                                        headers=header 
                                                                    ).json()
                                try:
                                    created_invoice = create_invoice['Status']
                                except:
                                    created_invoice = None
                                
                                if created_invoice == 'OK':
                                    print(payment_history.order.order_no,"invoice updated with bank charge")
                                    try:
                                        update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                        update_xero_invoice.amount           = Amount
                                        update_xero_invoice.xero_marked_date = timezone.now().date()
                                        update_xero_invoice.payment_policy   = payment_policy
                                        update_xero_invoice.save()
                                    except:
                                        XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
                        
                            #xero payment update
                            try:
                                xero_invoice        = XeroInvoice.objects.get(invoice_no=invoice['InvoiceNumber'])
                            except:
                                xero_invoice        = None 

                            payment_date        = payment_history.paid_date.date()
                            payment_date_string = datetime.strftime(payment_date,'%Y-%m-%d')
                            amount_paid         = payment_history.amount_paid

                            if payment_history.transaction_id:
                                transaction_id = payment_history.transaction_id
                            else:
                                transaction_id = payment_history.payment_mode
                            
                            if xero_invoice:
                                payment_data = {
                                            "Invoice":{
                                                "InvoiceNumber":xero_invoice.invoice_no
                                            },
                                            "Account":{
                                                "Code":"1201023"
                                            },
                                            "Date":payment_date_string,
                                            "Amount":float(amount_paid)-BankCharge,
                                            "Reference":transaction_id
                                            }

                                header                      = {
                                                            'xero-tenant-id': xero.tenant_id,
                                                            'Authorization': 'Bearer '+access_token,
                                                            'Accept': 'application/json',
                                                            'Content-Type': 'application/json'
                                                                }
                                
                                update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
                                                                    json=payment_data,
                                                                    headers=header 
                                                                ).json()

                                # print(update_payment)
                                try:
                                    created_payment = update_payment['Status']
                                except:
                                    created_payment = None

                                if created_payment == 'OK':
                                    print(payment_history.order.order_no,"payment updated")
                                    xero_invoice.is_paid   = True
                                    xero_invoice.paid_date = payment_date
                                    xero_invoice.save()
                            
                                    payment_history.is_xero_marked = True
                                    payment_history.save()
                        ##########################################################################################################

                    # INVOICE NOT PAID - UPDATING PAYMENT WITH BANK CHARGES
                    elif invoice['Status'] == 'AUTHORISED':

                        ##Xero Contact
                        if not payment_history.order.evaluation.customer.xero_account_id:
                            ##Xero Create Customer ID and Save
                            contact_data                = {
                                                            "Name":payment_history.order.evaluation.customer.name,
                                                            "ContactNumber":payment_history.order.evaluation.customer.mobile_number,
                                                            "EmailAddress":payment_history.order.evaluation.customer.email,
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

                            payment_history.order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
                            payment_history.order.evaluation.customer.save()
                        
                        
                        if payment_method == 'PREPAID':

                            if payment_history.payment_gateway == 'DEBITCARD':
                                BankCharge = .250
                            elif payment_history.payment_gateway == 'CREDITCARD':
                                BankCharge = float(payment_history.order.evaluation.total_cost)*.025
                            else:
                                BankCharge = 0

                            Amount = payment_history.order.evaluation.total_cost 
                            ##Invoice Line Item 
                            LineItems                 = []
                            LineItems.append({
                                "Description":"ONE TIME SERVICE",
                                "Quantity":"1",
                                "UnitAmount":Amount,
                                "AccountCode":1207004,
                                "TaxType":"NONE"
                                            }
                                )
                            
                            if payment_history.payment_mode == 'ONLINECREDIT':
                                LineItems.append({
                                    "Description":"BANK CHARGE",
                                    "Quantity":"1",
                                    "UnitAmount":-BankCharge,
                                    "AccountCode":3202014,
                                    "TaxType":"NONE"
                                                }
                                    )

                            payment_policy = 'PREPAID'

                            invoice_data              = 	{
                                                                "Type":"ACCREC",
                                                                "Contact":{
                                                                    "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                                },
                                                                "Date":payment_history.order.created.strftime('%Y-%m-%d'),
                                                                "DueDate":(payment_history.order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
                                                                "LineAmountTypes":"NoTax",
                                                                "InvoiceNumber":invoice['InvoiceNumber'],
                                                                "Reference":payment_history.order.order_no,
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

                            create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                    json=invoice_data,
                                                                    headers=header 
                                                                ).json()
                            try:
                                created_invoice = create_invoice['Status']
                            except:
                                created_invoice = None   
                            
                            if created_invoice == 'OK':
                                print(payment_history.order.order_no,"invoice bank charge updated")
                                try:
                                    update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                    update_xero_invoice.amount           = Amount
                                    update_xero_invoice.xero_marked_date = timezone.now().date()
                                    update_xero_invoice.payment_policy   = payment_policy
                                    update_xero_invoice.save()
                                except:    
                                    XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

                        if payment_method == 'POSTPAID':

                            if payment_history.payment_gateway == 'DEBITCARD':
                                BankCharge = .250
                            elif payment_history.payment_gateway == 'CREDITCARD':
                                BankCharge = float(payment_history.order.evaluation.total_cost)*.025
                            else:
                                BankCharge = 0

                            Amount = payment_history.order.evaluation.total_cost 
                            ##Invoice Line Item 
                            LineItems                 = []
                            LineItems.append({
                                "Description":"ONE TIME SERVICE",
                                "Quantity":"1",
                                "UnitAmount":Amount,
                                "AccountCode":1207004,
                                "TaxType":"NONE"
                                            }
                                )
                            
                            if payment_history.payment_mode == 'ONLINECREDIT':
                                LineItems.append({
                                    "Description":"BANK CHARGE",
                                    "Quantity":"1",
                                    "UnitAmount":-BankCharge,
                                    "AccountCode":3202014,
                                    "TaxType":"NONE"
                                                }
                                    )

                            payment_policy = 'POSTPAID'

                            invoice_data              = 	{
                                                                "Type":"ACCREC",
                                                                "Contact":{
                                                                    "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                                },
                                                                "Date":payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at.strftime('%Y-%m-%d'),
                                                                "DueDate":(payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at+timedelta(days=14)).strftime('%Y-%m-%d'),
                                                                "LineAmountTypes":"NoTax",
                                                                "InvoiceNumber":invoice['InvoiceNumber'],
                                                                "Reference":payment_history.order.order_no,
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

                            create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                    json=invoice_data,
                                                                    headers=header 
                                                                ).json()
                            try:
                                created_invoice = create_invoice['Status']
                            except:
                                created_invoice = None
                            
                            if created_invoice == 'OK':
                                print(payment_history.order.order_no,"invoice bank charge updated")
                                try:
                                    update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                    update_xero_invoice.amount           = Amount
                                    update_xero_invoice.xero_marked_date = timezone.now().date()
                                    update_xero_invoice.payment_policy   = payment_policy
                                    update_xero_invoice.save()
                                except:
                                    XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

                        if payment_method == 'BREAKDOWN':

                            if invoice['InvoiceNumber'][-1] == 'A':
                                Amount = payment_history.order.evaluation.before_cleaning_amount
                                DueDate= payment_history.order.orderschedules[0].start_at+timedelta(days=14)
                                payment_policy = 'BEFORE CLEANING'

                                if payment_history.payment_gateway == 'DEBITCARD':
                                    BankCharge = .250
                                elif payment_history.payment_gateway == 'CREDITCARD':
                                    BankCharge = float(payment_history.order.evaluation.before_cleaning_amount)*.025
                                else:
                                    BankCharge = 0

                            else:
                                Amount = payment_history.order.evaluation.after_cleaning_amount
                                DueDate= payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at+timedelta(days=14)
                                payment_policy = 'AFTER CLEANING'

                                if payment_history.payment_gateway == 'DEBITCARD':
                                    BankCharge = .250
                                elif payment_history.payment_gateway == 'CREDITCARD':
                                    BankCharge = float(payment_history.order.evaluation.after_cleaning_amount)*.025
                                else:
                                    BankCharge = 0

                            ##Invoice Line Item 
                            LineItems                 = []
                            LineItems.append({
                                "Description":"ONE TIME SERVICE",
                                "Quantity":"1",
                                "UnitAmount":Amount,
                                "AccountCode":1207004,
                                "TaxType":"NONE"
                                            }
                                )
                            
                            if payment_history.payment_mode == 'ONLINECREDIT':
                                LineItems.append({
                                    "Description":"BANK CHARGE",
                                    "Quantity":"1",
                                    "UnitAmount":-BankCharge,
                                    "AccountCode":3202014,
                                    "TaxType":"NONE"
                                                }
                                    )

                            invoice_data              = 	{
                                                        "Type":"ACCREC",
                                                        "Contact":{
                                                            "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                        },
                                                        "Date":DueDate.strftime('%Y-%m-%d'),
                                                        "DueDate":DueDate.strftime('%Y-%m-%d'),
                                                        "LineAmountTypes":"NoTax",
                                                        "InvoiceNumber":invoice['InvoiceNumber'],
                                                        "Reference":payment_history.order.order_no,
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

                            create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                    json=invoice_data,
                                                                    headers=header 
                                                                ).json()
                            try:
                                created_invoice = create_invoice['Status']
                            except:
                                created_invoice = None
                            
                            if created_invoice == 'OK':
                                print(payment_history.order.order_no,"invoice bank charge updated")
                                try:
                                    update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                    update_xero_invoice.amount           = Amount
                                    update_xero_invoice.xero_marked_date = timezone.now().date()
                                    update_xero_invoice.payment_policy   = payment_policy
                                    update_xero_invoice.save()
                                except:
                                    XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

                        if payment_method == 'SUBSCRIPTION':
                            
                            #exceptional condition check for subscription debit card
                            if invoice['AmountDue'] == 0.25 and float(invoice['AmountPaid'])+float(invoice['AmountDue']) == float(payment_history.amount_paid) and payment_history.payment_gateway == 'DEBITCARD':

                                #Payment Removal

                                header                      = {
                                                                                'xero-tenant-id': xero.tenant_id,
                                                                                'Authorization': 'Bearer '+access_token,
                                                                                'Accept': 'application/json',
                                                                                'Content-Type': 'application/json'
                                                                                    }

                                if payment_history.transaction_id:
                                    data     = requests.get('https://api.xero.com/api.xro/2.0/Payments?where=Reference=="'+str(payment_history.transaction_id)+'"',
                                                                                    headers=header 
                                                                                ).json()

                                    payments = data['Payments']
                                    for payment in payments:
                                        body = {"Status":"DELETED"}
                                        delete_payment = requests.post('https://api.xero.com/api.xro/2.0/Payments/'+payment['PaymentID'],
                                                                                        json=body,
                                                                                        headers=header 
                                                                                    ).json()
                                else:
                                    print(payment_history.order.order_no,"no transaction id")
                                    pass
                                
                                if delete_payment['Status'] == 'OK':
                                    payment_history.is_xero_marked = False
                                    payment_history.save()
                                    print(payment_history.order.order_no,"subscription xero payment deleted")

                            
                            if payment_history.payment_gateway == 'DEBITCARD':
                                BankCharge = .250
                            elif payment_history.payment_gateway == 'CREDITCARD':
                                BankCharge = float(payment_history.amount_paid )*.025
                            else:
                                BankCharge = 0

                            Amount = payment_history.amount_paid 
                            
                            ##Invoice Line Item 
                            LineItems                 = []
                            LineItems.append({
                                "Description":"SUBSCRIPTION",
                                "Quantity":"1",
                                "UnitAmount":Amount,
                                "AccountCode":1207004,
                                "TaxType":"NONE"
                                            }
                                )
                            
                            if payment_history.payment_mode == 'ONLINECREDIT':
                                LineItems.append({
                                        "Description":"BANK CHARGE",
                                        "Quantity":"1",
                                        "UnitAmount":-BankCharge,
                                        "AccountCode":3202014,
                                        "TaxType":"NONE"
                                                    }
                                        )
                            
                            payment_policy = 'SUBSCRIPTION'

                            invoice_data              = 	{
                                                        "Type":"ACCREC",
                                                        "Contact":{
                                                            "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                        },
                                                        "Date":payment_history.paid_date.strftime('%Y-%m-%d'),
                                                        "DueDate":payment_history.paid_date.strftime('%Y-%m-%d'),
                                                        "LineAmountTypes":"NoTax",
                                                        "InvoiceNumber":invoice['InvoiceNumber'],
                                                        "Reference":payment_history.order.order_no,
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

                            create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                    json=invoice_data,
                                                                    headers=header 
                                                                ).json()
                            try:
                                created_invoice = create_invoice['Status']
                            except:
                                created_invoice = None
                            
                            if created_invoice == 'OK':
                                print(payment_history.order.order_no,"invoice bank charge updated subscription")
                                try:
                                    update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=invoice['InvoiceNumber'])
                                    update_xero_invoice.amount           = Amount
                                    update_xero_invoice.xero_marked_date = timezone.now().date()
                                    update_xero_invoice.payment_policy   = payment_policy
                                    update_xero_invoice.save()
                                except:
                                    XeroInvoice.objects.create(order=payment_history.order,invoice_no=invoice['InvoiceNumber'],amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
                        ####################################################

                        #Payment Add to Xero
                        try:
                            xero_invoice        = XeroInvoice.objects.get(invoice_no=invoice['InvoiceNumber'])
                        except:
                            xero_invoice        = None 

                        payment_date        = payment_history.paid_date.date()
                        payment_date_string = datetime.strftime(payment_date,'%Y-%m-%d')
                        amount_paid         = payment_history.amount_paid

                        if payment_history.transaction_id:
                            transaction_id = payment_history.transaction_id
                        else:
                            transaction_id = payment_history.payment_mode
                        
                        if xero_invoice: 
                            payment_data = {
                                        "Invoice":{
                                            "InvoiceNumber":xero_invoice.invoice_no
                                        },
                                        "Account":{
                                            "Code":"1201023"
                                        },
                                        "Date":payment_date_string,
                                        "Amount":float(amount_paid)-BankCharge,
                                        "Reference":transaction_id
                                        }

                            header                      = {
                                                        'xero-tenant-id': xero.tenant_id,
                                                        'Authorization': 'Bearer '+access_token,
                                                        'Accept': 'application/json',
                                                        'Content-Type': 'application/json'
                                                            }

                            update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
                                                                json=payment_data,
                                                                headers=header 
                                                            ).json()

                            
                            try:
                                created_payment = update_payment['Status']
                            except:
                                created_payment = None

                            if created_payment == 'OK':
                                print(payment_history.order.order_no,"invoice payment updated")
                                xero_invoice.is_paid   = True
                                xero_invoice.paid_date = payment_date
                                xero_invoice.save()
                        
                                payment_history.is_xero_marked = True
                                payment_history.save()
                            ##########################################################################################################

                        #3RD CONDITION CASH, CHEQUE - ADD PAYMENT IF NOT PAID. NO BANK CHARGES
            
            #if invoice does not exist on xero - create invoice, add bank charge, update payment
            else:                                           
                
                ##Xero Contact
                if not payment_history.order.evaluation.customer.xero_account_id:
                    ##Xero Create Customer ID and Save
                    contact_data                = {
                                                    "Name":payment_history.order.evaluation.customer.name,
                                                    "ContactNumber":payment_history.order.evaluation.customer.mobile_number,
                                                    "EmailAddress":payment_history.order.evaluation.customer.email,
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

                    payment_history.order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
                    payment_history.order.evaluation.customer.save()
                
                
                if payment_method == 'PREPAID':

                    if payment_history.payment_gateway == 'DEBITCARD':
                        BankCharge = .250
                    elif payment_history.payment_gateway == 'CREDITCARD':
                        BankCharge = float(payment_history.order.evaluation.total_cost)*.025
                    else:
                        BankCharge = 0

                    Amount = payment_history.order.evaluation.total_cost 
                    ##Invoice Line Item 
                    LineItems                 = []
                    LineItems.append({
                        "Description":"ONE TIME SERVICE",
                        "Quantity":"1",
                        "UnitAmount":Amount,
                        "AccountCode":1207004,
                        "TaxType":"NONE"
                                    }
                        )
                    
                    if payment_history.payment_mode == 'ONLINECREDIT':
                        LineItems.append({
                            "Description":"BANK CHARGE",
                            "Quantity":"1",
                            "UnitAmount":-BankCharge,
                            "AccountCode":3202014,
                            "TaxType":"NONE"
                                        }
                            )

                    InvoiceNumber  = payment_history.order.invoice_no

                    payment_policy = 'PREPAID'

                    invoice_data              = 	{
                                                        "Type":"ACCREC",
                                                        "Contact":{
                                                            "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                        },
                                                        "Date":payment_history.order.created.strftime('%Y-%m-%d'),
                                                        "DueDate":(payment_history.order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
                                                        "LineAmountTypes":"NoTax",
                                                        "InvoiceNumber":InvoiceNumber,
                                                        "Reference":payment_history.order.order_no,
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

                    create_invoice              = requests.put('https://api.xero.com/api.xro/2.0/Invoices/',
                                                            json=invoice_data,
                                                            headers=header 
                                                        ).json()
                        
                    try:
                        created_invoice = create_invoice['Status']
                        
                    except:
                        
                        created_invoice = None   
                    
                    if created_invoice == 'OK':
                        print(payment_history.order.order_no,"invoice created and bank charge updated")
                        try:
                            
                            update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=InvoiceNumber)
                            update_xero_invoice.amount           = Amount
                            update_xero_invoice.xero_marked_date = timezone.now().date()
                            update_xero_invoice.payment_policy   = payment_policy
                            update_xero_invoice.save()
                        except:
                            
                            XeroInvoice.objects.create(order=payment_history.order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

                if payment_method == 'POSTPAID':

                    if payment_history.payment_gateway == 'DEBITCARD':
                        BankCharge = .250
                    elif payment_history.payment_gateway == 'CREDITCARD':
                        BankCharge = float(payment_history.order.evaluation.total_cost)*.025
                    else:
                        BankCharge = 0

                    Amount = payment_history.order.evaluation.total_cost 
                    ##Invoice Line Item 
                    LineItems                 = []
                    LineItems.append({
                        "Description":"ONE TIME SERVICE",
                        "Quantity":"1",
                        "UnitAmount":Amount,
                        "AccountCode":1207004,
                        "TaxType":"NONE"
                                    }
                        )
                    
                    if payment_history.payment_mode == 'ONLINECREDIT':
                        LineItems.append({
                            "Description":"BANK CHARGE",
                            "Quantity":"1",
                            "UnitAmount":-BankCharge,
                            "AccountCode":3202014,
                            "TaxType":"NONE"
                                        }
                            )
                    InvoiceNumber  = payment_history.order.invoice_no

                    payment_policy = 'POSTPAID'

                    invoice_data              = 	{
                                                        "Type":"ACCREC",
                                                        "Contact":{
                                                            "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                        },
                                                        "Date":payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at.strftime('%Y-%m-%d'),
                                                        "DueDate":(payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at+timedelta(days=14)).strftime('%Y-%m-%d'),
                                                        "LineAmountTypes":"NoTax",
                                                        "InvoiceNumber":InvoiceNumber,
                                                        "Reference":payment_history.order.order_no,
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

                    create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                            json=invoice_data,
                                                            headers=header 
                                                        ).json()
                    try:
                        created_invoice = create_invoice['Status']
                    except:
                        created_invoice = None
                    
                    if created_invoice == 'OK':
                        print(payment_history.order.order_no,"invoice created and bank charge updated")
                        try:
                            update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=InvoiceNumber)
                            update_xero_invoice.amount           = Amount
                            update_xero_invoice.xero_marked_date = timezone.now().date()
                            update_xero_invoice.payment_policy   = payment_policy
                            update_xero_invoice.save()
                        except:
                            XeroInvoice.objects.create(order=payment_history.order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

                if payment_method == 'BREAKDOWN':
                    
                    breakdown_histories = PaymentHistory.objects.prefetch_related('order__order_scheduler_order').filter(order=payment_history.order).annotate(total_cleanings_count=Count('order__order_scheduler_order')).prefetch_related(Prefetch('order__order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))
                    breakdown_counter      = 1
                    for breakdown_history in breakdown_histories:
                        if breakdown_history == payment_history:
                            #Before Cleaning
                            if breakdown_counter == 1:

                                if payment_history.payment_gateway == 'DEBITCARD':
                                    BankCharge = .250
                                elif payment_history.payment_gateway == 'CREDITCARD':
                                    BankCharge = float(payment_history.order.evaluation.before_cleaning_amount )*.025
                                else:
                                    BankCharge = 0

                                Amount = payment_history.order.evaluation.before_cleaning_amount 
                                ##Invoice Line Item 
                                LineItems                 = []
                                LineItems.append({
                                    "Description":"ONE TIME SERVICE",
                                    "Quantity":"1",
                                    "UnitAmount":Amount,
                                    "AccountCode":1207004,
                                    "TaxType":"NONE"
                                                }
                                    )
                                
                                if payment_history.payment_mode == 'ONLINECREDIT':
                                    LineItems.append({
                                        "Description":"BANK CHARGE",
                                        "Quantity":"1",
                                        "UnitAmount":-BankCharge,
                                        "AccountCode":3202014,
                                        "TaxType":"NONE"
                                                    }
                                        )
                                InvoiceNumber  = payment_history.order.invoice_no+'A'
                                
                                payment_policy = 'BEFORE CLEANING'

                                DueDate        = payment_history.order.orderschedules[0].start_at+timedelta(days=14)
                        
                            #After Cleaning
                            if breakdown_counter == 2:

                                if payment_history.payment_gateway == 'DEBITCARD':
                                    BankCharge = .250
                                elif payment_history.payment_gateway == 'CREDITCARD':
                                    BankCharge = float(payment_history.order.evaluation.after_cleaning_amount)*.025
                                else:
                                    BankCharge = 0

                                Amount = payment_history.order.evaluation.after_cleaning_amount
                                ##Invoice Line Item 
                                LineItems                 = []
                                LineItems.append({
                                    "Description":"ONE TIME SERVICE",
                                    "Quantity":"1",
                                    "UnitAmount":Amount,
                                    "AccountCode":1207004,
                                    "TaxType":"NONE"
                                                }
                                    )
                                
                                if payment_history.payment_mode == 'ONLINECREDIT':
                                    LineItems.append({
                                        "Description":"BANK CHARGE",
                                        "Quantity":"1",
                                        "UnitAmount":-BankCharge,
                                        "AccountCode":3202014,
                                        "TaxType":"NONE"
                                                    }
                                        )
                                InvoiceNumber  = payment_history.order.invoice_no+'B'
                                
                                payment_policy = 'AFTER CLEANING'

                                DueDate        = payment_history.order.orderschedules[payment_history.total_cleanings_count-1].start_at+timedelta(days=14)

                            invoice_data              = 	{
                                                        "Type":"ACCREC",
                                                        "Contact":{
                                                            "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                        },
                                                        "Date":DueDate.strftime('%Y-%m-%d'),
                                                        "DueDate":DueDate.strftime('%Y-%m-%d'),
                                                        "LineAmountTypes":"NoTax",
                                                        "InvoiceNumber":InvoiceNumber,
                                                        "Reference":payment_history.order.order_no,
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

                            create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                    json=invoice_data,
                                                                    headers=header 
                                                                ).json()
                            try:
                                created_invoice = create_invoice['Status']
                            except:
                                created_invoice = None
                            
                            if created_invoice == 'OK':
                                print(payment_history.order.order_no,"invoice created and bank charge updated")
                                try:
                                    update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=InvoiceNumber)
                                    update_xero_invoice.amount           = Amount
                                    update_xero_invoice.xero_marked_date = timezone.now().date()
                                    update_xero_invoice.payment_policy   = payment_policy
                                    update_xero_invoice.save()
                                except:
                                    XeroInvoice.objects.create(order=payment_history.order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
                        
                        breakdown_counter += 1

                if payment_method == 'SUBSCRIPTION':
                    
                    subscription_histories = PaymentHistory.objects.filter(order=payment_history.order)
                    subscription_counter   = 0
                    for subscription_history in subscription_histories:
                        #Before Cleaning
                        if subscription_history == payment_history:

                            if payment_history.payment_gateway == 'DEBITCARD':
                                BankCharge = .250
                            elif payment_history.payment_gateway == 'CREDITCARD':
                                BankCharge = float(payment_history.amount_paid)*.025
                            else:
                                BankCharge = 0

                            Amount = payment_history.amount_paid 
                            ##Invoice Line Item 
                            LineItems                 = []
                            LineItems.append({
                                "Description":"SUBSCRIPTION",
                                "Quantity":"1",
                                "UnitAmount":Amount,
                                "AccountCode":1207004,
                                "TaxType":"NONE"
                                            }
                                )
                            
                            if payment_history.payment_mode == 'ONLINECREDIT':
                                LineItems.append({
                                        "Description":"BANK CHARGE",
                                        "Quantity":"1",
                                        "UnitAmount":-BankCharge,
                                        "AccountCode":3202014,
                                        "TaxType":"NONE"
                                                    }
                                        )
                            InvoiceNumber  = payment_history.order.invoice_no+chr(ord('A')+subscription_counter)
                            
                            payment_policy = 'SUBSCRIPTION'

                            invoice_data              = 	{
                                                        "Type":"ACCREC",
                                                        "Contact":{
                                                            "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                        },
                                                        "Date":payment_history.paid_date.strftime('%Y-%m-%d'),
                                                        "DueDate":payment_history.paid_date.strftime('%Y-%m-%d'),
                                                        "LineAmountTypes":"NoTax",
                                                        "InvoiceNumber":InvoiceNumber,
                                                        "Reference":payment_history.order.order_no,
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

                            create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
                                                                    json=invoice_data,
                                                                    headers=header 
                                                                ).json()
                            try:
                                created_invoice = create_invoice['Status']
                            except:
                                created_invoice = None
                            
                            if created_invoice == 'OK':
                                print(payment_history.order.order_no,"invoice created and bank charge updated")
                                try:
                                    update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=InvoiceNumber)
                                    update_xero_invoice.amount           = Amount
                                    update_xero_invoice.xero_marked_date = timezone.now().date()
                                    update_xero_invoice.payment_policy   = payment_policy
                                    update_xero_invoice.save()
                                except:
                                    XeroInvoice.objects.create(order=payment_history.order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
                        
                        subscription_counter += 1
                        ###############################################################################
                
                
                #Payment Add to Xero
                try:
                    xero_invoice        = XeroInvoice.objects.get(invoice_no=InvoiceNumber)
                except:
                    xero_invoice        = None 

                payment_date        = payment_history.paid_date.date()
                payment_date_string = datetime.strftime(payment_date,'%Y-%m-%d')
                amount_paid         = payment_history.amount_paid

                if payment_history.transaction_id:
                    transaction_id = payment_history.transaction_id
                else:
                    transaction_id = payment_history.payment_mode
                
                if xero_invoice: 
                    payment_data = {
                                "Invoice":{
                                    "InvoiceNumber":xero_invoice.invoice_no
                                },
                                "Account":{
                                    "Code":"1201023"
                                },
                                "Date":payment_date_string,
                                "Amount":float(amount_paid)-BankCharge,
                                "Reference":transaction_id
                                }

                    header                      = {
                                                            'xero-tenant-id': xero.tenant_id,
                                                            'Authorization': 'Bearer '+access_token,
                                                            'Accept': 'application/json',
                                                            'Content-Type': 'application/json'
                                                                }
                    
                    update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
                                                        json=payment_data,
                                                        headers=header 
                                                    ).json()

                    
                    try:
                        created_payment = update_payment['Status']
                    except:
                        created_payment = None

                    if created_payment == 'OK':
                        print(payment_history.order.order_no,"invoice payment updated")
                        xero_invoice.is_paid   = True
                        xero_invoice.paid_date = payment_date
                        xero_invoice.save()
                
                        payment_history.is_xero_marked = True
                        payment_history.save()