from django.shortcuts import render,redirect,render_to_response
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsAccountant
# Create your views here.
import pandas as pd
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
from django.db.models.functions import ExtractMonth,ExtractYear

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia,CancellOrderAmountHistory
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from Api.models import XeroConnection

import requests
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect

from user.models import UserProfile,LeaveSchedule

def GetCashCollectOrderInfo(request):
	data               = {}
	order_info_dict = {}

	query       =   request.GET.get('keyword')

	orders = Order.objects.filter(is_active=True,order_status__isnull=False).filter(Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))).select_related('evaluation__customer').filter(Q(Q(evaluation__quatation_status='APPROVED') & Q(Q(evaluation__evaluation_id__icontains=query)|Q(evaluation__customer__name__icontains=query)) & ~Q(Q(order_status='ORDER_CANCELLED'))) | Q(Q(evaluation__quatation_status='APPROVED') & Q(Q(evaluation__evaluation_id__icontains=query)|Q(evaluation__customer__name__icontains=query)) & Q(order_status='CANCEL_IN_PROGRESS')) ).prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules')).annotate(Count('order_scheduler_order'))
			
	
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

		order = Order.objects.select_related('evaluation__customer','evaluation__call_attender').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('customer_address__area','customer_address','order_scheduler_book__service_type'),to_attr='order_secheduler_feedback'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules'),).annotate(total_cleaners=Sum('order_scheduler_order__order_scheduler_book__number_of_cleaners')).annotate(Count('order_scheduler_order')).get(id=order_id,is_active=True)

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
		try:
			dropdown_order_info['agent_image_url']	= order.evaluation.call_attender.profile_image.url
		except:
			dropdown_order_info['agent_image_url']  = None
		try:
			dropdown_order_info['agent_name']       = order.evaluation.call_attender.name
		except:
			dropdown_order_info['total_cleaners'] 	= None

		dropdown_order_info['remining_amount']     = order.remining_amount
		dropdown_order_info['before_amount']       = order.evaluation.before_cleaning_amount 
		dropdown_order_info['after_amount']        = order.evaluation.after_cleaning_amount
		dropdown_order_info['before_amount_paid']  = order.preamount_paid 
		dropdown_order_info['after_amount_paid']   = order.postamount_paid		

		#for subscription
		if order.evaluation.payment_method == 'SUBSCRIPTION':
			dropdown_order_info['subscription_amount'] = order.subscription_topay			

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

		print(dropdown_order_info)
		return JsonResponse(dropdown_order_info)	

def GetFineCollectOrderInfo(request):
	data               = {}
	order_info_dict = {}

	query       =   request.GET.get('keyword')

	orders = Order.objects.filter(is_active=True,order_status__isnull=False).select_related('evaluation__customer').filter(Q(evaluation__quatation_status='APPROVED') & Q(Q(evaluation__evaluation_id__icontains=query)|Q(evaluation__customer__name__icontains=query)) & ~Q(Q(order_status='ORDER_CANCELLED'))).prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).order_by('start_at'),to_attr='orderschedules')).annotate(Count('order_scheduler_order'))
			
	
	if orders:
		for order in orders:
			order_info_dict[order.id] = order.evaluation.evaluation_id+'-'+order.evaluation.customer.name 	

	
	data['order_details'] = order_info_dict


	data['status']     = 'true'

	if order_info_dict == {}: 
		data['status'] = 'false'	
	
	return JsonResponse(data)

class AccountantHome(IsAccountant,View):
	def get(self,request):


		#Payment Details
		search                  = request.GET.get('search')

		#sales amount
		try:
			invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
		except:
			invoices         = None

		#Payment Details
		payment_history = PaymentHistory.objects.filter(is_active=True)
		##week
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)		
		this_week_sales = payment_history.filter(paid_date__week=count_today_start.isocalendar()[1],paid_date__year=count_today_start.year).aggregate(total=Sum('amount_paid'))['total']
		last_week_sales = payment_history.filter(paid_date__week=count_today_start.isocalendar()[1]-1,paid_date__year=count_today_start.year).aggregate(total=Sum('amount_paid'))['total']				
		##month		
		prvmonth  = count_today_start-relativedelta(months=1)
		this_month_sales=payment_history.filter(paid_date__month=count_today_start.month,paid_date__year=count_today_start.year).aggregate(total=Sum('amount_paid'))['total']
		last_month_sales=payment_history.filter(paid_date__month=prvmonth.month,paid_date__year=prvmonth.year).aggregate(total=Sum('amount_paid'))['total']	
		

		##quarter
		curquarter      = []
		prvquarter      = []
		curquarternumber= int((count_today_start.month-1)/3)+1
		prvquarternumber= curquarternumber-1
		
		if prvquarternumber == 0:
			prvquarternumber = 4
			prvquarteryear   = (count_today_start.year)-1
		else:	
			prvquarteryear   = count_today_start.year

		#cur quarter
		if curquarternumber == 1:
			curquarter=[1,2,3]
		if curquarternumber == 2:
			curquarter=[4,5,6]
		if curquarternumber == 3:
			curquarter=[7,8,9]
		if curquarternumber == 4:
			curquarter=[10,11,12]

		#prv quarter
		if prvquarternumber == 1:
			prvquarter=[1,2,3]
		if prvquarternumber == 2:
			prvquarter=[4,5,6]
		if prvquarternumber == 3:
			prvquarter=[7,8,9]
		if prvquarternumber == 4:
			prvquarter=[10,11,12]
			

		this_quarter_sales=payment_history.filter(paid_date__month__in=curquarter,paid_date__year=count_today_start.year).aggregate(total=Sum('amount_paid'))['total']
		last_quarter_sales=payment_history.filter(paid_date__month__in=prvquarter,paid_date__year=prvquarteryear).aggregate(total=Sum('amount_paid'))['total']	


		#due payments calculation

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


		#Due Payment and Order Count			
		# total_due_amount = due_payments.aggregate(Sum('remining_amount'))['remining_amount__sum']
		# total_due_orders = due_payments.count()

		total_due_amount = total_doubtful_due_amount+total_normal_due_amount+total_subscription_due_amount
		total_due_orders = total_doubtful_due_orders+total_normal_due_orders+total_subscription_due_orders
		
		#Pending Payments
		pending_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) ))

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

		#subscriptions
		subscriptions = Order.objects.filter(Q(Q( Q(payment_status='PENDING') |Q(payment_status='ON_HOLD') ) & Q(evaluation__payment_method='SUBSCRIPTION'))).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())) )
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

		#buybackgiftpromos		
		# approved_paybackdiscounts = Investigation.objects.filter(is_paybackdiscount_approved=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True),to_attr='followup'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.select_related('investigation').filter(is_active=True,investigation__is_paybackdiscount_approved=True,is_completed=False),to_attr='paybackdiscounts')).annotate(paybackdiscount_count=Case(When(Q( Q(paybackdiscount_investigation__is_active=True) & Q(paybackdiscount_investigation__investigation__is_paybackdiscount_approved=True) & Q(paybackdiscount_investigation__is_completed=False) ),then=1),default=0,output_field=IntegerField()))
		approved_paybackdiscounts = Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True),to_attr='followup'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.select_related('investigation').filter(is_active=True,is_completed=False),to_attr='paybackdiscounts')).annotate(paybackdiscount_count=Case(When(Q( Q(paybackdiscount_investigation__is_active=True) & Q(paybackdiscount_investigation__is_completed=False) ),then=1),default=0,output_field=IntegerField()))
		ticket_count = 0
		#add days left
		if approved_paybackdiscounts:
			for ticket in approved_paybackdiscounts:
				ticket.days_left = (timezone.now()-ticket.scheduled_at).days
				
				for discount in ticket.paybackdiscounts:
					ticket_count += 1

		print(approved_paybackdiscounts,ticket_count,"tot")

		#order cancell cashback
		order_cancell_cashbacks = CancellOrderAmountHistory.objects.filter(amount_return_method='CASHBACK',is_completed=False).select_related('order__evaluation__customer').prefetch_related('order__order_scheduler_order__order_scheduler_book')
		
		for order_cancell_cashback in order_cancell_cashbacks:
			cleaning_price = 0
			for scheduler in order_cancell_cashback.order.order_scheduler_order.all():
				if scheduler.work_status=='CLEANING_FULFILLED':
					cleaning_price += scheduler.order_scheduler_book.total_cost/len(order_cancell_cashback.order.order_scheduler_order.all())			
			order_cancell_cashback.job_completed_amount = cleaning_price

		xero          = XeroConnection.objects.first()

		return render(request,'accountant/home/home.html',{"this_week_sales":this_week_sales,"last_week_sales":last_week_sales,"this_month_sales":this_month_sales,"last_month_sales":last_month_sales,"this_quarter_sales":this_quarter_sales,"last_quarter_sales":last_quarter_sales,"pending_payments":pending_payments,'total_due_amount':total_due_amount,"total_due_orders":total_due_orders,"approved_paybackdiscounts":approved_paybackdiscounts,"subscriptions":subscriptions,"ticket_count":ticket_count,"order_cancell_cashbacks":order_cancell_cashbacks,"xero":xero})

	

class ActiveSubscriptions(IsAccountant,View):
	def get(self,request):
		#subscriptions

		#Evaluation Details
		search                  = request.GET.get('search')
		
		if search:
			subscriptions = Order.objects.filter(Q(Q( Q(payment_status='PENDING') | Q(payment_status='ON_HOLD') | Q(payment_status='COMPLETED') ) & Q(evaluation__payment_method='SUBSCRIPTION') & Q(evaluation__quatation_status='APPROVED') & ~Q(order_status='ORDER_CANCELLED') & Q(Q(order_no__icontains=search)|Q(evaluation__customer__name__icontains=search)|Q(evaluation__customer__mobile_number__icontains=search)) )).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') ))   #Sum(Case(When( Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED') | Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS') | Q(order_scheduler_order__work_status=None) ),then=1),default=0,output_field=IntegerField()))
		else:
			subscriptions = Order.objects.filter(Q(Q( Q(payment_status='PENDING') | Q(payment_status='ON_HOLD') | Q(payment_status='COMPLETED') ) & Q(evaluation__payment_method='SUBSCRIPTION') & Q(evaluation__quatation_status='APPROVED') & ~Q(order_status='ORDER_CANCELLED'))).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='bookschedules')),to_attr='orderschedules')).annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())), remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count') ).exclude(Q( Q(remaining_cleanings_count = 0) & Q(payment_status='COMPLETED') ))
		
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

		return render(request,'accountant/subscription/active_subscriptions.html',{"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"subscriptions":subscriptions})

	def post(self,request):
		order_id            = request.POST.get('order')
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

		return redirect('accountant:accountant-active-subscriptions')

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
				
		return render(request,"accountant/client/order-page.html",{"order":order,"invoice":invoice,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count})

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

		return redirect('accountant:accountant-client-orderdetails', order_id)

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

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)
		
		messages.success(request,"Payment Policy Edited Succesfully")

		order			= Order.objects.get(evaluation_id=evaluation_id)
		
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

		
		
		fil_status 				= request.GET.get('status')
		fil_payment_policy		= request.GET.get('payment_policy')
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
				invoices         = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).filter(~Q(order_status='ORDER_CANCELLED')).filter(Q(Q(evaluation__customer__name__icontains=search)|Q(evaluation__evaluation_id__icontains=search))).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
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
			for payment in pending_payments:
				if payment.evaluation.payment_method in ['PREPAID','POSTPAID','BREAKDOWN']:
					total_pending_amount += payment.remining_amount

				if payment.evaluation.payment_method == 'SUBSCRIPTION':
					total_pending_amount += payment.subscription_topay		

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

		order_id       = request.POST.get('order_id')
		payment_policy = request.POST.get('payment_policy')
		
		if order_id:
			if payment_policy == 'CLEANING BALANCE':
				payment_method = request.POST.get('payment_method')
				amount         = request.POST.get('amount')
				payment_date   = datetime.strptime(request.POST.get('collection_date'),'%d/%m/%Y %I:%M %p')

				#Receipt Number
				receipt_no               = PaymentHistory.objects.filter(is_active=True,receipt_no__isnull=False).aggregate(t=Max('receipt_no'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
				current_receipt_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

				if current_receipt_starting == int(str(receipt_no)[:4]):
					new_receipt_no = int(receipt_no)+1
				else:
					new_receipt_no = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')

				if payment_method == 'CASH':
					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=0,order_status='ORDER_CANCELLED') 
					payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
					messages.success(request,"Payment Received thruogh Cash")

				if payment_method == 'CHEQUE':
					check_no   = request.POST.get('check_number')
					check_date = datetime.strptime(request.POST.get('check_date'),'%d-%m-%Y')

					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=0,order_status='ORDER_CANCELLED') 
					payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
					
					messages.success(request,"Payment Received through Cheque")

				if payment_method == 'BANK':
					bank_name   = request.POST.get('bank_name')
					bank_no     = request.POST.get('ibn_number')

					Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=0,order_status='ORDER_CANCELLED') 
					payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)

					messages.success(request,"Payment Received through Bank")
				
				xero          = XeroConnection.objects.first()
				order         = Order.objects.select_related('evaluation__customer').get(id=order_id)
				#Update Access Token and Refresh Token
				header                      = {
												'Authorization': 'Basic '+xero.client_encoded,
												'Content-Type': 'application/x-www-form-urlencoded'
													}
				body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
				token_response              = requests.post('https://identity.xero.com/connect/token',
														data=body,
														headers=header 
													).json()
				access_token                = token_response['access_token']
				refresh_token               = token_response['refresh_token']

				xero.access_token  = access_token
				xero.refresh_token = refresh_token
				xero.save()

				##Xero Contact
				if not cleaning_team_detail.order_scheduler.customer_address.customer.xero_account_id:

					##Xero Create Customer ID and Save
					contact_data                = {
													"Name":cleaning_team_detail.order_scheduler.customer_address.customer.name,
													"ContactNumber":cleaning_team_detail.order_scheduler.customer_address.customer.mobile_number,
													"EmailAddress":cleaning_team_detail.order_scheduler.customer_address.customer.email,
													"ContactStatus":"ACTIVE",
													"IsCustomer":True,
													"DefaultCurrency":"KWD"
																}
													
					header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

					create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
															json=contact_data,
															headers=header 
														).json()

					order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
					order.evaluation.customer.save() 

				#Xero Transaction
				header                      = {
											'xero-tenant-id': xero.tenant_id,
											'Authorization': 'Bearer '+access_token,
											'Accept': 'application/json',
											'Content-Type': 'application/json'
												}
				transaction_data            = {
												"Type": "RECEIVE-OVERPAYMENT",
												"Reference": order.evaluation.evaluation_id,
												"Date":datetime.strftime(payment_date,'%Y-%m-%d'),
												"Contact": {
													"ContactID": order.evaluation.customer.xero_account_id,
												},
												"LineItems": [{
													"Description": payment_method,
													"UnitAmount": amount,
													"AccountCode": "610",
													"TaxType":"NONE"
												}],
												"BankAccount": {
													"Code": "091"
												}
												}
												
				update_transaction          = requests.post('https://api.xero.com/api.xro/2.0/BankTransactions',
														json=transaction_data,
														headers=header 
													)

				payment_history.is_xero_marked = True
				payment_history.save()

			else:
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
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount) 
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
					elif payment_policy == 'BEFORE CLEANING':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=F('preamount_paid')+amount)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
					elif payment_policy == 'AFTER CLEANING':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=F('postamount_paid')+amount)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)
					elif payment_policy == 'SUBSCRIPTION':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,subscription_topay=0,is_advance=False)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CASH',received_by=request.user,paid_date=payment_date,receipt_no=new_receipt_no)

					messages.success(request,"Payment Received thruogh Cash")

				if payment_method == 'CHEQUE':
					check_no   = request.POST.get('check_number')
					check_date = datetime.strptime(request.POST.get('check_date'),'%d-%m-%Y')

					if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount) 
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
					elif payment_policy == 'BEFORE CLEANING':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=F('preamount_paid')+amount)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
					elif payment_policy == 'AFTER CLEANING':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=F('postamount_paid')+amount)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
					elif payment_policy == 'SUBSCRIPTION':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,subscription_topay=0,is_advance=False)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='CHEQUE',received_by=request.user,paid_date=payment_date,check_no=check_no,check_date=check_date,receipt_no=new_receipt_no)
					
					messages.success(request,"Payment Received thruogh Cheque")

				if payment_method == 'BANK':
					bank_name   = request.POST.get('bank_name')
					bank_no     = request.POST.get('ibn_number')

					if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount) 
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)
					elif payment_policy == 'BEFORE CLEANING':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,preamount_paid=F('preamount_paid')+amount)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)
					elif payment_policy == 'AFTER CLEANING':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,postamount_paid=F('postamount_paid')+amount)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)
					elif payment_policy == 'SUBSCRIPTION':
						Order.objects.filter(is_active=True,id=order_id).update(amount_paid=amount+F('amount_paid'),remining_amount=F('remining_amount')-amount,subscription_topay=0,is_advance=False)
						payment_history = PaymentHistory.objects.create(order_id=order_id,amount_paid=amount,payment_mode='BANK',received_by=request.user,paid_date=payment_date,bank_name=bank_name,bank_no=bank_no,receipt_no=new_receipt_no)

					messages.success(request,"Payment Received through Bank")

				is_payment_completed = Order.objects.get(id=order_id)

				if is_payment_completed.amount_paid == is_payment_completed.total_amount:
					is_payment_completed.payment_completed_date = payment_date 
					is_payment_completed.payment_status         = 'COMPLETED'
					is_payment_completed.save()
			
			
				####to close order
				order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=order_id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
				if order_closing_check:
					closing_order	= Order.objects.get(is_active=True,id=order_id)
					closing_order.order_status = 'ORDER_CLOSED'
					closing_order.save()


				xero          = XeroConnection.objects.first()
				order         = Order.objects.select_related('evaluation__customer').get(id=order_id)
				#Update Access Token and Refresh Token
				header                      = {
												'Authorization': 'Basic '+xero.client_encoded,
												'Content-Type': 'application/x-www-form-urlencoded'
													}
				body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
				token_response              = requests.post('https://identity.xero.com/connect/token',
														data=body,
														headers=header 
													).json()
				access_token                = token_response['access_token']
				refresh_token               = token_response['refresh_token']

				xero.access_token  = access_token
				xero.refresh_token = refresh_token
				xero.save()

				##Xero Contact
				if not order.evaluation.customer.xero_account_id:

					##Xero Create Customer ID and Save
					contact_data                = {
													"Name":order.evaluation.customer.name,
													"ContactNumber":order.evaluation.customer.mobile_number,
													"EmailAddress":order.evaluation.customer.email,
													"ContactStatus":"ACTIVE",
													"IsCustomer":True,
													"DefaultCurrency":"KWD"
																}
													
					header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

					create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
															json=contact_data,
															headers=header 
														).json()

					order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
					order.evaluation.customer.save() 

				#Xero Transaction
				header                      = {
											'xero-tenant-id': xero.tenant_id,
											'Authorization': 'Bearer '+access_token,
											'Accept': 'application/json',
											'Content-Type': 'application/json'
												}
				transaction_data            = {
												"Type": "RECEIVE-OVERPAYMENT",
												"Reference": order.evaluation.evaluation_id,
												"Date":datetime.strftime(payment_date,'%Y-%m-%d'),
												"Contact": {
													"ContactID": order.evaluation.customer.xero_account_id,
												},
												"LineItems": [{
													"Description": payment_method,
													"UnitAmount": amount,
													"AccountCode": "610",
													"TaxType":"NONE"
												}],
												"BankAccount": {
													"Code": "091"
												}
												}
												
				update_transaction          = requests.post('https://api.xero.com/api.xro/2.0/BankTransactions',
														json=transaction_data,
														headers=header 
													)

				print(update_transaction)
				payment_history.is_xero_marked = True
				payment_history.save()
		else:
			messages.success(request,"Something Went Wrong")

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

		paybackdiscount = PaybackDiscount.objects.get(id=paybackdiscount_id)
		investigation = Investigation.objects.get(id=paybackdiscount.investigation.id)

		if option == 'PAYBACK':
			
			PaybackDiscount.objects.filter(id=paybackdiscount_id).update(approved_option=option,approved_by=request.user,accountant_approval=request.user,is_completed=True,accountant_notes=request.POST.get('accountant_notes'))
			
			investigation.is_paybackdiscount_approved = True
			investigation.save()

			messages.success(request,"Payback Succesfully Added")

		if option == 'DISCOUNT':
			
			PaybackDiscount.objects.filter(id=paybackdiscount_id).update(approved_option=option,approved_by=request.user,accountant_approval=request.user,is_completed=True,accountant_notes=request.POST.get('accountant_notes'))
			
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

			investigation.is_paybackdiscount_approved = True
			investigation.save()

			messages.success(request,"Discount Succesfully Added")

		if request.user.user_type == 'BOOKINGOFFICER':
			return redirect('booking-officer:bookingofficerdash-board')
		else:
			return redirect('accountant:accountantdash-board')

class FineWriteBack(View):
	def get(self,request):
		return render(request,'accountant/payment/finewriteback.html',{})
	def post(self,request):
		order_id  = request.POST.get('order_id')
		order     = Order.objects.get(id=order_id)

		action = request.POST.get('finewriteback')
		
		#update Evaluation and fine
		if action == 'Fine':
			
			evaluation             = Evaluation.objects.filter(id=order.evaluation.id).first()
			if evaluation.payment_method == 'BREAKDOWN':
				Evaluation.objects.filter(id=order.evaluation.id).update(fine_amount=F('fine_amount')+float(request.POST.get('amount')), after_cleaning_amount=F('after_cleaning_amount')+float(request.POST.get('amount')), fine_created_by=request.user,total_cost=F('total_cost')+float(request.POST.get('amount')))
			else:
				Evaluation.objects.filter(id=order.evaluation.id).update(fine_amount=F('fine_amount')+float(request.POST.get('amount')),fine_created_by=request.user,total_cost=F('total_cost')+float(request.POST.get('amount')))

			order.total_amount    += float(request.POST.get('amount'))
			order.remining_amount += float(request.POST.get('amount'))
			if order.payment_status == 'COMPLETED':
				order.payment_status  = 'PENDING'
				order.order_status    = 'ORDER_IN_PROGRESS'				
			order.save()

			messages.success(request,"Fine Amount Succesfully Added")
		
		if action == 'Write-Off':
			#close payment if remining becomes zero 
			if (order.remining_amount-float(request.POST.get('amount'))) == 0:
				order.payment_completed_date = timezone.now()
				order.payment_status         = 'COMPLETED'
				order.save()
				
			if order.evaluation.payment_method == 'BREAKDOWN':
				Evaluation.objects.filter(id=order.evaluation.id).update(writeback_amount=F('writeback_amount')+float(request.POST.get('amount')),writeback_created_by=request.user,total_cost=F('total_cost')-float(request.POST.get('amount')),after_cleaning_amount=F('after_cleaning_amount')-float(request.POST.get('amount')))			
			else:
				Evaluation.objects.filter(id=order.evaluation.id).update(writeback_amount=F('writeback_amount')+float(request.POST.get('amount')),writeback_created_by=request.user,total_cost=F('total_cost')-float(request.POST.get('amount')))
			Order.objects.filter(id=order_id).update(total_amount=F('total_amount')-float(request.POST.get('amount')),remining_amount=F('remining_amount')-float(request.POST.get('amount')))
			
			####to close order
			order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=order_id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
			if order_closing_check:
				closing_order	= Order.objects.get(is_active=True,id=order_id)
				closing_order.order_status = 'ORDER_CLOSED'
				closing_order.save()

			messages.success(request,"Write Back Amount Succesfully Removed")


		return redirect('accountant:accountantdash-board')

def return_slots(start_time, end_time, visit_date):
	slot_list = []
	slot_list.append(str(visit_date))
	for i in range(start_time,end_time,2):
		slot = int((i+2)/2)
		slot_list.append(slot)
	
	return(slot_list)
				

#export to excel
def export_users_xls(request):

	from_date   = request.POST.get('from_date')
	to_date     = request.POST.get('to_date')
	report_type = request.POST.get('report_type')
	# print(from_date,to_date,report_type,"ftd")

	prevdate          = datetime.strptime(from_date, '%d-%m-%Y')
	todate            = datetime.strptime(to_date, '%d-%m-%Y')

	prev_date_start   = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
	prev_date_end     = prevdate+timedelta(1)
	todate_date_start = todate.replace(hour=0,minute=0,second=0,microsecond=0)   #single_date+timedelta(1)
	todate_date_end   = todate_date_start+timedelta(1)

	print(prev_date_start,todate_date_end,"mko")

	daterange  = pd.date_range(prev_date_start, todate_date_end)

	# print(daterange,"drange")

	# print(prev_date_start,todate_date_end,"datesss")
	# Sheet header, first row
	row_num = 0
	row_num2 = 0
	row_num3 = 0
	row_num4 = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	if report_type == 'employeecommission':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="EMPLOYEE_COMMISSION_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('EMPLOYEE COMMISSION SHEET')

		columns = ['Cleaner','Status','Occupied Hours','Total Working Hours']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		try:
			total_active_workers = CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(team__order_scheduler__end_at__range=(prev_date_start,todate_date_end)) )).values_list('member',flat=True).distinct().union(FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(end_at__range=(prev_date_start,todate_date_end))) ).values_list('member',flat=True)).distinct()
		except:
			total_active_workers = 0

		print(total_active_workers,"workrs")

		rows = []

		for worker in total_active_workers:
			employees = []
			employee = UserProfile.objects.get(id=int(worker))

			employee_cleanings_list = CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(member__id=employee.id)&Q(team__order_scheduler__end_at__range=(prev_date_start,todate_date_end)) )).values_list('team__order_scheduler__order__order_no','team__order_scheduler__start_at','team__order_scheduler__end_at').union(FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(member__id=employee.id)&Q(end_at__range=(prev_date_start,todate_date_end))) ).values_list('team__followup_scheduler__follow_up__investigation__order__order_no','start_at','end_at'))
			
			#occupied hours calc
			cleaning_durations = []
			
			for cleaning in employee_cleanings_list:
				
				duration_list = [] 
				duration_list.append(int(datetime.strftime(cleaning[1],'%H')))
				duration_list.append(int(datetime.strftime(cleaning[2],'%H')))
				duration_list.append(datetime.strftime(cleaning[2],'%d-%m-%Y'))
				

				cleaning_durations.append(duration_list)

			new_cleaning_durations=[]
			output=[]

			for i in cleaning_durations:
				
				if i[0]>i[1]:
					new_cleaning_durations= new_cleaning_durations+[[i[0],24,i[2]],[0,i[1],i[2]]]
				else:
					new_cleaning_durations= new_cleaning_durations+[i]
				
			total_duration = 0
			final_slots = []
			for i in new_cleaning_durations:
				
				slots= return_slots(i[0],i[1],i[2])
				output.append(slots)

			#calculating duration of slots for each date
			for date in daterange:
				str_date = datetime.strftime(date,'%d-%m-%Y')
				
				new_output = []

				date_slot_list = []
				
				for elem in output:
					print(elem[0],str_date,"ele")
					if str_date == elem[0]:
						elem.pop(0)
						print(elem,"ele2")
						for obj in elem:
							print(obj,"obj")
							date_slot_list.append(obj)
				print(date_slot_list,str_date,"dts")

				final_slots=(list(set(date_slot_list)))
				duration = len(final_slots)*(2)	
				total_duration += duration

			#total working hours calc
			d0 = prev_date_start
			d1 = todate_date_end
			print(d0,d1,"dee")

			delta = d1 - d0
			print(d0,d1,delta.days,"daysss")

			todate = todate_date_end - timedelta(days=1)
			todate = todate.replace(hour=23,minute=59,second=59,microsecond=0)		

			print(todate,"toddy")			

			leave_schedules = LeaveSchedule.objects.filter(staff=employee,leave_date__range=(prev_date_start,todate)).values_list('leave_date',flat=True).distinct().count()

			print(leave_schedules,"lvs")

			worked_days = int(delta.days) - int(leave_schedules)
			total_working_hours = worked_days * 10
			# total_working_hours = total_working_hours // 24

			employees.append(employee.name)
			if employee.is_active == True:
				employees.append('Active')
			else:
				employees.append('Inactive')
			employees.append(total_duration)
			employees.append(total_working_hours)

			rows.append(employees)

		# print(rows,"ross")
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

	if report_type == 'paymentdetails':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="PAYMENT_DETAILS_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('PAYMENT DETAILS SHEET')

		columns = ['Order No.','Cleaning Policy','Payment Policy', 'Order Amount','Total Paid Amount','Work Done','Balance','Order Status','Customer']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# evaluationbooks = EvaluationBook.objects.filter(evaluation_details__evaluation__quatation_status='APPROVED',created__range=(prev_date_start,todate_date_end)).select_related('evaluation_details__evaluation').prefetch_related(Prefetch('evaluation_details__evaluation__evaluation_order',queryset=Order.objects.filter(is_active=True).prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).exclude(work_status='CLEANING_CANCELLED'),to_attr='visits')),to_attr='order'))
		# orderschedules = OrderScheduler.objects.filter(is_active=True,end_at__range=(prev_date_start,todate_date_end)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).order_by('end_at')
		orders = Order.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end),evaluation__quatation_status='APPROVED').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).exclude(work_status='CLEANING_CANCELLED'),to_attr='visits')).annotate(completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())))
		
		print(orders,"countt")
		
		rows = []

		total_day_sales = 0

		for order in orders:
			schedule_data_list = []

			print(len(order.visits),order.completed_cleaning_count,"lenor")

			if order.evaluation.payment_method == 'SUBSCRIPTION' and int(len(order.visits)) > 0:
				cleaning_policy = 'SUBSCRIPTION'
				work_done = float(order.total_amount/len(order.visits)) * order.completed_cleaning_count
			else:
				cleaning_policy = 'ONE TIME CLEANING'
				if int(len(order.visits)) == int(order.completed_cleaning_count):
					work_done = order.total_amount
				else:
					work_done = 0.000
			print(work_done,"wdonw")

			if order.payment_status == 'COMPLETED' or order.preamount_paid != 0 or order.evaluation.payment_method == 'POSTPAID' or order.evaluation.payment_method == 'SUBSCRIPTION':
					
				if order.order_status == 'APPROVED_BY_CLIENT':
					order_status = 'APPROVED'
				elif order.order_status == 'ORDER_IN_PROGRESS':
					order_status = 'ORDER IN PROGRESS'
				elif order.order_status == 'ORDER_CLOSED':
					order_status = 'ORDER CLOSED'
				elif order.order_status == 'CANCEL_IN_PROGRESS':
					order_status = 'CANCEL IN PROGRESS'
				elif order.order_status == 'ORDER_CANCELLED':
					order_status = 'ORDER CANCELLED'
				else:
					order_status = 'EVALUATING'
			else:
				order_status = 'APPROVED-NOT PAID'

			schedule_data_list.append(order.order_no)
			schedule_data_list.append(cleaning_policy)
			schedule_data_list.append(order.evaluation.payment_method)
			schedule_data_list.append(order.total_amount)
			schedule_data_list.append(order.amount_paid)
			schedule_data_list.append(work_done)
			schedule_data_list.append(order.remining_amount)
			schedule_data_list.append(order_status)
			schedule_data_list.append(order.evaluation.customer.name)

			rows.append(schedule_data_list)

		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

	if report_type == 'salessummarylist':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="SALES_SUMMARY_REPORT_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('GENERAL PAYMENT SHEET')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Job Type','Customer ID','BLC no.','Job Start Date','Job End Date','Net Sales','Total Job Completed','Total Paid Amount','Bal. Job to complete','Bal. amount to collect']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		orders = Order.objects.filter(is_active=True,evaluation__quatation_status='APPROVED',created__range=(prev_date_start,todate_date_end)).values_list('evaluation__evaluation_details__evaluation_book_evaluation_details__cleaning_policy','evaluation__customer__customer_id','order_no','evaluation__id','order_no','total_amount','order_no','amount_paid','id','remining_amount').order_by('-id')
	
		print(orders,"ordss")
		#removing duplicates
		found = set()

		rows = []

		for order in orders:
			order_list = list(order)

			evaluationbooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation__id=int(order_list[3]))
			evaluationbooks_count = evaluationbooks.count()
			
			orderschedules_start = OrderScheduler.objects.filter(order__id=int(order_list[8])).first()
			orderschedules_end = OrderScheduler.objects.filter(order__id=int(order_list[8])).last()

			schedule_count = OrderScheduler.objects.filter(order__id=int(order_list[8])).count()

			if not schedule_count:
				schedule_count = 1

			if evaluationbooks_count > 1:
				job_completed = 0
				job_remaining = 0

				for book in evaluationbooks:
					cleanings_count = OrderScheduler.objects.filter(is_active=True,order__id=int(order_list[8]),order_scheduler_book__id=int(book.id)).count()
					completed_cleanings = OrderScheduler.objects.filter(is_active=True,order__id=int(order_list[8]),order_scheduler_book__id=int(book.id),work_status='CLEANING_FULFILLED')
					completed_cleanings_count = completed_cleanings.count()

					if book.cleaning_policy == 'ONE TIME SERVICE':
						job_completed += 0
						job_remaining += 0
					else:
						per_cleaning_amount = float(book.total_cost/cleanings_count)
						job_completed += float(per_cleaning_amount*completed_cleanings_count)
						job_remaining += float(book.total_cost - job_completed)
					
				order_list[6] = job_completed
				order_list[8] = job_remaining

			else:

				completed_cleanings_count = OrderScheduler.objects.filter(order__id=int(order_list[8]),work_status='CLEANING_FULFILLED').count()
				
				if order_list[0] == 'ONE TIME SERVICE':
					order_list[6] = 0
					order_list[8] = 0
				else:
					per_cleaning_amount = float(order_list[5]/schedule_count)
					job_completed = float(per_cleaning_amount * completed_cleanings_count)
					job_remaining = float(order_list[5] - job_completed)
					
					order_list[6] = job_completed
					order_list[8] = job_remaining

			if schedule_count > 1:
				order_list[3] = orderschedules_start.start_at
				order_list[4] = orderschedules_end.end_at
			elif schedule_count == 1:
				order_list[3] = orderschedules_start.start_at
				order_list[4] = orderschedules_start.end_at
			else:
				order_list[3] = '-'
				order_list[4] = '-'

			order = tuple(order_list)

			if order_list[2] not in found:
				rows.append(order)
			found.add(order_list[2])

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

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


	if report_type == 'due_payments':

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="DUE_PAYMENTS_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('DUE PAYMENTS')

		# columns = ['Order Date', 'Order Number', 'Client Name', 'Payment Policy', 'Payment Mode', 'Total Amount', 'Paid', 'Balance' ]

		columns = ['Date','Order No.','Customer Name','Mobile','Service Type','Amount','Payment Policy']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		orders = Order.objects.filter(is_active=True).order_by('-id').filter(evaluation__quatation_status='APPROVED',order_status__isnull=False).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
		orders = orders.filter(Q( Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) )).values_list('id','order_no','evaluation__customer__name','evaluation__customer__mobile_number','order_no','remining_amount','evaluation__payment_method')
		

		rows = []

		for order in orders:

			# end_date = order.orderschedules[0]

			# print(order.orderschedules,"ed")
			
			order_list = list(order)
			print(order_list[0],"ordrdat")

			last_orderschedule = OrderScheduler.objects.filter(is_active=True,order__id=order_list[0],end_at__range = (prev_date_start,todate_date_end)).last()

			if last_orderschedule:
				order_list[0] = last_orderschedule.end_at

				order_list[4] = last_orderschedule.order_scheduler_book.service_type.name

				print(last_orderschedule.end_at,"dat")

				order = tuple(order_list)
				
				rows.append(order)

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]

		rows = sorted(rows)
	
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

	if report_type == 'salesdetails' or report_type == 'allsalesdetails':
		response = HttpResponse(content_type='application/ms-excel')

		wb = xlwt.Workbook(encoding='utf-8')
		
		#total sales
		response['Content-Disposition'] = 'attachment; filename="SALES_REPORT_'+from_date+'_'+to_date+'.xls"'
		orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(prev_date_start,todate_date_end)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).values_list('order__order_no','end_at','end_at','id','evaluation_details__address__customer__name','evaluation_details__evaluation__payment_method','order_scheduler_book__estimated_cost','order__amount_paid','evaluation_details__evaluation__payment_way','order_scheduler_book__id','order__remining_amount','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__cleaning_hours','order_scheduler_book__number_of_cleaners','evaluation_details__evaluator__name','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluation__discount','order_scheduler_book__evaluation_details__evaluation__additional_charge').order_by('end_at')
		print(orderschedules,"schedules_list")
	
		
		rows = []

		for schedule in orderschedules:
			schedule_list = list(schedule)
			schedule_list[3] = schedule_list[1].strftime("%A")
			schedule_list[1] = schedule_list[1]+timedelta(hours=3)
			schedule = tuple(schedule_list)
			rows.append(schedule)
			
		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]


		#sales report
		ws2 = wb.add_sheet('SALES REPORT',cell_overwrite_ok = True)
	
		columns2 = ['Date','Day','Detailed Cleaning','Special Care','Kitchen Cleaning','Infection Control','Grand Total']
		
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

			# print(dates,"dts")

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

			detailed_cleaning = 0
			special_care = 0
			kitchen_cleaning = 0
			infection_control = 0
			
			test_elem = d

			#filtering rows list using date
			res = [item for item in rows if item[1] == d ]
			print(d)

			#calculating service totals and grand total
			for r in res:

				calc_orderschedules = OrderScheduler.objects.filter( order__order_no = r[0] , order_scheduler_book__id = r[9] )
			
				total_order_schedule_count = OrderScheduler.objects.filter( order__order_no = r[0] ).count()

				orderschedules_count = calc_orderschedules.count()


				day_name = r[3]

				# if d == '05-07-2021' and r[0] == 'BLC20210610161' :					
					# print(r[11],r[0], float(r[6]/orderschedules_count)-float(r[16]/total_order_schedule_count)-float(r[17]/total_order_schedule_count)+float(r[18]/total_order_schedule_count)-float(r[19]/total_order_schedule_count),"service")
				
				if r[6] != None:

					if r[11] == 'General Cleaning':
						detailed_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							detailed_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							detailed_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							detailed_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							detailed_cleaning -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							detailed_cleaning += float(r[20]/total_order_schedule_count)

					if r[11] == 'Deep Cleaning':
						detailed_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							detailed_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							detailed_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							detailed_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							detailed_cleaning -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							detailed_cleaning += float(r[20]/total_order_schedule_count)

					if r[11] == 'Facade Cleaning':
						detailed_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							detailed_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							detailed_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							detailed_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							detailed_cleaning -= float(r[19]/total_order_schedule_count)
						if r[20] > 0:
							detailed_cleaning += float(r[20]/total_order_schedule_count)

					if r[11] == 'Storage Area':
						detailed_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							detailed_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							detailed_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							detailed_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							detailed_cleaning -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							detailed_cleaning += float(r[20]/total_order_schedule_count)

					if r[11] == 'Car Parking Umbrella':
						detailed_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							detailed_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							detailed_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							detailed_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							detailed_cleaning -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							detailed_cleaning += float(r[20]/total_order_schedule_count)

					if r[11] == 'Window Cleaning':
						detailed_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							detailed_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							detailed_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							detailed_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							detailed_cleaning -= float(r[19]/total_order_schedule_count)
						if r[20] > 0:
							detailed_cleaning += float(r[20]/total_order_schedule_count)

					if r[11] == 'Outdoor Cleaning':
						detailed_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							detailed_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							detailed_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							detailed_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							detailed_cleaning -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							detailed_cleaning += float(r[20]/total_order_schedule_count)

					if r[11] == 'Sterilization':
						infection_control += float(r[6]/orderschedules_count)

						if r[16] > 0:
							infection_control -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							infection_control -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							infection_control += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							infection_control -= float(r[19]/total_order_schedule_count)
						if r[20] > 0:
							infection_control += float(r[20]/total_order_schedule_count)
						

					if r[11] == 'Carpet Cleaning':
						special_care += float(r[6]/orderschedules_count)

						if r[16] > 0:
							special_care -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							special_care -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							special_care += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							special_care -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							special_care += float(r[20]/total_order_schedule_count)

					if r[11] == 'Upholstery Cleaning':
						
						special_care += float(r[6]/orderschedules_count)

						if r[16] > 0:
							special_care -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							special_care -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							special_care += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							special_care -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							special_care += float(r[20]/total_order_schedule_count)

					if r[11] == 'Mattress Cleaning':
						special_care += float(r[6]/orderschedules_count)

						if r[16] > 0:
							special_care -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							special_care -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							special_care += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							special_care -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							special_care += float(r[20]/total_order_schedule_count)

					if r[11] == 'Kitchen Cleaning':
						kitchen_cleaning += float(r[6]/orderschedules_count)

						if r[16] > 0:
							kitchen_cleaning -= float(r[16]/total_order_schedule_count)
						if r[17] > 0:
							kitchen_cleaning -= float(r[17]/total_order_schedule_count)
						if r[18] > 0:
							kitchen_cleaning += float(r[18]/total_order_schedule_count)	
						if r[19] > 0:
							kitchen_cleaning -= float(r[19]/total_order_schedule_count)	
						if r[20] > 0:
							kitchen_cleaning += float(r[20]/total_order_schedule_count)

					grand_total += float(r[6]/orderschedules_count)

					#fine,promocode, write off calc
					if r[16] > 0:
						grand_total -= float(r[16]/total_order_schedule_count)
					if r[17] > 0:
						grand_total -= float(r[17]/total_order_schedule_count)
					if r[18] > 0:
						grand_total += float(r[18]/total_order_schedule_count)
					if r[19] > 0:
						grand_total -= float(r[19]/total_order_schedule_count)	
					if r[20] > 0:
						grand_total += float(r[20]/total_order_schedule_count)

					r[20] = '-'

			# print(detailed_cleaning,"gen")
			daily_report = (d, day_name, round(detailed_cleaning,3), round(special_care,3), round(kitchen_cleaning,3), round(infection_control,3), round(grand_total,3))

			rows2.append(daily_report)

		for row in rows2:
			row_num2 += 1
			for col_num in range(len(row)):
				ws2.write(row_num2, col_num, row[col_num], font_style)
	
		#individual sales
		response['Content-Disposition'] = 'attachment; filename="SALES_DETAILS_COMPLETED_'+from_date+'_'+to_date+'.xls"'
		# orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(prev_date_start,todate_date_end)).filter(Q(Q(work_status='CLEANING_FULFILLED')|Q(work_status='CLEANING_TEAM_ASSIGNED')|Q(work_status='CLEANING_IN_PROGRESS'))).values_list('order__order_no','end_at','end_at','id','evaluation_details__address__customer__name','evaluation_details__evaluation__payment_method','order_scheduler_book__total_cost','order__amount_paid','evaluation_details__evaluation__payment_way','order_scheduler_book__id','order__remining_amount','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__cleaning_hours','order_scheduler_book__number_of_cleaners','evaluation_details__evaluator__name','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount').order_by('end_at')

		
		#sales details
		ws = wb.add_sheet('SALES DETAILS',cell_overwrite_ok = True)
	
		columns = ['Order No.','Cleaning Date','Final Cleaning of service','Day','Customer','Payment Policy','Net Amount','Paid Amount','Payment Type','Payment Date','Balance Amount','Service Type','Cleaning Policy','Hours','Staff','Salesman']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		rows = []

		for schedule in orderschedules:

			schedule_list = list(schedule)

			if schedule_list[6] != None:

				calc_orderschedules = OrderScheduler.objects.filter( order__order_no = schedule_list[0] , order_scheduler_book__id = schedule_list[9] )

				total_order_schedule_count = OrderScheduler.objects.filter( order__order_no = schedule_list[0] ).count()

				orderschedules_count = calc_orderschedules.count()
				last_orderschedule = calc_orderschedules.last()

				# print(orderschedules_count,"osh")

				orderschedule = OrderScheduler.objects.get(id=int(schedule_list[3]))

				schedule_list[2] = last_orderschedule.end_at
				

				#splitting paid amount and balance

				schedule_list[6] = round(float(schedule_list[6] / orderschedules_count),3)

				#fine,promocode, write off calc
				if schedule_list[16] > 0:
					schedule_list[6] -= float(schedule_list[16]/total_order_schedule_count)
				if schedule_list[17] > 0:
					schedule_list[6] -= float(schedule_list[17]/total_order_schedule_count)
				if schedule_list[18] > 0:
					schedule_list[6] += float(schedule_list[18]/total_order_schedule_count)
				if schedule_list[19] > 0:
					schedule_list[6] -= float(schedule_list[19]/total_order_schedule_count)
				if schedule_list[20] > 0:
					schedule_list[6] += float(schedule_list[20]/total_order_schedule_count)

				schedule_list[7] = round(float(schedule_list[7] / orderschedules_count),3)

				if schedule_list[10] > 0:
					schedule_list[10] = round(float(schedule_list[10] / orderschedules_count),3)

				paymenthistory = PaymentHistory.objects.filter(order__order_no=schedule_list[0]).last()

				#adding payment date and payment mode
				if orderschedule.evaluation_details.evaluator == None and orderschedule.evaluation_details.evaluation.call_attender != None:
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

				schedule_list[16] = ''
				schedule_list[17] = ''
				schedule_list[18] = ''
				schedule_list[19] = ''
				schedule_list[20] = ''

				schedule_list[3] = schedule_list[1].strftime("%A")
				schedule_list = schedule_list[:-3]
				schedule = tuple(schedule_list)
				rows.append(schedule)
		
		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]

		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

		

	if report_type == 'orderhistory':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="ORDER_HISTORY_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		
		#sales details
		ws = wb.add_sheet('ORDER HISTORY',cell_overwrite_ok = True)
	
		columns = ['Quotation Date','Order No.','Customer ID','Customer Name','Type of Service','Cleaning Policy','Payment Policy','Job Starting Date','Total Amount','Discount','Fine Amount','Writeback Amount','Promocode Amount','Additional Charge','Cancelled Amount','Net Amount','Quotation Status','Evaluator']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		evaluations = Evaluation.objects.filter(is_active=True,evaluation_order__is_active=True,evaluation_order__created__range=(prev_date_start,todate_date_end)).values_list('evaluation_order__created','evaluation_id','customer__customer_id','customer__name','id','id','payment_method','id','estimated_cost','discount','fine_amount','writeback_amount','promocode_amount','additional_charge','cancelled_amount','total_cost','id','evaluation_details__evaluator__name')
		
		rows = []
		
		for evaluation in evaluations:

			evaluation_list = list(evaluation)

			estimated_cost = evaluation_list[8]
			
			#cleaning policy, service type
			evaluationbooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation__id=int(evaluation_list[16])).values('cleaning_policy','service_type__name','discount')
			print(evaluationbooks,"ebooks")

			found = set()
			servicetypes = []
			cleaning_policies = []

			for ebook in evaluationbooks:
				if ebook['service_type__name'] not in found:
					servicetypes.append(ebook['service_type__name'])
					# servicetypes.append(', ')
					found.add(ebook['service_type__name'])
				
				if ebook['cleaning_policy'] not in found:
					cleaning_policies.append(ebook['cleaning_policy'])
					# cleaning_policies.append('-')
					found.add(ebook['cleaning_policy'])

				if ebook['discount']:
					evaluation_list[9] = ebook['discount']
					estimated_cost -= float(ebook['discount'])

			evaluation_list[4] = tuple(servicetypes)
			evaluation_list[5] = tuple(cleaning_policies)

			#job starting date
			orderschedule = OrderScheduler.objects.filter(is_active=True,evaluation_details__evaluation__id=int(evaluation_list[16])).values('start_at').first()
			
			print(orderschedule,"osched")
			if orderschedule:
				evaluation_list[7] = orderschedule['start_at']
			else:
				evaluation_list[7] = '-'

			#evaluator
			evaluationdetails = EvaluationDetails.objects.filter(is_active=True,evaluation__id=int(evaluation_list[16])).values('evaluator__name','evaluation__call_attender__name')
			
			evaluators = []
			for detail in evaluationdetails:
				if evaluationdetails.last:
					print("last")
				else:
					print("raam")

				if detail['evaluator__name'] != None:
					if detail['evaluator__name'] not in found:
						evaluators.append(detail['evaluator__name'])
						# evaluators.append('-')
						found.add(detail['evaluator__name'])
				else:
					if detail['evaluation__call_attender__name'] not in found:
						evaluators.append(detail['evaluation__call_attender__name'])
						# evaluators.append('-')
						found.add(detail['evaluation__call_attender__name'])
					
				
			evaluation_list[17] = tuple(evaluators)


			#quotation status
			order = Order.objects.filter(is_active=True,evaluation__id=int(evaluation_list[16])).values('evaluation__writeback_amount','evaluation__promocode_amount','evaluation__cancelled_amount','evaluation__fine_amount','evaluation__additional_charge','evaluation__quatation_status','payment_status','preamount_paid','order_status','evaluation__discount').first()
			
			

			if order:

				if order['evaluation__quatation_status'] == 'APPROVED':
					if order['payment_status'] == 'COMPLETED' or order['preamount_paid'] != 0 or evaluation_list[6] == 'POSTPAID':
						if order['order_status'] == 'APPROVED_BY_CLIENT':
							evaluation_list[16] = 'APPROVED'
						elif order['order_status'] == 'ORDER_IN_PROGRESS':
							evaluation_list[16] = 'ORDER IN PROGRESS'
						elif order['order_status'] == 'ORDER_CLOSED':
							evaluation_list[16] = 'COMPLETED'
						else:
							evaluation_list[16] = '-'
					else:
						evaluation_list[16] = 'APPROVED-NOT PAID'

				elif order['evaluation__quatation_status'] == 'REJECTED':
					evaluation_list[16] = 'REJECTED'
				elif order['evaluation__quatation_status'] == 'PENDING':
					evaluation_list[16] = 'PENDING'
				elif order['evaluation__quatation_status'] == 'EXPIRED':
					evaluation_list[16] = 'EXPIRED'
				else:
					evaluation_list[16] = 'EVALUATING'
			else:
				evaluation_list[16] = '-'

			evaluation = tuple(evaluation_list)

			print(evaluation,"rosse2")
			rows.append(evaluation)
		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]

		print(rows,"rosse")

		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, str(row[col_num]), font_style)

	wb.save(response)

	# print(response.status_code,"resp")
	
	return response


class TicketDetails(IsAccountant,View):
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

		return render(request,'accountant/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})		


class TicketAdvanced(IsAccountant,View):
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

		return render(request,'accountant/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})


class OrderCancellation(IsAccountant,View):
	def get(self,request,order_cancel_id):
	
		order_cancell_cashbacks = CancellOrderAmountHistory.objects.select_related('order__evaluation__customer').prefetch_related('order__order_scheduler_order__order_scheduler_book').annotate(total_cleaners=Sum('order__order_scheduler_order__order_scheduler_book__number_of_cleaners')).get(amount_return_method='CASHBACK',is_completed=False,id=int(order_cancel_id))
	
		cleaning_price = 0
		for scheduler in order_cancell_cashbacks.order.order_scheduler_order.all():
			if scheduler.work_status=='CLEANING_FULFILLED':
				cleaning_price += scheduler.order_scheduler_book.total_cost/len(order_cancell_cashbacks.order.order_scheduler_order.all())			
		order_cancell_cashbacks.job_completed_amount = cleaning_price

		return render(request,"accountant/cancel-order/cancel-order.html",{'order_cancel_id':order_cancel_id,"order_cancell_cashbacks":order_cancell_cashbacks})

	def post(self,request,order_cancel_id):
		
		#cash back		
		cashback_id                   = request.POST.get('cashback_id')
		return_amount                 = request.POST.get('return_amount')
		cashback_history              = CancellOrderAmountHistory.objects.select_related('order').get(id=cashback_id)
		
		cashback_history.order.remining_amount  = 0
		cashback_history.order.amount_paid     -= float(return_amount)
		cashback_history.order.order_status     = 'ORDER_CANCELLED'
		cashback_history.is_completed           = True
		cashback_history.return_amount          = float(return_amount)
		cashback_history.order.save()
		cashback_history.save()

		print(cashback_history)
		return redirect('accountant:accountantdash-board')


	