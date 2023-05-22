import requests
import json
from django.core.management.base import BaseCommand
from order.models import Order,OrderScheduler
from evaluator.models import Evaluation
from senior_team_leader.models import CleaningTeam
from django.db.models import Prefetch
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,IntegerField
from datetime import datetime,date,timedelta
import pytz

class Command(BaseCommand):
    help = 'Order Status Update'

    def handle(self, *args, **kwargs):

        bookings = Evaluation.objects.filter(is_active=True,booking_evaluation__is_active=True,created__gte=datetime.strptime('01-12-2022','%d-%m-%Y').replace(tzinfo=pytz.utc))

        

        
                        