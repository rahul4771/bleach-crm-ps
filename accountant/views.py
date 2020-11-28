from django.shortcuts import render,redirect,render_to_response
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsAccountant
# Create your views here.

import xlwt
import itertools

import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,Max
from django.db.models.functions import Concat
from django.db.models.functions import Cast 
from django.db.models import Prefetch
from django.contrib import messages

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory

import requests
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect

from user.models import UserProfile

def GetCashCollectOrderInfo(request):
	data               = {}
	order_info_dict = {}

	query       =   request.GET.get('keyword')

	orders = Order.objects.filter(is_active=True,order_status__isnull=False).filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))).select_related('evaluation__customer').filter(Q(evaluation__quatation_status='APPROVED') & Q(Q(evaluation__evaluation_id__icontains=query)|Q(evaluation__customer__name__icontains=query)) & ~Q(Q(order_status='ORDER_CANCELLED'))).prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules')).annotate(Count('order_scheduler_order'))
			
	
	if orders:
		for order in orders:
			order_info_dict[order.id] = order.evaluation.evaluation_id+'-'+order.evaluation.customer.name 	

	
	data['order_details'] = order_info_dict


	data['status']     = 'true'

	if order_info_dict == {}: 
		data['status'] = 'false'	
	
	return JsonResponse(data)


def GetCashCollectOrderDetailedInfo(request):

		dropdown_order_info = {}

		order_id            = request.GET.get('order_id')

		order = Order.objects.select_related('evaluation__customer','evaluation__call_attender').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('customer_address__area','customer_address','order_scheduler_book__service_type'),to_attr='order_secheduler_feedback'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules')).annotate(total_cleaners=Sum('order_scheduler_order__order_scheduler_book__number_of_cleaners')).annotate(Count('order_scheduler_order')).get(id=order_id,is_active=True)

		#to mark last cleaning completed for breakdown
		if order.evaluation.payment_method == 'BREAKDOWN':
			very_latest_cleaning=order.orderschedules[order.order_scheduler_order__count-1]	
			#to check last cleaning completed for break down after payment
			if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
				order.last_completed = True
				dropdown_order_info['last_cleaning_completed']   = True
			else:
				dropdown_order_info['last_cleaning_completed']   = False	


		dropdown_order_info['order_id']      = order.id

		##order information
		dropdown_order_info['blc_no']           = order.order_no
		dropdown_order_info['name']          	= order.evaluation.customer.name
		dropdown_order_info['mobile_number'] 	= order.evaluation.customer.mobile_number
		dropdown_order_info['total_cost']    	= order.evaluation.total_cost
		dropdown_order_info['date']          	= order.evaluation.created.strftime('%b %d %Y,%I:%M %p')
		dropdown_order_info['order_status']  	= order.order_status
		dropdown_order_info['payment_status']	= order.payment_status
		dropdown_order_info['payment_policy']	= order.evaluation.payment_method
		dropdown_order_info['agent_image_url']	= order.evaluation.call_attender.profile_image.url or None
		dropdown_order_info['agent_name']       = order.evaluation.call_attender.name or None
		dropdown_order_info['total_cleaners'] 	= order.total_cleaners

		dropdown_order_info['remining_amount']     = order.remining_amount
		dropdown_order_info['before_amount']       = order.evaluation.before_cleaning_amount 
		dropdown_order_info['after_amount']        = order.evaluation.after_cleaning_amount
		dropdown_order_info['before_amount_paid']  = order.preamount_paid 
		dropdown_order_info['after_amount_paid']   = order.postamount_paid		


		#for multiple order addresses
		dropdown_order_info['order_address']   = []
		for scheduler in order.order_secheduler_feedback:
			customer_order_address = []

			customer_order_address.append(scheduler.customer_address.area.name)
			customer_order_address.append(scheduler.order_scheduler_book.service_type.name)
			customer_order_address.append(scheduler.order_scheduler_book.cleaning_policy)
			customer_order_address.append(scheduler.work_status)
			dropdown_order_info['order_address'].append(customer_order_address)


		##customer information
		customer_information = {}
		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=order.evaluation.customer_id)
		except:
			client_details = None

		customer_information['name']          = client_details.name
		customer_information['email']         = client_details.email
		customer_information['mobile']        = client_details.mobile_number
		customer_information['other_number']  = client_details.phone_number
		customer_information['nationality']   = client_details.nationality.code
		customer_information['company']       = client_details.company

		#for multiple customer addresses
		customer_information['customer_address']   = []
		for address in client_details.customer_addresses:
			customer_address = {}

			customer_address['governorate'] 	= address.governorate.name
			customer_address['area'] 			= address.area.name
			customer_address['block'] 			= address.block
			customer_address['avenue'] 			= address.avenue
			customer_address['building'] 		= address.building
			customer_address['street'] 			= address.street
			customer_address['floor'] 			= address.floor
			customer_address['apartment'] 		= address.apartment

			customer_information['customer_address'].append(customer_address)

		dropdown_order_info['customer_details'] = customer_information

		##previous order informations
		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=order.evaluation.customer_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()
		dropdown_order_info['active_orders_count'] = active_orders_count
		dropdown_order_info['total_orders_count']  = total_orders_count


		return JsonResponse(dropdown_order_info)	


class AccountantHome(IsAccountant,View):
	def get(self,request):
		#Payment Details
		search                  = request.GET.get('search')



		#sales amount
		try:
			invoices         = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',order_status__isnull=False).order_by('-id')
		except:
			invoices         = None


		payment_history = PaymentHistory.objects.filter(is_active=True)

		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)		
		this_week_sales = payment_history.filter(paid_date__gte=count_today_start-timedelta(7)).aggregate(total=Sum('amount_paid'))['total']
		last_week_sales = payment_history.filter(paid_date__gte=count_today_start-timedelta(14),paid_date__lte=count_today_start-timedelta(7)).aggregate(total=Sum('amount_paid'))['total']		
		
		month_start_date     = count_today_start.replace(day=1)
		nxtmonth_start_date  = month_start_date+relativedelta(months=1)
		prvmonth_start_date  = month_start_date-relativedelta(months=1)
		this_month_sales=payment_history.filter(paid_date__gte=month_start_date,paid_date__lt=nxtmonth_start_date).aggregate(total=Sum('amount_paid'))['total']
		last_month_sales=payment_history.filter(paid_date__gte=prvmonth_start_date,paid_date__lt=month_start_date).aggregate(total=Sum('amount_paid'))['total']	
		
		quarter_start_date   = month_start_date-relativedelta(months=2)
		prvquarter_start_date= month_start_date-relativedelta(months=5)
		this_quarter_sales=payment_history.filter(paid_date__gte=quarter_start_date,paid_date__lt=nxtmonth_start_date).aggregate(total=Sum('amount_paid'))['total']
		last_quarter_sales=payment_history.filter(paid_date__gte=prvquarter_start_date,paid_date__lt=quarter_start_date).aggregate(total=Sum('amount_paid'))['total']	
		
		#Pending Payments
		pending_payments = invoices.filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules')).annotate(Count('order_scheduler_order'))
			

		#remove object in postpaid if not last cleaning fulfilled	
		for payment in pending_payments:
			if payment.evaluation.payment_method == 'POSTPAID':
				very_latest_cleaning=payment.orderschedules[payment.order_scheduler_order__count-1]
				if very_latest_cleaning.work_status != 'CLEANING_FULFILLED':
					pending_payments = pending_payments.exclude(id=payment.id)


		#to find days
		for payment in pending_payments:

			if payment.evaluation.payment_method == 'PREPAID':
				very_old_cleaning   = payment.orderschedules[0]
				payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
			elif payment.evaluation.payment_method == 'POSTPAID':
				very_latest_cleaning=payment.orderschedules[payment.order_scheduler_order__count-1]
				payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	


			elif payment.evaluation.payment_method == 'BREAKDOWN':
			
				very_old_cleaning   = payment.orderschedules[0]
				very_latest_cleaning=payment.orderschedules[payment.order_scheduler_order__count-1]
				payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
				payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	

				#to check last cleaning completed for break down after payment
				if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
					payment.last_completed = True	




		#Pending Payment and Order Count	
		if pending_payments:
			total_pending_amount = pending_payments.aggregate(total=Sum(F('remining_amount')))['total']		
			total_pending_orders = pending_payments.count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0

		return render(request,'accountant/home/home.html',{"this_week_sales":this_week_sales,"last_week_sales":last_week_sales,"this_month_sales":this_month_sales,"last_month_sales":last_month_sales,"this_quarter_sales":this_quarter_sales,"last_quarter_sales":last_quarter_sales,"pending_payments":pending_payments,'total_pending_amount':total_pending_amount,"total_pending_orders":total_pending_orders})

class ClientDetails(IsAccountant,View):
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

		try:
			service_types = ServiceType.objects.filter(is_active=True) 
		except:
			service_types =	None

		#date filter
		fromdate = request.GET.get('fromdate',None)
		todate = request.GET.get('todate',None)

		if fromdate != None and todate != None:
			prevdate = datetime.strptime(fromdate, '%d-%m-%Y')
			todate = datetime.strptime(todate, '%d-%m-%Y')

			prev_date_start  = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
			prev_date_end = prevdate+timedelta(1)
			todate_date_start= todate.replace(hour=0,minute=0,second=0,microsecond=0)   #single_date+timedelta(1)
			todate_date_end = todate+timedelta(1)
			print(prev_date_start,"pds")
		elif fromdate != None and todate == None:
			prevdate = datetime.strptime(fromdate, '%d-%m-%Y')
			prev_date_start  = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
			todate_date_end = None
			todate_date_start = None
		elif fromdate == None and todate != None:
			todate = datetime.strptime(todate, '%d-%m-%Y')
			todate_date_start= todate.replace(hour=0,minute=0,second=0,microsecond=0)   #single_date+timedelta(1)
			todate_date_end = todate+timedelta(1)
			prev_date_start  = None
		else:
			prev_date_start = None
			todate_date_end = None
			todate_date_start = None

		#Evaluation Details
		search                  = request.GET.get('search')
		
		#sales amount
		if search:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED').filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))
			except:
				invoices         = None
		else:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules'))
			except:
				invoices         = None
				
		#Pending Payments
		try:
			pending_payments = invoices.filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(evaluation__quatation_status='APPROVED')&Q(order_status='APPROVED_BY_CLIENT'))
		except:
			pending_payments = None

		#Pending Payment and Order Count	
		if pending_payments: 
			total_pending_amount = pending_payments.aggregate(total=Sum(F('remining_amount')))['total']		
			total_pending_orders = pending_payments.count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0

		#Prefetch filters

		fil_cleaning_policy       	= request.GET.get('cleaning_policy')

		fil_cleaning_status			= request.GET.get('status',None)

		fil_payment_policy			= request.GET.get('payment_policy',None)

		filters =[]
		if fil_payment_policy:
			case1 = Q(evaluation__payment_method=fil_payment_policy)
			filters.append(case1)

		if fil_cleaning_status:
			case2       = Q(order_status=fil_cleaning_status)
			filters.append(case2)

		if prev_date_start and todate_date_end:
			case3       = Q(created__range=(prev_date_start,todate_date_end))
			filters.append(case3)

		if fil_payment_policy or fil_cleaning_status or fromdate or todate:
			filters=functools.reduce(operator.and_,filters)
			invoices = invoices.filter(filters)
			

		try:
			fil_service_type      = int(request.GET.get('service_type'))
		except:
			fil_service_type      = None

		
		evaluation_book_filter       	= []
		count_evaluation_book_filter = []

		if fil_cleaning_policy:
			case1       = Q(cleaning_policy=fil_cleaning_policy)
			count_case1 = Q(evaluation__evaluation_details__evaluation_book_evaluation_details__cleaning_policy=fil_cleaning_policy)
			evaluation_book_filter.append(case1)
			count_evaluation_book_filter.append(count_case1)

		if fil_service_type:     
			case2       = Q(service_type_id=fil_service_type)
			count_case2 = Q(evaluation__evaluation_details__evaluation_book_evaluation_details__service_type_id=fil_service_type)
			evaluation_book_filter.append(case2) 
			count_evaluation_book_filter.append(count_case2)             

		if fil_cleaning_policy or fil_service_type:
			evaluation_book_prefetch_filter              = functools.reduce(operator.and_,evaluation_book_filter)
			count_evaluation_book_prefetch_filter        = functools.reduce(operator.and_,count_evaluation_book_filter)
		
		else:
			evaluation_book_prefetch_filter              = None	
			count_evaluation_book_prefetch_filter        = None

		
		#Apply prefetch filter

		if evaluation_book_prefetch_filter :
			invoices = invoices.select_related('evaluation').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_book_count=Count(Case(When( Q(count_evaluation_book_prefetch_filter),then=1),output_field=IntegerField()))).filter(address_book_count__gt=0)		 
			print(invoices,"book only")
			

		else:
			invoices = invoices.select_related('evaluation').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))		
			print("not at all")

		
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

		return render(request,'accountant/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"service_types":service_types,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_status":fil_cleaning_status,"fil_payment_policy":fil_payment_policy,"fromdate":prev_date_start,"todate":todate_date_start})

class CashCollect(IsAccountant,View):
	def get(self,request):
		return render(request,'accountant/payment/cash-collect.html',{})
	def post(self,request):

		order_id = request.POST.get('order_id')

		if order_id:
			payment_policy = request.POST.get('payment_policy')
			payment_method = request.POST.get('payment_method')

			amount       = request.POST.get('amount')
			payment_date = datetime.strptime(request.POST.get('collection_date'),'%d/%m/%Y %I:%M %p')
			
			#Receipt Number
			receipt_no               = PaymentHistory.objects.filter(is_active=True,receipt_no__isnull=False).aggregate(t=Max('receipt_no'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_receipt_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_receipt_starting == int(str(receipt_no)[:4]):
				new_receipt_no = int(receipt_no)+1
			else:
				new_receipt_no = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')			
	

			if payment_method == 'CASH':
				if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount,remining_amount=0) 
				elif payment_policy == 'BEFORE CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=amount)
				elif payment_policy == 'AFTER CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=amount)

				PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
				
				messages.success(request,"Payment Received thruogh Cash")

			if payment_method == 'CHEQUE':
				check_no   = request.POST.get('check_number')
				check_date = datetime.strptime(request.POST.get('check_date'),'%d-%m-%Y')

				if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount,remining_amount=0) 
				elif payment_policy == 'BEFORE CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=amount)
				elif payment_policy == 'AFTER CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=amount)

				PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
				
				messages.success(request,"Payment Received thruogh Cheque")

			if payment_method == 'BANK':
				bank_name   = request.POST.get('bank_name')
				bank_no     = request.POST.get('ibn_number')

				if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount,remining_amount=0) 
				elif payment_policy == 'BEFORE CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=amount)
				elif payment_policy == 'AFTER CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=amount)

				PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)

				messages.success(request,"Payment Received through Bank")

			is_payment_completed = Order.objects.get(id=order_id)

			if is_payment_completed.amount_paid == is_payment_completed.total_amount:
				is_payment_completed.payment_completed_date = payment_date 
				is_payment_completed.payment_status         = 'COMPLETED'
				is_payment_completed.save()
		
		else:
			messages.suucess(request,"Something Went Wrong")

		return redirect('accountant:accountant-cashcollect')

#export to excel
def export_users_xls(request):

	from_date = request.POST.get('from_date')
	to_date = request.POST.get('to_date')
	report_type = request.POST.get('report_type')
	print(from_date,to_date,report_type,"ftd")

	prevdate = datetime.strptime(from_date, '%d-%m-%Y')
	todate = datetime.strptime(to_date, '%d-%m-%Y')

	prev_date_start  = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
	prev_date_end = prevdate+timedelta(1)
	todate_date_start= todate.replace(hour=0,minute=0,second=0,microsecond=0)   #single_date+timedelta(1)
	todate_date_end = todate+timedelta(1)

	# Sheet header, first row
	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	if report_type == 'paymentlist':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="GENERAL_PAYMENT_SHEET_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('GENERAL PAYMENT SHEET')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Quotation No.','Customer Name','Payment Policy','Amount','Paid Amount','Balance','Payment Mode','Job Status']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status'),payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).values_list('created','order_no','evaluation__customer__name', 'evaluation__payment_method','evaluation__total_cost','amount_paid','remining_amount','payment_type','job_status').order_by('-id')
	
		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[1] not in found:
				rows.append(order)
			found.add(order[1])
	
	
	if report_type == 'totalsales':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="TOTAL_SALES_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('TOTAL SALES')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Customer Name','Quotation No.','Salesman','Type of Contract','Type of location',
		'Invoice No.','Job Status','Payment Policy','Gross Amount','Discount','Net Amount','Paid Amount',
		'Payment Type','Date of Payment','Balance to Collect']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status'),payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).values_list('created','evaluation__customer__name','order_no','evaluation__call_attender__name', 'order_scheduler_order__evaluation_details__evaluation_book_evaluation_details__cleaning_policy' , 'order_scheduler_order__evaluation_details__evaluation_book_evaluation_details__location_type' , 'order_no' , 'job_status', 'evaluation__payment_method', 'evaluation__estimated_cost','evaluation__discount','evaluation__total_cost','amount_paid','payment_type','history_order__paid_date','remining_amount').order_by('-id')
	
		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[2] not in found:
				order_list = list(order)
				order_list[6] = order_list[6][9:]
				order = tuple(order_list)
				rows.append(order)
			found.add(order[2])

	
	
	if report_type == 'acceptedjobs':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="ACCEPTED_JOBS_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('ACCEPTED JOBS')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Customer Name','Quotation No.','Quotation Date','Quotation Status','Salesman',
		'Type of Contract','Type of location','Invoice No.','Job Execution Date','Job Status','Payment Policy',
		'Gross Amount','Discount','Net Amount']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status')).values_list('created','evaluation__customer__name','order_no','evaluation__created','evaluation__quatation_status','evaluation__call_attender__name', 'order_scheduler_order__evaluation_details__evaluation_book_evaluation_details__cleaning_policy' , 'order_scheduler_order__evaluation_details__evaluation_book_evaluation_details__location_type' , 'order_no', 'order_scheduler_order__start_at', 'job_status', 'evaluation__payment_method', 'evaluation__estimated_cost','evaluation__discount','evaluation__total_cost').order_by('-id')

		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[2] not in found:
				order_list = list(order)
				order_list[8] = order_list[8][9:]
				order = tuple(order_list)
				rows.append(order)
			found.add(order[2])

		print(rows,"lol")


	if report_type == 'rejectedjobs':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="REJECTED_JOBS_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('REJECTED JOBS')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Customer Name','Quotation No.','Quotation Date','Quotation Status','Salesman',
		'Type of Contract','Type of location','Invoice No.','Job Execution Date','Job Status','Payment Policy',
		'Gross Amount','Discount','Net Amount']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,evaluation__quatation_status='REJECTED',created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status')).values_list('created','evaluation__customer__name','order_no','evaluation__created','evaluation__quatation_status','evaluation__call_attender__name', 'order_scheduler_order__evaluation_details__evaluation_book_evaluation_details__cleaning_policy' , 'order_scheduler_order__evaluation_details__evaluation_book_evaluation_details__location_type' , 'order_no', 'order_scheduler_order__start_at', 'job_status', 'evaluation__payment_method', 'evaluation__estimated_cost','evaluation__discount','evaluation__total_cost').order_by('-id')
	
		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[2] not in found:
				order_list = list(order)
				order_list[8] = order_list[8][9:]
				order = tuple(order_list)
				rows.append(order)
			found.add(order[2])
	
	if report_type == 'onetime':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="ONETIME_CLEANING_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('ONETIME CLEANING')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Customer Name','Quotation No.','Salesman','Invoice No.','Job Status','Total Jobs',
		'Pending Jobs','Job Completion Date','Payment Policy','Gross Amount','Discount','Net Amount','Paid Amount',
		'Payment Type','Date of Payment','Balance to Collect']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status'),payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).annotate(total_jobs=Count('order_scheduler_order') or 0 + Count('investigation_orders') or 0 , pending_jobs=Sum(Case(When(Q(investigation_orders__followup_investigation__status='INVESTIGATOR_APPROVED')|Q(investigation_orders__followup_investigation__status='FOLLOWUP_IN_PROGRESS'),then=1),default=0,output_field=IntegerField())) + Sum(Case(When(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS'),then=1),default=0,output_field=IntegerField()))).values_list('created','evaluation__customer__name','order_no','evaluation__call_attender__name' , 'order_no', 'job_status', 'total_jobs', 'pending_jobs', 'created', 'evaluation__payment_method', 'evaluation__estimated_cost','evaluation__discount','evaluation__total_cost','amount_paid','payment_type','created','remining_amount').order_by('-id')
	
		#remove duplicates
		found = set()

		rows = []

		#invoice no and job completion date
		for order in orders:
			if order[2] not in found:
				order_list = list(order)

				order_completion_date = OrderScheduler.objects.filter(is_active=True,order__order_no=order_list[4]).last()
				followup_completion_date = FollowUpScheduler.objects.filter(is_active=True,follow_up__investigation__order__order_no=order_list[4]).last()

				order_cleaning_policy = OrderScheduler.objects.filter(is_active=True,order__order_no=order_list[4],order_scheduler_book__cleaning_policy='ONE TIME SERVICE').first()
				
				payment_date = PaymentHistory.objects.filter(is_active=True,order__order_no=order_list[4]).last()
				
				if order_cleaning_policy != None:
				
					if followup_completion_date != None :
						order_list[8] = followup_completion_date.end_at
					else:
						if order_completion_date != None :
							order_list[8] = order_completion_date.end_at
						else:
							order_list[8] = '-'

					if payment_date != None:
						order_list[15] = payment_date.paid_date
					else:
						order_list[15] = '-'
					
					order_list[4] = order_list[4][9:]
					order = tuple(order_list)
					rows.append(order)
				else:
					pass

			found.add(order[2])
	
	if report_type == 'subscription':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="SUBSCRIPTION_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('SUBSCRIPTION')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Customer Name','Quotation No.','Salesman','Invoice No.','Job Status','Total Jobs',
		'Pending Jobs','Job Completion Date','Payment Policy','Gross Amount','Discount','Net Amount','Paid Amount',
		'Payment Type','Date of Payment','Balance to Collect']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status'),payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).annotate(total_jobs=Count('order_scheduler_order') or 0 + Count('investigation_orders') or 0 , pending_jobs=Sum(Case(When(Q(investigation_orders__followup_investigation__status='INVESTIGATOR_APPROVED')|Q(investigation_orders__followup_investigation__status='FOLLOWUP_IN_PROGRESS'),then=1),default=0,output_field=IntegerField())) + Sum(Case(When(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS'),then=1),default=0,output_field=IntegerField()))).values_list('created','evaluation__customer__name','order_no','evaluation__call_attender__name' , 'order_no', 'job_status', 'total_jobs', 'pending_jobs', 'created', 'evaluation__payment_method', 'evaluation__estimated_cost','evaluation__discount','evaluation__total_cost','amount_paid','payment_type','created','remining_amount').order_by('-id')
	
		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[2] not in found:
				order_list = list(order)

				order_completion_date = OrderScheduler.objects.filter(is_active=True,order__order_no=order_list[4]).last()
				followup_completion_date = FollowUpScheduler.objects.filter(is_active=True,follow_up__investigation__order__order_no=order_list[4]).last()

				order_cleaning_policy = OrderScheduler.objects.filter(is_active=True,order__order_no=order_list[4],order_scheduler_book__cleaning_policy='SUBSCRIPTION').first()
				
				payment_date = PaymentHistory.objects.filter(is_active=True,order__order_no=order_list[4]).last()

				if order_cleaning_policy != None:
					if followup_completion_date != None :
						order_list[8] = followup_completion_date.end_at
					else:
						if order_completion_date != None :
							order_list[8] = order_completion_date.end_at
						else:
							order_list[8] = '-'

					if payment_date != None:
						order_list[15] = payment_date.paid_date
					else:
						order_list[15] = '-'

					order_list[4] = order_list[4][9:]
					order = tuple(order_list)
					rows.append(order)
				else:
					pass
	
			found.add(order[2])
	
	if report_type == 'customer':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="CUSTOMER_PAYMENTS_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Payments')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Customer Name','Quotation No.','Payment Policy',
		'Net Amount','Paid Amount','Payment Type','Date of Payment']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).values_list('created','evaluation__customer__name','order_no', 'evaluation__payment_method','evaluation__total_cost','amount_paid','payment_type','history_order__paid_date').order_by('-id')

		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[2] not in found:
				rows.append(order)
			found.add(order[2])
	
	if report_type == 'customeroutstanding':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="CUSTOMER_OUTSTANDING_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('CUSTOMER OUTSTANDING')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Customer Name','Quotation No.','Invoice No.','Job Status',
		'Job Completion Date','Payment Policy','Net Amount','Paid Amount',
		'Payment Type','Date of Payment','Balance to Collect']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status'),payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).values_list('created','evaluation__customer__name','order_no','order_no', 'job_status', 'order_scheduler_order__end_at', 'evaluation__payment_method' ,'evaluation__total_cost','amount_paid','payment_type','history_order__paid_date','remining_amount').order_by('-id')

		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[2] not in found:

				order_list = list(order)

				order_completion_date = OrderScheduler.objects.filter(is_active=True,order__order_no=order_list[3]).last()
				followup_completion_date = FollowUpScheduler.objects.filter(is_active=True,follow_up__investigation__order__order_no=order_list[3]).last()

				
				if followup_completion_date != None :
					order_list[5] = followup_completion_date.end_at
				else:
					if order_completion_date != None :
						order_list[5] = order_completion_date.end_at
					else:
						order_list[5] = '-'
					

				order_list[3] = order_list[3][9:]
				order = tuple(order_list)
				rows.append(order)

			found.add(order[2])


	rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
	for row in rows:
		row_num += 1
		for col_num in range(len(row)):
			ws.write(row_num, col_num, row[col_num], font_style)

	wb.save(response)

	print(response.status_code,"resp")
	
	return response


	