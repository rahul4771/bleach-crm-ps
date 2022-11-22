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
    help = 'Xero BC Invoice Load'

    def handle(self, *args, **kwargs):

        invoice_numbers = [  
                202203146, 
                202203148, 
                202203173, 
                202203105, 
                202203213, 
                202203202, 
                202203224, 
                202203223,
                202104867
            ]

        # invoice_nos = ','.join(str(item) for item in invoice_numbers)
        
        for invoice_number in invoice_numbers:
            print(invoice_number,"inv number")

            time.sleep(5)

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

            ##xero Create Invoice
            header                     = {
                                            'xero-tenant-id': xero.tenant_id,
                                            'Authorization': 'Bearer '+access_token,
                                            "Accept": "application/json",
                                                }

            invoices =  requests.request("GET", 'https://api.xero.com/api.xro/2.0/Invoices/'+str(invoice_number)+'', headers=header).json()

            print(invoices['Invoices'],"inv check")

            for invoice in invoices['Invoices']:

                
                #Payment Removal

                header                      = {
                                                                'xero-tenant-id': xero.tenant_id,
                                                                'Authorization': 'Bearer '+access_token,
                                                                'Accept': 'application/json',
                                                                'Content-Type': 'application/json'
                                                                    }

                for payment in invoice['Payments']:
                
                    data     = requests.get('https://api.xero.com/api.xro/2.0/Payments?where=Reference=="'+str(payment['Reference'])+'"',
                                                                    headers=header 
                                                                ).json()

                    payments = data['Payments']
                    for payment in payments:
                        body = {"Status":"DELETED"}
                        delete_payment = requests.post('https://api.xero.com/api.xro/2.0/Payments/'+payment['PaymentID'],
                                                                        json=body,
                                                                        headers=header 
                                                                    ).json()

                    payment_history = PaymentHistory.objects.filter(transaction_id=payment['Reference']).first()

                print(payment_history.order.order_no,"payment history")
                
                if delete_payment['Status'] == 'OK':
                    payment_history.is_xero_marked = False
                    payment_history.save()
                    print(invoice['Reference'],"payment deleted")

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

                    BankCharge = .250
                    # BankCharge = float(payment_history.order.evaluation.total_cost)*.025

                    Amount = invoice['SubTotal']

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

                    payment_policy = payment_history.order.evaluation.payment_method

                    invoice_data              = 	{
                                                        "Type":"ACCREC",
                                                        "Contact":{
                                                            "ContactID":payment_history.order.evaluation.customer.xero_account_id
                                                        },
                                                        "Date":datetime.strptime(''+invoice['DateString']+'', '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d'),
                                                        "DueDate":datetime.strptime(''+invoice['DueDateString']+'', '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d'),
                                                        "LineAmountTypes":"NoTax",
                                                        "InvoiceNumber":invoice['InvoiceNumber'],
                                                        "Reference":invoice['Reference'],
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