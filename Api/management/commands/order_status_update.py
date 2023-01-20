import requests
import json
from django.core.management.base import BaseCommand
from order.models import Order,OrderScheduler
from senior_team_leader.models import CleaningTeam
from django.db.models import Prefetch
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,IntegerField

class Command(BaseCommand):
    help = 'Order Status Update'

    def handle(self, *args, **kwargs):

        listed_orders = [
            'BLC20210210396',
            'BLC20210310376',
            'BLC20210410067',
            'BLC20210710085',
            'BLC20210810131',
            'BLC20210810381',
            'BLC20210810398',
            'BLC20211010161',
            'BLC20211010169',
            'BLC20211010229',
            'BLC20211010403',
            'BLC20211210194',
            'BLC20211210306',
            'BLC20220310188',
            'BLC20220410229',
            'BLC20220510015',
            'BLC20220510236',
            'BLC20220610043',
            'BLC20220710090'
        ]

        system_orders = Order.objects.filter(order_no__in=listed_orders)

        count = 0
        for order in system_orders:
            if order.payment_status == 'COMPLETED' :
                # order.order_status = 'ORDER_CLOSED'
                # order.save()
                schedules = OrderScheduler.objects.filter(Q(order=order) & Q( Q(work_status='CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_TEAM_ASSIGNED') ))

                for schedule in schedules:
                    if schedule.work_status == 'CLEANING_IN_PROGRESS':
                        cleaning_team = CleaningTeam.objects.filter(order_scheduler=schedule,check_out=None)
                        
                        for team in cleaning_team:
                            print(order.order_no,team.check_in,team.check_out,"team")

                    print(order.order_no,schedule.work_status,"schedule")
                
                count += 1
                print(count,order.order_no,order.order_status,"order")