from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import HttpResponse,JsonResponse

from django.views import View

from bleach_crm_ps.utils import get_error

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


from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,Promocode
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking
from bleachadmin.models import ServiceProductivity,ServicePriceRange
from agent.forms import UserProfileForm,AddressForm
from evaluator.forms import QuatationServiceFormCustomer
from itertools import chain
from agent.views import generate_random_username

import requests

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#all users views
class TermsandConditions(View):
	def get(self,request):
		return render(request,"customer/termsandconditions.html",{})


class Quatation(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]


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

		return render(request,"customer/quotation.html",{"order":order,"nonduplicate_schedules":nonduplicate_schedules})

	def post(self,request,evaluation_id):

		order_id 		  = request.POST.get('order_id')

		action            = request.POST.get('action_type')
		
		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		if action == 'Reject':
			#UPDATE EVALUATION REJECTION
			Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='REJECTED',quatation_rejected_date=timezone.now())
			Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='ORDER_CANCELLED')

		#print(request.POST)
		if action == 'Approve':
			#UPDATE EVALUATION APPROVAL
			termsandconditions = request.POST.get('termsandconditions')
			if termsandconditions:
				evaluation_update = Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='APPROVED',quatation_approved_date=timezone.now())
				
				last_invoice_no  		 = Order.objects.filter(is_active=True).aggregate(t=Max('invoice_no'))['t']
				current_invoice_starting = str(timezone.now().year)
				if last_invoice_no:		
					if current_invoice_starting == last_invoice_no[0:4]:
						new_invoice_no 		 = str(int(last_invoice_no[4:]) + 1 )
						new_invoice_no 		 = last_invoice_no[0:-(len(new_invoice_no))]+new_invoice_no
					else:
						new_invoice_no 		 = str(timezone.now().year)+'00001'
				else:
					new_invoice_no 		 = str(timezone.now().year)+'00001'

				order_update      = Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='APPROVED_BY_CLIENT',invoice_no=new_invoice_no)
				
				#close payment if remining becomes zero 
				order = Order.objects.get(order_no=evaluation_id)
				if order.remining_amount == 0:
					order.payment_completed_date = timezone.now()
					order.payment_status         = 'COMPLETED'
					order.save()

				#sms				
				evaluaation = Evaluation.objects.get(evaluation_id=evaluation_id,customer__username=user_name)

				language = evaluaation.customer.sms_preference
				
				if evaluaation.payment_method == 'PREPAID' or evaluaation.payment_method == 'BREAKDOWN':
					messages.success(request,"Quatation Approved Succesfully")

					if evaluaation.customer.is_sms == True:

						url = "https://smsapi.future-club.com/fccsms.aspx"

						if evaluaation.payment_method == 'SUBSCRIPTION':
							smsurl = "https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluaation.tracking_no)+""+str(evaluaation.customer.username)+""
						else:
							smsurl = "https://my.bleachkw.com/customer/invoice/prw"+str(evaluaation.tracking_no)+""+str(evaluaation.customer.username)+""

						if language == 'ENGLISH':

							message = "Dear Customer, Please find the Invoice against the order number "+str(evaluaation.evaluation_id)+"  here "+smsurl+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
					
							querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
						
						else:

							message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluaation.evaluation_id)+" في هذا الرابط "+smsurl+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
					
							querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
						
						headers = {
							'cache-control': "no-cache"
						}

						response = requests.request("GET", url, headers=headers, params=querystring)

						print(response.text,"respo")
					else:
						pass

					new_evaluation_id_encrypted = 'prw'+evaluation_id_encrypted[3:]
					
					return redirect('customer:invoice',new_evaluation_id_encrypted)
				else:
					messages.success(request,"Quatation Approved Succesfully")

					return redirect('customer:quatation',evaluation_id_encrypted)

				Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='APPROVED',quatation_approved_date=timezone.now())

				Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='APPROVED_BY_CLIENT')
				
				return redirect('customer:invoice',evaluation_id_encrypted)
			
			else:
				messages.error(request,"Please Read Terms & Conditions and Agree")
				return redirect('customer:quatation',evaluation_id_encrypted)

		return redirect('customer:quatation',evaluation_id_encrypted)


class SubscriptionQuatation(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]


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

		
		#per job cost
		per_job_cost = 0
		for orderschedule in nonduplicate_schedules:            
			for section in orderschedule.order_scheduler_book.evaluationbooksection:
				per_job_cost += section.section_cost
		
		return render(request,"customer/quotation.html",{"order":order,"nonduplicate_schedules":nonduplicate_schedules,"per_job_cost":per_job_cost})
 
	def post(self,request,evaluation_id):
		order_id 		  = request.POST.get('order_id')
		action            = request.POST.get('action_type')

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		if action == 'Reject':
			#UPDATE EVALUATION REJECTION
			Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='REJECTED',quatation_rejected_date=timezone.now())
			Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='ORDER_CANCELLED')

		#print(request.POST)
		if action == 'Approve':
			#UPDATE EVALUATION APPROVAL
			termsandconditions = request.POST.get('termsandconditions')
			if termsandconditions:
				evaluation_update = Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='APPROVED',quatation_approved_date=timezone.now())
				
				last_invoice_no  		 = Order.objects.filter(is_active=True).aggregate(t=Max('invoice_no'))['t']
				current_invoice_starting = str(timezone.now().year)		
				if current_invoice_starting == last_invoice_no[0:4] and last_invoice_no:
					new_invoice_no 		 = str(int(last_invoice_no[4:]) + 1 )
					new_invoice_no 		 = last_invoice_no[0:-(len(new_invoice_no))]+new_invoice_no
				else:
					new_invoice_no 		 = str(timezone.now().year)+'00001'
				order_update      = Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='APPROVED_BY_CLIENT',invoice_no=new_invoice_no)
				
				return redirect('customer:subscriptioninvoice',evaluation_id_encrypted)
			
			else:
				messages.error(request,"Please Read Terms & Conditions and Agree")
				return redirect('customer:subscriptionquatation',evaluation_id_encrypted)

		return redirect('customer:subscriptionquatation',evaluation_id_encrypted)

class CustomerInvoice(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

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

		#for credit card
		full_name_array = UserProfile.objects.get(username=user_name).name.split()
		firstname = full_name_array[0]
		lastname  = ''
		
		count = 0
		for i in full_name_array:
			if(count>=1):
				lastname += i+' '
			count += 1
		
		customer_ip_address = get_client_ip(request)

		return render(request,"customer/customer_invoice.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,'firstname':firstname,'lastname':lastname,'customer_ip_address':customer_ip_address,})		

	def post(self,request,evaluation_id):

		action            = request.POST.get('action_type')
		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		if action == 'CASH/CHEQUE':
			Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(payment_way='CASH/CHEQUE')
			messages.success(request,"Cash/Cheque payment method approved !")
		return redirect('customer:invoice',evaluation_id_encrypted)


class CustomerSubscriptionInvoice(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

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

		#per completed jobs count
		completed_jobs_count = 0 
		for schedule in order.orderschedules:
			if schedule.work_status == 'CLEANING_FULFILLED':
				completed_jobs_count += 1
		
		#for credit card
		full_name_array = UserProfile.objects.get(username=user_name).name.split()
		firstname = full_name_array[0]
		lastname  = ''
		
		count = 0
		for i in full_name_array:
			if(count>=1):
				lastname += i+' '
			count += 1
		
		customer_ip_address = get_client_ip(request)

		return render(request,"customer/customer_invoice_subscription.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,'firstname':firstname,'lastname':lastname,'customer_ip_address':customer_ip_address,"completed_jobs_count":completed_jobs_count})

	def post(self,request,evaluation_id):
		action            = request.POST.get('action_type')
		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		if action == 'CASH/CHEQUE':
			Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(payment_way='CASH/CHEQUE')
			messages.success(request,"Cash/Cheque payment method approved !")
		return redirect('customer:subscriptioninvoice',evaluation_id_encrypted)


class PaymentResponseDebit(View):
	def get(self,request):
		#evaluation id decryption
		evaluation_id_encrypted = request.GET.get("udf1")
		evaluation_id = 'BLC'+evaluation_id_encrypted[0:11]
		user_name     =  evaluation_id_encrypted[11:]

		amount_paid       = float(request.GET.get("amt"))
		payment_result    = request.GET.get("result")
		payment_mode      = request.GET.get("udf2")

		try:
			order = Order.objects.select_related('evaluation').get(order_no=evaluation_id,evaluation__customer__username=user_name)
		except:
			order = None	

		#To Check Payment Done 
		payment_history_check = PaymentHistory.objects.filter(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid')).exists()	
		

		if order and payment_result == 'CAPTURED' and not payment_history_check:

			#Receipt Number
			receipt_no               = PaymentHistory.objects.filter(is_active=True,receipt_no__isnull=False).aggregate(t=Max('receipt_no'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_receipt_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_receipt_starting == int(str(receipt_no)[:4]):
				new_receipt_no = int(receipt_no)+1
			else:
				new_receipt_no = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')

			#payment history
			payment_history = PaymentHistory.objects.create(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid'),receipt_no=new_receipt_no,payment_gateway='DEBITCARD')	

			#payment calculations
			if payment_mode == 'subscription':
				order.amount_paid      += amount_paid
				order.remining_amount  = order.remining_amount-amount_paid
				order.subscription_topay= 0
				#to check payment completed
				if order.remining_amount == 0:
					order.payment_status         = 'COMPLETED'
					order.payment_completed_date = timezone.now()					
			
			elif payment_mode == 'before_cleaning' and order.preamount_paid != order.evaluation.before_cleaning_amount:
				order.preamount_paid   = amount_paid
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

			elif payment_mode == 'after_cleaning' and order.postamount_paid != order.evaluation.after_cleaning_amount:
				order.postamount_paid   = amount_paid
				order.amount_paid      += amount_paid
				order.remining_amount   = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'prepaid' and order.amount_paid != order.total_amount:
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid					

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'postpaid' and order.amount_paid != order.total_amount:
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()
			order.save()

			#payment receipt sms
			if order.evaluation.customer.is_sms == True:

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if order.evaluation.customer.sms_preference == 'ENGLISH':

					message = "Dear Customer, We have successfully received your payment of amount "+ str(amount_paid) +" KD, (Transaction ID: "+ str(request.GET.get('tranid')) +", Ref ID: "+ str(request.GET.get('ref')) +") against the order number "+ str(order.order_no) +". Please find the Payment receipt here https://my.bleachkw.com/customer/payment/receipt/pvw"+ str(order.evaluation.tracking_no) +""+str(payment_history.id)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
				
				else:
					message = "عزيزي العميل، لقد تلقينا مدفوعاتك بنجاح مقابل رقم الطلب "+ order.order_no +". يرجى العثور على إيصال الدفع هنا https://my.bleachkw.com/customer/payment/receipt/pvw"+request.GET.get('paymentid')+". لأي مساعدة يرجى الاتصال بنا على9651882707 شكرا لاختيارك بليتش الكويت"
	

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)

				print(response.text)
			else:
				pass

			
			####to close order
			order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,order_no=evaluation_id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
			if order_closing_check:
				closing_order	= Order.objects.get(is_active=True,order_no=evaluation_id)
				closing_order.order_status = 'ORDER_CLOSED'
				closing_order.save()

			return redirect('customer:payment-receipt','pvw'+str(evaluation_id_encrypted[0:11])+str(payment_history.id))
		else:

			#payment fail sms
			if order.evaluation.customer.is_sms == True:

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if order.evaluation.payment_method == 'SUBSCRIPTION':
					smsurl = "https://my.bleachkw.com/customer/subscription/invoice/prw"+str(order.evaluation.tracking_no)+""+str(order.evaluation.customer.username)+""
				else:
					smsurl = "https://my.bleachkw.com/customer/invoice/prw"+str(order.evaluation.tracking_no)+""+str(order.evaluation.customer.username)+""

				if order.evaluation.customer.sms_preference == 'ENGLISH':

					message = "Dear Customer, Your payment against the order number "+ order.order_no +" has failed (Payment ID : "+str(request.GET.get('paymentid'))+", Ref. ID: "+ str(request.GET.get('ref')) +"). Click here to try again "+smsurl+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
				
				else:
					message = "عزيزي العميلفشل الدفع الخاص بك مقابل رقم الطلب "+ order.order_no +". اضغط هنا للمحاولة مرة أخرى "+smsurl+" أي مساعدة يرجى الاتصال بنا على . +9651882707 شكرا لاختيارك بليتش الكويت"

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)

				print(response.text)
			else:
				pass

			return redirect('/customer/payment/failed/?udf1='+evaluation_id_encrypted+'&paymentid='+request.GET.get('paymentid')+'&ref='+request.GET.get('ref'))


class PaymentFailedResponse(View):
	def get(self,request):

		payment_id   = request.GET.get('paymentid')
		reference_id = request.GET.get('ref')

		evaluation_id_encrypted = request.GET.get("udf1")

		#for back to invoice
		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate'),to_attr='orderschedules')).get(order_no='BLC'+evaluation_id_encrypted[0:11])
	
		return render(request,"customer/paymentfail.html",{'payment_id':payment_id,'evaluation_id_encrypted':evaluation_id_encrypted,'reference_id':reference_id,"order":order})			

class PaymentReceipt(View):
	def get(self,request,payment_id):

		original_payment_id    = payment_id[14:]
		evaluation_id 		   = 'BLC'+payment_id[3:14]

		try:
			payment_history = PaymentHistory.objects.select_related('order__evaluation').prefetch_related(Prefetch('order__order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(id=original_payment_id,order__order_no=evaluation_id)
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

		return render(request,"customer/voucher.html",{'payment_history':payment_history,'nonduplicate_schedules':nonduplicate_schedules,})

class CustomerOrderDetails(View):
	def get(self,request,order_id,service_id,section_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True,id=int(section_id)).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,id=order_id)
	
		# order_books = Order.objects.prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True,id=int(section_id)),to_attr='evaluationbooks')),to_attr='orderschedules')).get(is_active=True,id=order_id)

		section_id = section_id

		return render(request,"customer/content-page.html",{"order":order,"sectionid":int(section_id),"serviceid":int(service_id)})
		

class CustomerFeedback(View):
	def get(self,request,order_id):

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)

		try:
			feedback = FeedBack.objects.filter(order=order).first()
		except:
			feedback=None
		
		if feedback != None:
			feedback_exist = "yes"
		else:
			feedback_exist = "no"

		try:
			orders = Order.objects.filter(is_active=True,is_feedback_marked=False)
		except:
			orders = None

		try:
			questions = Question.objects.filter(is_active=True).order_by('id')
		except:
			questions = None

		return render(request,"customer/customer-feedback.html",{"order":order, "questions":questions, "feedback_exist":feedback_exist})

	def post(self,request,order_id):
		order_id        = int(order_id)
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
		
		for question in questions:
			rating = request.POST.get('rating'+str(question.id)) or 0

			create_feedbacks.append(FeedBack(order=order,question=question,rating=rating,response_date=timezone.now()))
		FeedBack.objects.bulk_create(create_feedbacks)

		messages.success(request,"Feedback Succesfully Submitted")
		
		return redirect('customer:customer-feedback', order_id)


#for download

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML

def quatation_html_to_pdf_view(request,evaluation_id):

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
    

	if order.evaluation.payment_method == 'SUBSCRIPTION':
		html_string = render_to_string('customer/subscriptionquatation.html', {"order":order,"nonduplicate_schedules":nonduplicate_schedules})
	else:
		html_string = render_to_string('customer/newquatation.html', {"order":order,"nonduplicate_schedules":nonduplicate_schedules})

	html = HTML(string=html_string,base_url=request.build_absolute_uri())
	html.write_pdf(target='/home/pdf/tmp/quatation/quatation.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/quatation/')
	with fs.open('quatation.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+evaluation_id+'_quatation.pdf"'
		return response
	return response

def orderdetail_html_to_pdf_view(request,order_id,service_id,section_id):

	order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)

	html_string = render_to_string('customer/content-page.html', {"order":order,"sectionid":int(section_id),"serviceid":int(service_id)})

	html = HTML(string=html_string,base_url=request.build_absolute_uri())
	html.write_pdf(target='/home/ansab/Desktop/orderdetails.pdf'); 
	# html.write_pdf(target='/home/pdf/tmp/orderdetails/orderdetails.pdf'); 

	fs = FileSystemStorage('/home/ansab/Desktop/')
	# fs = FileSystemStorage('/home/pdf/tmp/orderdetails/')
	with fs.open('orderdetails.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+order.order_no+'_orderdetails.pdf"'
		return response
	return response


def termsandconditions_to_pdf(request):
	fs = FileSystemStorage('/home/pdf/tmp/termsandconditions/')
	with fs.open('termsandconditions.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="termsandconditions.pdf"'
		return response
	return response	


def invoice_html_to_pdf_view(request,evaluation_id):

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
    

	html_string = render_to_string('customer/newquatation.html', {"order":order,"nonduplicate_schedules":nonduplicate_schedules})

	html = HTML(string=html_string,base_url=request.build_absolute_uri())
	html.write_pdf(target='/home/pdf/tmp/invoice/invoice.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/invoice/')
	with fs.open('invoice.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+evaluation_id+'_invoice.pdf"'
		return response
	return response		

def receipt_html_to_pdf_view(request,payment_id):

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
    

	html_string = render_to_string('customer/receipt-voucher.html', {'payment_history':payment_history,'nonduplicate_schedules':nonduplicate_schedules,})

	html = HTML(string=html_string,base_url=request.build_absolute_uri())
	html.write_pdf(target='/home/pdf/tmp/receipt/receipt.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/receipt/')
	with fs.open('receipt.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+payment_history.order.order_no+'_receipt.pdf"'
		return response
	return response	


def statement_of_account(request,client_id):
	client = UserProfile.objects.get(is_active=True,id=int(client_id))
	address = Address.objects.filter(customer__id=int(client_id)).first()

	invoices         = Order.objects.filter(is_active=True).order_by('evaluation__quatation_approved_date').filter(evaluation__customer__id=int(client_id),evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
	
	#Pending Payments
	pending_payments = invoices.filter(Q( Q(Q(evaluation__payment_method='PREPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))) | Q(Q(evaluation__payment_method='POSTPAID')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(preamount_paid=0)) | Q(Q(evaluation__payment_method='BREAKDOWN')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&Q(completed_cleaning_count=F('cleaning_count'))) | Q(Q(evaluation__payment_method='SUBSCRIPTION')&Q(Q(payment_status='PENDING')|Q(payment_status='ON_HOLD'))&~Q(subscription_topay=0)) ))
	
	#remove object in postpaid if not last cleaning fulfilled	
	#remove if subscription to pay date
	if pending_payments:
		for payment in pending_payments:
			if payment.evaluation.payment_method == 'POSTPAID':
				very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
				if very_latest_cleaning.work_status != 'CLEANING_FULFILLED':
					pending_payments = pending_payments.exclude(id=payment.id)
			if payment.evaluation.payment_method == 'SUBSCRIPTION' and not payment.subscription_topay_date:
				pending_payments = pending_payments.exclude(id=payment.id)	

	#to find days
	if pending_payments:
		for payment in pending_payments:
			if payment.evaluation.payment_method == 'PREPAID' and payment.orderschedules:
				very_old_cleaning   = payment.orderschedules[0]
				payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
			elif payment.evaluation.payment_method == 'POSTPAID' and payment.orderschedules:
				very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
				payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	
			elif payment.evaluation.payment_method == 'BREAKDOWN' and payment.orderschedules:
			
				very_old_cleaning   = payment.orderschedules[0]
				very_latest_cleaning=payment.orderschedules[payment.cleaning_count-1]
				payment.reminigdays = (very_old_cleaning.start_at-timezone.now()).days
				payment.delaydays   = (timezone.now()-very_latest_cleaning.start_at).days	

				#to check last cleaning completed for break down after payment
				if very_latest_cleaning.work_status == 'CLEANING_FULFILLED':
					payment.last_completed = True	

			elif payment.evaluation.payment_method == 'SUBSCRIPTION':				
				payment.delaydays= (timezone.now()-payment.subscription_topay_date).days	

	paymenthistory = PaymentHistory.objects.filter(is_active=True,order__evaluation__customer__id=int(client_id)).order_by('paid_date')
	
	accounts_list = []

	#appending items to list after multiple filters
	for invoice in pending_payments:
		if invoice.evaluation.payment_method == 'PREPAID' or invoice.evaluation.payment_method == 'POSTPAID':
			if invoice.evaluation.payment_method == 'PREPAID':
				if invoice.reminigdays >= 1 :

					accounts_list.append({
						"account_date":invoice.evaluation.quatation_approved_date.date(),
						"invoice_no":invoice.invoice_no,
						"amount":invoice.total_amount,
					})
				else:
					pass

			else:
				accounts_list.append({
						"account_date":invoice.evaluation.quatation_approved_date.date(),
						"invoice_no":invoice.invoice_no,
						"amount":invoice.total_amount,
					})

		elif invoice.evaluation.payment_method == 'BREAKDOWN':
			if invoice.preamount_paid != invoice.evaluation.before_cleaning_amount:
				if invoice.reminigdays >= 1:
					accounts_list.append({
						"account_date":invoice.evaluation.quatation_approved_date.date(),
						"invoice_no":invoice.invoice_no,
						"amount":invoice.evaluation.before_cleaning_amount
					})
				else:
					pass

			if invoice.last_completed and invoice.postamount_paid != invoice.evaluation.after_cleaning_amount:
				accounts_list.append({
						"account_date":invoice.evaluation.quatation_approved_date.date(),
						"invoice_no":invoice.invoice_no,
						"amount":invoice.evaluation.after_cleaning_amount
					})

		elif invoice.evaluation.payment_method == 'SUBSCRIPTION':
			if invoice.subscription_topay != 0:
				accounts_list.append({
						"account_date":invoice.evaluation.quatation_approved_date.date(),
						"invoice_no":invoice.invoice_no,
						"amount":invoice.subscription_topay
					})

		else:
			pass

	for history in paymenthistory:

		accounts_list.append({
						"account_date":history.order.evaluation.quatation_approved_date.date(),
						"invoice_no":history.order.invoice_no,
						"amount":history.amount_paid
					})

		accounts_list.append({
						"account_date":history.paid_date.date(),
						"receipt_no":history.receipt_no,
						"amount":history.amount_paid
					})

	accounts_list=sorted(accounts_list, key=lambda x: datetime.strptime(str(x["account_date"]), "%Y-%m-%d"))

	print(accounts_list,"listo")

	
	return render(request,"customer/statement_of_account.html",{"client":client,"address":address,"accounts":accounts_list,"pending_payments":pending_payments})

####Customer Booking########
from django.forms.models import model_to_dict
def GetCustomerDetails(request):
	customer_information = {}
	mobile_no            = request.GET.get('search_mobile')
	
	client_details       = UserProfile.objects.prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(currently_active=True),to_attr='customer_addresses')).get(mobile_number=mobile_no)

	customer_information['name']          = client_details.name
	customer_information['name_arabic']   = client_details.name_arabic
	customer_information['gender']        = client_details.gender
	customer_information['date_day']        = client_details.date_day
	customer_information['date_month']        = client_details.date_month
	customer_information['date_year']        = client_details.date_year
	customer_information['email']         = client_details.email
	customer_information['mobile']        = client_details.mobile_number
	customer_information['nationality']   = client_details.nationality.code
	customer_information['customer_type'] = client_details.customer_type
	customer_information['company']       = client_details.company
	customer_information['job_title']     = client_details.job_title
	customer_information['sms_preference']= client_details.sms_preference
	customer_information['is_sms']        = client_details.is_sms
	customer_information['is_email']      = client_details.is_email
	customer_information['is_whatsapp']   = client_details.is_whatsapp

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
	
	return JsonResponse(customer_information)

def GetEvaluationBookingSlotes(request):
	dropdown_slotes  = {}
	evaluation_date  = datetime.strptime(request.GET.get('evaluation_booking_date'),'%Y-%m-%d')
	
	available_slotes = []
	for slote in range(8,18):
		slote_datetime 			  = evaluation_date.replace(hour=slote,minute=0,second=0,microsecond=0)
		checkavailability         = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related('evaluator_evaluation').annotate(busyevaluationcount=Sum(Case(When(evaluator_evaluation__proposed_time=slote_datetime,then=1),default=0,output_field=IntegerField()))).filter(busyevaluationcount__lt=2)
		if checkavailability:
			available_slotes.append(slote)

	dropdown_slotes['slotes']=available_slotes
	
	return JsonResponse(dropdown_slotes)

def GetCleaningTimeSlotes(request):
	dropdown_slotes  = {}
	cleaning_date      = datetime.strptime(request.GET.get('booking_date'),'%d-%m-%Y')
	cleaning_duration  = float(request.GET.get('cleaning_duration'))
	
	number_of_cleaners = int(request.GET.get('number_of_cleaners'))
	service_type       = request.GET.get('service_type')

	#count total cleaners and total leaders
	if service_type == 'Kitchen Cleaning':
		total_cleaners 	= UserProfile.objects.filter(is_kitchen_skill=True,user_type='CLEANER').count()
		total_leaders 	= UserProfile.objects.filter(is_kitchen_skill=True,user_type='TEAMINCHARGE').count()
	elif service_type == 'Carpet Cleaning':
		total_cleaners 	= UserProfile.objects.filter(is_carpet_skill=True,user_type='CLEANER').count()
		total_leaders 	= UserProfile.objects.filter(is_carpet_skill=True,user_type='TEAMINCHARGE').count()
	elif service_type == 'Sterilization':
		total_cleaners 	= UserProfile.objects.filter(is_sterilization_skill=True,user_type='CLEANER').count()
		total_leaders 	= UserProfile.objects.filter(is_sterilization_skill=True,user_type='TEAMINCHARGE').count()
	elif service_type == 'Mattress Cleaning':
		total_cleaners 	= UserProfile.objects.filter(is_mattress_skill=True,user_type='CLEANER').count()
		total_leaders 	= UserProfile.objects.filter(is_mattress_skill=True,user_type='TEAMINCHARGE').count()
	elif service_type == 'Sofa Cleaning':
		total_cleaners 	= UserProfile.objects.filter(is_sofa_skill=True,user_type='CLEANER').count()
		total_leaders 	= UserProfile.objects.filter(is_sofa_skill=True,user_type='TEAMINCHARGE').count()

	#absent cleaners and leaders	
	absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date,staff__user_type='CLEANER').values_list('staff',flat=True)
	absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date,staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

	available_slotes = []
	#slote wise checking
	for slote in range(8,21):
		slote_starttime 			  = cleaning_date.replace(hour=slote,minute=0,second=0,microsecond=0)
		slote_endtime                 = slote_starttime+timedelta(hours=cleaning_duration)
		print(slote_starttime)
		print(slote_endtime)

		if service_type == 'Kitchen Cleaning':
			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_kitchen_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_kitchen_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
		elif service_type == 'Carpet Cleaning':
			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_carpet_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(slote_endtimee__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_carpet_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(slote_endtimee__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
		elif service_type == 'Sterilization':
			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_sterilization_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_sterilization_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
		elif service_type == 'Mattress Cleaning':
			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_mattress_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_mattress_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
		elif service_type == 'Sofa Cleaning':
			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_sofa_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_sofa_skill=True).filter(Q(Q(Q(start_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime))|Q(Q(end_at__gte=slote_starttime)&Q(end_at__lte=slote_endtime))|Q(Q(start_at__lte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__gte=slote_endtime))|Q(Q(start_at__gte=slote_starttime)&Q(end_at__gte=slote_starttime)&Q(start_at__lte=slote_endtime)&Q(end_at__lte=slote_endtime))))

		cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
		cleaning_active_cleaners     = active_cleaners1.filter(member__user_type='CLEANER').values_list('member',flat=True)

		followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
		followup_active_cleaners     = active_cleaners2.filter(member__user_type='CLEANER').values_list('member',flat=True)

		#merging
		team_leaders_scheduled      = []
		team_members_scheduled      = []

		for active_team_leaders in cleaning_active_team_leaders:
			team_leaders_scheduled.append(active_team_leaders)
		for active_team_leaders in followup_active_team_leaders:
			team_leaders_scheduled.append(active_team_leaders)

		for active_team_member in cleaning_active_cleaners:
			team_members_scheduled.append(active_team_member)
		for active_team_member in followup_active_cleaners:
			team_members_scheduled.append(active_team_member)

		for absent_cleaner in absent_cleaners:
			team_members_scheduled.append(absent_cleaner)
		for absent_leader in absent_leaders:
			team_leaders_scheduled.append(absent_leader)


		print(team_leaders_scheduled,"team_leaders_scheduled")
		print(team_members_scheduled,"team_members_scheduled")

		busy_leaders  = len(set(team_leaders_scheduled))
		busy_cleaners = len(set(team_members_scheduled))

		print(total_cleaners,"total_cleaners")
		print(total_leaders,"total_leaders")
		print(busy_leaders,"busy_leaders")
		print(busy_cleaners,"busy_cleaners")

		#slote appending
		if((total_cleaners-busy_cleaners)>=number_of_cleaners and (total_leaders-busy_leaders)>=1):
			available_slotes.append(slote)				
				
	dropdown_slotes['slotes'] = available_slotes
	print(dropdown_slotes,"dropdown_slotes")			
	return JsonResponse(dropdown_slotes)	

def GetServiceProductivity(request):
	service_productivity = {}
	service_type         = request.GET.get('service_type')
	total_estimated_size = request.GET.get('total_estimated_size')

	serviceproductivity = ServiceProductivity.objects.select_related('service_type').get(service_type__name=service_type)
	service_productivity['perhour_cleaning'] = serviceproductivity.perhour_cleaning

	service_pricerange                       = ServicePriceRange.objects.select_related('service_type').get(service_type__name=service_type,minimum_area__lte=total_estimated_size,maximum_area__gte=total_estimated_size)
	service_productivity['total_price']      = service_pricerange.price
	print(service_productivity['total_price'])
	if service_type == 'Kitchen Cleaning':
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_kitchen_skill=True).count()
	elif service_type == 'Carpet Cleaning':
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_carpet_skill=True).count()
	elif service_type == 'Sterilization':
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_sterilization_skill=True).count()
	elif service_type == 'Mattress Cleaning':
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_deep_skill=True).count()
	elif service_type == 'Sofa Cleaning':
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_sofa_skill=True).count()
	if total_cleaners > 0:
		total_cleaners = total_cleaners-1
	service_productivity['max_cleaners'] = total_cleaners

	return JsonResponse(service_productivity)


class CustomerBookingPhase1(View):
	def get(self,request):
		
		try:
			service_types = ServiceType.objects.filter(is_active=True)
		except:
			service_types = None

		try:
			area_types = AreaType.objects.filter(is_active=True)
		except:
			area_types = None

		return render(request,'customer/booking/bookingphase1.html',{"service_types":service_types,"area_types":area_types,})
	
	def post(self,request):
		action = request.POST.get('action_type')

		if action == 'bookevaluation':
			proposed_date                     = request.POST.get('booking_date')
			proposed_time                     = request.POST.get('booking_time')
			converted_proposed_time           = datetime.strptime(proposed_date+" "+proposed_time,'%Y-%m-%d %I:%M %p')	
			#available evaluator
			availableevaluators               = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related('evaluator_evaluation').annotate(busyevaluationcount=Sum(Case(When(evaluator_evaluation__proposed_time=converted_proposed_time,then=1),default=0,output_field=IntegerField()))).filter(busyevaluationcount__lt=2)
		

			if availableevaluators:
				#create Main Evaluation
				tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

				current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
				
				if current_blc_starting == int(str(tracking_no)[:6]):
					new_tracking_no = int(tracking_no)+1
					evaluation_no   = 'BLC'+str(new_tracking_no)
				else:
					evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
					tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')
				
				evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no,quatation_expiry_date=timezone.now()+timedelta(14))
				
				#Booking Number
				booking_id               = CustomerBooking.objects.filter(is_active=True).aggregate(t=Max('booking_id'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
				current_booking_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

				if current_booking_starting == int(str(booking_id)[:4]):
					new_booking_id = int(booking_id)+1
				else:
					new_booking_id = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')
				
				#booking save
				customerbooking = CustomerBooking.objects.create(booking_id=new_booking_id,booking_type='EVALUATIONBOOKING',evaluation=evaluation)
				
				#evaluation details save
				##select evaluator
				if availableevaluators.filter(busyevaluationcount=0):
					evaluator = availableevaluators.filter(busyevaluationcount=0).first()
				elif availableevaluators.filter(busyevaluationcount=1):
					evaluator = availableevaluators.filter(busyevaluationcount=1).first()

				evaluation_details = EvaluationDetails.objects.create(evaluation=evaluation,evaluator=evaluator,attender_note=request.POST.get('notes'),proposed_time=converted_proposed_time)		

				return redirect('customer:customerbookingevaluationphase2',evaluation_details.id,customerbooking.id)
			
			else:
				if not availableevaluators:
					messages.error(request,"Evaluators not Available...Please Change date or Slote !")

		if action == 'bookcleaning':
			service_form  = QuatationServiceFormCustomer(request.POST)

			if service_form.is_valid():
				try:
					booking_id         = request.COOKIES['booking_id']
					customerbooking    = CustomerBooking.objects.select_related('evaluation__customer').get(booking_id=booking_id,is_bookingcompleted=False)
				except:
					customerbooking    = None

				if not customerbooking:
					#create Main Evaluation
					tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

					current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
					
					if current_blc_starting == int(str(tracking_no)[:6]):
						new_tracking_no = int(tracking_no)+1
						evaluation_no   = 'BLC'+str(new_tracking_no)
					else:
						evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
						tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')
					
					evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no)
					
					#create order
					new_order = Order.objects.get_or_create(evaluation=evaluation,order_no=evaluation.evaluation_id)

					#Booking Number and booking save
					booking_id               = CustomerBooking.objects.filter(is_active=True).aggregate(t=Max('booking_id'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
					current_booking_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

					if current_booking_starting == int(str(booking_id)[:4]):
						new_booking_id = int(booking_id)+1
					else:
						new_booking_id = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')
					
					customerbooking = CustomerBooking.objects.create(booking_id=new_booking_id,booking_type='CLEANINGBOOKING',evaluation=evaluation)

					#Evaluation Details save
					evaluation_details = EvaluationDetails.objects.create(evaluation=evaluation)				

				else:
					
					evaluation_details = EvaluationDetails.objects.get(evaluation=customerbooking.evaluation)
					new_order          = Order.objects.get_or_create(evaluation=customerbooking.evaluation)					

				#service book saving
				service_form_save                    = service_form.save(commit=False)

				service_form_save.evaluation_details = evaluation_details

				service_form_save.estimated_cost     = float(request.POST.get('total_cost'))
				duration = request.POST.get('duration').split('-')
				service_form_save.number_of_cleaners =	duration[0].replace("_cleaners","")
				service_form_save.cleaning_hours     =  float(duration[1].replace("_Hours",""))
				
				service_form_save.cleaning_policy	 = 'ONE TIME SERVICE'
				service_form_save.cleaning_method	 = 'Method1'
				service_form_save.save()

				#To Save Media
				medias = request.FILES.getlist('media')
				if not medias==['']:
					for media in medias:
						EvaluationMedia.objects.create(
						        evaluation_book=service_form_save,
						        media=media,
						        media_type='PHOTO',
								taken_status='CUSTOMER_SEND'
						        )

				#to save schedule cleaning team and cleaning team members
				tendative_dates       = request.POST.get('tendative_date').split(',')
				start_time            = request.POST.get('tendative_time')
				
				for date in tendative_dates:
					start_date_time = datetime.strptime(date+' '+start_time,'%d-%m-%Y %I:%M %p')
					end_date_time   = start_date_time + timedelta(hours=int(service_form_save.cleaning_hours)) 	

					#schedule
					order_schedule = OrderScheduler.objects.create(order=new_order[0],status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book=service_form_save)
					
					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
					active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at))|Q(Q(end_at__gte=order_schedule.start_at)&Q(end_at__lte=order_schedule.end_at))|Q(Q(start_at__lte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__gte=order_schedule.end_at))|Q(Q(start_at__gte=order_schedule.start_at)&Q(end_at__gte=order_schedule.start_at)&Q(start_at__lte=order_schedule.end_at)&Q(end_at__lte=order_schedule.end_at)))).values_list("member",flat=True)
			
					leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
					cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)))
					
					service_type = service_form_save.service_type.name
					if service_type == 'Kitchen Cleaning':
						leaders = leaders.filter(is_kitchen_skill=True)
						cleaners= cleaners.filter(is_kitchen_skill=True).order_by('user_type')
					elif service_type == 'Carpet Cleaning':
						leaders = leaders.filter(is_carpet_skill=True)
						cleaners= cleaners.filter(is_carpet_skill=True).order_by('user_type')
					elif service_type == 'Mattress Cleaning':
						leaders = leaders.filter(is_mattress_skill=True)
						cleaners= cleaners.filter(is_mattress_skill=True).order_by('user_type')
					elif service_type == 'Sofa Cleaning':
						leaders = leaders.filter(is_sofa_skill=True)
						cleaners= cleaners.filter(is_sofa_skill=True).order_by('user_type')
					
					#cleaning team
					cleaning_team  = CleaningTeam.objects.create(order_scheduler=order_schedule,team_leader=leaders.first(),start_at=start_date_time,end_at=end_date_time)
					#cleaning team members
					no_of_cleaners = int(service_form_save.number_of_cleaners)-1
					cleaning_team_member_array = []
					for i in range(no_of_cleaners):
						cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=cleaners[i],start_at=start_date_time,end_at=end_date_time,start_time=start_date_time.time(),end_time=end_date_time.time()))
					cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=leaders.first(),start_at=start_date_time,end_at=end_date_time,start_time=start_date_time.time(),end_time=end_date_time.time()))

					CleaningTeamMember.objects.bulk_create(cleaning_team_member_array)

				#to save sections
				no_of_sections         = int(request.POST.get('section_counter'))
				section_array          = []
				for i in range(1,(no_of_sections+1)):
					section_name         = 'Section'+str(i)
					size                 = request.POST.get('bk-size-'+str(i))
					unit                 = request.POST.get('bk-unit-'+str(i))
					age                  = request.POST.get('bk-age-'+str(i))
					material             = request.POST.get('bk-material-'+str(i))
					colour               = request.POST.get('bk-color-'+str(i))
					cause_of_stain       = request.POST.get('bk-stain-reason-'+str(i))
					oil_resedue          = request.POST.get('bk-oil_resedue-'+str(i))
					service_productivity = ServiceProductivity.objects.get(service_type=service_form_save.service_type)
					section_cost         = service_productivity.perunit_price*int(request.POST.get('bk-size-'+str(i)))
					
					try:
						section_name_arabic =Translator().translate(section_name,src='en', dest='ar').text
					except:
						section_name_arabic = section_name

					#save section
					section = EvaluationBookSection.objects.create(evaluation_book=service_form_save,section_name=section_name,section_name_arabic=section_name_arabic,size=size,unit=unit,age=age,material=material,colour=colour,cause_of_stain=cause_of_stain,section_cost=section_cost,section_cleanings=1,section_net_cost=section_cost)
				
				#set cookie
				httpresponse = redirect('customer:customerbookingcleaningphase2')
				httpresponse.set_cookie('booking_id',customerbooking.booking_id)
				
				messages.success(request,"Service Added Succesfully")

				return httpresponse
			else:
				messages.error(request,get_error(service_form))
		
		return redirect('customer:customerbookingphase1')	

class CustomerBookingEvaluationPhase2(View):
	
	def get(self,request,evaluationdetails_id,customerbooking_id):
		return render(request,'customer/booking/evaluationbookingphase2.html',{})
	
	def post(self,request,evaluationdetails_id,customerbooking_id):
		try:
			existing_user = UserProfile.objects.get(mobile_number=request.POST.get('mobile_number'))
		except:
			existing_user = None


		if existing_user:
			customer_form    = UserProfileForm(request.POST,instance=existing_user)			
		else:
			customer_form    = UserProfileForm(request.POST)


		if customer_form.is_valid():
			###save customer details###
			customer_form_save            = customer_form.save(commit=False)
			customer_form_save.username    = generate_random_username()
			customer_form_save.user_type   = 'CUSTOMER'

			#customer id generation
			customer_id                  = UserProfile.objects.filter(is_active=True,customer_id__isnull=False).aggregate(t=Max('customer_id'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'1000')
			current_customer_id_starting = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2))					
			if current_customer_id_starting == int(str(customer_id)[:4]):
				new_customer_id = int(customer_id)+1
			else:
				new_customer_id   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2)+'1001')

			customer_form_save.customer_id = new_customer_id

			#To Save Contact Platform
			if request.POST.get('is_whatsapp'):
				customer_form_save.is_whatsapp = True
			else:
				customer_form_save.is_whatsapp = False

			if request.POST.get('is_email'):
				customer_form_save.is_email    = True
			else:
				customer_form_save.is_email    = False

			if request.POST.get('is_sms'):
				customer_form_save.is_sms      = True
			else:
				customer_form_save.is_sms      = False

			#APPEND MR / MS TO NAME
			customer_name = customer_form_save.name

			if customer_form_save.gender == 'MALE':
				prefix = 'Mr. '
				prefix_exists = customer_name.startswith(prefix)

				if prefix_exists == False :
					customer_form_save.name = prefix+customer_name
			elif customer_form_save.gender == 'FEMALE':
				prefix = 'Ms. '
				prefix_exists = customer_name.startswith(prefix)

				if prefix_exists == False :
					customer_form_save.name = prefix+customer_name
			else:
				pass

			customer_form_save.save()
		
			###update Evaluation###
			evaluation_details = EvaluationDetails.objects.select_related('evaluation').get(id=evaluationdetails_id)
			evaluation_details.evaluation.customer = customer_form_save
			evaluation_details.evaluation.save()

			messages.success(request,"Customer Details Succesfully Added")

			return redirect('customer:customerbookingevaluationphase3',evaluationdetails_id,customerbooking_id)

		else:
			messages.error(request,get_error(customer_form))
			return render(request,'customer/booking/evaluationbookingphase2.html',{})
	
		return redirect('customer:customerbookingevaluationphase2',evaluationdetails_id,customerbooking_id)

class CustomerBookingEvaluationPhase3(View):
	
	def get(self,request,evaluationdetails_id,customerbooking_id):
		
		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			locations = AreaType.objects.filter(is_active=True)
		except:
			locations = None

		customer_booking = CustomerBooking.objects.select_related('evaluation__customer').get(id=customerbooking_id)		


		active_addresses = Address.objects.filter(is_active=True,currently_active=True,customer=customer_booking.evaluation.customer)


		return render(request,'customer/booking/evaluationbookingphase3.html',{'governorates':governorates,'locations':locations,'active_addresses':active_addresses,})

	def post(self,request,evaluationdetails_id,customerbooking_id):
		evaluation_details = EvaluationDetails.objects.select_related('evaluation').get(id=evaluationdetails_id)

		#EXISTING ADDRESS OR NEW address
		try:
			update_address = Address.objects.get(id=request.POST.get('address_id'))
		except:
			update_address = None

		if update_address:
			address_form              = AddressForm(request.POST,instance=update_address)
		else:
			address_form              = AddressForm(request.POST)


		if address_form.is_valid():
			###save address details###
			address_form_save                   = address_form.save(commit=False)
			address_form_save.customer          = evaluation_details.evaluation.customer
			address_form_save.currently_active  = True

			#string check
			block_text = address_form_save.block
			floor_text = address_form_save.floor
			street_text = address_form_save.street
			avenue_text = address_form_save.avenue

			is_block = block_text.find("Block")
			is_street= street_text.find("Street")

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
	
			###update evaluation details and bookingdetails###
			evaluation_details.address    = address_form_save
			evaluation_details.save()
			CustomerBooking.objects.filter(id=customerbooking_id).update(is_bookingcompleted=True)

			messages.success(request,"Evaluation Booking Succesfully Completed")

			return redirect('customer:customerbookingevaluationphase4',evaluationdetails_id,customerbooking_id)
		else:
			try:
				governorates = Governorate.objects.filter(is_active=True)
			except:
				governorates = None

			try:
				locations = AreaType.objects.filter(is_active=True)
			except:
				locations = None

			return render(request,'customer/booking/evaluationbookingphase3.html',{'governorates':governorates,'locations':locations,})			

		return redirect('customer:customerbookingevaluationphase3',evaluationdetails_id,customerbooking_id)

class CustomerBookingEvaluationPhase4(View):
	
	def get(self,request,evaluationdetails_id,customerbooking_id):
		
		evaluation_details = EvaluationDetails.objects.select_related('evaluator','evaluation').get(id=evaluationdetails_id)
		booking_details    = CustomerBooking.objects.get(id=customerbooking_id)

		return render(request,'customer/booking/evaluationbookingphase4.html',{'evaluation_details':evaluation_details,'booking_details':booking_details,})

######cleaning booking
class CustomerBookingCleaningPhase2(View):
	def get(self,request):

		try:
			booking_details = CustomerBooking.objects.select_related('evaluation').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).get(booking_id=request.COOKIES['booking_id'])
		except:
			booking_details = None

		return render(request,'customer/booking/cleaningbookingphase2.html',{'booking_details':booking_details,})

	def post(self,request):
		#cost updates in evaluation details and evaluation
		try:
			booking_details = CustomerBooking.objects.select_related('evaluation').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluationbooks')),to_attr='evaluationdetails')).get(booking_id=request.COOKIES['booking_id'])
		except:
			booking_details = None
		
		total_cost = 0
		if booking_details:
			for evaluationdetail in booking_details.evaluation.evaluationdetails:
				for evaluationbook in evaluationdetail.evaluationbooks:
					total_cost += evaluationbook.total_cost

		EvaluationDetails.objects.filter(evaluation=booking_details.evaluation).update(total_cost=total_cost,estimated_cost=total_cost)
		Evaluation.objects.filter(id=booking_details.evaluation.id).update(total_cost=total_cost,estimated_cost=total_cost)
		Order.objects.filter(evaluation=booking_details.evaluation).update(total_amount=total_cost,remining_amount=total_cost)		

		return redirect('customer:customerbookingcleaningphase3')


class CustomerBookingCleaningPhase3(View):
	def get(self,request):
		return render(request,'customer/booking/cleaningbookingphase3.html',{})
	def post(self,request):
		try:
			existing_user = UserProfile.objects.get(mobile_number=request.POST.get('mobile_number'))
		except:
			existing_user = None


		if existing_user:
			customer_form    = UserProfileForm(request.POST,instance=existing_user)			
		else:
			customer_form    = UserProfileForm(request.POST)


		if customer_form.is_valid():
			###save customer details###
			customer_form_save            = customer_form.save(commit=False)
			customer_form_save.username    = generate_random_username()
			customer_form_save.user_type   = 'CUSTOMER'

			#customer id generation
			customer_id                  = UserProfile.objects.filter(is_active=True,customer_id__isnull=False).aggregate(t=Max('customer_id'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'1000')
			current_customer_id_starting = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2))					
			if current_customer_id_starting == int(str(customer_id)[:4]):
				new_customer_id = int(customer_id)+1
			else:
				new_customer_id   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2)+'1001')

			customer_form_save.customer_id = new_customer_id

			#To Save Contact Platform
			if request.POST.get('is_whatsapp'):
				customer_form_save.is_whatsapp = True
			else:
				customer_form_save.is_whatsapp = False

			if request.POST.get('is_email'):
				customer_form_save.is_email    = True
			else:
				customer_form_save.is_email    = False

			if request.POST.get('is_sms'):
				customer_form_save.is_sms      = True
			else:
				customer_form_save.is_sms      = False

			#APPEND MR / MS TO NAME
			customer_name = customer_form_save.name

			if customer_form_save.gender == 'MALE':
				prefix = 'Mr. '
				prefix_exists = customer_name.startswith(prefix)

				if prefix_exists == False :
					customer_form_save.name = prefix+customer_name
			elif customer_form_save.gender == 'FEMALE':
				prefix = 'Ms. '
				prefix_exists = customer_name.startswith(prefix)

				if prefix_exists == False :
					customer_form_save.name = prefix+customer_name
			else:
				pass

			customer_form_save.save()
		
			#update customer details in Evaluation
			booking_details = CustomerBooking.objects.select_related('evaluation').get(booking_id=request.COOKIES['booking_id'])
			booking_details.evaluation.customer = customer_form_save
			booking_details.evaluation.save()

			messages.success(request,"Customer Details Succesfully Added")

			return redirect('customer:customerbookingcleaningphase4')

		else:
			messages.error(request,get_error(customer_form))
			return render(request,'customer/booking/cleaningbookingphase3.html',{})

class CustomerBookingCleaningPhase4(View):
	def get(self,request):
		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		try:
			locations = AreaType.objects.filter(is_active=True)
		except:
			locations = None

		customer_booking = CustomerBooking.objects.select_related('evaluation__customer').get(booking_id=request.COOKIES['booking_id'])		

		active_addresses = Address.objects.filter(is_active=True,currently_active=True,customer=customer_booking.evaluation.customer)

		return render(request,'customer/booking/cleaningbookingphase4.html',{"governorates":governorates,"locations":locations,"active_addresses":active_addresses})

	def post(self,request):

		booking_details = CustomerBooking.objects.select_related('evaluation__customer').get(booking_id=request.COOKIES['booking_id'])

		#EXISTING ADDRESS OR NEW address
		try:
			update_address = Address.objects.get(id=request.POST.get('address_id'))
		except:
			update_address = None

		if update_address:
			address_form              = AddressForm(request.POST,instance=update_address)
		else:
			address_form              = AddressForm(request.POST)


		if address_form.is_valid():
			###save address details###
			address_form_save                   = address_form.save(commit=False)
			address_form_save.customer          = booking_details.evaluation.customer
			address_form_save.currently_active  = True

			#string check
			block_text = address_form_save.block
			floor_text = address_form_save.floor
			street_text = address_form_save.street
			avenue_text = address_form_save.avenue

			is_block = block_text.find("Block")
			is_street= street_text.find("Street")

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
	
			###update address in evaluation details and order schedulers###		
			EvaluationDetails.objects.filter(evaluation=booking_details.evaluation).update(address=address_form_save,status='EVALUATED')
			OrderScheduler.objects.filter(order__evaluation=booking_details.evaluation).update(customer_address=address_form_save)

			###update Evaluation and Order###
			Evaluation.objects.filter(id=booking_details.evaluation.id).update(quatation_status='APPROVED',quatation_approved_date=timezone.now(),payment_method='PREPAID',payment_way='ONLINE',quatation_expiry_date=timezone.now()+timedelta(14))
			
			last_invoice_no  		 = Order.objects.filter(is_active=True).aggregate(t=Max('invoice_no'))['t']
			current_invoice_starting = str(timezone.now().year)
			if last_invoice_no:		
				if current_invoice_starting == last_invoice_no[0:4]:
					new_invoice_no 		 = str(int(last_invoice_no[4:]) + 1 )
					new_invoice_no 		 = last_invoice_no[0:-(len(new_invoice_no))]+new_invoice_no
				else:
					new_invoice_no 		 = str(timezone.now().year)+'00001'
			else:
				new_invoice_no 		 = str(timezone.now().year)+'00001'
			Order.objects.filter(evaluation=booking_details.evaluation).update(payment_status='PENDING',invoice_no=new_invoice_no,order_status='APPROVED_BY_CLIENT')
			
			messages.success(request,"Cleaning Booking Succesfully Completed")

			return redirect('customer:customerbookingcleaningphase5')
		else:
			try:
				governorates = Governorate.objects.filter(is_active=True)
			except:
				governorates = None

			try:
				locations = AreaType.objects.filter(is_active=True)
			except:
				locations = None

			customer_booking = CustomerBooking.objects.select_related('evaluation__customer').get(booking_id=request.COOKIES['booking_id'])		

			active_addresses = Address.objects.filter(is_active=True,currently_active=True,customer=customer_booking.evaluation.customer)
			
			return render(request,'customer/booking/cleaningbookingphase4.html',{'governorates':governorates,'locations':locations,'active_addresses':active_addresses})

class CustomerBookingCleaningPhase5(View):
	def get(self,request):
		customer_booking = CustomerBooking.objects.select_related('evaluation__customer').get(booking_id=request.COOKIES['booking_id'])		

		#invoice data		
		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(evaluation=customer_booking.evaluation,is_active=True)
		nonduplicate_schedules = []
		#Remove duplicates for subscription
		duplicate_schedules    = []
		for orderschedule in order.orderschedules:
			if orderschedule.order_scheduler_book in duplicate_schedules:
				pass
			else:	
				nonduplicate_schedules.append(orderschedule)	

			duplicate_schedules.append(orderschedule.order_scheduler_book)

		return render(request,'customer/booking/cleaningbookingphase5.html',{'order':order,'nonduplicate_schedules':nonduplicate_schedules,'customer_booking':customer_booking,})


class CustomerBookingCleaningDebitPay(View):
	def get(self,request):
		#evaluation id decryption
		evaluation_id_encrypted = request.GET.get("udf1")
		payment_mode      		= request.GET.get("udf2")
		booking_id 		  		= request.GET.get("udf3")
		amount_paid       		= float(request.GET.get("amt"))
		payment_result    		= request.GET.get("result")
	
		try:
			bookingdetails = CustomerBooking.objects.select_related('evaluation').get(booking_id=booking_id)
		except:
			bookingdetails = None
		
		try:
			order = Order.objects.get(evaluation=bookingdetails.evaluation)
		except:
			order = None

		#To Check Payment Done 
		payment_history_check = PaymentHistory.objects.filter(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid')).exists()	
		

		if order and payment_result == 'CAPTURED' and not payment_history_check:

			#Receipt Number
			receipt_no               = PaymentHistory.objects.filter(is_active=True,receipt_no__isnull=False).aggregate(t=Max('receipt_no'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_receipt_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_receipt_starting == int(str(receipt_no)[:4]):
				new_receipt_no = int(receipt_no)+1
			else:
				new_receipt_no = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')

			#payment history
			payment_history = PaymentHistory.objects.create(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid'),receipt_no=new_receipt_no,payment_gateway='DEBITCARD')	
			#payment calculations
			if payment_mode == 'prepaid' and order.amount_paid != order.total_amount:
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			order.save()		
			

			#scheduler update
			order_scheduler             = OrderScheduler.objects.filter(order=order).update(work_status = 'CLEANING_TEAM_ASSIGNED')

			#update booking details
			bookingdetails.is_bookingcompleted = True
			bookingdetails.save()

			#delete cookies data
			response = HttpResponse()
			response.delete_cookie('booking_id')

			return redirect('customer:payment-receipt','pvw'+str(evaluation_id_encrypted[0:11])+str(payment_history.id))

		else:

			return redirect('/customer/payment/failed/?udf1='+evaluation_id_encrypted+'&paymentid='+request.GET.get('paymentid')+'&ref='+request.GET.get('ref'))


def addpromocode(request):
	
	orderId = request.GET.get('orderId')
	couponcode = request.GET.get('promocode')

	order = Order.objects.get(is_active=True,id=int(orderId))
	evaluation = order.evaluation

	#check if evaluation already has a promocode applied
	if evaluation.is_promocode_applied == False:
	
		try:
			promocode = Promocode.objects.filter(promocode=couponcode,is_active=True).first()
			
			#checking if promocode usage count is completed or date expired
			if promocode.total_usage == promocode.total_used or promocode.expiry_date <= date.today() :
				print("out")
				response_dict = {'success':False,'alert':'expired'}
			else:
				if promocode.percentage:
					print("wa")
					percentage = promocode.percentage
					order_amount = order.total_amount
					promocode_amount = float(promocode.percentage/100) * float(order_amount)

					if promocode_amount > promocode.percentage_upto_price:
						promocode_amount = promocode.percentage_upto_price

				elif promocode.price:
					print("warr")
					promocode_amount = promocode.price

				else:
					pass

				print(promocode_amount,"proamount")
				discount_amount = float(order.total_amount) - float(promocode_amount)
				discount_amount = round(discount_amount, 3)
				print(promocode_amount,discount_amount,"disc")

				#splitting offer amount into two and applying to before cleaning and after cleaning amount
				#if after coupon apply amount is 0 or less
				if discount_amount <= 0 and evaluation.payment_method != 'BREAKDOWN':

					evaluation.total_cost = 0.000
					evaluation.is_promocode_applied = True
					evaluation.promocode_amount = order.total_amount
					evaluation.save()

					promocode_amount = 0.000
					discount_amount = 0.000

					order.total_amount = 0.000
					order.remining_amount = 0.000
					order.payment_status = 'COMPLETED'
					order.save()

					####to close order
					order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=order.id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
					if order_closing_check:
						closing_order	= Order.objects.get(is_active=True,order_no=order.order_no)
						closing_order.order_status = 'ORDER_CLOSED'
						closing_order.save()					
					
					invoice_redirect = 'yes'

					response_dict = {'success':True,'amount':promocode_amount,'discount_amount':discount_amount,'preamount':evaluation.before_cleaning_amount,'redirect':invoice_redirect,
					'postamount':evaluation.after_cleaning_amount,'evaluationtotalcost':evaluation.total_cost,'remainingamount':order.remining_amount,'subscriptiontopay':order.subscription_topay}

				else:
					if evaluation.payment_method == 'BREAKDOWN':
						print("wa")
						#breakdown 2nd payment and coupon price
						if order.preamount_paid > 0 and promocode.price:
							postamount = float(evaluation.after_cleaning_amount) - float(promocode_amount)
							print(postamount,"postt")
							#if coupon amount is greater than payable amount
							if postamount <= 0 :
								order.total_amount = evaluation.before_cleaning_amount
								order.remining_amount = 0.000
								order.payment_status = 'COMPLETED'
								order.save()

								evaluation.total_cost = evaluation.before_cleaning_amount
								evaluation.promocode_amount = evaluation.after_cleaning_amount
								evaluation.after_cleaning_amount = 0.000
								evaluation.is_promocode_applied = True
								evaluation.save()

								####to close order
								order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=order.id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
								if order_closing_check:
									closing_order	= Order.objects.get(is_active=True,order_no=order.order_no)
									closing_order.order_status = 'ORDER_CLOSED'
									closing_order.save()

								invoice_redirect = 'yes'
							else:
								evaluation.after_cleaning_amount = float(evaluation.after_cleaning_amount) - float(promocode_amount)
								evaluation.total_cost = float(evaluation.total_cost) - float(promocode_amount)
								evaluation.is_promocode_applied = True
								evaluation.promocode_amount = round(promocode_amount, 3)
								evaluation.save()

								order.total_amount = float(order.total_amount) - float(promocode_amount)
								order.remining_amount = evaluation.after_cleaning_amount
								order.save()
								invoice_redirect = 'no'

						#breakdown 2nd payment and coupon percentage
						elif order.preamount_paid > 0 and promocode.percentage:
							promocode_amount = float(promocode.percentage/100) * float(order.total_amount)
							postamount = float(evaluation.after_cleaning_amount) - float(promocode_amount)

							#if coupon amount is greater than payable amount
							if postamount <= 0 :
								order.total_amount = evaluation.before_cleaning_amount
								order.remining_amount = 0.000
								order.payment_status = 'COMPLETED'
								order.save()

								evaluation.total_cost = evaluation.before_cleaning_amount
								evaluation.promocode_amount = evaluation.after_cleaning_amount
								evaluation.after_cleaning_amount = 0.000
								evaluation.is_promocode_applied = True
								evaluation.save()

								####to close order
								order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=order.id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
								if order_closing_check:
									closing_order	= Order.objects.get(is_active=True,order_no=order.order_no)
									closing_order.order_status = 'ORDER_CLOSED'
									closing_order.save()
									
								invoice_redirect = 'yes'
							
							else:
								evaluation.after_cleaning_amount = float(evaluation.after_cleaning_amount) - float(promocode_amount)
								evaluation.total_cost = float(evaluation.total_cost) - float(promocode_amount)
								evaluation.is_promocode_applied = True
								evaluation.promocode_amount = round(promocode_amount, 3)
								evaluation.save()

								order.total_amount = float(order.total_amount) - float(promocode_amount)
								order.remining_amount = evaluation.after_cleaning_amount
								order.save()
								invoice_redirect = 'no'
						#if promo code is applied at first payment of breakdown
						else:
							amount1	= round(float(discount_amount/2),3)
							amount2 = round(float(discount_amount)-float(amount1),3)
							evaluation.before_cleaning_amount = amount1
							evaluation.after_cleaning_amount = amount2
							evaluation.total_cost = discount_amount
							evaluation.is_promocode_applied = True
							evaluation.promocode_amount = round(promocode_amount, 3)
							evaluation.save()

							order.total_amount = discount_amount
							order.remining_amount = float(discount_amount) - float(order.amount_paid)
							order.save()

							invoice_redirect = 'no'

					#prepaid, postpaid, subscription
					else:
						order.total_amount = discount_amount
						order.remining_amount = float(discount_amount) - float(order.amount_paid)
						order.save()

						evaluation.total_cost = discount_amount
						evaluation.is_promocode_applied = True
						evaluation.promocode_amount = round(promocode_amount, 3)
						evaluation.save()	

						invoice_redirect = 'no'

					response_dict = {'success':True,'amount':promocode_amount,'discount_amount':discount_amount,'preamount':evaluation.before_cleaning_amount,'redirect':invoice_redirect,
					'postamount':evaluation.after_cleaning_amount,'evaluationtotalcost':evaluation.total_cost,'remainingamount':order.remining_amount,'subscriptiontopay':order.subscription_topay}				

				promocode.total_used += 1
				promocode.save()
				
				print(response_dict,"in")
		except:
			promocode = None
			response_dict = {'success':False,'alert':'Invalid'}

	else:
		response_dict = {'success':False,'alert':'exists'}
	print(orderId,couponcode,"codesss")

	return JsonResponse(response_dict)


######Client Booking#####
class ClientCleaningBookingPhase1(View):
	def get(self,request):
		
		try:
			service_types = ServiceType.objects.filter(is_active=True)
		except:
			service_types = None

		try:
			area_types = AreaType.objects.filter(is_active=True)
		except:
			area_types = None

		return render(request,'customer/booking/clientcleaningbookingphase1.html',{"service_types":service_types,"area_types":area_types,})