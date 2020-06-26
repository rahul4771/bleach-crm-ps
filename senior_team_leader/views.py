from django.shortcuts import render,redirect
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsSeniorTeamLeader
from bleach_crm_ps.utils import get_error

import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField
from django.db.models.functions import Cast 
from django.db.models import Prefetch
from django.contrib import messages

from user.models import UserProfile,Address
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp,Investigation,InvestigationMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember

from senior_team_leader.forms import CleaningTeamAssignForm,FollowupTeamAssignForm
# Create your views here.

class StlHome(IsSeniorTeamLeader,View):
	def get(self,request):
		
	    #Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(start_at__date=timezone.now().date()).count() 
		week_cleaning_job_count  = cleaning_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		


		#total workers count
		try:
			total_workers = UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER'))).count()
		except:
			total_workers = 0
		
		#total active workers
		try:
			total_active_workers = CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=timezone.now().date())|Q(end_at__date=timezone.now().date())) )).values_list('member',flat=True).distinct().union(FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=timezone.now().date())|Q(end_at__date=timezone.now().date())) )).values_list('member',flat=True)).distinct().count()
		except:
			total_active_workers = 0	
	
	
		##To find average and total men hour from script data
		try:
			cleaning_teams  = CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_teams  = None
		try:
			follow_up_teams = FollowUpTeam.objects.filter(is_active=True)
		except:
			follow_up_teams = None

	
		today_cleaning_active_teams  = cleaning_teams.filter(Q(Q(start_at__date=timezone.now().date())|Q(end_at__date=timezone.now().date())))
		today_followup_active_teams  = follow_up_teams.filter(Q(Q(start_at__date=timezone.now().date())|Q(end_at__date=timezone.now().date())))
		week_cleaning_active_teams   = cleaning_teams.filter(Q(Q(start_at__gte=timezone.now().date()-timedelta(6))|Q(end_at__gte=timezone.now().date()-timedelta(6))))
		week_followup_active_teams   = follow_up_teams.filter(Q(Q(start_at__gte=timezone.now().date()-timedelta(6))|Q(end_at__gte=timezone.now().date()-timedelta(6))))

		today_date            = timezone.now()
		weekstart_date        = timezone.now().date()-timedelta(6)

		try:
			today_total_team_mens = today_cleaning_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum'] or 0+today_followup_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum'] or 0
		except:
			today_total_team_mens = 0
		try:	
			week_total_team_mens  = week_cleaning_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum'] or 0+week_followup_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum'] or 0
		except:	
			week_total_team_mens  = 0



		#today and weekly active team count
		today_active_teams_count = today_cleaning_active_teams.count()+today_followup_active_teams.count()
		week_active_teams_count  = week_cleaning_active_teams.count()+week_followup_active_teams.count() 


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
 
		try:		
			workers_details = workers.prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=workers_date.date())|Q(end_at__date=workers_date.date())) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=workers_date.date())|Q(end_at__date=workers_date.date())) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details'))
		except:
			workers_details = None	

		#Investigation tasks
		investigation_calendar_date	= request.GET.get('investigation_calendar_date')
		
		try:
			investigation_date = datetime.strptime(investigation_calendar_date,'%d-%m-%Y')
		except:
			investigation_date = timezone.now()
		try:	
			investigations  = Investigation.objects.filter(is_active=True,sheduled_at__date=investigation_date.date(),investigator=request.user,check_out=None).select_related('order__evaluation__customer','order_schedule__customer_address__area','order_schedule__order_scheduler_book').prefetch_related(Prefetch('order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team_details'))
		except:
			investigations  = 	None
			
		#cleaning schedule & followup schedule for cleaning calendar			
		cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')
		
		try:
			schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			schedule_date = timezone.now()

		try:
			calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
		except:
			calendar_order_schedules = None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address','follow_up__investigation__order_schedule__order_scheduler_book')
		except:
			calendar_followup_schedules = None
	
		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&~Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__date=schedule_date.date())&~Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address','follow_up__investigation__order_schedule__order_scheduler_book')
		except:
			sp_calendar_followup_schedules = None

		return render(request,'stl/home/home.html',{'investigation_date':investigation_date,'investigations':investigations,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'schedule_date':schedule_date,"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams})

class TicketDetails(IsSeniorTeamLeader,View):
	def get(self,request):
		
		search                  = request.GET.get('search')
		
		#Followup details
		if search:
			try:
				tickets 	             = FollowUp.objects.select_related('investigation__order_schedule__order__evaluation__customer').filter(is_active=True,investigation__order_schedule__order__evaluation__customer__name__icontains=search).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))
				follow_ups_count         = tickets.count()
			except:
				tickets          = None
				follow_ups_count = 0
		else:
			try:
				tickets 	             = FollowUp.objects.select_related('investigation__order_schedule__order__evaluation__customer').filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))
				follow_ups_count         = tickets.count()
			except:
				tickets          = None
				follow_ups_count = 0


		#followup cleaning count	
		try:
			follow_up_cleaning_count = FollowUpScheduler.objects.filter(is_active=True,work_status='FOLLOW_UP_CLEANING_FULFILLED').count()
		except:
			follow_up_cleaning_count = 0

		#PAGINATION TICKETS		
		page = request.GET.get('page',1) 
		paginator=Paginator(tickets,10)
		try: 
			tickets=paginator.page(page) 
		except PageNotAnInteger:
			tickets=paginator.page(1)
		except EmptyPage:
			tickets = paginator.page(paginator.num_pages) 

		# Get the index of the current page
		index = tickets.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]	
		entry_per_page=(tickets.end_index())-(tickets.start_index())+1	

		return render(request,'stl/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})		
		

class AssigncleaningTeam(View):
	def get(self,request,scheduler_id):

		#shceduled order details
		order_schedule = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book__service_type').get(is_active=True,id=scheduler_id)
	
		cleaning_team_assign_form = CleaningTeamAssignForm()

		active_cleaner1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners     = active_cleaner1.union(active_cleaners2)		

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(~Q(id__in=active_cleaners))
		cleaners            = UserProfile.objects.filter(is_active=True,user_type='CLEANER').filter(~Q(id__in=active_cleaners))


		return render(request,'stl/cleaning/assign_cleaningteam.html',{'cleaning_team_assign_form':cleaning_team_assign_form,'order_schedule':order_schedule,'cleaners':cleaners,'leaders':leaders,})

	def post(self,request,scheduler_id):
		
		#shceduled order details
		order_schedule = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book').get(is_active=True,id=scheduler_id)
		
		cleaning_team_assign_form = CleaningTeamAssignForm(request.POST)
		assigned_cleaners         = request.POST.getlist('assigned_cleaner')

		active_cleaner1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners     = active_cleaner1.union(active_cleaners2)

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(~Q(id__in=active_cleaners))
		cleaners            = UserProfile.objects.filter(is_active=True,user_type='CLEANER').filter(~Q(id__in=active_cleaners))

	    #validation
		check_cleaners_assigned = UserProfile.objects.filter(is_active=True,user_type='CLEANER',id__in=assigned_cleaners).filter(Q(id__in=active_cleaners))
		check_tl_assigned       = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER',id__in=active_cleaners).filter(id=request.POST.get('team_leader'))
				

		if	cleaning_team_assign_form.is_valid() and not check_cleaners_assigned and not check_tl_assigned and len(assigned_cleaners)==int(request.POST.get('no_of_cleaners')):
			cleaning_team_assign_form_save                   = cleaning_team_assign_form.save(commit=False)
			cleaning_team_assign_form_save.order_scheduler_id= scheduler_id
			cleaning_team_assign_form_save.start_at          = order_schedule.start_at
			cleaning_team_assign_form_save.end_at            = order_schedule.end_at
			cleaning_team_assign_form_save.created_by        = request.user
			cleaning_team_assign_form_save.save()

			#cleaners
			assigned_cleaners_list   = []
			for cleaner in assigned_cleaners:
				assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team_assign_form_save,member_id=cleaner,start_at=order_schedule.start_at,end_at=order_schedule.end_at))
			assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team_assign_form_save,member=cleaning_team_assign_form_save.team_leader,start_at=order_schedule.start_at,end_at=order_schedule.end_at))
			#bulk create
			CleaningTeamMember.objects.bulk_create(assigned_cleaners_list)	

			OrderScheduler.objects.filter(id=scheduler_id).update(work_status='CLEANING_TEAM_ASSIGNED')
		else:
			if len(assigned_cleaners)!=int(request.POST.get('no_of_cleaners')):
				messages.error(request,"Assign Specified Number of cleaners")
			else:	
				messages.error(request,get_error(cleaning_team_assign_form))

			return render(request,'stl/cleaning/assign_cleaningteam.html',{'cleaning_team_assign_form':cleaning_team_assign_form,'order_schedule':order_schedule,'cleaners':cleaners,'leaders':leaders,})	

		messages.success(request,"Cleaning Team Succesfully Assigned")

		return redirect('stl:stldash-board')	

class AssignFollowupTeam(View):
	def get(self,request,scheduler_id):

		#shceduled order details
		followup_schedule = FollowUpScheduler.objects.select_related('follow_up__investigation__order','follow_up__investigation__order_schedule__order_scheduler_book__service_type','customer_address').get(is_active=True,id=scheduler_id)
	
		follow_up_team_assign_form = FollowupTeamAssignForm()
		assigned_cleaners          = request.POST.getlist('assigned_cleaner')

		active_cleaner1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners     = active_cleaner1.union(active_cleaners2)

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(~Q(id__in=active_cleaners))
		cleaners            = UserProfile.objects.filter(is_active=True,user_type='CLEANER').filter(~Q(id__in=active_cleaners))


		return render(request,'stl/cleaning/assign_followupteam.html',{'follow_up_team_assign_form':follow_up_team_assign_form,'followup_schedule':followup_schedule,'cleaners':cleaners,'leaders':leaders,})

	def post(self,request,scheduler_id):
	
		#shceduled order details
		followup_schedule = FollowUpScheduler.objects.select_related('follow_up__investigation__order','follow_up__investigation__order_schedule__order_scheduler_book__service_type','customer_address').get(is_active=True,id=scheduler_id)	

		follow_up_team_assign_form = FollowupTeamAssignForm(request.POST)



		active_cleaner1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners     = active_cleaner1.union(active_cleaners2)
	
		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(~Q(id__in=active_cleaners))
		cleaners            = UserProfile.objects.filter(is_active=True,user_type='CLEANER').filter(~Q(id__in=active_cleaners))

		#validation
		check_cleaners_assigned = UserProfile.objects.filter(is_active=True,user_type='CLEANER',id__in=assigned_cleaners).filter(Q(id__in=active_cleaners))
		check_tl_assigned       = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER',id__in=active_cleaners).filter(id=request.POST.get('team_leader'))
		

		
		if	follow_up_team_assign_form.is_valid() and not check_cleaners_assigned and not check_tl_assigned and len(assigned_cleaners)==int(request.POST.get('no_of_cleaners')):
			follow_up_team_assign_form_save                   = follow_up_team_assign_form.save(commit=False)
			follow_up_team_assign_form_save.followup_scheduler_id= scheduler_id
			follow_up_team_assign_form_save.start_at          = followup_schedule.start_at
			follow_up_team_assign_form_save.end_at            = followup_schedule.end_at
			follow_up_team_assign_form_save.created_by        = request.user
			follow_up_team_assign_form_save.save()

			#cleaners
			assigned_cleaners_list   = []
			for cleaner in assigned_cleaners:
				assigned_cleaners_list.append(FollowUpTeamMember(team=follow_up_team_assign_form_save,member_id=cleaner,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at))
			assigned_cleaners_list.append(FollowUpTeamMember(team=follow_up_team_assign_form_save,member=follow_up_team_assign_form_save.team_leader,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at))
			#bulk create
			FollowUpTeamMember.objects.bulk_create(assigned_cleaners_list)	

			FollowUpScheduler.objects.filter(id=scheduler_id).update(work_status='CLEANING_TEAM_ASSIGNED')
		else:

			if len(assigned_cleaners)!=int(request.POST.get('no_of_cleaners')):
				messages.error(request,"Assign Specified Number of cleaners")
			else:	
				messages.error(request,get_error(follow_up_team_assign_form))

			return render(request,'stl/cleaning/assign_followupteam.html',{'follow_up_team_assign_form':follow_up_team_assign_form,'followup_schedule':followup_schedule,'cleaners':cleaners,'leaders':leaders,})	

		messages.success(request,"FollowupTeam Team Succesfully Assigned")

		return redirect('stl:stldash-board')






class InvestigationTask(View):
	def get(self,request,investigation_id):
		
		try:
			investigation_details = Investigation.objects.select_related('order_schedule__customer_address__area','order_schedule__order_scheduler_book__service_type','investigator','order__evaluation__customer').get(id=investigation_id)
		except:
			investigation_details = None

		#save checkin_time
		investigation_details.check_in = timezone.now()
		investigation_details.save()

		return render(request,'stl/ticket/investigation.html',{'investigation_details':investigation_details})

	def post(self,request,investigation_id):
		follow_up_approved = request.POST.get('isapproved')

		try:
			investigation = Investigation.objects.select_related('order_schedule__customer_address').get(id=investigation_id)
		except:
			investigation = None	
		
		if follow_up_approved == 'yes':
			no_of_cleaners = request.POST.get('no_of_cleaners')
			cleaning_hours = request.POST.get('cleaning_hours')
			
			tendative_date = request.POST.get('tendative_date')
			tendative_time = request.POST.get('tendative_time')
			start_date_time = datetime.strptime(tendative_date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
			end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours))

			Investigation.objects.filter(id=investigation_id).update(is_followup_approved=True,check_out=timezone.now(),notes=request.POST.get('notes'))
			follow_up = FollowUp.objects.create(investigation_id=investigation_id,status='INVESTIGATOR_APPROVED',no_of_cleaners=no_of_cleaners,cleaning_hours=cleaning_hours)
			follow_up_scheduler = FollowUpScheduler.objects.create(follow_up=follow_up,start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address)
		
		else:
			Investigation.objects.filter(id=investigation_id).update(is_followup_approved=False,check_out=timezone.now(),notes=request.POST.get('notes'))

		#To Save Media
			medias = request.FILES.getlist('media')
			if not medias==['']:
				for media in medias:
					InvestigationMedia.objects.create(
					        investigation_id=investigation_id,
					        media=media,
					        )

		messages.success(request,"Investigation Form submitted succesfully")	
		return redirect('stl:stldash-board')		