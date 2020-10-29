from django.core.management.base import BaseCommand

from evaluator.models import Evaluation,EvaluationDetails

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

		#remove unwanted evaluations
		unwanted_evaluations = Evaluation.objects.filter(created__lt=today_end,quatation_status__isnull=True).prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True),to_attr='evaluationdetails')).annotate(active_evaluations_count=Sum(Case(When(Q(Q(evaluation_details__proposed_time__lt=today_end)|Q(evaluation_details__proposed_time__isnull=True)),then=1),default=0,output_field=IntegerField())),completed_evaluations_count=Sum(Case(When(evaluation_details__status='EVALUATED',then=1),default=0,output_field=IntegerField()))).exclude(active_evaluations_count=F('completed_evaluations_count')).delete()