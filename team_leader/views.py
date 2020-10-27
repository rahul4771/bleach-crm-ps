from django.shortcuts import render,redirect
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsTeamLeader

import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast 
from django.db.models import Prefetch
from django.contrib import messages

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp,Investigation,InvestigationMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia

# Create your views here.


def UpdateKeynoteStatus(request):
	keynote_id     = request.GET.get('keynote_id')
	keynote_status = request.GET.get('status')

	if keynote_status == 'true':
		EvaluationSectionKeynote.objects.filter(id=keynote_id).update(completion_status=True)
	else:
		EvaluationSectionKeynote.objects.filter(id=keynote_id).update(completion_status=False)
		
	data = {}

	data['keynote_id']     = keynote_id
	data['keynote_status'] = keynote_status

	return JsonResponse(data)




class TlHome(IsTeamLeader,View):
	def get(self,request):

		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)

		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))).count() 
		week_cleaning_job_count  = cleaning_job.filter(Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end))).count()
				

		#Investigation Count
		try:
			investigation = Investigation.objects.filter(is_active=True,investigator=request.user)
		except:
			investigation = None	

		today_investigation_count = investigation.filter(sheduled_at__gte=count_today_start,sheduled_at__lt=count_today_end).count()
		week_investigation_count   = investigation.filter(sheduled_at__gte=count_today_end-timedelta(7),sheduled_at__lt=count_today_end).count()	

		##To find average and total hour  team leader 
		try:
			cleaning_teams  = CleaningTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			cleaning_teams  = None
		try:
			follow_up_teams = FollowUpTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			follow_up_teams = None

		today_cleaning_active_teams  = cleaning_teams.filter(Q(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))))
		today_followup_active_teams  = follow_up_teams.filter(Q(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))))
		week_cleaning_active_teams   = cleaning_teams.filter(Q( Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end)) ))
		week_followup_active_teams   = follow_up_teams.filter(Q( Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end)) ))
		

		today_date            = timezone.now()
		weekstart_date        = timezone.now().date()-timedelta(6)


		try:
			today_total_team_mens = today_cleaning_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+today_cleaning_active_teams.count() or 0+today_followup_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+today_followup_active_teams.count() or 0
		except:
			today_total_team_mens = 0
		try:	
			week_total_team_mens  = week_cleaning_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+week_cleaning_active_teams.count() or 0+week_followup_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+week_followup_active_teams.count() or 0
		except:	
			week_total_team_mens  = 0


		#Investigation tasks
		investigation_to_date         = (timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)).replace(tzinfo=None) 	

		try:	
			investigations  = Investigation.objects.filter(is_active=True,investigator=request.user,check_out=None).select_related('order__evaluation__customer','order_schedule__customer_address__area','order_schedule__order_scheduler_book').prefetch_related(Prefetch('order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team_details')).annotate(color_status=Case(When(Q(Q(sheduled_at__gte=investigation_to_date) & Q(sheduled_at__lt=investigation_to_date+timedelta(1)) & Q(sheduled_at__lte=timezone.now())), then=Value('yellow')),
	                  When(Q(Q(sheduled_at__gte=investigation_to_date) & Q(sheduled_at__lt=investigation_to_date+timedelta(1)) & Q(sheduled_at__gt=timezone.now())), then=Value('green')),When(Q(sheduled_at__gte=investigation_to_date+timedelta(1)), then=Value('blue')),
	                  default=Value('red'),
	                  output_field=CharField(),))
		except:
			investigations  = 	None


		#My cleanings	
		my_cleaning_calendar_date	= request.GET.get('my_cleaning_calendar_date')
		
		try:
			my_cleaning_date = datetime.strptime(my_cleaning_calendar_date,'%d-%m-%Y')
		except:
			my_cleaning_date = timezone.now().replace(tzinfo=None)

		my_cleaning_date_start = my_cleaning_date.replace(hour=0,minute=0,second=0,microsecond=0)
		my_cleaning_date_end   = my_cleaning_date_start+timedelta(1)


		try:	
			my_cleanings  = CleaningTeam.objects.filter(Q(Q(Q(start_at__gte=my_cleaning_date_start)&Q(start_at__lt=my_cleaning_date_end))&Q(team_leader=request.user))).select_related('order_scheduler__order_scheduler_book__service_type','order_scheduler__order__evaluation__customer','order_scheduler__customer_address')
		except:
			my_cleanings  = None
		try:
			my_followups  = FollowUpTeam.objects.filter(Q(Q(Q(start_at__gte=my_cleaning_date_start)&Q(start_at__lt=my_cleaning_date_end))&Q(team_leader=request.user))).select_related('followup_scheduler__follow_up__investigation__order__evaluation__customer','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__service_type','followup_scheduler__customer_address')
		except:
			my_followups  = None		

		return render(request,'tl/home/home.html',{"today_cleaning_job_count":today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'today_cleaning_active_teams':today_cleaning_active_teams,'week_cleaning_active_teams':week_cleaning_active_teams,'today_followup_active_teams':today_followup_active_teams,'week_followup_active_teams':week_followup_active_teams,'today_date':today_date,'weekstart_date':weekstart_date,'investigations':investigations,'today_investigation_count':today_investigation_count,'week_investigation_count':week_investigation_count,'my_cleaning_date':my_cleaning_date,"my_cleanings":my_cleanings,"my_followups":my_followups,'today_total_team_mens':today_total_team_mens,'week_total_team_mens':week_total_team_mens,})

class TicketDetails(IsTeamLeader,View):
	def get(self,request):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			investigators = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='SENIORTEAMLEADER')|Q(user_type='TEAMLEADER')|Q(user_type='EVALUATOR'))))	
		except:
			investigators = None
			
		search                  = request.GET.get('search')
		
		#Followup details
		if search:
			tickets 	             = FollowUp.objects.select_related('investigation__order_schedule__order__evaluation__customer','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate').filter(is_active=True).filter(Q(Q(investigation__order_schedule__order__evaluation__customer__name__icontains=search)|Q(investigation__order_schedule__order__evaluation__evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))				
		else:
			tickets 	             = FollowUp.objects.filter(is_active=True).select_related('investigation__order_schedule__order__evaluation__customer','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate').order_by('-id').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))		

		follow_ups_count = FollowUp.objects.filter(is_active=True).count()


		#followup cleaning count	
		try:
			follow_up_cleaning_count = FollowUpScheduler.objects.filter(is_active=True,work_status='FOLLOW_UP_CLEANING_FULFILLED').count()
		except:
			follow_up_cleaning_count = 0


		#FILTER	
		try:
			fil_governorate     = int(request.GET.get('governorate')) 
			areas               = Area.objects.filter(is_active=True,governorate_id=fil_governorate)
		except:
			fil_governorate     = None
			areas               = None

		try:	
			fil_area            = int(request.GET.get('area'))
		except:
			fil_area            = None
		
		fil_status              = request.GET.get('status')
		
		try:
			fil_investigator    = int(request.GET.get('investigator'))
		except:
			fil_investigator    = None
		
		
		#filters
		filters=[] 
		if fil_governorate: 
		    case1 = Q(investigation__order_schedule__customer_address__governorate_id=fil_governorate)
		    filters.append(case1)
		if fil_area: 
		    case2 = Q(investigation__order_schedule__customer_address__area_id=fil_area)
		    filters.append(case2)
		if fil_status: 
		    case3 = Q(status=fil_status)
		    filters.append(case3)
		if fil_investigator: 
		    case4 = Q(investigation__investigator_id=fil_investigator)
		    filters.append(case4)            
	
		if fil_governorate or fil_area or fil_status or fil_investigator: 
		    filters     = functools.reduce(operator.and_,filters)
		    tickets = tickets.filter(filters)
		    	
		
		#PAGINATION TICKETS		
		no_of_entries = request.GET.get('no_of_entries')		
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1) 
		paginator=Paginator(tickets,no_of_entries)
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

		return render(request,'tl/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})		
	
class TicketAdvanced(IsTeamLeader,View):
	def get(self,request,client_id,followup_id):

		#client info
		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		#followup info
		
		followup_details = FollowUp.objects.select_related('investigation__investigator','investigation__order','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate','investigation__order_schedule__order_scheduler_book').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules'),Prefetch('investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),).get(is_active=True,id=followup_id)
			
			

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=client_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		return render(request,'tl/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})		



class InvestigationTask(IsTeamLeader,View):
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
		
		if follow_up_approved == 'APPROVED':
			no_of_cleaners = request.POST.get('no_of_cleaners')
			cleaning_hours = request.POST.get('cleaning_hours')
			
			tendative_date = request.POST.get('tendative_date')
			tendative_time = request.POST.get('tendative_time')
			start_date_time = datetime.strptime(tendative_date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
			end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours))

			Investigation.objects.filter(id=investigation_id).update(is_followup_approved=True,check_out=timezone.now(),notes=request.POST.get('notes'))
			
			follow_up 				 = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
			follow_up.status         = 'INVESTIGATOR_APPROVED'
			follow_up.no_of_cleaners = no_of_cleaners
			follow_up.cleaning_hours = cleaning_hours
			follow_up.save()

			follow_up_scheduler = FollowUpScheduler.objects.create(follow_up=follow_up,start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address)
		
		else:
			Investigation.objects.filter(id=investigation_id).update(is_followup_approved=False,check_out=timezone.now(),notes=request.POST.get('notes'))
			FollowUp.objects.filter(is_active=True,investigation_id=investigation_id).update(status='FOLLOWUP_CANCELLED')
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

class Cleaning(IsTeamLeader,View):
	def get(self,request,team_id):

		cleaning_team_detail = CleaningTeam.objects.select_related('team_leader','drop_off_driver','pick_up_driver','order_scheduler__evaluation_details','order_scheduler__order_scheduler_book__service_type','order_scheduler__customer_address','order_scheduler__order__evaluation').prefetch_related(Prefetch('order_scheduler__order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections')).get(is_active=True,id=team_id)

		#checkin save	
		if cleaning_team_detail: 
			if not cleaning_team_detail.check_in:
				cleaning_team_detail.check_in                    = timezone.now()
			cleaning_team_detail.order_scheduler.work_status     = 'CLEANING_IN_PROGRESS'
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
			cleaning_team_detail.check_out                    		= timezone.now()
			cleaning_team_detail.order_scheduler.work_status  		= 'CLEANING_FULFILLED'
			cleaning_team_detail.order_scheduler.order.order_status = 'ORDER_IN_PROGRESS'
			cleaning_team_detail.save()
			cleaning_team_detail.order_scheduler.save()
			cleaning_team_detail.order_scheduler.order.save()	

		#To Save Media
		medias = request.FILES.getlist('mediabefore')
		if not medias==['']:
			for media in medias:
				CleaningTeamMedia.objects.create(
				        team_id=team_id,
				        media=media,
				        taken_status='BEFORE_CLEANING'
				        )

		#To Save Media
		medias = request.FILES.getlist('mediaafter')
		if not medias==['']:
			for media in medias:
				CleaningTeamMedia.objects.create(
				        team_id=team_id,
				        media=media,
				        taken_status='AFTER_CLEANING'
				        )		

		messages.success(request,"Checkout Succesfully")

		my_cleaning_calendar_date = request.GET.get('my_cleaning_calendar_date') or ''
				
		return redirect('/tl/dashboard/?my_cleaning_calendar_date='+my_cleaning_calendar_date)

class FollowupCleaning(IsTeamLeader,View):
	def get(self,request,team_id):

		followup_team_detail = FollowUpTeam.objects.select_related('team_leader','drop_off_driver','pick_up_driver','followup_scheduler__follow_up__investigation__investigator','followup_scheduler__follow_up__investigation__order__evaluation','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__service_type','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book','followup_scheduler__customer_address').prefetch_related(Prefetch('followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True),to_attr='sections')).get(is_active=True,id=team_id)
			

		#checkin save
		if followup_team_detail: 
			if not followup_team_detail.check_in:
				followup_team_detail.check_in                       = timezone.now()
			followup_team_detail.followup_scheduler.work_status     = 'FOLLOW_UP_CLEANING_IN_PROGRESS'
			followup_team_detail.followup_scheduler.follow_up.status= 'FOLLOWUP_IN_PROGRESS'
			followup_team_detail.save()	
			followup_team_detail.followup_scheduler.save()
			followup_team_detail.followup_scheduler.follow_up.save()
		
		return render(request,'tl/cleaning/followup_cleaning.html',{"followup_team_detail":followup_team_detail,})

	def post(self,request,team_id):
		
		#checkout save
		try:
			followup_team_detail = FollowUpTeam.objects.select_related('followup_scheduler__follow_up').get(is_active=True,id=team_id)
		except:	
			followup_team_detail = None

		#checkin save	
		if followup_team_detail: 
			followup_team_detail.check_out                          = timezone.now()
			followup_team_detail.followup_scheduler.work_status     = 'FOLLOW_UP_CLEANING_FULFILLED'
			followup_team_detail.followup_scheduler.follow_up.status= 'FOLLOWUP_CLOSED'

			followup_team_detail.save()
			followup_team_detail.followup_scheduler.save()
			followup_team_detail.followup_scheduler.follow_up.save()	

		#To Save Media
		medias = request.FILES.getlist('mediabefore')
		if not medias==['']:
			for media in medias:
				FollowUpTeamMedia.objects.create(
				        team_id=team_id,
				        media=media,
				        taken_status='BEFORE_CLEANING'
				        )

		#To Save Media
		medias = request.FILES.getlist('mediaafter')
		if not medias==['']:
			for media in medias:
				FollowUpTeamMedia.objects.create(
				        team_id=team_id,
				        media=media,
				        taken_status='AFTER_CLEANING'
				        )


		messages.success(request,"Checkout Succesfully")
				
		my_cleaning_calendar_date = request.GET.get('my_cleaning_calendar_date') or ''
				
		return redirect('/tl/dashboard/?my_cleaning_calendar_date='+my_cleaning_calendar_date)