from django.core.management.base import BaseCommand

from evaluator.models import Evaluation,EvaluationDetails
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
		today_end   = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)+timedelta(1)
		
		#update expiry
		expired_evaluations = Evaluation.objects.filter(quatation_expiry_date__lte=today_end,quatation_status='PENDING').update(quatation_status='EXPIRED')
		expired_invoices    = Order.objects.select_related('evaluation').filter(evaluation__quatation_expiry_date__lte=today_end,evaluation__quatation_status='PENDING').update(invoice_status='CANCELLED')

		#remove unwanted evaluations
		unwanted_evaluations = Evaluation.objects.filter(created__lt=today_end,quatation_status__isnull=True).prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True),to_attr='evaluationdetails')).annotate(active_evaluations_count=Sum(Case(When(Q(Q(evaluation_details__proposed_time__lt=today_end)|Q(evaluation_details__proposed_time__isnull=True)),then=1),default=0,output_field=IntegerField())),completed_evaluations_count=Sum(Case(When(evaluation_details__status='EVALUATED',then=1),default=0,output_field=IntegerField()))).exclude(active_evaluations_count=F('completed_evaluations_count')).delete()

		#expired after 2 weeks if not paid
		try:
			orders         = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',order_status__isnull=False).order_by('-id')
		except:
			orders         = None

		pending_payments = orders.filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules')).annotate(Count('order_scheduler_order'))

		for payment in pending_payments:

			if payment.evaluation.payment_method == 'PREPAID' and payment.payment_status != 'COMPLETED':
				very_old_cleaning   = payment.orderschedules[0]
				passed_days = (timezone.now()-very_old_cleaning.start_at).days

				if passed_days >= 14:
					Evaluation.objects.filter(id=payment.evaluation.id).update(quatation_status='EXPIRED')
					Order.objects.select_related('evaluation').filter(is_active=True,evaluation__id=payment.evaluation.id).update(invoice_status='CANCELLED')

			if payment.evaluation.payment_method == 'BREAKDOWN' and payment.preamount_paid == 0:
				very_old_cleaning   = payment.orderschedules[0]
				passed_days = (timezone.now()-very_old_cleaning.start_at).days

				if passed_days >= 14:
					Evaluation.objects.filter(id=payment.evaluation.id).update(quatation_status='EXPIRED')
					Order.objects.select_related('evaluation').filter(is_active=True,evaluation__id=payment.evaluation.id).update(invoice_status='CANCELLED')










