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
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
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

	
		#Investigation tasks
		investigation_to_date         = (timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)).replace(tzinfo=None)

		try:	
			investigations  = Investigation.objects.filter(is_active=True,investigator=request.user,check_out=None).select_related('order__evaluation__customer','order_schedule__customer_address__area','order_schedule__order_scheduler_book').prefetch_related(Prefetch('order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team_details')).annotate(color_status=Case(When(Q(Q(sheduled_at__gte=investigation_to_date) & Q(sheduled_at__lt=investigation_to_date+timedelta(1)) & Q(sheduled_at__lte=timezone.now())), then=Value('yellow')),
	                  When(Q(Q(sheduled_at__gte=investigation_to_date) & Q(sheduled_at__lt=investigation_to_date+timedelta(1)) & Q(sheduled_at__gt=timezone.now())), then=Value('green')),When(Q(sheduled_at__gte=investigation_to_date+timedelta(1)), then=Value('blue')),
	                  default=Value('red'),
	                  output_field=CharField(),))
		except:
			investigations  = 	None

		return render(request,'qualitycontroll/home/home.html',{'investigations':investigations,"total_workers":total_workers,"total_active_workers":total_active_workers,"today_active_teams_count":today_active_teams_count,"week_active_teams_count":week_active_teams_count,"today_total_team_mens":today_total_team_mens,"week_total_team_mens":week_total_team_mens,"today_cleaning_active_teams":today_cleaning_active_teams,"today_followup_active_teams":today_followup_active_teams,"week_followup_active_teams":week_followup_active_teams,"week_cleaning_active_teams":week_cleaning_active_teams,})

class InvestigationTask(IsQualityControll,View):
	def get(self,request,investigation_id):
		
		try:
			investigation_details = Investigation.objects.select_related('order_schedule__customer_address__area','order_schedule__order_scheduler_book__service_type','order_schedule__evaluation_details__evaluator','investigator','order__evaluation__customer','order__evaluation__call_attender').prefetch_related(Prefetch('order_schedule__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_teams')).get(id=investigation_id)
		except:
			investigation_details = None

		#save checkin_time
		investigation_details.check_in = timezone.now()
		investigation_details.save()

		return render(request,'qualitycontroll/ticket/investigation.html',{'investigation_details':investigation_details})

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

class Followup(View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	def get(self,request,investigation_id):
		investigation = Investigation.objects.get(is_active=True,id=int(investigation_id))
		print(investigation.order_schedule.evaluation_details.id,"evs")
		evaluation_details = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=investigation.order_schedule.evaluation_details.id)

		service_type = investigation.order_schedule.order_scheduler_book.service_type

		return render(request,"qualitycontroll/ticket/follow-up.html",{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_type':service_type})

	def post(self,request,investigation_id):
		investigation = Investigation.objects.get(is_active=True,id=int(investigation_id))
		evaluation_details 	  = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=investigation.order_schedule.evaluation_details.id)

		no_of_cleaners = request.POST.get('number_of_cleaners')
		cleaning_hours = request.POST.get('cleaning_hours')
		
		tendative_date = request.POST.get('tendative_date')
		tendative_time = request.POST.get('tendative_time')
		start_date_time = datetime.strptime(tendative_date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
		end_date_time   = start_date_time + timedelta(hours=int(cleaning_hours))

		Investigation.objects.filter(id=investigation_id).update(is_followup_approved=True,check_out=timezone.now(),notes=request.POST.get('notes'))
		
		follow_up = FollowUp.objects.get(investigation_id=investigation_id,is_active=True)
		follow_up.status         = 'INVESTIGATOR_APPROVED'
		follow_up.no_of_cleaners = no_of_cleaners
		follow_up.cleaning_hours = cleaning_hours
		follow_up.save()
		
		follow_up_scheduler = FollowUpScheduler.objects.create(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address)
		
		
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


			messages.success(request,"Follow Up Cleaning Succesfully Added")

		return redirect('quality-control:investigation', investigation_id)

class Cashback(IsQualityControll,View):
	def get(self,request,investigation_id):
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

		messages.success(request,"Cash Back Added !")
		return redirect('quality-control:investigation', investigation_id)


class InternalReport(IsQualityControll,View):
	def get(self,request,investigation_id):
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

class BuyBackPromoCode(IsQualityControll,View):
	def get(self,request,investigation_id):
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

		messages.success(request,"Buy Back / Promo Code Added !")
		return redirect('quality-control:investigation', investigation_id)
