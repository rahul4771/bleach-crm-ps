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
        body                        = {}

        #Paid History                                
        payment_history_date   = datetime.strptime("01-04-2022","%d-%m-%Y").date()
        payment_histories      = PaymentHistory.objects.select_related('order__evaluation__customer').prefetch_related('order__order_scheduler_order').filter(is_active=True,paid_date__gte=payment_history_date,is_xero_marked=True).filter(Q(Q(payment_gateway='CREDITCARD')|Q(payment_gateway='DEBITCARD'))).annotate(total_cleanings_count=Count('order__order_scheduler_order')).prefetch_related(Prefetch('order__order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))
        print(payment_histories.count())
        for payment_history in payment_histories:
            print(payment_history.order.order_no)
            data     = requests.get('https://api.xero.com/api.xro/2.0/Payments?where=Reference=="'+payment_history.transaction_id+'"',
                                                                headers=header 
                                                            ).json()
            payments = data['Payments']
            for payment in payments:
                print(payment['PaymentID'])
                delete_payment = requests.post('https://api.xero.com/api.xro/2.0/Payments/'+payment['PaymentID'],
                                                                headers=header,
                                                                data={
                                                                    "Status": "DELETED"
                                                                } 
                                                            )
                print(delete_payment)
            break
                
            
            