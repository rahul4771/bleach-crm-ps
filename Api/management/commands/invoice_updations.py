from django.core.management.base import BaseCommand

from order.models import Order

from django.utils import timezone
from datetime import timedelta,date,datetime
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast
from django.db.models import Prefetch

class Command(BaseCommand):
    help = 'Automatic Updations'
    def handle(self, *args, **kwargs):
        #SUBSCRIPTION Invoices
        subscriptions = Order.objects.select_related('evaluation__customer').filter(evaluation__quatation_status='APPROVED',payment_method='SUBSCRIPTION',payment_status='PENDING',subscription_topay__gt=0)
        print(subscriptions,"subscriptions")
        print(subscriptions.count())
        #PREPAID, CLEANING BEFORE Invoices
        before_orders = Order.objects.select_related('evaluation__customer').filter(evaluation__quatation_status='APPROVED',payment_status='PENDING').filter(Q(evaluation__payment_method='PREPAID')|Q(Q(evaluation__payment_method='BREAKDOWN')&Q(preamount_paid__gt=0)))
        print(before_orders,"before_orders")
        print(before_orders.count())
        #POSTPAID, CLEANING AFTER Invoices
        after_orders  = Order.objects.select_related('evaluation__customer').prefetch_related('order_scheduler_order').filter(evaluation__quatation_status='APPROVED',payment_status='PENDING').filter(Q(payment_method='POSTPAID')|Q(Q(evaluation__payment_method='BREAKDOWN')&Q(postamount_paid__gt=0))).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()),remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count')).filter(remaining_cleanings_count=0)
        print(after_orders,"after_orders")
        print(after_orders.count())
