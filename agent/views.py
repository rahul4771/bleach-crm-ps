from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.views import View
from django.forms import formset_factory,modelformset_factory
from django.http import HttpResponse,JsonResponse

from django.conf import settings
from bleach_crm_ps.permissions import IsAgent
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

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory

from agent.forms import UserProfileForm,AddressForm
from evaluator.forms import EvaluationDetailsForm,QuatationServiceForm
from order.forms import InvestigationForm

from django.db.models import Count

from dateutil.relativedelta import relativedelta

#Username Random Generation
def generate_random_username(size=10, chars=string.ascii_uppercase + string.digits):

	username = ''.join(random.choice(chars) for n in range(size))


	try:
		UserProfile.objects.get(username=username)
		return generate_random_username(size=10, chars=string.ascii_uppercase + string.digits)
	except UserProfile.DoesNotExist:
		return username

def UpdateAddressStatus(request):
	address_id     = request.GET.get('address_id')
	address_status = request.GET.get('status')

	if address_status == 'true':
		Address.objects.filter(id=address_id).update(currently_active=True)
	else:
		Address.objects.filter(id=address_id).update(currently_active=False)

	data = {}

	data['address_id']     = address_id
	data['address_status'] = address_status

	return JsonResponse(data)

def MobileNumberValidate(request):
	mobile_no = request.GET.get('mobile_number')
	data 	  = {}

	try:
		existing_user = UserProfile.objects.get(mobile_number=mobile_no)
		data['validation']= False
	except:
		data['validation']= True
			
	return JsonResponse(data)

#Ajax for governorates Area
def GetArea(request):

	governorate_id        = request.GET.get('governorate_id')

	try:
		areas = Area.objects.filter(is_active=True,governorate_id=governorate_id)
	except:
		areas = None

	dropdown_areas={}

	if areas:
		for area in areas:
			dropdown_areas[area.id] = area.name

	return JsonResponse(dropdown_areas)

#Ajax for get feedback Order Information
def GetFeedbackOrderInfo(request):

		dropdown_order_info = {}

		order_id            = request.GET.get('order_id')

		order = Order.objects.select_related('evaluation__customer','evaluation__call_attender').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('customer_address__area','customer_address','order_scheduler_book__service_type'),to_attr='order_secheduler_feedback')).annotate(total_cleaners=Sum('order_scheduler_order__order_scheduler_book__number_of_cleaners')).get(id=order_id,is_active=True)
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
		if order.evaluation.payment_method == 'SUBSCRIPTION':
			dropdown_order_info['subscription_amount'] = order.remining_amount


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

def GetCleaningInfo(request):
	cleaning_dict = {}

	scheduler_id  = int(request.GET.get('schedule_id'))
	print(scheduler_id)
	schedule  = OrderScheduler.objects.select_related('order_scheduler_book','customer_address__customer','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_member')),to_attr='cleaning_team')).get(id=scheduler_id,is_active=True)

	print(schedule)

	if schedule.customer_address.floor == None and schedule.customer_address.avenue == None:
		address_list = [schedule.customer_address.apartment, schedule.customer_address.street, schedule.customer_address.building, schedule.customer_address.block, schedule.customer_address.area.name, schedule.customer_address.governorate.name]
	
	elif schedule.customer_address.floor == None:
		address_list = [schedule.customer_address.apartment, schedule.customer_address.street, schedule.customer_address.building, schedule.customer_address.avenue, schedule.customer_address.block, schedule.customer_address.area.name, schedule.customer_address.governorate.name]
	
	elif schedule.customer_address.avenue == None:
		address_list = [schedule.customer_address.apartment, schedule.customer_address.floor, schedule.customer_address.street, schedule.customer_address.building, schedule.customer_address.block, schedule.customer_address.area.name, schedule.customer_address.governorate.name]
	
	else:
		address_list = [schedule.customer_address.apartment, schedule.customer_address.floor, schedule.customer_address.street, schedule.customer_address.building, schedule.customer_address.avenue, schedule.customer_address.block, schedule.customer_address.area.name, schedule.customer_address.governorate.name]

	separator = ", "

	cleaning_dict['order_id'] 		 = schedule.order.id
	cleaning_dict['order_no'] 		 = schedule.order.order_no
	cleaning_dict['address']  		 = separator.join(address_list)
	cleaning_dict['customer'] 		 = schedule.customer_address.customer.name
	cleaning_dict['customer_mobile'] = schedule.customer_address.customer.mobile_number
	cleaning_dict['start_at_date']   = (schedule.start_at+timedelta(hours=3)).strftime('%d-%m-%Y')
	cleaning_dict['start_at_time']   = (schedule.start_at+timedelta(hours=3)).strftime('%I:%M %p')
	cleaning_dict['duration']		 = schedule.order_scheduler_book.cleaning_hours

	if schedule.work_status == 'CLEANING_FULFILLED':
		cleaning_dict['status'] = 'Cleaning Completed'
	elif schedule.work_status == 'CLEANING_TEAM_ASSIGNED' or schedule.work_status == 'CLEANING_FULFILLED':
		cleaning_dict['status'] = 'Cleaning Team Assigned'
	elif schedule.status == 'CONFIRMED':
		cleaning_dict['status'] = 'Date Confirmed'
	else:
		cleaning_dict['status'] = 'Waiting For Date Confirmation'

	#cleaners and team leader
	cleaners_info ={}

	cleaners_info['cleaners']   = []
	for team in schedule.cleaning_team:
		cleaning_dict['team_leader'] 	= team.team_leader.name
		cleaning_dict['team_leader_id'] = team.team_leader.id
		cleaning_dict['stl']            = team.created_by.name
		for cleaner in team.cleaning_member:
			cleaner_dict = {}

			if cleaner.member.id != team.team_leader.id:
				cleaner_dict["member_name"] 	= cleaner.member.name
				cleaner_dict["member_id"] 		= cleaner.member.id

				cleaners_info['cleaners'].append(cleaner_dict)

	cleaning_dict['cleanersinfo'] =	cleaners_info
	return JsonResponse(cleaning_dict)

def GetFollowupInfo(request):
	cleaning_dict = {}

	scheduler_id  = request.GET.get('schedule_id')

	schedule  = FollowUpScheduler.objects.select_related('customer_address__customer','follow_up__investigation__order').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_member')),to_attr='cleaning_team')).get(id=scheduler_id)

	cleaning_dict['order_no'] 		 = schedule.follow_up.investigation.order.order_no
	cleaning_dict['address']  		 = schedule.customer_address.apartment+', '+schedule.customer_address.block+', '+schedule.customer_address.street+', '+schedule.customer_address.avenue+', '+schedule.customer_address.building+', '+schedule.customer_address.area.name+', '+schedule.customer_address.governorate.name
	cleaning_dict['customer'] 		 = schedule.customer_address.customer.name
	cleaning_dict['customer_mobile'] = schedule.customer_address.customer.mobile_number
	cleaning_dict['start_at_date']   = (schedule.start_at+timedelta(hours=3)).strftime('%d-%m-%Y')
	cleaning_dict['start_at_time']   = (schedule.start_at+timedelta(hours=3)).strftime('%I:%M %p')
	cleaning_dict['duration']		 = schedule.follow_up.cleaning_hours

	if schedule.work_status == 'FOLLOW_UP_CLEANING_FULFILLED':
		cleaning_dict['status'] = 'Cleaning Completed'
	elif schedule.work_status == 'FOLLOW_UP_TEAM_ASSIGNED' or schedule.work_status == 'FOLLOW_UP_CLEANING_IN_PROGRESS':
		cleaning_dict['status'] = 'Cleaning Team Assigned'
	elif schedule.status == 'CONFIRMED':
		cleaning_dict['status'] = 'Date Confirmed'
	else:
		cleaning_dict['status'] = 'Waiting For Date Confirmation'

	#cleaners and team leader
	cleaners_info ={}

	cleaners_info['cleaners']   = []
	for team in schedule.cleaning_team:
		cleaning_dict['team_leader'] 	= team.team_leader.name
		cleaning_dict['team_leader_id'] = team.team_leader.id
		cleaning_dict['stl']            = team.created_by.name
		for cleaner in team.cleaning_member:
			cleaner_dict = {}

			cleaner_dict["member_name"] 	= cleaner.member.name
			cleaner_dict["member_id"] 		= cleaner.member.id

			cleaners_info['cleaners'].append(cleaner_dict)

	cleaning_dict['cleanersinfo'] =	cleaners_info
	return JsonResponse(cleaning_dict)


#Ajax for getticket ordershedules address Information
def GetOrderScheduleTicketInfo(request):
	dropdown_orderschedule_info = {}

	order_id            = request.GET.get('order_id')

	try:
		ordershedules   = OrderScheduler.objects.filter(order_id=order_id,is_active=True,work_status='CLEANING_FULFILLED').select_related('customer_address__area','order_scheduler_book').prefetch_related(Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(check_out__isnull=True),to_attr='assigned_investigations'))
	except:
		ordershedules   = None

	order_schedule = {}
	for schedule in ordershedules:
		if not schedule.assigned_investigations:
			order_schedule[schedule.id] = schedule.customer_address.area.name+'-'+schedule.order_scheduler_book.service_type.name+'/'+datetime.strftime((schedule.start_at+timedelta(hours=3)),'%d-%m-%Y %I:%M %p') or ''

			dropdown_orderschedule_info['name']          = schedule.customer_address.customer.name
			dropdown_orderschedule_info['mobile_number'] = schedule.customer_address.customer.mobile_number

	dropdown_orderschedule_info['schedules'] = order_schedule
	dropdown_orderschedule_info['order_id']  = order_id


	return JsonResponse(dropdown_orderschedule_info)

#Ajax for getticket ordershedules address Information
def GetCleaningTicketInfo(request):
	dropdown_cleaning_info = {}

	scheduler_id            = request.GET.get('scheduler_id')

	try:
		scheduler_cleanings   = SheduledOrderCleanings.objects.filter(order_scheduler_id=scheduler_id,is_active=True).select_related('order_scheduler_book__cleaning_type')
	except:
		scheduler_cleanings   = None

	cleanings = {}
	for cleaning in scheduler_cleanings:
		cleanings[cleaning.id] = cleaning.order_scheduler_book.service_type.name

	dropdown_cleaning_info['cleaning_info'] = cleanings

	return JsonResponse(dropdown_cleaning_info)



#Ajax for get  allready registered users
def GetCustomerInfo(request):

	data               = {}
	customer_info_dict = {}

	query       =   request.GET.get('keyword')


	customer_info = UserProfile.objects.filter(is_active=True,user_type='CUSTOMER').filter(Q(Q(name__icontains=query)|Q(mobile_number__icontains=query)))


	if customer_info:
		for details in customer_info:
			customer_info_dict[details.id] = details.name+'-'+details.mobile_number

	data['customer_details'] = customer_info_dict


	data['status']     = 'true'

	if customer_info_dict == {}:
		data['status'] = 'false'

	return JsonResponse(data)

#aJAX for customer address
def GetCustomerAddress(request):

	data               	  = {}
	customer_address_dict = {}

	customer_id       	  =   request.GET.get('customer_id')


	customer_address = Address.objects.filter(is_active=True,customer__id=customer_id,currently_active=True).select_related('area')


	if customer_address:
		for address in customer_address:
			customer_address_dict[address.id] = address.area.name+'-'+address.building

	data['customer_address'] = customer_address_dict


	data['status']     = 'true'

	if customer_address_dict == {}:
		data['status'] = 'false'

	return JsonResponse(data)



def GetCustomerOrderInfoFeedback(request):
	data               = {}
	order_info_dict = {}

	query       =   request.GET.get('keyword')
	orders = Order.objects.filter(is_active=True,is_feedback_marked=False,payment_status='COMPLETED').select_related('evaluation__customer').filter(Q(Q(evaluation__evaluation_id__icontains=query)|Q(evaluation__customer__name__icontains=query))).prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))

	if orders:
		for order in orders: 
			order_info_dict[order.id] = order.evaluation.evaluation_id+'-'+order.evaluation.customer.name 	
	
	data['order_details'] = order_info_dict


	data['status']     = 'true'

	if order_info_dict == {}:
		data['status'] = 'false'

	return JsonResponse(data)

def GetCustomerOrderInfo(request):
	data               = {}
	order_info_dict = {}

	query       =   request.GET.get('keyword')

	orders = Order.objects.filter(is_active=True).select_related('evaluation__customer').filter(Q(evaluation__quatation_status='APPROVED') & Q(Q(evaluation__evaluation_id__icontains=query)|Q(evaluation__customer__name__icontains=query)) & ~Q(Q(order_status='ORDER_CANCELLED')))
	
	
	if orders:
		for order in orders:
			order_info_dict[order.id] = order.evaluation.evaluation_id+'-'+order.evaluation.customer.name 	
	
	data['order_details'] = order_info_dict


	data['status']     = 'true'

	if order_info_dict == {}: 
		data['status'] = 'false'	
	
	return JsonResponse(data)

#Ajax for getting Cleaning Types
def GetCleaningMethodsInfo(request):

	dropdown_methods = {}
	service_type_id = request.GET.get('service_type_id')

	try:
		cleaning_methods = CleaningMethod.objects.filter(is_active=True,service_type_id=service_type_id)
	except:
		cleaning_methods = None

	if cleaning_methods:
		for method in cleaning_methods:
			dropdown_methods[method.id] = method.name

	return JsonResponse(dropdown_methods)

#Ajax for getting Cleaning Types
def GetCleaningSectionInfo(request):

	dropdown_methods = {}
	service_type_id = request.GET.get('service_type_id')
	print(service_type_id,"id")
	cleaning_sections = CleaningSection.objects.filter(is_active=True,service_type_id=service_type_id)

	if cleaning_sections:
		for cleaning_section in cleaning_sections:
			dropdown_methods[cleaning_section.id] = cleaning_section.name

	return JsonResponse(dropdown_methods)


def RemoveSection(request):

	data ={}

	section_id = request.GET.get('section_id')
	print(section_id)
	try:
		section         = EvaluationBookSection.objects.select_related('evaluation_book__evaluation_details__evaluation').get(id=section_id)
		section.delete()
		data['success'] = True
	except:
		data['success'] = False

	return JsonResponse(data)

def RemoveKeynote(request):

	data ={}

	keynote_id = request.GET.get('keynote_id')

	try:
		EvaluationSectionKeynote.objects.filter(id=keynote_id).delete()
		data['success'] = True
	except:
		data['success'] = False

	return JsonResponse(data)

def RemovePaybackDiscountKeynote(request):

	data ={}

	keynote_id = request.GET.get('keynote_id')

	try:
		paybackdiscountdetails = PaybackDiscountDetails.objects.filter(id=keynote_id).first()
		paybackdiscount = PaybackDiscount.objects.filter(id = paybackdiscountdetails.paybackdiscount.id).first()
		paybackdiscount.total_cost -= float(paybackdiscountdetails.cost)
		paybackdiscount.save()
		PaybackDiscountDetails.objects.filter(id=keynote_id).delete()
		data['success'] = True
	except:
		data['success'] = False

	return JsonResponse(data)

def RemoveBuyBackPromoKeynote(request):

	data ={}

	keynote_id = request.GET.get('keynote_id')

	try:
		BuybackPromocodeGiftDetails.objects.filter(id=keynote_id).delete()
		buybackpromocode_details = BuybackPromocodeGiftDetails.objects.filter(id=keynote_id).first()
		buybackpromocode = BuybackPromocodeGift.objects.filter(id = buybackpromocode_details.buybackpromocodegift.id).first()
		buybackpromocode.total_cost -= float(buybackpromocode_details.cost)
		buybackpromocode.save()
		BuybackPromocodeGiftDetails.objects.filter(id=keynote_id).delete()
		data['success'] = True
	except:
		data['success'] = False

	return JsonResponse(data)

def RemoveEvaluationMedia(request):

	data ={}

	media_id = request.GET.get('media_id')

	try:
		EvaluationMedia.objects.filter(id=media_id).delete()
		data['success'] = True
	except:
		data['success'] = False

	return JsonResponse(data)

def GetOrdersSchedulesFromEvalDetails(request):
	data = {}
	evaluation_id = request.GET.get('evaluation_id')

	
	order_schedules = OrderScheduler.objects.select_related('evaluation_details','order_scheduler_book__service_type').filter(evaluation_details_id=evaluation_id,status='WAITING').order_by('-start_at')
	
	complete_schedule_details = []
	if order_schedules:
		for schedule in order_schedules:
			schedule_details = {}
			schedule_details['id']       = schedule.id
			schedule_details['start_at_time']   = (schedule.start_at+timedelta(hours=3)).strftime('%I:%M %p')
			schedule_details['start_at_date']   = ((schedule.start_at+timedelta(hours=3)).date()).strftime('%d-%m-%Y')
			schedule_details['cleaning_policy'] = schedule.order_scheduler_book.cleaning_policy
			schedule_details['service_type']    = schedule.order_scheduler_book.service_type.name
			complete_schedule_details.append(schedule_details)

	data['schedules_details'] = complete_schedule_details

	return JsonResponse(data)		

def CleaningExistingDates(request):
	data = {}
	booking_time      = request.GET.get('booking_time')
	no_of_cleaners    = request.GET.get('number_of_cleaners')
	cleaning_duration = int(request.GET.get('cleaning_duration'))
	service_type      = request.GET.get('service_type')
	print(service_type)
	
	start_at          = datetime.strptime(request.GET.get('booking_time'),'%I:%M %p').time()
	end_at            = (datetime.strptime(request.GET.get('booking_time'),'%I:%M %p')+timedelta(hours=cleaning_duration)).time()


	if service_type == 'General Cleaning':		
		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_general_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_general_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
	elif service_type == 'Upholstery Cleaning':
		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_upholstery_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_upholstery_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
	elif service_type == 'Kitchen Cleaning':
		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_kitchen_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_kitchen_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
	elif service_type == 'Carpet Cleaning':
		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_carpet_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_carpet_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
	elif service_type == 'Sterilization':
		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_sterilization_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_sterilization_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
	elif service_type == 'Deep Cleaning':
		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_deep_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_deep_skill=True).filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
	else:
		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_time__gte=start_at)&Q(start_time__lte=end_at))|Q(Q(end_time__gte=start_at)&Q(end_time__lte=end_at))|Q(Q(start_time__lte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__gte=end_at))|Q(Q(start_time__gte=start_at)&Q(end_time__gte=start_at)&Q(start_time__lte=end_at)&Q(end_time__lte=end_at)))).extra({'start_at' : "date(start_at)"}).values('start_at').annotate(created_count=Count('id'))

	cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE')
	cleaning_active_cleaners     = active_cleaners1.filter(member__user_type='CLEANER')

	followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE')
	followup_active_cleaners     = active_cleaners2.filter(member__user_type='CLEANER')

	#merging
	team_leaders_scheduled_dates      = []
	team_members_scheduled_dates      = []

	for active_team_leaders in cleaning_active_team_leaders:
		team_leaders_scheduled_dates.append(active_team_leaders)
	for active_team_leaders in followup_active_team_leaders:
		team_leaders_scheduled_dates.append(active_team_leaders)

	for active_team_member in cleaning_active_cleaners:
		team_members_scheduled_dates.append(active_team_member)
	for active_team_member in followup_active_cleaners:
		team_members_scheduled_dates.append(active_team_member)

	#busy slotes and count
	team_leaders_busy = {}
	team_members_busy = {}

	for team_leader in team_leaders_scheduled_dates:
		try:
			index = datetime.strftime(team_leader['start_at'],'X%d-X%m-%Y').replace('X0','X').replace('X','')
			print("actual leader",index)
		except:
			index = datetime.strftime(datetime.strptime(team_leader['start_at'],'%Y-%m-%d'),'X%d-X%m-%Y').replace('X0','X').replace('X','')
			print("except leader",index)
		if index in team_leaders_busy:
			team_leaders_busy[index] += team_leader['created_count']
		else:	
			team_leaders_busy[index] = team_leader['created_count']

	for team_member in team_members_scheduled_dates:
		try:
			index = datetime.strftime(team_member['start_at'],'X%d-X%m-%Y').replace('X0','X').replace('X','')
			print("actual member",index)
		except:
			index = datetime.strftime(datetime.strptime(team_member['start_at'],'%Y-%m-%d'),'X%d-X%m-%Y').replace('X0','X').replace('X','')
			print("except member",index)

		if index in team_members_busy:
			team_members_busy[index] +=  team_member['created_count'] 
		else: 
			team_members_busy[index]   = team_member['created_count']


	#remove available dates
	if service_type == 'General Cleaning':
		total_cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER',is_general_skill=True).count()
		total_leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',is_general_skill=True).count()		
	elif service_type == 'Upholstery Cleaning':
		total_cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER',is_upholstery_skill=True).count()
		total_leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',is_upholstery_skill=True).count()
	elif service_type == 'Kitchen Cleaning':
		total_cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER',is_kitchen_skill=True).count()
		total_leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',is_kitchen_skill=True).count()
	elif service_type == 'Carpet Cleaning':
		total_cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER',is_carpet_skill=True).count()
		total_leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',is_carpet_skill=True).count()
	elif service_type == 'Sterilization':
		total_cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER',is_sterilization_skill=True).count()
		total_leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',is_sterilization_skill=True).count()
	elif service_type == 'Deep Cleaning':
		total_cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER',is_deep_skill=True).count()
		total_leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',is_deep_skill=True).count()
	else:
		total_cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER').count()
		total_leaders  = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').count()

	for k, v in list(team_leaders_busy.items()):
		if v < total_leaders:
			del team_leaders_busy[k]

	for k, v in list(team_members_busy.items()):
		if int(no_of_cleaners) <= (total_cleaners-v):
			del team_members_busy[k]

	data['leaders_busy_dates']  = team_leaders_busy
	data['cleaners_busy_dates'] = team_members_busy
	print(data)
	return JsonResponse(data)

# Create your views here.
class AgentHome(IsAgent,View):
	def get(self,request):

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
		lastmonth_average_feedback	  = feedbacks.filter(response_date__gte=count_today_end-timedelta(60),response_date__lte=count_today_end-timedelta(30)).aggregate(Avg('rating'))['rating__avg']	
		
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
			selected_date = request.GET.get('evaluation_calendar_date')
		except:
			evaluation_details 		  = None


		#Order and Followup Schedules for date confirmation
		# confirm_to_date         = (timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)).replace(tzinfo=None)

		# follow_up_schedules	  = FollowUpScheduler.objects.filter(is_active=True,start_at__lt=confirm_to_date+timedelta(4)).exclude(Q(Q(status='CONFIRMED')|Q(status='CANCELLED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		# for followupschedule in follow_up_schedules:
		# 	followupschedule.days_left_coming = (followupschedule.start_at-timezone.now()).days 

		
		# order_schedules_by_address = Order.objects.select_related('evaluation__call_attender').filter(evaluation__quatation_status='APPROVED').filter(Q( Q(Q(payment_status='COMPLETED')|~Q(preamount_paid = 0)) | Q(evaluation__payment_method='POSTPAID') )).prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED').select_related('evaluator').prefetch_related(Prefetch('order_scheduler_evaluationdetails',queryset=OrderScheduler.objects.filter(is_active=True,status='WAITING').order_by('start_at'),to_attr="orderschedules")),to_attr='evaluationdetails'))		
		# for order_details in order_schedules_by_address:
		# 	if order_details.evaluation.evaluationdetails:
		# 		for evaluation_detail in order_details.evaluation.evaluationdetails:
		# 			if evaluation_detail.orderschedules:
		# 				count = 0
		# 				for schedule in evaluation_detail.orderschedules:
		# 					if count == 0:
		# 						evaluation_detail.days_left_coming = (schedule.start_at-timezone.now()).days
		# 					count += 1 	

		#cleaning schedule & followup schedule for cleaning calendar
		cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')

		try:
			schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			schedule_date = timezone.now().replace(tzinfo=None)

		schedule_date_start = schedule_date.replace(hour=0,minute=0,second=0,microsecond=0)
		schedule_date_end   = schedule_date_start+timedelta(1)

		try:
			calendar_order_schedules 	= OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end)))).order_by('start_at').select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') )) 
		except:
			calendar_order_schedules 	= None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end)))).order_by('start_at').select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			calendar_followup_schedules = None

		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') ))
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end)))).select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			sp_calendar_followup_schedules = None

		try:
			spp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') ))
		except:
			spp_calendar_order_schedules = None

		try:
			spp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start)))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			spp_calendar_followup_schedules = None

		#for edit popup
		try:
			workers = UserProfile.objects.filter(is_active=True)
		except:
			workers = None

		#for popup
		customer_addresses = Address.objects.filter(is_active=True,currently_active=True).select_related('area')


		#followup confirmation for special user
		followup_to_be_closed = FollowUp.objects.filter(is_active=True,status='FOLLOWUP_IN_PROGRESS',).select_related('investigation__order_schedule__customer_address__area','investigation__order_schedule__order_scheduler_book__service_type','investigation__investigator','investigation__order__evaluation__customer')
				
		return render(request,'agent/home/home.html',{'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'month_average_feedback':month_average_feedback,'lastmonth_average_feedback':lastmonth_average_feedback,'cleaning_job':cleaning_job,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'follow_up_job':follow_up_job,'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'spp_calendar_order_schedules':spp_calendar_order_schedules,'spp_calendar_followup_schedules':spp_calendar_followup_schedules,'schedule_date':schedule_date,'workers':workers,"customer_addresses":customer_addresses,"followup_to_be_closed":followup_to_be_closed,})


	def post(self,request):
		action_mode = request.POST.get('action_type')

		# if action_mode =='confirm_followupchedule':
		# 	followupscheduler_id = request.POST.get('followupscheduler')
		# 	followup_scheduler   = FollowUpScheduler.objects.get(id=followupscheduler_id)
		# 	confirm_status       = request.POST.get('confirm')

		# 	confirm_date 	 = request.POST.get('followup_schedule_date')
		# 	confirm_time 	 = request.POST.get('followup_schedule_time')
		# 	start_at         = datetime.strptime(confirm_date+' '+confirm_time,'%d-%m-%Y %I:%M %p')
		# 	end_at           = start_at + timedelta(hours=followup_scheduler.follow_up.cleaning_hours)

		# 	if confirm_status:
		# 		FollowUpScheduler.objects.filter(id=followupscheduler_id).update(status='CONFIRMED',start_at=start_at,end_at=end_at)
		# 		messages.success(request,"Followup Cleaning Date Succesfully Confirmed")
		# 	else:
		# 		FollowUpScheduler.objects.filter(id=followupscheduler_id).update(start_at=start_at,end_at=end_at)
		# 		messages.success(request,"Followup Cleaning Date Not Confirmed")

		# 	evaluation_calendar_date	= request.GET.get('evaluation_calendar_date') or ''
		# 	cleaning_calendar_date	    = request.GET.get('cleaning_calendar_date') or ''

		# 	return redirect('/agent/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&evaluation_calendar_date='+evaluation_calendar_date)	

		# elif action_mode =='confirm_orderschedules':
		# 	total_schedules = int(request.POST.get('total_schedules_to_confirm'))
		# 	for i in range(total_schedules):
		# 		schedule_id    = request.POST.get('order_schedules_id'+str(i))
				
		# 		order_scheduler= OrderScheduler.objects.select_related('order_scheduler_book').get(id=schedule_id)
		# 		tendative_date = request.POST.get('order_schedule_date'+str(i))
		# 		tendative_time = request.POST.get('order_schedule_time'+str(i))
		# 		start_at         = datetime.strptime(tendative_date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
		# 		end_at           = start_at + timedelta(hours=order_scheduler.order_scheduler_book.cleaning_hours)

		# 		confirm_status = request.POST.get('confirm'+str(i))

		# 		if confirm_status:
		# 			OrderScheduler.objects.filter(id=schedule_id).update(status='CONFIRMED',start_at=start_at,end_at=end_at)
		# 		else:
		# 			OrderScheduler.objects.filter(id=schedule_id).update(start_at=start_at,end_at=end_at)
			
		# 	messages.success(request,"Cleaning Date(s) Confirmed/Changed Successfully")

		if action_mode == 'followup_close':
			followup = FollowUp.objects.filter(id=request.POST.get('followup')).update(status='FOLLOWUP_CLOSED')
			messages.success(request,"Followup Closed Successfully")

		elif action_mode == 'edit_evaluation':
			evaluation_detail_id 			  = request.POST.get('evaluation_id')

			new_proposed_date                 = request.POST.get('proposed_date')
			new_proposed_time                 = request.POST.get('proposed_time')
			converted_proposed_datetime       = datetime.strptime(new_proposed_date+' '+new_proposed_time,'%d-%m-%Y %I:%M %p')

			evaluator_id                      = request.POST.get('evaluator')
			attender_note                    = request.POST.get('attender_note')

			evaluation = EvaluationDetails.objects.filter(id=evaluation_detail_id).first()
			current_date=evaluation.proposed_time

			language = evaluation.address.customer.sms_preference
			contact_platform = evaluation.address.customer.is_sms

			print(contact_platform,"plo")

			gender = evaluation.address.customer.gender
			if gender == 'MALE':
				title = 'Mr.'
			else:
				title = 'Ms.'
			address = evaluation.address


			#update evaluation time
			EvaluationDetails.objects.filter(id=evaluation_detail_id).update(proposed_time=converted_proposed_datetime,evaluator_id=evaluator_id,attender_note=attender_note)	
			evaluator = EvaluationDetails.objects.get(id=evaluation_detail_id)
			messages.success(request,"Evaluation Edited Succesfully")

			if address.floor == None and address.avenue == None:
				address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			elif address.floor == None:
				address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
			
			elif address.avenue == None:
				address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			else:
				address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

			separator = ", "

			if converted_proposed_datetime.date() != current_date.date() and contact_platform == True:
				
				url = "https://smsapi.future-club.com/fccsms.aspx"

				if language == 'ENGLISH':

					message = "Dear Customer, We have changed the date of your Evaluation Appointment as per your request. "+ title +" "+evaluator.evaluator.name+" will be visiting you on "+str(converted_proposed_datetime)+" at "+ separator.join(address_list) +". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
				
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.address.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

				else:
					message = "عزيزي العميل، لقد قمنا بتغيير تاريخ موعد التقييم الخاص بك حسب طلبك.  "+ title +" "+evaluator.evaluator.name+" سيقوم بالزيارة في "+str(converted_proposed_datetime)+" في "+separator.join(address_list)+" لأي استفسارات يمكنكم التواصل معنا على  9651882707+ . شكراً لاختياركم بليتش لخدمات التنظيف"
					
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.address.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)

				print(response.text,"respo")

			else:
				pass

			evaluation_calendar_date	= request.GET.get('evaluation_calendar_date') or ''
			cleaning_calendar_date	    = request.GET.get('cleaning_calendar_date') or ''

			return redirect('/agent/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&evaluation_calendar_date='+evaluation_calendar_date)

		elif action_mode == 'edit_cleaning':
			schedule_id                       = request.POST.get('cleaning_id')

			cleaning_date 	= request.POST.get('cleaning_date')
			cleaning_time   = request.POST.get('cleaning_time')
			cleaning_hours 	= float(request.POST.get('cleaning_hours'))

			start_at         = datetime.strptime(cleaning_date+' '+cleaning_time,'%d-%m-%Y %I:%M %p')
			end_at           = start_at + timedelta(hours=cleaning_hours)


			#update schedule
			order_scheduler  = OrderScheduler.objects.select_related('order_scheduler_book').get(id=schedule_id)
			order_scheduler.start_at 							= start_at
			order_scheduler.end_at   							= end_at
			order_scheduler.order_scheduler_book.cleaning_hours = cleaning_hours

			order_scheduler.save()
			order_scheduler.order_scheduler_book.save()

			#update cleaning team
			try:
				cleaning_team_update = CleaningTeam.objects.filter(order_scheduler=order_scheduler).update(start_at=start_at,end_at=end_at,)
				cleaning_team = CleaningTeam.objects.filter(order_scheduler=order_scheduler).first()
			except:
				cleaning_team_update = None

			#update cleaning team member
			try:
				cleaner_update 		 =	CleaningTeamMember.objects.filter(team__order_scheduler=order_scheduler).update(start_at=start_at,end_at=end_at,)	
			except:
				cleaner_update       =	None

			orderschedule = OrderScheduler.objects.filter(id=schedule_id).first()

			address = orderschedule.evaluation_details.address

			language = orderschedule.evaluation_details.evaluation.customer.sms_preference

			contact_platform = orderschedule.evaluation_details.evaluation.customer.is_sms

			messages.success(request,"Cleaning Edited Succesfully")

			if address.floor == None and address.avenue == None:
				address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			elif address.floor == None:
				address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
			
			elif address.avenue == None:
				address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			else:
				address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

			separator = ", "

			if cleaning_team and start_at.date() != cleaning_team.start_at.date() and contact_platform == True:

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if language == 'ENGLISH':

					message = "Dear Customer, We have changed the date of your Cleaning Appointment against order number "+ orderschedule.order.order_no +" as per your request. Bleach’s Cleaning Team will be visiting you on "+ str(cleaning_date)+" "+ str(cleaning_time) +" at "+separator.join(address_list)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+orderschedule.order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

				else:
					message = "عزيزي العميل، لقد قمنا بتغيير تاريخ موعد التنظيف الخاص بك مقابل رقم الطلب "+ orderschedule.order.order_no +" وذلك وفق طلبكم.  سيقوم طاقم العمل بزيارتكم في "+ str(cleaning_date)+" "+ str(cleaning_time) +" في "+separator.join(address_list)+". لأي استفسارات يمكنكم التواصل معنا على . 9651882707+  شكراً لاختياركم بليتش لخدمات التنظيف"
				
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+orderschedule.order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)

				print(message,response,"res")

			else:
				pass

			evaluation_calendar_date	= request.GET.get('evaluation_calendar_date') or ''
			cleaning_calendar_date	    = request.GET.get('cleaning_calendar_date') or ''

			return redirect('/agent/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&evaluation_calendar_date='+evaluation_calendar_date)

		elif action_mode == 'edit_followup':
			schedule_id                       = request.POST.get('followup_id')

			cleaning_date 	= request.POST.get('cleaning_date')
			cleaning_time   = request.POST.get('cleaning_time')
			cleaning_hours 	= float(request.POST.get('cleaning_hours'))

			start_at         = datetime.strptime(cleaning_date+' '+cleaning_time,'%d-%m-%Y %I:%M %p')
			end_at           = start_at + timedelta(hours=cleaning_hours)

			#update schedule
			followup_scheduler  = FollowUpScheduler.objects.select_related('follow_up').get(id=schedule_id)
			followup_scheduler.start_at 							= start_at
			followup_scheduler.end_at   							= end_at
			followup_scheduler.follow_up.cleaning_hours 			= cleaning_hours

			followup_scheduler.save()
			followup_scheduler.follow_up.save()

			#update followup team
			try:
				followup_team = FollowUpTeam.objects.filter(followup_scheduler=followup_scheduler).update(start_at=start_at,end_at=end_at)
			except:
				followup_team = None

			#update followup team members
			try:
				followup_team_members = FollowUpTeamMember.objects.filter(is_active=True,team__followup_scheduler=followup_scheduler,member__user_type='CLEANER').update(start_at=start_at,end_at=end_at)
			except:
				followup_team_members = None

			messages.success(request,"Followup Cleaning Edited Succesfully")

			evaluation_calendar_date	= request.GET.get('evaluation_calendar_date') or ''
			cleaning_calendar_date	    = request.GET.get('cleaning_calendar_date') or ''

			return redirect('/agent/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&evaluation_calendar_date='+evaluation_calendar_date)

		elif action_mode == 'delete_evaluation':
			evaluation_id = request.POST.get('delete_evaluation_id')

			#Delete Evaluation Details
			evaluation = EvaluationDetails.objects.filter(id=evaluation_id).first()
			proposed_datetime=evaluation.proposed_time
			language = evaluation.address.customer.sms_preference

			# gender = evaluation.address.customer.gender
			# if gender == 'MALE':
			# 	title = 'Mr.'
			# else:
			# 	title = 'Ms.'
			address = evaluation.address
			mobile = evaluation.evaluation.customer.mobile_number
			EvaluationDetails.objects.filter(id=evaluation_id).delete()

			print(proposed_datetime,address.governorate,"prop")
			
			messages.success(request,"Evaluation Deleted Succesfully")

			if address.floor == None and address.avenue == None:
				address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			elif address.floor == None:
				address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
			
			elif address.avenue == None:
				address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			else:
				address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

			separator = ", "

			if evaluation.address.customer.is_sms == True:

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if language == 'ENGLISH':

					message = "Dear Customer, We have cancelled your Evaluation Appointment booked for "+str(proposed_datetime)+" at "+separator.join(address_list)+" as per your request.For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
				
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"L"}

				else:
					message = "عزيزنا العميل تم إلغاء موعد المعاينة الخاص بك المحجوز ب "+str(proposed_datetime)+" في "+separator.join(address_list)+" وذلك وفق طلب حضراتكم. لأي استفسارات يمكنكم التواصل معنا على 9651882707+ .  شكراً لاختياركم بليتش لخدمات التنظيف"
				
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"A"}

				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)
			else:
				pass

			evaluation_calendar_date	= request.GET.get('evaluation_calendar_date') or ''
			cleaning_calendar_date	    = request.GET.get('cleaning_calendar_date') or ''

			return redirect('/agent/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&evaluation_calendar_date='+evaluation_calendar_date)

		elif action_mode == 'delete_cleaning':
			cleaning_id = request.POST.get('delete_cleaning_id')

			orderschedule = OrderScheduler.objects.filter(id=cleaning_id).first()

			order_no = orderschedule.order.order_no

			mobile = orderschedule.order.evaluation.customer.mobile_number

			language = orderschedule.evaluation_details.evaluation.customer.sms_preference

			contact_sms = orderschedule.evaluation_details.evaluation.customer.is_sms

			#Delete Cleaning Schedule
			OrderScheduler.objects.filter(id=cleaning_id).delete()

			messages.success(request,"Cleaning Deleted Succesfully")

			if contact_sms == True:

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if language == 'ENGLISH':

					message = "Dear Customer, We have cancelled your Cleaning Appointment against the order number "+ order_no +" as per your request. For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"
				
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"L"}

				else:
					message = "ل تم إلغاء موعد التنظیف الخاص بكم بنجاح للطلب رقم "+ order_no +" وذلك وفق طلبكم. لأي استفسارات یمكنكم التواصل معنا على 9651882707+ لاختیاركم بلیتش لخدماتشكرا. التنظیف"
				
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+mobile+"","M":message,"IID":"1468","L":"A"}

				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)
			
			else:

				pass

			evaluation_calendar_date	= request.GET.get('evaluation_calendar_date') or ''
			cleaning_calendar_date	    = request.GET.get('cleaning_calendar_date') or ''

			return redirect('/agent/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&evaluation_calendar_date='+evaluation_calendar_date)

		elif action_mode == 'delete_followup':
			followup_id = request.POST.get('delete_followup_id')
			#Delete Followup Schedule
			FollowUpScheduler.objects.filter(id=followup_id).delete()

			messages.success(request,"Followup Deleted Succesfully")

			evaluation_calendar_date	= request.GET.get('evaluation_calendar_date') or ''
			cleaning_calendar_date	    = request.GET.get('cleaning_calendar_date') or ''

			return redirect('/agent/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&evaluation_calendar_date='+evaluation_calendar_date)

		return redirect('agent:agentdash-board')


class ResourceManagement(IsAgent,View):
	def get(self,request):

		try:
			staffs = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER')))
		except:
			staffs = None

		#cleaning schedule & followup schedule for cleaning calendar
		workers_calendar_date	= request.GET.get('workers_calendar_date')
		search                  = request.GET.get('search')

		try:
			workers_date = datetime.strptime(workers_calendar_date,'%d-%m-%Y')
		except:
			workers_date = timezone.now().replace(tzinfo=None)

		workers_date_start = workers_date.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		workers_date_end   = workers_date_start+timedelta(1)

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
			total_active_workers = CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__lte=workers_date_start)&Q(end_at__gte=workers_date_start)) )).values_list('member',flat=True).distinct().union(FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__lte=timezone.now().replace(tzinfo=None))&Q(end_at__gte=timezone.now().replace(tzinfo=None)))) ).values_list('member',flat=True)).distinct().count()			
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


		today_cleaning_active_teams  = cleaning_teams.filter(Q(Q(Q(start_at__gte=workers_date_start)&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_start)&Q(end_at__lt=workers_date_end))))
		today_followup_active_teams  = follow_up_teams.filter(Q(Q(Q(start_at__gte=workers_date_start)&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_start)&Q(end_at__lt=workers_date_end))))
		week_cleaning_active_teams   = cleaning_teams.filter(Q( Q(Q(start_at__gte=workers_date_end-timedelta(7))&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_end-timedelta(7))&Q(end_at__lt=workers_date_end)) ))
		week_followup_active_teams   = follow_up_teams.filter(Q( Q(Q(start_at__gte=workers_date_end-timedelta(7))&Q(start_at__lte=workers_date_end))|Q(Q(end_at__gte=workers_date_end-timedelta(7))&Q(end_at__lt=workers_date_end)) ))

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

		if search:
			try:
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))&Q(name__icontains=search))
			except:
				workers =  None
		else:
			try:
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER')))
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
			case1 = Q(user_type=fil_staff)
			filters.append(case1)

		if fil_staff:
			filters         = functools.reduce(operator.and_,filters)
			workers_details = workers_details.filter(filters)

		return render(request,'agent/resource/resource_management.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,"staffs":staffs,"fil_staff":fil_staff,"fil_minhours":fil_minhours,"fil_maxhours":fil_maxhours,"staff_type":fil_staff})


class OrderDetails(IsAgent,View):
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

		fil_status              = request.GET.get('status')
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
					case1 = Q(Q(approved_not_paid_count__gte=1)&~Q(payment_method='SUBSCRIPTION'))
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

		return render(request,'agent/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy})


class FeedbackDetails(IsAgent,View):
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
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True).filter(Q(Q(evaluation__evaluation_id__icontains=search)|Q(evaluation__customer__name__icontains=search))).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter( Q(Q(cleaning_count=F('completed_cleaning_count'))&Q(followup_count=F('completed_followup_count')))|Q(is_feedback_marked=True))		
			except:
				order_wise_feedbacks = None		
		else:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(Q(Q(cleaning_count=F('completed_cleaning_count'))&Q(followup_count=F('completed_followup_count')))|Q(is_feedback_marked=True))						
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
		
		#filters
		filters=[]
		if fil_minimumstarring:
			if fil_minimumstarring == 'RATED':
				case1 = Q(is_feedback_marked=True)
			elif fil_minimumstarring == 'NOT_RATED':
				case1 = Q(is_feedback_marked=False)
			else:
				case1 = Q(Q(avg_starring__gte=fil_minimumstarring)&Q(avg_starring__lt=float(fil_minimumstarring)+1))
			filters.append(case1)

		if fil_minimumstarring :
			filters              = functools.reduce(operator.and_,filters)
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

		return render(request,'agent/feedback/feedbacks.html',{"total_feedbacks":total_feedbacks,"order_wise_feedbacks":order_wise_feedbacks,"full_order_wise_feedbacks":full_order_wise_feedbacks,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_minimumstarring":fil_minimumstarring,"fil_service_type":fil_service_type,})

class FeedbackAdvanced(IsAgent,View):
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
			feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True,evaluation__customer_id=client_id).prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField())).annotate(average_rating=Avg('feed_backs_order__rating'))
		except:
			feedbacks = None

		#total_feedback_rating
		try:
			average_feedback  = feedbacks.filter(id=order_id).aggregate(Sum('average_rating'))['average_rating__sum']
		except:
			average_feedback = 0.0

		#other feedbacks
		try:
			other_feedbacks = feedbacks.exclude(id=order_id).filter(is_feedback_marked=True)
		except:	
			other_feedbacks = None

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=client_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		return render(request,'agent/feedback/feedback-page.html',{"order":order,"client_details":client_details,"feedback_details":feedback_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"other_feedbacks":other_feedbacks,"average_feedback":average_feedback,})


class TicketDetails(IsAgent,View):
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

		return render(request,"agent/ticket/tickets.html",{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})


class TicketAdvanced(IsAgent,View):
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

		return render(request,'agent/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})




class ClientDetails(IsAgent,View):
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

		return render(request,"agent/client/clients.html",{"client_details":client_details,"search_query":search,"new_clients_count":new_clients_count,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_customertype":fil_customertype,"fil_status":fil_status})


class ClientOrders(IsAgent,View):
	def get(self,request,client_id):

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'))

		#COUNT
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()

		return render(request,"agent/client/client-page.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,})

class ClientOrderDetails(IsAgent,View):
	def get(self,request,order_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True),to_attr='paybackdiscounts'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True),to_attr='buybackpromocodegift'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)


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


		return render(request,"agent/client/order-page.html",{"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"average_feedback":average_feedback,})

class NewEnquiry(IsAgent,View):
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

		return render(request,'agent/enquiry/newenquiry.html',{'enquiry_form':enquiry_form,'address_formset':self.address_formset_define(),'customer_info':customer_info,'governorates':governorates,'locations':locations})

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

			if enquiry_form_save.gender == 'MALE':
				prefix = 'Mr. '
				prefix_exists = customer_name.startswith(prefix)

				if prefix_exists == False :
					enquiry_form_save.name = prefix+customer_name
			elif enquiry_form_save.gender == 'FEMALE':
				prefix = 'Ms. '
				prefix_exists = customer_name.startswith(prefix)

				if prefix_exists == False :
					enquiry_form_save.name = prefix+customer_name
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
			return redirect('agent:agent-makeevaluation',enquiry_form_save.id)
		elif redirection == 'quatation':
			return redirect('agent:agent-makequatation',enquiry_form_save.id)
		else:
			return redirect('agent:existingenquiry',enquiry_form_save.id)


class ExistingEnquiry(IsAgent,View):

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

		return render(request,'agent/enquiry/existingenquiry.html',{'enquiry_user':enquiry_user,'enquiry_form':enquiry_form,"address_form":address_form,'enquiryid':enquiry_id,'addresses':addresses,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"governorates":governorates,'locations':locations})

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

				if enquiry_form_save.gender == 'MALE':
					prefix = 'Mr. '
					prefix_exists = customer_name.startswith(prefix)

					if prefix_exists == False :
						enquiry_form_save.name = prefix+customer_name
				elif enquiry_form_save.gender == 'FEMALE':
					prefix = 'Ms. '
					prefix_exists = customer_name.startswith(prefix)

					if prefix_exists == False :
						enquiry_form_save.name = prefix+customer_name
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

				return render(request,'agent/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,'governorates':governorates})
		
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

				return render(request,'agent/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,})

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
		
		return redirect('agent:agent-existingenquiry',enquiry_id)


class MakeEvaluation(IsAgent,View):
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

		return redirect('agent:agent-assignevaluator',enquiry_id,new_evaluation.id)


class AssignEvaluator(IsAgent,View):
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

		return render(request,'agent/enquiry/assign_evaluator.html',{'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'enquiryid':enquiry_id,'evaluation_id':evaluation_id,'evaluation_form':evaluation_form,"active_addresses":active_addresses,"evaluators":evaluators,})

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

					print(response.text,"respo")
					print(str(evaluation_form_save.proposed_time))
					print(message, evaluation_form_save.evaluation.customer.mobile_number,"mobile")
				else:
					pass

			else:
				messages.error(request,get_error(evaluation_form))

		selected_date = request.GET.get('evaluation_calendar_date') or ''

		return redirect('/agent/assignevaluator/'+enquiry_id+'/'+evaluation_id+'?evaluation_calendar_date='+selected_date)
		


class MakeQuatationBase(IsAgent,View):
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

		return redirect('agent:agent-makequatation1',enquiry_id,evaluation.id)

class MakeQuatationPhase1(IsAgent,View):

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

		return render(request,'agent/enquiry/phase1quatation.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})

	def post(self,request,enquiry_id,evaluation_id):

		payment_method 			= request.POST.get('payment_method')
		before_cleaning_amount	= float(request.POST.get('before_cleaning_amount')or 0)
		after_cleaning_amount	= float(request.POST.get('after_cleaning_amount')or 0)

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,quatation_status='PENDING',before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)

	
		#sms integration
		evaluation        = Evaluation.objects.filter(id=evaluation_id,is_active=True).first()
		evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
		evaluationbook    = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).first()
		language = evaluation.customer.sms_preference
		address = evaluationdetails.address

		messages.success(request,"Quotation Submitted Succesfully")

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

			print(message,response.text,"respondd")
		
		else:
			pass
		
		return redirect('agent:agentdash-board')


class MakeQuatationPhase2(IsAgent,View):
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

		return render(request,'agent/enquiry/phase2quatation.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,})

	def post(self,request,evaluation_detail_id):

		service_formset       = self.service_formset_define(request.POST)
		evaluation_details 	  = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=evaluation_detail_id)

		if service_formset.is_valid() :
			form_count = 0
			#create order roughly
			new_order 				= Order.objects.get_or_create(evaluation=evaluation_details.evaluation,order_no=evaluation_details.evaluation.evaluation_id)

			order_schedule_array = []
			#Save Service Form
			for service_form in service_formset:

				if service_form.is_valid():
					service_form_save 					    = service_form.save(commit=False)
					service_form_save.evaluation_details_id = evaluation_detail_id
					service_form_save.save()


					#To Save Media
					medias = request.FILES.getlist('form-'+str(form_count)+'-media')
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
						tendative_date  = request.POST.get('form-'+str(form_count)+'-tendative_date')

						start_date_time = datetime.strptime(tendative_date+' '+start_time,'%d-%m-%Y %I:%M %p')
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

						
						try:
							section_name_arabic = Translator().translate(section_name,src='en', dest='ar').text
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

			return render(request,'agent/enquiry/phase2quatation.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'area_types':area_types,'service_types':service_types,})

		return redirect('agent:agent-makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)
	
class MakeQuatationPhase1Edit(IsAgent,View):	

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

		return render(request,'agent/enquiry/phase1quatationedit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})	

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

		return redirect('agent:agentdash-board')




class MakeQuatationPhase2Edit(IsAgent,View):
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

		return render(request,'agent/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

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
								print(date)
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
								section_name_arabic = Translator().translate(section_name,src='en', dest='ar').text
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

			return render(request,'agent/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

		return redirect('agent:agent-makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)

class MakeQuatationDuplicate(IsAgent,View):
	
	def get(self,request,evaluation_id):
		

		duplicate_evaluation = Evaluation.objects.get(id=evaluation_id)
		
		duplicate_evaluation_details = EvaluationDetails.objects.filter(is_active=True,evaluation=duplicate_evaluation).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='booksections')),to_attr='evaluationbooks'))
		

		#duplicate the order
		tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

		current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
		
		if current_blc_starting == int(str(tracking_no)[:6]):
			new_tracking_no = int(tracking_no)+1
			evaluation_no   = 'BLC'+str(new_tracking_no)
		else:
			evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
			tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')
		
		new_evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no,customer=duplicate_evaluation.customer,call_attender=request.user,quatation_expiry_date=timezone.now()+timedelta(7),estimated_cost=duplicate_evaluation.estimated_cost,discount=duplicate_evaluation.discount,total_cost=duplicate_evaluation.total_cost)
		new_order      = Order.objects.get_or_create(evaluation=new_evaluation,order_no=new_evaluation.evaluation_id)
		
		if duplicate_evaluation_details:

			#new evaluation details
			for duplicate_evaluation in duplicate_evaluation_details:
				new_duplicate_evaluation_details = EvaluationDetails.objects.create(evaluation=new_evaluation,address=duplicate_evaluation.address,estimated_cost=duplicate_evaluation.estimated_cost,discount=duplicate_evaluation.discount,total_cost=duplicate_evaluation.total_cost,status=duplicate_evaluation.status)
				
				if duplicate_evaluation.evaluationbooks:
					#new book
					for duplicate_book in duplicate_evaluation.evaluationbooks:
						new_duplicate_book = EvaluationBook.objects.create(evaluation_details=new_duplicate_evaluation_details,cleaning_policy=duplicate_book.cleaning_policy,service_type=duplicate_book.service_type,area_type=duplicate_book.area_type,cleaning_method=duplicate_book.cleaning_method,location_type=duplicate_book.location_type,number_of_cleaners=duplicate_book.number_of_cleaners,estimated_cost=duplicate_book.estimated_cost,discount=duplicate_book.discount,total_cost=duplicate_book.total_cost,cleaning_hours=duplicate_book.cleaning_hours,evaluator_note=duplicate_book.evaluator_note)

						if duplicate_book.booksections:
							#new booksection
							for duplicate_book_section in duplicate_book.booksections:
								new_duplicate_section = EvaluationBookSection.objects.create(evaluation_book=new_duplicate_book,section_name=duplicate_book_section.section_name,section_name_arabic=duplicate_book_section.section_name_arabic,category=duplicate_book_section.category,dirt_level=duplicate_book_section.dirt_level,quantity=duplicate_book_section.quantity,size=duplicate_book_section.size,unit=duplicate_book_section.unit,age=duplicate_book_section.age,floor=duplicate_book_section.floor,apartment=duplicate_book_section.apartment,room=duplicate_book_section.room,wall_type=duplicate_book_section.wall_type,ceiling_type=duplicate_book_section.ceiling_type,floor_type=duplicate_book_section.floor_type,material=duplicate_book_section.material,colour=duplicate_book_section.colour,cause_of_stain=duplicate_book_section.cause_of_stain,section_cost=duplicate_book_section.section_cost)
						
							
								if duplicate_book_section.sectionkeynotes:
									#new keynotes
									for duplicate_keynote in duplicate_book_section.sectionkeynotes:	
										new_duplicate_keynote = EvaluationSectionKeynote.objects.create(evaluation_section=new_duplicate_section,sub_area=duplicate_keynote.sub_area,quantity=duplicate_keynote.quantity,)

		messages.success(request,"Duplicate Order Created Succesfully")

		return redirect('agent:agent-makequatation1duplicateedit',new_evaluation.customer.id,new_evaluation.id,)

class MakeQuatationPhase1DuplicateEdit(IsAgent,View):	

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
		evaluation_details_count           = evaluation_details.count()
		evaluation_details_completed_count = evaluation_details.filter(status='EVALUATED').count()

		if evaluation_details_count==evaluation_details_completed_count:
			allow_submit = True
		else:
			allow_submit = False	

		#allow submit only after date addition
		evaluation_books           = EvaluationBook.objects.select_related('evaluation_details__evaluation').filter(evaluation_details__evaluation=evaluation).prefetch_related('order_scheduler_book_details').annotate(individual_schedules=Count('order_scheduler_book_details'))
		scheduled_evaluation_books = evaluation_books.filter(individual_schedules__gt=0)

		if evaluation_books.count() != scheduled_evaluation_books.count():
			allow_submit = False

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=enquiry_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()				

		return render(request,'agent/enquiry/phase1quatationduplicateedit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})	

	def post(self,request,enquiry_id,evaluation_id):
		
		payment_method 			= request.POST.get('payment_method')
		before_cleaning_amount	= float(request.POST.get('before_cleaning_amount')or 0)
		after_cleaning_amount	= float(request.POST.get('after_cleaning_amount')or 0)

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,quatation_status='PENDING',before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)

		#sms integration
		evaluation = Evaluation.objects.prefetch_related(Prefetch('evaluation_details',EvaluationDetails.objects.filter(is_active=True).select_related('address'),to_attr='evaluation_address')).filter(id=evaluation_id,is_active=True).get(id=evaluation_id,is_active=True)
		evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
		evaluationbook = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).first()
		
		messages.success(request,"Quotation Edited Succesfully")

		#address check for floor,avenue None
		if evaluationdetails.address.floor == None and evaluationdetails.address.avenue == None:
			address_list = [evaluationdetails.address.apartment, evaluationdetails.address.street, evaluationdetails.address.building, evaluationdetails.address.block, evaluationdetails.address.area.name, evaluationdetails.address.governorate.name]
		
		elif evaluationdetails.address.floor == None:
			address_list = [evaluationdetails.address.apartment, evaluationdetails.address.street, evaluationdetails.address.building, evaluationdetails.address.avenue, evaluationdetails.address.block, evaluationdetails.address.area.name, evaluationdetails.address.governorate.name]
		
		elif evaluationdetails.address.avenue == None:
			address_list = [evaluationdetails.address.apartment, evaluationdetails.address.floor, evaluationdetails.address.street, evaluationdetails.address.building, evaluationdetails.address.block, evaluationdetails.address.area.name, evaluationdetails.address.governorate.name]
		
		else:
			address_list = [evaluationdetails.address.apartment, evaluationdetails.address.floor, evaluationdetails.address.street, evaluationdetails.address.building, evaluationdetails.address.avenue, evaluationdetails.address.block, evaluationdetails.address.area.name, evaluationdetails.address.governorate.name]

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

		return redirect('agent:agentdash-board')




class MakeQuatationPhase2DuplicateEdit(IsAgent,View):
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

		return render(request,'agent/enquiry/phase2quatationduplicateedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

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
								print(date)
								start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
								end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))
								order_schedule_array.append(OrderScheduler(order=old_order,status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=old_book))


							updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total,status='EVALUATED')
							updated_evaluation         = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total)
							update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')+total,remining_amount=F('remining_amount')+total)							
						else:
							tendative_date  = request.POST.get('form-'+str(form_count)+'-tendative_date')

							start_date_time = datetime.strptime(tendative_date+' '+start_time,'%d-%m-%Y %I:%M %p')
							end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))
							order_schedule_array.append(OrderScheduler(order=old_order,status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=old_book))

							updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total,status='EVALUATED')
							updated_evaluation 		   = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total)
							update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')+total,remining_amount=F('remining_amount')+total)
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
								section_name_arabic = Translator().translate(section_name,src='en', dest='ar').text
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

			return render(request,'agent/enquiry/phase2quatationduplicateedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

		return redirect('agent:agent-makequatation1duplicateedit',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)

class AddNewService(IsAgent,View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	def get(self,request,evaluation_detail_id,edit_type):
		
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

		return render(request,'agent/enquiry/addservice.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections})	

	def post(self,request,evaluation_detail_id,edit_type):
		service_formset       = self.service_formset_define(request.POST)
		evaluation_details 	  = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=evaluation_detail_id)

		if service_formset.is_valid() :
			form_count = 0
			#create order roughly
			new_order 				= Order.objects.get_or_create(evaluation=evaluation_details.evaluation,order_no=evaluation_details.evaluation.evaluation_id)

			order_schedule_array = []
			#Save Service Form
			for service_form in service_formset:

				if service_form.is_valid():
					service_form_save 					    = service_form.save(commit=False)
					service_form_save.evaluation_details_id = evaluation_detail_id
					service_form_save.save()


					#To Save Media
					medias = request.FILES.getlist('form-'+str(form_count)+'-media')
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
						if edit_type == 'duplicate':
							pass
						else:
							update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')+total,remining_amount=F('remining_amount')+total)
					else:
						tendative_date  = request.POST.get('form-'+str(form_count)+'-tendative_date')

						start_date_time = datetime.strptime(tendative_date+' '+start_time,'%d-%m-%Y %I:%M %p')
						end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours))
						order_schedule_array.append(OrderScheduler(order=new_order[0],status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=service_form_save))


						updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total,status='EVALUATED')
						updated_evaluation 		   = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total)
						if edit_type == 'duplicate':
							pass
						else:
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

						
						try:
							section_name_arabic = Translator().translate(section_name,src='en', dest='ar').text
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

			return render(request,'agent/enquiry/addservice.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'area_types':area_types,'service_types':service_types,})		

		if edit_type == 'duplicate':
			return redirect('agent:agent-makequatation2duplicateedit',evaluation_details.id)
		else:
			return redirect('agent:agent-makequatation2edit',evaluation_details.id)

class MakeQuatationPhase2Delete(IsAgent,View):
	def post(self,request,evaluation_detail_id):
		
		enquiry_id    = request.POST.get('enquiry_id')
		evaluation_id = request.POST.get('evaluation_id')

		evaluation_details = EvaluationDetails.objects.get(id=evaluation_detail_id)

		#update cost
		update_evaluation 		  = Evaluation.objects.filter(is_active=True,id=evaluation_id).update(estimated_cost=F('estimated_cost')-evaluation_details.estimated_cost,discount=F('discount')-evaluation_details.discount,total_cost=F('total_cost')-evaluation_details.total_cost,)
		update_order              = Order.objects.filter(is_active=True,evaluation__id=evaluation_id).update(total_amount=F('total_amount')-evaluation_details.total_cost)

		#delete evaluation details
		evaluation_details.delete()


		#delete full order if no other evaluations exists
		try:
			updated_evaluation = Evaluation.objects.prefetch_related('evaluation_details').get(is_active=True,id=evaluation_id)
		except:
			updated_evaluation = None

		if not updated_evaluation.evaluation_details.exists():
			updated_evaluation.delete()
			Order.objects.filter(is_active=True,evaluation__id=evaluation_id).delete()
			return redirect('agent:agent-orders')

		return redirect('agent:agent-makequatation1edit',enquiry_id,evaluation_id)


class AddFeedBack(IsAgent,View):
	def get(self,request):

		try:
			orders = Order.objects.filter(is_active=True,is_feedback_marked=False,payment_status='COMPLETED')
		except:
			orders = None

		try:
			questions = Question.objects.filter(is_active=True).order_by('id')
		except:
			questions = None

		return render(request,'agent/feedback/add-feedback.html',{'orders':orders,"questions":questions})

	def post(self,request):
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

		return redirect('agent:new-feedback')

class TicketRegistration(IsAgent,View):
	def get(self,request):

		try:
			orders = Order.objects.filter(is_active=True)
		except:
			orders = None

		investigators = UserProfile.objects.filter(user_type='QUALITYCONTROLL',is_active=True)

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
						
			messages.success(request,"Investigation Rised Succesfully!")
		else:
			messages.error(request,get_error(investigation_form))
		

		return redirect('agent:agent-ticketregister')

class OrderTicketRegistration(IsAgent,View):
	def get(self,request,orderid):

		order = Order.objects.filter(id=int(orderid)).first()

		investigators = UserProfile.objects.filter(user_type='QUALITYCONTROLL',is_active=True)

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
						
			messages.success(request,"Investigation Rised Succesfully!")
		else:
			messages.error(request,get_error(investigation_form))
		

		return redirect('agent:agent-ticketregister')

#ajax for client chart
def ClientData(request):
	print("lol")
	data = []
	dom = request.GET.get('dom',None)
	prevdate = request.GET.get('fromdate',None)
	todate  = request.GET.get('todate', None)
	print(prevdate,todate,"bhu")
	governorates = Governorate.objects.filter(is_active=True)

	if dom == 'Month':
		print("kabir")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")
		
		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=28,month=int(month2),year=int(year2),hour=23,minute=59,second=59,microsecond=0)
		
		try:
			for governorate in governorates:
				#change date field from evaluation date to order created date
				client_count = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,evaluation__customer__address_customer__governorate__id=governorate.id, evaluation__quatation_approved_date__range=(monthdate1,monthdate2)).values_list('evaluation__customer').distinct().count()

				data.append({
					"governorate" : governorate.name,
					"clients"	: client_count or 0,
					})
		except:
			governorates = None
	else:
		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=30)
		print(prevdate,todate,"bhoot")
		prev_date_start  = prevdate.replace(hour=0,minute=0,second=0,microsecond=0)
		prev_date_end = prevdate+timedelta(1)
		todate_date_start= todate.replace(hour=0,minute=0,second=0,microsecond=0)   #single_date+timedelta(1)
		todate_date_end = todate+timedelta(1)
		try:
			print("jn")
			for governorate in governorates:
				#change date field from evaluation date to order created date
				client_count = Order.objects.filter(is_active=True,evaluation__quatation_status__isnull=False,evaluation__customer__is_active=True,evaluation__customer__address_customer__governorate__id=governorate.id, evaluation__quatation_approved_date__gte=prev_date_start,evaluation__quatation_approved_date__lte=todate_date_end).values_list('evaluation__customer').distinct().count()
				print(client_count,"red")
				data.append({
					"governorate" : governorate.name,
					"clients"	: client_count,
					})
			print(data,"rgn")
		except:
			governorates = None

	return JsonResponse(data,safe=False)

#ajax for ticket chart
def TicketData(request):
	data = []
	dom = request.GET.get('dom', None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(dom,prevdate,todate,"pop")
	if dom == 'Month':
		print("kabir")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")

		print(month,year,month2,year2,"mko")

		monthdate1 = datetime(day=1,month=int(month),year=int(year))
		monthdate2 = datetime(day=28,month=int(month2),year=int(year2))

		tickets = FollowUp.objects.filter(is_active=True,investigation__order__created__range=(monthdate1,monthdate2))

		ticket_months = tickets.dates('investigation__order__created','month').distinct()
		print(tickets,"po")
		for tkt in ticket_months:
			month_start = datetime(day=1,month=tkt.month,year=tkt.year,hour=0,minute=0,second=0,microsecond=0)
			month_end = datetime(day=1,month=tkt.month,year=tkt.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
			print(month_start,month_end,"moth")

			monthly_tickets = FollowUp.objects.filter(is_active=True,investigation__order__created__range=(month_start,month_end)).count()
			followup_tickets = FollowUp.objects.filter(is_active=True,status='FOLLOWUP_CLOSED',investigation__order__created__range=(month_start,month_end)).count()
			print(followup_tickets,"huy")

			tkt_dict = {
			"date" : tkt.month,
			"total" : monthly_tickets,
			"followup" : followup_tickets
			}
			data.append(tkt_dict)
	else:
		print("kab")
		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=30)
		print(prevdate,todate,"testdt")
		daterange = pd.date_range(prevdate, todate)

		for single_date in daterange:
			ticket_date_start  = single_date.replace(hour=0,minute=0,second=0,microsecond=0)
			ticket_date_end    = single_date+timedelta(1)	
			
			total_tickets = FollowUp.objects.filter(is_active=True,investigation__order__evaluation__quatation_approved_date__gte=ticket_date_start,investigation__order__evaluation__quatation_approved_date__lte=ticket_date_end).count()
			followup_tickets = FollowUp.objects.filter(is_active=True,status='FOLLOWUP_CLOSED',investigation__order__evaluation__quatation_approved_date__gte=ticket_date_start,investigation__order__evaluation__quatation_approved_date__lte=ticket_date_end).count()
			print(total_tickets,followup_tickets,"qtc")
			tkt_dict = {
			"date" : single_date,
			"total" : total_tickets,
			"followup" : followup_tickets
			}
			data.append(tkt_dict)
	return JsonResponse(data,safe=False)

#ajax for feedback chart
def FeedBackData(request):
	data = []
	dom = request.GET.get('dom', None)
	prevdate  = request.GET.get('fromdate', None)
	todate  = request.GET.get('todate', None)
	print(dom,prevdate,todate,"pop")
	if dom == 'Month':
		print("kabir")
		month,year = prevdate.split("/")
		month2,year2 = todate.split("/")

		print(month2,year2,"mko")

		monthdate1 = datetime(day=1,month=int(month),year=int(year))
		monthdate2 = datetime(day=1,month=int(month2),year=int(year2),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)

		feedbacks = FeedBack.objects.filter(is_active=True,order__order_status='ORDER_CLOSED',order__created__range=(monthdate1,monthdate2))  #.values('order__evaluation__quatation_approved_date').annotate(month=Month('order__evaluation__quatation_approved_date'),).values('month').annotate(avg_rating=Avg('rating'))
		feedback_months = feedbacks.dates('order__created','month').distinct()
		print(feedback_months,"huh")
		
		for fb in feedback_months:
			month_start = datetime(day=1,month=fb.month,year=fb.year,hour=0,minute=0,second=0,microsecond=0)
			month_end = datetime(day=1,month=fb.month,year=fb.year,hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)
			print(month_start,month_end,"moth")
			feedback_avg_rating = FeedBack.objects.filter(is_active=True,order__order_status='ORDER_CLOSED',order__created__range=(month_start,month_end)).aggregate(avg_rating=Avg('rating'))['avg_rating']
			# if not feedback_avg_rating:
			# 	feedback_avg_rating = 0.0
			print(feedback_avg_rating,"fbr")
			fb_dict = {
			"date" : fb.month,
			"avg_rating" : feedback_avg_rating,
			}
			data.append(fb_dict)
	else:
		print("kab")
		try:
			prevdate = datetime.strptime(prevdate, '%Y-%m-%d')
			todate = datetime.strptime(todate, '%Y-%m-%d')
		except:
			todate = date.today() - timedelta(days=1)
			prevdate = todate - timedelta(days=30)
		print(prevdate,todate,"testdt")
		daterange = pd.date_range(prevdate, todate)

		for single_date in daterange:
			feedback_date_start  = single_date.replace(hour=0,minute=0,second=0,microsecond=0)
			feedback_date_end    = single_date+timedelta(1)	
			
			feedback_date = FeedBack.objects.filter(is_active=True,order__order_status='ORDER_CLOSED',order__created__range=(feedback_date_start,feedback_date_end)).aggregate(avg_rate=Avg('rating'))['avg_rate'] #use order date for final commit

			print(feedback_date,"qtc")
			if feedback_date:
				fb_dict = {
				"date" : single_date,
				"avg_rating" : feedback_date
				}
				data.append(fb_dict)
			else:
				pass
		print(data,"touche")
	return JsonResponse(data,safe=False)

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
		cleanings = CleaningTeamMember.objects.filter(is_active=True,member_id=d['id']).filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__order_scheduler__order__feed_backs_order').filter(team__check_out__isnull=False).values('team__order_scheduler__order__feed_backs_order__rating','member__id','member__profile_image','start_at','end_at')
		followups = FollowUpTeamMember.objects.filter(is_active=True,member_id=d['id']).filter(Q(Q(Q(start_at__gte=monthdate1)&Q(start_at__lt=monthdate2))|Q(Q(end_at__gte=monthdate1)&Q(end_at__lt=monthdate2)))).select_related('team__followup_scheduler__follow_up__investigation__order__feed_backs_order').filter(team__check_out__isnull=False).values('team__followup_scheduler__follow_up__investigation__order__feed_backs_order__rating','member__id','member__profile_image','start_at','end_at')		

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

# def emailview(request):
# 	send_mail('Using SparkPost with Django', 'This is a message from Django using SparkPost!', 'django-sparkpost@sparkpostbox.com',
#     ['rangeenkmr043@gmail.com'], fail_silently=False)

# 	return redirect('agent:agentdash-board')

def deleteservice(request,book_id,evaluation_detail_id):
	
	service = EvaluationBook.objects.get(id=book_id)
	evaluation = service.evaluation_details.evaluation
	order = Order.objects.get(evaluation__id=evaluation.id)
	evaluationdetails = service.evaluation_details

	#evaluation amount fix
	evaluation.estimated_cost = float(evaluation.estimated_cost) - float(service.total_cost)
	evaluation.total_cost = float(evaluation.estimated_cost) - float(evaluation.discount)
	evaluation.save()

	#evaluation details amount fix
	evaluationdetails.estimated_cost = float(evaluationdetails.estimated_cost) - float(service.total_cost)
	evaluationdetails.total_cost = float(evaluationdetails.estimated_cost) - float(evaluationdetails.discount)
	evaluationdetails.save()
	
	#order amount fix
	order.total_amount = float(order.total_amount) - float(service.total_cost)
	order.remining_amount = float(order.remining_amount) - float(service.total_cost)
	order.save()
	
	orderscheduler = OrderScheduler.objects.filter(order_scheduler_book__id=book_id).delete()
	service.delete()
	
	messages.success(request,"Service deleted successfully!")
	return redirect('agent:agent-makequatation2edit',evaluation_detail_id)

def deletesection(request,section_id,evaluation_detail_id):
	print(section_id,evaluation_detail_id,"ids47")
	section = EvaluationBookSection.objects.get(id=section_id)	
	service = section.evaluation_book
	evaluation = service.evaluation_details.evaluation
	evaluationdetails = service.evaluation_details
	order = Order.objects.get(evaluation__id=evaluation.id)

	if service.cleaning_policy == 'SUBSCRIPTION':
		orderschedules = OrderScheduler.objects.filter(order_scheduler_book__id=service.id).count()
		section_total_cost = float(section.section_cost) * float(orderschedules)
	else:
		section_total_cost = section.section_cost
	
	#evaluationbook amount fix
	service.estimated_cost = float(service.estimated_cost) - float(section_total_cost)
	service.total_cost = float(service.estimated_cost) - float(service.discount)
	service.save()

	#evaluation amount fix
	evaluation.estimated_cost = float(evaluation.estimated_cost) - float(section_total_cost)
	evaluation.total_cost = float(evaluation.estimated_cost) - float(evaluation.discount)
	evaluation.save()

	#evaluation details amount fix
	evaluationdetails.estimated_cost = float(evaluationdetails.estimated_cost) - float(section_total_cost)
	evaluationdetails.total_cost = float(evaluationdetails.estimated_cost) - float(evaluationdetails.discount)
	evaluationdetails.save()

	#order amount fix
	order.total_amount = float(order.total_amount) - float(section_total_cost)
	order.remining_amount = float(order.remining_amount) - float(section_total_cost)
	order.save()

	section.delete()
						
	messages.success(request,"Section deleted successfully!")
	return redirect('agent:agent-makequatation2edit',evaluation_detail_id)
