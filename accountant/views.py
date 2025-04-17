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
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia,CancellOrderAmountHistory,XeroInvoice
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

				##########################################################################################
				#Xero Integration
				# xero          = XeroConnection.objects.first()
				# order         = Order.objects.select_related('evaluation__customer').get(id=order_id)
				# #Update Access Token and Refresh Token
				# header                      = {
				# 								'Authorization': 'Basic '+xero.client_encoded,
				# 								'Content-Type': 'application/x-www-form-urlencoded'
				# 									}
				# body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
				# token_response              = requests.post('https://identity.xero.com/connect/token',
				# 										data=body,
				# 										headers=header 
				# 									).json()
				# access_token                = token_response['access_token']
				# refresh_token               = token_response['refresh_token']

				# xero.access_token  = access_token
				# xero.refresh_token = refresh_token
				# xero.save()

				# header                      = {
				# 								'xero-tenant-id': xero.tenant_id,
				# 								'Authorization': 'Bearer '+access_token,
				# 								'Accept': 'application/json',
				# 								'Content-Type': 'application/json'
				# 									}
				
				# #Invoice Authorize
				# if payment_policy == 'PREPAID':
				# 	Amount = order.evaluation.total_cost 
				# 	##Invoice Line Item 
				# 	LineItems                 = []
				# 	LineItems.append({
				# 		"Description":"ONE TIME SERVICE",
				# 		"Quantity":"1",
				# 		"UnitAmount":Amount,
				# 		"AccountCode":1207004,
				# 		"TaxType":"NONE"
				# 					}
				# 		)
				# 	InvoiceNumber  = order.invoice_no
				# 	payment_policy = 'PREPAID'

				# 	invoice_data        = 	{
				# 						"Type":"ACCREC",
				# 						"LineAmountTypes":"NoTax",
				# 						"InvoiceNumber":InvoiceNumber,
				# 						"Reference":order.order_no,
				# 						"Status":"AUTHORISED",
				# 						"LineItems":LineItems
				# 					}

				# 	##xero Create Invoice
				# 	header                      = {
				# 									'xero-tenant-id': xero.tenant_id,
				# 									'Authorization': 'Bearer '+access_token,
				# 									'Accept': 'application/json',
				# 									'Content-Type': 'application/json'
				# 										}

				# 	create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
				# 											json=invoice_data,
				# 											headers=header 
				# 										).json()
				
				# 	try:
				# 		created_invoice = create_invoice['Status']
				# 	except:
				# 		created_invoice = None
					
				# 	if created_invoice == 'OK':
				# 		try:
				# 			update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
				# 			update_xero_invoice.amount           = Amount
				# 			update_xero_invoice.xero_marked_date = timezone.now().date()
				# 			update_xero_invoice.payment_policy   = payment_policy
				# 			update_xero_invoice.save()
				# 		except:
				# 			XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

				# if payment_policy == 'BEFORE CLEANING':
				# 	#Before Invoice
				# 	Amount = order.evaluation.before_cleaning_amount
				# 	##Invoice Line Item 
				# 	LineItems                 = []
				# 	LineItems.append({
				# 		"Description":"ONE TIME SERVICE",
				# 		"Quantity":"1",
				# 		"UnitAmount":Amount,
				# 		"AccountCode":1207004,
				# 		"TaxType":"NONE"
				# 					}
				# 		)
				# 	InvoiceNumber  = order.invoice_no+'A'

				# 	invoice_data        = 	{
				# 						"Type":"ACCREC",
				# 						"LineAmountTypes":"NoTax",
				# 						"InvoiceNumber":InvoiceNumber,
				# 						"Reference":order.order_no,
				# 						"Status":"AUTHORISED",
				# 						"LineItems":LineItems
				# 					}

				# 	##xero Create Invoice
				# 	header                      = {
				# 									'xero-tenant-id': xero.tenant_id,
				# 									'Authorization': 'Bearer '+access_token,
				# 									'Accept': 'application/json',
				# 									'Content-Type': 'application/json'
				# 										}

				# 	create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
				# 											json=invoice_data,
				# 											headers=header 
				# 										).json()
				# 	try:
				# 		created_invoice = create_invoice['Status']
				# 	except:
				# 		created_invoice = None
					
				# 	if created_invoice == 'OK':
				# 		try:
				# 			update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
				# 			update_xero_invoice.amount           = Amount
				# 			update_xero_invoice.xero_marked_date = timezone.now().date()
				# 			update_xero_invoice.payment_policy   = payment_policy
				# 			update_xero_invoice.save()
				# 		except:
				# 			XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
				
				# #Payment Add
				# payment_date        = payment_date.date()
				# payment_date_string = datetime.strftime(payment_date,'%Y-%m-%d')

				# if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID' or payment_policy == 'BEFORE CLEANING' or payment_policy == 'AFTER CLEANING':
					
				# 	try:
				# 		xero_invoice = XeroInvoice.objects.get(order=order,payment_policy=payment_policy)
				# 	except:
				# 		xero_invoice = None

				# 	if xero_invoice:
				# 		payment_data = {
				# 					"Invoice":{
				# 						"InvoiceNumber":xero_invoice.invoice_no
				# 					},
				# 					"Account":{
				# 						"Code":"1201023"
				# 					},
				# 					"Date":payment_date_string,
				# 					"Amount":amount
				# 					}

				# 		update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
				# 											json=payment_data,
				# 											headers=header 
				# 										).json()


				# 		try:
				# 			created_payment = update_payment['Status']
				# 		except:
				# 			created_payment = None

				# 		if created_payment == 'OK':
				# 			xero_invoice.is_paid   = True
				# 			xero_invoice.paid_date = payment_date
				# 			xero_invoice.save()

				# 			payment_history.is_xero_marked = True
				# 			payment_history.save()

				# if payment_policy == 'SUBSCRIPTION':
				# 	try:
				# 		xero_invoice = XeroInvoice.objects.filter(order=order,payment_policy=payment_policy,is_paid=False).last()
				# 	except:
				# 		xero_invoice = None

				# 	if xero_invoice:
				# 		payment_data = {
				# 					"Invoice":{
				# 						"InvoiceNumber":xero_invoice.invoice_no
				# 					},
				# 					"Account":{
				# 						"Code":"1201023"
				# 					},
				# 					"Date":payment_date_string,
				# 					"Amount":amount
				# 					}

				# 		update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
				# 											json=payment_data,
				# 											headers=header 
				# 										).json()


				# 		try:
				# 			created_payment = update_payment['Status']
				# 		except:
				# 			created_payment = None

				# 		if created_payment == 'OK':
				# 			xero_invoice.is_paid   = True
				# 			xero_invoice.paid_date = payment_date
				# 			xero_invoice.save()
							
				# 			payment_history.is_xero_marked = True
				# 			payment_history.save()
					
					
				########################################################################################

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
		order     = Order.objects.select_related('evaluation').get(id=order_id)

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
	prev_date_end     = prev_date_start+timedelta(1)
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
	
	if report_type == 'xeroinvoices':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="System xeroInvoices.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('XeroInvoices')

		columns = ['Date','BLC','Payment Policy','Paid Amount']

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		xeroinvoices = XeroInvoice.objects.filter(is_active=True,created__range=(prev_date_start,todate_date_end),is_paid=True).values_list('created','order__order_no', 'payment_policy','amount').order_by('created')

		xeroinvoices = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in xeroinvoices ]

		for row in xeroinvoices:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

		
		
		
		ws2 = wb.add_sheet('PaymentHistories')

		columns2 = ['Paid Date','BLC','Payment Mode','Paid Amount']

		for col_num in range(len(columns2)):
			ws2.write(row_num2, col_num, columns2[col_num], font_style)

		paymenthistories = PaymentHistory.objects.filter(is_active=True,paid_date__range=(prev_date_start,todate_date_end)).values_list('paid_date','order__order_no', 'payment_mode','amount_paid').order_by('paid_date')

		paymenthistories = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in paymenthistories ]

		for row in paymenthistories:
			row_num2 += 1
			for col_num in range(len(row)):
				ws2.write(row_num2, col_num, row[col_num], font_style)
	
	if report_type == 'employeecommission':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="EMPLOYEE_COMMISSION_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		
		# Sheet 1: Summary Report (unchanged from previous version)
		ws = wb.add_sheet('EMPLOYEE SUMMARY')
		columns = ['Cleaner', 'Status', 'Occupied Hours', 'Total Working Hours', 'Efficiency (%)']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)
		
		# Get active workers during the period
		try:
			total_active_workers = CleaningTeamMember.objects.filter(
				Q(is_active=True) & Q(team__order_scheduler__end_at__range=(prev_date_start, todate_date_end))
			).values_list('member', flat=True).distinct().union(
				FollowUpTeamMember.objects.filter(
					Q(is_active=True) & Q(end_at__range=(prev_date_start, todate_date_end))
				).values_list('member', flat=True)
			).distinct()
		except:
			total_active_workers = []
		
		rows = []
		employee_detailed_data = {}  # Store detailed data for second sheet
		visit_data = {}  # Store visit-specific data
		
		# First, collect all order visits in the date range
		all_order_visits = OrderScheduler.objects.filter(
			start_at__range=(prev_date_start, todate_date_end),
			is_active=True
		).select_related(
			'order', 'evaluation_details', 'order_scheduler_book'
		).prefetch_related(
			'cleaning_team_order_scheduler__cleaning_member_team__member'
		)
		
		# Process order visits first to create a visit data structure
		for visit in all_order_visits:
			order_no = visit.order.order_no
			visit_id = visit.id
			visit_date = datetime.strftime(visit.start_at, '%d-%m-%Y')
			
			if order_no not in visit_data:
				visit_data[order_no] = {
					'order_no': order_no,
					'customer': visit.order.evaluation.customer.name if visit.order.evaluation.customer else 'N/A',
					'service_type': visit.order_scheduler_book.service_type.name if visit.order_scheduler_book and visit.order_scheduler_book.service_type else 'N/A',
					'location': visit.customer_address.area.name if visit.customer_address and visit.customer_address.area else 'N/A',
					'visits': {}
				}
			
			# Store visit details
			visit_data[order_no]['visits'][visit_id] = {
				'visit_id': visit_id,
				'date': visit_date,
				'start_time': datetime.strftime(visit.start_at, '%H:%M'),
				'end_time': datetime.strftime(visit.end_at, '%H:%M'),
				'budgeted_hours': visit.cleaning_hours,
				'actual_duration': (visit.end_at - visit.start_at).total_seconds() / 3600,
				'planned_cleaners': visit.no_of_cleaners,
				'hourly_rate': visit.hourly_cleaning_duration,
				'assigned_cleaners': []
			}
			
			# Add cleaning team members
			if hasattr(visit, 'cleaning_team') and visit.cleaning_team:
				team_members = CleaningTeamMember.objects.filter(
					team=visit.cleaning_team,
					is_active=True
				).select_related('member')
				
				for team_member in team_members:
					cleaner_info = {
						'id': team_member.member.id,
						'name': team_member.member.name,
						'role': 'TEAM LEADER' if team_member.member.user_type == 'TEAMINCHARGE' else 'CLEANER'
					}
					visit_data[order_no]['visits'][visit_id]['assigned_cleaners'].append(cleaner_info)
		
		# Now process follow-up visits
		all_followup_visits = FollowUpScheduler.objects.filter(
			start_at__range=(prev_date_start, todate_date_end),
			is_active=True
		).select_related(
			'follow_up__investigation__order'
		).prefetch_related(
			'followupteam_followupschedule__followup_team_members__member'
		)
		
		for followup in all_followup_visits:
			if not followup.follow_up or not followup.follow_up.investigation or not followup.follow_up.investigation.order:
				continue
				
			order_no = followup.follow_up.investigation.order.order_no
			visit_id = f"FU-{followup.id}"
			visit_date = datetime.strftime(followup.start_at, '%d-%m-%Y')
			
			if order_no not in visit_data:
				visit_data[order_no] = {
					'order_no': order_no,
					'customer': followup.follow_up.investigation.order.evaluation.customer.name 
						if followup.follow_up.investigation.order.evaluation.customer else 'N/A',
					'service_type': 'Follow-up',
					'location': followup.follow_up.investigation.address.area.name 
						if followup.follow_up.investigation.address and followup.follow_up.investigation.address.area else 'N/A',
					'visits': {}
				}
			
			# Store follow-up visit details
			visit_data[order_no]['visits'][visit_id] = {
				'visit_id': visit_id,
				'date': visit_date,
				'start_time': datetime.strftime(followup.start_at, '%H:%M'),
				'end_time': datetime.strftime(followup.end_at, '%H:%M'),
				'budgeted_hours': 2,  # Default for follow-ups
				'actual_duration': (followup.end_at - followup.start_at).total_seconds() / 3600,
				'planned_cleaners': 1,  # Default for follow-ups
				'hourly_rate': 1,      # Default for follow-ups
				'assigned_cleaners': []
			}
			
			# Add follow-up team members
			if hasattr(followup, 'team') and followup.team:
				team_members = FollowUpTeamMember.objects.filter(
					team=followup.team,
					is_active=True
				).select_related('member')
				
				for team_member in team_members:
					cleaner_info = {
						'id': team_member.member.id,
						'name': team_member.member.name,
						'role': 'TEAM LEADER' if team_member.member.user_type == 'TEAMINCHARGE' else 'CLEANER'
					}
					visit_data[order_no]['visits'][visit_id]['assigned_cleaners'].append(cleaner_info)
		
		# Now process employee data with visit information
		for worker in total_active_workers:
			employees = []
			employee = UserProfile.objects.get(id=int(worker))
			
			# Get all cleanings for this employee in the date range (similar to previous code)
			employee_cleanings_list = CleaningTeamMember.objects.filter(
				Q(is_active=True) & Q(member__id=employee.id) & 
				Q(team__order_scheduler__end_at__range=(prev_date_start, todate_date_end))
			).values_list(
				'team__order_scheduler__order__order_no',
				'team__order_scheduler__start_at',
				'team__order_scheduler__end_at',
				'team__order_scheduler__id',  # Added to identify specific visits
				'team__order_scheduler__no_of_cleaners',
				'team__order_scheduler__cleaning_hours',
				'team__order_scheduler__hourly_cleaning_duration'
			).union(
				FollowUpTeamMember.objects.filter(
					Q(is_active=True) & Q(member__id=employee.id) & 
					Q(end_at__range=(prev_date_start, todate_date_end))
				).values_list(
					'team__followup_scheduler__follow_up__investigation__order__order_no',
					'start_at',
					'end_at',
					Value(-1, output_field=IntegerField()),  # Placeholder for followup_id
					Value(1, output_field=IntegerField()),   # Default no_of_cleaners for followup
					Value(2, output_field=IntegerField()),   # Default cleaning_hours for followup
					Value(1, output_field=IntegerField())    # Default hourly_duration for followup
				)
			)
			
			# Calculate occupied hours
			cleaning_durations = []
			detailed_order_data = []
			employee_visits = []
			
			for cleaning in employee_cleanings_list:
				order_no = cleaning[0]
				start_time = cleaning[1]
				end_time = cleaning[2]
				visit_id = cleaning[3]
				no_of_cleaners = cleaning[4]
				budgeted_hours = cleaning[5]
				hourly_duration = cleaning[6]
				
				# Skip if order_no is None (can happen with deleted records)
				if not order_no:
					continue
				
				# Calculate duration for this cleaning
				duration_list = [] 
				duration_list.append(int(datetime.strftime(start_time, '%H')))
				duration_list.append(int(datetime.strftime(end_time, '%H')))
				duration_list.append(datetime.strftime(end_time, '%d-%m-%Y'))
				cleaning_durations.append(duration_list)
				
				# Find visit details for this order
				visit_key = visit_id if visit_id > 0 else f"FU-{abs(visit_id)}"
				
				# Store detailed info for order sheet
				if order_no in visit_data and visit_key in visit_data[order_no]['visits']:
					visit_info = visit_data[order_no]['visits'][visit_key]
					
					detailed_info = {
						'order_no': order_no,
						'date': datetime.strftime(start_time, '%d-%m-%Y'),
						'start_time': datetime.strftime(start_time, '%H:%M'),
						'end_time': datetime.strftime(end_time, '%H:%M'),
						'budgeted_hours': budgeted_hours,
						'actual_hours': (end_time - start_time).total_seconds() / 3600,
						'no_of_cleaners': no_of_cleaners,
						'hourly_duration': hourly_duration,
						'visit_id': visit_key,
						'customer': visit_data[order_no].get('customer', 'N/A'),
						'service_type': visit_data[order_no].get('service_type', 'N/A'),
						'location': visit_data[order_no].get('location', 'N/A'),
						'total_assigned_cleaners': len(visit_info.get('assigned_cleaners', []))
					}
					
					detailed_order_data.append(detailed_info)
					employee_visits.append(visit_key)
			
			# Store detailed data for employee sheets
			employee_detailed_data[employee.id] = {
				'name': employee.name,
				'status': 'Active' if employee.is_active else 'Inactive',
				'orders': detailed_order_data,
				'visits': employee_visits
			}
			
			# Calculate total occupied hours using the existing slot logic
			# (Same as in previous version)
			new_cleaning_durations = []
			output = []
			
			for i in cleaning_durations:
				if i[0] > i[1]:
					new_cleaning_durations = new_cleaning_durations + [[i[0], 24, i[2]], [0, i[1], i[2]]]
				else:
					new_cleaning_durations = new_cleaning_durations + [i]
			
			total_duration = 0
			final_slots = []
			for i in new_cleaning_durations:
				slots = return_slots(i[0], i[1], i[2])
				output.append(slots)
			
			# Calculate duration for each date
			for date in daterange:
				str_date = datetime.strftime(date, '%d-%m-%Y')
				date_slot_list = []
				
				for elem in output:
					if str_date == elem[0]:
						elem.pop(0)
						for obj in elem:
							date_slot_list.append(obj)
				
				final_slots = (list(set(date_slot_list)))
				duration = len(final_slots) * 2
				total_duration += duration
			
			# Calculate total working hours (same as before)
			leave_schedules = LeaveSchedule.objects.filter(
				staff=employee, 
				leave_date__range=(prev_date_start, todate_date_end - timedelta(days=1))
			).values_list('leave_date', flat=True).distinct().count()
			
			worked_days = int((todate_date_end - prev_date_start).days) - int(leave_schedules)
			total_working_hours = worked_days * 10
			
			# Calculate efficiency
			efficiency = (total_duration / total_working_hours * 100) if total_working_hours > 0 else 0
			
			# Prepare row for summary sheet
			employees.append(employee.name)
			employees.append('Active' if employee.is_active else 'Inactive')
			employees.append(total_duration)
			employees.append(total_working_hours)
			employees.append(f"{efficiency:.2f}%")
			
			rows.append(employees)
		
		# Write summary data
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)
		
		# Sheet 2: Visits Detailed Report
		ws_visits = wb.add_sheet('VISITS DETAILED REPORT')
		
		visits_columns = [
			'Order No', 'Customer', 'Service Type', 'Location', 'Visit Date', 'Visit ID', 
			'Start Time', 'End Time', 'Budgeted Hours', 'Actual Hours', 
			'Planned Team Size', 'Actual Team Size', 'Hourly Rate', 'Team Members'
		]
		
		for col_num in range(len(visits_columns)):
			ws_visits.write(0, col_num, visits_columns[col_num], font_style)
		
		visits_row = 0
		
		# Write visit data
		for order_no, order_info in visit_data.items():
			for visit_id, visit_info in order_info['visits'].items():
				visits_row += 1
				
				# Format team members as comma-separated list
				team_members = ", ".join([member['name'] + ' (' + member['role'] + ')' 
										for member in visit_info['assigned_cleaners']])
				
				visit_row_data = [
					order_no,
					order_info['customer'],
					order_info['service_type'],
					order_info['location'],
					visit_info['date'],
					visit_id,
					visit_info['start_time'],
					visit_info['end_time'],
					visit_info['budgeted_hours'],
					f"{visit_info['actual_duration']:.2f}",
					visit_info['planned_cleaners'],
					len(visit_info['assigned_cleaners']),
					visit_info['hourly_rate'],
					team_members
				]
				
				for col_num in range(len(visit_row_data)):
					ws_visits.write(visits_row, col_num, visit_row_data[col_num], font_style)
		
		# Sheet 3: Employee Detailed Report
		ws_detail = wb.add_sheet('EMPLOYEE DETAILED REPORT')
		
		detail_columns = [
			'Cleaner', 'Order No', 'Customer', 'Service Type', 'Location', 'Visit Date', 
			'Visit ID', 'Start Time', 'End Time', 'Budgeted Hours', 'Actual Hours', 
			'Total Team Size', 'Hourly Rate'
		]
		
		for col_num in range(len(detail_columns)):
			ws_detail.write(0, col_num, detail_columns[col_num], font_style)
		
		detail_row = 0
		
		# Write detailed employee data
		for employee_id, data in employee_detailed_data.items():
			employee_name = data['name']
			for order in data['orders']:
				detail_row += 1
				
				detail_data = [
					employee_name,
					order['order_no'],
					order['customer'],
					order['service_type'],
					order['location'],
					order['date'],
					order['visit_id'],
					order['start_time'],
					order['end_time'],
					order['budgeted_hours'],
					f"{order['actual_hours']:.2f}",
					order['total_assigned_cleaners'],
					order['hourly_duration']
				]
				
				for col_num in range(len(detail_data)):
					ws_detail.write(detail_row, col_num, detail_data[col_num], font_style)
		
		# Sheet 4: Shift Analysis (similar to previous version)
		ws_shift = wb.add_sheet('SHIFT ANALYSIS')
		
		shift_columns = ['Cleaner', 'Date', 'Official Shift Hours', 'Occupied Hours', 'Idle Hours', 'Efficiency (%)', 'Visit Count']
		
		for col_num in range(len(shift_columns)):
			ws_shift.write(0, col_num, shift_columns[col_num], font_style)
		
		shift_row = 0
		
		# Calculate shift data per day for each employee
		for employee_id, data in employee_detailed_data.items():
			employee_name = data['name']
			employee = UserProfile.objects.get(id=int(employee_id))
			
			# For each date in the range
			for date in daterange:
				shift_row += 1
				str_date = datetime.strftime(date, '%d-%m-%Y')
				
				# Check if employee has leave on this date
				has_leave = LeaveSchedule.objects.filter(
					staff=employee, 
					leave_date=date.date()
				).exists()
				
				if has_leave:
					shift_data = [
						employee_name,
						str_date,
						"On Leave",
						0,
						0,
						"0.00%",
						0
					]
				else:
					# Calculate occupied hours for this date
					date_orders = [order for order in data['orders'] if order['date'] == str_date]
					daily_occupied_hours = sum(order['actual_hours'] for order in date_orders)
					visit_count = len(date_orders)
					
					official_shift_hours = 10  # Standard shift hours
					idle_hours = max(0, official_shift_hours - daily_occupied_hours)
					daily_efficiency = (daily_occupied_hours / official_shift_hours * 100) if official_shift_hours > 0 else 0
					
					shift_data = [
						employee_name,
						str_date,
						official_shift_hours,
						f"{daily_occupied_hours:.2f}",
						f"{idle_hours:.2f}",
						f"{daily_efficiency:.2f}%",
						visit_count
					]
				
				for col_num in range(len(shift_data)):
					ws_shift.write(shift_row, col_num, shift_data[col_num], font_style)
		
		# Sheet 5: Order Analysis
		ws_orders = wb.add_sheet('ORDER ANALYSIS')
		
		order_columns = [
			'Order No', 'Customer', 'Service Type', 'Location', 'Total Visits', 
			'Total Budgeted Hours', 'Total Actual Hours', 'Total Cleaners Used', 
			'Average Team Size', 'Start Date', 'End Date'
		]
		
		for col_num in range(len(order_columns)):
			ws_orders.write(0, col_num, order_columns[col_num], font_style)
		
		order_row = 0
		
		# Calculate order statistics
		for order_no, order_info in visit_data.items():
			order_row += 1
			
			total_visits = len(order_info['visits'])
			total_budgeted_hours = sum(visit['budgeted_hours'] for visit in order_info['visits'].values())
			total_actual_hours = sum(visit['actual_duration'] for visit in order_info['visits'].values())
			
			# Calculate total cleaners used (unique cleaners across all visits)
			all_cleaners = set()
			for visit in order_info['visits'].values():
				for cleaner in visit['assigned_cleaners']:
					all_cleaners.add(cleaner['id'])
			
			# Calculate average team size
			avg_team_size = sum(len(visit['assigned_cleaners']) for visit in order_info['visits'].values()) / total_visits if total_visits > 0 else 0
			
			# Determine start and end dates
			visit_dates = [datetime.strptime(visit['date'], '%d-%m-%Y') for visit in order_info['visits'].values()]
			start_date = min(visit_dates).strftime('%d-%m-%Y') if visit_dates else 'N/A'
			end_date = max(visit_dates).strftime('%d-%m-%Y') if visit_dates else 'N/A'
			
			order_data = [
				order_no,
				order_info['customer'],
				order_info['service_type'],
				order_info['location'],
				total_visits,
				total_budgeted_hours,
				f"{total_actual_hours:.2f}",
				len(all_cleaners),
				f"{avg_team_size:.2f}",
				start_date,
				end_date
			]
			
			for col_num in range(len(order_data)):
				ws_orders.write(order_row, col_num, order_data[col_num], font_style)

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

	# if report_type == 'systemuserslist':

	# 	response = HttpResponse(content_type='application/ms-excel')
	# 	response['Content-Disposition'] = 'attachment; filename="BLEACH_CRM_SYSTEM_USERS.xls"'

	# 	wb = xlwt.Workbook(encoding='utf-8')
	# 	ws = wb.add_sheet('BLEACH CRM SYSTEM USERS')

	# 	columns = ['Name','Username','User Type','Is Active']
		
	# 	for col_num in range(len(columns)):
	# 		ws.write(row_num, col_num, columns[col_num], font_style)

	# 	users = UserProfile.objects.filter(~Q( Q(user_type='CUSTOMER')|Q(user_type=None) )).values_list('name','username','user_type','is_active')
	
	# 	for row in users:
	# 		row_num += 1
	# 		for col_num in range(len(row)):
	# 			ws.write(row_num, col_num, row[col_num], font_style)
	
	
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
		# response['Content-Disposition'] = 'attachment; filename="SALES_REPORT_'+from_date+'_'+to_date+'.xls"'
		
		# rows = []

		# for date in daterange:
		# 	# print(date,"deyit")

		# 	start_date_day = date
		# 	end_date_day   = date+timedelta(1)-timedelta(minutes=1)

		# 	gross_amount = 0
		# 	subtraction_amount = 0
		# 	addition_amount = 0
		# 	list_item = []
			
		# 	#date setup for getting schedules on specified date
		# 	todays_date = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

		# 	if date < todays_date:
		# 		orderschedules = OrderScheduler.objects.select_related('order').prefetch_related('order__order_scheduler_order').filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q( Q(work_status = 'CLEANING_CANCELLED') | Q(work_status='CLEANING_FULFILLED') )).annotate(no_of_order_visits=Count('order__order_scheduler_order'))
		# 	else:
		# 		orderschedules = OrderScheduler.objects.select_related('order').prefetch_related('order__order_scheduler_order').filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q( Q(work_status = 'CLEANING_CANCELLED') | Q(work_status='CLEANING_FULFILLED') | Q(work_status='CLEANING_TEAM_ASSIGNED') | Q(work_status='CLEANING_IN_PROGRESS'))).annotate(no_of_order_visits=Count('order__order_scheduler_order'))

		# 	for schedule in orderschedules:
				
		# 		try:
		# 			refund = CancellOrderAmountHistory.objects.filter(order=schedule.order).first()
		# 			refund_amount = refund.return_amount
		# 		except:
		# 			refund = None
		# 			refund_amount = 0
				
		# 		if schedule.cleaning_cost:
		# 			gross_amount += float(schedule.cleaning_cost)
		# 		else:
		# 			gross_amount += 0

		# 		addition_amount    += (float(schedule.order.evaluation.fine_amount)/float(schedule.no_of_order_visits)) + float(0 if schedule.additional_charge_cost is None else schedule.additional_charge_cost)

		# 		order_service_cancelled_amount = 0

		# 		if schedule.order_scheduler_book.cleaning_policy == 'SUBSCRIPTION':
		# 			if schedule.order.order_status == 'ORDER_CANCELLED':
		# 				order_schedules_cancelled_sum = OrderScheduler.objects.filter(order_scheduler_book=schedule.order_scheduler_book,work_status='CLEANING_CANCELLED').aggregate(order_sum=Sum('cleaning_cost'))['order_sum']
		# 				order_service_cancelled_amount = float(order_schedules_cancelled_sum)
		# 			else:
		# 				if schedule.order_scheduler_book.status == 'CANCELLED':
		# 					service_schedules_cancelled_sum = OrderScheduler.objects.filter(order_scheduler_book=schedule.order_scheduler_book,work_status='CLEANING_CANCELLED').aggregate(service_sum=Sum('cleaning_cost'))['service_sum']
		# 					order_service_cancelled_amount = float(service_schedules_cancelled_sum)
		# 				else:
		# 					pass
					
		# 			subtraction_amount += ( float(schedule.order.evaluation.cancelled_amount)+float(refund_amount)+float(schedule.order.evaluation.writeback_amount)+float(order_service_cancelled_amount)+float(schedule.order.evaluation.promocode_amount) )/float(schedule.no_of_order_visits) + float(0 if schedule.discount_cost is None else schedule.discount_cost)
					
		# 		else:
					
		# 			subtraction_amount += ( float(schedule.order.evaluation.cancelled_amount)+float(refund_amount)+float(schedule.order.evaluation.writeback_amount)+float(schedule.order.evaluation.promocode_amount) )/float(schedule.no_of_order_visits) + float(0 if schedule.discount_cost is None else schedule.discount_cost)
				
		# 	list_item = [str(date.date()),date.strftime("%A"),gross_amount,subtraction_amount,addition_amount,round( float(gross_amount) - float(subtraction_amount) + float(addition_amount), 2)]
	
		# 	rows.append(list_item)	
			
		# rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]


		# #sales report
		# ws2 = wb.add_sheet('SALES REPORT',cell_overwrite_ok = True)
	
		# columns2 = ['Date','Day','Gross Sales','Subtraction','Addition','Net Sales']
		
		# for col_num in range(len(columns2)):
		# 	ws2.write(row_num2, col_num, columns2[col_num], font_style)	

		# for row in rows:
		# 	row_num2 += 1
		# 	for col_num in range(len(row)):
		# 		ws2.write(row_num2, col_num, row[col_num], font_style)
	
		#----------------------------------------------------------------------------------

		#individual sales
		response['Content-Disposition'] = 'attachment; filename="SALES_DETAILS_COMPLETED_'+from_date+'_'+to_date+'.xls"'
		
		#date setup for getting schedules on specified date
		todays_date = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

		orderschedules_details = OrderScheduler.objects.select_related('order').prefetch_related('order__order_scheduler_order').filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(prev_date_start,todate_date_end)).filter(Q( Q(work_status = 'CLEANING_CANCELLED') | Q(work_status='CLEANING_FULFILLED') | Q(work_status='CLEANING_TEAM_ASSIGNED') | Q(work_status='CLEANING_IN_PROGRESS')))

		#sales details
		ws = wb.add_sheet('SALES DETAILS',cell_overwrite_ok = True)
	
		columns = ['Order No.','Service Date','Service Day','Customer','Payment Policy','Cleaning Policy','Salesman','Gross Amount']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		rows2 = []
		schedule_list = []

		for schedule in orderschedules_details:

			if schedule.end_at.date() < todays_date.date():
				if schedule.work_status == 'CLEANING_CANCELLED' or schedule.work_status == 'CLEANING_FULFILLED':

					#calculating schedule total
					if schedule.cleaning_cost:
						gross_amount = float(schedule.cleaning_cost) or 0
					else:
						gross_amount = 0

					if schedule.evaluation_details.evaluator:
						salesman = schedule.evaluation_details.evaluator.name
					else:
						salesman = schedule.order.evaluation.call_attender.name

					schedule_list = [schedule.order.order_no,str(schedule.end_at.date()),schedule.end_at.strftime("%A"),schedule.order.evaluation.customer.name,schedule.order.evaluation.payment_method,schedule.order_scheduler_book.cleaning_policy,salesman,gross_amount]
					
					rows2.append(schedule_list)
			
			if schedule.end_at.date() > todays_date.date():
				if schedule.work_status == 'CLEANING_CANCELLED' or schedule.work_status == 'CLEANING_FULFILLED' or schedule.work_status == 'CLEANING_TEAM_ASSIGNED' or schedule.work_status == 'CLEANING_IN_PROGRESS':
		
					#calculating schedule total
					if schedule.cleaning_cost:
						gross_amount = float(schedule.cleaning_cost) or 0
					else:
						gross_amount = 0

					if schedule.evaluation_details.evaluator:
						salesman = schedule.evaluation_details.evaluator.name
					else:
						salesman = schedule.order.evaluation.call_attender.name

					schedule_list = [schedule.order.order_no,str(schedule.end_at.date()),schedule.end_at.strftime("%A"),schedule.order.evaluation.customer.name,schedule.order.evaluation.payment_method,schedule.order_scheduler_book.cleaning_policy,salesman,gross_amount]
					
					rows2.append(schedule_list)

		rows2 = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows2 ]

		print(rows2,"roser")

		for row in rows2:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

	if report_type == 'non_checked_out_schedules':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="CHECKOUT_PENDING_'+from_date+'_'+to_date+'.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		
		#sales details
		ws = wb.add_sheet('CHECKOUT_PENDING',cell_overwrite_ok = True)
	
		columns = ['Cleaning Date','BLC No.','Team Leader','Check-In Time']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)	

		start_date_day = prev_date_start.replace(hour=0,minute=0,second=0,microsecond=0)
		end_date_day   = todate_date_end.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(1)-timedelta(minutes=1)
		print(start_date_day,end_date_day,"daterrr")
		cleaningteams = CleaningTeam.objects.filter(is_active=True,check_in__range=(start_date_day,end_date_day),check_out=None)

		rows = []
		team_data = []
		for team in cleaningteams:
			check_in_time = datetime.strftime(team.check_in,'%I:%M %p')
			team_data = [team.start_at.date(),team.order_scheduler.order.order_no,team.team_leader.name,check_in_time]
		
		rows.append(team_data)

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]

		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, str(row[col_num]), font_style)

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

	if report_type == 'Customer_Details':
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="CUSTOMER_DETAILS.xls"'

		wb = xlwt.Workbook(encoding='utf-8')
		
		#Sheet 1 Customers
		ws = wb.add_sheet('CUSTOMERS',cell_overwrite_ok = True)
	
		columns = ['Name','Mobile No','Email','Governorate','Area']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		users = UserProfile.objects.filter(is_active=True,user_type='CUSTOMER').prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True),to_attr='customer_addresses')).values_list('name','mobile_number','email','address_customer__governorate__name','address_customer__area__name').distinct()
		rows = users

		mobile_numbers_duplicate = []
		for row in rows:
			if not row[1] in mobile_numbers_duplicate:
				row_num += 1
				mobile_numbers_duplicate.append(row[1])
				for col_num in range(len(row)):
					ws.write(row_num, col_num, row[col_num], font_style)

	wb.save(response)

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

		#Xero Integration
		# xero                        = XeroConnection.objects.first()
		# ##xero Update Access Token and Refresh Token
		# header                      = {
		# 								'Authorization': 'Basic '+xero.client_encoded,
		# 								'Content-Type': 'application/x-www-form-urlencoded'
		# 									}
		# body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
		# token_response              = requests.post('https://identity.xero.com/connect/token',
		# 										data=body,
		# 										headers=header 
		# 									).json()
		# access_token                = token_response['access_token']
		# refresh_token               = token_response['refresh_token']

		# xero.access_token  = access_token
		# xero.refresh_token = refresh_token
		# xero.save()

		#Last Send Invoice Cancellation
		cashback_history              = CancellOrderAmountHistory.objects.select_related('order').get(id=cashback_id)
		order                         = cashback_history.order

		##xero Delete Invoice
		# header                      = {
		# 								'xero-tenant-id': xero.tenant_id,
		# 								'Authorization': 'Bearer '+access_token,
		# 								'Accept': 'application/json',
		# 								'Content-Type': 'application/json'
		# 									}
		# if order.evaluation.payment_method == 'PREPAID' or 'POSTPAID':
		# 	InvoiceNumber       = order.invoice_no
		# 	invoice_data        = 	{
		# 							"Type":"ACCREC",
		# 							"LineAmountTypes":"NoTax",
		# 							"InvoiceNumber":InvoiceNumber,
		# 							"Reference":order.order_no,
		# 							"Status":"DELETED"
		# 						}

		# 	delete_invoice      = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
		# 											json=invoice_data,
		# 											headers=header 
		# 										).json()
			
		# elif order.evaluation.payment_method == 'BREAKDOWN':
		# 	InvoiceNumber       = order.invoice_no+'A'
		# 	invoice_data        = 	{
		# 							"Type":"ACCREC",
		# 							"LineAmountTypes":"NoTax",
		# 							"InvoiceNumber":InvoiceNumber,
		# 							"Reference":order.order_no,
		# 							"Status":"DELETED"
		# 						}

		# 	delete_invoice      = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
		# 											json=invoice_data,
		# 											headers=header 
		# 										).json()

		# 	InvoiceNumber       = order.invoice_no+'B'
		# 	invoice_data        = 	{
		# 							"Type":"ACCREC",
		# 							"LineAmountTypes":"NoTax",
		# 							"InvoiceNumber":InvoiceNumber,
		# 							"Reference":order.order_no,
		# 							"Status":"DELETED"
		# 						}
								
		# 	delete_invoice      = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
		# 											json=invoice_data,
		# 											headers=header 
		# 										).json()

		# elif order.evaluation.payment_method == 'SUBSCRIPTION':
		# 	try:
		# 		last_invoice = XeroInvoice.objects.filter(order=order,is_paid=False).last()
		# 	except:
		# 		last_invoice = None
			
		# 	if last_invoice:
		# 		InvoiceNumber       = last_invoice.invoice_no
		# 		invoice_data        = 	{
		# 								"Type":"ACCREC",
		# 								"LineAmountTypes":"NoTax",
		# 								"InvoiceNumber":InvoiceNumber,
		# 								"Reference":order.order_no,
		# 								"Status":"DELETED"
		# 							}
									
		# 		delete_invoice      = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
		# 												json=invoice_data,
		# 												headers=header 
		# 											).json()
		
		#Update
		cashback_history.order.remining_amount  = 0
		cashback_history.order.amount_paid     -= float(return_amount)
		cashback_history.order.order_status     = 'ORDER_CANCELLED'
		cashback_history.is_completed           = True
		cashback_history.return_amount          = float(return_amount)
		cashback_history.order.save()
		cashback_history.save()

		return redirect('accountant:accountantdash-board')


	