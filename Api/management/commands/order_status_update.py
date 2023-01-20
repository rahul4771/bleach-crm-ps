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
                count += 1
                schedules = OrderScheduler.objects.filter(Q(order=order) & Q( Q(work_status='CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_TEAM_ASSIGNED') ))

                for schedule in schedules:
                    cleaning_team = CleaningTeam.objects.filter(order_scheduler=schedule)
                    
                    for team in cleaning_team:
                        if team.check_in == None:
                            team.check_in = datetime.now()
                        if team.check_out == None:
                            team.check_out = datetime.now()
                        team.save()
                        print(team.check_in,team.check_out,"team")
                    
                    schedule.work_status = 'CLEANING_FULFILLED'
                    schedule.save()
                    print(schedule.work_status,"schedule")

                order.order_status = 'ORDER_CLOSED'
                order.save()
                print(count,order.order_no,order.order_status,"order")
                        