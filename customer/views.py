from django.shortcuts import render,redirect
from django.views import View

from django.db.models import Prefetch

from django.utils import timezone

from django.db.models import F
from django.contrib import messages

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory

#all users views
class TermsandConditions(View):
	def get(self,request):
		return render(request,"customer/termsandconditions.html",{})


class Quatation(View):
	def get(self,request,evaluation_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,evaluation__id=evaluation_id)

		nonduplicate_schedules = []
		#Remove duplicates for subscription
		duplicate_schedules    = []
		for orderschedule in order.orderschedules:
			if orderschedule.order_scheduler_book in duplicate_schedules:
				pass
			else:	
				nonduplicate_schedules.append(orderschedule)	

			duplicate_schedules.append(orderschedule.order_scheduler_book)

		return render(request,"customer/newquatation.html",{"order":order,"nonduplicate_schedules":nonduplicate_schedules})

	def post(self,request,evaluation_id):

		order_id 		  = request.POST.get('order_id')

		action            = request.POST.get('action_type')
		
		if action == 'Reject':
			#UPDATE EVALUATION REJECTION
			Evaluation.objects.filter(id=evaluation_id).update(quatation_status='REJECTED',quatation_rejected_date=timezone.now())
			Order.objects.filter(id=order_id).update(order_status='ORDER_CANCELLED')

		if action == 'Approve':
			#UPDATE EVALUATION APPROVAL
			termsandconditions = request.POST.get('termsandconditions')
			if termsandconditions:
				Evaluation.objects.filter(id=evaluation_id).update(quatation_status='APPROVED',quatation_approved_date=timezone.now())
				Order.objects.filter(id=order_id).update(order_status='APPROVED_BY_CLIENT')
				return redirect('customer:invoice',evaluation_id)
			else:
				messages.error(request,"Please Read Terms & Conditions and Agree")
				return redirect('customer:quatation',evaluation_id)

		return redirect('customer:quatation',evaluation_id)

class CustomerInvoice(View):
	def get(self,request,evaluation_id):
		
		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,evaluation__id=evaluation_id)

		nonduplicate_schedules = []
		#Remove duplicates for subscription
		duplicate_schedules    = []
		for orderschedule in order.orderschedules:
			if orderschedule.order_scheduler_book in duplicate_schedules:
				pass
			else:	
				nonduplicate_schedules.append(orderschedule)	

			duplicate_schedules.append(orderschedule.order_scheduler_book)

		return render(request,"customer/invoice.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,})		

class PaymentResponse(View):
	def get(self,request):
		print(request.GET)
		return render(request,"customer/receipt-voucher.html",{})		