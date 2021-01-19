from django.shortcuts import render,redirect
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsQualityControll
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
from googletrans import Translator

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote,EvaluationMedia,ServiceType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp,FollowUpSection,FollowUpSectionKeynote,Investigation,InvestigationMedia,Reporting,ReportingMedia,PaybackDiscount,PaybackDiscountDetails,PaybackDiscountDetailsMedia,BuybackPromocodeGift,BuybackPromocodeGiftDetails,BuybackPromocodeGiftDetailsMedia
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from senior_team_leader.forms import CleaningTeamAssignForm,FollowupTeamAssignForm

from django.forms import formset_factory,modelformset_factory
from evaluator.forms import EvaluationDetailsForm,QuatationServiceForm
# Create your views here.

class QcHome(IsQualityControll,View):
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

		
		#cleaning schedule & followup schedule for cleaning calendar			
		cleaning_calendar_date	= request.GET.get('cleaning_calendar_date')
		
		try:
			schedule_date = datetime.strptime(cleaning_calendar_date,'%d-%m-%Y')
		except:
			schedule_date = timezone.now().replace(tzinfo=None)

		schedule_date_start = schedule_date.replace(hour=0,minute=0,second=0,microsecond=0)
		schedule_date_end   = schedule_date_start+timedelta(1)	

		try:
			calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).order_by('start_at').select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).order_by('start_at').filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(Q(order__evaluation__payment_method='PREPAIDSUBSCRIPTION')&Q(payment_subscription__is_paid=True)) | Q(Q(order__evaluation__payment_method='POSTPAIDSUBSCRIPTION')&Q(Q(payment_subscription__is_paid=True)|Q(payment_subscription__isnull=True))) ))
		except:
			calendar_order_schedules = None

		try:
			calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(end_at__lte=schedule_date_end))&Q(status='CONFIRMED'))).order_by('start_at').select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			calendar_followup_schedules = None
	
		try:
			sp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_teams')).filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(Q(order__evaluation__payment_method='PREPAIDSUBSCRIPTION')&Q(payment_subscription__is_paid=True)) | Q(Q(order__evaluation__payment_method='POSTPAIDSUBSCRIPTION')&Q(Q(payment_subscription__is_paid=True)|Q(payment_subscription__isnull=True))) ))
		except:
			sp_calendar_order_schedules = None

		try:
			sp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(start_at__gte=schedule_date_start)&Q(start_at__lt=schedule_date_end)&Q(end_at__gt=schedule_date_end))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address').prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True),to_attr='followup_teams'))
		except:
			sp_calendar_followup_schedules = None							

		try:
			spp_calendar_order_schedules = OrderScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('order__evaluation__customer','customer_address','order_scheduler_book').filter(order__evaluation__quatation_status='APPROVED').filter(Q( Q(Q(order__payment_status='COMPLETED')|~Q(order__preamount_paid = 0)) | Q(order__evaluation__payment_method='POSTPAID') | Q(Q(order__evaluation__payment_method='PREPAIDSUBSCRIPTION')&Q(payment_subscription__is_paid=True)) | Q(Q(order__evaluation__payment_method='POSTPAIDSUBSCRIPTION')&Q(Q(payment_subscription__is_paid=True)|Q(payment_subscription__isnull=True))) ))
		except:
			spp_calendar_order_schedules = None

		try:
			spp_calendar_followup_schedules = FollowUpScheduler.objects.filter(Q(Q(Q(end_at__gt=schedule_date_start)&Q(end_at__lte=schedule_date_end)&Q(start_at__lt=schedule_date_start))&Q(status='CONFIRMED'))).select_related('follow_up__investigation__order__evaluation__customer','customer_address')
		except:
			spp_calendar_followup_schedules = None


		#Investigation tasks
		investigation_to_date         = (timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)).replace(tzinfo=None)

		try:	
			investigations  = Investigation.objects.filter(is_active=True,investigator=request.user,check_out=None).select_related('order__evaluation__customer','order_schedule__customer_address__area','order_schedule__order_scheduler_book').prefetch_related(Prefetch('order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team_details'))
		except:
			investigations  = 	None

		#add days left
		for investigation in investigations:
			investigation.days_left = (timezone.now()-investigation.scheduled_at).days

		#buybackgiftpromos		
		approved_buybackgiftpromos = Investigation.objects.filter(is_buybackgiftpromo_approved=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True),to_attr='followup'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.select_related('investigation').filter(investigation__is_buybackgiftpromo_approved=False,is_active=True),to_attr='buybackpromocodegifts'))
		#add days left
		for ticket in approved_buybackgiftpromos:
			ticket.days_left = (timezone.now()-ticket.scheduled_at).days

		return render(request,'qualitycontroll/home/home.html',{'investigations':investigations,"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,'calendar_order_schedules':calendar_order_schedules,'calendar_followup_schedules':calendar_followup_schedules,'sp_calendar_order_schedules':sp_calendar_order_schedules,'sp_calendar_followup_schedules':sp_calendar_followup_schedules,'spp_calendar_order_schedules':spp_calendar_order_schedules,'spp_calendar_followup_schedules':spp_calendar_followup_schedules,'schedule_date':schedule_date,"approved_buybackgiftpromos":approved_buybackgiftpromos})

class OrderDetails(IsQualityControll,View):
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
					case1 = Q(approved_not_paid_count__gte=1)
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

		return render(request,'qualitycontroll/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"service_types":service_types,"fil_governorate":fil_governorate,"fil_area":fil_area,"fil_status":fil_status,"fil_cleaning_policy":fil_cleaning_policy,"fil_service_type":fil_service_type,})

class ClientOrderDetails(IsQualityControll,View):
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


		return render(request,"qualitycontroll/client/order-page.html",{"order":order,"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"average_feedback":average_feedback,})

class ClientOrders(IsQualityControll,View):
	def get(self,request,client_id):

		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		orders = Order.objects.filter(evaluation__customer_id=client_id).select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(total_cleaners=Sum('evaluation__evaluation_details__evaluation_book_evaluation_details__number_of_cleaners'))

		#COUNT
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()

		return render(request,"qualitycontroll/client/client-page.html",{"client_details":client_details,"orders":orders,"active_orders_count":active_orders_count,})

class ResourceManagement(IsQualityControll,View):
	def get(self,request):

		try:
			staffs = UserProfile.objects.filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER')))
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
			total_workers = UserProfile.objects.filter(is_active=True).filter(Q(Q(user_type='TEAMLEADER')|Q(user_type='CLEANER'))).count()
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

		#filters
		filters=[]
		if fil_staff:
			case1 = Q(user_type=fil_staff)
			filters.append(case1)

		if fil_staff:
			filters         = functools.reduce(operator.and_,filters)
			workers_details = workers_details.filter(filters)

		return render(request,'qualitycontroll/resource/resource_management.html',{"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"workers_details":workers_details,"workers_date":workers_date,"search_query":search,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_date":today_date,"weekstart_date":weekstart_date,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,"staffs":staffs,"fil_staff":fil_staff,"fil_minhours":fil_minhours,"fil_maxhours":fil_maxhours,"staff_type":fil_staff})

class TicketDetails(IsQualityControll,View):
	def get(self,request):

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			investigators = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='SENIORTEAMLEADER')|Q(user_type='TEAMLEADER')|Q(user_type='EVALUATOR'))))	
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

		follow_ups_count = FollowUp.objects.filter(Q(is_active=True)&Q(Q(status='TICKET_RISED')|Q(status='INVESTIGATOR_APPRVED')|Q(status='FOLLOWUP_IN_PROGRESS'))).count()


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

		return render(request,'qualitycontroll/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})		

class TicketAdvanced(IsQualityControll,View):
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

		return render(request,'qualitycontroll/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})




class InvestigationTask(IsQualityControll,View):
	def get(self,request,investigation_id):
		
		try:
			investigation_details = Investigation.objects.select_related('order_schedule__customer_address__area','order_schedule__order_scheduler_book__service_type','order_schedule__evaluation_details__evaluator','investigator','order__evaluation__customer','order__evaluation__call_attender').prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True),to_attr='followup'),Prefetch('reporting_investigation',queryset=Reporting.objects.filter(is_active=True),to_attr='internalreport'), Prefetch('paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True),to_attr='paybackdiscount'),Prefetch('buybackpromocodegift_investigation',queryset=BuybackPromocodeGift.objects.filter(is_active=True),to_attr='buybackpromocodegift'),Prefetch('order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_teams')).get(id=investigation_id)
			orderschedules_count = OrderScheduler.objects.filter(is_active=True,order_scheduler_book__id=investigation_details.order_schedule.order_scheduler_book.id).count()
		except:
			orderschedules_count = 1
			investigation_details = None

		

		follow_up_scheduler = FollowUpScheduler.objects.filter(is_active=True,follow_up__investigation__id=investigation_id).first()
		if follow_up_scheduler:
			follow_up_scheduler_exists = True
		else:
			follow_up_scheduler_exists = False

		#save checkin_time
		investigation_details.check_in = timezone.now()
		investigation_details.save()

		return render(request,'qualitycontroll/ticket/investigation.html',{'investigation_details':investigation_details,"followup_scheduler_exists":follow_up_scheduler_exists,"orderschedules_count":orderschedules_count})

	def post(self,request,investigation_id):

		form_action = request.POST.get('action')
		if form_action == "followup":
			return redirect('quality-control:follow-up', investigation_id)
		if form_action == "discount":
			return redirect('quality-control:cash-back', investigation_id)
		if form_action == "gift":
			return redirect('quality-control:buy-back-promo-code', investigation_id)
		if form_action == "internal":
			return redirect('quality-control:internal-report',investigation_id)
		
		return redirect('quality-control:investigation', investigation_id)

class Followup(IsQualityControll,View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	def get(self,request,investigation_id):
		investigation = Investigation.objects.get(is_active=True,id=int(investigation_id))
		print(investigation.order_schedule.evaluation_details.id,"evs")
		evaluation_details = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=investigation.order_schedule.evaluation_details.id)

		service_type = investigation.order_schedule.order_scheduler_book.service_type
		
		# followup status change
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status = 'FOLLOWUP_IN_PROGRESS'
		follow_up.save()

		return render(request,"qualitycontroll/ticket/follow-up.html",{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_type':service_type})

	def post(self,request,investigation_id):
		investigation = Investigation.objects.get(is_active=True,id=int(investigation_id))
		evaluation_details 	  = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=investigation.order_schedule.evaluation_details.id)

		followup_schedule_array          = []

		total_cost	= request.POST.get('total_cost')
		no_of_cleaners = request.POST.get('number_of_cleaners')
		cleaning_hours = request.POST.get('cleaning_hours')
		
		tendative_date = request.POST.get('tendative_date').split(',')

		tendative_time = request.POST.get('tendative_time')

		Investigation.objects.filter(id=investigation_id).update(is_followup_approved=True,check_out=timezone.now(),notes=request.POST.get('notes'))
		
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status         = 'FOLLOWUP_IN_PROGRESS'
		follow_up.no_of_cleaners = no_of_cleaners
		follow_up.cleaning_hours = cleaning_hours
		follow_up.total_cost = total_cost
		follow_up.save()
		
		for date in tendative_date:
			print(date)
			start_date_time = datetime.strptime(date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
			end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))
			followup_schedule_array.append(FollowUpScheduler(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address))
		# follow_up_scheduler = FollowUpScheduler.objects.create(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address)
		
		
		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				InvestigationMedia.objects.create(
				        investigation_id=investigation_id,
				        media=media,
				        )

		#to save sections
		no_of_sections         = int(request.POST.get('section_counter'))
		section_array          = []
		for i in range(no_of_sections):
			section_name  = request.POST.get('section'+str(i))
			category      = request.POST.get('category'+str(i))
			dirt_level    = request.POST.get('dirt_level'+str(i))
			quantity      = request.POST.get('quantity'+str(i))
			size          = request.POST.get('size'+str(i))
			unit          = request.POST.get('unit'+str(i))
			age           = request.POST.get('age'+str(i))
			floor         = request.POST.get('floor'+str(i))
			apartment     = request.POST.get('apartment'+str(i))
			room          = request.POST.get('room'+str(i))
			wall_type     = request.POST.get('walltype'+str(i))
			ceiling_type  = request.POST.get('ceilingtype'+str(i))
			floor_type    = request.POST.get('floortype'+str(i))
			material      = request.POST.get('material'+str(i))
			colour        = request.POST.get('colour'+str(i))
			cause_of_stain=request.POST.get('staincause'+str(i))
			section_cost  = request.POST.get('sectioncost'+str(i))

			try:
				section_name_arabic = Translator().translate(section_name,src='en', dest='ar').text
			except:
				section_name_arabic = section_name
			
			section = FollowUpSection.objects.create(follow_up=follow_up,section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=1,section_net_cost=section_cost)

			#to save keynotes
			try:
				no_of_keynotes = int(request.POST.get('section'+str(i)+'-keynote_counter'))
			except:
				no_of_keynotes = None

			keynote_array = []
			if no_of_keynotes:
				for j in range(no_of_keynotes):
					keynote = request.POST.get('section'+str(i)+'_keynote'+str(j))
					quantity= request.POST.get('section'+str(i)+'_quantity'+str(j))
					if keynote and quantity:
						keynote_array.append(FollowUpSectionKeynote(followup_section=section,sub_area=keynote,quantity=quantity))
				#bulk_create keynote
				FollowUpSectionKeynote.objects.bulk_create(keynote_array)

		FollowUpScheduler.objects.bulk_create(followup_schedule_array)

		messages.success(request,"Follow Up Cleaning Succesfully Added")

		return redirect('quality-control:investigation', investigation_id)

class FollowupEdit(IsQualityControll,View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	def get(self,request,investigation_id):
		investigation = Investigation.objects.get(is_active=True,id=int(investigation_id))
		print(investigation.order_schedule.evaluation_details.id,"evs")
		evaluation_details = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=investigation.order_schedule.evaluation_details.id)

		service_type = investigation.order_schedule.order_scheduler_book.service_type

		followupscheduler = FollowUpScheduler.objects.filter(follow_up__investigation__id = int(investigation_id),is_active=True)
		
		# followup status change
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status = 'FOLLOWUP_IN_PROGRESS'
		follow_up.save()
		
		followup_sections = FollowUpSection.objects.filter(follow_up__investigation__id=int(investigation_id),is_active=True).prefetch_related(Prefetch('keynotesectionsfollowup',queryset=FollowUpSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'))

		return render(request,"qualitycontroll/ticket/follow-up-edit.html",{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_type':service_type,"followupscheduler":followupscheduler,"followupsections":followup_sections})

	def post(self,request,investigation_id):
		investigation = Investigation.objects.get(is_active=True,id=int(investigation_id))
		evaluation_details 	  = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=investigation.order_schedule.evaluation_details.id)

		followup_schedule_array          = []

		total_cost	   = request.POST.get('total_cost')
		no_of_cleaners = request.POST.get('number_of_cleaners')
		cleaning_hours = request.POST.get('cleaning_hours')
		
		tendative_date = request.POST.get('tendative_date').split(',')
		tendative_time = request.POST.get('tendative_time')
		# start_date_time = datetime.strptime(tendative_date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
		# end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours))

		Investigation.objects.filter(id=investigation_id).update(is_followup_approved=True,check_out=timezone.now(),notes=request.POST.get('notes'))
		
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status         = 'FOLLOWUP_IN_PROGRESS'
		follow_up.no_of_cleaners = no_of_cleaners
		follow_up.cleaning_hours = cleaning_hours
		follow_up.total_cost     = total_cost
		follow_up.save()
		
		for date in tendative_date:
			print(date,"dt")
			start_date_time = datetime.strptime(date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
			end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))
			followup_schedule_array.append(FollowUpScheduler(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address))

		# follow_up_scheduler = FollowUpScheduler.objects.filter(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address)
		
		
		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				InvestigationMedia.objects.create(
				        investigation_id=investigation_id,
				        media=media,
				        )

		#to save sections
		no_of_sections         = int(request.POST.get('section_counter'))
		section_array          = []
		for i in range(no_of_sections):
			section_name  = request.POST.get('section'+str(i))
			category      = request.POST.get('category'+str(i))
			dirt_level    = request.POST.get('dirt_level'+str(i))
			quantity      = request.POST.get('quantity'+str(i))
			size          = request.POST.get('size'+str(i))
			unit          = request.POST.get('unit'+str(i))
			age           = request.POST.get('age'+str(i))
			floor         = request.POST.get('floor'+str(i))
			apartment     = request.POST.get('apartment'+str(i))
			room          = request.POST.get('room'+str(i))
			wall_type     = request.POST.get('walltype'+str(i))
			ceiling_type  = request.POST.get('ceilingtype'+str(i))
			floor_type    = request.POST.get('floortype'+str(i))
			material      = request.POST.get('material'+str(i))
			colour        = request.POST.get('colour'+str(i))
			cause_of_stain=request.POST.get('staincause'+str(i))
			section_cost  = request.POST.get('sectioncost'+str(i))

			old_section_id=request.POST.get('editform_section'+str(i))
			print(old_section_id,"oisd")
			try:
				section_name_arabic = Translator().translate(section_name,src='en', dest='ar').text
			except:
				section_name_arabic = section_name
			
			if old_section_id:
				print("old")
				section = FollowUpSection.objects.filter(id=old_section_id).update(section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=len(tendative_date),section_net_cost=section_cost)
			else:
				print("new")
				section = FollowUpSection.objects.create(follow_up=follow_up,section_name=section_name,section_name_arabic=section_name_arabic,category=category,dirt_level=dirt_level,quantity=quantity,size=size,unit=unit,age=age,floor=floor,apartment=apartment,room=room,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=1,section_net_cost=section_cost)

			#to save keynotes
			try:
				no_of_keynotes = int(request.POST.get('section'+str(i)+'-keynote_counter'))
			except:
				no_of_keynotes = None

			keynote_array = []
			if no_of_keynotes:
				for j in range(no_of_keynotes):
					old_keynote_id=request.POST.get('editform_section'+str(i)+'_keynote'+str(j))

					keynote = request.POST.get('section'+str(i)+'_keynote'+str(j))
					quantity= request.POST.get('section'+str(i)+'_quantity'+str(j))

					if old_keynote_id:
						if keynote and quantity:
							FollowUpSectionKeynote.objects.filter(id=old_keynote_id).update(id=old_keynote_id,sub_area=keynote,quantity=quantity)
					else:
						if keynote and quantity:
							keynote_array.append(FollowUpSectionKeynote(followup_section=section,sub_area=keynote,quantity=quantity))
				#bulk_create keynote
				FollowUpSectionKeynote.objects.bulk_create(keynote_array)

		#delete old followup schedules
		FollowUpScheduler.objects.filter(follow_up=follow_up).delete()

		FollowUpScheduler.objects.bulk_create(followup_schedule_array)

		messages.success(request,"Follow Up Cleaning Succesfully Updated !")

		return redirect('quality-control:investigation', investigation_id)

class Cashback(IsQualityControll,View):
	def get(self,request,investigation_id):
		# followup status change
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status = 'FOLLOWUP_IN_PROGRESS'
		follow_up.save()
		return render(request,"qualitycontroll/ticket/cash-back.html")

	def post(self,request,investigation_id):

		paybackdiscount = PaybackDiscount.objects.create(investigation=Investigation.objects.get(is_active=True,id=int(investigation_id)),
		is_active=True
		)

		#to save sections
		no_of_sections         = int(request.POST.get('section_counter'))
		print(no_of_sections,"nose")
		section_array          = []

		total_cost = 0
		section_items_total_cost = 0
		for i in range(no_of_sections):
			section_name  = request.POST.get('section'+str(i))

			#to save keynotes
			try:
				no_of_keynotes = int(request.POST.get('section'+str(i)+'-keynote_counter'))
			except:
				no_of_keynotes = None

			items_total_cost = 0
			keynote_array = []
			if no_of_keynotes:
				for j in range(no_of_keynotes):
					keynote = request.POST.get('section'+str(i)+'_keynote'+str(j))
					quantity= request.POST.get('section'+str(i)+'_quantity'+str(j))
					if keynote and quantity:
						keynote_array.append(PaybackDiscountDetails(paybackdiscount=paybackdiscount,category=section_name,name=keynote,cost=quantity,is_active=True))
					
					items_total_cost += float(quantity)
				#bulk_create keynote
				PaybackDiscountDetails.objects.bulk_create(keynote_array)

			section_items_total_cost += float(items_total_cost)

		total_cost += float(section_items_total_cost)

		paybackdiscount.total_cost = total_cost
		paybackdiscount.save()

		medias = request.FILES.getlist('media')

		if not medias==['']:
			for img in medias:
				PaybackDiscountDetailsMedia.objects.create(
					paybackdiscount = paybackdiscount,
					media = img,
					is_active = True
				)

		messages.success(request,"Cash Back Added !")
		return redirect('quality-control:investigation', investigation_id)

class CashbackEdit(IsQualityControll,View):
	def get(self,request,investigation_id):
		paybackdiscount = PaybackDiscount.objects.get(is_active=True,investigation__id=investigation_id)
		paybackdiscount_details = PaybackDiscountDetails.objects.filter(is_active=True,paybackdiscount=paybackdiscount)
		return render(request,"qualitycontroll/ticket/cash-back-edit.html",{"paybackdiscount":paybackdiscount,"paybackdiscount_details":paybackdiscount_details})

	def post(self,request,investigation_id):

		paybackdiscount = PaybackDiscount.objects.get(investigation_id=int(investigation_id),is_active=True)

		#to save sections
		no_of_sections         = int(request.POST.get('section_counter'))
		print(no_of_sections,"nose")
		section_array          = []

		total_cost = 0
		section_items_total_cost = 0
		for i in range(no_of_sections):
			section_name  = request.POST.get('section'+str(i))

			#to save keynotes
			try:
				no_of_keynotes = int(request.POST.get('section'+str(i)+'-keynote_counter'))
			except:
				no_of_keynotes = None
			print(range(no_of_keynotes),"keyss")
			items_total_cost = 0
			keynote_array = []
			if no_of_keynotes:
				for j in range(no_of_keynotes):
					old_keynote_id=request.POST.get('editform_section'+str(i)+'_keynote'+str(j))

					keynote = request.POST.get('section'+str(i)+'_keynote'+str(j))
					quantity= request.POST.get('section'+str(i)+'_quantity'+str(j))

					print(old_keynote_id,keynote,quantity,'section'+str(i)+'_quantity'+str(j),"datt")

					if old_keynote_id:
						if keynote and quantity:
							PaybackDiscountDetails.objects.filter(is_active=True,id=old_keynote_id).update(id=old_keynote_id,name=keynote,cost=quantity)
					else:
						if keynote and quantity:
							keynote_array.append(PaybackDiscountDetails(paybackdiscount=paybackdiscount,category=section_name,name=keynote,cost=quantity,is_active=True))
					
					items_total_cost += float(quantity)
				#bulk_create keynote
				PaybackDiscountDetails.objects.bulk_create(keynote_array)

			section_items_total_cost += float(items_total_cost)

		total_cost += float(section_items_total_cost)

		paybackdiscount.total_cost = total_cost
		paybackdiscount.save()

		messages.success(request,"Cash Back Updated !")
		return redirect('quality-control:investigation', investigation_id)


class InternalReport(IsQualityControll,View):
	def get(self,request,investigation_id):
		# followup status change
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status = 'FOLLOWUP_IN_PROGRESS'
		follow_up.save()
		return render(request,"qualitycontroll/ticket/internal-report.html")

	def post(self,request,investigation_id):
		report_title = request.POST.get('title')
		report_notes = request.POST.get('notes')

		internal_report = Reporting.objects.create(
			investigation = Investigation.objects.get(is_active=True,id=int(investigation_id)),
			title = report_title,
			notes = report_notes,
			is_active = True
		)

		internal_report.investigation.is_internalreporting_approved = True
		internal_report.save()

		medias = request.FILES.getlist('media')

		print(medias,"medis")
		if not medias==['']:
			for img in medias:
				ReportingMedia.objects.create(
					reporting = internal_report,
					media = img,
					is_active = True
				)
		
		messages.success(request,"Internal Report Submitted !")
		return redirect('quality-control:investigation', investigation_id)

class InternalReportEdit(IsQualityControll,View):
	def get(self,request,investigation_id):
		internalreport = Reporting.objects.get(is_active=True,investigation__id=investigation_id)
		internalreport_media = ReportingMedia.objects.filter(is_active=True,reporting=internalreport)
		return render(request,"qualitycontroll/ticket/internal-report-edit.html",{"internal_report":internalreport,"report_medias":internalreport_media})

	def post(self,request,investigation_id):
		report_title = request.POST.get('title')
		report_notes = request.POST.get('notes')

		internal_report = Reporting.objects.get(is_active = True,investigation__id=investigation_id)
		internal_report.title = report_title
		internal_report.notes = report_notes
		internal_report.investigation.is_internalreporting_approved = True
		internal_report.save()
		
		medias = request.FILES.getlist('media')

		print(medias,"medis")
		if not medias==['']:
			for img in medias:
				ReportingMedia.objects.create(
					reporting = internal_report,
					media = img,
					is_active = True
				)
		
		messages.success(request,"Internal Report Updated !")
		return redirect('quality-control:investigation', investigation_id)

class BuyBackPromoCode(IsQualityControll,View):
	def get(self,request,investigation_id):
		# followup status change
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status = 'FOLLOWUP_IN_PROGRESS'
		follow_up.save()
		return render(request,"qualitycontroll/ticket/promocode.html")

	def post(self,request,investigation_id):

		buybackpromocodegift = BuybackPromocodeGift.objects.create(investigation=Investigation.objects.get(is_active=True,id=int(investigation_id)),
		is_active=True
		)

		#to save sections
		no_of_sections         = int(request.POST.get('section_counter'))
		
		section_array          = []

		total_cost = 0
		section_items_total_cost = 0
		for i in range(no_of_sections):
			section_name  = request.POST.get('section'+str(i))

			#to save keynotes
			try:
				no_of_keynotes = int(request.POST.get('section'+str(i)+'-keynote_counter'))
			except:
				no_of_keynotes = None

			items_total_cost = 0
			keynote_array = []
			if no_of_keynotes:
				for j in range(no_of_keynotes):
					keynote = request.POST.get('section'+str(i)+'_keynote'+str(j))
					quantity= request.POST.get('section'+str(i)+'_quantity'+str(j))
					if keynote and quantity:
						keynote_array.append(BuybackPromocodeGiftDetails(buybackpromocodegift=buybackpromocodegift,category=section_name,name=keynote,cost=quantity,is_active=True))
					
					items_total_cost += float(quantity)
				#bulk_create keynote
				BuybackPromocodeGiftDetails.objects.bulk_create(keynote_array)

			section_items_total_cost += float(items_total_cost)

		total_cost += float(section_items_total_cost)

		buybackpromocodegift.total_cost = total_cost
		buybackpromocodegift.save()

		medias = request.FILES.getlist('media')

		if not medias==['']:
			for img in medias:
				BuybackPromocodeGiftDetailsMedia.objects.create(
					buybackpromocodegift = buybackpromocodegift,
					media = img,
					is_active = True
				)

		messages.success(request,"Buy Back / Promo Code Added !")
		return redirect('quality-control:investigation', investigation_id)

class BuyBackPromoCodeEdit(IsQualityControll,View):
	def get(self,request,investigation_id):
		return render(request,"qualitycontroll/ticket/promocode-edit.html")

	def post(self,request,investigation_id):

		buybackpromocodegift = BuybackPromocodeGift.objects.create(investigation=Investigation.objects.get(is_active=True,id=int(investigation_id)),
		is_active=True
		)

		#to save sections
		no_of_sections         = int(request.POST.get('section_counter'))
		
		section_array          = []

		total_cost = 0
		section_items_total_cost = 0
		for i in range(no_of_sections):
			section_name  = request.POST.get('section'+str(i))

			#to save keynotes
			try:
				no_of_keynotes = int(request.POST.get('section'+str(i)+'-keynote_counter'))
			except:
				no_of_keynotes = None

			items_total_cost = 0
			keynote_array = []
			if no_of_keynotes:
				for j in range(no_of_keynotes):
					keynote = request.POST.get('section'+str(i)+'_keynote'+str(j))
					quantity= request.POST.get('section'+str(i)+'_quantity'+str(j))
					if keynote and quantity:
						keynote_array.append(BuybackPromocodeGiftDetails(buybackpromocodegift=buybackpromocodegift,category=section_name,name=keynote,cost=quantity,is_active=True))
					
					items_total_cost += float(quantity)
				#bulk_create keynote
				BuybackPromocodeGiftDetails.objects.bulk_create(keynote_array)

			# medias = request.FILES.getlist('media'+str(i))

			# print('media'+str(i),medias,"medis")
			# if not medias==['']:
			# 	for img in medias:
			# 		BuybackPromocodeGiftDetailsMedia.objects.create(
			# 			buybackpromocodegift_details = buybackpromocodegift,
			# 			media = img,
			# 			is_active = True
			# 		)

			section_items_total_cost += float(items_total_cost)

		total_cost += float(section_items_total_cost)

		buybackpromocodegift.total_cost = total_cost
		buybackpromocodegift.save()

		messages.success(request,"Buy Back / Promo Code Updated !")
		return redirect('quality-control:investigation', investigation_id)
