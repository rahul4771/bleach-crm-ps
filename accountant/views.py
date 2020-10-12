from django.shortcuts import render,redirect
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsAccountant
# Create your views here.

import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField
from django.db.models.functions import Cast 
from django.db.models import Prefetch

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,CleaningMethod,ServiceType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory

import requests

class AccountantHome(IsAccountant,View):
	def get(self,request):
		#Payment Details
		search                  = request.GET.get('search')

		#sales amount
		try:
			invoices         = Order.objects.filter(is_active=True).order_by('-id')
		except:
			invoices         = None

		this_week_sales = invoices.filter(payment_status='COMPLETED',payment_completed_date__gte=timezone.now().date()-timedelta(6)).aggregate(total=Sum('amount_paid'))['total']
		last_week_sales = invoices.filter(payment_status='COMPLETED',payment_completed_date__gte=timezone.now().date()-timedelta(13),payment_completed_date__lte=timezone.now().date()-timedelta(6)).aggregate(total=Sum('amount_paid'))['total']		
		
		this_month_sales=invoices.filter(payment_status='COMPLETED',payment_completed_date__month=timezone.now().month,payment_completed_date__year=timezone.now().year).aggregate(total=Sum('amount_paid'))['total']
		last_month_sales=invoices.filter(payment_status='COMPLETED',payment_completed_date__month=((timezone.now().date()-relativedelta(months=1)).month),payment_completed_date__year=timezone.now().year).aggregate(total=Sum('amount_paid'))['total']	
		
		this_quarter_sales=invoices.filter(payment_status='COMPLETED',payment_completed_date__lte=timezone.now().date(),payment_completed_date__gte=(timezone.now().date()-relativedelta(months=3,day=1))).aggregate(total=Sum('amount_paid'))['total']
		last_quarter_sales=invoices.filter(payment_status='COMPLETED',payment_completed_date__lt=(timezone.now().date()-relativedelta(months=3,day=1)),payment_completed_date__gte=(timezone.now().date()-relativedelta(months=6,day=1))).aggregate(total=Sum('amount_paid'))['total']	
		
		#Pending Payments
		if search:
			try:
				pending_payments = invoices.filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD')&Q(evaluation__quatation_status='APPROVED'))).select_related('evaluation__customer').filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'))
			except:
				pending_payments = None
		else:
			try:
				pending_payments = invoices.filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD')&Q(evaluation__quatation_status='APPROVED'))).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'))
			except:
				pending_payments = None		

		#Pending Payment and Order Count	
		if pending_payments:
			total_pending_amount = pending_payments.aggregate(total=Sum(F('remining_amount')))['total']		
			total_pending_orders = pending_payments.count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0
		#PAGINATION PENDING PAYMENTS	
		page = request.GET.get('page',1) 
		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20
		

		page = request.GET.get('page',1) 
		paginator=Paginator(pending_payments,no_of_entries)
		try: 
			pending_payments=paginator.page(page) 
		except PageNotAnInteger:
			pending_payments=paginator.page(1)
		except EmptyPage:
			pending_payments = paginator.page(paginator.num_pages) 

		# Get the index of the current page
		index = pending_payments.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]	
		entry_per_page=(pending_payments.end_index())-(pending_payments.start_index())+1

		return render(request,'accountant/home/home.html',{"this_week_sales":this_week_sales,"last_week_sales":last_week_sales,"this_month_sales":this_month_sales,"last_month_sales":last_month_sales,"this_quarter_sales":this_quarter_sales,"last_quarter_sales":last_quarter_sales,"pending_payments":pending_payments,'total_pending_amount':total_pending_amount,"total_pending_orders":total_pending_orders,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"search_query":search,})

class ClientDetails(IsAccountant,View):
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

		new_clients_count    = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True,created__date__gte=timezone.now().date()-timedelta(30)).count()
		

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

		return render(request,'accountant/client/clients.html',{"client_details":client_details,"search_query":search,"new_clients_count":new_clients_count,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_customertype":fil_customertype,"fil_status":fil_status})		

		
class ClientOrders(IsAccountant,View):
	def get(self,request,client_id):

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None
	
		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'))
					
		#COUNT			
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()

		return render(request,"accountant/client/client-page.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,})

class ClientOrderDetails(IsAccountant,View):
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
					
				
		return render(request,"accountant/client/order-page.html",{"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count})



class OrderDetails(IsAccountant,View):
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

		return render(request,'accountant/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,})		


class PaymentDetails(IsAccountant,View):
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
		page = request.GET.get('page',1) 
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

		return render(request,'accountant/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,})

class PaymentLinkGeneration(View):
	baseURL = "https://apitest.myfatoorah.com"
	token = '7Fs7eBv21F5xAocdPvvJ-sCqEyNHq4cygJrQUFvFiWEexBUPs4AkeLQxH4pzsUrY3Rays7GVA6SojFCz2DMLXSJVqk8NG-plK-cZJetwWjgwLPub_9tQQohWLgJ0q2invJ5C5Imt2ket_-JAlBYLLcnqp_WmOfZkBEWuURsBVirpNQecvpedgeCx4VaFae4qWDI_uKRV1829KCBEH84u6LYUxh8W_BYqkzXJYt99OlHTXHegd91PLT-tawBwuIly46nwbAs5Nt7HFOozxkyPp8BW9URlQW1fE4R_40BXzEuVkzK3WAOdpR92IkV94K_rDZCPltGSvWXtqJbnCpUB6iUIn1V-Ki15FAwh_nsfSmt_NQZ3rQuvyQ9B3yLCQ1ZO_MGSYDYVO26dyXbElspKxQwuNRot9hi3FIbXylV3iN40-nCPH4YQzKjo5p_fuaKhvRh7H8oFjRXtPtLQQUIDxk-jMbOp7gXIsdz02DrCfQIihT4evZuWA6YShl6g8fnAqCy8qRBf_eLDnA9w-nBh4Bq53b1kdhnExz0CMyUjQ43UO3uhMkBomJTXbmfAAHP8dZZao6W8a34OktNQmPTbOHXrtxf6DS-oKOu3l79uX_ihbL8ELT40VjIW3MJeZ_-auCPOjpE3Ax4dzUkSDLCljitmzMagH2X8jN8-AYLl46KcfkBV'

	
	def get(self,request):

		#send link
		url 	= self.baseURL + "/v2/SendPayment"
		payload = "{\"CustomerName\": \"Ahmed\",\"NotificationOption\": \"ALL\",\"MobileCountryCode\": \"+965\"," \
              "\"CustomerMobile\": \"92249465\",\"CustomerEmail\": \"aramadan@myfatoorah.com\",\"InvoiceValue\": 100," \
              "\"DisplayCurrencyIso\": \"KWD\",\"CallBackUrl\": \"https://google.com\",\"ErrorUrl\": " \
              "\"https://google.com\",\"Language\": \"en\",\"CustomerReference\": \"ref 1\",\"CustomerCivilId\": " \
              "12345678,\"UserDefinedField\": \"Custom field\",\"ExpireDate\": \"\",\"CustomerAddress\": {\"Block\": " \
              "\"\",\"Street\": \"\",\"HouseBuildingNo\": \"\",\"Address\": \"\",\"AddressInstructions\": \"\"}," \
              "\"InvoiceItems\": [{\"ItemName\": \"Product 01\",\"Quantity\": 1,\"UnitPrice\": 100}]} "
		headers = {'Content-Type': "application/json", 'Authorization': "Bearer " + self.token}
		response = requests.request("POST", url, data=payload, headers=headers)

		print("send link response")
		print(response)
		print(response.json())

		#initiate execute payment

		####### Initiate Payment ######
		url 		= self.baseURL + "/v2/InitiatePayment"
		payload 	= "{\"InvoiceAmount\":100,\"CurrencyIso\":\"KWD\"}"
		headers 	= {'Content-Type': "application/json", 'Authorization': "Bearer " + self.token}
		response 	= requests.request("POST", url, data=payload, headers=headers)
		
		print("Initiate Payment Response")
		print(response)
		print(response.json())

		####### Execute Payment ######
		url 	= self.baseURL + "/v2/ExecutePayment"
		payload = "{\"CustomerName\": \"Ahmed\",\"MobileCountryCode\": \"+965\"," \
		              "\"CustomerMobile\": \"92249465\",\"CustomerEmail\": \"aramadan@myfatoorah.com\",\"InvoiceValue\": 100," \
		              "\"DisplayCurrencyIso\": \"KWD\",\"CallBackUrl\": \"https://google.com\",\"ErrorUrl\": " \
		              "\"https://google.com\",\"Language\": \"en\",\"CustomerReference\": \"ref 1\",\"CustomerCivilId\": " \
		              "12345678,\"UserDefinedField\": \"Custom field\",\"ExpireDate\": \"\",\"CustomerAddress\": {\"Block\": " \
		              "\"\",\"Street\": \"\",\"HouseBuildingNo\": \"\",\"Address\": \"\",\"AddressInstructions\": \"\"}," \
		              "\"InvoiceItems\": [{\"ItemName\": \"Product 01\",\"Quantity\": 1,\"UnitPrice\": 100}]}"
		headers = {'Content-Type': "application/json", 'Authorization': "Bearer " + self.token}
		response = requests.request("POST", url, data=payload, headers=headers)
		
		print("Execute Payment Response")
		print(response)
		print(response.json())


		####### Direct Payment ######
		
		#initialize payment
		url     = self.baseURL + "/v2/ExecutePayment"
		payload = "{\"PaymentMethodId\":2,\"CustomerName\": \"Ahmed\",\"MobileCountryCode\": \"+965\"," \
	              "\"CustomerMobile\": \"92249465\",\"CustomerEmail\": \"aramadan@myfatoorah.com\",\"InvoiceValue\": 100," \
	              "\"DisplayCurrencyIso\": \"KWD\",\"CallBackUrl\": \"https://google.com\",\"ErrorUrl\": " \
	              "\"https://google.com\",\"Language\": \"en\",\"CustomerReference\": \"ref 1\",\"CustomerCivilId\": " \
	              "12345678,\"UserDefinedField\": \"Custom field\",\"ExpireDate\": \"\",\"CustomerAddress\": {\"Block\": " \
	              "\"\",\"Street\": \"\",\"HouseBuildingNo\": \"\",\"Address\": \"\",\"AddressInstructions\": \"\"}," \
	              "\"InvoiceItems\": [{\"ItemName\": \"Product 01\",\"Quantity\": 1,\"UnitPrice\": 100}]}"

		headers = {'Content-Type': "application/json", 'Authorization': "Bearer " + self.token}
		response = requests.request("POST", url, data=payload, headers=headers)
		print("Initiate direct Payment Response")
		print(response)
		print(response.json())	    


		#direct payment
		data        = response.json()['Data']
		payment_url = data['PaymentURL']

		print("PaymentURL  Response:\n" + payment_url)
	    # after getting the payment url call it as a post API and pass card info to it
	    # if you saved the card info before you can pass the token for the api

		payload = "{\"paymentType\": \"card\",\"card\": {\"Number\":\"5123450000000008\",\"expiryMonth\":\"05\","\
		          "\"expiryYear\":\"21\",\"securityCode\":\"100\"},\"saveToken\": false} "
		headers = {'Content-Type': "application/json", 'Authorization': "Bearer " + self.token}
		response = requests.request("POST", payment_url, data=payload, headers=headers)

		print("Direct Payment Response")
		print(response)


		return redirect('accountant:accountantdash-board')