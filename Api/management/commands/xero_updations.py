from django.core.management.base import BaseCommand

from django.utils import timezone
from datetime import timedelta,date,datetime
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch

import requests
import json


class Command(BaseCommand):
    help = 'Automatic Updations'

    def handle(self, *args, **kwargs):   
        #Get access Token
        header                      = {
                                        'Authorization': 'Basic MTEwRDVGMzhFOTNCNEQ1NDgwOTU2MzVDNEU0MUJGOTM6dmZoN0VVQXVnZEF3LUhwRkZ2YVoxMVFkVDEzRmtqYmw0bUtrMU01RTdyeVYwN19n',
                                        'Content-Type': 'application/x-www-form-urlencoded'
                                            }
        body                        = {"grant_type":"client_credentials","scope":"accounting.settings accounting.contacts accounting.transactions"}
        access_token                = requests.post('https://identity.xero.com/connect/token',
                                                data=body,
                                                headers=header 
                                            ).json()['access_token']
        print(access_token)
        #Bank Transaction
        header                      = {
                                        'Authorization': 'Bearer '+access_token,
                                        'Accept': 'application/json'
                                            }
        transaction_data            = {
                                        "Type": "RECEIVE",
                                        "Reference": "Test",
                                        "Date":"2022-02-09",
                                        "Contact": {
                                            "ContactID": "3b954d80-bfbf-4c98-825c-2b7f22803147"
                                        },
                                        "LineItems": [{
                                            "Description": "Test2",
                                            "UnitAmount": "1.00",
                                            "AccountCode": "200",
                                            "TaxType":"NONE"
                                        }],
                                        "BankAccount": {
                                            "Code": "090"
                                        }
                                        }
        update_transaction          = requests.post('https://api.xero.com/api.xro/2.0/BankTransactions',
                                                json=transaction_data,
                                                headers=header 
                                            )
        print(update_transaction.json())