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

    def handle(self, *args, **kwargs):

        invoice_numbers = [
                202200006, 202200014, 202200033, 202200046]

        # invoice_numbers = [
        #         202200006, 202200014, 202200033, 202200046, 202200070, 202200050, 202200067, 202104753, 202200263, 202200203, 
        #         202200337, 
        #         202200341, 
        #         202200383, 
        #         202200380, 
        #         202200363, 
        #         202200414, 
        #         202200403, 
        #         202200397, 
        #         202200436, 
        #         202104778, 
        #         202200445, 
        #         202200471, 
        #         202200463, 
        #         "202100829B", 
        #         202200474, 
        #         202200492, 
        #         "202200497B", 
        #         202200498, 
        #         "202200497A", 
        #         202200506, 
        #         202200536, 
        #         202200540, 
        #         202200436, 
        #         202200584, 
        #         202200611, 
        #         202200614, 
        #         202200667, 
        #         202200684, 
        #         202200681, 
        #         202200716, 
        #         202200786, 
        #         202200802, 
        #         202200754, 
        #         202200805, 
        #         202200814, 
        #         202200817, 
        #         202200822, 
        #         202200838, 
        #         202200837, 
        #         202200823, 
        #         202200820, 
        #         202200852, 
        #         202200867, 
        #         202200890, 
        #         202200876, 
        #         202200886, 
        #         202200893, 
        #         202200920, 
        #         202200772, 
        #         202200934, 
        #         202200933, 
        #         202200948, 
        #         202200965, 
        #         202200997, 
        #         202201013, 
        #         202201011, 
        #         202201003, 
        #         202201027, 
        #         202201044, 
        #         202201060, 
        #         202201039, 
        #         202201028, 
        #         202201058, 
        #         202201080, 
        #         202201125, 
        #         202201136, 
        #         202201128, 
        #         202201137, 
        #         202201158, 
        #         202201174, 
        #         202201170, 
        #         202201188, 
        #         202201191, 
        #         202200848, 
        #         202201194, 
        #         202201198, 
        #         202201213, 
        #         202201222, 
        #         202201228, 
        #         202201255, 
        #         202201279, 
        #         202201280, 
        #         202201249, 
        #         202201296, 
        #         202201310, 
        #         202201298, 
        #         202201307, 
        #         202201330, 
        #         202201363, 
        #         202201348, 
        #         202201372, 
        #         202201376, 
        #         202201393, 
        #         202201224, 
        #         202201400, 
        #         202201402, 
        #         202201410, 
        #         202201416, 
        #         202201341, 
        #         202201440, 
        #         202201436, 
        #         202201233, 
        #         202201482, 
        #         202201432, 
        #         202201500, 
        #         202201491, 
        #         202201520, 
        #         202201555, 
        #         202201553, 
        #         202201547, 
        #         202201537, 
        #         202201592, 
        #         202201546, 
        #         202201575, 
        #         202201620, 
        #         202201611, 
        #         202201642, 
        #         202201633, 
        #         202201624, 
        #         202201664, 
        #         202201688, 
        #         202201689, 
        #         202201714, 
        #         202201720, 
        #         202201716, 
        #         202201713, 
        #         202202613, 
        #         202202697, 
        #         202202563, 
        #         202202741, 
        #         202202765, 
        #         202202944, 
        #         202203017, 
        #         202203080, 
        #         202203140, 
        #         202203142, 
        #         202203146, 
        #         202203148, 
        #         202203173, 
        #         202203105, 
        #         202203213, 
        #         202203202, 
        #         202203224, 
        #         202203223, 
        #         "202200480A", 
        #         202200535, 
        #         "202201096A", 
        #         202201105, 
        #         202201043, 
        #         202201456, 
        #         "202201544A", 
        #         202201653, 
        #         "202202599E", 
        #         "202202599M", 
        #         202203017, 
        #         202203080, 
        #         202203140, 
        #         202203142, 
        #         202203146, 
        #         202203148, 
        #         202203173, 
        #         202203105, 
        #         202203213, 
        #         202203202, 
        #         202203224, 
        #         202203223
        #     ]

        invoice_nos = ','.join(str(item) for item in invoice_numbers)
            
            
        print(invoice_nos,"invs")
        # for invoice_number in invoice_numbers:
        # time.sleep(5)

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

        print('https://api.xero.com/api.xro/2.0/Invoices/?InvoiceNumbers="'+invoice_nos+'"',"urlss")
        
        invoices =  requests.request("GET", 'https://api.xero.com/api.xro/2.0/Invoices/?InvoiceNumbers="'+invoice_nos+'"', headers=header).json()

        print(invoices['Invoices'],"inv check")