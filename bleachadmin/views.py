from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from bleach_crm_ps.permissions import IsAdmin
from dateutil.relativedelta import relativedelta
import pandas as pd
import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField
from django.db.models.functions import Cast 
from django.db.models import Prefetch

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,CleaningMethod,ServiceType,EvaluationBookSection,EvaluationSectionKeynote,LocationType,CleaningType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory

from django.db.models.functions import TruncMonth as Month, TruncYear as Year
from django.db.models import Count

# Create your views here.

class AdminHome(IsAdmin,View):
	def get(self,request):
		#evaluators
		evaluators_sales_target = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR')
		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)

		#Enquiry Details count
		try:
			enquiry = EvaluationDetails.objects.filter(is_active=True)
		except:
			enquiry	= None

		today_enquiry_count = enquiry.filter(proposed_time__gte=count_today_start,proposed_time__lt=count_today_end,).count()
		week_enquiry_count  = enquiry.filter(proposed_time__gte=count_today_end-timedelta(7),proposed_time__lt=count_today_end).count()	

		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))).count() 
		week_cleaning_job_count  = cleaning_job.filter(Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end))).count()		
		
		#Followup jobs count
		try:
			follow_up_job    = FollowUpTeam.objects.filter(is_active=True)
		except:
			follow_up_job	 = None

		today_follow_up_job_count = follow_up_job.filter(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))).count() 
		week_follow_up_job_count  = follow_up_job.filter(Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end))).count()		

		#Feedback Staring count
		try:
			feedbacks                 = FeedBack.objects.filter(is_active=True)
		except:
			feedbacks				  = None

		month_average_feedback		  = feedbacks.filter(response_date__gte=count_today_end-timedelta(30)).aggregate(Avg('rating'))['rating__avg']
		lastmonth_average_feedback		  = feedbacks.filter(response_date__gte=count_today_end-timedelta(60),response_date__lte=count_today_end-timedelta(30)).aggregate(Avg('rating'))['rating__avg']	
		

		#Evaluation details of each evaluator for evaluation table
		evaluation_calendar_date	= request.GET.get('evaluation_calendar_date')
		
		try:
			evaluation_date = datetime.strptime(evaluation_calendar_date,'%d-%m-%Y')
		except:
			evaluation_date = timezone.now().replace(tzinfo=None)	

		evaluation_date_start  = evaluation_date.replace(hour=0,minute=0,second=0,microsecond=0)
		evaluation_date_end    = evaluation_date_start+timedelta(1)	
		
		try:
			evaluation_details		  = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related(Prefetch('evaluator_evaluation',queryset=EvaluationDetails.objects.filter(is_active=True,proposed_time__gte=evaluation_date_start,proposed_time__lte=evaluation_date_end),to_attr='evaluation_details'))
		except:
			evaluation_details 		  = None


		#cleaning schedule & followup schedule for cleaning calendar			
		cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')
		
		try:
			schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			schedule_date = timezone.now().replace(tzinfo=None)

		schedule_date_start = schedule_date.replace(hour=0,minute=0,second=0,microsecond=0)
		schedule_date_end   = schedule_date_start+timedelta(1)		

		try:
			calendar_order_schedules 	= OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams'))
		except:
			calendar_order_schedules 	= None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			calendar_followup_schedules = None
	
		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams'))
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			sp_calendar_followup_schedules = None							

		try:
			spp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
		except:
			spp_calendar_order_schedules = None

		try:
			spp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			spp_calendar_followup_schedules = None

		return render(request,'admin/home/home.html',{'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'month_average_feedback':month_average_feedback,'lastmonth_average_feedback':lastmonth_average_feedback,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'spp_calendar_order_schedules':spp_calendar_order_schedules,'spp_calendar_followup_schedules':spp_calendar_followup_schedules,'schedule_date':schedule_date,'evaluators_sales_targets':evaluators_sales_target})

class ClientDetails(IsAdmin,View):
	def get(self,request):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		
		search                  = request.GET.get('search')

		if search:
			try:
				client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True,name__icontains=search).order_by('-id').prefetch_related(Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True,order_status='ORDER_IN_PROGRESS'),to_attr='order_evaluation')),to_attr='customer_evaluations'))
			except:
				client_details = None
		else:
			client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True).order_by('-id').prefetch_related(Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True,order_status='ORDER_IN_PROGRESS'),to_attr='order_evaluation')),to_attr='customer_evaluations'))			



		fil_status                = request.GET.get('status')			
				
		#code must change for optimisation	
		for detail in client_details:
			detail.active_status = False
			if detail.customer_evaluations:
				for evaluation in detail.customer_evaluations:
					if evaluation.order_evaluation:
						detail.active_status = True	

		#To Find active and new client
		try:
			orders = Order.objects.filter(is_active=True).select_related('evaluation__customer')
		except:
			orders = None	

		new_clients_count    = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True,created__gte=timezone.now().date()-timedelta(30)).count()
		

		#Prefetch filters
		try:
			fil_governorate       = int(request.GET.get('governorate'))
			areas                 = Area.objects.filter(governorate_id=fil_governorate) 
		except:
			fil_governorate       = None
			areas                 = None

		try:	
			fil_area			  = int(request.GET.get('area'))
		except:
			fil_area              = None	



		customer_address_filter       = []
		count_customer_address_filter = [] 
		if fil_governorate: 
		    case1       = Q(is_active=True,governorate_id=fil_governorate)
		    count_case1 = Q(address_customer__governorate_id=fil_governorate)
		    customer_address_filter.append(case1)
		    count_customer_address_filter.append(count_case1)
		
		if fil_area:
		    case2 		= Q(is_active=True,area_id=fil_area)
		    count_case2 = Q(address_customer__area_id=fil_area)
		    customer_address_filter.append(case2)
		    count_customer_address_filter.append(count_case2)

		if fil_governorate or fil_area: 
			customer_address_prefetch_filter              = functools.reduce(operator.and_,customer_address_filter)
			count_customer_address_prefetch_filter        = functools.reduce(operator.and_,count_customer_address_filter)
		else:
			customer_address_prefetch_filter              = None
			count_customer_address_prefetch_filter        = None	

		#Apply prefetch filter
		if customer_address_prefetch_filter:
			
			client_details = client_details.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(customer_address_prefetch_filter).select_related('area'),to_attr='customer_address')).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)	

		else:
			client_details = client_details.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area'),to_attr='customer_address'))		


		#FILTER	
		fil_customertype          = request.GET.get('customertype')
		fil_status                = request.GET.get('status')

		filters = []
		if fil_customertype: 
		    case1 = Q(customer_type=fil_customertype)
		    filters.append(case1)
		

		if fil_customertype: 
		    filters            = functools.reduce(operator.and_,filters)
		    client_details     = client_details.filter(filters)
		
		#PAGINATION CLIENTS		
		no_of_entries = request.GET.get('no_of_entries')		
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1) 
		paginator=Paginator(client_details,no_of_entries)
		try: 
			client_details=paginator.page(page) 
		except PageNotAnInteger:
			client_details=paginator.page(1)
		except EmptyPage:
			client_details = paginator.page(paginator.num_pages) 

		# Get the index of the current page
		index = client_details.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]	
		entry_per_page=(client_details.end_index())-(client_details.start_index())+1


		return render(request,'admin/client/clients.html',{"client_details":client_details,"search_query":search,"new_clients_count":new_clients_count,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_customertype":fil_customertype,"fil_status":fil_status})		

class ClientOrders(IsAdmin,View):
	def get(self,request,client_id):

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None
	
		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'))
					
		#COUNT			
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()

		return render(request,"admin/client/client-page.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,})

class ClientOrderDetails(IsAdmin,View):
	def get(self,request,order_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)
			

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=order.evaluation.customer_id)
		except:
			client_details = None

		#orders count
		orders = Order.objects.filter(is_active=True,evaluation__customer_id=order.evaluation.customer_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()
					
				
		return render(request,"admin/client/order-page.html",{"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count})




class TicketDetails(IsAdmin,View):
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

		return render(request,'admin/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})		


class TicketAdvanced(IsAdmin,View):
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

		return render(request,'admin/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})


class OrderDetails(IsAdmin,View):
	def get(self,request):
		
		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			service_types = ServiceType.objects.filter(is_active=True) 
		except:
			service_types =	None

		#Evaluation Details
		search                  = request.GET.get('search')

		if search:
			evaluations = Evaluation.objects.filter(is_active=True,quatation_status__isnull=False).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder'))
		else:
			evaluations = Evaluation.objects.filter(is_active=True,quatation_status__isnull=False).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder'))

		if evaluations:
			approved_orders_count = evaluations.filter(Q(quatation_status='APPROVED')).count()
			pending_orders_count  =	evaluations.filter(Q(quatation_status='PENDING')).count()
		else:
			approved_orders_count = 0
			pending_orders_count  = 0	



		#Prefetch filters
		try:
			fil_governorate       = int(request.GET.get('governorate'))
			areas                 = Area.objects.filter(governorate_id=fil_governorate) 
		except:
			fil_governorate       = None
			areas                 = None

		try:	
			fil_area			  = int(request.GET.get('area'))
		except:
			fil_area              = None

		fil_cleaning_policy       = request.GET.get('cleaning_policy')
		
		try:
			fil_service_type      = int(request.GET.get('service_type'))
		except:
			fil_service_type      = None
			

		customer_address_filter       = []
		count_customer_address_filter = [] 
		if fil_governorate: 
		    case1       = Q(address__governorate_id=fil_governorate)
		    count_case1 = Q(evaluation_details__address__governorate_id=fil_governorate)
		    customer_address_filter.append(case1)
		    count_customer_address_filter.append(count_case1)
		
		if fil_area:
		    case2 		= Q(address__area_id=fil_area)
		    count_case2 = Q(evaluation_details__address__area_id=fil_area)
		    customer_address_filter.append(case2)
		    count_customer_address_filter.append(count_case2)

		if fil_governorate or fil_area: 
			customer_address_prefetch_filter              = functools.reduce(operator.and_,customer_address_filter)
			count_customer_address_prefetch_filter        = functools.reduce(operator.and_,count_customer_address_filter)
		else:
			customer_address_prefetch_filter              = None
			count_customer_address_prefetch_filter        = None

		
		evaluation_book_filter       = []
		count_evaluation_book_filter = []
		if fil_cleaning_policy:
			case1       = Q(cleaning_policy=fil_cleaning_policy)
			count_case1 = Q(evaluation_details__evaluation_book_evaluation_details__cleaning_policy=fil_cleaning_policy)
			evaluation_book_filter.append(case1)
			count_evaluation_book_filter.append(count_case1)
		if fil_service_type:     
			case2       = Q(service_type_id=fil_service_type)
			count_case2 = Q(evaluation_details__evaluation_book_evaluation_details__service_type_id=fil_service_type)
			evaluation_book_filter.append(case2)              
			count_evaluation_book_filter.append(count_case2)

		if fil_cleaning_policy or fil_service_type:
			evaluation_book_prefetch_filter              = functools.reduce(operator.and_,evaluation_book_filter)
			count_evaluation_book_prefetch_filter        = functools.reduce(operator.and_,count_evaluation_book_filter)
		else:
			evaluation_book_prefetch_filter              = None	
			count_evaluation_book_prefetch_filter        = None

		#Apply prefetch filter
		if evaluation_book_prefetch_filter and customer_address_prefetch_filter: 
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_book_count=Count(Case(When( Q(count_evaluation_book_prefetch_filter & count_customer_address_prefetch_filter),then=1),output_field=IntegerField()))).filter(address_book_count__gt=0)		 
			print("both")
		elif evaluation_book_prefetch_filter and not customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(book_count=Count(Case(When( count_evaluation_book_prefetch_filter,then=1),output_field=IntegerField()))).filter(book_count__gt=0)
			print("book only")
		elif not evaluation_book_prefetch_filter and customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)
			print("address only") 
		else:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))		
			print("not at all")
		
		
		fil_status = request.GET.get('status')
		#filters 	
		filters=[] 
		if fil_status: 
		    case1 = Q(quatation_status=fil_status)
		    filters.append(case1)
	
		if fil_status: 
		    filters     = functools.reduce(operator.and_,filters)
		    evaluations = evaluations.filter(filters)

		#PAGINATION ORDERS		
		no_of_entries = request.GET.get('no_of_entries')		
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1) 
		paginator=Paginator(evaluations,no_of_entries)
		try: 
			evaluations=paginator.page(page) 
		except PageNotAnInteger:
			evaluations=paginator.page(1)
		except EmptyPage:
			evaluations = paginator.page(paginator.num_pages) 

		# Get the index of the current page
		index = evaluations.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]	
		entry_per_page=(evaluations.end_index())-(evaluations.start_index())+1

		return render(request,'admin/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,})		


class FeedbackDetails(IsAdmin,View):
	def get(self,request):
		
		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			service_types = ServiceType.objects.filter(is_active=True) 
		except:
			service_types =	None



		search                  = request.GET.get('search')

		#order wise feedback
		if search:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True,is_feedback_marked=True).filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id=search))).order_by('-id')		
			except:
				order_wise_feedbacks = None

		else:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True,is_feedback_marked=True).order_by('-id')						
			except:	
				order_wise_feedbacks = None

		#Prefetch filters
		try:
			fil_governorate       = int(request.GET.get('governorate'))
			areas                 = Area.objects.filter(governorate_id=fil_governorate) 
		except:
			fil_governorate       = None
			areas                 = None

		try:	
			fil_area			  = int(request.GET.get('area'))
		except:
			fil_area              = None

		
		try:
			fil_service_type      = int(request.GET.get('service_type'))
		except:
			fil_service_type      = None
		

		customer_address_filter       = []
		count_customer_address_filter = [] 
		if fil_governorate: 
		    case1       = Q(address__governorate_id=fil_governorate)
		    count_case1 = Q(evaluation__evaluation_details__address__governorate_id=fil_governorate)
		    customer_address_filter.append(case1)
		    count_customer_address_filter.append(count_case1)
		
		if fil_area:
		    case2 		= Q(address__area_id=fil_area)
		    count_case2 = Q(evaluation__evaluation_details__address__area_id=fil_area)
		    customer_address_filter.append(case2)
		    count_customer_address_filter.append(count_case2)

		if fil_governorate or fil_area: 
			customer_address_prefetch_filter              = functools.reduce(operator.and_,customer_address_filter)
			count_customer_address_prefetch_filter        = functools.reduce(operator.and_,count_customer_address_filter)
		else:
			customer_address_prefetch_filter              = None
			count_customer_address_prefetch_filter        = None

		
		evaluation_book_filter       = []
		count_evaluation_book_filter = []
		if fil_service_type:     
			case1       = Q(service_type_id=fil_service_type)
			count_case1 = Q(evaluation__evaluation_details__evaluation_book_evaluation_details__service_type_id=fil_service_type)
			evaluation_book_filter.append(case1)              
			count_evaluation_book_filter.append(count_case1)

		if fil_service_type:
			evaluation_book_prefetch_filter              = functools.reduce(operator.and_,evaluation_book_filter)
			count_evaluation_book_prefetch_filter        = functools.reduce(operator.and_,count_evaluation_book_filter)
		else:
			evaluation_book_prefetch_filter              = None	
			count_evaluation_book_prefetch_filter        = None	


		#Apply prefetch filter
		if evaluation_book_prefetch_filter and customer_address_prefetch_filter: 
			order_wise_feedbacks = order_wise_feedbacks.prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField())).annotate(address_book_count=Count(Case(When( Q(count_evaluation_book_prefetch_filter & count_customer_address_prefetch_filter),then=1),output_field=IntegerField()))).filter(address_book_count__gt=0)
			print("both")
		elif evaluation_book_prefetch_filter and not customer_address_prefetch_filter:
			order_wise_feedbacks = order_wise_feedbacks.prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField())).annotate(book_count=Count(Case(When( count_evaluation_book_prefetch_filter,then=1),output_field=IntegerField()))).filter(book_count__gt=0)
			print("book only")
		elif not evaluation_book_prefetch_filter and customer_address_prefetch_filter:
			order_wise_feedbacks = order_wise_feedbacks.prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField())).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)
			print("address only") 
		else:
			order_wise_feedbacks = order_wise_feedbacks.prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField()))		
			print("not at all")	

		#FILTER
		fil_minimumstarring       		  = request.GET.get('minimumstarring')	
		fil_maximumstarring       		  = request.GET.get('maximumstarring')
		#filters 	
		filters=[] 
		if fil_minimumstarring: 
		    case1 = Q(avg_starring__gte=fil_minimumstarring)
		    filters.append(case1)
		
		if fil_maximumstarring: 
		    case2 = Q(avg_starring__lte=fil_maximumstarring)
		    filters.append(case2)

		if fil_minimumstarring or fil_maximumstarring: 
			if fil_minimumstarring and fil_maximumstarring:
				if fil_minimumstarring <= fil_maximumstarring:
					filters              = functools.reduce(operator.and_,filters)
					order_wise_feedbacks = order_wise_feedbacks.filter(filters)
				else:
					messages.error(request,"Minimum Starring Should be less than Maximum Starring")    
			else:
				filters              = functools.reduce(operator.and_,filters)
				order_wise_feedbacks = order_wise_feedbacks.filter(filters)	    




		#to find starring caluculations in whole system
		try:
			feedbacks                 = FeedBack.objects.filter(is_active=True)
		except:
			feedbacks				  = None

		total_feedbacks               = feedbacks.values('order').distinct().count()
		full_order_wise_feedbacks     = order_wise_feedbacks
				
				
		#PAGINATION FEEDBACKS		
		no_of_entries = request.GET.get('no_of_entries')		
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1) 
		paginator=Paginator(order_wise_feedbacks,no_of_entries)
		try: 
			order_wise_feedbacks=paginator.page(page) 
		except PageNotAnInteger:
			order_wise_feedbacks=paginator.page(1)
		except EmptyPage:
			order_wise_feedbacks = paginator.page(paginator.num_pages) 

		# Get the index of the current page
		index = order_wise_feedbacks.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]	
		entry_per_page=(order_wise_feedbacks.end_index())-(order_wise_feedbacks.start_index())+1

		return render(request,'admin/feedback/feedbacks.html',{"feedbacks":feedbacks,"total_feedbacks":total_feedbacks,"order_wise_feedbacks":order_wise_feedbacks,"full_order_wise_feedbacks":full_order_wise_feedbacks,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_minimumstarring":fil_minimumstarring,"fil_maximumstarring":fil_maximumstarring,"fil_service_type":fil_service_type,})

class FeedbackAdvanced(IsAdmin,View):
	def get(self,request,client_id,order_id):
		
		#client info
		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		#feedback_info
		try:
			feedback_details   = Order.objects.prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(id=order_id)		
		except:
			feedback_details   = None

		#total feedback
		try:
			feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True,evaluation__customer_id=client_id).prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField()))		
		except:
			feedbacks = None

		#total_feedback_rating
		average_feedback  = feedbacks.filter(id=order_id).aggregate(Sum('avg_starring'))['avg_starring__sum']
		
		#other feedbacks
		try:
			other_feedbacks = feedbacks.exclude(id=order_id).filter(is_feedback_marked=True)
		except:	
			other_feedbacks = None

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=client_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()	

		return render(request,'admin/feedback/feedback-page.html',{"client_details":client_details,"feedback_details":feedback_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"other_feedbacks":other_feedbacks,"average_feedback":average_feedback,})




class ResourceManagement(IsAdmin,View):
	def get(self,request):
		
		try:
			staffs = UserProfile.objects.filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER')))
		except:
			staffs = None	


		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)


		#total workers count
		try:
			total_workers = UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER'))).count()
		except:
			total_workers = 0
		
		#total active workers
		try:
			total_active_workers = CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__lte=count_today_start)&Q(end_at__gte=count_today_start)) )).values_list('member',flat=True).distinct().union(FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__lte=timezone.now().replace(tzinfo=None))&Q(end_at__gte=timezone.now().replace(tzinfo=None)))) ).values_list('member',flat=True)).distinct().count()
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


		today_cleaning_active_teams  = cleaning_teams.filter(Q(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))))
		today_followup_active_teams  = follow_up_teams.filter(Q(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))))
		week_cleaning_active_teams   = cleaning_teams.filter(Q( Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end)) ))
		week_followup_active_teams   = follow_up_teams.filter(Q( Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end)) ))
		

		today_date            = timezone.now()
		weekstart_date        = timezone.now()-timedelta(6)


		try:
			today_total_team_mens = today_cleaning_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+today_cleaning_active_teams.count() or 0+today_followup_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+today_followup_active_teams.count() or 0
		except:
			today_total_team_mens = 0
		try:	
			week_total_team_mens  = week_cleaning_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+week_cleaning_active_teams.count() or 0+week_followup_active_teams.aggregate(Sum('no_of_cleaners'))['no_of_cleaners__sum']+week_followup_active_teams.count() or 0
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
			workers_date = timezone.now().replace(tzinfo=None)

		workers_date_start = workers_date.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		workers_date_end   = workers_date_start+timedelta(1)		

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
			workers_details = workers.prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(Q(start_at__gte=workers_date_start)&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_start)&Q(end_at__lte=workers_date_end))) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation','team__order_scheduler__order_scheduler_book'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(Q(start_at__gte=workers_date_start)&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_start)&Q(end_at__lte=workers_date_end))) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details'))
		except:
			workers_details = None

		#Filter
		try:
			fil_staff = int(request.GET.get('staff'))
		except:
			fil_staff = ''

		try:
			fil_minhours       = int(request.GET.get('minhours'))
		except:
			fil_minhours       = None

		try:
			fil_maxhours       = int(request.GET.get('maxhours'))	
		except:
			fil_maxhours	   = None

		if 	fil_minhours and fil_maxhours:
			if fil_minhours>=fil_maxhours:
				messages.error(request,"Minimum Duration should be less than Maximum Duration")
				fil_minhours = None
				fil_maxhours = None
				
		#filters 	
		filters=[] 
		if fil_staff: 
		    case1 = Q(id=fil_staff)
		    filters.append(case1)
	
		if fil_staff: 
		    filters         = functools.reduce(operator.and_,filters)
		    workers_details = workers_details.filter(filters)

		return render(request,'admin/resource/resources.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,"staffs":staffs,"fil_staff":fil_staff,"fil_minhours":fil_minhours,"fil_maxhours":fil_maxhours,})

class PaymentDetails(IsAdmin,View):
	def get(self,request):
		
		#Evaluation Details
		search                  = request.GET.get('search')
		
		#sales amount
		if search:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').select_related('evaluation__customer').filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area'),to_attr='invoice_evaluation_details'))
			except:
				invoices         = None
		else:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area'),to_attr='invoice_evaluation_details'))
			except:
				invoices         = None
				
		#Pending Payments
		try:
			pending_payments = invoices.filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD')))
		except:
			pending_payments = None

		#Pending Payment and Order Count	
		if pending_payments: 
			total_pending_amount = pending_payments.aggregate(total=Sum(F('remining_amount')))['total']		
			total_pending_orders = pending_payments.count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0

		#PAGINATION INVOICE	
		no_of_entries = request.GET.get('no_of_entries')	
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1) 
		paginator=Paginator(invoices,no_of_entries)
		try: 
			invoices=paginator.page(page) 
		except PageNotAnInteger:
			invoices=paginator.page(1)
		except EmptyPage:
			invoices = paginator.page(paginator.num_pages) 

		# Get the index of the current page
		index = invoices.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]	
		entry_per_page=(invoices.end_index())-(invoices.start_index())+1	

		return render(request,'admin/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,'no_of_entries':no_of_entries,})		

#ajax for sales charts
def SalesLocationData(request):
	data = []
	
	dom = request.GET.get('dom', None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(dom,prevdate,todate,"pop")
	location_types = AreaType.objects.all()
	if dom == 'Month':
		print("derr")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")
		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=28,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+timedelta(1)
		locationcount = 0
		others_count = 0

		# appending each location counts
		for location in location_types:			
			
			sales_location_count = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(monthdate1,monthdate2),evaluation__evaluation_details__evaluation_book_evaluation_details__area_type=location.name).count()
			if not sales_location_count:
				sales_location_count = 0
			
			if sales_location_count > 0:
				locationcount += 1
				if locationcount <= 5:
					location_dict = {
					"location" : location.name,
					"count" : sales_location_count,
					}
					data.append(location_dict)

				if locationcount > 5:
					
					others_count += sales_location_count

		# appending total of other locations
		if others_count > 0:
			location_dict = {
			"location" : "Others",
			"count" : others_count,
			}
			data.append(location_dict)

	else:
		print("war")
		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=30)
		print(prevdate,todate,"testdt")

		prevdate_date_start  = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
		todate_date_end  = todate.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(1)

		locationcount = 0
		others_count = 0

		# appending each location counts
		for location in location_types:
			locationcount += 1
			sales_location_count = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(prevdate_date_start,todate_date_end),evaluation__evaluation_details__evaluation_book_evaluation_details__area_type=location.name).count()
			# if not sales_location_count:
			# 	sales_location_count = 0

			if locationcount <= 5 :
				location_dict = {
				"location" : location.name,
				"count" : sales_location_count,
				}
				data.append(location_dict)

			if locationcount > 5 :
				others_count += sales_location_count

		# appending total of other locations
		if others_count > 0:
			location_dict = {
			"location" : "Others",
			"count" : others_count,
			}
			data.append(location_dict)
							
	print(data,"dot")
 
	return JsonResponse(data,safe=False)

#ajax for sales charts
def SalesCleaningTypeData(request):
	print("ram")
	data = []
	dom = request.GET.get('dom',None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(prevdate,todate,"pop")
	cleaning_types = ServiceType.objects.all()
	if dom == 'Month':
		print("derr")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")

		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=28,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+timedelta(1)

		for clean in cleaning_types:
			sales_cleaningtype_count = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(monthdate1,monthdate2),evaluation__evaluation_details__evaluation_book_evaluation_details__service_type=clean).count()
			if sales_cleaningtype_count > 0:
				clean_dict = {
				"cleaning_type" : clean.name,
				"count" : sales_cleaningtype_count,
				}
				data.append(clean_dict)
	else:
		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=30)
		print(prevdate,todate,"testdt")

		prevdate_date_start  = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
		todate_date_end  = todate.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(1)
	
		for clean in cleaning_types:
			sales_cleaningtype_count = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(prevdate_date_start,todate_date_end),evaluation__evaluation_details__evaluation_book_evaluation_details__service_type=clean).count()
			if sales_cleaningtype_count > 0:
				clean_dict = {
				"cleaning_type" : clean.name,
				"count" : sales_cleaningtype_count,
				}
				data.append(clean_dict)
		print(data)
	return JsonResponse(data,safe=False)

#ajax for sales charts
def SalesGovernorateData(request):
	data = []
	dom = request.GET.get('dom',None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(prevdate,todate,"pop")
	governorates = Governorate.objects.all()
	if dom == 'Month':
		print("derr")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")

		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=28,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+timedelta(1)

		for gov in governorates:
			print(gov,"govrt")
			sales_governorate_count = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(monthdate1,monthdate2),evaluation__customer__address_customer__governorate=gov).count()
			if sales_governorate_count >0:
				gov_dict = {
				"governorate" : gov.name,
				"count" : sales_governorate_count,
				}
				data.append(gov_dict)
	else:

		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=60)
		print(prevdate,todate,"testdt")

		prevdate_date_start  = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
		todate_date_end  = todate.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(1)
	
		for gov in governorates:
			sales_governorate_count = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(prevdate_date_start,todate_date_end),evaluation__customer__address_customer__governorate=gov).count()
			if sales_governorate_count > 0:
				print(sales_governorate_count,"sgc")		
				gov_dict = {
				"governorate" : gov.name,
				"count" : sales_governorate_count,
				}
				data.append(gov_dict)
		print(data)
	return JsonResponse(data,safe=False)

#ajax for sales charts
def SalesData(request):
	data = []
	dom = request.GET.get('dom', None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(dom,prevdate,todate,"pop")
	sales_dict = dict()

	if dom == 'Month':
		print("derr")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")

		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=28,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)
		monthdate2_end = monthdate2+timedelta(1)

		sales = Order.objects.filter(is_active=True,created__range=(monthdate1,monthdate2_end)).values('created').values('created').annotate(month=Month('created'),).values('month').annotate(count=Sum('evaluation__total_cost'))

		print(sales,"po")
		for sale in sales:
			total_sales = Order.objects.filter(is_active=True,evaluation__quatation_status="APPROVED",created__range=(monthdate1,monthdate2_end)).values('created').values('created').annotate(month=Month('created'),).values('month').annotate(count=Sum('evaluation__total_cost'))
			
			sale_total = 0

			for s in total_sales:
				if s['month'] == sale['month'] :
					sale_total = s['count']

			sales_dict = {
			"date" : sale['month'],
			"amount" : sale_total,
			"total" : sale['count'],
			}
			data.append(sales_dict)
	else:
		print("njk")
		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=30)
		print(prevdate,todate,"testdt310")
		daterange = pd.date_range(prevdate, todate)

		for single_date in daterange:
			sale_date_start  = single_date.replace(hour=0,minute=0,second=0,microsecond=0)
			sale_date_end    = single_date+timedelta(1)

			total_sales = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(sale_date_start,sale_date_end)).aggregate(Sum('evaluation__total_cost'))['evaluation__total_cost__sum'] or 0.0

			total_orders = Order.objects.filter(is_active=True,created__range=(sale_date_start,sale_date_end)).aggregate(Sum('evaluation__total_cost'))['evaluation__total_cost__sum'] or 0.0

			print(total_sales,"qtc")
			sales_dict = {
			"date" : single_date,
			"amount" : total_sales,
			"total" : total_orders,
			}
			data.append(sales_dict)
	print(data,"sdt")
	return JsonResponse(data,safe=False)

#ajax for sales target charts
def SalesTargetData(request):
	data = []
	dom = request.GET.get('dom', None)
	evaluator_id = request.GET.get('evaluator',None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(dom,prevdate,todate,evaluator_id,"pop333")
	sales_dict = dict()
	
	if dom == 'Month':
		print("derr")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")

		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=28,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)
		monthdate2_end = monthdate2+timedelta(1)

		if evaluator_id == 0 :
			sales = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=None,created__range=(monthdate1,monthdate2_end)).values('created').annotate(month=Month('created'),).values('month').annotate(count=Sum('evaluation__total_cost'))
		else:
			sales = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=evaluator_id,created__range=(monthdate1,monthdate2_end)).values('created').annotate(month=Month('created'),).values('month').annotate(count=Sum('evaluation__total_cost'))
		print(sales,"po")
		for sale in sales:
			total_sales = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=evaluator_id,evaluation__quatation_status='APPROVED',created__range=(monthdate1,monthdate2_end)).values('created').annotate(month=Month('created')).values('month').annotate(count=Sum('evaluation__total_cost'))
			print(total_sales,"totsal")
			sale_total = 0

			for s in total_sales:
				if s['month'] == sale['month'] :
					sale_total = s['count']
			print(sale['count'],sale_total,"red1")
			sales_dict = {
			"date" : sale['month'],
			"amount" : sale_total,
			"total" : sale['count'],
			}
			data.append(sales_dict)
	else:
		print("njk")
		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=30)
		print(prevdate,todate,"testdt")
		daterange = pd.date_range(prevdate, todate)

		for single_date in daterange:
			saletarget_date_start  = single_date.replace(hour=0,minute=0,second=0,microsecond=0)
			saletarget_date_end    = single_date+timedelta(1)

			if evaluator_id == '0' :
				total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__quatation_status='APPROVED',created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)			

				total_orders = Order.objects.filter(evaluation__evaluation_details__evaluator=None,created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
			else:
				total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator_id,evaluation__quatation_status='APPROVED',created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)			

				total_orders = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator_id,created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
			
			print(total_sales,total_orders,"red2")
			sales_dict = {
			"date" : single_date,
			"amount" : total_sales or 0.0,
			"total" : total_orders or 0.0,
			}
			data.append(sales_dict)
	print(data,"sdt")
	return JsonResponse(data,safe=False)

def cleaningcalendardate(request):
	data = dict()
	cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')
		
	try:
		schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
	except:
		schedule_date = timezone.now().replace(tzinfo=None)

	schedule_date_start = schedule_date.replace(hour=0,minute=0,second=0,microsecond=0)
	schedule_date_end   = schedule_date_start+timedelta(1)		

	try:
		calendar_order_schedules 	= OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
	except:
		calendar_order_schedules 	= None

	try:
		calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
	except:
		calendar_followup_schedules = None

	try:
		sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
	except:
		sp_calendar_order_schedules = None

	try:
		sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
	except:
		sp_calendar_followup_schedules = None							

	try:
		spp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
	except:
		spp_calendar_order_schedules = None

	try:
		spp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
	except:
		spp_calendar_followup_schedules = None

	context = {'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'spp_calendar_order_schedules':spp_calendar_order_schedules,'spp_calendar_followup_schedules':spp_calendar_followup_schedules}
	data['cleaningdetails'] = render_to_string('admin/home/cleaning-calendar-snippet.html',context)	
	return JsonResponse(data)

def SalesTargetDaily(request):
	data = []
	data2 = []
	target_dict = dict()
	evaluators_sales_target = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR')
	target_date = request.GET.get('target_date')
	target_date = datetime.strptime(target_date, '%d-%m-%Y')

	target_date_start = target_date.replace(hour=0,minute=0,second=0,microsecond=0)
	target_date_end= target_date+timedelta(1)

	for evaluator in evaluators_sales_target:
		total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(target_date_start,target_date_end)).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		if not total_sales:
			total_sales = 0.0

		evaluator_target_dict = {
		"evaluator_id" : evaluator.id,
		"amount" : total_sales,
		}
		data.append(evaluator_target_dict)
	print(data,"here")

	agent_sales_total = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(target_date_start,target_date_end)).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
	if not agent_sales_total:
		agent_sales_total = 0.0
		
	agent_target_dict = {
		"evaluator_id" : 0,
		"amount" : agent_sales_total,
		}
	data.append(agent_target_dict)
	return JsonResponse(data,safe=False)

def evaluationcalendardate(request):
	data = dict()
	evaluation_calendar_date	= request.GET.get('evaluation_calendar_date')
		
	try:
		evaluation_date = datetime.strptime(evaluation_calendar_date,'%d-%m-%Y')
	except:
		evaluation_date = timezone.now().replace(tzinfo=None)	

	evaluation_date_start  = evaluation_date.replace(hour=0,minute=0,second=0,microsecond=0)
	evaluation_date_end    = evaluation_date_start+timedelta(1)	
	
	try:
		evaluation_details		  = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related(Prefetch('evaluator_evaluation',queryset=EvaluationDetails.objects.filter(is_active=True,proposed_time__gte=evaluation_date_start,proposed_time__lte=evaluation_date_end),to_attr='evaluation_details'))
	except:
		evaluation_details 		  = None

	try:
		workers = UserProfile.objects.filter(is_active=True)
	except:
		workers = None

	context = {'evaluation_details':evaluation_details,"workers":workers}
	data['evaluationdetails'] = render_to_string('admin/home/evaluation-calendar-snippet.html',context)
	return JsonResponse(data)