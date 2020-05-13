from django.shortcuts import render
from django.views import View

from django.conf import settings
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,BooleanField,IntegerField,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField
from django.db.models import Prefetch

from user.models import UserProfile
from evaluator.models import Evaluation,EvaluationDetails
from order.models import OrderScheduler,FollowUpScheduler,FeedBack
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember

from order.forms import OrderSchedulerConfirmationForm,FollowUpSchedulerConfirmationForm

from tzlocal import get_localzone

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

		#Feedback Staring
		try:
			feedbacks                 = FeedBack.objects.filter(is_active=True)
		except:
			feedbacks				  = None

		today_average_feedback		  = feedbacks.filter(response_date__date=timezone.now().date()).aggregate(Avg('rating'))['rating__avg']
		week_average_feedback		  = feedbacks.filter(response_date__gte=timezone.now().date()-timedelta(6)).aggregate(Avg('rating'))['rating__avg']	
		
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
			order_schedules		  = OrderScheduler.objects.filter(is_active=True).exclude(Q(Q(status='CONFIRMED')|Q(status='CANCELLED'))).select_related('order__evaluation__customer','customer_address')
		except:
			order_schedules		  = None
		
		try:
			follow_up_schedules	  = FollowUpScheduler.objects.filter(is_active=True,).exclude(Q(Q(status='CONFIRMED')|Q(status='CANCELLED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
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
			calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address')
		except:
			calendar_order_schedules = None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			calendar_followup_schedules = None
	
		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&~Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address')
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&~Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			sp_calendar_followup_schedules = None							

		return render(request,'agent/home/home.html',{'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'today_average_feedback':today_average_feedback,'week_average_feedback':week_average_feedback,'cleaning_job':cleaning_job,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'follow_up_job':follow_up_job,'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'order_schedules':order_schedules,'follow_up_schedules':follow_up_schedules,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'schedule_date':schedule_date,'order_scheduler_confirmation_form':order_scheduler_confirmation_form,'followup_scheduler_confirmation_form':followup_scheduler_confirmation_form,})


class ResourceManagement(View):
	def get(self,request):

		# exact_cleaning_date 				 = timezone.localtime(timezone.now())
		# cleaning_date                        = exact_cleaning_date.replace(hour=00,minute=0,second=0,microsecond=0)

		# exact_cleaning_date_tomorrow         = exact_cleaning_date+timezone.timedelta(days=1)
		# cleaning_date_tomorrow               = exact_cleaning_date_tomorrow.replace(hour=00,minute=0,second=0,microsecond=0)

		# exact_cleaning_date_for_filter_start = exact_cleaning_date+timezone.timedelta(days=-1)
		# cleaning_date_for_filter_start       = exact_cleaning_date_for_filter.replace(hour=18,minute=30,second=0,microsecond=0)
		# cleaning_date_for_filter_end         = .replace(hour=5,minute=30,second=0,microsecond=0)

		# #cleaning_team	    = CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='cleaning_member')).annotate(team_duration=Case(When(start_at__date=cleaning_date.date(),then=ExpressionWrapper(((F('end_at'))-F('start_at'))*Count('cleaning_member_team'),output_field=DurationField())),When(~Q(start_at__date=cleaning_date.date()),then=ExpressionWrapper(((cleaning_date+timedelta(days=1))-F('start_at'))*Count('cleaning_member_team'),output_field=DurationField())),default=0,output_field=DurationField()),   team_average_duration=Case(When(start_at__date=cleaning_date.date(),then=ExpressionWrapper((F('end_at')-F('start_at')),output_field=DurationField())),When(~Q(start_at__date=cleaning_date.date()),then=ExpressionWrapper((F('end_at')-F('start_at')),output_field=DurationField())),default=0,output_field=DurationField()),    team_active_cleaners=Count('cleaning_member_team'),).aggregate(total_duration=Sum(ExpressionWrapper(F('team_duration'),output_field=DurationField())),average_duration=Sum(ExpressionWrapper(F('team_average_duration'),output_field=DurationField())),active_cleaners=Sum('team_active_cleaners'))
		
		# cleaning_team	    = CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='cleaning_member')).annotate(team_active_cleaners=Count('cleaning_member_team'),)
		
		# for team in cleaning_team.filter(Q(Q(start_at__gt=cleaning_date_for_filter)|Q(end_at__gt=cleaning_date_for_filter))):
		# 	print(team)

		# today_cleaning_hours = timedelta()		
		# for team in cleaning_team:

		# 	if timezone.localtime(team.end_at).date()==timezone.localtime(team.start_at).date():
		# 		today_cleaning_hours += (timezone.localtime(team.end_at)-timezone.localtime(team.start_at))*team.team_active_cleaners
			
		# 	if timezone.localtime(team.end_at).date()!=timezone.localtime(team.start_at).date():
		# 		if timezone.localtime(exact_cleaning_date).date() == timezone.localtime(team.start_at).date():
		# 			today_cleaning_hours += (cleaning_date_tomorrow-timezone.localtime(team.start_at))*team.team_active_cleaners 
		# 		else:
		# 			today_cleaning_hours += (timezone.localtime(team.end_at) - cleaning_date_tomorrow)*team.team_active_cleaners	

		#cleaning schedule & followup schedule for cleaning calendar			
		workers_calendar_date	= request.GET.get('workers_calendar_date')
		search                  = request.GET.get('search')
		
		try:
			workers_date = datetime.strptime(workers_calendar_date,'%d-%m-%Y')
		except:
			workers_date = timezone.now()

		if search:
			try:
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER'))&Q(name__icontains=search))
			except:
				workers =  None
		else:
			try:
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER')))
			except:
				workers =  None


		workers_details = workers.prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=workers_date.date())|Q(end_at__date=workers_date.date())) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=workers_date.date())|Q(end_at__date=workers_date.date())) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details'))
		


		return render(request,'agent/resource/resource_management.html',{"workers_details":workers_details,"workers_date":workers_date,"search_query":search})		




















