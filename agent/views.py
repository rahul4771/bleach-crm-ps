from django.shortcuts import render,redirect
from django.views import View
from django.forms import formset_factory,modelformset_factory
from django.http import HttpResponse,JsonResponse

from django.conf import settings
from bleach_crm_ps.permissions import IsAgent
from bleach_crm_ps.utils import get_error


import random
import string
import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField
from django.db.models.functions import Cast 
from django.db.models import Prefetch
from django.contrib import messages

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,CleaningMethod
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember

from agent.forms import UserProfileForm,AddressForm
from evaluator.forms import EvaluationDetailsForm,QuatationServiceForm,PaymentTrackForm
from order.forms import InvestigationForm

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

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('customer_address__area','customer_address'),to_attr='order_secheduler_feedback')).get(id=order_id,is_active=True)
		
		dropdown_order_info['name']          = order.evaluation.customer.name
		dropdown_order_info['mobile_number'] = order.evaluation.customer.mobile_number
		dropdown_order_info['order_id']      = order.id 		
		dropdown_order_info['address']       = []

		#for multiple addresses
		for scheduler in order.order_secheduler_feedback:
			customer_address = {}

			customer_address['governorate'] 	= scheduler.customer_address.governorate.name
			customer_address['area'] 			= scheduler.customer_address.area.name
			customer_address['block'] 		= scheduler.customer_address.block
			customer_address['avenue'] 		= scheduler.customer_address.avenue
			customer_address['building'] 		= scheduler.customer_address.building
			customer_address['street'] 		= scheduler.customer_address.street
			customer_address['floor'] 		= scheduler.customer_address.floor
			customer_address['apartment'] 	= scheduler.customer_address.apartment

			dropdown_order_info['address'].append(customer_address)			

		return JsonResponse(dropdown_order_info)

#Ajax for getticket ordershedules address Information
def GetOrderScheduleTicketInfo(request):
	dropdown_orderschedule_info = {}

	order_id            = request.GET.get('order_id') 

	try:
		ordershedules   = OrderScheduler.objects.filter(order_id=order_id,is_active=True).select_related('customer_address__area','order_scheduler_book')
	except:
		ordershedules   = None

	order_schedule = {}
	for schedule in ordershedules:
		order_schedule[schedule.id] = schedule.customer_address.area.name+'-'+schedule.order_scheduler_book.service_type.name or ''

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




# Create your views here. 
class AgentHome(IsAgent,View):
	def get(self,request):


		#Enquiry Details count
		try:
			enquiry = EvaluationDetails.objects.filter(is_active=True)
		except:
			enquiry	= None

		today_enquiry_count = enquiry.filter(proposed_time__contains=timezone.now().date()).count()
		week_enquiry_count  = enquiry.filter(proposed_time__gte=timezone.now().date()-timedelta(6)).count()	

		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(start_at__contains=timezone.now().date()).count() 
		week_cleaning_job_count  = cleaning_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		
		
		#Followup jobs count
		try:
			follow_up_job    = FollowUpTeam.objects.filter(is_active=True)
		except:
			follow_up_job	 = None

		today_follow_up_job_count = follow_up_job.filter(start_at__contains=timezone.now().date()).count() 
		week_follow_up_job_count  = follow_up_job.filter(start_at__gte=timezone.now().date()-timedelta(6)).count()		

		#Feedback Staring count
		try:
			feedbacks                 = FeedBack.objects.filter(is_active=True)
		except:
			feedbacks				  = None

		today_average_feedback		  = feedbacks.filter(response_date__contains=timezone.now().date()).aggregate(Avg('rating'))['rating__avg']
		week_average_feedback		  = feedbacks.filter(response_date__gte=timezone.now().date()-timedelta(6)).aggregate(Avg('rating'))['rating__avg']	
		
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


		#Order and Followup Schedules for date confirmation
		try:
			order_schedules		  = OrderScheduler.objects.filter(is_active=True).exclude(Q(Q(status='CONFIRMED')|Q(status='CANCELLED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
		except:
			order_schedules		  = None
		
		try:
			follow_up_schedules	  = FollowUpScheduler.objects.filter(is_active=True,).exclude(Q(Q(status='CONFIRMED')|Q(status='CANCELLED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			follow_up_schedules	  = None		
		

		#cleaning schedule & followup schedule for cleaning calendar			
		cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')
		
		try:
			schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			schedule_date = timezone.now()

		try:
			calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__contains=schedule_date.date())&Q(end_at__contains=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
		except:
			calendar_order_schedules = None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__contains=schedule_date.date())&Q(end_at__date=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			calendar_followup_schedules = None
	
		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__contains=schedule_date.date())&~Q(end_at__contains=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book')
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__contains=schedule_date.date())&~Q(end_at__contains=schedule_date.date()))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			sp_calendar_followup_schedules = None							

		return render(request,'agent/home/home.html',{'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'today_average_feedback':today_average_feedback,'week_average_feedback':week_average_feedback,'cleaning_job':cleaning_job,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'follow_up_job':follow_up_job,'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'order_schedules':order_schedules,'follow_up_schedules':follow_up_schedules,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'schedule_date':schedule_date,})


	def post(self,request):
		action_mode = request.POST.get('action_type')

		if action_mode =='delete_followupchedule':
			followupscheduler_id = request.POST.get('followupscheduler')
			FollowUpScheduler.objects.filter(id=followupscheduler_id).update(status='CONFIRMED')
		
		elif action_mode =='delete_orderschedule':	
			orderscheduler_id = request.POST.get('orderscheduler')
			OrderScheduler.objects.filter(id=orderscheduler_id).update(status='CONFIRMED')

		return redirect('agent:agentdash-board')	


class ResourceManagement(IsAgent,View):
	def get(self,request):


		#total workers count
		try:
			total_workers = UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER'))).count()
		except:
			total_workers = 0
		
		#total active workers
		try:
			total_active_workers = CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__contains=timezone.now().date())|Q(end_at__contains=timezone.now().date())) )).values_list('member',flat=True).distinct().union(FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__contains=timezone.now().date())|Q(end_at__contains=timezone.now().date())) )).values_list('member',flat=True)).distinct().count()
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

	
		today_cleaning_active_teams  = cleaning_teams.filter(Q(Q(start_at__contains=timezone.now().date())|Q(end_at__contains=timezone.now().date())))
		today_followup_active_teams  = follow_up_teams.filter(Q(Q(start_at__contains=timezone.now().date())|Q(end_at__contains=timezone.now().date())))
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
			workers_details = workers.prefetch_related(Prefetch('cleaning_member_user',queryset=CleaningTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__contains=workers_date.date())|Q(end_at__contains=workers_date.date())) )).select_related('team__order_scheduler__customer_address__area','team__order_scheduler__order__evaluation','team__order_scheduler__order_scheduler_book'),to_attr='cleaning_member_details'),Prefetch('followup_member',queryset=FollowUpTeamMember.objects.filter( Q( Q(is_active=True)&Q(Q(start_at__contains=workers_date.date())|Q(end_at__contains=workers_date.date())) )).select_related('team__followup_scheduler__customer_address__area'),to_attr='followup_member_details'))
		except:
			workers_details = None


		return render(request,'agent/resource/resource_management.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams})		


class OrderDetails(IsAgent,View):
	def get(self,request):

		#Evaluation Details
		search                  = request.GET.get('search')
		
		if search:
			try:
				evaluations = Evaluation.objects.select_related('customer').filter(is_active=True,customer__name__icontains=search).prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))
			except:
				evaluations = None 
		 
		else:
			try:
				evaluations = Evaluation.objects.filter(is_active=True).select_related('customer').prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))
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

		return render(request,'agent/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})


class FeedbackDetails(IsAgent,View):
	def get(self,request):
		
		search                  = request.GET.get('search')

		#Feedback Staring count
		try:
			feedbacks                 = FeedBack.objects.filter(is_active=True)
		except:
			feedbacks				  = None

		average_feedback    		  = feedbacks.aggregate(Avg('rating'))['rating__avg']
		total_feedbacks               = feedbacks.count()
		starring_percentages          = list(feedbacks.values('rating').annotate(percentage=Cast(Count('rating')/float(total_feedbacks)*100,FloatField())).order_by('rating'))

		#append not done rating to default 0
		for i in range(1,6):
			new_rating = {}
			if not any(starring['rating'] == i for starring in starring_percentages):
				new_rating['rating']     = i
				new_rating['percentage'] = 0
				starring_percentages.append(new_rating)	

		starring_percentages = sorted(starring_percentages, key = lambda i: i['rating'])		



		#order wise feedback
		if search:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True,evaluation__customer__name__icontains=search).prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField()))		
			except:
				order_wise_feedbacks = None

		else:
			try:
				order_wise_feedbacks = Order.objects.select_related('evaluation__customer').filter(is_active=True).prefetch_related(Prefetch('feed_backs_order',queryset=FeedBack.objects.filter(is_active=True),to_attr='feedback_details'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='order_evaluation_details')).annotate(avg_starring=Cast(Sum('feed_backs_order__rating')/5.0,FloatField()))						
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

		return render(request,'agent/feedback/feedbacks.html',{"feedbacks":feedbacks,"average_feedback":average_feedback,"total_feedbacks":total_feedbacks,"starring_percentages":starring_percentages,"order_wise_feedbacks":order_wise_feedbacks,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})
		

class TicketDetails(IsAgent,View):
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

		return render(request,"agent/ticket/tickets.html",{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page})		


class ClientDetails(IsAgent,View):
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
		
		return render(request,"agent/client/clients.html",{"client_details":client_details,"search_query":search,"active_clients_count":active_clients_count,"new_clients_count":new_clients_count,"page_range":page_range,"entry_per_page":entry_per_page}) 


class NewEnquiry(IsAgent,View):
	address_formset_define    = formset_factory(AddressForm)
	def get(self,request):
		
		enquiry_form    = UserProfileForm()	

		try:
			customer_info = UserProfile.objects.filter(is_active=True,user_type='CUSTOMER')
		except:	
			customer_info = None

		return render(request,'agent/enquiry/new_enquiry.html',{'enquiry_form':enquiry_form,'address_formset':self.address_formset_define(),'customer_info':customer_info})

	def post(self,request):
		enquiry_form     = UserProfileForm(request.POST,request.FILES or None)
		address_formset  = self.address_formset_define(request.POST)


		if enquiry_form.is_valid() and address_formset.is_valid(): 
			enquiry_form_save            = enquiry_form.save(commit=False)	
			enquiry_form_save.username   = generate_random_username()
			enquiry_form_save.created_by = request.user
			enquiry_form_save.user_type  = 'CUSTOMER'
			enquiry_form_save.save()

			for address_form in address_formset:
				if address_form.is_valid():
					address_form_save                   = address_form.save(commit=False)
					address_form_save.customer          = enquiry_form_save
					address_form_save.currently_active  = True
					address_form_save.save()
			messages.success(request,"Customer Details Succesfully Added")

		else:
			if not enquiry_form.is_valid():
				messages.error(request,get_error(enquiry_form))
			if not address_formset.is_valid():
				messages.error(request,"An Error Occured")

			return render(request,'agent/enquiry/new_enquiry.html',{'enquiry_form':enquiry_form,'address_formset':address_formset})					

		redirection = request.POST.get('redirect_to')	
		
		if redirection == 'assign_evaluator':
			return redirect('agent:agent-assignevaluator',enquiry_form_save.id)	
		elif redirection == 'quatation':
			return redirect('agent:agent-makequatation',enquiry_form_save.id)
		else:
			return redirect('agent-existingenquiry',enquiry_form_save.id)


class ExistingEnquiry(IsAgent,View):
	
	def get(self,request,enquiry_id):
		
		enquiry_user    = UserProfile.objects.get(id=enquiry_id) 


		try:
			addresses   = Address.objects.filter(customer__id=enquiry_id)
		except:	
			addresses   = None


		enquiry_form    = UserProfileForm(request.FILES or None,instance=enquiry_user)	
		address_form    = AddressForm()	

		return render(request,'agent/enquiry/existing_enquiry.html',{'enquiry_form':enquiry_form,"address_form":address_form,'enquiryid':enquiry_id,'addresses':addresses,})

	def post(self,request,enquiry_id):

		enquiry_user    = UserProfile.objects.get(id=enquiry_id)
		
		action_mode 	= request.POST.get('action_type')

		if action_mode == 'update_customer_details':
			enquiry_form    = UserProfileForm(request.POST,request.FILES or None,instance=enquiry_user)

			if enquiry_form.is_valid(): 
				enquiry_form_save            = enquiry_form.save(commit=False)	
				enquiry_form_save.save()

				messages.success(request,"Customer Details Succesfully updated")

			else:
				messages.error(request,get_error(enquiry_form))
				
				address_form = AddressForm()

				return render(request,'agent/enquiry/existing_enquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,})

		if action_mode == 'add_address':
			address_form = AddressForm(request.POST)

			if address_form.is_valid():
				address_form_save          = address_form.save(commit=False)
				address_form_save.customer = enquiry_user
				address_form_save.save()
				
				messages.success(request,"New Address Succesfully Added")

			else:
				messages.error(request,get_error(address_form))					

				enquiry_form = UserProfileForm(request.FILES or None,instance=enquiry_user)

				return render(request,'agent/enquiry/existing_enquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,})

		return redirect('agent:agent-existingenquiry',enquiry_id)

class AssignEvaluator(IsAgent,View):
	evaluation_formset_define    = formset_factory(EvaluationDetailsForm)
	def get(self,request,enquiry_id):
				
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

		return render(request,'agent/enquiry/assign_evaluator.html',{'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'enquiryid':enquiry_id,'evaluation_formset':self.evaluation_formset_define(form_kwargs={'enquiry_user_id':enquiry_id}),})

	def post(self,request,enquiry_id):
		evaluation_formset  = self.evaluation_formset_define(request.POST,form_kwargs={'enquiry_user_id':enquiry_id})

		action_mode    = request.POST.get('action_type')


		if action_mode == 'add':

			agent_notes  = request.POST.get('agent_notes')
			tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or 10000
			evaluation_no= 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+str(tracking_no+1)

			#Create New Evaluation
			new_evaluation = Evaluation.objects.create(evaluation_id=evaluation_no,tracking_no=tracking_no+1,call_attender=request.user,attender_notes=agent_notes,customer_id=enquiry_id)	

			#Save Evaluation Details
			if evaluation_formset.is_valid(): 

				for evaluation_form in evaluation_formset:
					if evaluation_form.is_valid():
						evaluation_form_save              = evaluation_form.save(commit=False)
						
						proposed_time                     = evaluation_form.cleaned_data['proposed_time']
						converted_proposed_time           = datetime.strptime(proposed_time,'%d/%m/%Y %I:%M %p')
						
						evaluation_form_save.proposed_time= converted_proposed_time
						evaluation_form_save.evaluation   = new_evaluation
						evaluation_form_save.save()

				messages.success(request,"Evaluation Details Succesfully Completed")

			else:
				messages.error(request,"An Error Occured")	
		
		return redirect('agent:agent-assignevaluator',enquiry_id)


class MakeQuatationBase(IsAgent,View):
	def get(self,request,enquiry_id):
		#create Main Evaluation
		tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or 10000
		evaluation_no= 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+str(tracking_no+1)

		try:
			evaluation = Evaluation.objects.create(tracking_no=tracking_no+1,evaluation_id=evaluation_no,customer_id=enquiry_id,call_attender=request.user)
		except:
			evaluation = None

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
	payment_track_formset_define = formset_factory(PaymentTrackForm)

	def get(self,request,enquiry_id,evaluation_id):
		enquiry_user    	  = UserProfile.objects.get(id=enquiry_id)
		
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

		return render(request,'agent/enquiry/quatationphase1.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,'payment_track_formset':self.payment_track_formset_define(),"allow_submit":allow_submit})	

	def post(self,request,enquiry_id,evaluation_id):
		payment_track_formset       = self.payment_track_formset_define(request.POST)
		
		payment_method = request.POST.get('payment_method')

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,quatation_status='PENDING')
		#SAVE payment breakdown details
		if payment_method == 'BREAKDOWN':
			if payment_track_formset.is_valid():
				for payment_track_form in payment_track_formset:
					if payment_track_form.is_valid():
						payment_track_form_save 			  = payment_track_form.save(commit=False)
						payment_track_form_save.evaluation_id = evaluation_id
						payment_track_form_save.save()
			else:
				messages.error(request,"An Error Occured")
				return redirect('agent:agent-makequatation1',enquiry_id,evaluation_id)
							
		messages.success(request,"Quatation Submitted Succesfully")		
		return redirect('agent:agentdash-board')

		
class MakeQuatationPhase2(IsAgent,View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	def get(self,request,evaluation_detail_id):

		evaluation_details = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=evaluation_detail_id)

		return render(request,'agent/enquiry/quatationphase2.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,})

	def post(self,request,evaluation_detail_id):

		service_formset       = self.service_formset_define(request.POST)
		evaluation_details    = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=evaluation_detail_id)
		if service_formset.is_valid() : 

			form_count = 0
			#create order					
			new_order = Order.objects.get_or_create(evaluation=evaluation_details.evaluation,order_no=evaluation_details.evaluation.evaluation_id,)	
				
			order_schedule_array          = []
			#Save Service Form
			for service_form in service_formset:
				
				if service_form.is_valid():
					service_form_save 					    = service_form.save(commit=False)
					service_form_save.evaluation_details_id = evaluation_detail_id
					service_form_save.save()


					#for updating cost details in evaluation details
					cost     = int(request.POST.get('form-'+str(form_count)+'-estimated_cost')) 
					discount = int(request.POST.get('form-'+str(form_count)+'-discount'))
					total    = int(request.POST.get('form-'+str(form_count)+'-total_cost'))

					#for creating cleaning schedules and corresponding cleanings

					cleaning_policy = request.POST.get('form-'+str(form_count)+'-cleaning_policy')
					start_time      = request.POST.get('form-'+str(form_count)+'-start_time')
					cleaning_hours  = request.POST.get('form-'+str(form_count)+'-cleaning_hours')

					if cleaning_policy == 'SUBSCRIPTION':
						tendative_dates = request.POST.get('form-'+str(form_count)+'-tendative_dates').split(',')
						
						for date in tendative_dates:
							start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
							end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours)) 
							
							order_schedule_array.append(OrderScheduler(order=new_order[0],evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=service_form_save))	
							

						updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')+cost*len(tendative_dates),discount=F('discount')+discount*len(tendative_dates),total_cost=F('total_cost')+total*len(tendative_dates),status='EVALUATED')
						updated_evaluation         = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')+cost*len(tendative_dates),discount=F('discount')+discount*len(tendative_dates),total_cost=F('total_cost')+total*len(tendative_dates))
					else:
						tendative_date  = request.POST.get('form-'+str(form_count)+'-tendative_date')	
						
						start_date_time = datetime.strptime(tendative_date+' '+start_time,'%d-%m-%Y %I:%M %p')
						end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours))

						order_schedule_array.append(OrderScheduler(order=new_order[0],evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=service_form_save))
						

						updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total,status='EVALUATED')
						updated_evaluation 		   = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')+cost,discount=F('discount')+discount,total_cost=F('total_cost')+total)	
			
			#bulk_create order schedules
			now = timezone.now()
			OrderScheduler.objects.bulk_create(order_schedule_array)
			created_schedules = OrderScheduler.objects.filter(order=new_order[0],created__gte=now)	
	

			#To Save Media
			medias = request.FILES.getlist('media')
			if not medias==['']:
				for media in medias:
					EvaluationMedia.objects.create(
					        evaluation_details_id=evaluation_detail_id,
					        media=media,
					        )

			messages.success(request,"Services Succesfully Added")

		else:
			if not service_formset.is_valid():
				messages.error(request,"An Error Occured")

			return render(request,'agent/enquiry/quatationphase2.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,})	

		return redirect('agent:agent-makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)
		


class AddFeedBack(IsAgent,View):
	def get(self,request):
		
		try:
			orders = Order.objects.filter(is_active=True,is_feedback_marked=False,)
		except:
			orders = None

		try:
			questions = Question.objects.filter(is_active=True).order_by('id')
		except:
			questions = None		
			
		return render(request,'agent/feedback/feedback_form.html',{'orders':orders,"questions":questions})

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

		investigation_form = InvestigationForm()
		
		return render(request,'agent/ticket/ticket_registration.html',{'investigation_form':investigation_form,'orders':orders,})		

	def post(self,request):
		order_id           = request.POST.get('order_id')
		investigation_form = InvestigationForm(request.POST)

		if investigation_form.is_valid(): 
			investigation_form_save            = investigation_form.save(commit=False)	
			investigation_form_save.assigned_by= request.user
			investigation_form_save.order_id   = order_id
			investigation_form_save.save()	

			messages.success(request,"Ticket Succesfully Rised")
		else:
			messages.error(request,get_error(investigation_form))

		return redirect('agent:agent-ticketregister')		