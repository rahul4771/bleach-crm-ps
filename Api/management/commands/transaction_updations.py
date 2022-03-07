from django.core.management.base import BaseCommand

from django.utils import timezone
from datetime import timedelta,date,datetime
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch

import requests
import json

from accountant.models import PaymentHistory
from Api.models import XeroConnection


class Command(BaseCommand):
    help = 'Automatic Updations'

    def handle(self, *args, **kwargs): 
        xero          = XeroConnection.objects.first()
        PaymentHistory.objects.select_related('order__evaluation__customer').filter(paid_date__date__gte=transaction_start_date,is_xero_marked=False).update(is_xero_marked=False)

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

        #Bank Transaction
        transaction_start_date      = datetime.strptime("01-01-2022","%d-%m-%Y").date()
        transactions                = PaymentHistory.objects.select_related('order__evaluation__customer').filter(paid_date__date__gte=transaction_start_date,is_xero_marked=False)
        for transaction in transactions:
            if transaction.payment_mode == 'ONLINECREDIT':
                Description = transaction.payment_gateway
            else:
                Description = transaction.payment_mode

            ##Xero Contact
            if not transaction.order.evaluation.customer.xero_account_id:
                ##Xero Create Customer ID and Save
                contact_data                = {
                                                "Name":transaction.order.evaluation.customer.name,
                                                "ContactNumber":transaction.order.evaluation.customer.mobile_number,
                                                "EmailAddress":transaction.order.evaluation.customer.email,
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
                                                    )
                print(create_contact)
                print(contact_data)
                create_contact = create_contact.json()
                transaction.order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
                transaction.order.evaluation.customer.save()

            header                      = {
                                            'xero-tenant-id': xero.tenant_id,
                                            'Authorization': 'Bearer '+access_token,
                                            'Accept': 'application/json',
                                            'Content-Type': 'application/json'
                                                }

            transaction_data            = {
                                            "Type": "RECEIVE",
                                            "Reference": transaction.order.evaluation.evaluation_id,
                                            "Date":datetime.strftime(transaction.paid_date,"%Y-%m-%d"),
                                            "Contact": {
                                                "ContactID": transaction.order.evaluation.customer.xero_account_id,
                                            },
                                            "LineItems": [{
                                                "Description": Description,
                                                "UnitAmount": transaction.amount_paid,
                                                "AccountCode": "200",
                                                "TaxType":"NONE"
                                            }],
                                            "BankAccount": {
                                                "Code": "091"
                                            }
                                            }
                                            
            update_transaction          = requests.post('https://api.xero.com/api.xro/2.0/BankTransactions',
                                                    json=transaction_data,
                                                    headers=header 
                                                )

            transaction.is_xero_marked = True
            transaction.save()