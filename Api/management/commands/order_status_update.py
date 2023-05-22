import requests
import json
from django.core.management.base import BaseCommand
from order.models import Order,OrderScheduler
from evaluator.models import Evaluation,EvaluationBook
from senior_team_leader.models import CleaningTeam
from django.db.models import Prefetch
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,IntegerField
from datetime import datetime,date,timedelta
import pytz
from order.models import OrderScheduler

class Command(BaseCommand):
    help = 'updating cleaning cost of visits in customer booked orders'

    def handle(self, *args, **kwargs):

        bookings = Evaluation.objects.filter(is_active=True,booking_evaluation__is_active=True,created__gte=datetime.strptime('01-12-2022','%d-%m-%Y').replace(tzinfo=pytz.utc)).only('id')
        for booking in bookings:
            books = EvaluationBook.objects.filter(evaluation_details__evaluation__id=booking.id,is_active=True).only('id','total_cost')
            for book in books:
                schedules = OrderScheduler.objects.filter(order_scheduler_book=book.id,is_active=True).only('cleaning_cost')

                cleaning_cost_sum          = 0
                total_cleanings            = len(schedules)
                count                      = 0

                for schedule in schedules:
                    print(schedule.cleaning_cost,"pre")
                    count += 1

                    #schedule cleaning cost calculation
                    if int(count) == int(total_cleanings): #final iteration
                        #sum of previous cleaning cost subtracted from book total to adjust the division amount properly.
                        cleaning_cost           = round(book.total_cost-cleaning_cost_sum,2)
                        cleaning_cost_sum       = 0
                    else: #iterations before the final iteration
                        cleaning_cost           = round(book.total_cost/total_cleanings,2)
                        cleaning_cost_sum       += float(cleaning_cost)

                    schedule.cleaning_cost = cleaning_cost
                    schedule.save()
                    print(schedule.cleaning_cost,"post")
        

        
                        