from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.views import View
from django.forms import formset_factory,modelformset_factory
from django.http import HttpResponse,JsonResponse

from django.conf import settings
from bleach_crm_ps.permissions import IsAgent,IsAuthenticated
from bleach_crm_ps.utils import get_error
import glob
import os
from os.path import splitext
import requests

import pandas as pd
from googletrans import Translator

import random
import string
import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast,TruncDate,ExtractMonth,ExtractYear,Concat
from django.db.models import Prefetch
from django.contrib import messages

from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking
from agent.forms import UserProfileForm,AddressForm
from evaluator.forms import EvaluationDetailsForm,QuatationServiceForm
from order.forms import InvestigationForm

from django.db.models import Count

from dateutil.relativedelta import relativedelta


from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string

#restframe work 
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK

from agent.serializers import CleaningScheduleSerializer,FollowupScheduleSerializer,UserProfileShowSerializer

# Create your views here.


class OrderDetails(IsAuthenticated,View):
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
			fil_evaluator	   		  = int(request.GET.get('evaluator'))
		except:
			fil_evaluator 			  = None

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

		return render(request,'common/order/orders.html',{"evaluations":evaluations,"evaluators":evaluators,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy,"fil_evaluator":fil_evaluator})		


class ClientDetails(IsAuthenticated,View):
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

		return render(request,"common/client/clients.html",{"client_details":client_details,"search_query":search,"new_clients_count":new_clients_count,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_customertype":fil_customertype,"fil_status":fil_status})


class ClientOrders(IsAuthenticated,View):
	def get(self,request,client_id):

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'))

		#COUNT
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()

		return render(request,"common/client/client-page.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,})

class TicketDetails(IsAuthenticated,View):
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

		return render(request,"common/ticket/tickets.html",{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})

class TicketAdvanced(IsAuthenticated,View):
	def get(self,request,client_id,followup_id):

		#client info
		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		#followup info

		followup_details = FollowUp.objects.select_related('investigation__investigator','investigation__order','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate','investigation__order_schedule__order_scheduler_book').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_media',queryset=FollowUpTeamMedia.objects.filter(is_active=True),to_attr='followupmedias'),Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules'),Prefetch('investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('follow_up_of_section',queryset=FollowUpSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesectionsfollowup',queryset=FollowUpSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='followupsections'),Prefetch('investigation__buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True).prefetch_related(Prefetch('buybackpromocodegiftdetails',queryset=BuybackPromocodeGiftDetails.objects.filter(is_active=True),to_attr='buybackpromogiftdetails'),Prefetch('buybackpromocodegift_media',queryset=BuybackPromocodeGiftDetailsMedia.objects.filter(is_active=True),to_attr='buybackpromogiftmedias')),to_attr='buybackpromogifts'),Prefetch('investigation__paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True).prefetch_related(Prefetch('paybackdiscount_details',queryset=PaybackDiscountDetails.objects.filter(is_active=True),to_attr='paybackdiscountdetails'),Prefetch('paybackdiscount_media',queryset=PaybackDiscountDetailsMedia.objects.filter(is_active=True),to_attr='paybackdiscountmedias')),to_attr='paybackdiscounts'),Prefetch('investigation__reporting_investigation',queryset=Reporting.objects.filter(is_active=True).prefetch_related(Prefetch('reporting_media',queryset=ReportingMedia.objects.filter(is_active=True),to_attr='reporting_medias')),to_attr='reports')).annotate(followup_schedule_count=Count('follow_up_of_scheduler'),completed_followup_count=Sum(Case(When(follow_up_of_scheduler__work_status='FOLLOW_UP_CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())) ).get(is_active=True,id=followup_id)



		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=client_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		return render(request,'common/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})

	
class CustomerBookingsList(IsAuthenticated,View):
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

		return render(request,'common/customer-bookings/bookings.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy})


class PaymentDetails(IsAuthenticated,View):
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
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(~Q(order_status='ORDER_CANCELLED')).filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         = None
		else:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(~Q(order_status='ORDER_CANCELLED')).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
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
			for payment in pending_payments:
				if payment.evaluation.payment_method in ['PREPAID','POSTPAID','BREAKDOWN']:
					total_pending_amount += payment.remining_amount

				if payment.evaluation.payment_method == 'SUBSCRIPTION':
					total_pending_amount += payment.subscription_topay		

			total_pending_orders = pending_payments.count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0

		#remove object in postpaid if not last cleaning fulfilled	
		#remove if subscription to pay date
		if pending_payments:
			for payment in pending_payments:
				if payment.evaluation.payment_method == 'POSTPAID' and payment.cleaning_count :
					very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
					if very_latest_cleaning.work_status != 'CLEANING_FULFILLED':
						pending_payments = pending_payments.exclude(id=payment.id)
				if payment.evaluation.payment_method == 'SUBSCRIPTION' and not payment.subscription_topay_date:
					pending_payments = pending_payments.exclude(id=payment.id)	

		#to find days
		if pending_payments:
			for payment in pending_payments:
				if payment.evaluation.payment_method == 'PREPAID' and payment.orderschedules:
					very_old_cleaning   = payment.orderschedules[0]
					payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
				elif payment.evaluation.payment_method == 'POSTPAID' and payment.orderschedules:
					very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
					payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	
				elif payment.evaluation.payment_method == 'BREAKDOWN' and payment.orderschedules:
				
					very_old_cleaning   = payment.orderschedules[0]
					very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
					payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
					payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	

					#to check last cleaning completed for break down after payment
					if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
						payment.last_completed = True	

				elif payment.evaluation.payment_method == 'SUBSCRIPTION':				
					payment.delaydays= (timezone.now()-payment.subscription_topay_date).days	

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
				case2       = Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) )
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



		return render(request,'common/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"service_types":service_types,"fil_payment_policy":fil_payment_policy,"fil_payment_status":fil_payment_status,"fil_order_status":fil_order_status,"pending_payments":pending_payments})


class ActiveSubscriptions(IsAuthenticated,View):
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

		return render(request,'common/subscription/active_subscriptions.html',{"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"subscriptions":subscriptions})

	def post(self,request):
		order_id            = request.POST.get('order')
		subscription_topay  = float(request.POST.get('subscription_topay'))
		invoice_type  		= request.POST.get('invoice_type')
		print(invoice_type,"ivtp")

		Order.objects.filter(id=order_id).update(subscription_topay=subscription_topay,subscription_topay_date=timezone.now())

		order = Order.objects.filter(id=order_id).first()

		evaluaation = order.evaluation

		if evaluaation.customer.is_sms == True and invoice_type == "invoice" :
			print("sms")

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

		return redirect('common_items:active-subscriptions')


class ClientOrderDetails(IsAuthenticated,View):
	def get(self,request,order_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True),to_attr='paybackdiscounts'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True),to_attr='buybackpromocodegift'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)

		invoice = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') )).get(is_active=True,id=order_id)
		
		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=order.evaluation.customer_id)
		except:
			client_details = None

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=order.evaluation.customer_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		#average feedbacks
		average_feedback 	= order.feed_backs_order.aggregate(Avg('rating'))['rating__avg']

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


		return render(request,"common/client/order-page.html",{"order":order,"invoice":invoice,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"average_feedback":average_feedback,})

	def post(self,request,order_id):
		action = request.POST.get('action_type')

		if action == 'cancell_order':
			evaluation_id = request.POST.get('evaluation')

			#cancell order
			order 				= Order.objects.select_related('evaluation__customer').get(evaluation__id=evaluation_id)
			order.order_status  = 'CANCEL_IN_PROGRESS'
			order.cancell_requester = request.user
			order.save()

			#status change of scheduler
			schedules = OrderScheduler.objects.filter(order=order)
					
			for schedule in schedules:
				if not schedule.work_status == 'CLEANING_FULFILLED':
					schedule.work_status = 'CLEANING_CANCELLED'
					schedule.save()

			#delete assigned cleaning team and members
			CleaningTeam.objects.select_related('order_scheduler__order').filter(order_scheduler__order=order).delete() 

			#Email Send
			salesadmin_list = UserProfile.objects.filter(is_active=True,user_type='SALESADMIN').values_list('email',flat=True)
			msg_html = render_to_string('email/cancellation_request.html',{'order':order})
			msg      = EmailMultiAlternatives('Order Cancellation', '', 'notification@bleach-kw.com', salesadmin_list)
			msg.attach_alternative(msg_html, "text/html")
			msg.send(fail_silently=False)
			
			messages.success(request,"Cancel Request Proceeded to Admin successfully !")
		
		
		if action == 'send_invoice':
			subscription_topay  = float(request.POST.get('subscription_topay'))

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

		
		return redirect('common_items:client-orderdetails',order_id)


class MakeQuatationPhase1Edit(IsAuthenticated,View):	

	def get(self,request,enquiry_id,evaluation_id):
		enquiry_user    	  = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(id=enquiry_id)
		
		try:
			evaluation = Evaluation.objects.get(id=evaluation_id)
		except:
			evaluation = None		
	
		try:
			evaluation_details = EvaluationDetails.objects.filter(is_active=True,evaluation=evaluation).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True,cleaning_policy='SUBSCRIPTION'),to_attr='evaluationbooks'))
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

		return render(request,'common/order/phase1quatationedit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})	

	def post(self,request,enquiry_id,evaluation_id):
		
		payment_method 			= request.POST.get('payment_method')
		before_cleaning_amount	= float(request.POST.get('before_cleaning_amount')or 0)
		after_cleaning_amount	= float(request.POST.get('after_cleaning_amount')or 0)

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,quatation_status='PENDING',before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)


		#sms integration
		evaluation = Evaluation.objects.prefetch_related(Prefetch('evaluation_details',EvaluationDetails.objects.filter(is_active=True).select_related('address'),to_attr='evaluation_address')).filter(id=evaluation_id,is_active=True).get(id=evaluation_id,is_active=True)	
		evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
		if evaluationdetails.address.floor == None:
			address_floor = '-'
		else:
			address_floor = evaluationdetails.address.floor

		if evaluationdetails.address.avenue == None:
			address_avenue = '-'
		else:
			address_avenue = evaluationdetails.address.avenue

		evaluationbook = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).first()
		
		messages.success(request,"Quatation Edited Succesfully")

		if evaluation.customer.is_sms == True:

			url = "https://smsapi.future-club.com/fccsms.aspx"

			if evaluation.payment_method == 'SUBSCRIPTION':
				smsurl = "https://my.bleachkw.com/customer/subscription/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+""
			else:
				smsurl = "https://my.bleachkw.com/customer/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+""

			if evaluation.customer.sms_preference == 'ENGLISH':

				message = "Dear Customer, Please find the Revised Quotation against the order number "+str(evaluation.evaluation_id)+"  here "+smsurl+" . Order Number : "+ str(evaluation.evaluation_id) +". Service Type(s) : "+ evaluationbook.service_type.name +", Address(s) : "+evaluationdetails.address.apartment+","+address_floor+","+evaluationdetails.address.street+","+evaluationdetails.address.building+","+address_avenue+","+evaluationdetails.address.block+","+evaluationdetails.address.area.name+","+evaluationdetails.address.governorate.name+", Cost : "+ str(evaluation.total_cost) +", Due Date : "+ str(evaluation.quatation_expiry_date) +". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

			else:
				message = "عزيزنا العميل نرجوا الاطلاع على عرض السعر المعدّل للطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط "+smsurl+" .رقم الطلب: "+ str(evaluation.evaluation_id) +"الخدمة: "+ evaluationbook.service_type.name +"العنوان: "+evaluationdetails.address.apartment+","+address_floor+","+evaluationdetails.address.street+","+evaluationdetails.address.building+","+address_avenue+","+evaluationdetails.address.block+","+evaluationdetails.address.area.name+","+evaluationdetails.address.governorate.name+"السعر: "+ str(evaluation.total_cost) +" KDتاريخ الخدمة: "+ str(evaluation.quatation_expiry_date) +"لأي استفسارات يمكنكم التواصل معنا على . 9651882707+  شكراً لاختياركم بليتش لخدمات التنظيف"
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

			headers = {
				'cache-control': "no-cache"
			}

			response = requests.request("GET", url, headers=headers, params=querystring)

			print(response.text,"respo")
		else:
			pass

		return redirect('common_items:orders')


class DailySales(IsAuthenticated, View):
	def get(self,request):
		# for monthly tab and daily sales tab
		today = datetime.now()
		todate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
		full_month_name = today.strftime("%B")
		
		monthdate1 = today.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = today.replace(day=1,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)-relativedelta(days=1)
		daterange  = pd.date_range(monthdate1, monthdate2)
		print(daterange,"dr")

		monthly_sales = 0
		daily_sales = 0

		for date in daterange:
			start_date_day = date
			end_date_day   = date+timedelta(1)

			print(date.strftime("%A"),"dt")

			cleaning_amount = 0

			if date < todate:
				print(date,"dtER")
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount').order_by('end_at')
			else:
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount').order_by('end_at')

			found = set()
			schedules_list = []

			for schedule in orderschedules:
				schedules_list.append(schedule)


			print(schedules_list,"listss")

			for schedule in schedules_list:

				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()

				order_amount = schedule[1]

				cleaning_amount += float(order_amount/schedule_count)

				if schedule[6] != None:
					cleaning_amount -= float(schedule[6]/schedule_count)
				if schedule[7] != None:
					cleaning_amount -= float(schedule[7]/schedule_count)
				if schedule[8] != None:
					cleaning_amount += float(schedule[8]/schedule_count)


			todate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

			if date == todate:
		
				daily_sales = round(cleaning_amount)

			monthly_sales += cleaning_amount

		monthly_sales = round(monthly_sales)

		return render(request,'common/dailysales/daily-sales.html',{"dailysales":daily_sales,"monthlysales":monthly_sales,"month_name":full_month_name})


class ResourceManagement(IsAuthenticated,View):
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
		
		return render(request,'common/resource/resource_management.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,"staffs":staffs,"fil_staff":fil_staff,"fil_endingtime":fil_endingtime,"fil_startingtime":fil_startingtime,'service_type':service_type})


def ResourcesToggle(request):
	data = dict()
	workers2 = []
	workers_list = []
	newlist = []
	
	#staff type
	staff_type = request.GET.get('staff_type',None)
	
	#date range for a month from month/year 
	month_year = request.GET.get('month_year',None)
	month,year = month_year.split("/")
	monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
	monthdate2 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
	daterange  = pd.date_range(monthdate1, monthdate2)
	
	#search
	search = request.GET.get('search',None)

	if search:
		workers = UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))&Q(name__icontains=search))#.prefetch_related( Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__order_scheduler__order__feed_backs_order').filter(is_active=True,team__check_out__isnull=False),to_attr='cleaningmembers'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__followup_scheduler__follow_up__investigation__order').filter(is_active=True,team__check_out__isnull=False),to_attr='followupmembers'))
	else:
		workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER')))#.prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__order_scheduler__order__feed_backs_order').filter(is_active=True,team__check_out__isnull=False),to_attr='cleaningmembers'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__followup_scheduler__follow_up__investigation__order').filter(is_active=True,team__check_out__isnull=False),to_attr='followupmembers'))

	if staff_type:
		workers =  workers.filter(user_type=staff_type)
	

	#append worker deatil to workers_list as dictionary
	for worker in workers:
		workers_list.append({
			"id":worker.id,
			"worker":worker.name,
			"worker_photo":worker.profile_image,
			"rating":0.0,
			"worked_days":0,
			"total_hours":0,
		})


	daterange = pd.date_range(monthdate1, monthdate2)

	for d in workers_list:
		cleanings = CleaningTeamMember.objects.filter(is_active=True,member_id=d['id']).filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__order_scheduler__order__feed_backs_order').values('team__order_scheduler__order__feed_backs_order__rating','member__id','member__profile_image','start_at','end_at')
		followups = FollowUpTeamMember.objects.filter(is_active=True,member_id=d['id']).filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__followup_scheduler__follow_up__investigation__order__feed_backs_order').values('team__followup_scheduler__follow_up__investigation__order__feed_backs_order__rating','member__id','member__profile_image','start_at','end_at')		

		#to find worked days
		for date in daterange:
			start_date_day = date
			end_date_day   = date+timedelta(1)
			if cleanings.filter(start_at__range=(start_date_day,end_date_day),end_at__range=(start_date_day,end_date_day)) or followups.filter(start_at__range=(start_date_day,end_date_day),end_at__range=(start_date_day,end_date_day)):
				d['worked_days'] = d['worked_days']+1
		
		cleaning_hours = cleanings.annotate(duration = ExpressionWrapper(F('end_at') - F('start_at'), output_field=DurationField())).aggregate(total_duration=Sum('duration'))
		followup_hours = followups.annotate(duration = ExpressionWrapper(F('start_at') - F('start_at'), output_field=DurationField())).aggregate(total_duration=Sum('duration'))

		cleaning_rating = cleanings.aggregate(total_rating=Sum('team__order_scheduler__order__feed_backs_order__rating')/Count('team__order_scheduler__order__feed_backs_order__rating'))

		d['total_hours'] = (cleaning_hours['total_duration']or timedelta()) + (followup_hours['total_duration']or timedelta())
		d['rating']      = cleaning_rating['total_rating']or 0
		
		#to convert duration to hours
		d['total_hours'] = d['total_hours'].days*24+d['total_hours'].seconds/3600
	
				
	data['html_workers_list'] = render_to_string('agent/resource/resource-month.html', {"workers_details_month":workers_list})
	return JsonResponse(data)

def ResourcesFilter(request):
	staff_type = request.GET.get('')
	try:
	 	workers =  UserProfile.objects.filter(is_active=True).filter(user_type=staff_type)
	except:
		workers =  None


	return JsonResponse()


class FeedbackDetails(IsAuthenticated,View):
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

		return render(request,'common/feedback/feedbacks.html',{"total_feedbacks":total_feedbacks,"order_wise_feedbacks":order_wise_feedbacks,"full_order_wise_feedbacks":full_order_wise_feedbacks,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_minimumstarring":fil_minimumstarring,"fil_service_type":fil_service_type,})

class FeedbackAdvanced(IsAuthenticated,View):
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

		return render(request,'common/feedback/feedback-page.html',{"order":order,"client_details":client_details,"feedback_details":feedback_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"other_feedbacks":other_feedbacks,"average_feedback":average_feedback,})

class LeaveScheduler(IsAuthenticated,View):
	def get(self,request):
		return render(request,'common/leavescheduler/leave.html',{})

class ResourceManagementTest(IsAuthenticated,View):
	def get(self,request):

		workers_date       = timezone.now().date()
		workers            =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).prefetch_related('leave_staff').annotate(leave=Sum( Case( When( leave_staff__leave_date=workers_date,then=1),default=0,output_field=IntegerField())) ).prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=workers_date)|Q(end_at__date=workers_date)) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation','team__order_scheduler__order_scheduler_book'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter(Q( Q(is_active=True)&Q(Q(start_at__date=workers_date)|Q(end_at__date=workers_date)) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details'))
		print(workers,"workers")

		return render(request,'common/resource/resource-new.html',{"workers":workers,"workers_date":workers_date})