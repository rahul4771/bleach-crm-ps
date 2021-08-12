from django.shortcuts import render,redirect
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
from bleach_crm_ps.utils import get_error
from django.db.models.functions import ExtractMonth,ExtractYear

from django.contrib import messages
from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,CleaningMethod,ServiceType,EvaluationBookSection,EvaluationSectionKeynote,LocationType,CleaningType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia,Promocode
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from bleachadmin.models import ServiceProductivity,ServicePriceRange

from order.forms import PromocodeForm
from bleachadmin.forms import ProductivityForm,ServicePriceRangeForm

from django.db.models.functions import TruncMonth as Month, TruncYear as Year
from django.db.models import Count
from operator import itemgetter
import requests

from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

class AdminHome(IsAdmin,View):
	def get(self,request):

		#cleaners and leaders
		cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER')
		leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE')
		count    = 0
		
		for cleaner in cleaners:
			print(cleaner.username)
			if count%2 == 0:
				cleaner.shift_start = datetime.strptime('06:00 AM','%I:%M %p')
				cleaner.shift_end   = datetime.strptime('06:00 PM','%I:%M %p')
			else:
				cleaner.shift_start = datetime.strptime('09:00 AM','%I:%M %p')
				cleaner.shift_end   = datetime.strptime('09:00 PM','%I:%M %p')
			count = count+1
			cleaner.save()

		for leader in leaders:
			print(leader.username)
			if count%2 == 0:
				leader.shift_start  = datetime.strptime('06:00 AM','%I:%M %p')
				leader.shift_end    = datetime.strptime('06:00 PM','%I:%M %p')
			else:
				leader.shift_start  = datetime.strptime('09:00 AM','%I:%M %p')
				leader.shift_end    = datetime.strptime('09:00 PM','%I:%M %p')
			count = count+1
			leader.save()


		#evaluators
		staff_sales_target = UserProfile.objects.filter(is_active=True).filter(Q(user_type='EVALUATOR')|Q(user_type='AGENT')|Q(user_type='BOOKINGOFFICER'))

		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)

		#Enquiry Details count
		try:
			enquiry = EvaluationDetails.objects.filter(is_active=True)
		except:
			enquiry	= None

		today_enquiry_count = enquiry.filter(proposed_time__date=count_today_start.date()).count()
		week_enquiry_count  = enquiry.filter( Q(Q(proposed_time__week=count_today_start.isocalendar()[1])&Q(proposed_time__year=count_today_start.year)) ).count()	

		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(Q(Q(start_at__date=count_today_start.date())|Q(end_at__date=count_today_start.date()))).count() 
		week_cleaning_job_count  = cleaning_job.filter(Q( Q(Q(start_at__week=count_today_start.isocalendar()[1])&Q(start_at__year=count_today_start.year)) | Q(Q(end_at__week=count_today_start.isocalendar()[1])&Q(end_at__year=count_today_start.year)))).count()		
		
		#Followup jobs count
		try:
			follow_up_job    = FollowUpTeam.objects.filter(is_active=True)
		except:
			follow_up_job	 = None

		today_follow_up_job_count = follow_up_job.filter(Q(Q(start_at__date=count_today_start.date())|Q(end_at__date=count_today_start.date()))).count() 
		week_follow_up_job_count  = follow_up_job.filter(Q( Q(Q(start_at__week=count_today_start.isocalendar()[1])&Q(start_at__year=count_today_start.year)) | Q(Q(end_at__week=count_today_start.isocalendar()[1])&Q(end_at__year=count_today_start.year)))).count()		

		#Feedback Staring count
		try:
			feedbacks                 = FeedBack.objects.filter(is_active=True)
		except:
			feedbacks				  = None


		prvmonth                      = count_today_start-relativedelta(months=1)
		month_average_feedback		  = feedbacks.filter(response_date__month=count_today_start.month,response_date__year=count_today_start.year).aggregate(Avg('rating'))['rating__avg']
		lastmonth_average_feedback	  = feedbacks.filter(response_date__month=prvmonth.month,response_date__year=prvmonth.year).aggregate(Avg('rating'))['rating__avg']	
		

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
			calendar_order_schedules 	= OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end)))).order_by('start_at').select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') | Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__remining_amount=0)&Q(order__remining_amount=F('order__evaluation__fine_amount'))) )) 
		except:
			calendar_order_schedules 	= None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end)))).order_by('start_at').select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			calendar_followup_schedules = None

		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') | Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__remining_amount=0)&Q(order__remining_amount=F('order__evaluation__fine_amount'))) ))
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end)))).select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			sp_calendar_followup_schedules = None

		try:
			spp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') | Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__remining_amount=0)&Q(order__remining_amount=F('order__evaluation__fine_amount'))) ))
		except:
			spp_calendar_order_schedules = None

		try:
			spp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start)))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			spp_calendar_followup_schedules = None

		#for not approved quatations cleaning in cleaning callendar
		try:
			calendar_notapprovedorder_schedules 	= OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end)))).order_by('start_at').select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(Q( Q(order__evaluation__quatation_status='PENDING')|Q(Q(order__evaluation__quatation_status='APPROVED')&Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0)) | Q(Q(order__evaluation__quatation_status='APPROVED')&Q(order__evaluation__payment_method='PREPAID')&Q(order__amount_paid=0)) )) 
		except:
			calendar_notapprovedorder_schedules 	= None

		try:
			sp_calendar_notapprovedorder_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(Q( Q(order__evaluation__quatation_status='PENDING')|Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='BREAKDOWN') & Q(order__preamount_paid = 0) ) | Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='PREPAID') & Q(order__amount_paid=0) ) ))
		except:
			sp_calendar_notapprovedorder_schedules = None

		try:
			spp_calendar_notapprovedorder_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(Q( Q(order__evaluation__quatation_status='PENDING')|Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='BREAKDOWN') & Q(order__preamount_paid = 0) ) | Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='PREPAID') & Q(order__amount_paid=0) ) ))
		except:
			spp_calendar_notapprovedorder_schedules = None

		#ticket approval task
		ticket_count = 0

		approve_tickets = Investigation.objects.filter(Q(Q(is_casesandcomplaints_submit=True)&Q(Q(is_buybackgiftpromo_approved=False)|Q(is_paybackdiscount_approved=False)))).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True),to_attr='followup'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.select_related('investigation').filter(is_active=True,investigation__is_paybackdiscount_approved=False),to_attr='paybackdiscounts'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.select_related('investigation').filter(investigation__is_buybackgiftpromo_approved=False,is_active=True),to_attr='buybackpromocodegifts')).annotate(paybackdiscount_count=Case(When(paybackdiscount_investigation__is_completed=False,then=1),default=0,output_field=IntegerField()),buybackpromocodegift_count=Case(When(buybackpromocodegift_investigation__is_completed=False,then=1),default=0,output_field=IntegerField())).filter( Q(Q(paybackdiscount_count__gte=1)|Q(buybackpromocodegift_count__gte=1)) )
		for ticket in approve_tickets:
			print(ticket.paybackdiscount_count,ticket.buybackpromocodegift_count,"appp")
		#add days left
		if approve_tickets:
			for ticket in approve_tickets:
				ticket.days_left = (timezone.now()-ticket.scheduled_at).days
				
				for paybackdiscount in ticket.paybackdiscounts:
					ticket_count += 1

				for buybackpromocodegift in ticket.buybackpromocodegifts:
					ticket_count += 1

		return render(request,'admin/home/home.html',{'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'month_average_feedback':month_average_feedback,'lastmonth_average_feedback':lastmonth_average_feedback,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'spp_calendar_order_schedules':spp_calendar_order_schedules,'spp_calendar_followup_schedules':spp_calendar_followup_schedules,'schedule_date':schedule_date,'staff_sales_targets':staff_sales_target,'approve_tickets':approve_tickets,"calendar_notapprovedorder_schedules":calendar_notapprovedorder_schedules,"sp_calendar_notapprovedorder_schedules":sp_calendar_notapprovedorder_schedules,"spp_calendar_notapprovedorder_schedules":spp_calendar_notapprovedorder_schedules,"ticket_count":ticket_count})


class ActiveSubscriptions(IsAdmin,View):
	def get(self,request):
		#subscriptions

		#Evaluation Details
		search                  = request.GET.get('search')
		
		if search:
			subscriptions = Order.objects.filter(Q(Q( Q(payment_status='PENDING') |Q(payment_status='ON_HOLD') | Q(payment_status='COMPLETED') ) & Q(evaluation__payment_method='SUBSCRIPTION') & Q(evaluation__quatation_status='APPROVED') & ~Q(order_status='ORDER_CANCELLED') & Q(Q(order_no__icontains=search)|Q(evaluation__customer__name__icontains=search)|Q(evaluation__customer__mobile_number__icontains=search)) )).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') ))
		else:
			subscriptions = Order.objects.filter(Q(Q( Q(payment_status='PENDING') |Q(payment_status='ON_HOLD') | Q(payment_status='COMPLETED') ) & Q(evaluation__payment_method='SUBSCRIPTION') & Q(evaluation__quatation_status='APPROVED') & ~Q(order_status='ORDER_CANCELLED') )).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') ))
		
		if subscriptions:
			for invoice in subscriptions:
				cleaning_price = 0
				for scheduler in invoice.orderschedules:
					if scheduler.work_status=='CLEANING_FULFILLED':
						cleaning_price += scheduler.order_scheduler_book.total_cost/len(scheduler.order_scheduler_book.bookschedules)	
				if cleaning_price > invoice.amount_paid:
					invoice.balance       = cleaning_price-invoice.amount_paid
				else:
					invoice.balance       = cleaning_price-invoice.amount_paid

				if invoice.balance == int(invoice.balance):
					invoice.balance = int(invoice.balance)

		#PAGINATION CLIENTS
		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1)
		paginator=Paginator(subscriptions,no_of_entries)
		try:
			subscriptions=paginator.page(page)
		except PageNotAnInteger:
			subscriptions=paginator.page(1)
		except EmptyPage:
			subscriptions = paginator.page(paginator.num_pages)

		# Get the index of the current page
		index = subscriptions.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]
		entry_per_page=(subscriptions.end_index())-(subscriptions.start_index())+1

		return render(request,'admin/subscription/active_subscriptions.html',{"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"subscriptions":subscriptions})



class ClientDetails(IsAdmin,View):
	def get(self,request):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		
		search                  = request.GET.get('search')

		if search:
			try:
				client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True,name__icontains=search).order_by('-id').prefetch_related(Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True).filter(Q(Q(order_status='ORDER_IN_PROGRESS')|Q(order_status='APPROVED_BY_CLIENT')|Q(order_status__isnull=True))),to_attr='order_evaluation')),to_attr='customer_evaluations'))
			except:
				client_details = None
		else:
			client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True).order_by('-id').prefetch_related(Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True).filter(Q(Q(order_status='ORDER_IN_PROGRESS')|Q(order_status='APPROVED_BY_CLIENT')|Q(order_status__isnull=True))),to_attr='order_evaluation')),to_attr='customer_evaluations'))			



		fil_status                = request.GET.get('status')			
					

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

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True),to_attr='paybackdiscounts'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True),to_attr='buybackpromocodegift'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)
		
		invoice = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') )).get(is_active=True,id=order_id)

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=order.evaluation.customer_id)
		except:
			client_details = None

		#orders count
		orders = Order.objects.filter(is_active=True,evaluation__customer_id=order.evaluation.customer_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		if invoice:
			cleaning_price = 0
			for scheduler in invoice.orderschedules:
				if scheduler.work_status=='CLEANING_FULFILLED':
					cleaning_price += scheduler.order_scheduler_book.total_cost/len(scheduler.order_scheduler_book.bookschedules)	
			if cleaning_price > invoice.amount_paid:
				invoice.balance       = cleaning_price-invoice.amount_paid
			else:
				invoice.balance       = cleaning_price-invoice.amount_paid

			if invoice.balance == int(invoice.balance):
				invoice.balance = int(invoice.balance)					
				
		return render(request,"admin/client/order-page.html",{"order":order,"invoice":invoice,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count})

	def post(self,request,order_id):
		# order_id            = request.POST.get('order')
		subscription_topay  = float(request.POST.get('subscription_topay'))
		print(order_id,subscription_topay,"ddd")

		Order.objects.filter(id=order_id).update(subscription_topay=subscription_topay,subscription_topay_date=timezone.now())

		order = Order.objects.filter(id=order_id).first()

		evaluaation = order.evaluation

		if evaluaation.customer.is_sms == True:

			url = "https://smsapi.future-club.com/fccsms.aspx"

			if evaluaation.customer.sms_preference == 'ENGLISH':

				message = "Dear Customer, Please find the Invoice against the order number "+str(evaluaation.evaluation_id)+"  here https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluaation.evaluation_id[3:])+""+str(evaluaation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
		
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
			
			else:

				message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluaation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluaation.evaluation_id[3:])+""+str(evaluaation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
		
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
			
			headers = {
				'cache-control': "no-cache"
			}

			response = requests.request("GET", url, headers=headers, params=querystring)

			print(message,response.text,"respo")

		messages.success(request,"Invoice has been Sent !")

		return redirect('bleach_admin:admin-client-orderdetails', order_id)


class TicketDetails(IsAdmin,View):
	def get(self,request):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			investigators = UserProfile.objects.filter(is_active=True,user_type='QUALITYCONTROLL')
		except:
			investigators = None

		search                  = request.GET.get('search')
		
		#Followup details
		if search:
			if search.startswith('TKT'):
				search = search[len('TKT'):]
			
			tickets 	             = FollowUp.objects.select_related('investigation__order_schedule__order__evaluation__customer','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate').filter(is_active=True).filter(Q(Q(investigation__order_schedule__order__evaluation__customer__name__icontains=search)|Q(ticket_no__icontains=search))).order_by('-id').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))				
			
			if not search.startswith('TKT'):
				search = 'TKT'+search				
		else:
			tickets 	             = FollowUp.objects.filter(is_active=True).select_related('investigation__order_schedule__order__evaluation__customer','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate').order_by('-id').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))		

		follow_ups_count = FollowUp.objects.filter(Q(is_active=True)&Q(Q(status='TICKET_RISED')|Q(status='FOLLOWUP_IN_PROGRESS'))).count()


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
		
		followup_details = FollowUp.objects.select_related('investigation__investigator','investigation__order','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate','investigation__order_schedule__order_scheduler_book').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_media',queryset=FollowUpTeamMedia.objects.filter(is_active=True),to_attr='followupmedias'),Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules'),Prefetch('investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('follow_up_of_section',queryset=FollowUpSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesectionsfollowup',queryset=FollowUpSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='followupsections'),Prefetch('investigation__buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True).prefetch_related(Prefetch('buybackpromocodegiftdetails',queryset=BuybackPromocodeGiftDetails.objects.filter(is_active=True),to_attr='buybackpromogiftdetails'),Prefetch('buybackpromocodegift_media',queryset=BuybackPromocodeGiftDetailsMedia.objects.filter(is_active=True),to_attr='buybackpromogiftmedias')),to_attr='buybackpromogifts'),Prefetch('investigation__paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True).prefetch_related(Prefetch('paybackdiscount_details',queryset=PaybackDiscountDetails.objects.filter(is_active=True),to_attr='paybackdiscountdetails'),Prefetch('paybackdiscount_media',queryset=PaybackDiscountDetailsMedia.objects.filter(is_active=True),to_attr='paybackdiscountmedias')),to_attr='paybackdiscounts'),Prefetch('investigation__reporting_investigation',queryset=Reporting.objects.filter(is_active=True).prefetch_related(Prefetch('reporting_media',queryset=ReportingMedia.objects.filter(is_active=True),to_attr='reporting_medias')),to_attr='reports')).get(is_active=True,id=followup_id)
			
			

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=client_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		return render(request,'admin/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})


class OrderDetails(IsAdmin,View):
	def get(self,request):

		evaluators = UserProfile.objects.filter(is_active=True).filter(Q(user_type='EVALUATOR')|Q(user_type='AGENT')).only('id','name')
		
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
		#for order filtering
		status = request.GET.get('status')
		
		if search:
			evaluations = Evaluation.objects.filter(is_active=True).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(customer__mobile_number__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCEL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
		else:
			evaluations = Evaluation.objects.filter(is_active=True).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCEL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
			

		if evaluations:
			#approved count should change code
			approved_orders_count = 0
			for evaluation in evaluations:
				if evaluation.evaluationorder and evaluation.quatation_status == 'APPROVED':
					for order in evaluation.evaluationorder:
						if (order.payment_status == 'COMPLETED' or order.preamount_paid != 0 or order.evaluation.payment_method == 'POSTPAID') and (order.order_status == 'APPROVED_BY_CLIENT'):				
							approved_orders_count += 1
							
			pending_orders_count  =	evaluations.filter(Q(quatation_status='PENDING')).count()
		else:
			approved_orders_count = 0
			pending_orders_count  = 0	



		#Prefetch filters
		try:
			fil_governorate       	  = int(request.GET.get('governorate'))
			areas                 	  = Area.objects.filter(governorate_id=fil_governorate) 
		except:
			fil_governorate       	  = None
			areas               	  = None

		try:	
			fil_area				  = int(request.GET.get('area'))
		except:
			fil_area      	          = None

		try:
			fil_evaluator	   		  = int(request.GET.get('evaluator'))
		except:
			fil_evaluator 			  = None

		try:
			fil_cleaning_policy       = request.GET.get('cleaning_policy')
		except:
			fil_cleaning_policy       = None

		try:
			fil_service_type      	  = int(request.GET.get('service_type'))
		except:
			fil_service_type      	  = None
			

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

		if fil_evaluator:
		    case3 		= Q(Q(evaluator__id=fil_evaluator) | Q(Q(evaluation__call_attender__id=fil_evaluator) & Q(evaluator__id=None)))
		    count_case3 = Q(Q(evaluation_details__evaluator__id=fil_evaluator) | Q(Q(evaluation_details__evaluation__call_attender__id=fil_evaluator) & Q(evaluation_details__evaluator__id=None)))
		    customer_address_filter.append(case3)
		    count_customer_address_filter.append(count_case3)
		
		if fil_governorate or fil_area or fil_evaluator: 
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
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area','evaluator','evaluation__call_attender').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_book_count=Count(Case(When( Q(count_evaluation_book_prefetch_filter & count_customer_address_prefetch_filter),then=1),output_field=IntegerField()))).filter(address_book_count__gt=0)		 
			print("both")
		elif evaluation_book_prefetch_filter and not customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(book_count=Count(Case(When( count_evaluation_book_prefetch_filter,then=1),output_field=IntegerField()))).filter(book_count__gt=0)
			print("book only")
		elif not evaluation_book_prefetch_filter and customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area','evaluator','evaluation__call_attender').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)
			print("address only") 
		else:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))		
			print("not at all")
		
		#exclude atleast 1 not completed evaluation
		exclude_ids = []	
		for evaluation in evaluations:
			if not evaluation.completed_evaluations:
				exclude_ids.append(evaluation.id)
		evaluations = evaluations.exclude(id__in=exclude_ids)
		
		fil_status         = request.GET.get('status')
		fil_payment_policy = request.GET.get('payment_policy')
		
		#filters
		filters=[]
		if fil_status:
			if fil_status == 'ORDER_IN_PROGRESS' or fil_status == 'ORDER_CLOSED' or fil_status == 'CANCEL_IN_PROGRESS' or fil_status == 'ORDER_CANCELLED' or fil_status == 'APPROVED-NOT PAID' or fil_status == 'EVALUATING':
				if fil_status == 'ORDER_IN_PROGRESS':
					case1 = Q(order_in_progress_count__gte=1)
				elif fil_status == 'ORDER_CLOSED':
					case1 = Q(order_closed_count__gte=1)
				elif fil_status == 'APPROVED-NOT PAID':
					case1 = Q(Q(approved_not_paid_count__gte=1)&~Q(payment_method='SUBSCRIPTION'))
				elif fil_status == 'CANCEL_IN_PROGRESS':
					case1 = Q(order_cancellinprogress_count__gte=1)
				elif fil_status == 'ORDER_CANCELLED':
					case1 = Q(order_cancelled_count__gte=1)
				elif fil_status == 'EVALUATING':
					case1 = Q(quatation_status__isnull=True)
			else:
				if fil_status == 'APPROVED':
					case1 = Q(Q(quatation_status=fil_status)&~Q(order_in_progress_count__gte=1)&~Q(order_closed_count__gte=1)&~Q(approved_not_paid_count__gte=1))
				else:
					case1 = Q(quatation_status=fil_status)
			filters.append(case1)

		if fil_payment_policy:
			case2 = Q(payment_method=fil_payment_policy)
			filters.append(case2)

		if fil_status or fil_payment_policy : 
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

		return render(request,'admin/order/orders.html',{"evaluations":evaluations,"evaluators":evaluators,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy,"fil_evaluator":fil_evaluator})		

class CustomerBookingsList(IsAdmin,View):
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
		#for order filtering
		status = request.GET.get('status')
		
		if search:
			evaluations = Evaluation.objects.filter(is_active=True,booking_evaluation__is_active=True).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(customer__mobile_number__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCELL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
		else:
			evaluations = Evaluation.objects.filter(is_active=True,booking_evaluation__is_active=True).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCELL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
			

		if evaluations:
			#approved count should change code
			approved_orders_count = 0
			for evaluation in evaluations:
				if evaluation.evaluationorder and evaluation.quatation_status == 'APPROVED':
					for order in evaluation.evaluationorder:
						if (order.payment_status == 'COMPLETED' or order.preamount_paid != 0 or order.evaluation.payment_method == 'POSTPAID') and (order.order_status == 'APPROVED_BY_CLIENT'):				
							approved_orders_count += 1
			
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
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_book_count=Count(Case(When( Q(count_evaluation_book_prefetch_filter & count_customer_address_prefetch_filter),then=1),output_field=IntegerField()))).filter(address_book_count__gt=0)
			print("both")
		elif evaluation_book_prefetch_filter and not customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(book_count=Count(Case(When( count_evaluation_book_prefetch_filter,then=1),output_field=IntegerField()))).filter(book_count__gt=0)
			print("book only")
		elif not evaluation_book_prefetch_filter and customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)
			print("address only")
		else:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))
			print("not at all")

		#exclude atleast 1 not completed evaluation
		exclude_ids = []	
		for evaluation in evaluations:
			if not evaluation.completed_evaluations:
				exclude_ids.append(evaluation.id)
		evaluations = evaluations.exclude(id__in=exclude_ids)	

		fil_status              = request.GET.get('status')
		fil_payment_policy		= request.GET.get('payment_policy')
		#filters
		filters=[]
		if fil_status:
			if fil_status == 'ORDER_IN_PROGRESS' or fil_status == 'ORDER_CLOSED' or fil_status == 'APPROVED-NOT PAID' or fil_status == 'ORDER_CANCELLED' or fil_status == 'CANCELL_IN_PROGRESS' or fil_status == 'EVALUATING':
				if fil_status == 'ORDER_IN_PROGRESS':
					case1 = Q(order_in_progress_count__gte=1)
				elif fil_status == 'ORDER_CLOSED':
					case1 = Q(order_closed_count__gte=1)
				elif fil_status == 'APPROVED-NOT PAID':
					case1 = Q(Q(approved_not_paid_count__gte=1)&~Q(payment_method='SUBSCRIPTION'))
				elif fil_status == 'CANCELL_IN_PROGRESS':
					case1 = Q(order_cancellinprogress_count__gte=1)
				elif fil_status == 'ORDER_CANCELLED':
					case1 = Q(order_cancelled_count__gte=1)
				elif fil_status == 'EVALUATING':
					case1 = Q(quatation_status__isnull=True)
			else:
				if fil_status == 'APPROVED':
					case1 = Q(Q(quatation_status=fil_status)&~Q(order_in_progress_count__gte=1)&~Q(order_closed_count__gte=1)&~Q(approved_not_paid_count__gte=1))
				else:
					case1 = Q(quatation_status=fil_status)
			
			filters.append(case1)

		if fil_payment_policy:
			case2 = Q(payment_method=fil_payment_policy)
			filters.append(case2)
			
		if fil_status or fil_payment_policy: 
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

		return render(request,'admin/customer-bookings/bookings.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy})

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
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True).filter(Q(Q(evaluation__evaluation_id__icontains=search)|Q(evaluation__customer__name__icontains=search))).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(Q(is_feedback_marked=True))		
			except:
				order_wise_feedbacks = None		
		else:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(Q(is_feedback_marked=True))						
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
		# fil_maximumstarring       		  = request.GET.get('maximumstarring')
		#filters 	
		filters=[] 
		if fil_minimumstarring: 
		    case1 = Q(Q(avg_starring__gte=fil_minimumstarring)&Q(avg_starring__lt=float(fil_minimumstarring)+1))
		    filters.append(case1)

		if fil_minimumstarring : 
			filters = functools.reduce(operator.and_,filters)
			order_wise_feedbacks = order_wise_feedbacks.filter(filters)					    

		#to find starring caluculations in whole system
		full_order_wise_feedbacks     = Order.objects.select_related('evaluation__customer').filter(is_active=True).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField())).filter(Q(is_feedback_marked=True))		
		total_feedbacks               = full_order_wise_feedbacks.filter(is_feedback_marked=True).count()
				
				
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

		return render(request,'admin/feedback/feedbacks.html',{"total_feedbacks":total_feedbacks,"order_wise_feedbacks":order_wise_feedbacks,"full_order_wise_feedbacks":full_order_wise_feedbacks,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_minimumstarring":fil_minimumstarring,"fil_service_type":fil_service_type,})

class FeedbackAdvanced(IsAdmin,View):
	def get(self,request,client_id,order_id):
		
		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)

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

		return render(request,'admin/feedback/feedback-page.html',{"order":order,"client_details":client_details,"feedback_details":feedback_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"other_feedbacks":other_feedbacks,"average_feedback":average_feedback,})




class ResourceManagement(IsAdmin,View):
	def get(self,request):
		
		try:
			staffs = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER')))
		except:
			staffs = None	


		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)


		#total workers count
		try:
			total_workers = UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).count()
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



		#Resources
		#date			
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
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))&Q(name__icontains=search)).prefetch_related('leave_staff').annotate(leave=Sum( Case( When( Q(Q(leave_staff__leave_date__gte=workers_date_start.date())&Q(leave_staff__leave_date__lt=workers_date_end.date())),then=1),default=0,output_field=IntegerField())) )
			except:
				workers =  None
		else:
			try:
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).prefetch_related('leave_staff').annotate(leave=Sum( Case( When( Q(Q(leave_staff__leave_date__gte=workers_date_start.date())&Q(leave_staff__leave_date__lt=workers_date_end.date())),then=1),default=0,output_field=IntegerField())) )
			except:
				workers =  None
 
		try:		
			workers_details = workers.prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(Q(start_at__gte=workers_date_start)&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_start)&Q(end_at__lte=workers_date_end))) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation','team__order_scheduler__order_scheduler_book'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(Q(start_at__gte=workers_date_start)&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_start)&Q(end_at__lte=workers_date_end))) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details'))
		except:
			workers_details = None


		#Filter
		try:
			fil_staff = request.GET.get('staff')
		except:
			fil_staff = ''

		try:
			service_type = request.GET.get('service_type')
		except:
			service_type = None
				
		#filters 	
		filters=[] 
		if fil_staff: 
		    case1 = Q(user_type=fil_staff)
		    filters.append(case1)
		
		if service_type:
			if service_type == 'is_general_skill':
				case2 = Q(is_general_skill=True)
			if service_type == 'is_deep_skill':
				case2 = Q(is_deep_skill=True)
			if service_type == 'is_upholstery_skill':
				case2 = Q(is_upholstery_skill=True)
			if service_type == 'is_carpet_skill':
				case2 = Q(is_carpet_skill=True)
			if service_type == 'is_kitchen_skill':
				case2 = Q(is_kitchen_skill=True)
			if service_type == 'is_sterilization_skill':
				case2 = Q(is_sterilization_skill=True)
			filters.append(case2)

		if fil_staff or service_type: 
		    filters         = functools.reduce(operator.and_,filters)
		    workers_details = workers_details.filter(filters)

		#time filter
		try:
			fil_startingtime       = request.GET.get('fil_startingtime')
		except:
			fil_startingtime       = None

		try:
			fil_endingtime         = request.GET.get('fil_endingtime')	
		except:
			fil_endingtime	       = None

		
		if fil_startingtime and fil_endingtime:
			actual_starting_datetime     = datetime.strptime(fil_startingtime,'%I:%M %p').replace(day=workers_date.day,month=workers_date.month,year=workers_date.year)
			actual_ending_datetime       = datetime.strptime(fil_endingtime,'%I:%M %p').replace(day=workers_date.day,month=workers_date.month,year=workers_date.year)
			
			if actual_starting_datetime > actual_ending_datetime:
				messages.error(request,"Starting Time should be less than Ending Time !")
			else:
				workers_details = workers_details.annotate(cleaningbusy=Sum(Case(When(Q( Q(Q(cleaning_member_user__start_at__gte=actual_starting_datetime)&Q(cleaning_member_user__start_at__lte=actual_ending_datetime)) | Q(Q(cleaning_member_user__end_at__gte=actual_starting_datetime)&Q(cleaning_member_user__end_at__lte=actual_ending_datetime)) | Q(Q(cleaning_member_user__start_at__lte=actual_starting_datetime)&Q(cleaning_member_user__end_at__gte=actual_starting_datetime)&Q(cleaning_member_user__start_at__lte=actual_ending_datetime)&Q(cleaning_member_user__end_at__gte=actual_ending_datetime)) | Q(Q(cleaning_member_user__start_at__gte=actual_starting_datetime)&Q(cleaning_member_user__end_at__gte=actual_starting_datetime)&Q(cleaning_member_user__start_at__lte=actual_ending_datetime)&Q(cleaning_member_user__end_at__lte=actual_ending_datetime)) ),then=1),default=0,output_field=IntegerField())),followupbusy=Sum(Case(When(Q(Q(Q(followup_member__start_at__gte=actual_starting_datetime)&Q(followup_member__start_at__lte=actual_ending_datetime))|Q(Q(followup_member__end_at__gte=actual_starting_datetime)&Q(followup_member__end_at__lte=actual_ending_datetime))|Q(Q(followup_member__start_at__lte=actual_starting_datetime)&Q(followup_member__end_at__gte=actual_starting_datetime)&Q(followup_member__start_at__lte=actual_ending_datetime)&Q(followup_member__end_at__gte=actual_ending_datetime)) | Q(Q(followup_member__start_at__gte=actual_starting_datetime)&Q(followup_member__end_at__gte=actual_starting_datetime)&Q(followup_member__start_at__lte=actual_ending_datetime)&Q(followup_member__end_at__lte=actual_ending_datetime))),then=1),default=0,output_field=IntegerField()))).exclude(Q(Q(cleaningbusy__gte=1)|Q(followupbusy__gte=1)))

		return render(request,'admin/resource/resources.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,"staffs":staffs,"fil_staff":fil_staff,"fil_endingtime":fil_endingtime,"fil_startingtime":fil_startingtime,'service_type':service_type})

class PaymentDetails(IsAdmin,View):
	def get(self,request):

		try:
			service_types = ServiceType.objects.filter(is_active=True) 
		except:
			service_types =	None
		
		#Evaluation Details
		search                  = request.GET.get('search')
		
		#sales amount
		if search:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).filter(~Q(order_status='ORDER_CANCELLED')).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         = None
		else:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(~Q(order_status='ORDER_CANCELLED')).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         = None
				
		#Pending Payments
		try:
			pending_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) ))
		except:
			pending_payments = None

		#Pending Payment and Order Count	
		if pending_payments: 
			total_pending_amount = 0
			total_pending_orders = pending_payments.count()
			for payment in pending_payments:
				if payment.evaluation.payment_method in ['PREPAID','POSTPAID','BREAKDOWN']:
					total_pending_amount += payment.remining_amount
				if payment.evaluation.payment_method == 'SUBSCRIPTION':
					total_pending_amount += payment.subscription_topay			
		else:
			total_pending_amount = 0
			total_pending_orders = 0

		#filters

		fil_order_status			= request.GET.get('status')

		fil_payment_status       	= request.GET.get('payment_status')

		fil_payment_policy			= request.GET.get('payment_policy')

		filters = []
		if fil_payment_policy:
			case1 = Q(evaluation__payment_method=fil_payment_policy)
			filters.append(case1)

		if fil_payment_status:
			if fil_payment_status == 'PENDING':
				case2       = Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))|Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0))) )
			else:
				case2       = Q(payment_status=fil_payment_status)
			filters.append(case2)
			
		if fil_order_status:
			if fil_order_status == 'NOT STARTED':
				case3 = Q(Q(cleaning_in_progress_count=0)&Q(completed_cleaning_count=0))
			elif fil_order_status == 'IN PROGRESS':
				case3 = Q(cleaning_in_progress_count__gte=1)
			elif fil_order_status == 'COMPLETED':
				case3 = Q(completed_cleaning_count=F('cleaning_count'))

			filters.append(case3)

		if fil_payment_policy or fil_payment_status or fil_order_status:
			filters=functools.reduce(operator.and_,filters)
			invoices = invoices.filter(filters)
			

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

		return render(request,'admin/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,'no_of_entries':no_of_entries,"service_types":service_types,"fil_payment_policy":fil_payment_policy,"fil_payment_status":fil_payment_status,"fil_order_status":fil_order_status})		


class TicketApprove(IsAdmin,View):
	def get(self,request,ticket_id):
		
		try:
			investigation_details = Investigation.objects.select_related('order_schedule__customer_address__area','order_schedule__order_scheduler_book__service_type','order_schedule__evaluation_details__evaluator','investigator','order__evaluation__customer','order__evaluation__call_attender').prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True),to_attr='follow_up_schedules')),to_attr='followup'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True).prefetch_related(Prefetch('paybackdiscount_details',queryset=PaybackDiscountDetails.objects.filter(is_active=True),to_attr='paybackdiscountdetails')),to_attr='paybackdiscount'),Prefetch('reporting_investigation',queryset=Reporting.objects.filter(is_active=True),to_attr='reports'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True).prefetch_related(Prefetch('buybackpromocodegiftdetails',queryset=BuybackPromocodeGiftDetails.objects.filter(is_active=True),to_attr='buybackpromogiftdetails')),to_attr='buybackpromocodegift'),Prefetch('order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_teams')).get(id=ticket_id)
		except:
		 	investigation_details = None

		ticket_types_list = []
		if investigation_details.ticket_types:
			ticket_types = investigation_details.ticket_types.split(",")
			for type in ticket_types:
				ticket_types_list.append(type)
		else:
			ticket_types = None

		print(ticket_types_list,"typo")

		promocodes = Promocode.objects.filter(is_active=True)

		return render(request,'admin/ticket/ticket-approval.html',{"ticket_types":ticket_types,"investigation_details":investigation_details,"promocodes":promocodes})

	def post(self,request,ticket_id):

		try:
			paybackdiscount = PaybackDiscount.objects.get(investigation__id=int(ticket_id),is_active=True)
		except:
			paybackdiscount = None
		
		try:	
			buybackpromocodegift = BuybackPromocodeGift.objects.get(investigation__id=int(ticket_id),is_active=True)
		except:
			buybackpromocodegift = None

		investigation = Investigation.objects.get(id=ticket_id)
		
		approve_action = request.POST.get('approve_action')

		if approve_action == 'payback':
			
			payback_amount = request.POST.get('payback_amount',0.0)

			paybackdiscount.approved_total_cost = payback_amount

			paybackdiscount.approved_by = request.user

			paybackdiscount.is_completed = True

			paybackdiscount.save()

			investigation.is_paybackdiscount_approved = True

			investigation.save()

			#Email Send
			accountant_list = UserProfile.objects.filter(is_active=True,user_type='ACCOUNTANT').values_list('email',flat=True)
			msg_html = render_to_string('email/paybackdiscount_approval.html',{'paybackdiscount':paybackdiscount})
			msg      = EmailMultiAlternatives('Payback/Discount Confirm', '', 'notification@bleach-kw.com', accountant_list)
			msg.attach_alternative(msg_html, "text/html")
			msg.send(fail_silently=False)

			messages.success(request,"Payback Approved !")

		if approve_action == 'buyback':

			buyback_type = request.POST.get('buyback_type')

			if buyback_type == 'PROMOCODE':

				promo_code = request.POST.get('promocode',None)

				buybackpromocodegift.approved_promo_code = promo_code

				buybackpromocodegift.approved_by = request.user
				
				buybackpromocodegift.save()

			else:

				buyback_amount = request.POST.get('buyback_amount',0.0)

				buybackpromocodegift.approved_total_cost = buyback_amount

				buybackpromocodegift.approved_by = request.user

				buybackpromocodegift.save()

			buybackpromocodegift.approved_option = buyback_type

			buybackpromocodegift.is_completed = True
			
			buybackpromocodegift.save()

			investigation.is_buybackgiftpromo_approved = True

			investigation.save()

			messages.success(request,"BuyBack/PromoCode/Gift Approved !")
		
		return redirect('bleach_admin:admin-ticketapprove', ticket_id)

class PromocodeView(IsAdmin,View):

	def get(self,request):
		
		try:
			promo_codes = Promocode.objects.filter(is_active=True).order_by('-created').annotate(active=Case(When(expiry_date__gt=timezone.now().date(),then=True),default=False,output_field=BooleanField()))
		except:
			promo_codes = None

		#counts
		try:
			active_promocodes_count = promo_codes.filter(active=True).count()
			used_coupons_count      = promo_codes.aggregate(total_used_count=Sum('total_used'))['total_used_count']
		except:
			active_promocodes_count = 0
			used_coupons_count      = 0

		return render(request,'admin/promocode/promo.html',{'promo_codes':promo_codes,'active_promocodes_count':active_promocodes_count,'used_coupons_count':used_coupons_count,})

	def post(self,request):
		action = request.POST.get('action_type')

		if action == 'addpromocode':
			promocode_form = PromocodeForm(request.POST)
			if promocode_form.is_valid():
				promocode_form.save()
				messages.success(request,"Promocode Successfully Added")
			else:
				messages.error(request,get_error(promocode_form))

		if action == 'editpromocode':
			promocode_id = request.POST.get('promocodeid')
			promocode = Promocode.objects.get(id=promocode_id)

			promocode_form = PromocodeForm(request.POST,instance=promocode)
			
			if promocode_form.is_valid():
				promocode_form.save()
				messages.success(request,"Promocode Successfully Updated")
			else:
				messages.error(request,get_error(promocode_form))		
		
		return redirect('bleach_admin:admin-promocode')		



class ProductivityView(IsAdmin,View):

	def get(self,request):
		
		try:
			productivities = ServiceProductivity.objects.filter(is_active=True)
		except:
			productivities = None

		try:
			price_ranges = ServicePriceRange.objects.filter(is_active=True)
		except:
			price_ranges = None


		added_services = productivities.values_list('service_type',flat=True)
		try:
			service_types = ServiceType.objects.filter(is_active=True)
		except:
			service_types = None

		return render(request,'admin/productivity/productivity.html',{'productivities':productivities,'service_types':service_types,'price_ranges':price_ranges})

	def post(self,request):
		action = request.POST.get('action_type')

		if action == 'editproductivity':
			productivity_id = request.POST.get('productivityid')
			productivity    = ServiceProductivity.objects.get(id=productivity_id)

			productivity_form = ProductivityForm(request.POST,instance=productivity)
			
			if productivity_form.is_valid():
				productivity_form.save()
				messages.success(request,"Service Productivity Successfully Updated")
			else:
				messages.error(request,get_error(productivity_form))	

		elif action == 'addpricerange':
			pricerange_form = ServicePriceRangeForm(request.POST)
			
			if pricerange_form.is_valid():
				pricerange_form.save()
				messages.success(request,"Service Price Range Successfully Updated")
			else:
				messages.error(request,get_error(pricerange_form))

		elif action == 'editpricerange':	
			pricerange_id   = request.POST.get('pricerange_id')
			pricerange      = ServicePriceRange.objects.get(id=pricerange_id)
			pricerange_form = ServicePriceRangeForm(request.POST,instance=pricerange)
			
			if pricerange_form.is_valid():
				print(pricerange_form)
				pricerange_form.save()
				messages.success(request,"Service Price Range Successfully Updated")
			else:
				messages.error(request,get_error(pricerange_form))

		return redirect('bleach_admin:admin-productivity')

def DeletePriceRange(request):
	response_dict            = {}
	response_dict['success'] = False

	pricerange_id = request.GET.get('pricerange_id')
	price_range   = ServicePriceRange.objects.get(id=pricerange_id)
	price_range.delete()

	response_dict['success'] = True

	return JsonResponse(response_dict)


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

			location_dict = {
					"location" : location.name,
					"count" : sales_location_count,
					}
			data.append(location_dict)

		data_sorted = sorted(data, key = itemgetter('count'),reverse=True)

		data_list = data_sorted[:5]

		others_sum = 0 

		for d in data_sorted[5:] :
			others_sum += int(d['count'])
		
		others_dict = {
			"location" : 'Others',
			"count" : others_sum,
		}

		data_list.append(others_dict)

		print(data_list,"sortt")

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

		# appending each location counts
		for location in location_types:
			
			sales_location_count = Order.objects.filter(evaluation__quatation_status='APPROVED',evaluation__quatation_approved_date__range=(prevdate_date_start,todate_date_end),evaluation__evaluation_details__evaluation_book_evaluation_details__area_type=location.name).count()
			if not sales_location_count:
				sales_location_count = 0
				
			location_dict = {
					"location" : location.name,
					"count" : sales_location_count,
					}
			data.append(location_dict)

		data_sorted = sorted(data, key = itemgetter('count'),reverse=True)

		data_list = data_sorted[:5]

		others_sum = 0 

		for d in data_sorted[5:] :
			others_sum += int(d['count'])
		
		others_dict = {
			"location" : 'Others',
			"count" : others_sum,
		}

		data_list.append(others_dict)

		print(data_list,"sortt2")
 
	return JsonResponse(data_list,safe=False)

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
		monthdate2 = datetime(day=1,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)

		sales = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,created__range=(monthdate1,monthdate2))   #.values('created').values('created').annotate(month=Month('created'),).values('month').annotate(count=Sum('evaluation__total_cost'))

		sales_month = sales.dates('created','month')
		print(sales,"po")
		for sale in sales_month:
			month_start = datetime(day=1,month=sale.month,year=sale.year,hour=0,minute=0,second=0,microsecond=0)
			month_end = datetime(day=1,month=sale.month,year=sale.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)

			total_sales = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(month_start,month_end)).aggregate(count=Sum('evaluation__total_cost'))['count']

			sales_dict = {
			"date" : sale.month,
			"amount" : total_sales or 0.0,
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

			print(total_sales,"qtc")
			sales_dict = {
			"date" : single_date,
			"amount" : total_sales,
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
		monthdate2 = datetime(day=1,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)

		if evaluator_id == 0 :
			sales = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=None,evaluation__quatation_status__isnull=False,created__range=(monthdate1,monthdate2))
		else:
			sales = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=evaluator_id,evaluation__quatation_status__isnull=False,created__range=(monthdate1,monthdate2))
		print(sales,evaluator_id,"po")

		sales_month = sales.dates('created','month')
		
		for sale in sales_month:
			month_start = datetime(day=1,month=sale.month,year=sale.year,hour=0,minute=0,second=0,microsecond=0)
			month_end = datetime(day=1,month=sale.month,year=sale.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
			
			total_sales = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=evaluator_id,evaluation__quatation_status__isnull=False,order_status='ORDER_CLOSED',created__range=(monthdate1,monthdate2)).aggregate(count=Sum('evaluation__total_cost'))['count'] or 0.0
			total_orders = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=evaluator_id,evaluation__quatation_status__isnull=False,created__range=(monthdate1,monthdate2)).aggregate(count2=Sum('evaluation__total_cost'))['count2'] or 0.0
			print(total_sales,total_orders,"totsal")
			
			sales_dict = {
			"date" : sale.month,
			"amount" : total_sales,
			"total" : total_orders,
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

		testvar = 0
		for single_date in daterange:
			saletarget_date_start  = single_date.replace(hour=0,minute=0,second=0,microsecond=0)
			saletarget_date_end    = single_date+timedelta(1)

			if evaluator_id == '0' :
				total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__quatation_status__isnull=False,order_status='ORDER_CLOSED',created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)			

				total_orders = Order.objects.filter(is_active=True,evaluation__evaluation_details__evaluator=None,evaluation__quatation_status__isnull=False,created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
			else:
				total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator_id,evaluation__quatation_status__isnull=False,order_status='ORDER_CLOSED',created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)			

				total_orders = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator_id,evaluation__quatation_status__isnull=False,created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
			
			testvar += total_orders or 0.0
			print(total_sales,total_orders,evaluator_id,"red2")
			sales_dict = {
			"date" : single_date,
			"amount" : total_sales or 0.0,
			"total" : total_orders or 0.0,
			}
			data.append(sales_dict)
		print(testvar,"warria")
	print(data,"sdt")
	return JsonResponse(data,safe=False)

#ajax for sales target charts
def PaymentData(request):
	data = []
	dom = request.GET.get('dom', None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(dom,prevdate,todate,"pop333")
	sales_dict = dict()
	
	if dom == 'Month':
		print("derr")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")

		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=1,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)

		sales = Order.objects.filter(is_active=True,created__range=(monthdate1,monthdate2)).filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD')|Q(payment_status='COMPLETED')))
		print(sales,"po")

		sales_month = sales.dates('created','month')
		
		for sale in sales_month:
			month_start = datetime(day=1,month=sale.month,year=sale.year,hour=0,minute=0,second=0,microsecond=0)
			month_end = datetime(day=1,month=sale.month,year=sale.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
			
			paid_orders = Order.objects.filter(is_active=True,payment_status='COMPLETED',created__range=(monthdate1,monthdate2)).aggregate(count=Sum('evaluation__total_cost'))['count'] or 0.0
			pending_orders = Order.objects.filter(is_active=True,created__range=(monthdate1,monthdate2)).filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))).aggregate(count2=Sum('evaluation__total_cost'))['count2'] or 0.0
			print(paid_orders,pending_orders,"totsal")
			
			sales_dict = {
			"date" : sale.month,
			"paid" : paid_orders,
			"pending" : pending_orders,
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

			paid_orders = Order.objects.filter(is_active=True,payment_status='COMPLETED',created__gte=saletarget_date_start,created__lte=saletarget_date_end).aggregate(count=Sum('evaluation__total_cost'))['count'] or 0.0
			pending_orders = Order.objects.filter(is_active=True,created__gte=saletarget_date_start,created__lte=saletarget_date_end).filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))).aggregate(count2=Sum('evaluation__total_cost'))['count2'] or 0.0
			
			print(paid_orders,pending_orders,"red2")
			sales_dict = {
			"date" : single_date,
			"paid" : paid_orders or 0.0,
			"pending" : pending_orders or 0.0,
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
	agents_sales_target = UserProfile.objects.filter(is_active=True,user_type='AGENT')
	bookingofficer_sales_target = UserProfile.objects.filter(is_active=True,user_type='BOOKINGOFFICER')
	target_date = request.GET.get('target_date')
	date_or_month = request.GET.get('date_or_month')
	print(date_or_month,"dom")

	if date_or_month == 'Month':
		#month year range making
		month,year = target_date.split("/")
		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
		print(monthdate1,monthdate2,"msdt")
		daterange  = pd.date_range(monthdate1, monthdate2)
	else:
		target_date = datetime.strptime(target_date, '%d-%m-%Y')
		target_date_start = target_date.replace(hour=0,minute=0,second=0,microsecond=0)
		target_date_end= target_date+timedelta(1)

	for evaluator in evaluators_sales_target:
		# total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,order_status='ORDER_CLOSED',created__range=(target_date_start,target_date_end)).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		
		if date_or_month == 'Month':
			total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,created__range=(monthdate1,monthdate2),evaluation__quatation_status='APPROVED')
			total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,created__range=(monthdate1,monthdate2))
		else:
			total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,created__range=(target_date_start,target_date_end),evaluation__quatation_status='APPROVED')
			total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,created__range=(target_date_start,target_date_end))

		total_sales_approved_amount = total_sales_approved.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		total_sales_approved_count = total_sales_approved.count()
		
		total_sales_submitted_amount = total_sales_submitted.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		total_sales_submitted_count = total_sales_submitted.count()

		if not total_sales_approved_amount:
			total_sales_approved_amount = 0.0
		if not total_sales_submitted_amount:
			total_sales_submitted_amount = 0.0

		print(total_sales_approved_amount,total_sales_submitted_amount,"evat")

		evaluator_target_dict = {
		"evaluator_id" : evaluator.id,
		"amount" : total_sales_approved_amount,
		"submitted":total_sales_submitted_amount,
		"approved_count":total_sales_approved_count,
		"submitted_count":total_sales_submitted_count
		}
		data.append(evaluator_target_dict)
	print(data,"here")

	
	for agent in agents_sales_target:
		# total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,order_status='ORDER_CLOSED',created__range=(target_date_start,target_date_end)).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		
		if date_or_month == 'Month':
			total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=agent,created__range=(monthdate1,monthdate2),evaluation__quatation_status='APPROVED')
			total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=agent,created__range=(monthdate1,monthdate2))
		else:
			total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=agent,created__range=(target_date_start,target_date_end),evaluation__quatation_status='APPROVED')
			total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=agent,created__range=(target_date_start,target_date_end))

		total_sales_approved_amount = total_sales_approved.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		total_sales_approved_count = total_sales_approved.count()
		
		total_sales_submitted_amount = total_sales_submitted.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		total_sales_submitted_count = total_sales_submitted.count()

		if not total_sales_approved_amount:
			total_sales_approved_amount = 0.0
		if not total_sales_submitted_amount:
			total_sales_submitted_amount = 0.0

		print(total_sales_approved_amount,total_sales_submitted_amount,"evat")

		agent_target_dict = {
		"evaluator_id" : agent.id,
		"amount" : total_sales_approved_amount,
		"submitted":total_sales_submitted_amount,
		"approved_count":total_sales_approved_count,
		"submitted_count":total_sales_submitted_count
		}
		data.append(agent_target_dict)
	print(data,"here")


	for officer in bookingofficer_sales_target:
		# total_sales = Order.objects.filter(evaluation__evaluation_details__evaluator=evaluator,order_status='ORDER_CLOSED',created__range=(target_date_start,target_date_end)).aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		
		if date_or_month == 'Month':
			total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=officer,created__range=(monthdate1,monthdate2),evaluation__quatation_status='APPROVED')
			total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=officer,created__range=(monthdate1,monthdate2))
		else:
			total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=officer,created__range=(target_date_start,target_date_end),evaluation__quatation_status='APPROVED')
			total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=None,evaluation__call_attender=officer,created__range=(target_date_start,target_date_end))

		total_sales_approved_amount = total_sales_approved.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		total_sales_approved_count = total_sales_approved.count()
		
		total_sales_submitted_amount = total_sales_submitted.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
		total_sales_submitted_count = total_sales_submitted.count()

		if not total_sales_approved_amount:
			total_sales_approved_amount = 0.0
		if not total_sales_submitted_amount:
			total_sales_submitted_amount = 0.0

		print(total_sales_approved_amount,total_sales_submitted_amount,"evat")

		bookingofficer_target_dict = {
		"evaluator_id" : officer.id,
		"amount" : total_sales_approved_amount,
		"submitted":total_sales_submitted_amount,
		"approved_count":total_sales_approved_count,
		"submitted_count":total_sales_submitted_count
		}
		data.append(bookingofficer_target_dict)
	
	
	# if date_or_month == 'Month':
	# 	agent_total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=None,created__range=(monthdate1,monthdate2),evaluation__quatation_status='APPROVED')
	# 	agent_total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=None,created__range=(monthdate1,monthdate2))
	# else:
	# 	agent_total_sales_approved = Order.objects.filter(evaluation__evaluation_details__evaluator=None,created__range=(target_date_start,target_date_end),evaluation__quatation_status='APPROVED')
	# 	agent_total_sales_submitted = Order.objects.filter(evaluation__evaluation_details__evaluator=None,created__range=(target_date_start,target_date_end))
	
	# agent_sales_approved_amount = agent_total_sales_approved.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
	# agent_sales_approved_count = agent_total_sales_approved.count()
	
	# agent_sales_submitted_amount = agent_total_sales_submitted.aggregate(Sum('evaluation__total_cost')).get('evaluation__total_cost__sum', 0.0)
	# agent_sales_submitted_count = agent_total_sales_submitted.count()

	# if not agent_sales_approved_amount:
	# 	agent_sales_approved_amount = 0.0
	# if not agent_sales_submitted_amount:
	# 	agent_sales_submitted_amount = 0.0

	# print(agent_sales_approved_amount,agent_sales_submitted_amount,"aget")
		
	# agent_target_dict = {
	# 	"evaluator_id" : 0,
	# 	"amount" : agent_sales_approved_amount,
	# 	"submitted":agent_sales_submitted_amount,
	# 	"approved_count":agent_sales_approved_count,
	# 	"submitted_count":agent_sales_submitted_count
	# 	}
	# data.append(agent_target_dict)
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

class AdminPaymentEdit(IsAdmin,View):

	def get(self,request,enquiry_id,evaluation_id):
		enquiry_user    	  = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(id=enquiry_id)
		
		try:
			evaluation = Evaluation.objects.get(id=evaluation_id)
		except:
			evaluation = None		
	
		try:
			evaluation_details = EvaluationDetails.objects.filter(is_active=True,evaluation=evaluation)
		except:
			evaluation_details = None

		#allow submition	
		evaluation_details_count         = evaluation_details.count()
		evaluation_details_completed_count= evaluation_details.filter(status='EVALUATED').count()
		if evaluation_details_count==evaluation_details_completed_count:
			allow_submit = True
		else:
			allow_submit = False	

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=enquiry_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()				

		return render(request,'admin/payment/payment_edit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})	

	def post(self,request,enquiry_id,evaluation_id):
		
		payment_method 			= request.POST.get('payment_method')
		before_cleaning_amount	= float(request.POST.get('before_cleaning_amount')or 0)
		after_cleaning_amount	= float(request.POST.get('after_cleaning_amount')or 0)

		#for delete previous subscription
		evaluation      = Evaluation.objects.get(id=evaluation_id)
		order			= Order.objects.get(evaluation_id=evaluation_id)

		if evaluation.payment_method == 'POSTPAIDSUBSCRIPTION' or evaluation.payment_method == 'PREPAIDSUBSCRIPTION':
			OrderScheduler.objects.filter(order__evaluation__id=evaluation_id).update(payment_subscription=None)
			PaymentSubscriptionDetails.objects.filter(order__evaluation__id=evaluation_id).delete()

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)

		#update payment subscription if it is subscription
		if payment_method == 'POSTPAIDSUBSCRIPTION' or payment_method == 'PREPAIDSUBSCRIPTION':
			order           = Order.objects.get(evaluation_id=evaluation_id)
			order_schedules = OrderScheduler.objects.filter(order__evaluation__id=evaluation_id)

			#create subscription model
			cleaning_months = order_schedules.annotate(month=ExtractMonth('start_at'),year=ExtractYear('start_at')).values_list('month','year').distinct()
			count=0
			for month in cleaning_months:
				count += 1
				if len(cleaning_months) == count:
					amount = evaluation.total_cost-round((evaluation.total_cost/len(cleaning_months)*(count-1)),3)			
					subscription = PaymentSubscriptionDetails.objects.create(order=order,amount=amount,monthyear=(str(month[0])+'-'+str(month[1])) )
				else:
					subscription = PaymentSubscriptionDetails.objects.create(order=order,amount=round(evaluation.total_cost/len(cleaning_months),3),monthyear=(str(month[0])+'-'+str(month[1])) )			
	
				#update orderschedules
				for schedule in order_schedules:
					if payment_method == 'POSTPAIDSUBSCRIPTION':
						if schedule.start_at.date().month-1 == month[0]:
							schedule.payment_subscription = subscription
							schedule.save()
						elif schedule.start_at.date().month == 1 and schedule.start_at.date().year-1 == month[1] and month[0] == 12:	
							schedule.payment_subscription = subscription
							schedule.save()
					else:
						if schedule.start_at.date().month == month[0] and schedule.start_at.date().year == month[1]:
							schedule.payment_subscription = subscription
							schedule.save()
		
		messages.success(request,"Payment Policy Edited Succesfully")

		return redirect('bleach_admin:admin-client-orderdetails',order.id)

class LeaveScheduler(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/leavescheduler/leave.html',{})