from django.shortcuts import render,redirect
from django.views import View
from django.forms import formset_factory,modelformset_factory
from django.http import HttpResponse,JsonResponse

from django.conf import settings
from bleach_crm_ps.permissions import IsEvaluator,IsAgentEvaluatorSalesAdmin
from bleach_crm_ps.utils import get_error

from django.db.models.functions import ExtractMonth,ExtractYear

import random
import string
import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast 
from django.db.models import Prefetch
from django.contrib import messages
from dateutil.relativedelta import relativedelta

from googletrans import Translator

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningSection,CleaningMethod,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,Reporting,ReportingMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory

from agent.forms import UserProfileForm,AddressForm
from evaluator.forms import MyEvaluationDetailsForm,QuatationServiceForm

import requests
# Create your views here.


#Username Random Generation
def generate_random_username(size=10, chars=string.ascii_uppercase + string.digits):
    
    username = ''.join(random.choice(chars) for n in range(size))

    
    try:
        UserProfile.objects.get(username=username)
        return generate_random_username(size=10, chars=string.ascii_uppercase + string.digits)
    except UserProfile.DoesNotExist:
        return username




class EvaluatorHome(IsEvaluator,View):
	def get(self,request):

		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)

		#Enquiry Details count
		try:
			enquiry = EvaluationDetails.objects.filter(is_active=True)
		except:
			enquiry	= None

		today_enquiry_count = enquiry.filter(proposed_time__gte=count_today_start,proposed_time__lt=count_today_end,evaluator=request.user).count()
		week_enquiry_count  = enquiry.filter(proposed_time__gte=count_today_end-timedelta(7),proposed_time__lt=count_today_end,evaluator=request.user).count()

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
		lastmonth_average_feedback		  = feedbacks.filter(response_date__gte=count_today_end-timedelta(60),response_date__lte=count_today_end-timedelta(30)).aggregate(Avg('rating'))['rating__avg']



		#sales amount
		# try:
		# 	invoices         = Invoice.objects.filter(is_active=True)
		# except:
		# 	invoices         = None

		# this_week_sales = invoices.filter(status='COMPLETED',created__date__gte=timezone.now().date()-timedelta(6)).aggregate(total=Sum('amount_paid'))['total']
		# last_week_sales = invoices.filter(status='COMPLETED',created__date__gte=timezone.now().date()-timedelta(13),created__date__lte=timezone.now().date()-timedelta(6)).aggregate(total=Sum('amount_paid'))['total']		
		# this_month_sales=invoices.filter(status='COMPLETED',created__month=timezone.now().month,created__year=timezone.now().year).aggregate(total=Sum('amount_paid'))['total']
		# last_month_sales=invoices.filter(status='COMPLETED',created__month=((timezone.now().date()-relativedelta(months=1)).month),created__year=timezone.now().year).aggregate(total=Sum('amount_paid'))['total']	
			
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
		
		#for not approved quatations cleaning in cleaning callendar
		try:
			calendar_notapprovedorder_schedules 	= OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end)))).order_by('start_at').select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(Q( Q(order__evaluation__quatation_status='PENDING')|Q(Q(order__evaluation__quatation_status='APPROVED')&Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0)) | Q(Q(order__evaluation__quatation_status='APPROVED')&Q(order__evaluation__payment_method='PREPAID')&Q(order__amount_paid=0)) )) 
		except:
			calendar_notapprovedorder_schedules 	= None

		try:
			sp_calendar_notapprovedorder_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(Q( Q(order__evaluation__quatation_status='PENDING')|Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='BREAKDOWN') & Q(order__preamount_paid = 0) ) | Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='PREPAID') & Q(order__amount_paid=0) ) ))
		except:
			sp_calendar_notapprovedorder_schedules = None

		try:
			spp_calendar_notapprovedorder_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start)))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(Q( Q(order__evaluation__quatation_status='PENDING')|Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='BREAKDOWN') & Q(order__preamount_paid = 0) ) | Q( Q(order__evaluation__quatation_status='APPROVED') & Q(order__evaluation__payment_method='PREPAID') & Q(order__amount_paid=0) ) ))
		except:
			spp_calendar_notapprovedorder_schedules = None

		#Evaluation details of each evaluator for evaluation table
		evaluation_calendar_date	= request.GET.get('evaluation_calendar_date')
		
		try:
			evaluation_date = datetime.strptime(evaluation_calendar_date,'%d-%m-%Y')
		except:
			evaluation_date = timezone.now().replace(tzinfo=None)
		
		evaluation_date_start     = evaluation_date.replace(hour=0,minute=0,second=0,microsecond=0)
		evaluation_date_end       = evaluation_date_start+timedelta(1)

		try:
			my_evaluations = EvaluationDetails.objects.filter(is_active=True,proposed_time__gte=evaluation_date_start,proposed_time__lte=evaluation_date_end,evaluator=request.user,address__isnull=False).order_by('proposed_time')
		except:
			my_evaluations = None	

		return render(request,'evaluator/home/home.html',{'today_follow_up_job_count':today_follow_up_job_count,'week_follow_up_job_count':week_follow_up_job_count,'month_average_feedback':month_average_feedback,'lastmonth_average_feedback':lastmonth_average_feedback,'today_enquiry_count':today_enquiry_count,'week_enquiry_count':week_enquiry_count,'today_cleaning_job_count':today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'spp_calendar_order_schedules':spp_calendar_order_schedules,'spp_calendar_followup_schedules':spp_calendar_followup_schedules,'schedule_date':schedule_date,'evaluation_date':evaluation_date,'my_evaluations':my_evaluations,"calendar_notapprovedorder_schedules":calendar_notapprovedorder_schedules,"sp_calendar_notapprovedorder_schedules":sp_calendar_notapprovedorder_schedules,"spp_calendar_notapprovedorder_schedules":spp_calendar_notapprovedorder_schedules,})

class ClientDetails(IsEvaluator,View):
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

		return render(request,'evaluator/client/clients.html',{"client_details":client_details,"search_query":search,"new_clients_count":new_clients_count,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_customertype":fil_customertype,"fil_status":fil_status})		
	

class ClientOrders(IsEvaluator,View):
	def get(self,request,client_id):

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None
	
		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'))
					
		#COUNT			
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()

		return render(request,"evaluator/client/client-page.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,})

class ClientOrderDetails(IsEvaluator,View):
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
					
				
		return render(request,"evaluator/client/order-page.html",{"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count})



class OrderDetails(IsEvaluator,View):
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
			evaluations = Evaluation.objects.filter(is_active=True,evaluation_details__evaluator=request.user).select_related('customer').filter(Q(Q(customer__name__icontains=search)|Q(customer__mobile_number__icontains=search)|Q(evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))
		else:
			evaluations = Evaluation.objects.filter(is_active=True,evaluation_details__evaluator=request.user).select_related('customer').order_by('-id').prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True),to_attr='evaluationorder')).annotate(order_in_progress_count=Count(Case(When( evaluation_order__order_status='ORDER_IN_PROGRESS',then=1),output_field=IntegerField())),order_closed_count=Count(Case(When( evaluation_order__order_status='ORDER_CLOSED',then=1),output_field=IntegerField())),approved_not_paid_count=Count(Case(When( Q( Q(quatation_status='APPROVED') & Q(Q(Q(payment_method='PREPAID')&~Q(evaluation_order__payment_status='COMPLETED'))|Q(Q(payment_method='BREAKDOWN')&Q(evaluation_order__preamount_paid=0))) ),then=1),output_field=IntegerField())))

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
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,evaluator=request.user),to_attr='evaluators_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_book_count=Count(Case(When( Q(count_evaluation_book_prefetch_filter & count_customer_address_prefetch_filter),then=1),output_field=IntegerField()))).filter(address_book_count__gt=0)
			print("both")
		elif evaluation_book_prefetch_filter and not customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,evaluator=request.user),to_attr='evaluators_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type').filter(evaluation_book_prefetch_filter),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(book_count=Count(Case(When( count_evaluation_book_prefetch_filter,then=1),output_field=IntegerField()))).filter(book_count__gt=0)
			print("book only")
		elif not evaluation_book_prefetch_filter and customer_address_prefetch_filter:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,evaluator=request.user),to_attr='evaluators_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').filter(customer_address_prefetch_filter).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation')).annotate(address_count=Count(Case(When( count_customer_address_prefetch_filter,then=1),output_field=IntegerField()))).filter(address_count__gt=0)
			print("address only")
		else:
			evaluations = evaluations.prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,evaluator=request.user),to_attr='evaluators_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True,status='EVALUATED'),to_attr='completed_evaluations'),Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).select_related('service_type'),to_attr='evaluation_book')),to_attr='details_evaluation'))
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

		return render(request,'evaluator/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,"fil_payment_policy":fil_payment_policy})		


class ResourceManagement(IsEvaluator,View):
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
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))&Q(name__icontains=search)).prefetch_related('leave_staff').annotate(leave=Case( When( Q(Q(leave_staff__leave_date__gte=workers_date_start.date())&Q(leave_staff__leave_date__lt=workers_date_end.date())),then=True),default=False,output_field=BooleanField()))
			except:
				workers =  None
		else:
			try:
				workers =  UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).prefetch_related('leave_staff').annotate(leave=Case( When( Q(Q(leave_staff__leave_date__gte=workers_date_start.date())&Q(leave_staff__leave_date__lt=workers_date_end.date())),then=True),default=False,output_field=BooleanField()))
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

		return render(request,'evaluator/resource/resources.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,"staffs":staffs,"fil_staff":fil_staff,"fil_endingtime":fil_endingtime,"fil_startingtime":fil_startingtime,'service_type':service_type})

class TicketDetails(IsEvaluator,View):
	def get(self,request):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			investigators = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='SENIORTEAMLEADER')|Q(user_type='TEAMINCHARGE')|Q(user_type='EVALUATOR'))))	
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




		#followup cleaning count	
		no_of_entries = request.GET.get('no_of_entries')		
		if not no_of_entries:
			no_of_entries = 20

		try:
			follow_up_cleaning_count = FollowUpScheduler.objects.filter(is_active=True,work_status='FOLLOW_UP_CLEANING_FULFILLED').count()
		except:
			follow_up_cleaning_count = 0

		#PAGINATION TICKETS		
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

		return render(request,'evaluator/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})

class TicketAdvanced(IsEvaluator,View):
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

		return render(request,'evaluator/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})

class NewEnquiry(IsEvaluator,View):
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

		return render(request,'evaluator/enquiry/newenquiry.html',{'enquiry_form':enquiry_form,'address_formset':self.address_formset_define(),'customer_info':customer_info,'governorates':governorates,'locations':locations})

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
					address_form_save = address_form.save(commit=False)
					address_form_save.currently_active  = True
					address_form_save.customer = enquiry_form_save

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

					address_form.save()
					
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

			return render(request,'evaluator/enquiry/newenquiry.html',{'enquiry_form':enquiry_form,'address_formset':address_formset,'governorates':governorates,'locations':locations})					

		redirection = request.POST.get('redirect_to')	
		
		if redirection == 'assign_evaluator':
			return redirect('evaluator:evaluator-makeevaluation',enquiry_form_save.id)	
		elif redirection == 'quatation':
			return redirect('evaluator:evaluator-makequatation',enquiry_form_save.id)
		else:
			return redirect('evaluator:existingenquiry',enquiry_form_save.id)


class ExistingEnquiry(IsEvaluator,View):
	
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
		
		return render(request,'evaluator/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,'addresses':addresses,'enquiry_user':enquiry_user,'governorates':governorates,'locations':locations, "active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})

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

				try:
					locations = AreaType.objects.filter(is_active=True)
				except:
					locations = None
				
				return render(request,'evaluator/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,'governorates':governorates,'locations':locations})			


		if action_mode == 'add_address':
			address_form = AddressForm(request.POST)

			if address_form.is_valid():
				address_form_save          = address_form.save(commit=False)
				address_form_save.customer = enquiry_user
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

				return render(request,'evaluator/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,})					

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
				is_street = street_text.find("street")

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

				return render(request,'evaluator/enquiry/existingenquiry.html',{'enquiry_form':enquiry_form,'address_form':address_form,'enquiryid':enquiry_id,})

		return redirect('evaluator:evaluator-existingenquiry',enquiry_id)


class MakeEvaluation(IsEvaluator,View):
	def get(self,request,enquiry_id):
		
		tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

		current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
		
		if current_blc_starting == int(str(tracking_no)[:6]):
			new_tracking_no = int(tracking_no)+1
			evaluation_no   = 'BLC'+str(new_tracking_no)
		else:
			evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
			tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

		#Create New Evaluation
		new_evaluation = Evaluation.objects.create(evaluation_id=evaluation_no,tracking_no=int(tracking_no)+1,call_attender=request.user,customer_id=enquiry_id,quatation_expiry_date=timezone.now()+timedelta(14))
		
		return redirect('evaluator:evaluator-assignevaluator',enquiry_id,new_evaluation.id)


class AssignEvaluator(IsEvaluator,View):
	def get(self,request,enquiry_id,evaluation_id):

		evaluation_form 		    = MyEvaluationDetailsForm(enquiry_user_id=enquiry_id,evaluation_id=evaluation_id,)
				
		#Evaluation details of each evaluator for evaluation table
		evaluation_calendar_date	= request.GET.get('evaluation_calendar_date')
		
		try:
			evaluation_date = datetime.strptime(evaluation_calendar_date,'%d-%m-%Y')
		except:
			evaluation_date = timezone.now()
		
		evaluation_details		  = UserProfile.objects.filter(is_active=True,id=request.user.id).prefetch_related(Prefetch('evaluator_evaluation',queryset=EvaluationDetails.objects.filter(is_active=True,proposed_time__contains=evaluation_date.date()),to_attr='evaluation_details'))
		
		assigned_addresses = EvaluationDetails.objects.filter(is_active=True,evaluation_id=evaluation_id).values_list('address')
		active_addresses   = Address.objects.filter(is_active=True,customer_id=enquiry_id,currently_active=True).exclude(id__in=assigned_addresses)

		return render(request,'evaluator/enquiry/assign_evaluator.html',{'evaluation_details':evaluation_details,'evaluation_date':evaluation_date,'enquiryid':enquiry_id,'evaluation_id':evaluation_id,'evaluation_form':evaluation_form,"active_addresses":active_addresses,})

	def post(self,request,enquiry_id,evaluation_id):
		evaluation_form  = MyEvaluationDetailsForm(enquiry_user_id=enquiry_id,evaluation_id=evaluation_id,data=request.POST)		

		action_mode      = request.POST.get('action_type')


		if action_mode == 'add':

			evaluation = Evaluation.objects.filter(id=evaluation_id).first()
			if evaluation.customer.gender == 'MALE':
				title = 'Mr.'
			else:
				title = 'Ms.'

			#Save Evaluation Details
			if evaluation_form.is_valid():
				evaluation_form_save              = evaluation_form.save(commit=False)
				
				proposed_date                     = request.POST.get('proposed_date')
				proposed_time                     = request.POST.get('proposed_time')
				converted_proposed_time           = datetime.strptime(proposed_date+" "+proposed_time,'%d-%m-%Y %I:%M %p')
				
				evaluation_form_save.proposed_time   = converted_proposed_time
				evaluation_form_save.evaluation_id   = evaluation_id
				evaluation_form_save.evaluator       = request.user
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

						message = "Dear Customer , We have confirmed your Evaluation Appointment. "+ title +" "+evaluation_form_save.evaluator.name+" will be visiting you on "+str(evaluation_form_save.proposed_time)+" at  "+separator.join(address_list)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."

						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

					else:

						message = "عزيزينا العميل تم تأكيد موعد المعاينة الخاص بك.  "+ title +" "+evaluation_form_save.evaluator.name+" سيقوم بالزيارة في "+str(evaluation_form_save.proposed_time)+" في "+separator.join(address_list)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+  شكراً لاختياركم بليتش لخدمات التنظيف"

						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
					
					headers = {
						'cache-control': "no-cache"
					}

					response = requests.request("GET", url, headers=headers, params=querystring)

					print(response.text,"respo")
					print(str(evaluation_form_save.proposed_time))
					print(evaluation_form_save.evaluation.customer.mobile_number,"mobile")
				else:
					pass

			else:
				messages.error(request,get_error(evaluation_form))	
		
		#For Date in Redirection
		selected_date = request.GET.get('evaluation_calendar_date') or ''
		
		return redirect('/evaluator/assignevaluator/'+enquiry_id+'/'+evaluation_id+'?evaluation_calendar_date='+selected_date)


class MakeQuatationBase(IsEvaluator,View):
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

		try:
			evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no,customer_id=enquiry_id,call_attender=request.user,quatation_expiry_date=timezone.now()+timedelta(14))
		except:
			evaluation = None

		#create evaluation details
		try:
			addresses = Address.objects.filter(is_active=True,customer_id=enquiry_id,currently_active=True)
		except:
			addresses = None

		evaluation_details_array = []	
		for address in addresses:
			evaluation_details_array.append(EvaluationDetails(evaluation=evaluation,address=address,evaluator=request.user))
		EvaluationDetails.objects.bulk_create(evaluation_details_array)	

		return redirect('evaluator:evaluator-makequatation1',enquiry_id,evaluation.id)	

class MakeQuatationPhase1(IsEvaluator,View):

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

		return render(request,'evaluator/enquiry/phase1quatation.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit})	

	def post(self,request,enquiry_id,evaluation_id):
		
		payment_method = request.POST.get('payment_method')
		before_cleaning_amount	= float(request.POST.get('before_cleaning_amount')or 0.000)
		after_cleaning_amount	= float(request.POST.get('after_cleaning_amount')or 0.000)

		#for backbutton safety delete subscription
		evaluation      = Evaluation.objects.get(id=evaluation_id)
		if evaluation.payment_method == 'POSTPAIDSUBSCRIPTION' or evaluation.payment_method == 'PREPAIDSUBSCRIPTION':
			OrderScheduler.objects.filter(order__evaluation__id=evaluation_id).update(payment_subscription=None)
			PaymentSubscriptionDetails.objects.filter(order__evaluation__id=evaluation_id).delete()

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,quatation_status='PENDING',before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)

		#sms integration
		evaluation = Evaluation.objects.filter(id=evaluation_id,is_active=True).first()
		evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
		evaluationbook = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).first()
		language = evaluation.customer.sms_preference

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

			print(response.text,"respo")
		else:
			pass

		return redirect('evaluator:evaluatordash-board')

		
class MakeQuatationPhase2(IsAgentEvaluatorSalesAdmin,View):
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

		return render(request,'evaluator/enquiry/phase2quatation.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,})

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
				return render(request,'evaluator/enquiry/phase2quatation.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,})	
			if request.user.user_type == 'AGENT':
				return render(request,'agent/enquiry/phase2quatation.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'area_types':area_types,'service_types':service_types,})
	
		if request.user.user_type == 'EVALUATOR':
			return redirect('evaluator:evaluator-makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)
		if request.user.user_type == 'AGENT':
			return redirect('agent:agent-makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)

class MakeQuatationPhase2Edit(IsAgentEvaluatorSalesAdmin,View):
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

		return render(request,'evaluator/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

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
			if request.user.user_type == 'SALESADMIN':
				return render(request,'salesadmin/enquiry/phase2quatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

		if request.user.user_type == 'EVALUATOR':
			return redirect('evaluator:evaluator-makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)
		if request.user.user_type == 'AGENT':
			return redirect('agent:agent-makequatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)
		if request.user.user_type == 'SALESADMIN':
			return redirect('bleach_salesadmin:salesadmin-makequatation1edit',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)


class MakeAssignedQuatationPhase1(IsEvaluator,View):

	def get(self,request,enquiry_id,evaluation_id):
		enquiry_user    	  = UserProfile.objects.get(id=enquiry_id)
		
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

		return render(request,'evaluator/enquiry/phase1assignedquatation.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit})	

	def post(self,request,enquiry_id,evaluation_id):
		
		action = request.POST.get('action_type',None)
		if action == 'cancel' :
			evaluation_detail_id =request.POST.get('evaluation_detail')
			cancel_reason = request.POST.get('cancellation_reason')
			print(evaluation_detail_id,"evd")
			evaluation_detail = EvaluationDetails.objects.filter(id=int(evaluation_detail_id)).first()
			evaluation_detail.status = 'CANCELLED'
			evaluation_detail.evaluation_cancel_reason = cancel_reason
			evaluation_detail.save()
			messages.success(request,"Evaluation Cancelled !!")
			return redirect('evaluator:evaluator-makeassignedquatation1', enquiry_id,evaluation_id)

		
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

			if language == 'ENGLISH':
				print(str(evaluation.id),str(evaluation.evaluation_id),str(evaluation.total_cost),str(evaluation.quatation_expiry_date),str(evaluation.customer.username),str(evaluation.tracking_no),"trerr")

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
												
		messages.success(request,"Quatation Submitted Succesfully")		
		return redirect('evaluator:evaluatordash-board')

		
class MakeAssignedQuatationPhase2(IsEvaluator,View):
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

		return render(request,'evaluator/enquiry/phase2assignedquatation.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,})

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
			
			return render(request,'evaluator/enquiry/phase2assignedquatation.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,})	

		return redirect('evaluator:evaluator-makeassignedquatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)		

class MakeAssignedQuatationPhase2Edit(IsEvaluator,View):
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

		return render(request,'evaluator/enquiry/phase2assignedquatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

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
			
			return render(request,'evaluator/enquiry/phase2assignedquatationedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})	

		return redirect('evaluator:evaluator-makeassignedquatation1',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)


class MakeQuatationPhase1Edit(IsEvaluator,View):

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

		return render(request,'evaluator/enquiry/phase1quatationedit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit})	

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
		return redirect('evaluator:evaluatordash-board')

class AddNewService(IsAgentEvaluatorSalesAdmin,View):
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

		return render(request,'evaluator/enquiry/addservice.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections})	

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

			return render(request,'evaluator/enquiry/addservice.html',{'service_formset':service_formset,'evaluation_details':evaluation_details,'area_types':area_types,'service_types':service_types,})		

		if edit_type == 'duplicate':
			if request.user.user_type == 'EVALUATOR':
				return redirect('evaluator:evaluator-makequatation2duplicateedit',evaluation_details.id)
			if request.user.user_type == 'AGENT': 
				return redirect('agent:agent-makequatation2duplicateedit',evaluation_details.id)
		
		elif edit_type == 'edit': 
			return redirect('evaluator:evaluator-makequatation2edit',evaluation_details.id)

		else:
			if request.user.user_type == 'EVALUATOR':
				return redirect('evaluator:evaluator-makeassignedquatation2edit',evaluation_details.id)
			if request.user.user_type == 'AGENT' or request.user.user_type == 'SALESADMIN':
				return redirect('evaluator:evaluator-makequatation2edit',evaluation_details.id)


class MakeQuatationPhase2Delete(IsEvaluator,View):
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
			return redirect('evaluator:evaluator-orders')

		return redirect('evaluator:evaluator-makequatation1edit',enquiry_id,evaluation_id)
		

def deleteservice(request,book_id,evaluation_detail_id):
	
	service = EvaluationBook.objects.get(id=book_id)
	evaluation = service.evaluation_details.evaluation
	order = Order.objects.get(evaluation__id=evaluation.id)
	evaluationdetails = service.evaluation_details

	#evaluation amount fix
	evaluation.estimated_cost = float(evaluation.estimated_cost) - float(service.total_cost)
	evaluation.total_cost     = float(evaluation.estimated_cost) - float(evaluation.discount)
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
	return redirect('evaluator:evaluator-makeassignedquatation2edit',evaluation_detail_id)

def deletesection(request,url_type,section_id,evaluation_detail_id):
	print(url_type,section_id,evaluation_detail_id,"ids47")
	section = EvaluationBookSection.objects.get(id=section_id)
	
	service = section.evaluation_book
	evaluation = service.evaluation_details.evaluation
	order = Order.objects.get(evaluation__id=evaluation.id)
	evaluationdetails = service.evaluation_details

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

	if url_type == 'assigned':
		return redirect('evaluator:evaluator-makeassignedquatation2edit',evaluation_detail_id)
	else:
		return redirect('evaluator:evaluator-makequatation2edit',evaluation_detail_id)

#duplicate re-order
class MakeQuatationDuplicate(IsEvaluator,View):
	
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
				new_duplicate_evaluation_details = EvaluationDetails.objects.create(evaluator=request.user,evaluation=new_evaluation,address=duplicate_evaluation.address,estimated_cost=duplicate_evaluation.estimated_cost,discount=duplicate_evaluation.discount,total_cost=duplicate_evaluation.total_cost,status=duplicate_evaluation.status)
				
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

		return redirect('evaluator:evaluator-makequatation1duplicateedit',new_evaluation.customer.id,new_evaluation.id,)

class MakeQuatationPhase1DuplicateEdit(IsEvaluator,View):	

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

		return render(request,'evaluator/enquiry/phase1quatationduplicateedit.html',{'enquiry_user':enquiry_user,'evaluation':evaluation,'evaluation_details':evaluation_details,"allow_submit":allow_submit,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,})	

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

				message = "Dear Customer, Please find the Revised Quotation against the order number "+str(evaluation.evaluation_id)+"  here "+smsurl+" . Order Number : "+ str(evaluation.evaluation_id) +". Service Type(s) : "+ evaluationbook.service_type.name +", Address(s) : "+ separator.join(address_list) +", Cost : "+ str(evaluation.total_cost) +", Due Date : "+ str(evaluation.quatation_expiry_date) +". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

			else:
				message = "عزيزنا العميل نرجوا الاطلاع على عرض السعر المعدّل للطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط "+smsurl+" .رقم الطلب: "+ str(evaluation.evaluation_id) +"الخدمة: "+ evaluationbook.service_type.name +"العنوان: "+ separator.join(address_list) +"السعر: "+ str(evaluation.total_cost) +" KDتاريخ الخدمة: "+ str(evaluation.quatation_expiry_date) +"لأي استفسارات يمكنكم التواصل معنا على . 9651882707+  شكراً لاختياركم بليتش لخدمات التنظيف"
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

			headers = {
				'cache-control': "no-cache"
			}

			response = requests.request("GET", url, headers=headers, params=querystring)

			print(response.text,"respo")
		else:
			pass

		return redirect('evaluator:evaluatordash-board')




class MakeQuatationPhase2DuplicateEdit(IsAgentEvaluatorSalesAdmin,View):
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

		return render(request,'evaluator/enquiry/phase2quatationduplicateedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})

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
							updated_evaluation         = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=total) #F('total_cost')-very_old_book.total_cost
							update_order               = Order.objects.filter(is_active=True,evaluation__id=evaluation_details.evaluation.id).update(total_amount=F('total_amount')+total,remining_amount=F('remining_amount')+total)							
						else:
							tendative_dates  = request.POST.get('form-'+str(form_count)+'-tendative_date').split(',')

							for date in tendative_dates:
								print(date)
								start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
								end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))
								order_schedule_array.append(OrderScheduler(order=old_order,status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,customer_address=evaluation_details.address,order_scheduler_book=old_book))

							updated_evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluation_detail_id).update(evaluator=evaluation_details.evaluator,estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=F('total_cost')-very_old_book.total_cost+total,status='EVALUATED')
							updated_evaluation 		   = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).update(estimated_cost=F('estimated_cost')-very_old_book.estimated_cost+cost,discount=F('discount')-very_old_book.discount+discount,total_cost=total) #F('total_cost')-very_old_book.total_cost
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

			if request.user.user_type == 'EVALUATOR':
				return render(request,'evaluator/enquiry/phase2quatationduplicateedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})
			elif request.user.user_type == 'AGENT':
				return render(request,'agent/enquiry/phase2quatationduplicateedit.html',{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_types':service_types,'area_types':area_types,'cleaning_sections':cleaning_sections,})
		

		if request.user.user_type == 'EVALUATOR':
			return redirect('evaluator:evaluator-makequatation1duplicateedit',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)
		elif request.user.user_type == 'AGENT':
			return redirect('agent:agent-makequatation1duplicateedit',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)
		elif request.user.user_type == 'SALESADMIN':
			return redirect('bleach_salesadmin:salesadmin-makequatation1duplicateedit',evaluation_details.evaluation.customer.id,evaluation_details.evaluation.id)

class EvaluatorPaymentEdit(IsEvaluator,View):

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

		return redirect('evaluator:evaluator-client-orderdetails',order.id)