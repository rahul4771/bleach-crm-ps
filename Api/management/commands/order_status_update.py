import requests
import json
from django.core.management.base import BaseCommand
from order.models import Order,OrderScheduler
import os
import logging

# credit card test logging
logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'log/order_status_updates.log'), level=logging.INFO)

class Command(BaseCommand):
    help = 'Order Status Update'

    def handle(self, *args, **kwargs):

        listed_orders = [
            BLC20221010084,
            BLC20210710188,
            BLC20210610361,
            BLC20210610360,
            BLC20210510338,
            BLC20210410129,
            BLC20210310196,
            BLC20210310164,
            BLC20210210170,
            BLC20210210396,
            BLC20210310376,
            BLC20210410067,
            BLC20210410120,
            BLC20210410349,
            BLC20210710085,
            BLC20210710127,
            BLC20210710173,
            BLC20210710328,
            BLC20210810131,
            BLC20210810325,
            BLC20210810381,
            BLC20210810398,
            BLC20210910041,
            BLC20210910064,
            BLC20210910113,
            BLC20210910195,
            BLC20210910324,
            BLC20210910368,
            BLC20211010005,
            BLC20211010055,
            BLC20211010161,
            BLC20211010169,
            BLC20211010229,
            BLC20211010290,
            BLC20211010299,
            BLC20211010319,
            BLC20211010403,
            BLC20211110233,
            BLC20211110251,
            BLC20211110309,
            BLC20211110366,
            BLC20211210002,
            BLC20211210194,
            BLC20211210306,
            BLC20220110230,
            BLC20220110377,
            BLC20220110361,
            BLC20220210081,
            BLC20220210257,
            BLC20220210271,
            BLC20220310096,
            BLC20220310114,
            BLC20220310093,
            BLC20220310120,
            BLC20220310122,
            BLC20220310126,
            BLC20220310188,
            BLC20220310212,
            BLC20220310233,
            BLC20220310308,
            BLC20220310384,
            BLC20220310407,
            BLC20220410035,
            BLC20220410045,
            BLC20220410024,
            BLC20220410121,
            BLC20220410120,
            BLC20220410179,
            BLC20220410185,
            BLC20220410187,
            BLC20220410227,
            BLC20220410229,
            BLC20220410244,
            BLC20220510015,
            BLC20220510236,
            BLC20220610043,
            BLC20220710090,
            BLC20220710153,
            BLC20220810151,
            BLC20220810173,
            BLC20220810232,
            BLC20220910001,
            BLC20220910047,
            BLC20220910060,
            BLC20220910061,
            BLC20220910052,
            BLC20220910070,
            BLC20220910075,
            BLC20220910068,
            BLC20221010004,
            BLC20221010240,
            BLC20230110109
        ]

        system_orders = Order.objects.filter(order_no__in=listed_orders)

        logging.info(system_orders)