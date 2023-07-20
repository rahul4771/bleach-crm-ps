import requests
import json

from django.core.management.base import BaseCommand

from user.models import UserProfile

from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch
from order.models import OrderScheduler

class Command(BaseCommand):
    help = 'Automatic Invoice Generations'

    def handle(self, *args, **kwargs):
        # customers = UserProfile.objects.all()

        # first_num = 20000000
        # for customer in customers:
        #     first_num = int(first_num+1)
        #     print(first_num,"mob")
        #     customer.mobile_number = first_num
        #     customer.bleach_mobile_number = first_num
        #     customer.email = str(first_num)+'@bleachtest.kw'
        #     customer.save()

        OrderScheduler.objects.filter(order__order_no='BLC20230710070').update(cleaning_cost=265)