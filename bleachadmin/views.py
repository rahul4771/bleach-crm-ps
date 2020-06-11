from django.shortcuts import render
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsAdmin
from dateutil.relativedelta import relativedelta

import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField
from django.db.models.functions import Cast 
from django.db.models import Prefetch

from user.models import UserProfile,Address
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember
from accountant.models import Invoice


# Create your views here.

class AdminHome(IsAdmin,View):
	def get(self,request):
		
		#Enquiry Details count
		try:
			enquiry = EvaluationDetails.objects.filter(is_active=True)
		except:
			enquiry	= None

		today_enquiry_count = enquiry.filter(proposed_time__date=timezone.now().date()).count()
		week_enquiry_count  = enquiry.filter(proposed_time__date__gte=timezone.now().date()-timedelta(6)).count()	

		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(start_at__date=timezone.now().date()).count() 
		week_cleaning_job_count  = cleaning_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		
		
		#Followup jobs count
		try:
			follow_up_job    = FollowUpTeam.objects.filter(is_active=True)
		except:
			follow_up_job	 = None

		today_follow_up_job_count = follow_up_job.filter(start_at__date=timezone.now().date()).count() 
		week_follow_up_job_count  = follow_up_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		

		#Feedback Staring count
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

		return render(request,'admin/home/home.html',{'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'today_average_feedback':today_average_feedback,'week_average_feedback':week_average_feedback,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'schedule_date':schedule_date,})

class ClientDetails(IsAdmin,View):
	def get(self,request):

		search                  = request.GET.get('search')

		if search:
			try:
				client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True,name__icontains=search).prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area'),to_attr='customer_address'),Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True,order_status='ORDER_CLOSED'),to_attr='order_evaluation')),to_attr='customer_evaluations'))
			except:
				client_details = None
		else:
			client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True).prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area'),to_attr='customer_address'),Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True,order_status='ORDER_CLOSED'),to_attr='order_evaluation')),to_attr='customer_evaluations'))			

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

		active_clients_count = orders.filter(~Q(order_status='ORDER_CLOSED')).values_list('evaluation__customer').distinct().count()	
		new_clients_count    = orders.filter(evaluation__created__date__gte=timezone.now().date()-timedelta(30),evaluation__customer__created__date__gte=timezone.now().date()-timedelta(30),).values_list('evaluation__customer').distinct().count()
		
		#PAGINATION CLIENTS		
		page = request.GET.get('page',1) 
		paginator=Paginator(client_details,10)
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


		return render(request,'admin/client/clients.html',{"client_details":client_details,"search_query":search,"active_clients_count":active_clients_count,"new_clients_count":new_clients_count,"page_range":page_range,"entry_per_page":entry_per_page})		

class TicketDetails(IsAdmin,View):
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
				tickets 	             = FollowUp.objects.filter(is_active=True).select_related('investigation__order_schedule__order__evaluation__customer').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))
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

		return render(request,'admin/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})		

class OrderDetails(IsAdmin,View):
	def get(self,request):
		
		#Evaluation Details
		search                  = request.GET.get('search')
		
		if search:
			try:
				evaluations = Evaluation.objects.select_related('customer').filter(is_active=True,customer__name__icontains=search).prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('cleaning_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))
			except:
				evaluations = None 
		 
		else:
			try:
				evaluations = Evaluation.objects.filter(is_active=True).select_related('customer').prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('cleaning_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))
			except:
				evaluations = None 
			
		approved_orders_count = evaluations.filter(Q(quatation_status='APPROVED')).count()
		pending_orders_count  =	evaluations.filter(Q(Q(quatation_status='ASK_FOR_DISCOUNT')|Q(quatation_status='PENDING'))).count()

		#PAGINATION ORDERS		
		page = request.GET.get('page',1) 
		paginator=Paginator(evaluations,10)
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

		return render(request,'admin/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})		


class FeedbackDetails(IsAdmin,View):
	def get(self,request):
		
		search                  = request.GET.get('search')

		#Feedback Staring count
		try:
			feedbacks                 = FeedBack.objects.filter(is_active=True)
		except:
			feedbacks				  = None

		average_feedback    		  = feedbacks.aggregate(Avg('rating'))['rating__avg']
		total_feedbacks               = feedbacks.count()
		starring_percentages          = feedbacks.values('rating').annotate(percentage=Cast(Count('rating')/float(total_feedbacks)*100,FloatField())).order_by('rating')
		
		#order wise feedback
		if search:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True,evaluation__customer__name__icontains=search).prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('cleaning_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField()))		
			except:
				order_wise_feedbacks = None

		else:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True).prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('cleaning_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField()))						
			except:	
				order_wise_feedbacks = None

		#PAGINATION FEEDBACKS		
		page = request.GET.get('page',1) 
		paginator=Paginator(order_wise_feedbacks,10)
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

		return render(request,'admin/feedback/feedbacks.html',{"feedbacks":feedbacks,"average_feedback":average_feedback,"total_feedbacks":total_feedbacks,"starring_percentages":starring_percentages,"order_wise_feedbacks":order_wise_feedbacks,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})

class ResourceManagement(IsAdmin,View):
	def get(self,request):
		
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

		return render(request,'admin/resource/resources.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams})

class PaymentDetails(IsAdmin,View):
	def get(self,request):
		
		#Evaluation Details
		search                  = request.GET.get('search')
		
		#sales amount
		if search:
			try:
				invoices         = Invoice.objects.filter(is_active=True).order_by('-id').select_related('order__evaluation__customer').filter(order__evaluation__customer__name__icontains=search).prefetch_related(Prefetch('order__evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area'),to_attr='invoice_evaluation_details'))
			except:
				invoices         = None
		else:
			try:
				invoices         = Invoice.objects.filter(is_active=True).order_by('-id').select_related('order__evaluation__customer').prefetch_related(Prefetch('order__evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area'),to_attr='invoice_evaluation_details'))
			except:
				invoices         = None
				
		#Pending Payments
		try:
			pending_payments = invoices.filter(Q(Q(status='PENDING')|Q(status='ON_HOLD')))
		except:
			pending_payments = None

		#Pending Payment and Order Count	
		if pending_payments: 
			total_pending_amount = pending_payments.aggregate(total=Sum(F('total_amount')-F('amount_paid')))['total']		
			total_pending_orders = pending_payments.count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0

		#PAGINATION INVOICE		
		page = request.GET.get('page',1) 
		paginator=Paginator(invoices,10)
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

		return render(request,'admin/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})		
