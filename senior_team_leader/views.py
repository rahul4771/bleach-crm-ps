from django.shortcuts import render,redirect
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsSeniorTeamLeader
from bleach_crm_ps.utils import get_error
from django.http import HttpResponse,JsonResponse

import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast 
from django.db.models import Prefetch
from django.contrib import messages

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote,EvaluationMedia,ServiceType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp,Investigation,InvestigationMedia,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from senior_team_leader.forms import CleaningTeamAssignForm,FollowupTeamAssignForm
# Create your views here.


def GetCleaningInfo(request):
	cleaning_dict = {}

	scheduler_id  = int(request.GET.get('schedule_id'))
	schedule  = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book','customer_address__customer','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_member')),to_attr='cleaning_team')).get(id=scheduler_id,is_active=True)

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

	#same blc cleaners for excluding
	sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=schedule.evaluation_details.evaluation).values_list("member",flat=True)

	#free slotes
	active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at))|Q(Q(end_at__gte=schedule.start_at)&Q(end_at__lte=schedule.end_at))|Q(Q(start_at__lte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__gte=schedule.end_at))|Q(Q(start_at__gte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__lte=schedule.end_at)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
	active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at))|Q(Q(end_at__gte=schedule.start_at)&Q(end_at__lte=schedule.end_at))|Q(Q(start_at__lte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__gte=schedule.end_at))|Q(Q(start_at__gte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__lte=schedule.end_at)))).values_list("member",flat=True)
			
	leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
	cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMLEADER')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))

	#available leaders
	available_leaders_info = {}
	available_leaders_info['available_leaders']   = []
	for leader in leaders:
		available_leaders_dict = {}

		available_leaders_dict["leader_name"] 	= leader.name
		available_leaders_dict["leader_id"] 	= leader.id

		available_leaders_info['available_leaders'].append(available_leaders_dict)

	cleaning_dict['availableleadersinfo'] =	available_leaders_info


	#available cleaners
	available_cleaners_info = {}
	available_cleaners_info['available_cleaners']   = []
	for cleaner in cleaners:
		available_cleaners_dict = {}

		available_cleaners_dict["cleaner_name"] 	= cleaner.name
		available_cleaners_dict["cleaner_id"]   	= cleaner.id

		available_cleaners_info['available_cleaners'].append(available_cleaners_dict)

	cleaning_dict['availablecleanersinfo'] =	available_cleaners_info

	print(cleaning_dict)
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
	

	#free slotes
	active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at))|Q(Q(end_at__gte=schedule.start_at)&Q(end_at__lte=schedule.end_at))|Q(Q(start_at__lte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__gte=schedule.end_at))|Q(Q(start_at__gte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__lte=schedule.end_at)))).values_list("member",flat=True)
	active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at))|Q(Q(end_at__gte=schedule.start_at)&Q(end_at__lte=schedule.end_at))|Q(Q(start_at__lte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__gte=schedule.end_at))|Q(Q(start_at__gte=schedule.start_at)&Q(end_at__gte=schedule.start_at)&Q(start_at__lte=schedule.end_at)&Q(end_at__lte=schedule.end_at)))).values_list("member",flat=True)

	leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
	cleaners            = UserProfile.objects.filter(is_active=True,user_type='CLEANER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))

	#available leaders
	available_leaders_info = {}
	available_leaders_info['available_leaders']   = []
	for leader in leaders:
		available_leaders_dict = {}

		available_leaders_dict["leader_name"] 	= leader.name
		available_leaders_dict["leader_id"] 	= leader.id

		available_leaders_info['available_leaders'].append(available_leaders_dict)

	cleaning_dict['availableleadersinfo'] =	available_leaders_info


	#available cleaners
	available_cleaners_info = {}
	available_cleaners_info['available_cleaners']   = []
	for cleaner in cleaners:
		available_cleaners_dict = {}

		available_cleaners_dict["cleaner_name"] 	= cleaner.name
		available_cleaners_dict["cleaner_id"]   	= cleaner.id

		available_cleaners_info['available_cleaners'].append(available_cleaners_dict)

	cleaning_dict['availablecleanersinfo'] =	available_cleaners_info

	print(cleaning_dict)
	return JsonResponse(cleaning_dict)	



class OrderDetails(IsSeniorTeamLeader,View):
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

		#exclude atleast 1 not completed evaluatis
		exclude_ids = []	
		for evaluation in evaluations:
			if not evaluation.completed_evaluations:
				exclude_ids.append(evaluation.id)
		evaluations = evaluations.exclude(id__in=exclude_ids)	

		fil_status = request.GET.get('status')
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

		return render(request,'stl/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,})

class ClientOrderDetails(IsSeniorTeamLeader,View):
	def get(self,request,order_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)


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


		return render(request,"stl/client/order-page.html",{"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"average_feedback":average_feedback,})


class ClientOrders(IsSeniorTeamLeader,View):
	def get(self,request,client_id):

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'))

		#COUNT
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()

		return render(request,"stl/client/client-page.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,})


class StlHome(IsSeniorTeamLeader,View):
	def get(self,request):

		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)
		
	    #Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))).count() 
		week_cleaning_job_count  = cleaning_job.filter(Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end))).count()		


		#total workers count
		try:
			total_workers = UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER'))).count()
		except:
			total_workers = 0
		
		#total active workers
		try:
			total_active_workers = CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__lte=timezone.now())&Q(end_at__gte=timezone.now())) )).values_list('member',flat=True).distinct().union(FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__lte=timezone.now())&Q(end_at__gte=timezone.now()))) ).values_list('member',flat=True)).distinct().count()
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
		weekstart_date        = timezone.now().date()-timedelta(6)

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


		#cleaning schedule & followup schedule for resources			
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
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER'))&Q(name__icontains=search))
			except:
				workers =  None
		else:
			try:
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER')))
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

		filters=[]
		if fil_staff:
			case1 = Q(user_type=fil_staff)
			filters.append(case1)

		if fil_staff:
			filters         = functools.reduce(operator.and_,filters)
			workers_details = workers_details.filter(filters)	

			
		#cleaning schedule & followup schedule for cleaning calendar			
		cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')
		
		try:
			schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			schedule_date = timezone.now().replace(tzinfo=None)

		schedule_date_start = schedule_date.replace(hour=0,minute=0,second=0,microsecond=0)
		schedule_date_end   = schedule_date_start+timedelta(1)	

		try:
			calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).order_by('start_at').select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).order_by('start_at').filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') ))
		except:
			calendar_order_schedules = None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).order_by('start_at').select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			calendar_followup_schedules = None
	
		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') ))
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			sp_calendar_followup_schedules = None							

		try:
			spp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(order__evaluation__payment_method='SUBSCRIPTION') ))
		except:
			spp_calendar_order_schedules = None

		try:
			spp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			spp_calendar_followup_schedules = None


		#cleaning team assignment task
		teamassign_to_date         = (timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)).replace(tzinfo=None)
		
		try:
			assign_order_schedules = OrderScheduler.objects.filter(work_status__isnull=True,status='CONFIRMED',is_active=True,start_at__lt=teamassign_to_date+timedelta(14)).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='SUBSCRIPTION') ))
		except:
			assign_order_schedules = None

		try:
			assign_followup_schedules = FollowUpScheduler.objects.filter(work_status__isnull=True,status='CONFIRMED',is_active=True,start_at__lt=teamassign_to_date+timedelta(14)).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			assign_followup_schedules = None

		#add days left
		if assign_order_schedules:
			for schedule in assign_order_schedules:
				schedule.days_left_coming = (schedule.start_at-timezone.now()).days
		if assign_followup_schedules:
			for followupschedule in assign_followup_schedules:
				followupschedule.days_left_coming = (followupschedule.start_at-timezone.now()).days

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
	


		return render(request,'stl/home/home.html',{'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'spp_calendar_order_schedules':spp_calendar_order_schedules,'spp_calendar_followup_schedules':spp_calendar_followup_schedules,'schedule_date':schedule_date,"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,"fil_minhours":fil_minhours,"fil_maxhours":fil_maxhours,"fil_staff":fil_staff,'assign_order_schedules':assign_order_schedules,'assign_followup_schedules':assign_followup_schedules})

	def post(self,request):
		action = request.POST.get('action_type')

		if action == 'edit_cleaning':
			schedule_id    = request.POST.get('cleaning_id')	
			order_schedule      = OrderScheduler.objects.select_related('evaluation_details__evaluation').get(is_active=True,id=schedule_id)
			assigned_cleaners   = request.POST.getlist('team_member')

			#new cleaning dates
			cleaning_date 	= request.POST.get('cleaning_date')
			cleaning_time   = request.POST.get('cleaning_time')
			cleaning_hours 	= float(request.POST.get('cleaning_hours'))
			start_at        = datetime.strptime(cleaning_date+' '+cleaning_time,'%d-%m-%Y %I:%M %p')
			end_at          = start_at + timedelta(hours=cleaning_hours)


			#update cleaners count
			if assigned_cleaners:
				order_schedule.order_scheduler_book.number_of_cleaners = len(assigned_cleaners)
				order_schedule.order_scheduler_book.save()

			#delete existing cleaners
			cleaners_to_be_deleted = CleaningTeamMember.objects.filter(team__order_scheduler_id=schedule_id).delete()

			#same blc cleaners for excluding
			sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).values_list("member",flat=True)
			#validates
			active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).exclude(member__id__in=sameblc_cleaners).values_list('member',flat=True)
			active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list('member',flat=True)	


			check_cleaners_assigned = UserProfile.objects.filter(is_active=True,user_type='CLEANER').filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
			check_tl_assigned       = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=request.POST.get('team_leader'))		

			if schedule_id and not check_cleaners_assigned and not check_tl_assigned and start_at == ((order_schedule.start_at+timedelta(hours=3)).replace(tzinfo=None)) and end_at == ((order_schedule.end_at+timedelta(hours=3)).replace(tzinfo=None)):
				
				#update cleaning team leader
				assigned_leader  = request.POST.get('team_leader')
				
				cleaning_team                = CleaningTeam.objects.get(is_active=True,order_scheduler_id=schedule_id,team_leader__user_type='TEAMLEADER')
				cleaning_team.team_leader_id = assigned_leader
				cleaning_team.save()

				#update cleaning team members
				start_at_to_assign=(order_schedule.start_at+timedelta(hours=3)).time()
				end_at_to_assign  =(order_schedule.end_at+timedelta(hours=3)).time()
				assigned_cleaners_list   = []
				for cleaner in assigned_cleaners:
					assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member_id=cleaner,start_at=order_schedule.start_at,end_at=order_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
				assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member_id=assigned_leader,start_at=order_schedule.start_at,end_at=order_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
				#bulk create
				CleaningTeamMember.objects.bulk_create(assigned_cleaners_list)
						
				messages.success(request,"Cleaning Team Updated")

			#update cleaning dates	
			elif start_at != ((order_schedule.start_at+timedelta(hours=3)).replace(tzinfo=None)) and end_at != ((order_schedule.start_at+timedelta(hours=3)).replace(tzinfo=None)): 
				CleaningTeam.objects.filter(order_scheduler=order_schedule).delete()
				order_schedule.work_status = None
				order_schedule.start_at    = start_at
				order_schedule.end_at      = end_at
				order_schedule.save()

				messages.success(request,"Cleaning Date Changed Please Assign New Cleaning Team")
			else:
				messages.error(request,"Something Went Wrong")			

		if action == 'edit_followup':
			schedule_id    = request.POST.get('followup_id')
			followup_schedule = FollowUpScheduler.objects.get(is_active=True,id=schedule_id)
			assigned_cleaners   = request.POST.getlist('team_member')

			#update followup count
			followup_schedule.follow_up.no_of_cleaners = len(assigned_cleaners)
			followup_schedule.follow_up.save()

			#delete existing cleaners
			cleaners_to_be_deleted = FollowUpTeamMember.objects.filter(team__followup_scheduler_id=schedule_id).delete()

			#validates
			active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
			active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)	

			check_cleaners_assigned = UserProfile.objects.filter(is_active=True,user_type='CLEANER').filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
			check_tl_assigned       = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=request.POST.get('team_leader'))

			if schedule_id and not check_cleaners_assigned and not check_tl_assigned:
				#update followup team leader
				assigned_leader  = request.POST.get('team_leader')
				
				followup_team                = FollowUpTeam.objects.get(is_active=True,followup_scheduler_id=schedule_id,team_leader__user_type='TEAMLEADER')
				followup_team.team_leader_id = assigned_leader
				followup_team.save()

				#update Followup team members
				start_at_to_assign=(followup_schedule.start_at+timedelta(hours=3)).time()
				end_at_to_assign  =(followup_schedule.end_at+timedelta(hours=3)).time()
				assigned_cleaners_list   = []
				for cleaner in assigned_cleaners:
					assigned_cleaners_list.append(FollowUpTeamMember(team=followup_team,member_id=cleaner,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
				assigned_cleaners_list.append(FollowUpTeamMember(team=followup_team,member_id=assigned_leader,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
				#bulk create
				FollowUpTeamMember.objects.bulk_create(assigned_cleaners_list)	

				FollowUpScheduler.objects.filter(id=schedule_id).update(work_status='FOLLOW_UP_TEAM_ASSIGNED')
				
				messages.success(request,"Follow Up Team Updated")		
			else:
				messages.error(request,"Something Went Wrong")				

		if action =='confirm_followupchedule':
			followupscheduler_id = request.POST.get('followupscheduler')
			followup_scheduler   = FollowUpScheduler.objects.get(id=followupscheduler_id)
			confirm_status       = request.POST.get('confirm')

			confirm_date 	 = request.POST.get('followup_schedule_date')
			confirm_time 	 = request.POST.get('followup_schedule_time')
			start_at         = datetime.strptime(confirm_date+' '+confirm_time,'%d-%m-%Y %I:%M %p')
			end_at           = start_at + timedelta(hours=followup_scheduler.follow_up.cleaning_hours)

			if confirm_status:
				FollowUpScheduler.objects.filter(id=followupscheduler_id).update(status='CONFIRMED',start_at=start_at,end_at=end_at)
				messages.success(request,"Followup Cleaning Date Succesfully Confirmed")
			else:
				FollowUpScheduler.objects.filter(id=followupscheduler_id).update(start_at=start_at,end_at=end_at)
				messages.success(request,"Followup Cleaning Date Not Confirmed")	

		# if action =='confirm_orderschedules':
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

		cleaning_calendar_date = request.GET.get('cleaning_calendar_date') or ''
		workers_calendar_date  = request.GET.get('workers_calendar_date') or ''

		return redirect('/stl/dashboard/?cleaning_calendar_date='+cleaning_calendar_date+'&workers_calendar_date='+workers_calendar_date)


class TicketDetails(IsSeniorTeamLeader,View):
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

		return render(request,'stl/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})		

class TicketAdvanced(IsSeniorTeamLeader,View):
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

		return render(request,'stl/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})		

class AssigncleaningTeam(IsSeniorTeamLeader,View):
	def get(self,request,scheduler_id):

		#shceduled order details
		order_schedule = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book__service_type').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections')).get(is_active=True,id=scheduler_id)

		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).values_list("member",flat=True)
		
		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list("member",flat=True)
			
		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMLEADER')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		drivers             = UserProfile.objects.filter(is_active=True,user_type='DRIVER')

		return render(request,'stl/cleaning/cleaningteam_assign.html',{'order_schedule':order_schedule,'cleaners':cleaners,'leaders':leaders,'drivers':drivers,})

	def post(self,request,scheduler_id):
		
		#shceduled order details
		order_schedule = OrderScheduler.objects.select_related('evaluation_details__evaluation','order_scheduler_book').get(is_active=True,id=scheduler_id)
		
		#to block back button submission
		if order_schedule.work_status=='CLEANING_TEAM_ASSIGNED':
			return redirect('agent:agentdash-board')

		cleaning_team_assign_form = CleaningTeamAssignForm(request.POST)
		assigned_cleaners         = request.POST.getlist('assigned_cleaner')
		#update cleaners count
		order_schedule.order_scheduler_book.number_of_cleaners = len(assigned_cleaners)
		order_schedule.order_scheduler_book.save()

		#same blc cleaners for excluding
		sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).values_list("member",flat=True)

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).exclude(member__id__in=sameblc_cleaners).values_list('member',flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list('member',flat=True)	

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMLEADER')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		drivers             = UserProfile.objects.filter(is_active=True,user_type='DRIVER')
	    #validation
		check_cleaners_assigned = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMLEADER')))).filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
		check_tl_assigned       = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=request.POST.get('team_leader'))
				

		if	cleaning_team_assign_form.is_valid() and not check_cleaners_assigned and not check_tl_assigned:
			cleaning_team_assign_form_save                   = cleaning_team_assign_form.save(commit=False)
			cleaning_team_assign_form_save.order_scheduler_id= scheduler_id
			cleaning_team_assign_form_save.start_at          = order_schedule.start_at
			cleaning_team_assign_form_save.end_at            = order_schedule.end_at
			cleaning_team_assign_form_save.created_by        = request.user
			cleaning_team_assign_form_save.save()


			#cleaners
			start_at_to_assign=(order_schedule.start_at+timedelta(hours=3)).time()
			end_at_to_assign  =(order_schedule.end_at+timedelta(hours=3)).time()
			assigned_cleaners_list   = []
			for cleaner in assigned_cleaners:
				assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team_assign_form_save,member_id=cleaner,start_at=order_schedule.start_at,end_at=order_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
			assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team_assign_form_save,member=cleaning_team_assign_form_save.team_leader,start_at=order_schedule.start_at,end_at=order_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
			#bulk create
			CleaningTeamMember.objects.bulk_create(assigned_cleaners_list)	

			OrderScheduler.objects.filter(id=scheduler_id).update(work_status='CLEANING_TEAM_ASSIGNED')
		else:	
			messages.error(request,"Something Went Wrong")

			return render(request,'stl/cleaning/cleaningteam_assign.html',{'cleaning_team_assign_form':cleaning_team_assign_form,'order_schedule':order_schedule,'cleaners':cleaners,'leaders':leaders,'drivers':drivers})	

		messages.success(request,"Cleaning Team Succesfully Assigned")

		cleaning_calendar_date = request.GET.get('cleaning_calendar_date') or ''
		workers_calendar_date  = request.GET.get('workers_calendar_date') or ''

		return redirect('/stl/dashboard/?cleaning_calendar_date ='+cleaning_calendar_date+'&workers_calendar_date='+workers_calendar_date)	

class AssignFollowupTeam(IsSeniorTeamLeader,View):
	def get(self,request,scheduler_id):

		#shceduled order details
		followup_schedule = FollowUpScheduler.objects.select_related('follow_up__investigation__order','follow_up__investigation__order_schedule__order_scheduler_book__service_type','customer_address').prefetch_related(Prefetch('follow_up__investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr="investigationmedias"),Prefetch('follow_up__investigation__order_schedule__order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections')).get(is_active=True,id=scheduler_id)
	
		follow_up_team_assign_form = FollowupTeamAssignForm()
		

		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)

		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		cleaners            = UserProfile.objects.filter(is_active=True,user_type='CLEANER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		drivers             = UserProfile.objects.filter(is_active=True,user_type='DRIVER')

		return render(request,'stl/cleaning/followupteam_assign.html',{'follow_up_team_assign_form':follow_up_team_assign_form,'followup_schedule':followup_schedule,'cleaners':cleaners,'leaders':leaders,'drivers':drivers,})

	def post(self,request,scheduler_id):
	
		#shceduled order details
		followup_schedule = FollowUpScheduler.objects.select_related('follow_up__investigation__order','follow_up__investigation__order_schedule__order_scheduler_book__service_type','customer_address').get(is_active=True,id=scheduler_id)	

		follow_up_team_assign_form = FollowupTeamAssignForm(request.POST)
		assigned_cleaners          = request.POST.getlist('assigned_cleaner')
		#update cleaners count
		followup_schedule.follow_up.no_of_cleaners = len(assigned_cleaners)
		followup_schedule.follow_up.save()


		active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
		active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at))|Q(Q(end_at__gte=followup_schedule.start_at)&Q(end_at__lte=followup_schedule.end_at))|Q(Q(start_at__lte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__gte=followup_schedule.end_at))|Q(Q(start_at__gte=followup_schedule.start_at)&Q(end_at__gte=followup_schedule.start_at)&Q(start_at__lte=followup_schedule.end_at)&Q(end_at__lte=followup_schedule.end_at)))).values_list('member',flat=True)
	
		leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		cleaners            = UserProfile.objects.filter(is_active=True,user_type='CLEANER').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
		drivers             = UserProfile.objects.filter(is_active=True,user_type='DRIVER')

		#validation
		check_cleaners_assigned = UserProfile.objects.filter(is_active=True,user_type='CLEANER').filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
		check_tl_assigned       = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER').filter(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=request.POST.get('team_leader'))
		

		
		if	follow_up_team_assign_form.is_valid() and not check_cleaners_assigned and not check_tl_assigned:
			follow_up_team_assign_form_save                   = follow_up_team_assign_form.save(commit=False)
			follow_up_team_assign_form_save.followup_scheduler_id= scheduler_id
			follow_up_team_assign_form_save.start_at          = followup_schedule.start_at
			follow_up_team_assign_form_save.end_at            = followup_schedule.end_at
			follow_up_team_assign_form_save.created_by        = request.user
			follow_up_team_assign_form_save.save()

			#cleaners
			start_at_to_assign=(followup_schedule.start_at+timedelta(hours=3)).time()
			end_at_to_assign  =(followup_schedule.end_at+timedelta(hours=3)).time()
			assigned_cleaners_list   = []
			for cleaner in assigned_cleaners:
				assigned_cleaners_list.append(FollowUpTeamMember(team=follow_up_team_assign_form_save,member_id=cleaner,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
			assigned_cleaners_list.append(FollowUpTeamMember(team=follow_up_team_assign_form_save,member=follow_up_team_assign_form_save.team_leader,start_at=followup_schedule.start_at,end_at=followup_schedule.end_at,start_time=start_at_to_assign,end_time=end_at_to_assign))
			#bulk create
			FollowUpTeamMember.objects.bulk_create(assigned_cleaners_list)	

			FollowUpScheduler.objects.filter(id=scheduler_id).update(work_status='FOLLOW_UP_TEAM_ASSIGNED')
		else:	
			messages.error(request,"Something Went Wrong")

			return render(request,'stl/cleaning/followupteam_assign.html',{'follow_up_team_assign_form':follow_up_team_assign_form,'followup_schedule':followup_schedule,'cleaners':cleaners,'leaders':leaders,'drivers':drivers,})	

		messages.success(request,"FollowupTeam Team Succesfully Assigned")

		cleaning_calendar_date = request.GET.get('cleaning_calendar_date') or ''
		workers_calendar_date  = request.GET.get('workers_calendar_date') or ''

		return redirect('/stl/dashboard/?cleaning_calendar_date ='+cleaning_calendar_date+'&workers_calendar_date='+workers_calendar_date)

