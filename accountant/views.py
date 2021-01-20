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
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,PaymentSubscriptionDetails,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia
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

		order = Order.objects.select_related('evaluation__customer','evaluation__call_attender').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('customer_address__area','customer_address','order_scheduler_book__service_type'),to_attr='order_secheduler_feedback'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules'),Prefetch('ordersubscription',queryset=PaymentSubscriptionDetails.objects.filter(is_paid=False,is_active=True),to_attr='subscriptions')).annotate(total_cleaners=Sum('order_scheduler_order__order_scheduler_book__number_of_cleaners')).annotate(Count('order_scheduler_order')).get(id=order_id,is_active=True)

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

		#for subscription
		if order.subscriptions and (order.evaluation.payment_method == 'PREPAIDSUBSCRIPTION' or order.evaluation.payment_method == 'POSTPAIDSUBSCRIPTION'):
			if order.subscriptions[0]:
				dropdown_order_info['subscription_amount'] = order.subscriptions[0].amount
				dropdown_order_info['subscription_id']     = order.subscriptions[0].id			

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

		#Payment Details
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

		#Pending Payment and Order Count	
		if invoices:
			total_pending_amount = invoices.prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) )).aggregate(total=Sum(F('remining_amount')))['total']		
			total_pending_orders = invoices.prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) )).count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0

		
		#Pending Payments
		pending_payments = invoices.filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules'),Prefetch('ordersubscription',queryset=PaymentSubscriptionDetails.objects.filter(is_paid=False,is_active=True),to_attr='subscriptions')).annotate(Count('order_scheduler_order'))
			

		#remove object in postpaid if not last cleaning fulfilled	
		for payment in pending_payments:
			if payment.evaluation.payment_method == 'POSTPAID':
				very_latest_cleaning=payment.orderschedules[payment.order_scheduler_order__count-1]
				if very_latest_cleaning.work_status != 'CLEANING_FULFILLED':
					pending_payments = pending_payments.exclude(id=payment.id)

		#to find days
		for payment in pending_payments:
			if payment.evaluation.payment_method == 'PREPAID' and payment.orderschedules:
				very_old_cleaning   = payment.orderschedules[0]
				payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
			elif payment.evaluation.payment_method == 'POSTPAID' and payment.orderschedules:
				very_latest_cleaning=payment.orderschedules[payment.order_scheduler_order__count-1]
				payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	
			elif payment.evaluation.payment_method == 'BREAKDOWN' and payment.orderschedules:
			
				very_old_cleaning   = payment.orderschedules[0]
				very_latest_cleaning=payment.orderschedules[payment.order_scheduler_order__count-1]
				payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
				payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	

				#to check last cleaning completed for break down after payment
				if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
					payment.last_completed = True	

			elif payment.evaluation.payment_method == 'PREPAIDSUBSCRIPTION' and payment.subscriptions:
				if payment.subscriptions[0]:
					month = int(payment.subscriptions[0].monthyear.split('-')[0])
					year  = int(payment.subscriptions[0].monthyear.split('-')[1])
					
					if timezone.now().replace(hour=0,minute=0,second=0,microsecond=0) <= timezone.now().replace(day=1,month=month,year=year,hour=0,minute=0,second=0,microsecond=0):
						payment.reminigdays = ((timezone.now().replace(day=1,month=month,year=year,hour=0,minute=0,second=0,microsecond=0))-(timezone.now().replace(hour=0,minute=0,second=0,microsecond=0))).days	
					else:
						payment.delaydays   = ((timezone.now().replace(hour=0,minute=0,second=0,microsecond=0))-(timezone.now().replace(day=1,month=month,year=year,hour=0,minute=0,second=0,microsecond=0))).days	

			elif payment.evaluation.payment_method == 'POSTPAIDSUBSCRIPTION' and payment.subscriptions:
				if payment.subscriptions[0]: 				
					if int(payment.subscriptions[0].monthyear.split('-')[0]) == 12:
						month = 1
						year  = int(payment.subscriptions[0].monthyear.split('-')[0])+1
					else:
						month = int(payment.subscriptions[0].monthyear.split('-')[0])+1
						year  = int(payment.subscriptions[0].monthyear.split('-')[1]) 	
					if timezone.now().replace(hour=0,minute=0,second=0,microsecond=0) <= timezone.now().replace(day=1,month=month,year=year,hour=0,minute=0,second=0,microsecond=0):
						payment.reminigdays = ((timezone.now().replace(day=1,month=month,year=year,hour=0,minute=0,second=0,microsecond=0))-(timezone.now().replace(hour=0,minute=0,second=0,microsecond=0))).days	
					else:
						payment.delaydays   = ((timezone.now().replace(hour=0,minute=0,second=0,microsecond=0))-(timezone.now().replace(day=1,month=month,year=year,hour=0,minute=0,second=0,microsecond=0))).days	

		#buybackgiftpromos		
		approved_paybackdiscounts = Investigation.objects.filter(is_paybackdiscount_approved=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True),to_attr='followup'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.select_related('investigation').filter(is_active=True,investigation__is_paybackdiscount_approved=True,is_completed=False),to_attr='paybackdiscounts'))
		#add days left
		for ticket in approved_paybackdiscounts:
			ticket.days_left = (timezone.now()-ticket.scheduled_at).days

		return render(request,'accountant/home/home.html',{"this_week_sales":this_week_sales,"last_week_sales":last_week_sales,"this_month_sales":this_month_sales,"last_month_sales":last_month_sales,"this_quarter_sales":this_quarter_sales,"last_quarter_sales":last_quarter_sales,"pending_payments":pending_payments,'total_pending_amount':total_pending_amount,"total_pending_orders":total_pending_orders,"approved_paybackdiscounts":approved_paybackdiscounts,})

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

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True),to_attr='paybackdiscounts'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True),to_attr='buybackpromocodegift'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)
			

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=order.evaluation.customer_id)
		except:
			client_details = None

		#orders count
		orders = Order.objects.filter(is_active=True,evaluation__customer_id=order.evaluation.customer_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()
					
				
		return render(request,"accountant/client/order-page.html",{"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count})

class PaymentEdit(IsAccountant,View):

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

		return render(request,'accountant/payment/payment_edit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})	

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

		return redirect('accountant:accountant-client-orderdetails',order.id)

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
		#for order filtering
		status = request.GET.get('status')
		
		if search:
			evaluations = Evaluation.objects.filter(is_active=True).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(customer__mobile_number__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
		else:
			evaluations = Evaluation.objects.filter(is_active=True).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
			

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

		
		
		fil_status = request.GET.get('status')
		fil_payment_policy		= request.GET.get('payment_policy')
		#filters
		filters=[]
		if fil_status:
			if fil_status == 'ORDER_IN_PROGRESS' or fil_status == 'ORDER_CLOSED' or fil_status == 'APPROVED-NOT PAID' or fil_status == 'EVALUATING':
				if fil_status == 'ORDER_IN_PROGRESS':
					case1 = Q(order_in_progress_count__gte=1)
				elif fil_status == 'ORDER_CLOSED':
					case1 = Q(order_closed_count__gte=1)
				elif fil_status == 'APPROVED-NOT PAID':
					case1 = Q(approved_not_paid_count__gte=1)
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

		return render(request,'accountant/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy})		


class PaymentDetails(IsAccountant,View):
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
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         = None
		else:
			try:
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
			except:
				invoices         = None
				
		#Pending Payments
		try:
			pending_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) ))
		except:
			pending_payments = None

		#Pending Payment and Order Count	
		if pending_payments: 
			total_pending_amount = pending_payments.aggregate(total=Sum(F('remining_amount')))['total']		
			total_pending_orders = pending_payments.count()
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
				case2       = Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) )
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

		return render(request,'accountant/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"service_types":service_types,"fil_payment_policy":fil_payment_policy,"fil_payment_status":fil_payment_status,"fil_order_status":fil_order_status})

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
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
				elif payment_policy == 'BEFORE CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=amount)
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
				elif payment_policy == 'AFTER CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=amount)
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
				elif payment_policy == 'PREPAIDSUBSCRIPTION':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount)
					subscription_id = request.POST.get('subscription')
					PaymentSubscriptionDetails.objects.filter(id=subscription_id).update(is_paid=True)
				elif payment_policy == 'POSTPAIDSUBSCRIPTION':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount)
					subscription_id = request.POST.get('subscription')
					PaymentSubscriptionDetails.objects.filter(id=subscription_id).update(is_paid=True)
				
				messages.success(request,"Payment Received thruogh Cash")

			if payment_method == 'CHEQUE':
				check_no   = request.POST.get('check_number')
				check_date = datetime.strptime(request.POST.get('check_date'),'%d-%m-%Y')

				if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount,remining_amount=0) 
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
				elif payment_policy == 'BEFORE CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=amount)
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
				elif payment_policy == 'AFTER CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=amount)
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
				elif payment_policy == 'PREPAIDSUBSCRIPTION':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount)
					subscription_id = request.POST.get('subscription')
					PaymentSubscriptionDetails.objects.filter(id=subscription_id).update(is_paid=True)
				elif payment_policy == 'POSTPAIDSUBSCRIPTION':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount)
					subscription_id = request.POST.get('subscription')
					PaymentSubscriptionDetails.objects.filter(id=subscription_id).update(is_paid=True)
				
				messages.success(request,"Payment Received thruogh Cheque")

			if payment_method == 'BANK':
				bank_name   = request.POST.get('bank_name')
				bank_no     = request.POST.get('ibn_number')

				if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount,remining_amount=0) 
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)
				elif payment_policy == 'BEFORE CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=amount)
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)
				elif payment_policy == 'AFTER CLEANING':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=amount)
					PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)
				elif payment_policy == 'PREPAIDSUBSCRIPTION':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount)
					subscription_id = request.POST.get('subscription')
					PaymentSubscriptionDetails.objects.filter(id=subscription_id).update(is_paid=True)
				elif payment_policy == 'POSTPAIDSUBSCRIPTION':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount)
					subscription_id = request.POST.get('subscription')
					PaymentSubscriptionDetails.objects.filter(id=subscription_id).update(is_paid=True)

				messages.success(request,"Payment Received through Bank")

			is_payment_completed = Order.objects.get(id=order_id)

			if is_payment_completed.amount_paid == is_payment_completed.total_amount:
				is_payment_completed.payment_completed_date = payment_date 
				is_payment_completed.payment_status         = 'COMPLETED'
				is_payment_completed.save()
		
		
			####to close order
			order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=order_id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
			if order_closing_check:
				closing_order	= Order.objects.get(is_active=True,order_no=evaluation_id)
				closing_order.order_status = 'ORDER_CLOSED'
				closing_order.save()
		else:
			messages.suucess(request,"Something Went Wrong")

		return redirect('accountant:accountant-cashcollect')

class PaybackDiscountProcessing(View):
	def get(self,request,paybackdiscount_id):
		
		try:
			paybackdiscount_details_data = PaybackDiscount.objects.select_related('investigation__order__evaluation__customer','investigation__order_schedule__customer_address','investigation__order_schedule__order_scheduler_book','investigation__order_schedule__evaluation_details__evaluator').prefetch_related(Prefetch('investigation__followup_investigation',queryset=FollowUp.objects.filter(is_active=True),to_attr='followup'),Prefetch('investigation__order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_teams')).get(id=paybackdiscount_id)
		except:
			paybackdiscount_details_data = None

		ticket_types = paybackdiscount_details_data.investigation.ticket_types.split(",")
		ticket_types_list = []
		for type in ticket_types:
			ticket_types_list.append(type)
		
		paybackdiscount 		= PaybackDiscount.objects.get(is_active=True,id=paybackdiscount_id)
		paybackdiscount_details = PaybackDiscountDetails.objects.filter(is_active=True,paybackdiscount=paybackdiscount)
		payback_servicequality 	= paybackdiscount_details.filter(category='SERVICEQUALITY')
		payback_damage 			= paybackdiscount_details.filter(category='DAMAGE')

		return render(request,'accountant/ticket/paybackdiscountprocess.html',{"ticket_types":ticket_types,"paybackdiscount":paybackdiscount,"paybackdiscount_details_data":paybackdiscount_details_data,"payback_servicequality":payback_servicequality,"payback_damage":payback_damage})

	def post(self,request,paybackdiscount_id):
		option = request.POST.get('approved_option')

		if option == 'PAYBACK':
			
			PaybackDiscount.objects.filter(id=paybackdiscount_id).update(approved_option=option,is_completed=True,accountant_notes=request.POST.get('accountant_notes'))

			messages.success(request,"Payback Succesfully Added")

		if option == 'DISCOUNT':
			
			PaybackDiscount.objects.filter(id=paybackdiscount_id).update(approved_option=option,is_completed=True,accountant_notes=request.POST.get('accountant_notes'))
			
			#update order and evaluation
			order_id      =  request.POST.get('order_id')
			evaluation_id =  request.POST.get('evaluation_id')
			
			Order.objects.filter(id=order_id).update(total_amount=F('total_amount')-float(request.POST.get('approved_total_cost')),remining_amount=F('remining_amount')-float(request.POST.get('approved_total_cost')))
			
			evaluation = Evaluation.objects.get(id=evaluation_id)
			evaluation.total_cost     = evaluation.total_cost-float(request.POST.get('approved_total_cost'))
			evaluation.discount       = evaluation.discount+float(request.POST.get('approved_total_cost'))
			evaluation.extra_discount = evaluation.extra_discount+float(request.POST.get('approved_total_cost'))
			if evaluation.payment_method == 'BREAKDOWN':
				evaluation.after_cleaning_amount = evaluation.after_cleaning_amount-float(request.POST.get('approved_total_cost'))
			evaluation.save()

			messages.success(request,"Discount Succesfully Added")

		return redirect('accountant:accountantdash-board')

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
	row_num2 = 0
	row_num3 = 0
	row_num4 = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	if report_type == 'paymentlist':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="GENERAL_PAYMENT_SHEET_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('GENERAL PAYMENT SHEET')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Quotation No.','Customer Name','Payment Policy','Amount','Paid Amount','Balance','Payment Mode','Job Status']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(job_status=Concat('order_scheduler_order__work_status',Value(' , '),'investigation_orders__followup_investigation__status'),payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).values_list('created','order_no','evaluation__customer__name', 'evaluation__payment_method','evaluation__total_cost','amount_paid','remining_amount','payment_type','job_status').order_by('-id')
	
		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[1] not in found:
				rows.append(order)
			found.add(order[1])

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)
	
	
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

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

	
	
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

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)


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

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)
	
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

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(total_jobs=Count('order_scheduler_order') or 0 + Count('investigation_orders') or 0 , pending_jobs=Sum(Case(When(Q(investigation_orders__followup_investigation__status='FOLLOWUP_IN_PROGRESS'),then=1),default=0,output_field=IntegerField())) + Sum(Case(When(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS'),then=1),default=0,output_field=IntegerField()))).values_list('created','evaluation__customer__name','order_no','evaluation__call_attender__name' , 'order_no', 'order_status', 'total_jobs', 'pending_jobs', 'created', 'evaluation__payment_method', 'evaluation__estimated_cost','evaluation__discount','evaluation__total_cost','amount_paid','created','created','remining_amount').order_by('-id')
	
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
				
					#job completion date
					if followup_completion_date != None :
						order_list[8] = followup_completion_date.end_at
					else:
						if order_completion_date != None :
							order_list[8] = order_completion_date.end_at
						else:
							order_list[8] = '-'

					#payment mode
					if payment_date != None:
						order_list[15] = payment_date.paid_date

						if payment_date.payment_mode != None:

							order_list[14] = payment_date.payment_mode

							# if payment_date.payment_gateway != None:
							# 	order_list[14] = payment_date.payment_gateway
							# else:
							# 	order_list[14] = '-'

						else:
							order_list[14] = '-'
						
					else:
						order_list[15] = '-'
						order_list[14] = '-'
					
					order_list[4] = order_list[4][9:]
					order = tuple(order_list)
					rows.append(order)
				else:
					pass

			found.add(order[2])

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)
	
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

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(total_jobs=Count('order_scheduler_order') or 0 + Count('investigation_orders') or 0 , pending_jobs=Sum(Case(When(Q(investigation_orders__followup_investigation__status='FOLLOWUP_IN_PROGRESS'),then=1),default=0,output_field=IntegerField())) + Sum(Case(When(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS'),then=1),default=0,output_field=IntegerField()))).values_list('created','evaluation__customer__name','order_no','evaluation__call_attender__name' , 'order_no', 'order_status', 'total_jobs', 'pending_jobs', 'created', 'evaluation__payment_method', 'evaluation__estimated_cost','evaluation__discount','evaluation__total_cost','amount_paid','created','created','remining_amount').order_by('-id')
	
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
						if payment_date.payment_mode != None:

							order_list[14] = payment_date.payment_mode

							# if payment_date.payment_gateway != None:
							# 	order_list[14] = payment_date.payment_gateway
							# else:
							# 	order_list[14] = '-'

						else:
							order_list[14] = '-'
					else:
						order_list[15] = '-'
						order_list[14] = '-'

					order_list[4] = order_list[4][9:]
					order = tuple(order_list)
					rows.append(order)
				else:
					pass
	
			found.add(order[2])

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)
	
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

		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end)).annotate(payment_type=Concat('history_order__payment_mode',Value(' '),'history_order__payment_gateway')).values_list('created','evaluation__customer__name','order_no', 'evaluation__payment_method','evaluation__total_cost','amount_paid','payment_type','history_order__paid_date').order_by('-id')

		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			if order[2] not in found:
				rows.append(order)
			found.add(order[2])

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)
	
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


	if report_type == 'transactionhistory':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="TRANSACTION_HISTORY_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		
		#online
		ws = wb.add_sheet('ONLINE',cell_overwrite_ok = True)
	
		columns = ['Transaction Date','Order No.','Payment Policy','Invoice No.','Transaction Amount',
		'Transaction ID','Payment Method','Receipt No.']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		payments = PaymentHistory.objects.filter(is_active=True,payment_mode='ONLINECREDIT',created__range=(prev_date_start,todate_date_end)).values_list('paid_date','order__order_no','order__evaluation__payment_method','amount_paid','amount_paid','transaction_id', 'payment_gateway', 'receipt_no').order_by('-id')

		rows = []

		for pay in payments:
			pay_list = list(pay)

			pay_list[3] = pay_list[1][9:]
			pay = tuple(pay_list)
			rows.append(pay)

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

		#cash sheet
		ws2 = wb.add_sheet('CASH',cell_overwrite_ok = True)
	
		columns2 = ['Transaction Date','Order No.','Payment Policy','Invoice No.','Transaction Amount','Payment Method','Receipt No.']
		
		for col_num in range(len(columns2)):
			ws2.write(row_num2, col_num, columns2[col_num], font_style)

		payments2 = PaymentHistory.objects.filter(is_active=True,payment_mode='CASH',created__range=(prev_date_start,todate_date_end)).values_list('paid_date','order__order_no','order__evaluation__payment_method','amount_paid','amount_paid', 'payment_mode' , 'receipt_no').order_by('-id')

		
		print(payments2,"payss")

		rows2 = []

		for pay in payments2:
			pay_list = list(pay)

			pay_list[3] = pay_list[1][9:]
			pay = tuple(pay_list)
			rows2.append(pay)

		rows2 = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows2 ]

		print(rows2,"ross2")

		for row in rows2:
			row_num2 += 1
			for col_num in range(len(row)):
				ws2.write(row_num2, col_num, row[col_num], font_style)

		#CHEQUE sheet
		ws3 = wb.add_sheet('CHEQUE',cell_overwrite_ok = True)
	
		columns3 = ['Transaction Date','Order No.','Payment Policy','Invoice No.','Transaction Amount','Cheque Number','Cheque Date','Payment Method','Receipt No.']
		
		for col_num in range(len(columns3)):
			ws3.write(row_num3, col_num, columns3[col_num], font_style)

		payments3 = PaymentHistory.objects.filter(is_active=True,payment_mode='CHEQUE',created__range=(prev_date_start,todate_date_end)).values_list('paid_date','order__order_no','order__evaluation__payment_method','amount_paid','amount_paid', 'check_no', 'check_date', 'payment_mode', 'receipt_no').order_by('-id')

		rows3 = []

		for pay in payments3:
			pay_list = list(pay)

			pay_list[3] = pay_list[1][9:]
			pay = tuple(pay_list)
			rows3.append(pay)

		rows3 = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows3 ]

		for row in rows3:
			row_num3 += 1
			for col_num in range(len(row)):
				ws3.write(row_num3, col_num, row[col_num], font_style)

		#bank transfer sheet
		ws4 = wb.add_sheet('BANK TRANSFER',cell_overwrite_ok = True)
	
		columns4 = ['Transaction Date','Order No.','Payment Policy','Invoice No.','Transaction Amount','Bank Name','IBAN number','Payment Method','Receipt No.']
		
		for col_num in range(len(columns4)):
			ws4.write(row_num4, col_num, columns4[col_num], font_style)

		payments4 = PaymentHistory.objects.filter(is_active=True,payment_mode='BANK',created__range=(prev_date_start,todate_date_end)).values_list('paid_date','order__order_no','order__evaluation__payment_method','amount_paid','amount_paid', 'bank_name', 'bank_no', 'payment_mode', 'receipt_no').order_by('-id')

		rows4 = []

		for pay in payments4:
			pay_list = list(pay)

			pay_list[3] = pay_list[1][9:]
			pay = tuple(pay_list)
			rows4.append(pay)

		rows4 = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows4 ]

		for row in rows4:
			row_num4 += 1
			for col_num in range(len(row)):
				ws4.write(row_num4, col_num, row[col_num], font_style)	

	if report_type == 'salesdetails':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="SALES_DETAILS_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		
		#sales details
		ws = wb.add_sheet('SALES DETAILS',cell_overwrite_ok = True)
	
		columns = ['Order No.','Cleaning Date','Final Cleaning of service','Day','Customer','Payment Policy','Net Amount','Paid Amount','Payment Type','Payment Date','Balance Amount','Service Type','Cleaning Policy','Hours','Staff','Salesman']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		orderschedules = OrderScheduler.objects.filter(is_active=True,work_status='CLEANING_FULFILLED',end_at__range=(prev_date_start,todate_date_end)).values_list('order__order_no','end_at','end_at','id','evaluation_details__address__customer__name','evaluation_details__evaluation__payment_method','order_scheduler_book__total_cost','order__amount_paid','evaluation_details__evaluation__payment_way','order_scheduler_book__id','order__remining_amount','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__cleaning_hours','order_scheduler_book__number_of_cleaners','evaluation_details__evaluator__name').order_by('end_at')

		rows = []

		for schedule in orderschedules:

			schedule_list = list(schedule)

			calc_orderschedules = OrderScheduler.objects.filter( order__order_no = schedule_list[0]  )
			
			multi_service = calc_orderschedules.filter(order_scheduler_book__id=schedule_list[9])
			multi_service_count = multi_service.count()
			multi_service_last = multi_service.last()

			orderschedules_count = calc_orderschedules.count()
			last_orderschedule = calc_orderschedules.last()

			print(orderschedules_count,last_orderschedule,"osh")

			orderschedule = OrderScheduler.objects.get(id=int(schedule_list[3]))

			if multi_service_count > 0:
				if multi_service_last.order_scheduler_book.id == orderschedule.order_scheduler_book.id:
					schedule_list[2] = multi_service_last.end_at
			else:
				schedule_list[2] = last_orderschedule.end_at
			

			#splitting paid amount and balance
			if orderschedules_count > 0:
				#splitting service cost for multi cleaning and subscription
				if multi_service_count > 0:
					
					if multi_service_last.id == orderschedule.id:
					
						schedule_list[6] = int(schedule_list[6] / multi_service_count) + float( schedule_list[6] % multi_service_count )

					else:

						schedule_list[6] = int(schedule_list[6] / multi_service_count)
				else:
					pass

				if schedule_list[5] == 'BREAKDOWN':
					if last_orderschedule.id == orderschedule.id:
						schedule_list[7] = int(schedule_list[7] / orderschedules_count) + float( schedule_list[7] % orderschedules_count )
						
						if schedule_list[10] > 0:
							schedule_list[10] = int(schedule_list[10] / orderschedules_count) + float( schedule_list[10] % orderschedules_count )

					else:
						schedule_list[7] = int(schedule_list[7] / orderschedules_count)

						if schedule_list[10] > 0:
							schedule_list[10] = int(schedule_list[10] / orderschedules_count)

					#multiple cleaning and subscription paid amount and balance split
					if multi_service_count > 0:
					
						if multi_service_last.id == orderschedule.id:
							schedule_list[7] = int(schedule_list[7] / multi_service_count) + float( schedule_list[7] % multi_service_count )
						
							if schedule_list[10] > 0:
								schedule_list[10] = int(schedule_list[10] / multi_service_count) + float( schedule_list[10] % multi_service_count )

						else:
							schedule_list[7] = int(schedule_list[7] / multi_service_count)

							if schedule_list[10] > 0:
								schedule_list[10] = int(schedule_list[10] / multi_service_count)
					else:
						pass


				elif schedule_list[5] == 'PREPAID' or schedule_list[5] == 'PREPAIDUBSCRIPTION':
					if schedule_list[10] == 0.00 :
						schedule_list[7] = schedule_list[6]
					else:
						schedule_list[10] = schedule_list[6]

				elif schedule_list[5] == 'POSTPAID' or schedule_list[5] == 'POSTPAIDUBSCRIPTION':
					if schedule_list[7] == 0.00 :
						schedule_list[10] = schedule_list[6]
					else:
						schedule_list[7] = schedule_list[6]
					
				else:
					pass

			else:
				pass

			paymenthistory = PaymentHistory.objects.filter(order__order_no=schedule_list[0]).last()

			#adding payment date and payment mode
			if orderschedule.evaluation_details.evaluator == None :
				schedule_list[15] = orderschedule.evaluation_details.evaluation.call_attender.name

			if paymenthistory:
				if paymenthistory.payment_mode == 'ONLINECREDIT':
					schedule_list[8] = paymenthistory.payment_gateway
				else:
					schedule_list[8] = paymenthistory.payment_mode

				schedule_list[9] = paymenthistory.paid_date
			else:
				schedule_list[8] = '-'
				schedule_list[9] = '-'

			schedule_list[3] = schedule_list[1].strftime("%A")
			schedule = tuple(schedule_list)
			rows.append(schedule)
		
		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]

		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

		#sales report
		ws2 = wb.add_sheet('SALES REPORT',cell_overwrite_ok = True)
	
		columns2 = ['Date','Day','General Cleaning','Deep Cleaning','Sanitization','Carpet Cleaning','Upholstery Cleaning','Kitchen Cleaning','Grand Total']
		
		for col_num in range(len(columns2)):
			ws2.write(row_num2, col_num, columns2[col_num], font_style)

		#creating date list
		found = set()

		dates = []

		for cln_date in rows:
			ro = list(cln_date)

			if ro[1] not in found:
				dates.append(ro[1])
				found.add(ro[1])

			print(dates,"dts")

		#appending data to list
		rows2 = []

		for d in dates:

			grand_total = 0

			general = 0
			upholstery = 0
			deep = 0
			sterilization = 0
			carpet = 0
			kitchen = 0
			
			test_elem = d

			#filtering rows list using date
			res = [item for item in rows if item[1] == d ]

			#calculating service totals and grand total
			for r in res:
				day_name = r[3]

				if r[11] == 'General Cleaning':
					general += float(r[6])

				if r[11] == 'Deep Cleaning':
					deep += float(r[6]) 

				if r[11] == 'Sterilization':
					sterilization += float(r[6]) 

				if r[11] == 'Carpet Cleaning':
					carpet += float(r[6]) 

				if r[11] == 'Upholstery Cleaning':
					upholstery += float(r[6]) 

				if r[11] == 'Kitchen Cleaning':
					kitchen += float(r[6])

				grand_total += r[6]

			daily_report = (d, day_name, general, deep, sterilization, carpet, upholstery, kitchen, grand_total)

			rows2.append(daily_report)

		for row in rows2:
			row_num2 += 1
			for col_num in range(len(row)):
				ws2.write(row_num2, col_num, row[col_num], font_style)

	if report_type == 'orderhistory':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="ORDER_HISTORY_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		
		#sales details
		ws = wb.add_sheet('ORDER HISTORY',cell_overwrite_ok = True)
	
		columns = ['Quotation Date','Order No.','Customer ID','Customer Name','Type of Service','Cleaning Policy','Payment Policy','Job Starting Date','Total Amount','Discount','Net Amount','Quotation Status','Evaluator']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		evaluations = Evaluation.objects.filter(is_active=True,evaluation_order__is_active=True,evaluation_order__created__range=(prev_date_start,todate_date_end)).values_list('evaluation_order__created','evaluation_id','customer__customer_id','customer__name','id','id','payment_method','id','evaluation_details__estimated_cost','evaluation_details__discount','evaluation_details__total_cost','id','evaluation_details__evaluator__name')
		
		rows = []
		
		for evaluation in evaluations:
			evaluation_list = list(evaluation)
			
			#cleaning policy, service type
			evaluationbooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation__id=int(evaluation_list[11])).values('cleaning_policy','service_type__name')
			print(evaluationbooks,"ebooks")

			found = set()
			servicetypes = []
			cleaning_policies = []

			for ebook in evaluationbooks:
				if ebook['service_type__name'] not in found:
					servicetypes.append(ebook['service_type__name'])
					servicetypes.append(', ')
					found.add(ebook['service_type__name'])
				
				if ebook['cleaning_policy'] not in found:
					cleaning_policies.append(ebook['cleaning_policy'])
					cleaning_policies.append(', ')
					found.add(ebook['cleaning_policy'])

			evaluation_list[4] = tuple(servicetypes)
			evaluation_list[5] = tuple(cleaning_policies)

			#job starting date
			orderschedule = OrderScheduler.objects.filter(is_active=True,evaluation_details__evaluation__id=int(evaluation_list[11])).values('start_at').first()
			
			print(orderschedule,"osched")
			if orderschedule:
				evaluation_list[7] = orderschedule['start_at']
			else:
				evaluation_list[7] = '-'

			#evaluator
			evaluationdetails = EvaluationDetails.objects.filter(is_active=True,evaluation__id=int(evaluation_list[11])).values('evaluator__name','evaluation__call_attender__name')
			
			evaluators = []
			for detail in evaluationdetails:
				if evaluationdetails.last:
					print("last")
				else:
					print("raam")

				if detail['evaluator__name'] != None:
					if detail['evaluator__name'] not in found:
						evaluators.append(detail['evaluator__name'])
						evaluators.append(',')
						found.add(detail['evaluator__name'])
				else:
					if detail['evaluation__call_attender__name'] not in found:
						evaluators.append(detail['evaluation__call_attender__name'])
						evaluators.append(',')
						found.add(detail['evaluation__call_attender__name'])
					
				
			evaluation_list[12] = tuple(evaluators)


			#quotation status
			order = Order.objects.filter(is_active=True,evaluation__id=int(evaluation_list[11])).values('evaluation__quatation_status','payment_status','preamount_paid','order_status').first()
			
			if order:
				if order['evaluation__quatation_status'] == 'APPROVED':
					if order['payment_status'] == 'COMPLETED' or order['preamount_paid'] != 0 or evaluation_list[6] == 'POSTPAID':
						if order['order_status'] == 'APPROVED_BY_CLIENT':
							evaluation_list[11] = 'APPROVED'
						elif order['order_status'] == 'ORDER_IN_PROGRESS':
							evaluation_list[11] = 'ORDER IN PROGRESS'
						elif order['order_status'] == 'ORDER_CLOSED':
							evaluation_list[11] = 'COMPLETED'
						else:
							evaluation_list[11] = '-'
					else:
						evaluation_list[11] = 'APPROVED-NOT PAID'

				elif order['evaluation__quatation_status'] == 'REJECTED':
					evaluation_list[11] = 'REJECTED'
				elif order['evaluation__quatation_status'] == 'PENDING':
					evaluation_list[11] = 'PENDING'
				elif order['evaluation__quatation_status'] == 'EXPIRED':
					evaluation_list[11] = 'EXPIRED'
				else:
					evaluation_list[11] = 'EVALUATING'
			else:
				evaluation_list[11] = '-'

			evaluation = tuple(evaluation_list)
			rows.append(evaluation)
		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]

		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

	wb.save(response)

	print(response.status_code,"resp")
	
	return response


	