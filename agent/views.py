from django.shortcuts import render
from django.views import View

from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,BooleanField,IntegerField,Value,F,Func,Count
from django.db.models import Prefetch

from user.models import UserProfile
from evaluator.models import Evaluation,EvaluationDetails
from order.models import OrderScheduler,FollowUpScheduler
from senior_team_leader.models import CleaningTeam,FollowUpTeam

from order.forms import OrderSchedulerConfirmationForm,FollowUpSchedulerConfirmationForm

# Create your views here.
class AgentHome(View):
	def get(self,request):

		#Enquiry Details
		try:
			enquiry = Evaluation.objects.filter(is_active=True)
		except:
			enquiry	= None

		today_enquiry_count = enquiry.filter(created__date=timezone.now().date()).count()
		week_enquiry_count  = enquiry.filter(created__date__gte=timezone.now().date()-timedelta(6)).count()	

		#Cleaning Jobs
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(start_at__date=timezone.now().date()).count() 
		week_cleaning_job_count  = cleaning_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		

		#Followup jobs
		try:
			follow_up_job    = FollowUpTeam.objects.filter(is_active=True)
		except:
			follow_up_job	 = None

		today_follow_up_job_count = follow_up_job.filter(start_at__date=timezone.now().date()).count() 
		week_follow_up_job_count  = follow_up_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		

		#Evaluation details of each evaluator for evaluation table
		evaluation_calendar_date	= request.GET.get('evaluation_calendar_date')
		
		try:
			evaluation_date = datetime.strptime(evaluation_calendar_date,'%d-%m-%Y')
		except:
			evaluation_date = timezone.now()
		
		try:
			evaluation_details		  = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related(Prefetch('evaluator_evaluation',queryset=EvaluationDetails.objects.filter(is_active=True,proposed_time__date=evaluation_date.date()),to_attr='evaluation_details'))
		except:
			evaluation_details 		  = None


		#Order and Followup Schedules for date confirmation
		try:
			order_schedules		  = OrderScheduler.objects.filter(is_active=True).exclude(Q(Q(status='CONFIRMED')|Q(status='CANCELLED')))
		except:
			order_schedules		  = None
		
		try:
			follow_up_schedules	  = FollowUpScheduler.objects.filter(is_active=True,).exclude(Q(Q(status='CONFIRMED')|Q(status='CANCELLED')))
		except:
			follow_up_schedules	  = None	

		order_scheduler_confirmation_form    = OrderSchedulerConfirmationForm()	
		followup_scheduler_confirmation_form = FollowUpSchedulerConfirmationForm()	
		
		#cleaning schedule & followup schedule for cleaning calendar			
		cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')
		
		try:
			schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			schedule_date = timezone.now()

		try:
			calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED')))
		except:
			calendar_order_schedules = None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED')))
		except:
			calendar_followup_schedules = None
	
		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&~Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED')))
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&~Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED')))
		except:
			sp_calendar_followup_schedules = None							

		return render(request,'agent/home/home.html',{'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'cleaning_job':cleaning_job,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'follow_up_job':follow_up_job,'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'order_schedules':order_schedules,'follow_up_schedules':follow_up_schedules,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'schedule_date':schedule_date,'order_scheduler_confirmation_form':order_scheduler_confirmation_form,'followup_scheduler_confirmation_form':followup_scheduler_confirmation_form,})