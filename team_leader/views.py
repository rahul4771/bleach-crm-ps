from django.shortcuts import render,redirect
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsTeamLeader

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
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia

# Create your views here.

class TlHome(IsTeamLeader,View):
	def get(self,request):
		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(start_at__date=timezone.now().date()).count() 
		week_cleaning_job_count  = cleaning_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		

		#Investigation Count
		try:
			investigation = Investigation.objects.filter(is_active=True,investigator=request.user)
		except:
			investigation = None	

		today_investigation_count = investigation.filter(sheduled_at__date=timezone.now().date()).count()
		week_investigation_count   = investigation.filter(sheduled_at__gte=timezone.now().date()-timedelta(6)).count()	

		##To find average and total hour  team leader 
		try:
			cleaning_teams  = CleaningTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			cleaning_teams  = None
		try:
			follow_up_teams = FollowUpTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			follow_up_teams = None

		today_cleaning_active_teams  = cleaning_teams.filter(Q(Q(start_at__date=timezone.now().date())|Q(end_at__date=timezone.now().date())))
		today_followup_active_teams  = follow_up_teams.filter(Q(Q(start_at__date=timezone.now().date())|Q(end_at__date=timezone.now().date())))
		week_cleaning_active_teams   = cleaning_teams.filter(Q(Q(start_at__gte=timezone.now().date()-timedelta(6))|Q(end_at__gte=timezone.now().date()-timedelta(6))))
		week_followup_active_teams   = follow_up_teams.filter(Q(Q(start_at__gte=timezone.now().date()-timedelta(6))|Q(end_at__gte=timezone.now().date()-timedelta(6))))
		

		today_date            = timezone.now()
		weekstart_date        = timezone.now().date()-timedelta(6)

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
			cleaning_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			cleaning_date = timezone.now()

		try:
			calendar_order_cleaning = CleaningTeam.objects.filter(Q(Q(Q(start_at__contains=cleaning_date.date())&Q(end_at__contains=cleaning_date.date()))&Q(team_leader=request.user))).select_related('order_scheduler__order_scheduler_book','order_scheduler__order__evaluation__customer','order_scheduler__customer_address')
		except:
			calendar_order_cleaning = None

		try:
			calendar_followup_cleaning = FollowUpTeam.objects.filter(Q(Q(Q(start_at__date=cleaning_date.date())&Q(end_at__date=cleaning_date.date()))&Q(team_leader=request.user))).select_related('followup_scheduler__follow_up__investigation__order__evaluation__customer','followup_scheduler__customer_address')
		except:
			calendar_followup_cleaning = None
	
		try:
			sp_calendar_order_cleaning = CleaningTeam.objects.filter(Q(Q(Q(start_at__date=cleaning_date.date())&~Q(end_at__date=cleaning_date.date()))&Q(team_leader=request.user))).select_related('order_scheduler__order__evaluation__customer','order_scheduler__customer_address')
		except:
			sp_calendar_order_cleaning = None

		try:
			sp_calendar_followup_cleaning = FollowUpTeam.objects.filter(Q(Q(Q(start_at__date=cleaning_date.date())&~Q(end_at__date=cleaning_date.date()))&Q(team_leader=request.user))).select_related('followup_scheduler__follow_up__investigation__order__evaluation__customer','followup_scheduler__customer_address')
		except:
			sp_calendar_followup_cleaning = None

		return render(request,'tl/home/home.html',{"today_cleaning_job_count":today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'today_cleaning_active_teams':today_cleaning_active_teams,'week_cleaning_active_teams':week_cleaning_active_teams,'today_followup_active_teams':today_followup_active_teams,'week_followup_active_teams':week_followup_active_teams,'today_date':today_date,'weekstart_date':weekstart_date,'investigation_date':investigation_date,'investigations':investigations,'calendar_order_cleaning':calendar_order_cleaning,'calendar_followup_cleaning':calendar_followup_cleaning,'sp_calendar_order_cleaning':sp_calendar_order_cleaning,'sp_calendar_followup_cleaning':sp_calendar_followup_cleaning,'cleaning_date':cleaning_date,'today_investigation_count':today_investigation_count,'week_investigation_count':week_investigation_count})

class TicketDetails(IsTeamLeader,View):
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

		return render(request,'tl/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})		
		
class InvestigationTask(View):
	def get(self,request,investigation_id):
		
		try:
			investigation_details = Investigation.objects.select_related('order_schedule__customer_address__area','order_schedule__order_scheduler_book__service_type','investigator','order__evaluation__customer').get(id=investigation_id)
		except:
			investigation_details = None

		#save checkin_time
		investigation_details.check_in = timezone.now()
		investigation_details.save()

		return render(request,'tl/ticket/investigation.html',{'investigation_details':investigation_details})

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
		return redirect('tl:tldash-board')	

class Cleaning(View):
	def get(self,request,team_id):

		try:
			cleaning_team_detail = CleaningTeam.objects.select_related('team_leader','drop_off_driver','pick_up_driver','order_scheduler__order_scheduler_book__service_type','order_scheduler__order_scheduler_book__cleaning_method','order_scheduler__order_scheduler_book__cleaning_method','order_scheduler__order_scheduler_book__location_type','order_scheduler__order_scheduler_book','order_scheduler__customer_address').get(is_active=True,id=team_id)
		except:	
			cleaning_team_detail = None

		#checkin save	
		if cleaning_team_detail: 
			if not cleaning_team_detail.check_in:
				cleaning_team_detail.check_in                    = timezone.now()
			cleaning_team_detail.order_scheduler.work_status = 'CLEANING_IN_PROGRESS'
			cleaning_team_detail.save()	
			cleaning_team_detail.order_scheduler.save()
		
		return render(request,'tl/cleaning/cleaning.html',{"cleaning_team_detail":cleaning_team_detail,})
	def post(self,request,team_id):
		
		#checkout save
		try:
			cleaning_team_detail = CleaningTeam.objects.select_related('order_scheduler__order').get(is_active=True,id=team_id)
		except:	
			cleaning_team_detail = None

		#checkin save	
		if cleaning_team_detail: 
			cleaning_team_detail.check_out                    = timezone.now()
			cleaning_team_detail.order_scheduler.work_status  = 'CLEANING_FULFILLED'
			cleaning_team_detail.order_scheduler.order.order_status = 'ORDER_IN_PROGRESS'
			cleaning_team_detail.save()
			cleaning_team_detail.order_scheduler.save()
			cleaning_team_detail.order_scheduler.order.save()	

		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				CleaningTeamMedia.objects.create(
				        team_id=team_id,
				        media=media,
				        )

		messages.success(request,"Checkout Succesfully")
				
		return redirect('tl:tldash-board')

class FollowupCleaning(View):
	def get(self,request,team_id):

		followup_team_detail = FollowUpTeam.objects.select_related('team_leader','drop_off_driver','pick_up_driver','followup_scheduler__follow_up__investigation__investigator','followup_scheduler__follow_up__investigation__order','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__service_type','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__cleaning_method','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__location_type','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book','followup_scheduler__customer_address').get(is_active=True,id=team_id)
		

		print(followup_team_detail)	

		#checkin save	
		if followup_team_detail: 
			if not followup_team_detail.check_in:
				followup_team_detail.check_in                       = timezone.now()
			followup_team_detail.followup_scheduler.work_status     = 'FOLLOW_UP_CLEANING_IN_PROGRESS'
			followup_team_detail.save()	
			followup_team_detail.followup_scheduler.save()
		
		return render(request,'tl/cleaning/followup_cleaning.html',{"followup_team_detail":followup_team_detail,})

	def post(self,request,team_id):
		
		#checkout save
		try:
			followup_team_detail = FollowUpTeam.objects.select_related('followup_scheduler__follow_up').get(is_active=True,id=team_id)
		except:	
			followup_team_detail = None

		#checkin save	
		if followup_team_detail: 
			followup_team_detail.check_out                         = timezone.now()
			followup_team_detail.followup_scheduler.work_status    = 'FOLLOW_UP_CLEANING_FULFILLED'
			followup_team_detail.followup_scheduler.follow_up.status= 'FOLLOWUP_IN_PROGRESS'

			followup_team_detail.save()
			followup_team_detail.followup_scheduler.save()
			followup_team_detail.followup_scheduler.follow_up.save()	

		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				FollowUpTeamMedia.objects.create(
				        team_id=team_id,
				        media=media,
				        )

		messages.success(request,"Checkout Succesfully")
				
		return redirect('tl:tldash-board')