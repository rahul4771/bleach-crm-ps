from django.shortcuts import render,redirect
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsTeamLeader,IsAuthenticated

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
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote,EvaluationSectionAddons,EvaluationMedia
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp,Investigation,InvestigationMedia,FollowUpSection,FollowUpSectionKeynote,PaybackDiscount,BuybackPromocodeGift,Reporting
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from bleachadmin.models import ServicePriceRange
from customer.models import CustomerBooking
from bleachinventory.models import CheckOutItems
import requests

from django.http import HttpResponse,JsonResponse
# Create your views here.


def UpdateKeynoteStatus(request):
	keynote_id     = request.GET.get('keynote_id')
	keynote_status = request.GET.get('status')
	keynote_type = request.GET.get('keynote_type')

	print(keynote_type,"ktype")

	if keynote_type == 'followupcleaning':
		if keynote_status == 'true':
			FollowUpSectionKeynote.objects.filter(id=keynote_id).update(completion_status=True)
		else:
			FollowUpSectionKeynote.objects.filter(id=keynote_id).update(completion_status=False)
	else:
		if keynote_status == 'true':
			EvaluationSectionKeynote.objects.filter(id=keynote_id).update(completion_status=True)
		else:
			EvaluationSectionKeynote.objects.filter(id=keynote_id).update(completion_status=False)
		
	data = {}

	data['keynote_id']     = keynote_id
	data['keynote_status'] = keynote_status

	return JsonResponse(data)




class TlHome(IsTeamLeader,View):
	def get(self,request):

		#for taking today counts
		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)

		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			cleaning_job    = None

		today_cleaning_job_count = cleaning_job.filter(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))).count() 
		week_cleaning_job_count  = cleaning_job.filter(Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end))).count()
				

		#Investigation Count
		try:
			investigation = Investigation.objects.filter(is_active=True,investigator=request.user)
		except:
			investigation = None	

		today_investigation_count = investigation.filter(scheduled_at__gte=count_today_start,scheduled_at__lt=count_today_end).count()
		week_investigation_count   = investigation.filter(scheduled_at__gte=count_today_end-timedelta(7),scheduled_at__lt=count_today_end).count()	

		##To find average and total hour  team leader 
		try:
			cleaning_teams  = CleaningTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			cleaning_teams  = None
		try:
			follow_up_teams = FollowUpTeam.objects.filter(is_active=True,team_leader=request.user)
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


		#My cleanings	
		my_cleaning_calendar_date	= request.GET.get('my_cleaning_calendar_date')
		
		try:
			my_cleaning_date = datetime.strptime(my_cleaning_calendar_date,'%d-%m-%Y')
		except:
			my_cleaning_date = timezone.now().replace(tzinfo=None)

		my_cleaning_date_start = my_cleaning_date.replace(hour=0,minute=0,second=0,microsecond=0)
		my_cleaning_date_end   = my_cleaning_date_start+timedelta(1)


		try:	
			my_cleanings  = CleaningTeam.objects.filter(Q(Q(Q(start_at__gte=my_cleaning_date_start)&Q(start_at__lt=my_cleaning_date_end))&Q(team_leader=request.user))).select_related('order_scheduler__order_scheduler_book__service_type','order_scheduler__order__evaluation__customer','order_scheduler__customer_address')
		except:
			my_cleanings  = None
		
		#partitions
		for my_cleaning in my_cleanings:
			similar_schedules 			= OrderScheduler.objects.filter(order_scheduler_book=my_cleaning.order_scheduler.order_scheduler_book).order_by('start_at')
			my_cleaning.total_cleanings = similar_schedules.count()
			my_cleaning.partition       = list(similar_schedules.values_list('id',flat=True)).index(my_cleaning.order_scheduler.id)+1

		try:
			my_followups  = FollowUpTeam.objects.filter(Q(Q(Q(start_at__gte=my_cleaning_date_start)&Q(start_at__lt=my_cleaning_date_end))&Q(team_leader=request.user))).select_related('followup_scheduler__follow_up__investigation__order__evaluation__customer','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__service_type','followup_scheduler__customer_address')
		except:
			my_followups  = None	

		return render(request,'tl/home/home.html',{"today_cleaning_job_count":today_cleaning_job_count,'week_cleaning_job_count':week_cleaning_job_count,'today_cleaning_active_teams':today_cleaning_active_teams,'week_cleaning_active_teams':week_cleaning_active_teams,'today_followup_active_teams':today_followup_active_teams,'week_followup_active_teams':week_followup_active_teams,'today_date':today_date,'weekstart_date':weekstart_date,'today_investigation_count':today_investigation_count,'week_investigation_count':week_investigation_count,'my_cleaning_date':my_cleaning_date,"my_cleanings":my_cleanings,"my_followups":my_followups,'today_total_team_mens':today_total_team_mens,'week_total_team_mens':week_total_team_mens})


class TicketDetails(IsTeamLeader,View):
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
			tickets 	             = FollowUp.objects.select_related('investigation__order_schedule__order__evaluation__customer','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate').filter(is_active=True).filter(Q(Q(investigation__order_schedule__order__evaluation__customer__name__icontains=search)|Q(investigation__order_schedule__order__evaluation__evaluation_id__icontains=search))).order_by('-id').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).select_related('customer_address__area'),to_attr='follow_up_scheduler_details'))				
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

		return render(request,'tl/ticket/tickets.html',{"tickets":tickets,"follow_ups_count":follow_ups_count,"follow_up_cleaning_count":follow_up_cleaning_count,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"governorates":governorates,"areas":areas,"investigators":investigators,"fil_governorate":fil_governorate,'fil_area':fil_area,"fil_investigator":fil_investigator,"fil_status":fil_status,})		
	
class TicketAdvanced(IsTeamLeader,View):
	def get(self,request,client_id,followup_id):

		#client info
		try:
			client_details = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area','governorate'),to_attr='customer_addresses')).get(is_active=True,id=client_id)
		except:
			client_details = None

		#followup info
		
		followup_details = FollowUp.objects.select_related('investigation__investigator','investigation__order','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate','investigation__order_schedule__order_scheduler_book').prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules'),Prefetch('investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),).get(is_active=True,id=followup_id)
			
			

		#orders count
		orders 				= Order.objects.filter(is_active=True,evaluation__customer_id=client_id)
		active_orders_count = orders.filter(Q(Q(order_status='APPROVED_BY_CLIENT')|Q(order_status='ORDER_IN_PROGRESS'))).count()
		total_orders_count  = orders.count()

		return render(request,'tl/ticket/followup-page.html',{"client_details":client_details,"active_orders_count":active_orders_count,"total_orders_count":total_orders_count,"followup_details":followup_details,})		

class Cleaning(IsTeamLeader,View):
	def get(self,request,team_id):

		cleaning_team_detail = CleaningTeam.objects.select_related('team_leader','drop_off_driver','pick_up_driver','order_scheduler__evaluation_details','order_scheduler__order_scheduler_book__service_type','order_scheduler__customer_address','order_scheduler__order__evaluation').prefetch_related(Prefetch('order_scheduler__order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr="evaluationmedias"),Prefetch('order_scheduler__order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons'),Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='sections')).get(is_active=True,id=team_id)
		cleaning_team_members = CleaningTeamMember.objects.filter(team=team_id,is_active=True)
		
		try:
			customerbooking = CustomerBooking.objects.get(evaluation__id=cleaning_team_detail.order_scheduler.order.evaluation.id,is_active=True,booking_type='CLEANINGBOOKING',is_bookingcompleted=True)
		except:
			customerbooking = None

		if customerbooking:
			is_customer_booking = True
		else:
			is_customer_booking = False

		price_ranges_change = ServicePriceRange.objects.filter(is_active=True,service_type__id=cleaning_team_detail.order_scheduler.order_scheduler_book.service_type.id)	

		price_ranges = ServicePriceRange.objects.filter(is_active=True)

		#remaining teams
		cleaning_teams = CleaningTeam.objects.filter(order_scheduler__order_scheduler_book=cleaning_team_detail.order_scheduler.order_scheduler_book).values('order_scheduler__work_status')
		cleaning_teams_count = cleaning_teams.count()
		remaining_team = 0
		for team in cleaning_teams:
			if team['order_scheduler__work_status'] != 'CLEANING_FULFILLED':
				remaining_team += 1

		#cleaning items
		cleaning_items = CheckOutItems.objects.filter(visit__id=cleaning_team_detail.order_scheduler.id,is_collected=False)
		
		return render(request,'tl/cleaning/cleaning.html',{"cleaning_items":cleaning_items,"price_ranges":price_ranges,"price_ranges_change":price_ranges_change,"cleaning_team_detail":cleaning_team_detail,"cleaning_team_members":cleaning_team_members,"is_customer_booking":is_customer_booking,"cleaning_teams_count":cleaning_teams_count,"remaining_team":remaining_team})


	# def post(self,request,team_id):
	# 	print("checkk")
	# 	#checkout save
	# 	try:
	# 		cleaning_team_detail = CleaningTeam.objects.select_related('order_scheduler__order').get(is_active=True,id=team_id)
	# 	except:	
	# 		cleaning_team_detail = None

	# 	#remaining teams
	# 	cleaning_teams = CleaningTeam.objects.filter(order_scheduler__order_scheduler_book=cleaning_team_detail.order_scheduler.order_scheduler_book).values('order_scheduler__work_status')
	# 	cleaning_teams_count = cleaning_teams.count()
	# 	remaining_team = 0
	# 	for team in cleaning_teams:
	# 		if team['order_scheduler__work_status'] != 'CLEANING_FULFILLED':
	# 			remaining_team += 1
		
	# 	print(remaining_team,"rtm")
	# 	#remaining keynotes
	# 	keynotes = EvaluationSectionKeynote.objects.filter(evaluation_section__evaluation_book=cleaning_team_detail.order_scheduler.order_scheduler_book).values('completion_status')
	# 	remaining_keynotes = 0
	# 	if keynotes:
	# 		for key in keynotes:
	# 			if key['completion_status'] == False:
	# 				remaining_keynotes += 1
	# 	else:
	# 		pass
	# 	print(remaining_keynotes,"rky")

			
	# 	if cleaning_team_detail: 
	# 		print("ctd")
	# 		submit_status = request.POST.get('jax')
	# 		print(submit_status,"ctdd")
	# 		#checkin save
	# 		if submit_status == 'Check In':
	# 			print("valhalla")
	# 			# if not cleaning_team_detail.check_in:
	# 			# 	cleaning_team_detail.check_in                    = timezone.now()
	# 			# if not cleaning_team_detail.check_out:
	# 			# 	cleaning_team_detail.order_scheduler.work_status     = 'CLEANING_IN_PROGRESS'
	# 			# cleaning_team_detail.save()	
	# 			# cleaning_team_detail.order_scheduler.save()

	# 			# #To Save Media
	# 			# medias = request.FILES.getlist('mediabefore')
	# 			# if not medias==['']:
	# 			# 	for media in medias:
	# 			# 		CleaningTeamMedia.objects.create(
	# 			# 				team_id=team_id,
	# 			# 				media=media,
	# 			# 				taken_status='BEFORE_CLEANING'
	# 			# 				)

	# 			if cleaning_team_detail.is_section_updated == True:
	# 				print("send smmsr")
	# 				evaluaation = cleaning_team_detail.order_scheduler.order.evaluation
	# 				if evaluaation.customer.is_sms == True:

	# 					url = "https://smsapi.future-club.com/fccsms.aspx"

	# 					if evaluaation.customer.sms_preference == 'ENGLISH':

	# 						message = "Dear Customer, Please find the updated Invoice against the order number "+str(evaluaation.evaluation_id)+"  here https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluaation.evaluation_id[3:])+""+str(evaluaation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
					
	# 						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
						
	# 					else:

	# 						message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluaation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluaation.evaluation_id[3:])+""+str(evaluaation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
					
	# 						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
						
	# 					headers = {
	# 						'cache-control': "no-cache"
	# 					}

	# 					response = requests.request("GET", url, headers=headers, params=querystring)

	# 					print(message,response.text,"respo")

	# 			messages.success(request,"Check In Completed Successfully !")

	# 		#checkout save
	# 		if submit_status == 'Check Out':

	# 			if cleaning_team_detail.order_scheduler.order_scheduler_book.cleaning_policy == 'SUBSCRIPTION':
					
	# 				if remaining_keynotes >= 1:
	# 					messages.error(request,"Please Check all Keynotes!!!")
	# 					return redirect('tl:cleaning',team_id)
	# 				else:
	# 					cleaning_team_detail.order_scheduler.work_status  		= 'CLEANING_FULFILLED'	
	# 					cleaning_team_detail.check_out                    		= timezone.now()
				
	# 			else:
	# 				if cleaning_teams_count > 1:
	# 					if remaining_team == 1 and remaining_keynotes >= 1:
	# 						messages.error(request,"Please Check all Keynotes!!!")
	# 						return redirect('tl:cleaning',team_id)
	# 					else:	
	# 						cleaning_team_detail.order_scheduler.work_status  		= 'CLEANING_FULFILLED'	
	# 						cleaning_team_detail.check_out                    		= timezone.now()
	# 				else:	
	# 					cleaning_team_detail.order_scheduler.work_status  		= 'CLEANING_FULFILLED'	
	# 					cleaning_team_detail.check_out                    		= timezone.now()

	# 			cleaning_team_detail.order_scheduler.order.order_status = 'ORDER_IN_PROGRESS'
				
	# 			cleaning_team_detail.save()
	# 			cleaning_team_detail.order_scheduler.save()
	# 			cleaning_team_detail.order_scheduler.order.save()	

	# 			#To Save Media
	# 			medias = request.FILES.getlist('mediaafter')
	# 			if not medias==['']:
	# 				for media in medias:
	# 					CleaningTeamMedia.objects.create(
	# 							team_id=team_id,
	# 							media=media,
	# 							taken_status='AFTER_CLEANING'
	# 							)		

	# 			messages.success(request,"Checkout Succesfully")

	# 			language = cleaning_team_detail.order_scheduler.order.evaluation.customer.sms_preference


	# 			evaluation = cleaning_team_detail.order_scheduler.order.evaluation
	# 			#invoice sms
	# 			if cleaning_team_detail.order_scheduler.order.remining_amount > 0 and evaluation.customer.is_sms == True:

	# 				url = "https://smsapi.future-club.com/fccsms.aspx"

	# 				if language == 'ENGLISH':

	# 					message = "Dear Customer, Please find the Invoice against the order number "+str(evaluation.evaluation_id)+"  here https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
				
	# 					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
					
	# 				else:

	# 					message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
				
	# 					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
					
	# 				headers = {
	# 					'cache-control': "no-cache"
	# 				}

	# 				response = requests.request("GET", url, headers=headers, params=querystring)

	# 				print(response.text,"respo")
	# 			else:
	# 				pass


	# 			#feedback sms
	# 			order = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=int(cleaning_team_detail.order_scheduler.order.id)).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))

	# 			for ord in order:
	# 				print(ord.cleaning_count,ord.followup_count,ord.completed_cleaning_count,ord.completed_followup_count,'countss')
	# 				order_data = ord

	# 			if order and order_data.evaluation.customer.is_sms == True:   #.completed_cleaning_count == order_data.cleaning_count or order_data.completed_followup_count == order_data.followup_count :

	# 				url = "https://smsapi.future-club.com/fccsms.aspx"

	# 				if order_data.evaluation.customer.sms_preference == 'ENGLISH':

	# 					message = "Dear Customer, Thank you for choosing Bleach Kuwait. Kindly share your feedback for the order number "+ order_data.order_no +" here https://my.bleachkw.com/customer/feedback-page/"+str(order_data.id)+". For any assistance please contact us on +9651882707."
					
	# 					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order_data.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

	# 				else:
	# 					message = "عزيزينا العميل نرجوا أن تكون خدماتنا خازت على رضاكم و شكراً لاختياركم بليتش لخدمات التنظيف.  نرجوا التكرم بإنجاز الاستبيان الخاص بالطلب رقم "+ order_data.order_no +" https://my.bleachkw.com/customer/feedback-page/"+str(order_data.id)+" وذلك لضمان جودة الخدمة. لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"

	# 					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order_data.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

	# 				headers = {
	# 					'cache-control': "no-cache"
	# 				}

	# 				response = requests.request("GET", url, headers=headers, params=querystring)
	# 			else:
	# 				pass

	# 			####to close order
	# 			try:
	# 				closing_order	= Order.objects.get(is_active=True,order_no=cleaning_team_detail.order_scheduler.order.order_no,payment_status='COMPLETED')
	# 			except:
	# 				closing_order   = None

	# 			if closing_order and order:
	# 				closing_order.order_status = 'ORDER_CLOSED'
	# 				closing_order.save()


	# 	my_cleaning_calendar_date = request.GET.get('my_cleaning_calendar_date') or ''
				
	# 	return redirect('/tl/dashboard/?my_cleaning_calendar_date='+my_cleaning_calendar_date)

class FollowupCleaning(IsTeamLeader,View):
	def get(self,request,team_id):

		followup_team_detail = FollowUpTeam.objects.select_related('team_leader','drop_off_driver','pick_up_driver','followup_scheduler__follow_up__investigation__investigator','followup_scheduler__follow_up__investigation__order__evaluation','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__service_type','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book','followup_scheduler__customer_address').prefetch_related(Prefetch('followup_scheduler__follow_up__investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr="investigationmedias"),Prefetch('followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='sections')).get(is_active=True,id=team_id)
		followup_team_members= FollowUpTeamMember.objects.filter(team=team_id,is_active=True)			

		followupsections = FollowUpSection.objects.filter(follow_up__id = followup_team_detail.followup_scheduler.follow_up.id,is_active=True )
		followupsectionkeynotes = FollowUpSectionKeynote.objects.filter(followup_section__follow_up__id = followup_team_detail.followup_scheduler.follow_up.id,is_active=True)
		
		
		return render(request,'tl/cleaning/followup_cleaning.html',{"followup_team_detail":followup_team_detail,"followup_team_members":followup_team_members,"sections":followupsections,"keynotes":followupsectionkeynotes})

	def post(self,request,team_id):
		
		#checkout save
		try:
			followup_team_detail = FollowUpTeam.objects.select_related('followup_scheduler__follow_up').get(is_active=True,id=team_id)
		except:	
			followup_team_detail = None
		
		#checkin save	
		if followup_team_detail: 
			submit_status = request.POST.get('assign')

			#checkin save
			if submit_status == 'Check In':
				if not followup_team_detail.check_in:
					followup_team_detail.check_in                       = timezone.now()
				if not followup_team_detail.check_out:
					followup_team_detail.followup_scheduler.work_status     = 'FOLLOW_UP_CLEANING_IN_PROGRESS'
					followup_team_detail.followup_scheduler.follow_up.status= 'FOLLOWUP_IN_PROGRESS'
				followup_team_detail.save()	
				followup_team_detail.followup_scheduler.save()
				followup_team_detail.followup_scheduler.follow_up.save()

				#To Save Media
				medias = request.FILES.getlist('mediabefore')
				if not medias==['']:
					for media in medias:
						FollowUpTeamMedia.objects.create(
								team_id=team_id,
								media=media,
								taken_status='BEFORE_CLEANING'
								)
				messages.success(request,"Check In Completed Successfully !")


			if submit_status == 'Check Out':
				
				followup_team_detail.check_out                          = timezone.now()
				followup_team_detail.followup_scheduler.work_status     = 'FOLLOW_UP_CLEANING_FULFILLED'
				followup_team_detail.save()
				followup_team_detail.followup_scheduler.save()	

				#To Save Media
				medias = request.FILES.getlist('mediaafter')
				if not medias==['']:
					for media in medias:
						FollowUpTeamMedia.objects.create(
								team_id=team_id,
								media=media,
								taken_status='AFTER_CLEANING'
								)

				messages.success(request,"Checkout Succesfully")

				#feedback sms
				order = Order.objects.select_related('evaluation__customer').filter(is_active=True,order_no=followup_team_detail.followup_scheduler.follow_up.investigation.order.order_no).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))

				for ord in order:
					order_data = ord
				
				if order and order_data.evaluation.customer.is_sms == True:

					url = "https://smsapi.future-club.com/fccsms.aspx"

					if order_data.evaluation.customer.sms_preference == 'ENGLISH':

						message = "Dear Customer, Thank you for choosing Bleach Kuwait. Kindly share your feedback for the order number "+ order_data.order_no +" here https://my.bleachkw.com/customer/feedback-page/"+str(order_data.id)+". For any assistance please contact us on +9651882707."
					
						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order_data.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

					else:
						message = "عزيزينا العميل نرجوا أن تكون خدماتنا خازت على رضاكم و شكراً لاختياركم بليتش لخدمات التنظيف.  نرجوا التكرم بإنجاز الاستبيان الخاص بالطلب رقم "+ order_data.order_no +" https://my.bleachkw.com/customer/feedback-page/"+str(order_data.id)+" وذلك لضمان جودة الخدمة. لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"

						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order_data.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

					headers = {
						'cache-control': "no-cache"
					}

					response = requests.request("GET", url, headers=headers, params=querystring)

					print(response.text,",ess")

				else:
					pass

				####to close order
				try:
					closing_order	= Order.objects.get(is_active=True,order_no=followup_team_detail.followup_scheduler.follow_up.investigation.order.order_no,payment_status='COMPLETED')
				except:
					closing_order   = None
					
				if closing_order and order:
					closing_order.order_status = 'ORDER_CLOSED'
					closing_order.save()
					
		my_cleaning_calendar_date = request.GET.get('my_cleaning_calendar_date') or ''
				
		return redirect('/tl/dashboard/?my_cleaning_calendar_date='+my_cleaning_calendar_date)

class ItemsList(IsTeamLeader,View):
	def get(self,request):
		tl_items = CheckOutItems.objects.filter(is_collected=True,is_collected_by=request.user,is_checked_in=False,item__is_reusable=True)
		
		for item in tl_items:
			item.days_since_cleaning = (timezone.now()-item.visit.end_at).days

		return render(request,"tl/items/items.html",{"tl_items":tl_items})

	def post(self,request):
		item_ids = request.POST.get('item_ids')
		item_ids = item_ids.split(",")
		item_ids.remove('')
		
		for item_id in item_ids:
			print(item_id,"idee")
			checkout_item = CheckOutItems.objects.get(id=int(item_id))
			checkout_item.is_returned = True
			checkout_item.save()

		return redirect('tl:tl-items')