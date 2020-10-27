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

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[0:11]
		user_name     =  evaluation_id_encrypted[11:]


		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,order_no=evaluation_id,evaluation__customer__username=user_name)

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
		
		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[0:11]
		user_name     =  evaluation_id_encrypted[11:]

		if action == 'Reject':
			#UPDATE EVALUATION REJECTION
			Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='REJECTED',quatation_rejected_date=timezone.now())
			Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='ORDER_CANCELLED')

		if action == 'Approve':
			#UPDATE EVALUATION APPROVAL
			termsandconditions = request.POST.get('termsandconditions')
			if termsandconditions:
				Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='APPROVED',quatation_approved_date=timezone.now())
				Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='APPROVED_BY_CLIENT')
				return redirect('customer:invoice',evaluation_id_encrypted)
			else:
				messages.error(request,"Please Read Terms & Conditions and Agree")
				return redirect('customer:quatation',evaluation_id_encrypted)

		return redirect('customer:quatation',evaluation_id_encrypted)

class CustomerInvoice(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[0:11]
		user_name     =  evaluation_id_encrypted[11:]

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,evaluation__evaluation_id=evaluation_id,evaluation__customer__username=user_name)

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
		evaluation_id     = request.GET.get("udf1")
		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[0:11]
		user_name     =  evaluation_id_encrypted[11:]

		amount_paid       = float(request.GET.get("amt"))
		payment_result    = request.GET.get("result")

		try:
			order = Order.objects.select_related('evaluation').get(order_no=evaluation_id,evaluation__customer__username=user_name)
		except:
			order = None	

		#To Check Payment Done 
		payment_history_check = PaymentHistory.objects.filter(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid')).exists()	
		

		if order and payment_result == 'CAPTURED' and not payment_history_check:
			payment_history = PaymentHistory.objects.create(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid'))	
			
			#check payment completion
			if (order.remining_amount-amount_paid) == 0:
				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			#UPDATE TOTAL AMOUNTS
			order.amount_paid      = order.amount_paid+amount_paid
			order.remining_amount  = order.remining_amount-amount_paid

			#update breakdown info
			if order.evaluation.payment_method == 'BREAKDOWN':
				order.preamount_paid = order.evaluation.before_cleaning_amount
				order.postamount_paid = order.evaluation.after_cleaning_amount 					

			order.save()

			return redirect('customer:payment-receipt',payment_history.id)
		else:
			messages.error(request,"Something Went Wrong ! Please Contact Admin")

			return redirect('customer:invoice',evaluation_id_encrypted)

class PaymentReceipt(View):
	def get(self,request,payment_id):

		try:
			payment_history = PaymentHistory.objects.select_related('order__evaluation').prefetch_related(Prefetch('order__order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(id=payment_id)
		except:	
			payment_history = None

		nonduplicate_schedules = []
		#Remove duplicates for subscription
		duplicate_schedules    = []
		for orderschedule in payment_history.order.orderschedules:
			if orderschedule.order_scheduler_book in duplicate_schedules:
				pass
			else:	
				nonduplicate_schedules.append(orderschedule)	

			duplicate_schedules.append(orderschedule.order_scheduler_book)

		return render(request,"customer/receipt-voucher.html",{'payment_history':payment_history,'nonduplicate_schedules':nonduplicate_schedules,})
