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

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote,EvaluationMedia,ServiceType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp,Investigation,InvestigationMedia
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
			return redirect('quality-control:cash-back')
		
		return redirect('quality-control:investigation', investigation_id)

class Followup(View):
	service_formset_define    = formset_factory(QuatationServiceForm)
	def get(self,request,investigation_id):
		investigation = Investigation.objects.get(is_active=True,id=int(investigation_id))
		print(investigation.order_schedule.evaluation_details.id,"evs")
		evaluation_details = EvaluationDetails.objects.select_related('evaluation__customer','address__area').get(is_active=True,id=investigation.order_schedule.evaluation_details.id)

		service_type = investigation.order_schedule.order_scheduler_book.service_type.id

		return render(request,"qualitycontroll/ticket/follow-up.html",{'service_formset':self.service_formset_define(),'evaluation_details':evaluation_details,'service_type':service_type})

	def post(self,request,investigation_id):
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

			return redirect('quality-control:investigation')

class Cashback(View):
    def get(self,request):
        return render(request,"qualitycontroll/ticket/cash-back.html")
