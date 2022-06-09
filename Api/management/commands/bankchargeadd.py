import requests
import json

from django.core.management.base import BaseCommand

from order.models import Order,OrderScheduler,XeroInvoice
from Api.models import XeroConnection
from accountant.models import PaymentHistory
from user.models import UserProfile

from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch


class Command(BaseCommand):
    help = 'Automatic Invoice Generations'

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

        
        ##Payment Removal

        # #Paid History                                
        # payment_history_date   = datetime.strptime("01-04-2022","%d-%m-%Y").date()
        # payment_histories      = PaymentHistory.objects.select_related('order__evaluation__customer').prefetch_related('order__order_scheduler_order').filter(is_active=True,paid_date__gte=payment_history_date,is_xero_marked=True).filter(Q(Q(payment_gateway='CREDITCARD')|Q(payment_gateway='DEBITCARD'))).annotate(total_cleanings_count=Count('order__order_scheduler_order')).prefetch_related(Prefetch('order__order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))
        # print(payment_histories.count())
        # for payment_history in payment_histories:
        #     print(payment_history.order.order_no)
        #     data     = requests.get('https://api.xero.com/api.xro/2.0/Payments?where=Reference=="'+payment_history.transaction_id+'"',
        #                                                         headers=header 
        #                                                     ).json()
        #     payments = data['Payments']
        #     for payment in payments:
        #         print(payment['PaymentID'])
        #         body = {"Status":"DELETED"}
        #         delete_payment = requests.post('https://api.xero.com/api.xro/2.0/Payments/'+payment['PaymentID'],
        #                                                         json=body,
        #                                                         headers=header 
        #                                                     ).json()
        #         print(delete_payment)
            
        #     if delete_payment['Status'] == 'OK':
        #         payment_history.is_xero_marked = False
        #         payment_history.save()


        ##Invoice Editing and Payment Add
        #Paid History                                
        payment_history_date   = datetime.strptime("01-04-2022","%d-%m-%Y").date()
        payment_histories      = PaymentHistory.objects.select_related('order__evaluation__customer').prefetch_related('order__order_scheduler_order').filter(is_active=True,paid_date__gte=payment_history_date,is_xero_marked=False).filter(Q(Q(payment_gateway='CREDITCARD')|Q(payment_gateway='DEBITCARD'))).annotate(total_cleanings_count=Count('order__order_scheduler_order')).prefetch_related(Prefetch('order__order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))
        print(payment_histories.count())  
        for payment_history in payment_histories:

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


            payment_method    = payment_history.order.evaluation.payment_method
            print(payment_method,"Payment Method")
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
                            if payment_history.payment_gateway == 'CREDITCARD':
                                BankCharge = float(payment_history.order.evaluation.before_cleaning_amount)*.025

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
                            if payment_history.payment_gateway == 'CREDITCARD':
                                BankCharge = float(payment_history.order.evaluation.after_cleaning_amount)*.025

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
                            try:
                                update_xero_invoice                  = XeroInvoice.objects.get(order=payment_history.order,invoice_no=InvoiceNumber)
                                update_xero_invoice.amount           = Amount
                                update_xero_invoice.xero_marked_date = timezone.now().date()
                                update_xero_invoice.payment_policy   = payment_policy
                                update_xero_invoice.save()
                            except:
                                XeroInvoice.objects.create(order=payment_history.order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
                    
                    subscription_counter += 1

            print(InvoiceNumber)
            print(create_invoice)
            #Payment Add to Xero
            try:
                xero_invoice        = XeroInvoice.objects.get(invoice_no=InvoiceNumber)
            except:
                xero_invoice        = None 

            payment_date        = payment_history.paid_date.date()
            payment_date_string = datetime.strftime(payment_date,'%Y-%m-%d')
            amount_paid         = payment_history.amount_paid
            
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
                            "Reference":payment_history.transaction_id
                            }

                update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
                                                    json=payment_data,
                                                    headers=header 
                                                ).json()

                print(update_payment)
                try:
                    created_payment = update_payment['Status']
                except:
                    created_payment = None

                if created_payment == 'OK':
                    xero_invoice.is_paid   = True
                    xero_invoice.paid_date = payment_date
                    xero_invoice.save()
            
                    payment_history.is_xero_marked = True
                    payment_history.save()
            
            