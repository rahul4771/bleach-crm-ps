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

from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import Promocode,OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking
from agent.forms import UserProfileForm,AddressForm
from evaluator.forms import EvaluationDetailsForm,QuatationServiceForm
from order.forms import InvestigationForm,PromocodeForm
from bleachadmin.models import ServiceProductivity,ServicePriceRange,Settings
from bleachadmin.forms import ServicePriceRangeForm,DiscountSettingsForm
from senior_team_leader.forms import CleaningTeamAssignForm,FollowupTeamAssignForm
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

#Username Random Generation
def generate_random_username(size=10, chars=string.ascii_uppercase + string.digits):

	username = ''.join(random.choice(chars) for n in range(size))


	try:
		UserProfile.objects.get(username=username)
		return generate_random_username(size=10, chars=string.ascii_uppercase + string.digits)
	except UserProfile.DoesNotExist:
		return username


class NewRaiseTicket(IsAuthenticated,View):
    def get(self,request):
        return render(request,'common/ticket/raiseticket.html',{})

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

		tab = request.GET.get('tab')
		
		if not tab:
			tab = 'orders'

		#Evaluation Details
		search                  = request.GET.get('search')
		#for order filtering
		status = request.GET.get('status')
		
		if search:
			evaluations = Evaluation.objects.filter(is_active=True).filter(Q(estimated_cost__gt=0)|Q(quatation_status__isnull=False)).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(customer__mobile_number__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCEL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
			# bookings = Evaluation.objects.filter(is_active=True,booking_evaluation__is_active=True).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(customer__mobile_number__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCEL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
		else:
			evaluations = Evaluation.objects.filter(is_active=True).filter(Q(estimated_cost__gt=0)|Q(quatation_status__isnull=False)).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCEL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
			# bookings = Evaluation.objects.filter(is_active=True,booking_evaluation__is_active=True).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),order_cancelled_count=Count(Case(When( evaluation_order__order_status='ORDER_CANCELLED',then=1),output_field=IntegerField())),order_cancellinprogress_count=Count(Case(When( evaluation_order__order_status='CANCEL_IN_PROGRESS',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
			

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
			# bookings = bookings.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_book_count=Count(Case(When( Q(count_evaluation_book_prefetch_filter & count_customer_address_prefetch_filter),then=1),output_field=IntegerField()))).filter(address_book_count__gt=0)		 		 
			print("both")
		elif evaluation_book_prefetch_filter and not customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(book_count=Count(Case(When( count_evaluation_book_prefetch_filter,then=1),output_field=IntegerField()))).filter(book_count__gt=0)
			# bookings = bookings.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(book_count=Count(Case(When( count_evaluation_book_prefetch_filter,then=1),output_field=IntegerField()))).filter(book_count__gt=0)
			print("book only")
		elif not evaluation_book_prefetch_filter and customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)
			# bookings = bookings.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)
			print("address only") 
		else:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))
			# bookings = bookings.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))				
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

		bookings = evaluations.filter(booking_evaluation__is_active=True)
			

		#PAGINATION ORDERS		
		no_of_entries = request.GET.get('no_of_entries')		
		if not no_of_entries:
			no_of_entries = 20

		page1 = request.GET.get('page1',1) 
		paginator1=Paginator(evaluations,no_of_entries)
		try: 
			evaluations=paginator1.page(page1) 
		except PageNotAnInteger:
			evaluations=paginator1.page(1)
		except EmptyPage:
			evaluations = paginator1.page(paginator1.num_pages) 

		page2 = request.GET.get('page2',1) 
		paginator2=Paginator(bookings,no_of_entries)
		try: 
			bookings=paginator2.page(page2) 
		except PageNotAnInteger:
			bookings=paginator2.page(1)
		except EmptyPage:
			bookings = paginator2.page(paginator2.num_pages)

		# Get the index of the current page
		index1 = evaluations.number - 1  # edited to something easier without index
		index2 = bookings.number - 1
		# This value is maximum index of your pages, so the last page - 1
		max_index1 = len(paginator1.page_range)
		max_index2 = len(paginator2.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index1 = index1 - 3 if index1 >= 3 else 0
		end_index1 = index1 + 3 if index1 <= max_index1 - 3 else max_index1

		start_index2 = index2 - 3 if index2 >= 3 else 0
		end_index2 = index2 + 3 if index2 <= max_index2 - 3 else max_index2
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range1 = list(paginator1.page_range)[start_index1:end_index1]	
		page_range2 = list(paginator2.page_range)[start_index2:end_index2]	

		entry_per_page1=(evaluations.end_index())-(evaluations.start_index())+1
		entry_per_page2=(bookings.end_index())-(bookings.start_index())+1

		return render(request,'common/order/orders.html',{"bookings":bookings,"tab":tab,"evaluations":evaluations,"evaluators":evaluators,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range1":page_range1,"page_range2":page_range2,"entry_per_page1":entry_per_page1,"entry_per_page2":entry_per_page2,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy,"fil_evaluator":fil_evaluator})		


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

		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'), avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField()))

		for order in orders:
			tickets = FollowUp.objects.filter(is_active=True,investigation__order_schedule__order__id=order.id).count()
			order.total_tickets = tickets
			print(order.total_tickets,"tots")

		#COUNT
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		completed_orders_count = orders.filter(order_status='ORDER_CLOSED').count()

		active_followups = FollowUp.objects.filter(is_active=True,investigation__order_schedule__order__evaluation__customer_id=client_id).filter(Q(status='TICKET_RISED')|Q(status='FOLLOWUP_IN_PROGRESS')).count()
		closed_followups = FollowUp.objects.filter(is_active=True,investigation__order_schedule__order__evaluation__customer_id=client_id,status='FOLLOWUP_CLOSED').count()

		total_paid = orders.aggregate(paid=Sum('amount_paid'))['paid']
		total_balance = orders.aggregate(balance=Sum('remining_amount'))['balance']

		return render(request,"common/client/client-page-test.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,"completed_orders_count":completed_orders_count,"active_followups":active_followups,"closed_followups":closed_followups,"total_paid":total_paid,"total_balance":total_balance})

	def post(self,request,client_id):

		enquiry_user    = UserProfile.objects.get(id=client_id)

		action_mode 	= request.POST.get('action_type')

		print(enquiry_user,action_mode,"llp")

		if action_mode == 'edit_customer':
			
			enquiry_form    = UserProfileForm(request.POST,request.FILES or None,instance=enquiry_user)

			if enquiry_form.is_valid():
				
				enquiry_form_save            = enquiry_form.save(commit=False)

				#To Save Contact Platform
				is_sms 			 = request.POST.get('is_sms')
				is_email 			 = request.POST.get('is_email')
				is_whatsapp 			 = request.POST.get('is_whatsapp')
				print(is_sms,is_email,"pfp")

				if is_whatsapp == 'WHATSAPP':
					enquiry_form_save.is_whatsapp = True
				else:
					enquiry_form_save.is_whatsapp = False

				if is_email == 'EMAIL':
					enquiry_form_save.is_email    = True
				else:
					enquiry_form_save.is_email    = False

				if is_sms == 'SMS':
					enquiry_form_save.is_sms      = True
				else:
					enquiry_form_save.is_sms      = False

				#APPEND MR / MS TO NAME
				customer_name = enquiry_form_save.name
				customer_name = customer_name.lower()

				if enquiry_form_save.gender == 'MALE':
					prefix_list = ['mr.','mr']
					for prefix in prefix_list:
						
						prefix_exists = customer_name.startswith(prefix)

						if prefix_exists == False :
							if customer_name.startswith('dr.') == True or customer_name.startswith('dr') == True :
								enquiry_form_save.name = customer_name.title()
							else:	
								enquiry_form_save.name = 'Mr. '+customer_name
						else:
							enquiry_form_save.name = customer_name.title()													

				elif enquiry_form_save.gender == 'FEMALE':
					prefix_list = ['ms.','ms']
					for prefix in prefix_list:
						
						prefix_exists = customer_name.startswith(prefix)

						if prefix_exists == False :
							if customer_name.startswith('dr.') == True or customer_name.startswith('dr') == True or customer_name.startswith('mrs.') == True or customer_name.startswith('mrs') == True:
								enquiry_form_save.name = customer_name.title()
							else:	
								enquiry_form_save.name = 'Ms. '+customer_name
						else:
							enquiry_form_save.name = customer_name.title()

				else:
					pass

				enquiry_form_save.save()
				messages.success(request,"Client Details Succesfully updated")

		return redirect('common_items:client-orders',client_id)

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
		
		#OPEN TICKETS
		this_month_open_tickets = FollowUp.objects.filter(Q(is_active=True) & Q(Q(status='TICKET_RISED')|Q(status='FOLLOWUP_IN_PROGRESS')) & Q(investigation__created__month=timezone.now().month)).count()
		last_month_open_tickets = FollowUp.objects.filter(Q(is_active=True) & Q(Q(status='TICKET_RISED')|Q(status='FOLLOWUP_IN_PROGRESS')) & Q(investigation__created__month=(timezone.now()-relativedelta(months=1)).month)).count()
		
		#followup cleaning count	
		try:
			follow_up_cleaning = FollowUpScheduler.objects.filter(is_active=True,work_status='FOLLOW_UP_CLEANING_FULFILLED')
			this_month_followup_count = follow_up_cleaning.filter(start_at__month=timezone.now().month).count()
			last_month_followup_count = follow_up_cleaning.filter(start_at__month=(timezone.now()-relativedelta(months=1)).month).count()
		except:
			follow_up_cleaning = None
			this_month_followup_count = 0
			last_month_followup_count = 0

		#monthlly and last monthlly lost
		this_month_evaluations = Evaluation.objects.filter(is_active=True,quatation_approved_date__month=timezone.now().month,quatation_approved_date__year=timezone.now().year)
		last_month_evaluations = Evaluation.objects.filter(is_active=True,quatation_approved_date__month=(timezone.now()-relativedelta(months=1)).month,quatation_approved_date__year=(timezone.now()-relativedelta(months=1)).year)		
		
		if this_month_evaluations:
			thismonth_loss = this_month_evaluations.aggregate(Sum('promocode_amount'))['promocode_amount__sum']+this_month_evaluations.aggregate(Sum('extra_discount'))['extra_discount__sum']+this_month_evaluations.aggregate(Sum('fine_amount'))['fine_amount__sum']+this_month_evaluations.aggregate(Sum('writeback_amount'))['writeback_amount__sum']
		else:
			thismonth_loss = 0

		if last_month_evaluations:
			lastmonth_loss = last_month_evaluations.aggregate(Sum('promocode_amount'))['promocode_amount__sum']+last_month_evaluations.aggregate(Sum('extra_discount'))['extra_discount__sum']+last_month_evaluations.aggregate(Sum('fine_amount'))['fine_amount__sum']+last_month_evaluations.aggregate(Sum('writeback_amount'))['writeback_amount__sum']
		else:
			lastmonth_loss = 0
			
			

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

		return render(request,"common/ticket/tickets.html",{"this_month_open_tickets":this_month_open_tickets,"last_month_open_tickets":last_month_open_tickets, "this_month_followup_count":this_month_followup_count,"last_month_followup_count":last_month_followup_count,"tickets":tickets,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,"lastmonth_loss":lastmonth_loss,"thismonth_loss":thismonth_loss})

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

		return render(request,'common/ticket/followup-tickets.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})

	
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
		
		tab = request.GET.get('tab')
		if not tab:
			tab = 'ALL'

		#Evaluation Details
		search                  = request.GET.get('search')
		
		#sales amount
		if search:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         = None

			#Transactions
			try:
				transactions 	 = PaymentHistory.objects.filter(is_active=True).filter(Q(Q(order__evaluation__customer__name__icontains=search)|Q(order__evaluation__evaluation_id__icontains=search))).annotate(cleaning_count=Count('order__order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order__order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order__order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order__order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField()))).order_by('-paid_date')
			except:
				transactions	 = None

		else:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))				
			except:
				invoices         	 = None

			#Transactions
			try:
				transactions = PaymentHistory.objects.filter(is_active=True).annotate(cleaning_count=Count('order__order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order__order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order__order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order__order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField()))).order_by('-paid_date')
			except:
				transactions = None

		
		
		#Pending Payments

		# try:
		# 	pending_payments = invoices.filter( Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) ))
		# except:
		#  	pending_payments = None

		#remove object in postpaid if not last cleaning fulfilled	
		#remove if subscription to pay date

		# if pending_payments:
		# 	for payment in pending_payments:
		# 		if payment.evaluation.payment_method == 'POSTPAID' and payment.cleaning_count :
		# 			very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
		# 			if very_latest_cleaning.work_status != 'CLEANING_FULFILLED':
		# 				pending_payments = pending_payments.exclude(id=payment.id)
		# 		if payment.evaluation.payment_method == 'SUBSCRIPTION' and not payment.subscription_topay_date:
		# 			pending_payments = pending_payments.exclude(id=payment.id)	

		#Pending Payment and Order Count	
		# if pending_payments: 
		# 	total_pending_amount = 0
		# 	for payment in pending_payments:
		# 		if payment.evaluation.payment_method in ['PREPAID','POSTPAID','BREAKDOWN']:
		# 			total_pending_amount += payment.remining_amount

		# 		if payment.evaluation.payment_method == 'SUBSCRIPTION':
		# 			total_pending_amount += payment.subscription_topay		

		# 	total_pending_orders = pending_payments.count()
		# else:
		# 	total_pending_amount = 0
		# 	total_pending_orders = 0


		#due payments
		# try:
		# 	due_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) ))
		# except:
		# 	due_payments = None
		
		#Due Payment and Order Count	
		# if due_payments: 
		# 	total_due_amount = 0
		# 	for payment in due_payments:
		# 		if payment.evaluation.payment_method in ['POSTPAID','BREAKDOWN']:
		# 			total_due_amount += payment.remining_amount

		# 		if payment.evaluation.payment_method == 'SUBSCRIPTION':
		# 			total_due_amount += payment.subscription_topay		

		# 	total_due_orders = due_payments.count()
		# else:
		# 	total_due_amount = 0
		# 	total_due_orders = 0


		#doubtful due payments
		try:
			doubtful_due_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) )).filter(callback_status='LEGAL_ACTION')
		except:
			doubtful_due_payments = None

		#Doubtfull Due Payment and Order Count	
		if doubtful_due_payments: 
			total_doubtful_due_amount = 0
			for payment in doubtful_due_payments:
				if payment.evaluation.payment_method in ['POSTPAID','BREAKDOWN']:
					total_doubtful_due_amount += payment.remining_amount

				if payment.evaluation.payment_method == 'SUBSCRIPTION':
					total_doubtful_due_amount += payment.subscription_topay		

			total_doubtful_due_orders = doubtful_due_payments.count()
		else:
			total_doubtful_due_amount = 0
			total_doubtful_due_orders = 0

		#normal due Payments
		try:
			normal_due_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) )).filter(~Q(callback_status='LEGAL_ACTION'))
		except:
			normal_due_payments = None
		
		#Normal Due Payment and Order Count	
		if normal_due_payments: 
			total_normal_due_amount = 0
			for payment in normal_due_payments:
				if payment.evaluation.payment_method in ['POSTPAID','BREAKDOWN']:
					total_normal_due_amount += payment.remining_amount		

			total_normal_due_orders = normal_due_payments.count()
		else:
			total_normal_due_amount = 0
			total_normal_due_orders = 0

		#subscription due Payments
		try:
			subscription_due_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) )).filter(~Q(callback_status='LEGAL_ACTION'))
		except:
			subscription_due_payments = None

		#Subscription Due Payment and Order Count	
		if subscription_due_payments: 
			total_subscription_due_amount = 0
			for payment in subscription_due_payments:

				if payment.evaluation.payment_method == 'SUBSCRIPTION':
					total_subscription_due_amount += payment.subscription_topay		

			total_subscription_due_orders = subscription_due_payments.count()
		else:
			total_subscription_due_amount = 0
			total_subscription_due_orders = 0

		#New Order due Payments
		try:
			neworder_due_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(amount_paid=0)) | Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(amount_paid=0)) )).filter(~Q(callback_status='LEGAL_ACTION'))
		except:
			neworder_due_payments = None

		#New Order Due Payment and Order Count	
		if neworder_due_payments: 
			total_neworder_due_amount = 0
			for payment in neworder_due_payments:
				if payment.evaluation.payment_method in ['POSTPAID','BREAKDOWN']:
					total_neworder_due_amount += payment.remining_amount		

			total_neworder_due_orders = neworder_due_payments.count()		
		else:
			total_neworder_due_amount = 0
			total_neworder_due_orders = 0

		total_due_amount = total_normal_due_amount+total_subscription_due_amount+total_neworder_due_amount
		total_due_orders = total_normal_due_orders+total_subscription_due_orders+total_neworder_due_orders


		#to find days
		# if pending_payments:
		# 	for payment in pending_payments:
		# 		if payment.evaluation.payment_method == 'PREPAID' and payment.orderschedules:
		# 			very_old_cleaning   = payment.orderschedules[0]
		# 			payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
		# 		elif payment.evaluation.payment_method == 'POSTPAID' and payment.orderschedules:
		# 			very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
		# 			payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	
		# 		elif payment.evaluation.payment_method == 'BREAKDOWN' and payment.orderschedules:
				
		# 			very_old_cleaning   = payment.orderschedules[0]
		# 			very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
		# 			payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
		# 			payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	

		# 			#to check last cleaning completed for break down after payment
		# 			if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
		# 				payment.last_completed = True	

		# 		elif payment.evaluation.payment_method == 'SUBSCRIPTION':				
		# 			payment.delaydays= (timezone.now()-payment.subscription_topay_date).days	

		# if due_payments:
		# 	for payment in due_payments:
		# 		if payment.evaluation.payment_method == 'PREPAID' and payment.orderschedules:
		# 			very_old_cleaning   = payment.orderschedules[0]
		# 			payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
		# 		elif payment.evaluation.payment_method == 'POSTPAID' and payment.orderschedules:
		# 			very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
		# 			payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	
		# 		elif payment.evaluation.payment_method == 'BREAKDOWN' and payment.orderschedules:
				
		# 			very_old_cleaning   = payment.orderschedules[0]
		# 			very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
		# 			payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
		# 			payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	

		# 			#to check last cleaning completed for break down after payment
		# 			if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
		# 				payment.last_completed = True	

		# 		elif payment.evaluation.payment_method == 'SUBSCRIPTION':				
		# 			payment.delaydays= (timezone.now()-payment.subscription_topay_date).days

		if doubtful_due_payments:
			for payment in doubtful_due_payments:
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

		if normal_due_payments:
			for payment in normal_due_payments:
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
		
		if subscription_due_payments:
			for payment in subscription_due_payments:
				if payment.evaluation.payment_method == 'SUBSCRIPTION':				
					payment.delaydays= (timezone.now()-payment.subscription_topay_date).days


		if neworder_due_payments:
			for payment in neworder_due_payments:
				if payment.evaluation.payment_method == 'PREPAID' and payment.orderschedules:
					very_old_cleaning   = payment.orderschedules[0]
					payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days	
				elif payment.evaluation.payment_method == 'BREAKDOWN' and payment.orderschedules:
				
					very_old_cleaning   = payment.orderschedules[0]
					payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days	

					#to check last cleaning completed for break down after payment
					if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
						payment.last_completed = True

		#PAGINATION INVOICE		

		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20
		
		#page1
		page1 = request.GET.get('page1',1) 

		paginator1=Paginator(transactions,no_of_entries)
			
		try: 
			transactions=paginator1.page(page1) 
		except PageNotAnInteger:
			transactions=paginator1.page(1) 
		except EmptyPage:
			transactions=paginator1.page(paginator1.num_pages) 

		#page2
		page2 = request.GET.get('page2',1) 

		paginator2=Paginator(doubtful_due_payments,no_of_entries)
			
		try: 
			doubtful_due_payments=paginator2.page(page2) 
		except PageNotAnInteger:
			doubtful_due_payments=paginator2.page(1) 
		except EmptyPage:
			doubtful_due_payments=paginator2.page(paginator2.num_pages) 

		#page3
		page3 = request.GET.get('page3',1) 

		paginator3=Paginator(normal_due_payments,no_of_entries)
			
		try: 
			normal_due_payments=paginator3.page(page3) 
		except PageNotAnInteger:
			normal_due_payments=paginator3.page(1) 
		except EmptyPage:
			normal_due_payments=paginator3.page(paginator3.num_pages)

		#page4
		page4 = request.GET.get('page4',1) 

		paginator4=Paginator(subscription_due_payments,no_of_entries)
			
		try: 
			subscription_due_payments=paginator4.page(page4) 
		except PageNotAnInteger:
			subscription_due_payments=paginator4.page(1) 
		except EmptyPage:
			subscription_due_payments=paginator4.page(paginator4.num_pages)

		#page5
		page5     = request.GET.get('page5',1) 

		paginator5=Paginator(neworder_due_payments,no_of_entries)
			
		try: 
			neworder_due_payments=paginator5.page(page5) 
		except PageNotAnInteger:
			neworder_due_payments=paginator5.page(1) 
		except EmptyPage:
			neworder_due_payments=paginator5.page(paginator5.num_pages) 

		# Get the index of the current page
		index1 = transactions.number - 1
		index2 = doubtful_due_payments.number - 1
		index3 = normal_due_payments.number - 1
		index4 = subscription_due_payments.number - 1
		index5 = neworder_due_payments.number - 1
		# edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index1 = len(paginator1.page_range)
		max_index2 = len(paginator2.page_range)
		max_index3 = len(paginator3.page_range)
		max_index4 = len(paginator4.page_range)
		max_index5 = len(paginator5.page_range)
		
		# You want a range of 7, so lets calculate where to slice the list
		start_index1 = index1 - 3 if index1 >= 3 else 0
		end_index1 = index1 + 3 if index1 <= max_index1 - 3 else max_index1

		start_index2 = index2 - 3 if index2 >= 3 else 0
		end_index2 = index2 + 3 if index2 <= max_index2 - 3 else max_index2

		start_index3 = index3 - 3 if index3 >= 3 else 0
		end_index3 = index3 + 3 if index3 <= max_index3 - 3 else max_index3

		start_index4 = index4 - 3 if index4 >= 3 else 0
		end_index4   = index4 + 3 if index4 <= max_index4 - 3 else max_index4

		start_index5 = index4 - 3 if index5 >= 3 else 0
		end_index5 = index4 + 3 if index5 <= max_index5 - 3 else max_index5

		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range1 = list(paginator1.page_range)[start_index1:end_index1]
		page_range2 = list(paginator2.page_range)[start_index2:end_index2]
		page_range3 = list(paginator3.page_range)[start_index3:end_index3]
		page_range4 = list(paginator4.page_range)[start_index4:end_index4]
		page_range5 = list(paginator5.page_range)[start_index5:end_index5]

		entry_per_page1 = (transactions.end_index())-(transactions.start_index())+1
		entry_per_page2 = (doubtful_due_payments.end_index())-(doubtful_due_payments.start_index())+1
		entry_per_page3 = (normal_due_payments.end_index())-(normal_due_payments.start_index())+1
		entry_per_page4 = (subscription_due_payments.end_index())-(subscription_due_payments.start_index())+1
		entry_per_page5 = (neworder_due_payments.end_index())-(neworder_due_payments.start_index())+1

		return render(request,'common/payment/payments.html',{'total_due_amount':total_due_amount,'total_due_orders':total_due_orders,'total_doubtful_due_amount':total_doubtful_due_amount,'total_doubtful_due_orders':total_doubtful_due_orders,'tab':tab,'invoices':invoices,"search_query":search,"page_range1":page_range1,"page_range2":page_range2,"page_range3":page_range3,"page_range4":page_range4,"page_range5":page_range5,"entry_per_page1":entry_per_page1,"entry_per_page2":entry_per_page2,"entry_per_page3":entry_per_page3,"entry_per_page4":entry_per_page4,"entry_per_page5":entry_per_page5,"no_of_entries":no_of_entries,'transactions':transactions,"doubtful_due_payments":doubtful_due_payments,'normal_due_payments':normal_due_payments,'subscription_due_payments':subscription_due_payments,'neworder_due_payments':neworder_due_payments})

	def post(self,request):
		order_id = request.POST.get('orderid')
		tab = request.POST.get('tab_id')
		
		notes = request.POST.get('payment_note')

		order = Order.objects.filter(is_active=True,id=int(order_id)).first()
		order.payment_notes = notes
		order.payment_note_by = request.user
		order.save()

		messages.success(request,"Payment note updated !!")
		return redirect('/common/payments/?tab='+tab+'')

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
						cleaning_price -= invoice.evaluation.promocode_amount
						cleaning_price -= invoice.evaluation.writeback_amount
						cleaning_price += invoice.evaluation.fine_amount

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

		evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluaation).first()
    
		address = evaluationdetails.address

		evaluationbooks = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True),to_attr='sections'))
		evaluationbook = evaluationbooks.first()

		if address.floor == None and address.avenue == None:
			address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
		
		elif address.floor == None:
			address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
		
		elif address.avenue == None:
			address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
		
		else:
			address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

		separator = ", "

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

		if evaluaation.customer.is_email == True and invoice_type == "invoice" :
			#Email Send
			msg_html = render_to_string('email/invoice.html',{"invoice":order,"address_list":separator.join(address_list),"evaluationbooks":evaluationbooks})
			msg = EmailMultiAlternatives('Bleach Invoice', '', 'notification@bleach-kw.com', [evaluaation.customer.email])
			msg.attach_alternative(msg_html, "text/html")
			msg.send(fail_silently=False)

		messages.success(request,"Invoice has been Sent !")

		return redirect('common_items:active-subscriptions')


class ClientOrderDetails(IsAuthenticated,View):
	def get(self,request,order_id):

		order = Order.objects.select_related('evaluation__customer','evaluation__call_attender').prefetch_related(
			Prefetch('evaluation__booking_evaluation',queryset=CustomerBooking.objects.filter(is_active=True,booking_type='CLEANINGBOOKING'),to_attr='customer_booking'),
			Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('evaluator','address__governorate','address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').prefetch_related(Prefetch('evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationbookmedias'),Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='evaluationbooksectionkeynotes')).annotate(kitchen_keynote=Sum( Case( When(keynotesections__sub_area='kitchen',then=1),default=0,output_field=IntegerField()))),to_attr='evaluationbooksections')),to_attr='evaluationbooks')),to_attr='evaluationdetails'),
			Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book','customer_address__area','customer_address__governorate').order_by('start_at').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True),to_attr='paybackdiscounts'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True),to_attr='buybackpromocodegift'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),
			Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),
			Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)

		try:
			booking_id = CustomerBooking.objects.get(is_active=True,evaluation__id=order.evaluation.id,booking_type='CLEANINGBOOKING').booking_id
		except:
			booking_id = None
		
		invoice = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).get(is_active=True,id=order_id)   #.annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') ))
		
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

		price_ranges = ServicePriceRange.objects.filter(is_active=True)

		return render(request,"common/client/order-page.html",{"invoice":invoice,"booking_id":booking_id,"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"average_feedback":average_feedback,"price_ranges":price_ranges})

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


class ClientOrderDetailsTest(IsAuthenticated,View):
	def get(self,request,order_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__booking_evaluation',queryset=CustomerBooking.objects.filter(is_active=True,booking_type='CLEANINGBOOKING'),to_attr='customer_booking'),Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book',queryset=EvaluationBook.objects.filter(is_active=True)),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')).annotate(kitchen_keynote=Sum( Case( When(keynotesections__sub_area='kitchen',then=1),default=0,output_field=IntegerField()))),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True),to_attr='paybackdiscounts'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True),to_attr='buybackpromocodegift'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)

		try:
			booking_id = CustomerBooking.objects.get(is_active=True,evaluation__id=order.evaluation.id,booking_type='CLEANINGBOOKING').booking_id
		except:
			booking_id = None
		
		invoice = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).get(is_active=True,id=order_id)   #.annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') ))
		
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

		price_ranges = ServicePriceRange.objects.filter(is_active=True)
			
		return render(request,"common/client/order-page-test.html",{"invoice":invoice,"booking_id":booking_id,"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"average_feedback":average_feedback,"price_ranges":price_ranges})


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

			# if date < todate:
			# 	print(date,"dtER")
			orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','order_scheduler_book__estimated_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluation__discount').order_by('end_at')
			# else:
			# 	orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','order_scheduler_book__estimated_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluation__discount').order_by('end_at')

			found = set()
			schedules_list = []

			for schedule in orderschedules:
				schedules_list.append(schedule)


			print(schedules_list,"listss")

			for schedule in schedules_list:

				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()

				total_schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0]).count()

				order_amount = schedule[1]

				cleaning_amount += float(order_amount/schedule_count)

				if schedule[6] > 0:
					cleaning_amount -= float(schedule[6]/total_schedule_count)
				if schedule[7] > 0:
					cleaning_amount -= float(schedule[7]/total_schedule_count)
				if schedule[8] > 0:
					cleaning_amount += float(schedule[8]/total_schedule_count)
				if schedule[9] > 0:
					cleaning_amount -= float(schedule[9]/total_schedule_count)
				


			todate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

			if date == todate:
		
				daily_sales = round(cleaning_amount)

			print(cleaning_amount,"clamt")

			monthly_sales += float(cleaning_amount)

		monthly_sales = round(monthly_sales)

		return render(request,'common/dailysales/daily-sales.html',{"dailysales":daily_sales,"monthlysales":monthly_sales,"month_name":full_month_name})


class ResourceManagementOld(IsAuthenticated,View):
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

class AddFeedBackOrder(IsAuthenticated,View):
	def get(self,request,orderid):

		order = Order.objects.filter(id=int(orderid)).first()

		try:
			questions = Question.objects.filter(is_active=True).order_by('id')
		except:
			questions = None

		return render(request,'common/feedback/add-feedback.html',{'order':order,"questions":questions})

	def post(self,request,orderid):
		order_id        = request.POST.get('order_id')
		feedback_remark = request.POST.get('notes')

		try:
			order                    = Order.objects.get(id=order_id)
			order.feedback_notes     = feedback_remark
			order.is_feedback_marked = True
			order.save()
		except:
			order = 	None

		try:
			questions = Question.objects.filter(is_active=True).order_by('id')
		except:
			questions = None

		create_feedbacks = []
		if order:
			for question in questions:
				rating = request.POST.get('rating'+str(question.id)) or 0

				create_feedbacks.append(FeedBack(order=order,question=question,rating=rating,response_date=timezone.now()))
			FeedBack.objects.bulk_create(create_feedbacks)

			messages.success(request,"Feedback Succesfully Submitted")
		else:
			messages.error(request,'Please Select a BLC Number')

		return redirect('common_items:orders')

class PromocodeView(IsAuthenticated,View):

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

		return render(request,'common/promocode/promo.html',{'promo_codes':promo_codes,'active_promocodes_count':active_promocodes_count,'used_coupons_count':used_coupons_count,})

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
		
		return redirect('common_items:promocode')


class LeaveScheduler(IsAuthenticated,View):
	def get(self,request):
		return render(request,'common/leavescheduler/leave.html',{})

class ResourceManagement(IsAuthenticated,View):
	def get(self,request):
		
		#workers_date
		workers_calendar_date	= request.GET.get('workers_calendar_date')
		
		try:
			workers_date = datetime.strptime(workers_calendar_date,'%d-%m-%Y')
		except:
			workers_date = timezone.now().date()

		#time filter
		try:
			starting_datetime  = datetime.strptime(str(workers_calendar_date+' '+request.GET.get('starting_time')),'%d-%m-%Y %I:%M %p')
			ending_datetime    = datetime.strptime(str(workers_calendar_date+' '+request.GET.get('ending_time')),'%d-%m-%Y %I:%M %p')
		except:
			starting_datetime  = None 
			ending_datetime    = None

		#apply time and date filter
		if starting_datetime and ending_datetime:
			workers            =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).prefetch_related('leave_staff').annotate(leave=Sum( Case( When( leave_staff__leave_date=workers_date,then=1),default=0,output_field=IntegerField())) ).prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=workers_date)|Q(end_at__date=workers_date)) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation','team__order_scheduler__order_scheduler_book'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter(Q( Q(is_active=True)&Q(Q(start_at__date=workers_date)|Q(end_at__date=workers_date)) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details')).annotate(cleaning_contained=Sum(Case(When(Q(Q(cleaning_member_user__start_at__range=(starting_datetime,ending_datetime))|Q(cleaning_member_user__end_at__range=(starting_datetime,ending_datetime))),then=1),default=0,output_field=IntegerField()))).filter(cleaning_contained=0)
		else:
			workers            =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).prefetch_related('leave_staff').annotate(leave=Sum( Case( When( leave_staff__leave_date=workers_date,then=1),default=0,output_field=IntegerField())) ).prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__date=workers_date)|Q(end_at__date=workers_date)) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation','team__order_scheduler__order_scheduler_book'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter(Q( Q(is_active=True)&Q(Q(start_at__date=workers_date)|Q(end_at__date=workers_date)) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details'))

		#otherfilters
		search 		   = request.GET.get('search')
		staff_type     = request.GET.get('staff_type')
		service_type   = request.GET.get('service_type')
		

		filters=[]
		if search: 
		    case1 = Q(name__icontains=search)
		    filters.append(case1)
		if staff_type:
			case2 = Q(user_type=staff_type)
			filters.append(case2)
		if service_type:
			if service_type == 'is_general_skill':
				case3 = Q(is_general_skill=True)
			if service_type == 'is_deep_skill':
				case3 = Q(is_deep_skill=True)
			if service_type == 'is_upholstery_skill':
				case3 = Q(is_upholstery_skill=True)
			if service_type == 'is_carpet_skill':
				case3 = Q(is_carpet_skill=True)
			if service_type == 'is_kitchen_skill':
				case3 = Q(is_kitchen_skill=True)
			if service_type == 'is_sterilization_skill':
				case3 = Q(is_sterilization_skill=True)
			if service_type == 'is_carpet_skill':
				case3 = Q(is_carpet_skill=True)
			if service_type == 'is_mattress_skill':
				case3 = Q(is_mattress_skill=True)
			if service_type == 'is_facade_skill':
				case3 = Q(is_facade_skill=True)
			if service_type == 'is_storagearea_skill':
				case3 = Q(is_storagearea_skill=True)
			if service_type == 'is_carparkingumbrella_skill':
				case3 = Q(is_carparkingumbrella_skill=True)
			if service_type == 'is_outdoor_skill':
				case3 = Q(is_outdoor_skill=True)
			if service_type == 'is_window_skill':
				case3 = Q(is_window_skill=True)
			
			filters.append(case3)
		
		if staff_type or service_type or search: 
		    filters         = functools.reduce(operator.and_,filters)
		    workers = workers.filter(filters)

		##Monthlly Data
		# month_start    = workers_date.replace(day=1)
		# month_end      = month_start+relativedelta(months=1)-relativedelta(days=1)
		# month_range    = pd.date_range(month_start, month_end)
		
		# for worker in workers:
		# 	cleanings = CleaningTeamMember.objects.filter(is_active=True,member=worker).filter(Q(Q(start_at__month=workers_date.month)|Q(end_at__month=workers_date.month))).values('team__order_scheduler__order__feed_backs_order__rating','member__id','member__profile_image','start_at','end_at').annotate(duration = ExpressionWrapper(F('end_at') - F('start_at'), output_field=DurationField()))
		# 	followups = FollowUpTeamMember.objects.filter(is_active=True,member=worker).filter(Q(Q(start_at__month=workers_date.month)|Q(end_at__month=workers_date.month))).select_related('team__followup_scheduler__follow_up__investigation__order__feed_backs_order').values('team__followup_scheduler__follow_up__investigation__order__feed_backs_order__rating','member__id','member__profile_image','start_at','end_at').annotate(duration = ExpressionWrapper(F('start_at') - F('start_at'), output_field=DurationField()))		

		# 	###to find worked days
		# 	worked_days = 0
		# 	for date in month_range:
		# 		start_date_day = date
		# 		end_date_day   = date+timedelta(1)
		# 		if cleanings.filter(start_at__range=(start_date_day,end_date_day),end_at__range=(start_date_day,end_date_day)) or followups.filter(start_at__range=(start_date_day,end_date_day),end_at__range=(start_date_day,end_date_day)):
		# 			worked_days = worked_days+1		
		# 	worker.worked_days = worked_days

			###to find total hours
			# cleaning_hours     = cleanings.aggregate(total_duration=Sum('duration'))
			# followup_hours     = followups.aggregate(total_duration=Sum('duration'))
			# total_time         = (cleaning_hours['total_duration']or timedelta()) + (followup_hours['total_duration']or timedelta())
			# total_hours        = total_time.days*24+total_time.seconds/3600
			# worker.total_hours = total_hours
			
			# ###to find average work hour
			# if total_hours and worked_days:
			# 	worker.average_hours = total_hours/worked_days
			# else:
			# 	worker.average_hours = 0.00

			# ###to find total rating
			# worker.rating = cleanings.aggregate(total_rating=Sum('team__order_scheduler__order__feed_backs_order__rating')/Count('team__order_scheduler__order__feed_backs_order__rating'))['total_rating']or 0			

		return render(request,'common/resource/resource-new.html',{"workers":workers,"workers_date":workers_date,"service_type":service_type,"staff_type":staff_type,"search":search})

	def post(self,request):
		
		response_dict = {}
		user = UserProfile.objects.filter(id=request.POST.get('user_id')).update(is_general_skill=request.POST.get('is_general_skill'),is_deep_skill=request.POST.get('is_deep_skill'),is_upholstery_skill=request.POST.get('is_upholstery_skill'),is_carpet_skill=request.POST.get('is_carpet_skill'),is_kitchen_skill=request.POST.get('is_kitchen_skill'),is_sterilization_skill=request.POST.get('is_sterilization_skill'),is_mattress_skill=request.POST.get('is_mattress_skill'),is_facade_skill=request.POST.get('is_facade_skill'),is_storagearea_skill=request.POST.get('is_storagearea_skill'),is_carparkingumbrella_skill=request.POST.get('is_carparkingumbrella_skill'),is_outdoor_skill=request.POST.get('is_outdoor_skill'),is_window_skill=request.POST.get('is_window_skill'))
		response_dict['success'] = True

		return JsonResponse(response_dict)

class Productivity(IsAuthenticated,View):
	def get(self,request):

		#save ajax productivity
		response_dict = {}
		action = request.GET.get('action_type')
		if action == 'edit_productivity':
			productivity_id    = request.GET.get('productivity_id')
			productivity_value = request.GET.get('productivity_value')

			productivity                  = ServiceProductivity.objects.get(id=productivity_id)
			productivity.perhour_cleaning = productivity_value
			productivity.save()
			response_dict['success'] =True
			return JsonResponse(response_dict)
		
		
		try:
			service_types = ServiceType.objects.filter(is_active=True)	
		except:
			service_types = None

		try:
			service_price_ranges = ServicePriceRange.objects.filter(is_active=True)
		except:
			service_price_ranges = None

		try:
			service_productivities = ServiceProductivity.objects.filter(is_active=True)
		except:
			service_productivities = None

		discount_settings = Settings.objects.filter(is_active=True).first()

		return render(request,'common/productivity/productivity.html',{'service_price_ranges':service_price_ranges,'service_productivities':service_productivities,'service_types':service_types,"discount_settings":discount_settings,})

	def post(self,request):
		
		action = request.POST.get('action_type')
	
		if action == 'edit_price_range':
			price_range_id       = request.POST.get('price_range')
			price_range          = ServicePriceRange.objects.get(id=price_range_id)
			price_range_form     = ServicePriceRangeForm(request.POST,instance=price_range)
			if price_range_form.is_valid():
				price_range_form.save()
				messages.success(request,"Service Price Range Updated Successfully")
			else:
				messages.error(request,get_error(price_range_form))

		if action == 'add_price_range':
			price_range_form     = ServicePriceRangeForm(request.POST)
			if price_range_form.is_valid():
				price_range_form.save()
				messages.success(request,"Service Price Range Added Successfully")
			else:
				messages.error(request,get_error(price_range_form))

		if action == 'delete_price_range':
			price_range_id       = request.POST.get('price_range')
			price_range          = ServicePriceRange.objects.filter(id=price_range_id).delete()
			messages.success(request,"Service Price Range Deleted Successfully")

		if action == 'edit_customer_discount':
			discount_setting_id    = request.POST.get('discount_setting_id')
			discount_setting       = Settings.objects.get(id=discount_setting_id)
			discount_setting_form  = DiscountSettingsForm(request.POST,instance=discount_setting)
			
			if discount_setting_form.is_valid():
				discount_setting_form.save()
				messages.success(request,"Customer Discount Successfully Updated")
			else:
				messages.error(request,get_error(discount_setting_form))

		return redirect('common_items:productivity')

class CallBackList(IsAuthenticated,View):
	def get(self,request):

		tab = request.GET.get('tab')
		if not tab:
			tab = 'ORDERS'
		print(tab,"tabber")

		payment_type = request.GET.get('payment_type')
		if not payment_type :
			payment_type = 'DUE'

		#Evaluation Details
		search                  = request.GET.get('search')
		#for order filtering
		
		order_status = request.GET.get('order_status')
		order_status2 = request.GET.get('order_status')

		if tab == 'ORDERS':
			callback_status = request.GET.get('callback_status')
		else:
			callback_status = request.GET.get('callback_status_payments')
			
		print(callback_status,"tabber2")

		
		if search:
			evaluations = Evaluation.objects.filter(is_active=True).filter(Q( Q(Q(quatation_status='APPROVED') & Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) | Q(quatation_status='PENDING')|Q(quatation_status='REJECTED')|Q(quatation_status='EXPIRED') )).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(customer__mobile_number__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_book')),to_attr='details_evaluation'))
		else:
			evaluations = Evaluation.objects.filter(is_active=True).filter(Q( Q(Q(quatation_status='APPROVED') & Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) | Q(quatation_status='PENDING')|Q(quatation_status='REJECTED')|Q(quatation_status='EXPIRED') )).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_book')),to_attr='details_evaluation'))

		#sales amount
		if search:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         = None
			
		else:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         	 = None
						
		
		if payment_type != 'DUE':

			#Pending Payments
			try:
				payments_list = invoices.filter(Q( Q(Q(Q(evaluation__payment_method='PREPAID')&~Q(payment_status='COMPLETED'))|Q(Q(evaluation__payment_method='BREAKDOWN')&Q(preamount_paid=0))) | Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) ))
			except:
				payments_list = None

			
			#remove object in postpaid if not last cleaning fulfilled	
			#remove if subscription to pay date
			if payments_list:
				for payment in payments_list:
					if payment.evaluation.payment_method == 'POSTPAID' and payment.cleaning_count :
						very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
						if very_latest_cleaning.work_status != 'CLEANING_FULFILLED':
							pending_payments = pending_payments.exclude(id=payment.id)
					if payment.evaluation.payment_method == 'SUBSCRIPTION' and not payment.subscription_topay_date:
						pending_payments = pending_payments.exclude(id=payment.id)	

			#to find days
			if payments_list:
				for payment in payments_list:
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

		else:

			#due Payments
			try:
				payments_list = invoices.filter(Q( Q( Q(Q(evaluation__payment_method='POSTPAID')|Q(evaluation__payment_method='BREAKDOWN')) & Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD')) & Q(completed_cleaning_count=F('cleaning_count')) ) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) ))
			except:
				payments_list = None

		
		# callback and order status filters
		order_callback_status_filter       = []
		payment_callback_status_filter       = []

		if order_status:
			if order_status == 'APPROVED_NOT_PAID':
				case1       = Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0)))
			else:
				case1       = Q(quatation_status=order_status)

			if order_status == 'APPROVED_NOT_PAID':
				case2       = Q(evaluation__quatation_status='APPROVED') & Q(Q(Q(evaluation__payment_method='PREPAID')&~Q(payment_status='COMPLETED'))|Q(Q(evaluation__payment_method='BREAKDOWN')&Q(preamount_paid=0)))
			else:
				case2       = Q(evaluation__quatation_status=order_status)
			order_callback_status_filter.append(case1)	
			payment_callback_status_filter.append(case2)	

		if callback_status:
			case3 		= Q(evaluation_order__callback_status=callback_status)
			case4 		= Q(callback_status=callback_status)
			order_callback_status_filter.append(case3)
			payment_callback_status_filter.append(case4)

		if order_status or callback_status:
			order_callback_status_filter     = functools.reduce(operator.and_,order_callback_status_filter)
			payment_callback_status_filter     = functools.reduce(operator.and_,payment_callback_status_filter)
			evaluations = evaluations.filter(order_callback_status_filter)
			payments_list = payments_list.filter(payment_callback_status_filter)


		#PAGINATION ORDERS		
		no_of_entries = request.GET.get('no_of_entries')		
		if not no_of_entries:
			no_of_entries = 20

		page1 = request.GET.get('page1',1) 
		paginator1=Paginator(evaluations,no_of_entries)
		try: 
			evaluations=paginator1.page(page1) 
		except PageNotAnInteger:
			evaluations=paginator1.page(1)
		except EmptyPage:
			evaluations = paginator1.page(paginator1.num_pages) 

		page2 = request.GET.get('page2',1) 
		paginator2=Paginator(payments_list,no_of_entries)
		try: 
			payments_list=paginator2.page(page2) 
		except PageNotAnInteger:
			payments_list=paginator2.page(1)
		except EmptyPage:
			payments_list = paginator2.page(paginator2.num_pages)

		# Get the index of the current page
		index1 = evaluations.number - 1  # edited to something easier without index
		index2 = payments_list.number - 1
		# This value is maximum index of your pages, so the last page - 1
		max_index1 = len(paginator1.page_range)
		max_index2 = len(paginator2.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index1 = index1 - 3 if index1 >= 3 else 0
		end_index1 = index1 + 3 if index1 <= max_index1 - 3 else max_index1

		start_index2 = index2 - 3 if index2 >= 3 else 0
		end_index2 = index2 + 3 if index2 <= max_index2 - 3 else max_index2
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range1 = list(paginator1.page_range)[start_index1:end_index1]
		page_range2 = list(paginator2.page_range)[start_index2:end_index2]	

		entry_per_page1=(evaluations.end_index())-(evaluations.start_index())+1
		entry_per_page2=(payments_list.end_index())-(payments_list.start_index())+1

		return render(request,"common/callback-list/callbacklist.html",{"tab":tab,"order_status":order_status,"payment_type":payment_type,"payments":payments_list,"callback_status":callback_status,"evaluations":evaluations,"search_query":search,"page_range1":page_range1,"page_range2":page_range2,"entry_per_page1":entry_per_page1,"entry_per_page2":entry_per_page2,"no_of_entries":no_of_entries})

	def post(self,request):
		order_id = request.POST.get('callback_orderid')
		notes = request.POST.get('payment_note')
		print(order_id,notes,'notes')
		order = Order.objects.filter(is_active=True,id=int(order_id)).first()
		order.payment_notes = notes
		order.payment_note_by = request.user
		order.save()

		messages.success(request,"Payment note updated !!")
		return redirect('common_items:callback-list')

class TicketDetailsEdit(IsAuthenticated,View):
	def get(self,request,ticket_id,order_id):

		order = Order.objects.filter(id=int(order_id)).prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True,work_status='CLEANING_FULFILLED').select_related('customer_address__area','order_scheduler_book').prefetch_related(Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(check_out__isnull=True),to_attr='assigned_investigations')),to_attr='orderschedules')).first()
		ticket = FollowUp.objects.filter(is_active=True,id=int(ticket_id)).first()
		investigators = UserProfile.objects.filter(Q(Q(user_type='QUALITYCONTROLL')|Q(user_type='OPERATIONSUPERVISOR')),is_active=True)
		investigationmedias = InvestigationMedia.objects.filter(investigation__id=ticket.investigation.id,taken_status = 'CUSTOMER_SEND',is_active=True)
		
		return render(request,"common/ticket/ticket_registration_edit.html",{'order':order,'investigators':investigators,"ticket":ticket,"investigationmedias":investigationmedias})

	def post(self,request,ticket_id,order_id):
		
		investigation_form = InvestigationForm(request.POST)
		
		if investigation_form.is_valid():
			investigation_form_save = investigation_form.save(commit=False)
			
			ticket = FollowUp.objects.get(is_active=True,id=ticket_id)
			investigation = Investigation.objects.filter(is_active=True,id=ticket.investigation.id).first()
			
			investigation.assigned_by = request.user
			investigation.ticket_types = investigation_form_save.ticket_types
			investigation.notes = investigation_form_save.notes
			investigation.order_schedule = investigation_form_save.order_schedule
			investigation.investigator = investigation_form_save.investigator
			investigation.scheduled_at= timezone.now()
			investigation.save()

			#save media
			investigation_medias = request.FILES.getlist('investigation_media')
			if not investigation_medias == ['']:
					for image in investigation_medias:
						InvestigationMedia.objects.create(
							investigation = investigation,
							media = image,
							media_type = 'PHOTO',
							taken_status = 'CUSTOMER_SEND',
							is_active = True
						)
						
			messages.success(request,"Ticket Updated Succesfully!")
		else:
			messages.error(request,get_error(investigation_form))

		return redirect('common_items:tickets')



class NewEnquiry(IsAuthenticated,View):
	address_formset_define    = formset_factory(AddressForm)
	def get(self,request):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			locations = AreaType.objects.filter(is_active=True)
		except:
			locations = None

		enquiry_form    = UserProfileForm()

		try:
			customer_info = UserProfile.objects.filter(is_active=True,user_type='CUSTOMER')
		except:
			customer_info = None

		return render(request,'common/enquiry/newenquiry.html',{'enquiry_form':enquiry_form,'address_formset':self.address_formset_define(),'customer_info':customer_info,'governorates':governorates,'locations':locations})

	def post(self,request):
		enquiry_form     = UserProfileForm(request.POST,request.FILES or None)
		address_formset  = self.address_formset_define(request.POST)


		if enquiry_form.is_valid() and address_formset.is_valid():
			enquiry_form_save            = enquiry_form.save(commit=False)
			enquiry_form_save.username   = generate_random_username()
			enquiry_form_save.created_by = request.user
			enquiry_form_save.user_type  = 'CUSTOMER'

			#customer id generation
			customer_id                  = UserProfile.objects.filter(is_active=True,customer_id__isnull=False).aggregate(t=Max('customer_id'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'1000')
			current_customer_id_starting = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2))					
			if current_customer_id_starting == int(str(customer_id)[:4]):
				new_customer_id = int(customer_id)+1
			else:
				new_customer_id   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2)+'1001')

			enquiry_form_save.customer_id = new_customer_id

			#To Save Contact Platform
			contact_platforms 			 = request.POST.get('contact_platform')
			contact_platform_list 		 = contact_platforms.split(",")
			if contact_platform_list:
				for contact_platform in contact_platform_list:
					if contact_platform == 'Whatsapp':
						enquiry_form_save.is_whatsapp = True
					elif contact_platform == 'Email':
						enquiry_form_save.is_email    = True
					else:
						enquiry_form_save.is_sms      = True

			#APPEND MR / MS TO NAME
			customer_name = enquiry_form_save.name
			customer_name = customer_name.lower()

			if enquiry_form_save.gender == 'MALE':
				prefix_list = ['mr.','mr']
				for prefix in prefix_list:
					
					prefix_exists = customer_name.startswith(prefix)

					if prefix_exists == False :
						if customer_name.startswith('dr.') == True or customer_name.startswith('dr') == True :
							enquiry_form_save.name = customer_name.title()
						else:	
							enquiry_form_save.name = 'Mr. '+customer_name
					else:
						enquiry_form_save.name = customer_name.title()													

			elif enquiry_form_save.gender == 'FEMALE':
				prefix_list = ['ms.','ms']
				for prefix in prefix_list:
					
					prefix_exists = customer_name.startswith(prefix)

					if prefix_exists == False :
						if customer_name.startswith('dr.') == True or customer_name.startswith('dr') == True or customer_name.startswith('mrs.') == True or customer_name.startswith('mrs') == True:
							enquiry_form_save.name = customer_name.title()
						else:	
							enquiry_form_save.name = 'Ms. '+customer_name
					else:
						enquiry_form_save.name = customer_name.title()

			else:
				pass

			enquiry_form_save.save()

			for address_form in address_formset:
				if address_form.is_valid():
					address_form_save                   = address_form.save(commit=False)
					address_form_save.customer          = enquiry_form_save
					address_form_save.currently_active  = True

					#string check
					block_text = address_form_save.block
					floor_text = address_form_save.floor
					street_text = address_form_save.street
					avenue_text = address_form_save.avenue

					is_block = block_text.find("Block")
					is_street = street_text.find("Street")

					if floor_text:
						is_floor = floor_text.find("Floor")

						if is_floor == -1 :
							floor_text += ' '
							floor_text += 'Floor'
							address_form_save.floor = floor_text
						else:
							pass
					else: 
						pass

					if avenue_text:
						is_avenue = avenue_text.find("Avenue")

						if is_avenue == -1 :
							avenue_text += ' '
							avenue_text += 'Avenue'
							address_form_save.avenue = avenue_text
						else:
							pass
					else:
						pass

					print(block_text,is_block,"blockkk")

					if is_block == -1 :
						block_text += ' '
						block_text += 'Block'
						address_form_save.block = block_text
					else:
						pass

					if is_street == -1 :
						street_text += ' '
						street_text += 'Street'
						address_form_save.street = street_text
					else:
						pass

					address_form_save.save()

			messages.success(request,"Customer Details Succesfully Added")

		else:	
			if not enquiry_form.is_valid():
				messages.error(request,get_error(enquiry_form))
			if not address_formset.is_valid():
				messages.error(request,"An Error Occured")

			try:
				governorates = Governorate.objects.filter(is_active=True)
			except:
				governorates = None

			try:
				locations = AreaType.objects.filter(is_active=True)
			except:
				locations = None
			
			return render(request,'agent/enquiry/newenquiry.html',{'enquiry_form':enquiry_form,'address_formset':address_formset,'governorates':governorates,'locations':locations})					

		redirection = request.POST.get('redirect_to')

		if redirection == 'assign_evaluator':
			return redirect('common_items:makeevaluation',enquiry_form_save.id)
		elif redirection == 'quatation':
			return redirect('common_items:makequatation',enquiry_form_save.id)
		else:
			return redirect('common_items:existingenquiry',enquiry_form_save.id)


class ExistingEnquiry(IsAuthenticated,View):

	def get(self,request,enquiry_id):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			locations = AreaType.objects.filter(is_active=True)
		except:
			locations = None


		enquiry_user    = UserProfile.objects.get(id=enquiry_id)


		try:
			addresses   = Address.objects.filter(customer__id=enquiry_id)
		except:
			addresses   = None


		enquiry_form    = UserProfileForm(request.FILES or None,instance=enquiry_user)
		address_form    = AddressForm()

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=enquiry_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		return render(request,'common/enquiry/existingenquiry.html',{'enquiry_user':enquiry_user,'enquiry_form':enquiry_form,"address_form":address_form,'enquiryid':enquiry_id,'addresses':addresses,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"governorates":governorates,'locations':locations})

	def post(self,request,enquiry_id):

		enquiry_user    = UserProfile.objects.get(id=enquiry_id)

		action_mode 	= request.POST.get('action_type')

		if action_mode == 'update_customer_details':
			enquiry_form    = UserProfileForm(request.POST,request.FILES or None,instance=enquiry_user)

			if enquiry_form.is_valid():
				enquiry_form_save            = enquiry_form.save(commit=False)

				#To Save Contact Platform
				contact_platforms 			 = request.POST.get('contact_platform')
				contact_platform_list 		 = contact_platforms.split(",")

				if 'Whatsapp' in contact_platform_list:
					enquiry_form_save.is_whatsapp = True
				else:
					enquiry_form_save.is_whatsapp = False

				if 'Email' in contact_platform_list:
					enquiry_form_save.is_email    = True
				else:
					enquiry_form_save.is_email    = False

				if 'SMS' in contact_platform_list:
					enquiry_form_save.is_sms      = True
				else:
					enquiry_form_save.is_sms      = False

				#APPEND MR / MS TO NAME
				customer_name = enquiry_form_save.name
				customer_name = customer_name.lower()

				if enquiry_form_save.gender == 'MALE':
					prefix_list = ['mr.','mr']
					for prefix in prefix_list:
						
						prefix_exists = customer_name.startswith(prefix)

						if prefix_exists == False :
							if customer_name.startswith('dr.') == True or customer_name.startswith('dr') == True :
								enquiry_form_save.name = customer_name.title()
							else:	
								enquiry_form_save.name = 'Mr. '+customer_name
						else:
							enquiry_form_save.name = customer_name.title()													

				elif enquiry_form_save.gender == 'FEMALE':
					prefix_list = ['ms.','ms']
					for prefix in prefix_list:
						
						prefix_exists = customer_name.startswith(prefix)

						if prefix_exists == False :
							if customer_name.startswith('dr.') == True or customer_name.startswith('dr') == True or customer_name.startswith('mrs.') == True or customer_name.startswith('mrs') == True:
								enquiry_form_save.name = customer_name.title()
							else:	
								enquiry_form_save.name = 'Ms. '+customer_name
						else:
							enquiry_form_save.name = customer_name.title()

				else:
					pass

				enquiry_form_save.save()
				messages.success(request,"Customer Details Succesfully updated")

			else:
				messages.error(request,get_error(enquiry_form))

				address_form = AddressForm()

				try:
					governorates = Governorate.objects.filter(is_active=True)
				except:
					governorates = None

				return render(request,'common/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,'governorates':governorates})
		
		if action_mode == 'add_address':
			address_form = AddressForm(request.POST)

			if address_form.is_valid():
				address_form_save                  = address_form.save(commit=False)
				address_form_save.customer         = enquiry_user
				address_form_save.currently_active = True

				#string check
				block_text = address_form_save.block
				floor_text = address_form_save.floor
				street_text = address_form_save.street
				avenue_text = address_form_save.avenue

				is_block = block_text.find("Block")
				is_street = street_text.find("Street")

				if floor_text:
					is_floor = floor_text.find("Floor")

					if is_floor == -1 :
						floor_text += ' '
						floor_text += 'Floor'
						address_form_save.floor = floor_text
					else:
						pass
				else: 
					pass

				if avenue_text:
					is_avenue = avenue_text.find("Avenue")

					if is_avenue == -1 :
						avenue_text += ' '
						avenue_text += 'Avenue'
						address_form_save.avenue = avenue_text
					else:
						pass
				else:
					pass

				print(block_text,is_block,"blockkk")

				if is_block == -1 :
					block_text += ' '
					block_text += 'Block'
					address_form_save.block = block_text
				else:
					pass

				if is_street == -1 :
					street_text += ' '
					street_text += 'Street'
					address_form_save.street = street_text
				else:
					pass

				address_form_save.save()

				messages.success(request,"New Address Succesfully Added")

			else:
				messages.error(request,get_error(address_form))

				enquiry_form = UserProfileForm(request.FILES or None,instance=enquiry_user)

				return render(request,'common/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,})

		if action_mode == 'edit_address':
			address_id = request.POST.get('address')
			address = Address.objects.select_related('customer').get(id=address_id)

			address_form = AddressForm(request.POST,instance=address)
			if address_form.is_valid():
				address_form_save                  = address_form.save(commit=False)
				address_form_save.currently_active = True

				#string check
				block_text = address_form_save.block
				floor_text = address_form_save.floor
				street_text = address_form_save.street
				avenue_text = address_form_save.avenue

				is_block = block_text.find("Block")
				is_street = street_text.find("Street")

				if floor_text:
					is_floor = floor_text.find("Floor")

					if is_floor == -1 :
						floor_text += ' '
						floor_text += 'Floor'
						address_form_save.floor = floor_text
					else:
						pass
				else: 
					pass

				if avenue_text:
					is_avenue = avenue_text.find("Avenue")

					if is_avenue == -1 :
						avenue_text += ' '
						avenue_text += 'Avenue'
						address_form_save.avenue = avenue_text
					else:
						pass
				else:
					pass

				print(block_text,is_block,"blockkk")

				if is_block == -1 :
					block_text += ' '
					block_text += 'Block'
					address_form_save.block = block_text
				else:
					pass

				if is_street == -1 :
					street_text += ' '
					street_text += 'Street'
					address_form_save.street = street_text
				else:
					pass

				address_form_save.save()

				messages.success(request,"Address Updated Succesfully")

			else:
				messages.error(request,get_error(address_form))

				enquiry_form = UserProfileForm(request.FILES or None,instance=address.customer)

				return render(request,'agent/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,})			
		
		return redirect('common_items:existingenquiry',enquiry_id)

class MakeEvaluation(IsAuthenticated,View):
	def get(self,request,enquiry_id):
		
		tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

		current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
		
		if current_blc_starting == int(str(tracking_no)[:6]):
			new_tracking_no = int(tracking_no)+1
			evaluation_no   = 'BLC'+str(new_tracking_no)
		else:
			evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
			tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

		existing_user_note = request.POST.get('agent_notes',None)

		#Create New Evaluation
		new_evaluation = Evaluation.objects.create(evaluation_id=evaluation_no,tracking_no=int(tracking_no)+1,call_attender=request.user,customer_id=enquiry_id,quatation_expiry_date=timezone.now()+timedelta(14))

		return redirect('common_items:assignevaluator',enquiry_id,new_evaluation.id)


class AssignEvaluator(IsAuthenticated,View):
	def get(self,request,enquiry_id,evaluation_id):

		evaluation_form 		    = EvaluationDetailsForm(enquiry_user_id=enquiry_id,evaluation_id=evaluation_id,)

		#Evaluation details of each evaluator for evaluation table
		evaluation_calendar_date	= request.GET.get('evaluation_calendar_date')

		try:
			evaluation_date = datetime.strptime(evaluation_calendar_date,'%d-%m-%Y')
		except:
			evaluation_date = timezone.now()

		try:
			evaluation_details		  = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related(Prefetch('evaluator_evaluation',queryset=EvaluationDetails.objects.filter(is_active=True,proposed_time__contains=evaluation_date.date()),to_attr='evaluation_details'))
		except:
			evaluation_details 		  = None

		assigned_addresses = EvaluationDetails.objects.filter(is_active=True,evaluation_id=evaluation_id).values_list('address')
		active_addresses   = Address.objects.filter(is_active=True,customer_id=enquiry_id,currently_active=True).exclude(id__in=assigned_addresses)

		evaluators 		   = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR')

		return render(request,'common/enquiry/assign_evaluator.html',{'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'enquiryid':enquiry_id,'evaluation_id':evaluation_id,'evaluation_form':evaluation_form,"active_addresses":active_addresses,"evaluators":evaluators,})

	def post(self,request,enquiry_id,evaluation_id):
		evaluation_form  = EvaluationDetailsForm(enquiry_user_id=enquiry_id,evaluation_id=evaluation_id,data=request.POST)

		action_mode    = request.POST.get('action_type')


		if action_mode == 'add':

			evaluation = Evaluation.objects.filter(id=evaluation_id).first()
			if evaluation.customer.gender == 'MALE':
				title = 'Mr.'
			else:
				title = 'Ms.'

			mobile = evaluation.customer.mobile_number

			#Save Evaluation Details
			if evaluation_form.is_valid():
				evaluation_form_save              = evaluation_form.save(commit=False)

				proposed_date                     = request.POST.get('proposed_date')
				proposed_time                     = request.POST.get('proposed_time')
				
				converted_proposed_time           = datetime.strptime(proposed_date+" "+proposed_time,'%d-%m-%Y %I:%M %p')

				evaluation_form_save.proposed_time   = converted_proposed_time
				evaluation_form_save.evaluation_id   = evaluation_id
				evaluation_form_save.save()

				messages.success(request,"Evaluation Details Succesfully Completed")

				#address check for floor,avenue None
				if evaluation_form_save.address.floor == None and evaluation_form_save.address.avenue == None:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]
				
				elif evaluation_form_save.address.floor == None:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.avenue, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]
				
				elif evaluation_form_save.address.avenue == None:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.floor, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]
				
				else:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.floor, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.avenue, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]

				separator = ", "

				if evaluation.customer.is_sms == True:
				
					url = "https://smsapi.future-club.com/fccsms.aspx"

					if evaluation.customer.sms_preference == 'ENGLISH':

						message = "Dear Customer , We have confirmed your Evaluation Appointment. "+ title +" "+evaluation_form_save.evaluator.name+" will be visiting you on "+str(evaluation_form_save.proposed_time)+" at  "+ separator.join(address_list) +". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."

						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"L"}

					else:

						message = "عزيزينا العميل تم تأكيد موعد المعاينة الخاص بك.  "+ title +" "+evaluation_form_save.evaluator.name+" سيقوم بالزيارة في "+str(evaluation_form_save.proposed_time)+" في "+ separator.join(address_list)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+  شكراً لاختياركم بليتش لخدمات التنظيف"

						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"A"}
					
					headers = {
						'cache-control': "no-cache"
					}

					response = requests.request("GET", url, headers=headers, params=querystring)
				else:
					pass

				#Email Send
				msg_html = render_to_string('email/evaluation_task.html',{'evaluation_form_save':evaluation_form_save})
				msg      = EmailMultiAlternatives('Evaluation Task', '', 'notification@bleach-kw.com', [evaluation_form_save.evaluator.email])
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)
			else:
				messages.error(request,get_error(evaluation_form))

		selected_date = request.GET.get('evaluation_calendar_date') or ''

		return redirect('/common/assignevaluator/'+enquiry_id+'/'+evaluation_id+'?evaluation_calendar_date='+selected_date)
		
class AssignEvaluator(IsAuthenticated,View):
	def get(self,request,enquiry_id,evaluation_id):

		evaluation_form 		    = EvaluationDetailsForm(enquiry_user_id=enquiry_id,evaluation_id=evaluation_id,)

		#Evaluation details of each evaluator for evaluation table
		evaluation_calendar_date	= request.GET.get('evaluation_calendar_date')

		try:
			evaluation_date = datetime.strptime(evaluation_calendar_date,'%d-%m-%Y')
		except:
			evaluation_date = timezone.now()

		try:
			evaluation_details		  = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related(Prefetch('evaluator_evaluation',queryset=EvaluationDetails.objects.filter(is_active=True,proposed_time__contains=evaluation_date.date()),to_attr='evaluation_details'))
		except:
			evaluation_details 		  = None

		assigned_addresses = EvaluationDetails.objects.filter(is_active=True,evaluation_id=evaluation_id).values_list('address')
		active_addresses   = Address.objects.filter(is_active=True,customer_id=enquiry_id,currently_active=True).exclude(id__in=assigned_addresses)

		evaluators 		   = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR')

		return render(request,'common/enquiry/assign_evaluator.html',{'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'enquiryid':enquiry_id,'evaluation_id':evaluation_id,'evaluation_form':evaluation_form,"active_addresses":active_addresses,"evaluators":evaluators,})

	def post(self,request,enquiry_id,evaluation_id):
		evaluation_form  = EvaluationDetailsForm(enquiry_user_id=enquiry_id,evaluation_id=evaluation_id,data=request.POST)

		action_mode    = request.POST.get('action_type')


		if action_mode == 'add':

			evaluation = Evaluation.objects.filter(id=evaluation_id).first()
			if evaluation.customer.gender == 'MALE':
				title = 'Mr.'
			else:
				title = 'Ms.'

			mobile = evaluation.customer.mobile_number

			#Save Evaluation Details
			if evaluation_form.is_valid():
				evaluation_form_save              = evaluation_form.save(commit=False)

				proposed_date                     = request.POST.get('proposed_date')
				proposed_time                     = request.POST.get('proposed_time')
				
				converted_proposed_time           = datetime.strptime(proposed_date+" "+proposed_time,'%d-%m-%Y %I:%M %p')

				evaluation_form_save.proposed_time   = converted_proposed_time
				evaluation_form_save.evaluation_id   = evaluation_id
				evaluation_form_save.save()

				messages.success(request,"Evaluation Details Succesfully Completed")

				#address check for floor,avenue None
				if evaluation_form_save.address.floor == None and evaluation_form_save.address.avenue == None:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]
				
				elif evaluation_form_save.address.floor == None:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.avenue, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]
				
				elif evaluation_form_save.address.avenue == None:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.floor, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]
				
				else:
					address_list = [evaluation_form_save.address.apartment, evaluation_form_save.address.floor, evaluation_form_save.address.street, evaluation_form_save.address.building, evaluation_form_save.address.avenue, evaluation_form_save.address.block, evaluation_form_save.address.area.name, evaluation_form_save.address.governorate.name]

				separator = ", "

				if evaluation.customer.is_sms == True:
				
					url = "https://smsapi.future-club.com/fccsms.aspx"

					if evaluation.customer.sms_preference == 'ENGLISH':

						message = "Dear Customer , We have confirmed your Evaluation Appointment. "+ title +" "+evaluation_form_save.evaluator.name+" will be visiting you on "+str(evaluation_form_save.proposed_time)+" at  "+ separator.join(address_list) +". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."

						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"L"}

					else:

						message = "عزيزينا العميل تم تأكيد موعد المعاينة الخاص بك.  "+ title +" "+evaluation_form_save.evaluator.name+" سيقوم بالزيارة في "+str(evaluation_form_save.proposed_time)+" في "+ separator.join(address_list)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+  شكراً لاختياركم بليتش لخدمات التنظيف"

						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"A"}
					
					headers = {
						'cache-control': "no-cache"
					}

					response = requests.request("GET", url, headers=headers, params=querystring)
				else:
					pass

				#Email Send
				msg_html = render_to_string('email/evaluation_task.html',{'evaluation_form_save':evaluation_form_save})
				msg      = EmailMultiAlternatives('Evaluation Task', '', 'notification@bleach-kw.com', [evaluation_form_save.evaluator.email])
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)
			else:
				messages.error(request,get_error(evaluation_form))

		selected_date = request.GET.get('evaluation_calendar_date') or ''

		return redirect('/common/assignevaluator/'+enquiry_id+'/'+evaluation_id+'?evaluation_calendar_date='+selected_date)

class MakeQuatationBase(IsAuthenticated,View):
	def get(self,request,enquiry_id):
		#create Main Evaluation
		tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

		current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
		
		if current_blc_starting == int(str(tracking_no)[:6]):
			new_tracking_no = int(tracking_no)+1
			evaluation_no   = 'BLC'+str(new_tracking_no)
		else:
			evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
			tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')
		
		evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no,customer_id=enquiry_id,call_attender=request.user,quatation_expiry_date=timezone.now()+timedelta(14))
		

		#create evaluation details
		try:
			addresses = Address.objects.filter(is_active=True,customer_id=enquiry_id,currently_active=True)
		except:
			addresses = None

		evaluation_details_array = []
		for address in addresses:
			evaluation_details_array.append(EvaluationDetails(evaluation=evaluation,address=address))
		EvaluationDetails.objects.bulk_create(evaluation_details_array)

		return redirect('common_items:makequatation1',enquiry_id,evaluation.id)

class MakeQuatationPhase1(IsAuthenticated,View):

	def get(self,request,enquiry_id,evaluation_id):
		enquiry_user    	  = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(id=enquiry_id)
		
		try:
			evaluation = Evaluation.objects.prefetch_related(Prefetch('booking_evaluation',queryset=CustomerBooking.objects.filter(is_active=True),to_attr='bookings')).get(id=evaluation_id)
		except:
			evaluation = None		
	
		try:
			evaluation_details = EvaluationDetails.objects.filter(is_active=True,evaluation=evaluation).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True,cleaning_policy='SUBSCRIPTION'),to_attr='evaluationbooks'))
		except:
			evaluation_details = None

		#allow submition	
		evaluation_details_count          = evaluation_details.count()
		evaluation_details_completed_count= evaluation_details.filter(status='EVALUATED').count()
		if evaluation_details_count==evaluation_details_completed_count:
			allow_submit = True
		else:
			allow_submit = False				

		return render(request,'common/enquiry/phase1quatation.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit})	

	def post(self,request,enquiry_id,evaluation_id):
		
		action = request.POST.get('action_type',None)
		if action == 'cancel' :
			evaluation_detail_id =request.POST.get('evaluation_detail')
			cancel_reason = request.POST.get('cancellation_reason')
			evaluation_detail = EvaluationDetails.objects.filter(id=int(evaluation_detail_id)).first()
			evaluation_detail.status = 'CANCELLED'
			evaluation_detail.evaluation_cancel_reason = cancel_reason
			evaluation_detail.save()
			messages.success(request,"Evaluation Cancelled !!")
			return redirect('common_items:makequatation1', enquiry_id,evaluation_id)


        ###SUBMIT QUATATION
		payment_method          = request.POST.get('payment_method')
		before_cleaning_amount	= float(request.POST.get('before_cleaning_amount')or 0.000)
		after_cleaning_amount	= float(request.POST.get('after_cleaning_amount')or 0.000)
		discount                = float(request.POST.get('discount')or 0.000)
		total_cost              = float(request.POST.get('total_amount')or 0.000)


		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,quatation_status='PENDING',before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount,total_cost=total_cost,discount=discount)

		##advance payment check
		is_advance              = request.POST.get('is_advance')
		if is_advance:
			subscription_topay      = request.POST.get('subscription_topay')
			Order.objects.filter(evaluation__id=evaluation_id,is_active=True).update(total_amount=total_cost,remining_amount=total_cost,subscription_topay=subscription_topay,is_advance=True,subscription_topay_date=timezone.now())
		else:
			Order.objects.filter(evaluation__id=evaluation_id,is_active=True).update(total_amount=total_cost,remining_amount=total_cost)

		#sms integration
		order             = Order.objects.filter(evaluation__id=evaluation_id,is_active=True).prefetch_related(Prefetch('evaluation__booking_evaluation',queryset=CustomerBooking.objects.filter(is_active=True,booking_type='CLEANINGBOOKING'),to_attr='customerbooking')).first()
		evaluation        = order.evaluation
		evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
		
		if evaluationdetails.evaluator:
			evaluator = evaluationdetails.evaluator.name
		else:
			evaluator = evaluation.call_attender.name

		evaluationbooks = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True),to_attr='sections'))
		evaluationbook  = evaluationbooks.first()
		language        = evaluation.customer.sms_preference

		messages.success(request,"Quotation Submitted Succesfully")	
		
		address = evaluationdetails.address

		#address check for floor,avenue None
		if address.floor == None and address.avenue == None:
			address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
		
		elif address.floor == None:
			address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
		
		elif address.avenue == None:
			address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
		
		else:
			address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

		separator = ", "

		#SEPERATE MSG FOR LET CUSTOMER BOOKING AND DIRECT BOOKING
		if evaluation.customer.is_sms == True:

			if evaluation.customerbooking:

				url     = "https://smsapi.future-club.com/fccsms.aspx"

				sms_url = "https://my.bleachkw.com/customer/booking/invoice/paw"+str(evaluation.evaluation_id [3:14])+str(evaluation.customer.username)

				if language == 'ENGLISH':

					message = "Dear Customer , We have completed your Site Evaluation.You can Book your Slote through "+sms_url+".For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

				else:

					message = "عزيزي العميل ، لقد أكملنا تقييم الموقع الخاص بك.يمكنك حجز الكسلان الخاص بك من خلال "+sms_url+". للحصول على أي مساعدة يرجى الاتصال بنا على +9651882707. شكرا لاختيارك بليتش الكويت."

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
				
				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)

			else:
				messages.success(request,"Direct BOOKED")

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if evaluation.payment_method == 'SUBSCRIPTION':
					smsurl = "https://my.bleachkw.com/customer/subscription/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+""
				else:
					smsurl = "https://my.bleachkw.com/customer/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+""

				if language == 'ENGLISH':
					print(str(evaluation.id),str(evaluation.evaluation_id),str(evaluation.total_cost),str(evaluation.quatation_expiry_date),str(evaluation.customer.username),str(evaluation.tracking_no),"trerr")

					message = "Dear Customer, Please find the Quotation against the cleaning at "+separator.join(address_list)+" here "+smsurl+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
				
				else:
					message = "عزيزنا العميل نرجوا الاطلاع على عرض سعر خدمات التنظيف المطلوبة في "+separator.join(address_list)+" "+smsurl+"  لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

				headers = {
					'cache-control': "no-cache"
				}
				
				response = requests.request("GET", url, headers=headers, params=querystring)

		else:
			pass



		#Different Email FOR LET CUSTOMER BOOKING AND DIRECT BOOKING
		if evaluation.customer.is_email == True :
			if evaluation.customerbooking:				
				msg_html = render_to_string('email/invoice.html',{"invoice":order,"address_list":separator.join(address_list),"evaluationbooks":evaluationbooks})
				msg = EmailMultiAlternatives('Bleach Invoice', '', 'notification@bleach-kw.com', [evaluation.customer.email])
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)
			else:
				msg_html = render_to_string('email/quatation.html',{"evaluator":evaluator,"evaluation":evaluation,"evaluationbooks":evaluationbooks,"address_list":separator.join(address_list)})
				msg = EmailMultiAlternatives('Bleach Quotation', '', 'notification@bleach-kw.com', [evaluation.customer.email])
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)
				
		
		if request.user.user_type == 'AGENT':
			return redirect('agent:agentdash-board')
		elif request.user.user_type == 'EVALUATOR':
			return redirect('evaluator:evaluatordash-board')
		else:
			return redirect('booking-officer:bookingofficerdash-board')

class MakeQuatationPhase2(IsAuthenticated,View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	def get(self,request,evaluation_detail_id):

		evaluation_details = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=evaluation_detail_id)

		try:
			service_types = ServiceType.objects.filter(is_active=True)
		except:	
			service_types = None

		try:
			area_types = AreaType.objects.filter(is_active=True)
		except:
			area_types = None

		return render(request,'common/enquiry/phase2quatation.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,})

	def post(self,request,evaluation_detail_id):

		service_formset       = self.service_formset_define(request.POST)
		evaluation_details    = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=evaluation_detail_id)
		
		if service_formset.is_valid() : 

			form_count = 0
			#create order					
			new_order = Order.objects.get_or_create(evaluation=evaluation_details.evaluation,order_no=evaluation_details.evaluation.evaluation_id)	
				
			order_schedule_array          = []
			#Save Service Form
			for service_form in service_formset:
				
				if service_form.is_valid():
					service_form_save 					    = service_form.save(commit=False)
					service_form_save.evaluation_details_id = evaluation_detail_id
					service_form_save.save()

					#To Save Media
					medias = request.FILES.getlist('media'+str(form_count))
					if not medias==['']:
						for media in medias:
							EvaluationMedia.objects.create(
							        evaluation_book=service_form_save,
							        media=media,
							        media_type='PHOTO',
									taken_status='AGENT_TAKEN'
							        )

					#for updating cost details in evaluation details
					cost     = float(request.POST.get('form-'+str(form_count)+'-estimated_cost')) 
					discount = float(request.POST.get('form-'+str(form_count)+'-discount'))
					total    = float(request.POST.get('form-'+str(form_count)+'-total_cost'))

					#for creating cleaning schedules and corresponding cleanings

					cleaning_policy = request.POST.get('form-'+str(form_count)+'-cleaning_policy')
					start_time      = request.POST.get('form-'+str(form_count)+'-tendative_time')
					cleaning_hours  = request.POST.get('form-'+str(form_count)+'-cleaning_hours')

					if cleaning_policy == 'SUBSCRIPTION':
						tendative_dates = request.POST.get('form-'+str(form_count)+'-tendative_dates').split(',')
						
						for date in tendative_dates:
							start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
							end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours)) 
							
							order_schedule_array.append(OrderScheduler(order=new_order[0],status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=service_form_save))	
							

						updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total,status='EVALUATED')
						updated_evaluation         = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total)
						update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')+total,remining_amount=F('remining_amount')+total)
					else:
						tendative_dates = request.POST.get('form-'+str(form_count)+'-tendative_date').split(',')
						
						for date in tendative_dates:
							start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
							end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours)) 	

							order_schedule_array.append(OrderScheduler(order=new_order[0],status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=service_form_save))
						

						updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total,status='EVALUATED')
						updated_evaluation 		   = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total)	
						update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')+total,remining_amount=F('remining_amount')+total)
					#to save sections
					no_of_sections         = int(request.POST.get('form-'+str(form_count)+'-section_counter'))
					section_array          = []
					for i in range(no_of_sections):
						section_name  = request.POST.get('form'+str(form_count)+'_section'+str(i))
						category      = request.POST.get('form'+str(form_count)+'_category'+str(i))
						dirt_level    = request.POST.get('form'+str(form_count)+'_dirt_level'+str(i))
						quantity      = request.POST.get('form'+str(form_count)+'_quantity'+str(i))
						size          = request.POST.get('form'+str(form_count)+'_size'+str(i))
						unit          = request.POST.get('form'+str(form_count)+'_unit'+str(i))
						age           = request.POST.get('form'+str(form_count)+'_age'+str(i))
						floor         = request.POST.get('form'+str(form_count)+'_floor'+str(i))
						apartment     = request.POST.get('form'+str(form_count)+'_apartment'+str(i))
						room          = request.POST.get('form'+str(form_count)+'_room'+str(i))
						wall_type     = request.POST.get('form'+str(form_count)+'_walltype'+str(i))
						ceiling_type  = request.POST.get('form'+str(form_count)+'_ceilingtype'+str(i))
						floor_type    = request.POST.get('form'+str(form_count)+'_floortype'+str(i))
						material      = request.POST.get('form'+str(form_count)+'_material'+str(i))
						colour        = request.POST.get('form'+str(form_count)+'_colour'+str(i))
						cause_of_stain=request.POST.get('form'+str(form_count)+'_staincause'+str(i))
						section_cost  = request.POST.get('form'+str(form_count)+'_sectioncost'+str(i))
						print("hereeeeeeeeeeeeeeeeeeeeeee")
						print(wall_type)
						print(ceiling_type)
						print(floor_type)
						try:
							section_name_arabic =Translator().translate(section_name,src='en', dest='ar').text
						except:
							section_name_arabic = section_name

						#save section
						if cleaning_policy == 'SUBSCRIPTION':
							section = EvaluationBookSection.objects.create(evaluation_book=service_form_save,section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=len(tendative_dates),section_net_cost=len(tendative_dates)*float(section_cost))
						else:
							section = EvaluationBookSection.objects.create(evaluation_book=service_form_save,section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=1,section_net_cost=section_cost)

						#to save keynotes
						try:
							no_of_keynotes = int(request.POST.get('form'+str(form_count)+'_section'+str(i)+'-keynote_counter'))
						except:
							no_of_keynotes = None
							
						keynote_array = []
						if no_of_keynotes:
							for j in range(no_of_keynotes):
								keynote = request.POST.get('form'+str(form_count)+'_section'+str(i)+'_keynote'+str(j))
								quantity= request.POST.get('form'+str(form_count)+'_section'+str(i)+'_quantity'+str(j))
								if keynote and quantity:
									keynote_array.append(EvaluationSectionKeynote(evaluation_section=section,sub_area=keynote,quantity=quantity))
							#bulk_create keynote
							EvaluationSectionKeynote.objects.bulk_create(keynote_array)

				form_count = form_count+1
			#bulk_create order schedules
			now = timezone.now()
			OrderScheduler.objects.bulk_create(order_schedule_array)	

			messages.success(request,"Services Succesfully Added")

		else:
			if not service_formset.is_valid():
				messages.error(request,"An Error Occured")

			try:
				service_types = ServiceType.objects.filter(is_active=True)
			except:	
				service_types = None

			try:
				area_types = AreaType.objects.filter(is_active=True)
			except:
				area_types = None
			
			if request.user.user_type == 'EVALUATOR':
				return render(request,'common/enquiry/phase2quatation.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,})	
			if request.user.user_type == 'AGENT':
				return render(request,'common/enquiry/phase2quatation.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'area_types':area_types,'service_types':service_types,})
			if request.user.user_type == 'BOOKINGOFFICER':
				return render(request,'common/enquiry/phase2quatation.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'area_types':area_types,'service_types':service_types,})
	
		
		return redirect('common_items:makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)


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
		evaluation_details_count          = evaluation_details.count()
		evaluation_details_completed_count= evaluation_details.filter(status='EVALUATED').count()
		if evaluation_details_count==evaluation_details_completed_count:
			allow_submit = True
		else:
			allow_submit = False				

		return render(request,'common/enquiry/phase1quatationedit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit})	

	def post(self,request,enquiry_id,evaluation_id):
		
		payment_method = request.POST.get('payment_method')
		before_cleaning_amount	= float(request.POST.get('before_cleaning_amount')or 0)
		after_cleaning_amount	= float(request.POST.get('after_cleaning_amount')or 0)

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,quatation_status='PENDING',before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)

		#sms integration
		evaluation = Evaluation.objects.filter(id=evaluation_id,is_active=True).first()
		evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
		evaluationbook = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).first()
		language = evaluation.customer.sms_preference

		messages.success(request,"Quotation Edited Succesfully")

		address = evaluationdetails.address

		#address check for floor,avenue None
		if address.floor == None and address.avenue == None:
			address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
		
		elif address.floor == None:
			address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
		
		elif address.avenue == None:
			address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
		
		else:
			address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

		separator = ", "	

		if evaluation.customer.is_sms == True:

			url = "https://smsapi.future-club.com/fccsms.aspx"

			if evaluation.payment_method == 'SUBSCRIPTION':
				smsurl = "https://my.bleachkw.com/customer/subscription/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+""
			else:
				smsurl = "https://my.bleachkw.com/customer/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+""

			if evaluation.customer.sms_preference == 'ENGLISH':

				message = "Dear Customer, Please find the Revised Quotation against the order number "+str(evaluation.evaluation_id)+"  here "+smsurl+" . Order Number : "+ str(evaluation.evaluation_id) +". Service Type(s) : "+ evaluationbook.service_type.name +", Address(s) : "+separator.join(address_list)+", Cost : "+ str(evaluation.total_cost) +", Due Date : "+ str(evaluation.quatation_expiry_date) +". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

			else:
				message = "عزيزنا العميل نرجوا الاطلاع على عرض السعر المعدّل للطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط "+smsurl+" .رقم الطلب: "+ str(evaluation.evaluation_id) +"الخدمة: "+ evaluationbook.service_type.name +"العنوان: "+separator.join(address_list)+"السعر: "+ str(evaluation.total_cost) +" KDتاريخ الخدمة: "+ str(evaluation.quatation_expiry_date) +"لأي استفسارات يمكنكم التواصل معنا على . 9651882707+  شكراً لاختياركم بليتش لخدمات التنظيف"
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

			headers = {
				'cache-control': "no-cache"
			}
			
			response = requests.request("GET", url, headers=headers, params=querystring)

			print(response.text,"respo")
		else:
			pass

		if request.user.user_type == 'EVALUATOR':
			return redirect('evaluator:evaluatordash-board')
		if request.user.user_type == 'AGENT':
			return redirect('agent:agentdash-board')
		if request.user.user_type == 'BOOKINGOFFICER':
			return redirect('booking-officer:bookingofficerdash-board')


class MakeQuatationPhase2Edit(IsAuthenticated,View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	service_formset_store     = modelformset_factory(EvaluationBook,QuatationServiceForm)
	def get(self,request,evaluation_detail_id):

		evaluation_details = EvaluationDetails.objects.select_related('evaluation__customer','address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationbookmedias'),Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'),Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='booksections')),to_attr='evaluationbooks')).get(is_active=True,id=evaluation_detail_id)
		
		try:
			service_types = ServiceType.objects.filter(is_active=True)
		except:	
			service_types = None

		try:
			area_types = AreaType.objects.filter(is_active=True)
		except:
			area_types = None

		try:
			cleaning_sections = CleaningSection.objects.filter(is_active=True)
		except:
			cleaning_sections = None

		return render(request,'common/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

	def post(self,request,evaluation_detail_id):
		
		evaluation_details 	  = EvaluationDetails.objects.select_related('evaluation__customer','address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationbookmedias'),Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'),Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='booksections')),to_attr='evaluationbooks')).get(is_active=True,id=evaluation_detail_id)		
		service_formset       = self.service_formset_store(request.POST)
		
		if service_formset.is_valid() : 
			form_count = 0
			#old order update					
			old_order = Order.objects.get(evaluation=evaluation_details.evaluation)	
				
			order_schedule_array          = []
			#Save Service Form
			for service_form in service_formset:
				if service_form.is_valid():

					old_form_id                                 = request.POST.get('editform'+str(form_count))
					if old_form_id:
						old_form_id								= int(old_form_id)
						very_old_book                           = EvaluationBook.objects.get(id=old_form_id)		                   
						
						#update book
						EvaluationBook.objects.filter(id=service_form['id'].value()).update(cleaning_policy=service_form['cleaning_policy'].value(),service_type=service_form['service_type'].value(),area_type=service_form['area_type'].value(),cleaning_method=service_form['cleaning_method'].value(),location_type=service_form['location_type'].value(),number_of_cleaners=service_form['number_of_cleaners'].value(),estimated_cost=service_form['estimated_cost'].value(),discount=service_form['discount'].value(),total_cost=service_form['total_cost'].value(),cleaning_hours=service_form['cleaning_hours'].value(),evaluator_note=service_form['evaluator_note'].value())
						
						#To Save Media
						medias = request.FILES.getlist('newform-'+str(form_count)+'-media')
						if not medias==['']:
							for media in medias:
								EvaluationMedia.objects.create(
								        evaluation_book_id=old_form_id,
								        media=media,
								        media_type='PHOTO',
								        taken_status='AGENT_TAKEN'
								        )

						#for updating cost details in evaluation details and evaluation
						cost     = float(request.POST.get('form-'+str(form_count)+'-estimated_cost')) 
						discount = float(request.POST.get('form-'+str(form_count)+'-discount'))
						total    = float(request.POST.get('form-'+str(form_count)+'-total_cost'))

						#for creating cleaning schedules and corresponding cleanings
						cleaning_policy = request.POST.get('form-'+str(form_count)+'-cleaning_policy')
						start_time      = request.POST.get('form-'+str(form_count)+'-tendative_time')
						cleaning_hours  = request.POST.get('form-'+str(form_count)+'-cleaning_hours')

						old_book      =  EvaluationBook.objects.get(id=old_form_id)

						if cleaning_policy == 'SUBSCRIPTION':
							tendative_dates = request.POST.get('form-'+str(form_count)+'-tendative_dates').split(',')
							for date in tendative_dates:
								start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
								end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours)) 
								order_schedule_array.append(OrderScheduler(order=old_order,status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=old_book))	
								

							updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total,status='EVALUATED')
							updated_evaluation         = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total)
							update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')-very_old_book.total_cost+total,remining_amount=F('remining_amount')-very_old_book.total_cost+total)	
						else:
							tendative_dates = request.POST.get('form-'+str(form_count)+'-tendative_date').split(',')
							for date in tendative_dates:
								start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
								end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours)) 

								order_schedule_array.append(OrderScheduler(order=old_order,status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=old_book))

							updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total,status='EVALUATED')
							updated_evaluation 		   = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total)
							update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')-very_old_book.total_cost+total,remining_amount=F('remining_amount')-very_old_book.total_cost+total)
						#to save and update sections
						no_of_sections         = int(request.POST.get('form-'+str(form_count)+'-section_counter'))		
						section_array          = []
						for i in range(no_of_sections):
							section_name  = request.POST.get('form'+str(form_count)+'_section'+str(i))
							category      = request.POST.get('form'+str(form_count)+'_category'+str(i))
							dirt_level    = request.POST.get('form'+str(form_count)+'_dirt_level'+str(i))
							quantity      = request.POST.get('form'+str(form_count)+'_quantity'+str(i))
							size          = request.POST.get('form'+str(form_count)+'_size'+str(i))
							unit          = request.POST.get('form'+str(form_count)+'_unit'+str(i))
							age           = request.POST.get('form'+str(form_count)+'_age'+str(i))
							floor         = request.POST.get('form'+str(form_count)+'_floor'+str(i))
							apartment     = request.POST.get('form'+str(form_count)+'_apartment'+str(i))
							room          = request.POST.get('form'+str(form_count)+'_room'+str(i))
							wall_type     = request.POST.get('form'+str(form_count)+'_walltype'+str(i))
							ceiling_type  = request.POST.get('form'+str(form_count)+'_ceilingtype'+str(i))
							floor_type    = request.POST.get('form'+str(form_count)+'_floortype'+str(i))
							material      = request.POST.get('form'+str(form_count)+'_material'+str(i))
							colour        = request.POST.get('form'+str(form_count)+'_colour'+str(i))
							cause_of_stain=request.POST.get('form'+str(form_count)+'_staincause'+str(i))
							section_cost  = request.POST.get('form'+str(form_count)+'_sectioncost'+str(i))
							
							old_section_id=request.POST.get('editform'+str(form_count)+'_section'+str(i)) 
							
							try:
								section_name_arabic =Translator().translate(section_name,src='en', dest='ar').text
							except:
								section_name_arabic = section_name
							
							if old_section_id:
								#edit section
								if cleaning_policy == 'SUBSCRIPTION':
									section = EvaluationBookSection.objects.filter(id=old_section_id).update(section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=len(tendative_dates),section_net_cost=len(tendative_dates)*float(section_cost))
								else:
									section = EvaluationBookSection.objects.filter(id=old_section_id).update(section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=1,section_net_cost=section_cost)
							else:
								#save section
								if cleaning_policy == 'SUBSCRIPTION':
									section = EvaluationBookSection.objects.create(evaluation_book=old_book,section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=len(tendative_dates),section_net_cost=len(tendative_dates)*float(section_cost))
								else:
									section = EvaluationBookSection.objects.create(evaluation_book=old_book,section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=1,section_net_cost=section_cost)

							#to save and update keynotes
							try:
								no_of_keynotes = int(request.POST.get('form'+str(form_count)+'_section'+str(i)+'-keynote_counter'))
							except:
								no_of_keynotes = None

							keynote_array = []
							if no_of_keynotes:
								for j in range(no_of_keynotes):
									old_keynote_id=request.POST.get('editform'+str(form_count)+'_section'+str(i)+'_keynote'+str(j))

									keynote = request.POST.get('form'+str(form_count)+'_section'+str(i)+'_keynote'+str(j))
									quantity= request.POST.get('form'+str(form_count)+'_section'+str(i)+'_quantity'+str(j))

									if old_keynote_id:
										if keynote and quantity:
											EvaluationSectionKeynote.objects.filter(id=old_keynote_id).update(id=old_keynote_id,sub_area=keynote,quantity=quantity)
									else:	
										if old_section_id and keynote and quantity:
											old_section = EvaluationBookSection.objects.get(id=old_section_id)
											keynote_array.append(EvaluationSectionKeynote(evaluation_section=old_section,sub_area=keynote,quantity=quantity))
										elif keynote and quantity:
											keynote_array.append(EvaluationSectionKeynote(evaluation_section=section,sub_area=keynote,quantity=quantity))
								#bulk_create keynote
								EvaluationSectionKeynote.objects.bulk_create(keynote_array)	
						
						#delete old order schedules
						OrderScheduler.objects.filter(order_scheduler_book_id=old_form_id).delete()

				form_count = form_count+1

			#bulk_create order schedules
			OrderScheduler.objects.bulk_create(order_schedule_array)

			messages.success(request,"Services Succesfully Updated")

		else:
			if not service_formset.is_valid():
				messages.error(request,"An Error Occured")

			try:
				service_types = ServiceType.objects.filter(is_active=True)
			except:	
				service_types = None

			try:
				area_types = AreaType.objects.filter(is_active=True)
			except:
				area_types = None

			try:
				cleaning_sections = CleaningSection.objects.filter(is_active=True)
			except:
				cleaning_sections = None

			if request.user.user_type == 'EVALUATOR':
				return render(request,'evaluator/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})	
			if request.user.user_type == 'AGENT':
				return render(request,'agent/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})
			if request.user.user_type == 'BOOKINGOFFICER':
				return render(request,'common/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})
			if request.user.user_type == 'SALESADMIN':
				return render(request,'salesadmin/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

		return redirect('common_items:makequatation1edit',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)

class Booking(IsAuthenticated,View):
	def get(self,request,evaluation_detail_id):
		return render(request,"booking/booking.html")

class Reorder(IsAuthenticated,View):
	def get(self,request):
		return render(request,"common/client/reorder.html")	

class EditcleaningTeam(IsAuthenticated,View):
	def get(self,request,scheduler_id):
		#shceduled order details
		order_schedule  = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections')).get(is_active=True,id=scheduler_id)
		start_at_datetime = order_schedule.start_at
		end_at_datetime   = order_schedule.end_at
		start_at_date     = (order_schedule.start_at+timedelta(hours=3)).date()
		end_at_date       = (order_schedule.end_at+timedelta(hours=3)).date()
		start_at_time     = (order_schedule.start_at+timedelta(hours=3)).time()
		end_at_time       = (order_schedule.end_at+timedelta(hours=3)).time()

		#same time schedules
		order_schedules = OrderScheduler.objects.filter(start_at=start_at_datetime,end_at=end_at_datetime,evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections'))

		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		#included shift cleaners & exclude absent cleaners & exclude active cleaners
		shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time)))).values_list('staff',flat=True)
		shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time)))).values_list('staff',flat=True)
		today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).values_list('staff',flat=True)
		super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time)) ).values_list('id',flat=True)
		super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time))).values_list('id',flat=True)

		absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
		absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
		cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

		#cleaning members and leader
		current_leader      = CleaningTeam.objects.select_related('team_leader','order_scheduler').get(order_scheduler=order_schedule).team_leader
		current_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler').filter(team__order_scheduler=order_schedule).exclude(member_id=current_leader.id)

		return render(request,'common/cleaning/cleaningteam_edit.html',{'order_schedule':order_schedule,'order_schedules':order_schedules,'cleaners':cleaners,'leaders':leaders,'current_leader':current_leader,'current_cleaners':current_cleaners,})		

	def post(self,request,scheduler_id):
		schedule_id         = request.POST.get('cleaningschedule_id')	
		assigned_leader     = request.POST.get('team_leader')
		assigned_cleaners   = request.POST.getlist('assigned_cleaner')

		#shceduled order details
		order_schedule      = OrderScheduler.objects.select_related('evaluation_details__evaluation').get(is_active=True,id=schedule_id)
		start_at_datetime   = order_schedule.start_at
		end_at_datetime     = order_schedule.end_at
		start_at_time       = (order_schedule.start_at+timedelta(hours=3)).time()
		end_at_time         = (order_schedule.end_at+timedelta(hours=3)).time()
		
		#same time schedules
		order_schedules 	= OrderScheduler.objects.filter(start_at=start_at_datetime,end_at=end_at_datetime,evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections'))
		
		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)
				
		#check cleaners	& leaders	
		check_cleaners      = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
		check_tl            = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=assigned_leader)

		#for multiple schedule
		if check_cleaners.count() >= len(assigned_cleaners) and check_tl:
			for order_schedule in order_schedules:
				#delete existing cleaners
				cleaners_to_be_deleted       = CleaningTeamMember.objects.filter(team__order_scheduler=order_schedule).delete()

				#update cleaning team leader
				cleaning_team                = CleaningTeam.objects.get(is_active=True,order_scheduler=order_schedule,team_leader__user_type='TEAMINCHARGE')
				cleaning_team.team_leader_id = assigned_leader
				cleaning_team.no_of_cleaners = len(assigned_cleaners)+1
				cleaning_team.save()

				#update cleaning team members
				assigned_cleaners_list   = []
				for cleaner in assigned_cleaners:
					assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member_id=cleaner,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member_id=assigned_leader,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				
				CleaningTeamMember.objects.bulk_create(assigned_cleaners_list)
					
				order_schedule.no_of_cleaners = len(assigned_cleaners_list)
				order_schedule.save()

			messages.success(request,"Cleaning Team Updated")
	
		else:
			messages.error(request,"Something Went Wrong !! Please Reupdate")
			return redirect('common_items:edit-cleaningteam',schedule_id)

		return redirect('common_items:orders')





class AssigncleaningTeam(IsAuthenticated,View):
	def get(self,request,scheduler_id):

		#shceduled order details
		order_schedule    = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')).annotate(kitchen_keynote=Sum( Case( When(keynotesections__sub_area='kitchen',then=1),default=0,output_field=IntegerField()))),to_attr='sections')).get(is_active=True,id=scheduler_id)
		start_at_datetime = order_schedule.start_at
		end_at_datetime   = order_schedule.end_at
		start_at_date     = (order_schedule.start_at+timedelta(hours=3)).date()
		end_at_date       = (order_schedule.end_at+timedelta(hours=3)).date()
		start_at_time     = (order_schedule.start_at+timedelta(hours=3)).time()
		end_at_time       = (order_schedule.end_at+timedelta(hours=3)).time()
		
		#same time schedules
		order_schedules = OrderScheduler.objects.filter(start_at=start_at_datetime,end_at=end_at_datetime,evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections'))		

		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		#included shift cleaners & exclude absent cleaners & exclude active cleaners
		shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).values_list('staff',flat=True)
		super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time)) ).values_list('id',flat=True)
		super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time))).values_list('id',flat=True)

		absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
		absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)
		
		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
		cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

		return render(request,'common/cleaning/cleaningteam_assign.html',{'order_schedule':order_schedule,'order_schedules':order_schedules,'cleaners':cleaners,'leaders':leaders})

	def post(self,request,scheduler_id):
		
		#shceduled order details
		order_schedule = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).get(is_active=True,id=scheduler_id)
		start_at_datetime = order_schedule.start_at
		end_at_datetime   = order_schedule.end_at
		start_at_date     = (order_schedule.start_at+timedelta(hours=3)).date()
		end_at_date       = (order_schedule.end_at+timedelta(hours=3)).date()
		start_at_time     = (order_schedule.start_at+timedelta(hours=3)).time()
		end_at_time       = (order_schedule.end_at+timedelta(hours=3)).time()

		#same time schedules
		order_schedules = OrderScheduler.objects.filter(start_at=start_at_datetime,end_at=end_at_datetime,evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections'))	
		
		#to block back button submission
		if order_schedule.cleaning_team and order_schedule.work_status=='CLEANING_TEAM_ASSIGNED':
			return redirect('stl:stldash-board')

		assigned_cleaners         = request.POST.getlist('assigned_cleaner')
		assigned_leader           = request.POST.get('team_leader')

		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		#check cleaners	& leaders	
		check_cleaners      = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
		check_tl            = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=assigned_leader)

		for order_scheduler in order_schedules:
			cleaning_team_assign_form = CleaningTeamAssignForm(request.POST)
			if	cleaning_team_assign_form.is_valid() and check_cleaners.count() >= len(assigned_cleaners) and check_tl:
				cleaning_team_assign_form_save                   = cleaning_team_assign_form.save(commit=False)
				cleaning_team_assign_form_save.order_scheduler   = order_scheduler
				cleaning_team_assign_form_save.start_at          = start_at_datetime
				cleaning_team_assign_form_save.end_at            = end_at_datetime
				cleaning_team_assign_form_save.created_by        = request.user
				cleaning_team_assign_form_save.save()
				
				#cleaners
				assigned_cleaners_list   = []
				for cleaner in assigned_cleaners:
					assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team_assign_form_save,member_id=cleaner,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team_assign_form_save,member=cleaning_team_assign_form_save.team_leader,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				#bulk create
				cleaning_team_members_assign = CleaningTeamMember.objects.bulk_create(assigned_cleaners_list)

				if cleaning_team_members_assign:
					#update cleaners count
					order_scheduler.no_of_cleaners = len(assigned_cleaners)+1
					order_scheduler.work_status    = 'CLEANING_TEAM_ASSIGNED'
					order_scheduler.save()
					
			else:	
				messages.error(request,"Something Went Wrong !! Please Reupdate")

				return redirect('common_items:assign-cleaningteam',scheduler_id)	
		
		messages.success(request,"Cleaning Team Succesfully Assigned")
		cleaning_calendar_date = request.GET.get('cleaning_calendar_date') or ''
		workers_calendar_date  = request.GET.get('workers_calendar_date') or ''

		if request.user.user_type == 'SENIORTEAMLEADER':
			return redirect('/stl/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&workers_calendar_date='+workers_calendar_date)	
		elif request.user.user_type == 'OPERATIONSUPERVISOR':
			return redirect('/operation-supervisor/dashboard/?cleaning_calendar_date='+cleaning_calendar_date)
		else:
			pass


class EditcleaningTeam(IsAuthenticated,View):
	def get(self,request,scheduler_id):
		#shceduled order details
		order_schedule  = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')).annotate(kitchen_keynote=Sum( Case( When(keynotesections__sub_area='kitchen',then=1),default=0,output_field=IntegerField()))),to_attr='sections')).get(is_active=True,id=scheduler_id)
		start_at_datetime = order_schedule.start_at
		end_at_datetime   = order_schedule.end_at
		start_at_date     = (order_schedule.start_at+timedelta(hours=3)).date()
		end_at_date       = (order_schedule.end_at+timedelta(hours=3)).date()
		start_at_time     = (order_schedule.start_at+timedelta(hours=3)).time()
		end_at_time       = (order_schedule.end_at+timedelta(hours=3)).time()

		#same time schedules
		order_schedules = OrderScheduler.objects.filter(start_at=start_at_datetime,end_at=end_at_datetime,evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections'))

		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		#included shift cleaners & exclude absent cleaners & exclude active cleaners
		shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).values_list('staff',flat=True)
		super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time)) ).values_list('id',flat=True)
		super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time))).values_list('id',flat=True)

		absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
		absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
		cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

		#cleaning members and leader
		current_leader      = CleaningTeam.objects.select_related('team_leader','order_scheduler').get(order_scheduler=order_schedule).team_leader
		current_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler').filter(team__order_scheduler=order_schedule).exclude(member_id=current_leader.id)

		return render(request,'common/cleaning/cleaningteam_edit.html',{'order_schedule':order_schedule,'order_schedules':order_schedules,'cleaners':cleaners,'leaders':leaders,'current_leader':current_leader,'current_cleaners':current_cleaners,})		

	def post(self,request,scheduler_id):
		schedule_id         = request.POST.get('cleaningschedule_id')	
		assigned_leader     = request.POST.get('team_leader')
		assigned_cleaners   = request.POST.getlist('assigned_cleaner')

		#shceduled order details
		order_schedule      = OrderScheduler.objects.select_related('evaluation_details__evaluation').get(is_active=True,id=schedule_id)
		start_at_datetime   = order_schedule.start_at
		end_at_datetime     = order_schedule.end_at
		start_at_time       = (order_schedule.start_at+timedelta(hours=3)).time()
		end_at_time         = (order_schedule.end_at+timedelta(hours=3)).time()
		
		#same time schedules
		order_schedules 	= OrderScheduler.objects.filter(start_at=start_at_datetime,end_at=end_at_datetime,evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections'))
		
		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)
				
		#check cleaners	& leaders	
		check_cleaners      = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
		check_tl            = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=assigned_leader)

		#for multiple schedule
		if check_cleaners.count() >= len(assigned_cleaners) and check_tl:
			for order_schedule in order_schedules:
				#delete existing cleaners
				cleaners_to_be_deleted       = CleaningTeamMember.objects.filter(team__order_scheduler=order_schedule).delete()

				#update cleaning team leader
				cleaning_team                = CleaningTeam.objects.get(is_active=True,order_scheduler=order_schedule,team_leader__user_type='TEAMINCHARGE')
				cleaning_team.team_leader_id = assigned_leader
				cleaning_team.no_of_cleaners = len(assigned_cleaners)+1
				cleaning_team.save()

				#update cleaning team members
				assigned_cleaners_list   = []
				for cleaner in assigned_cleaners:
					assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member_id=cleaner,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member_id=assigned_leader,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				
				CleaningTeamMember.objects.bulk_create(assigned_cleaners_list)
					
				order_schedule.no_of_cleaners = len(assigned_cleaners_list)
				order_schedule.save()

			messages.success(request,"Cleaning Team Updated")
	
		else:
			messages.error(request,"Something Went Wrong !! Please Reupdate")
			return redirect('common_items:edit-cleaningteam',schedule_id)
		if request.user.user_type == 'SENIORTEAMLEADER':
			return redirect('stl:stldash-board')
		else:
			return redirect('op-supervisor:op-supervisor-dash-board')


class AssignFollowupTeam(IsAuthenticated,View):
	def get(self,request,scheduler_id):

		#shceduled order details

		followup_schedule = FollowUpScheduler.objects.select_related('follow_up','follow_up__investigation__order','follow_up__investigation__order_schedule__order_scheduler_book__service_type','customer_address').prefetch_related(Prefetch('follow_up__investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr="investigationmedias")).get(is_active=True,id=scheduler_id)
	
		start_at_datetime = followup_schedule.start_at
		end_at_datetime   = followup_schedule.end_at
		start_at_date     = (followup_schedule.start_at+timedelta(hours=3)).date()
		end_at_date       = (followup_schedule.end_at+timedelta(hours=3)).date()
		start_at_time     = (followup_schedule.start_at+timedelta(hours=3)).time()
		end_at_time       = (followup_schedule.end_at+timedelta(hours=3)).time()

		followupsections = FollowUpSection.objects.filter(follow_up=followup_schedule.follow_up,is_active=True)
		followupkeynotes = FollowUpSectionKeynote.objects.filter(followup_section__follow_up=followup_schedule.follow_up,is_active=True)

		follow_up_team_assign_form = FollowupTeamAssignForm()
		

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)


		#included shift cleaners & exclude absent cleaners & exclude active cleaners
		shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).values_list('staff',flat=True)
		super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time)) ).values_list('id',flat=True)
		super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time))).values_list('id',flat=True)

		absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
		absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
		cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

		return render(request,'common/cleaning/followupteam_assign.html',{'follow_up_team_assign_form':follow_up_team_assign_form,'followup_schedule':followup_schedule,'cleaners':cleaners,'leaders':leaders,"sections":followupsections,"keynotes":followupkeynotes})

	def post(self,request,scheduler_id):
	
		#shceduled order details
		followup_schedule = FollowUpScheduler.objects.select_related('follow_up__investigation__order','follow_up__investigation__order_schedule__order_scheduler_book__service_type','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_team')).get(is_active=True,id=scheduler_id)	
		start_at_datetime = followup_schedule.start_at
		end_at_datetime   = followup_schedule.end_at
		start_at_date     = (followup_schedule.start_at+timedelta(hours=3)).date()
		end_at_date       = (followup_schedule.end_at+timedelta(hours=3)).date()
		start_at_time     = (followup_schedule.start_at+timedelta(hours=3)).time()
		end_at_time       = (followup_schedule.end_at+timedelta(hours=3)).time()

		#to block back button submission
		if followup_schedule.followup_team and followup_schedule.work_status=='FOLLOW_UP_TEAM_ASSIGNED':
			return redirect('stl:stldash-board')

		follow_up_team_assign_form = FollowupTeamAssignForm(request.POST)
		assigned_cleaners          = request.POST.getlist('assigned_cleaner')
		assigned_leader            = request.POST.get('team_leader')

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		#validation
		check_cleaners      = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
		check_tl            = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=assigned_leader)
				
		if	follow_up_team_assign_form.is_valid() and check_cleaners.count() >= len(assigned_cleaners) and check_tl:
			follow_up_team_assign_form_save                   = follow_up_team_assign_form.save(commit=False)
			follow_up_team_assign_form_save.followup_scheduler_id= scheduler_id
			follow_up_team_assign_form_save.start_at          = start_at_datetime
			follow_up_team_assign_form_save.end_at            = end_at_datetime
			follow_up_team_assign_form_save.created_by        = request.user
			follow_up_team_assign_form_save.save()

			#cleaners
			assigned_cleaners_list   = []
			for cleaner in assigned_cleaners:
				assigned_cleaners_list.append(FollowUpTeamMember(team=follow_up_team_assign_form_save,member_id=cleaner,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_time,end_time=end_at_time))
			assigned_cleaners_list.append(FollowUpTeamMember(team=follow_up_team_assign_form_save,member=follow_up_team_assign_form_save.team_leader,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_time,end_time=end_at_time))
			#bulk create
			follow_up_team_members_assign = FollowUpTeamMember.objects.bulk_create(assigned_cleaners_list)

			#update cleaners count
			if follow_up_team_members_assign:
				followup_schedule.follow_up.no_of_cleaners = len(assigned_cleaners)+1			
				followup_schedule.work_status                          = 'FOLLOW_UP_TEAM_ASSIGNED'
				followup_schedule.follow_up.save()
				followup_schedule.save()	
		else:	
			messages.error(request,"Something Went Wrong")

			return render(request,'common/cleaning/followupteam_assign.html',{'follow_up_team_assign_form':follow_up_team_assign_form,'followup_schedule':followup_schedule,'cleaners':cleaners,'leaders':leaders,'drivers':drivers,})	

		messages.success(request,"FollowupTeam Team Succesfully Assigned")

		cleaning_calendar_date = request.GET.get('cleaning_calendar_date') or ''
		workers_calendar_date  = request.GET.get('workers_calendar_date') or ''

		if request.user.user_type == 'SENIORTEAMLEADER':
			return redirect('/stl/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&workers_calendar_date='+workers_calendar_date)
		elif request.user.user_type == 'OPERATIONSUPERVISOR':
			return redirect('/operation-supervisor/dashboard/?cleaning_calendar_date='+cleaning_calendar_date)
		else:
			pass


class EditFollowupTeam(IsAuthenticated,View):
	def get(self,request,scheduler_id):
		
		follow_up_team_assign_form = FollowupTeamAssignForm()

		#shceduled order details
		followup_schedule   = FollowUpScheduler.objects.select_related('follow_up','follow_up__investigation__order','follow_up__investigation__order_schedule__order_scheduler_book__service_type','customer_address').prefetch_related(Prefetch('follow_up__investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr="investigationmedias")).get(is_active=True,id=scheduler_id)
		followupsections    = FollowUpSection.objects.filter(follow_up=followup_schedule.follow_up,is_active=True)
		followupkeynotes    = FollowUpSectionKeynote.objects.filter(followup_section__follow_up=followup_schedule.follow_up,is_active=True)
		
		start_at_datetime   = followup_schedule.start_at
		end_at_datetime     = followup_schedule.end_at
		start_at_date       = (followup_schedule.start_at+timedelta(hours=3)).date()
		end_at_date         = (followup_schedule.end_at+timedelta(hours=3)).date()
		start_at_time       = (followup_schedule.start_at+timedelta(hours=3)).time()
		end_at_time         = (followup_schedule.end_at+timedelta(hours=3)).time()


		#finding active leaders and cleaners
		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		#included shift cleaners & exclude absent cleaners & exclude active cleaners
		shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_at_time)&Q(shift1_end_at__gte=start_at_time))&Q(Q(shift1_start_at__lte=end_at_time)&Q(shift1_end_at__gte=end_at_time))) | Q(Q(Q(shift2_start_at__lte=start_at_time)&Q(shift2_end_at__gte=start_at_time))&Q(Q(shift2_start_at__lte=end_at_time)&Q(shift2_end_at__gte=end_at_time))) | Q(Q(Q(shift3_start_at__lte=start_at_datetime)&Q(shift3_end_at__gte=start_at_datetime))&Q(Q(shift3_start_at__lte=end_at_datetime)&Q(shift3_end_at__gte=end_at_datetime)))).values_list('staff',flat=True)
		today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).values_list('staff',flat=True)
		super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time)) ).values_list('id',flat=True)
		super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_at_time)&Q(universal_shift_end__gte=start_at_time))&Q(Q(universal_shift_start__lte=end_at_time)&Q(universal_shift_end__gte=end_at_time))).values_list('id',flat=True)

		absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
		absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
		cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

		#cleaning members and leader
		current_leader      = FollowUpTeam.objects.select_related('team_leader','followup_scheduler').get(followup_scheduler=followup_schedule).team_leader
		current_cleaners    = FollowUpTeamMember.objects.select_related('team__followup_scheduler').filter(team__followup_scheduler=followup_schedule).exclude(member_id=current_leader.id)

		return render(request,'common/cleaning/followupteam_edit.html',{'follow_up_team_assign_form':follow_up_team_assign_form,'followup_schedule':followup_schedule,'cleaners':cleaners,'leaders':leaders,"sections":followupsections,"keynotes":followupkeynotes,"current_leader":current_leader,"current_cleaners":current_cleaners,})		

	def post(self,request,scheduler_id):
		schedule_id         = request.POST.get('followupschedule_id')	
		assigned_leader     = request.POST.get('team_leader')
		assigned_cleaners   = request.POST.getlist('assigned_cleaner')

		followup_schedule   = FollowUpScheduler.objects.select_related('follow_up').get(is_active=True,id=schedule_id)
		start_at_datetime   = followup_schedule.start_at
		end_at_datetime     = followup_schedule.end_at
		start_at_time       = (followup_schedule.start_at+timedelta(hours=3)).time()
		end_at_time         = (followup_schedule.end_at+timedelta(hours=3)).time()

		#validates
		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

		#validation
		check_cleaners      = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
		check_tl            = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=assigned_leader)
		
		
		#Assign Followup Team
		if check_cleaners.count() >= len(assigned_cleaners)  and check_tl:	
			
			#delete existing cleaners
			cleaners_to_be_deleted = FollowUpTeamMember.objects.filter(team__followup_scheduler_id=schedule_id).delete()
			
			#update followup team leader				
			followup_team                = FollowUpTeam.objects.get(is_active=True,followup_scheduler_id=schedule_id)
			followup_schedule.follow_up.no_of_cleaners = len(assigned_cleaners)+1
			followup_team.team_leader_id = assigned_leader			
			followup_schedule.follow_up.save()
			followup_team.save()

			#update Followup team members
			start_at_to_assign=(followup_schedule.start_at+timedelta(hours=3)).time()
			end_at_to_assign  =(followup_schedule.end_at+timedelta(hours=3)).time()
			assigned_cleaners_list   = []
			for cleaner in assigned_cleaners:
				assigned_cleaners_list.append(FollowUpTeamMember(team=followup_team,member_id=cleaner,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
			assigned_cleaners_list.append(FollowUpTeamMember(team=followup_team,member_id=assigned_leader,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
			FollowUpTeamMember.objects.bulk_create(assigned_cleaners_list)	

			messages.success(request,"Follow Up Team Updated Succesfully")
		else:
			messages.error(request,"Something Went Wrong !! Please Refresh Page and Reupdate")
			return redirect('common_items:edit-followupteam',schedule_id)

		if request.user.user_type == 'SENIORTEAMLEADER':
			return redirect('stl:stldash-board')
		else:
			return redirect('op-supervisor:op-supervisor-dash-board')

class ResetcleaningTeam(IsAuthenticated,View):
	def get(self,request,scheduler_id):

		#shceduled order details
		order_schedule    = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')).annotate(kitchen_keynote=Sum( Case( When(keynotesections__sub_area='kitchen',then=1),default=0,output_field=IntegerField()))),to_attr='sections')).get(is_active=True,id=scheduler_id)
		start_at_datetime = order_schedule.start_at
		end_at_datetime   = order_schedule.end_at
		start_at_date     = (order_schedule.start_at+timedelta(hours=3)).date()
		end_at_date       = (order_schedule.end_at+timedelta(hours=3)).date()
		start_at_time     = (order_schedule.start_at+timedelta(hours=3)).time()
		end_at_time       = (order_schedule.end_at+timedelta(hours=3)).time()

		related_schedules = OrderScheduler.objects.filter(Q(start_at__date=start_at_date)|Q(end_at__date=start_at_date)|Q(start_at__date=end_at_date)|Q(end_at__date=end_at_date)).filter(work_status='CLEANING_TEAM_ASSIGNED',order__evaluation__id=order_schedule.order.evaluation.id).select_related('order__evaluation')

		if related_schedules:
			for schedule in related_schedules:
				cleaningteams = CleaningTeam.objects.filter(is_active=True,order_scheduler__id=schedule.id).delete()
				schedule.work_status = None
				schedule.save()	
		else:
			cleaningteams = CleaningTeam.objects.filter(is_active=True,order_scheduler__id=scheduler_id).delete()
			order_schedule.work_status = None
			order_schedule.save()

		messages.success(request,"Cleaning team reset successfully !")
			
		return redirect('stl:stldash-board')

# class ResetFollowUpTeam(IsAuthenticated,View):
# 	def get(self,request,scheduler_id):
# 		followupteams = FollowUpTeam.objects.filter(is_active=True,followup_scheduler__id=int(scheduler_id))
# 		for team in followupteams:
# 			team.delete()
# 		return redirect('stl:stldash-board')


class TicketRegistration(IsAuthenticated,View):
	def get(self,request):

		try:
			orders = Order.objects.filter(is_active=True)
		except:
			orders = None

		investigators = UserProfile.objects.filter(Q(Q(user_type='QUALITYCONTROLL')|Q(user_type='OPERATIONSUPERVISOR')),is_active=True)

		return render(request,'agent/ticket/ticket_registration.html',{'orders':orders,'investigators':investigators})

	def post(self,request):
		order_id           = request.POST.get('order_id')
		
		investigation_form = InvestigationForm(request.POST)
		if investigation_form.is_valid():
			investigation_form_save             = investigation_form.save(commit=False)
			investigation_form_save.assigned_by = request.user
			investigation_form_save.order_id    = order_id
			investigation_form_save.scheduled_at= timezone.now()
			investigation_form_save.save()

			FollowUp.objects.create(investigation=investigation_form_save,status='TICKET_RISED')

			#save media
			investigation_medias = request.FILES.getlist('investigation_media')
			if not investigation_medias == ['']:
					for image in investigation_medias:
						InvestigationMedia.objects.create(
							investigation = investigation_form_save,
							media = image,
							media_type = 'PHOTO',
							taken_status = 'CUSTOMER_SEND',
							is_active = True
						)
						
			#Email Send
			msg_html = render_to_string('email/rise_ticket_request.html',{'investigation_form_save':investigation_form_save})
			msg      = EmailMultiAlternatives('Ticket Raised', '', 'notification@bleach-kw.com', [investigation_form_save.investigator.email])
			msg.attach_alternative(msg_html, "text/html")
			msg.send(fail_silently=False)

			messages.success(request,"Investigation Raised Succesfully!")
		else:
			messages.error(request,get_error(investigation_form))
		

		return redirect('common_items:ticketregister')


class OrderTicketRegistration(IsAuthenticated,View):
	def get(self,request,orderid):

		order = Order.objects.filter(id=int(orderid)).first()

		investigators = UserProfile.objects.filter(Q(Q(user_type='QUALITYCONTROLL')|Q(user_type='OPERATIONSUPERVISOR')),is_active=True)

		return render(request,'agent/ticket/ticket_registration.html',{'order':order,'investigators':investigators})

	def post(self,request,orderid):
		order_id           = request.POST.get('order_id')
		
		investigation_form = InvestigationForm(request.POST)
		if investigation_form.is_valid():
			investigation_form_save             = investigation_form.save(commit=False)
			investigation_form_save.assigned_by = request.user
			investigation_form_save.order_id    = order_id
			investigation_form_save.scheduled_at= timezone.now()
			investigation_form_save.save()

			FollowUp.objects.create(investigation=investigation_form_save,status='TICKET_RISED')

			#save media
			investigation_medias = request.FILES.getlist('investigation_media')
			if not investigation_medias == ['']:
					for image in investigation_medias:
						InvestigationMedia.objects.create(
							investigation = investigation_form_save,
							media = image,
							media_type = 'PHOTO',
							taken_status = 'CUSTOMER_SEND',
							is_active = True
						)

			#Email Send
			msg_html = render_to_string('email/rise_ticket_request.html',{'investigation_form_save':investigation_form_save})
			msg      = EmailMultiAlternatives('Ticket Raised', '', 'notification@bleach-kw.com', [investigation_form_save.investigator.email])
			msg.attach_alternative(msg_html, "text/html")
			msg.send(fail_silently=False)
									
			messages.success(request,"Investigation Raised Succesfully!")
		else:
			messages.error(request,get_error(investigation_form))
		

		return redirect('common_items:ticketregister')