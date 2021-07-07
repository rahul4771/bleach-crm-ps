from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import HttpResponse,JsonResponse
from django_countries import countries

from django.views import View

from bleach_crm_ps.utils import get_error
from agent.views import generate_random_username

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


from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule
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

#restframe work 
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK 

from customer.serilizers import UserProfileSerializer,AddressSerializer,AddressSaveSerializer,EvaluationBookSerializer,EvaluationBookSectionSerializer,EvaluationSectionKeynoteSerializer,EvaluationSerializer,OrderSerializer,EvaluationDetailsSerializer,CustomerBookingSerializer

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
class Cart(View):
	def get(self,request):
		return render(request,"customer/cart.html",{})

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

		#update order & evaluation if credit exist
		if order.evaluation.customer.credit_amount > 0 and order.evaluation.credit_amount == 0 and order.order_status == None:
			total_amount                = order.evaluation.total_cost-order.evaluation.customer.credit_amount
			if total_amount > 0:
				order.evaluation.credit_amount          = order.evaluation.customer.credit_amount
				order.evaluation.total_cost             = total_amount
				
				order.total_amount                      = total_amount
				order.remining_amount                   = total_amount

				order.evaluation.customer.credit_amount = 0

				order.evaluation.customer.save()
				order.evaluation.save()
				order.save()
			else:
				order.evaluation.credit_amount          = order.evaluation.total_cost
				order.evaluation.total_cost             = 0

				order.total_amount                      = 0
				order.remining_amount                   = 0
				order.payment_status                    = 'COMPLETED'

				order.evaluation.customer.credit_amount = abs(total_amount)
				
				order.evaluation.customer.save()
				order.evaluation.save()
				order.save()


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
				
				 
				order = Order.objects.select_related('evaluation__customer').get(order_no=evaluation_id)
				#check credit
				if order.evaluation.customer.credit_amount != 0:
					if order.evaluation.total_cost-order.evaluation.customer.credit_amount >= 0:
						order.total_amount                       -= order.evaluation.customer.credit_amount
						order.remining_amount                    -= order.evaluation.customer.credit_amount

						order.evaluation.total_cost              -= order.evaluation.customer.credit_amount
						order.evaluation.credit_amount            = order.evaluation.customer.credit_amount

						order.evaluation.customer.credit_amount   = 0
					else:
						order.total_amount                        = 0
						order.remining_amount                     = 0

						order.evaluation.total_cost               = 0
						order.evaluation.credit_amount            = order.evaluation.total_cost

						order.evaluation.customer.credit_amount  -= order.evaluation.total_cost
					order.evaluation.customer.save()
					order.evaluation.save()
					order.save()
					
				#close payment if remining becomes zero
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
		
		#update order & evaluation if credit exist
		if order.evaluation.customer.credit_amount > 0 and order.evaluation.credit_amount == 0 and order.order_status == None:
			total_amount                = order.evaluation.total_cost-order.evaluation.customer.credit_amount
			if total_amount > 0:
				order.evaluation.credit_amount          = order.evaluation.customer.credit_amount
				order.evaluation.total_cost             = total_amount
				
				order.total_amount                      = total_amount
				order.remining_amount                   = total_amount

				order.evaluation.customer.credit_amount = 0

				order.evaluation.customer.save()
				order.evaluation.save()
				order.save()
			else:
				order.evaluation.credit_amount          = order.evaluation.total_cost
				order.evaluation.total_cost             = 0

				order.total_amount                      = 0
				order.remining_amount                   = 0
				order.payment_status                    = 'COMPLETED'

				order.evaluation.customer.credit_amount = abs(total_amount)
				
				order.evaluation.customer.save()
				order.evaluation.save()
				order.save()
				
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
class BleachCustomerInvoice(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True),to_attr='booksections')),to_attr='evaluationbooks')),to_attr='evaluationdetails')).get(is_active=True,evaluation__evaluation_id=evaluation_id,evaluation__customer__username=user_name)

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

		return render(request,"customer/bleach-invoice.html",{'order':order,'firstname':firstname,'lastname':lastname,'customer_ip_address':customer_ip_address,})		

	def post(self,request,evaluation_id):

		action            = request.POST.get('action_type')
		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		if action == 'CASH/CHEQUE':
			Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(payment_way='CASH/CHEQUE')
			messages.success(request,"Cash/Cheque payment method approved !")

		return redirect('customer:bookinginvoice',evaluation_id_encrypted)


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
		order_status      = request.GET.get("udf3")

		try:
			order = Order.objects.select_related('evaluation').get(order_no=evaluation_id,evaluation__customer__username=user_name)
		except:
			order = None	

		#To Check Payment Done 
		payment_history_check = PaymentHistory.objects.filter(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid')).exists()	
		

		if order and payment_result == 'CAPTURED' and not payment_history_check and order_status != 'CANCEL_IN_PROGRESS':

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
				order.remining_amount   = order.remining_amount-amount_paid
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
				order.postamount_paid  += amount_paid
				order.amount_paid      += amount_paid
				order.remining_amount   = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'prepaid' and order.amount_paid != order.total_amount:
				order.amount_paid       += amount_paid
				order.remining_amount   = order.remining_amount-amount_paid					

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'postpaid' and order.amount_paid != order.total_amount:
				order.amount_paid      += amount_paid
				order.remining_amount   = order.remining_amount-amount_paid

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

			try:
				booking_completed = CustomerBooking.objects.filter(evaluation=evaluation).update(is_bookingcompleted=True)
			except:
				booking_completed = None
				
			return redirect('customer:payment-receipt','pvw'+str(evaluation_id_encrypted[0:11])+str(payment_history.id))

		elif order and payment_result == 'CAPTURED' and not payment_history_check and order_status == 'CANCEL_IN_PROGRESS':
			#Receipt Number
			receipt_no               = PaymentHistory.objects.filter(is_active=True,receipt_no__isnull=False).aggregate(t=Max('receipt_no'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_receipt_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_receipt_starting == int(str(receipt_no)[:4]):
				new_receipt_no = int(receipt_no)+1
			else:
				new_receipt_no = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')

			#payment history
			payment_history = PaymentHistory.objects.create(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid'),receipt_no=new_receipt_no,payment_gateway='DEBITCARD')

			order.remining_amount  = 0
			order.amount_paid     += amount_paid
			order.save()
			
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

		return render(request,"customer/feedback.html",{"order":order, "questions":questions, "feedback_exist":feedback_exist})

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

from weasyprint import HTML,CSS


def quatation_html_to_pdf_view(request,evaluation_id):

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
    
	#Main Content
	if order.evaluation.payment_method == 'SUBSCRIPTION':
		#per job cost
		per_job_cost = 0
		for orderschedule in nonduplicate_schedules:            
			for section in orderschedule.order_scheduler_book.evaluationbooksection:
				per_job_cost += section.section_cost

		html_string = render_to_string("customer/downloads/quatation.html",{"order":order,"nonduplicate_schedules":nonduplicate_schedules,"per_job_cost":per_job_cost})
	else:
		html_string = render_to_string('customer/downloads/quatation.html',{"order":order,"nonduplicate_schedules":nonduplicate_schedules})
	
	html     = HTML(string=html_string,base_url=request.build_absolute_uri())
	main_doc = html.render()

	main_doc.write_pdf(target='/home/pdf/tmp/quatation/quatation.pdf');

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
	# html.write_pdf(target='/home/ansab/Desktop/orderdetails.pdf'); 
	html.write_pdf(target='/home/pdf/tmp/orderdetails/orderdetails.pdf'); 

	# fs = FileSystemStorage('/home/ansab/Desktop/')
	fs = FileSystemStorage('/home/pdf/tmp/orderdetails/')
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

	# return render(request,"customer/customer_invoice.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,'firstname':firstname,'lastname':lastname,'customer_ip_address':customer_ip_address,})
    

	html_string = render_to_string("customer/downloads/invoice.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,'completed_jobs_count':completed_jobs_count})

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


def statement_of_account_old(request,client_id):
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

def statement_of_account(request,client_id):
	customer = UserProfile.objects.get(is_active=True,id=int(client_id))
	address = Address.objects.filter(customer__id=int(client_id)).first()

	orders = Order.objects.filter(is_active=True,evaluation__customer__id=client_id).order_by('created').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'))
	print(orders,"ods")
	customer_orders = Order.objects.filter(is_active=True).order_by('evaluation__quatation_approved_date').filter(evaluation__customer__id=int(client_id),evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='evaluationdetails'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
	
	accounts_list = []

		
	for order in customer_orders:
		if order.evaluation.payment_method != 'SUBSCRIPTION' and order.order_status == 'ORDER_CLOSED':
			accounts_list.append({
						"date":order.created.date(),
						"invoice_no":order.order_no,
						"details":"Cleaning Services",
						"amount":order.total_amount,
						"credit":order.amount_paid,
						"debit":""
					})

			for payment in order.paymenthistory:
				if payment:
					if payment.payment_mode == 'CASH':
						details = 'CASH'
					elif payment.payment_mode == 'CHEQUE':
						details = payment.check_no
					elif payment.payment_mode == 'BANK':
						details = payment.bank_name
					else:
						details = payment.payment_gateway

					accounts_list.append({
							"date":payment.created.date(),
							"invoice_no":payment.payment_mode,
							"details":details,
							"amount":"",
							"credit":"",
							"debit":payment.amount_paid
						})

		elif order.evaluation.payment_method == 'SUBSCRIPTION' and order.order_status == 'ORDER_IN_PROGRESS' or order.order_status == 'ORDER_CLOSED':
			
			evaluationbooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation__id=order.evaluation.id)
			evaluationbooks_count = evaluationbooks.count()

			job_completed = 0
			job_remaining = 0

			for book in evaluationbooks:
				cleanings_count = OrderScheduler.objects.filter(is_active=True,order__id=order.id,order_scheduler_book__id=book.id).count()
				completed_cleanings = OrderScheduler.objects.filter(is_active=True,order__id=order.id,order_scheduler_book__id=book.id,work_status='CLEANING_FULFILLED')
				completed_cleanings_count = completed_cleanings.count()

				total_cost = book.total_cost

				per_cleaning_amount = float(book.total_cost/cleanings_count)
				job_completed += float(per_cleaning_amount*completed_cleanings_count)
				# job_remaining += float(book.total_cost - job_completed)	

				if order.evaluation.fine_amount:
					job_completed -= float(order.evaluation.fine_amount/cleanings_count)

				if order.evaluation.writeback_amount:
					job_completed -= float(order.evaluation.writeback_amount/cleanings_count)

				if order.evaluation.promocode_amount:
					job_completed -= float(order.evaluation.promocode_amount/cleanings_count)
			
			accounts_list.append({
						"date":order.created.date(),
						"invoice_no":order.order_no,
						"details":"Cleaning Services",
						"amount":order.total_amount,
						"credit":job_completed,
						"debit":""
					})

			for payment in order.paymenthistory:
				if payment:
					if payment.payment_mode == 'CASH':
						details = 'CASH'
					elif payment.payment_mode == 'CHEQUE':
						details = payment.check_no
					elif payment.payment_mode == 'BANK':
						details = payment.bank_name
					else:
						details = payment.payment_gateway

					accounts_list.append({
							"date":payment.created.date(),
							"invoice_no":payment.payment_mode,
							"details":details,
							"amount":"",
							"credit":"",
							"debit":payment.amount_paid
						})
		else:
			pass
	
	return render(request,"customer/soa_test.html",{"customer":customer,"address":address,"orders":accounts_list})

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

					if promocode.percentage_upto_price and promocode_amount > promocode.percentage_upto_price:
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




####Customer Evaluation Booking########
from django.forms.models import model_to_dict

class GetEvaluationBookingSlotes(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	
	def get(self,request):
		dropdown_slotes  = {}
		dropdown_slotes['success'] = False

		evaluation_date  = datetime.strptime(request.GET.get('evaluation_booking_date'),'%d-%m-%Y')
		
		available_slotes = []
		for slote in range(0,24):
			slote_datetime 			  = evaluation_date.replace(hour=slote,minute=0,second=0,microsecond=0)
			checkavailability         = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR',is_onlineevaluator=True).prefetch_related('evaluator_evaluation').annotate(busyevaluationcount=Sum(Case(When(evaluator_evaluation__proposed_time=slote_datetime,then=1),default=0,output_field=IntegerField()))).filter(busyevaluationcount__lt=2)
			if checkavailability:
				available_slotes.append(slote)

		dropdown_slotes['slotes']   = available_slotes
		
		dropdown_slotes['success']  = True
		
		return JsonResponse(dropdown_slotes)	


class CustomerBookingPhase1(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		response_dict = {}
		response_dict['success'] = False

		proposed_date                     = request.data.get('booking_date')
		proposed_time                     = request.data.get('booking_time')
		converted_proposed_time           = datetime.strptime(proposed_date+" "+proposed_time,'%d-%m-%Y %I:%M %p')	
		#available evaluator
		availableevaluators               = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR',is_onlineevaluator=True).prefetch_related('evaluator_evaluation').annotate(busyevaluationcount=Sum(Case(When(evaluator_evaluation__proposed_time=converted_proposed_time,then=1),default=0,output_field=IntegerField()))).filter(busyevaluationcount__lt=2)
	

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

			response_dict['evaluation_id']  = evaluation_details.id
			response_dict['booking_id']     = customerbooking.id
			response_dict['success']        = True
		else:
			response_dict['Error']          = "Evaluators not Available...Please Change date or Slote !"
		
		return Response(response_dict,HTTP_200_OK)	

class CustomerBookingEvaluationPhase2(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		response_dict            = {}
		response_dict['success'] = False

		evaluationdetails_id = request.data.get('evaluation_id')
		customerbooking_id   = request.data.get('booking_id')

		#save customer details
		try:
			existing_customer = UserProfile.objects.get(id=request.data.get('customer_id'))
		except:
			existing_customer = None

		if existing_customer:
			customer_saveupdate_serializer = UserProfileSerializer(data=request.data.get('customer_details'),instance=existing_customer)
		else:
			customer_saveupdate_serializer = UserProfileSerializer(data=request.data.get('customer_details'))


		if customer_saveupdate_serializer.is_valid():   
			
			#username generation and customer_id generation
			if existing_customer:
				user_name                      = existing_customer.username
				new_customer_id                = existing_customer.customer_id
			else:
				user_name                      = generate_random_username()
				customer_id                    = UserProfile.objects.filter(is_active=True,customer_id__isnull=False).aggregate(t=Max('customer_id'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'1000')
				current_customer_id_starting   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2))					
				if current_customer_id_starting == int(str(customer_id)[:4]):
					new_customer_id = int(customer_id)+1
				else:
					new_customer_id   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2)+'1001')

			#contact platform
			contact_platform               = request.data.get('customer_details')['contact_platform']
			contact_platform_list 	       = contact_platform.split(",")
			if contact_platform_list:
				is_whatsapp = False
				is_email    = False
				is_sms      = False
				for contact_platform in contact_platform_list:
					if contact_platform == 'Whatsapp':
						is_whatsapp = True
					elif contact_platform == 'Email':
						is_email    = True
					else:
						is_sms      = True

			savedupdated_customer = customer_saveupdate_serializer.save(is_whatsapp=is_whatsapp,is_sms=is_sms,is_email=is_email,username=user_name,user_type='CUSTOMER',customer_id=new_customer_id)       
		
		else: 
			errors= customer_saveupdate_serializer.errors   
			key=tuple(errors.keys())[0] 
			error=errors[key]
			response_dict['customerdetails_Error']=key +':'+ error[0]
			response_dict['customerdetails_Error_List'] = customer_saveupdate_serializer.errors

			response_dict['customerdetails_success']  = False

			return Response(response_dict,HTTP_200_OK)

		#create address or update address
		try:
			existing_address = Address.objects.get(id=request.data.get('address_id'))
		except:
			existing_address = None

		if existing_address:
			address_saveupdate_serializer = AddressSaveSerializer(data=request.data.get('address_details'),instance=existing_address)
		else:
			address_saveupdate_serializer = AddressSaveSerializer(data=request.data.get('address_details'))

		if address_saveupdate_serializer.is_valid():
			savedupdated_address = address_saveupdate_serializer.save(customer=savedupdated_customer,currently_active=True)

			response_dict['customeraddress_success']  = True
		else:
			errors= address_saveupdate_serializer.errors   
			key=tuple(errors.keys())[0] 
			error=errors[key]
			response_dict['customeraddress_Error']=key +':'+ error[0]
			response_dict['customeraddress_Error_List'] = customer_saveupdate_serializer.errors

			response_dict['customeraddress_success']  = False

			return Response(response_dict,HTTP_200_OK)
		
		###update Evaluation###
		evaluation_details                     = EvaluationDetails.objects.select_related('evaluation').get(id=evaluationdetails_id)
		evaluation_details.evaluation.customer = savedupdated_customer
		evaluation_details.address  = savedupdated_address
		evaluation_details.evaluation.save()
		evaluation_details.save()
		
		###booking update###
		customer_booking                     = CustomerBooking.objects.get(id=customerbooking_id)
		customer_booking.is_bookingcompleted = True
		customer_booking.save()

		response_dict['booking_id']         = customer_booking.id
		response_dict['evaluation_details'] = evaluation_details.id

		response_dict['success'] = True		
		return Response(response_dict,HTTP_200_OK)

class CustomerBookingEvaluationPhase3(APIView):

	def get(self,request):
		response_dict = {}
		response_dict['success'] = False

		booking_id                       = request.GET.get('booking_id')
		booking_details                  = CustomerBooking.objects.get(id=booking_id)
		response_dict['booking_details'] = CustomerBookingSerializer(booking_details).data

		evaluationdetails_id                = request.GET.get('evaluationdetails_id')
		evaluation_details                  = EvaluationDetails.objects.get(id=evaluationdetails_id)
		response_dict['evaluation_details'] = EvaluationDetailsSerializer(evaluation_details).data

		response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)		

######Client Booking#####
#Username Random Generation
def generate_random_otp(size=5, chars=string.digits):

	otp = ''.join(random.choice(chars) for n in range(size))


	try:
		UserProfile.objects.get(address_otp=otp)
		return generate_random_otp(size=5,chars=string.digits)
	except UserProfile.DoesNotExist:
		return otp

class GetCountries(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict        		= {}
		response_dict['success']	= False

		djangocountries =[]
		for code, name in list(countries):
			djangocountries.append({'country':name,'code':code})
		response_dict['countries']=	djangocountries

		response_dict['success']	= True
		return JsonResponse(response_dict)

class ExistingMobileCheck(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict        		= {}
		response_dict['success']	= False

		mobile_number               = request.GET.get('mobile_number')
		existing_customer           = UserProfile.objects.filter(mobile_number=mobile_number)
		
		if not existing_customer:
			response_dict['success']	= True

		return JsonResponse(response_dict)

class GetServiceTypes(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict        		= {}
		response_dict['susccess']	= False

		try:
			service_types = ServiceType.objects.filter(is_active=True)
		except:
			service_types = None

		service_typeslist = []
		for service_type in service_types:
			service_typeslist.append({'name':service_type.name,'id':service_type.id})

		response_dict['service_types']	= service_typeslist
		response_dict['susccess']		= True

		return JsonResponse(response_dict)

class GetGovernorates(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict        		= {}
		response_dict['success']	= False

		try:
			governorates = Governorate.objects.filter(is_active=True)
		except:
			governorates = None

		governorate_list = []
		for governrate in governorates:
			governorate_list.append({'name':governrate.name,'id':governrate.id})

		response_dict['governorates']	= governorate_list
		response_dict['success']    = True

		return JsonResponse(response_dict)

class GetAreas(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict        		= {}
		response_dict['success']	= False

		try:
			areas = Area.objects.select_related('governorate').filter(governorate__id=request.GET.get('governorate_id'))
		except:
			areas = None

		area_list = []
		for area in areas:
			area_list.append({'name':area.name,'id':area.id})

		response_dict['areas']	= area_list
		response_dict['success']= True

		return JsonResponse(response_dict)


class GetAreaTypes(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict        		= {}
		response_dict['success']	= False

		try:
			area_types = AreaType.objects.filter(is_active=True)
		except:
			area_types = None

		area_typeslist = []
		for area_type in area_types:
			area_typeslist.append({'name':area_type.name,'id':area_type.id})

		response_dict['area_types']	= area_typeslist
		response_dict['success']    = True

		return JsonResponse(response_dict)

class GetServiceSizePrice(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		service_type         = request.GET.get('service_type')
		response_dict        = {}
		service_price_ranges = ServicePriceRange.objects.filter(service_type__name=service_type)
		print(service_type,"service_type")
		print(service_price_ranges)

		counter = 1
		for service_price_range in service_price_ranges:
			service_price_range_dict = {}
			service_price_range_dict['name']     = service_price_range.name
			service_price_range_dict['min_size'] = service_price_range.minimum_area
			service_price_range_dict['max_size'] = service_price_range.maximum_area
			service_price_range_dict['cost']     = service_price_range.price
			
			if service_price_range.service_type.name   == 'Upholstery Cleaning':
				service_price_range_dict['upholstery_type']     = service_price_range.upholstery_type
				if service_price_range.upholstery_type == 'SOFA':
					service_price_range_dict['unit_price'] = service_price_range.unit_price
				elif service_price_range.upholstery_type == 'CHAIR':
					service_price_range_dict['unit_price'] = service_price_range.unit_price
				else:
					pass
			elif service_price_range.service_type.name == 'Window Cleaning':
				service_price_range_dict['is_highprice_window'] = service_price_range.is_highprice_window
			elif service_price_range.service_type.name == 'Facade Cleaning':
				service_price_range_dict['is_highprice_facade'] = service_price_range.is_highprice_facade 
			elif service_price_range.service_type.name == 'Kitchen Cleaning':
				service_price_range_dict['is_newkitchen']       = service_price_range.is_newkitchen

			response_dict[counter] = service_price_range_dict

			counter += 1
		print(response_dict)
		return JsonResponse(response_dict)


class GetServiceProductivity(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		service_productivity = {}
		service_type         = request.GET.get('service_type')

		if service_type         == 'Upholstery Cleaning':
			serviceproductivities = ServiceProductivity.objects.select_related('service_type').filter(service_type__name=service_type)
			for serviceproductivity in serviceproductivities:
				if serviceproductivity.upholstery_type == 'SOFA':
					service_productivity['sofa_perhour_cleaning']     = serviceproductivity.perhour_cleaning
				elif serviceproductivity.upholstery_type == 'CURTAIN':
					service_productivity['curtain_perhour_cleaning']  = serviceproductivity.perhour_cleaning
				else:
					service_productivity['chair_perhour_cleaning']    = serviceproductivity.perhour_cleaning

		elif service_type         == 'Window Cleaning':
			serviceproductivities = ServiceProductivity.objects.select_related('service_type').filter(service_type__name=service_type)
			for serviceproductivity in serviceproductivities:
				if serviceproductivity.is_highprice_window:
					service_productivity['highpricewindow_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				else:
					service_productivity['lowpricewindow_perhour_cleaning']  = serviceproductivity.perhour_cleaning
		
		elif service_type         == 'Facade Cleaning':
			serviceproductivities = ServiceProductivity.objects.select_related('service_type').filter(service_type__name=service_type)
			for serviceproductivity in serviceproductivities:
				if serviceproductivity.is_highprice_facade:
					service_productivity['highpricefacade_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				else:
					service_productivity['lowpricefacade_perhour_cleaning']  = serviceproductivity.perhour_cleaning
		
		elif service_type         == 'Kitchen Cleaning':
			serviceproductivities = ServiceProductivity.objects.select_related('service_type').filter(service_type__name=service_type)
			for serviceproductivity in serviceproductivities:
				if serviceproductivity.is_newkitchen:
					service_productivity['newkitchen_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				else:
					service_productivity['oldkitchen_perhour_cleaning']  = serviceproductivity.perhour_cleaning

		else:
			serviceproductivity = ServiceProductivity.objects.select_related('service_type').get(service_type__name=service_type)
			service_productivity['perhour_cleaning'] = serviceproductivity.perhour_cleaning

		if service_type   == 'General Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_general_skill=True).count()
		elif service_type == 'Deep Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_deep_skill=True).count()
		elif service_type == 'Upholstery Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_upholstery_skill=True).count()
		elif service_type == 'Kitchen Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_kitchen_skill=True).count()
		elif service_type == 'Carpet Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_carpet_skill=True).count()
		elif service_type == 'Sterilization':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_sterilization_skill=True).count()
		elif service_type == 'Mattress Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_deep_skill=True).count()
		elif service_type == 'Facade Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_facade_skill=True).count()
		elif service_type == 'Storage Area':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_storagearea_skill=True).count()
		elif service_type == 'Car Parking Umbrella':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_carparkingumbrella_skill=True).count()
		elif service_type == 'Window Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_window_skill=True).count()
		elif service_type == 'Outdoor Cleaning':
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))).filter(is_active=True,is_outdoor_skill=True).count()	
		else:
			total_cleaners = 0

		if total_cleaners > 0:
			total_cleaners = total_cleaners-1
		service_productivity['max_cleaners'] = total_cleaners

		return JsonResponse(service_productivity)


class GetCleaningSlotes(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		dropdown_slotes    = {}

		cleaning_date      = datetime.strptime(request.GET.get('cleaning_date'),'%d-%m-%Y')
		number_of_cleaners = int(request.GET.get('number_of_cleaners'))-1
		service_type       = request.GET.get('service_type')

		#count total cleaners and total leaders
		if service_type == 'General Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_general_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_general_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Deep Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_deep_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_deep_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Upholstery Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_upholstery_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_upholstery_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Kitchen Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_kitchen_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_kitchen_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Carpet Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_carpet_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_carpet_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Sterilization':
			total_cleaners 	= UserProfile.objects.filter(is_sterilization_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_sterilization_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Mattress Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_mattress_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_mattress_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Facade Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_facade_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_facade_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Storage Area':
			total_cleaners 	= UserProfile.objects.filter(is_storagearea_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_storagearea_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Car Parking Umbrella':
			total_cleaners 	= UserProfile.objects.filter(is_carparkingumbrella_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_carparkingumbrella_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Window Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_window_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_window_skill=True,user_type='TEAMINCHARGE')
		elif service_type == 'Outdoor Cleaning':
			total_cleaners 	= UserProfile.objects.filter(is_outdoor_skill=True).filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders 	= UserProfile.objects.filter(is_outdoor_skill=True,user_type='TEAMINCHARGE')
		
		#absent cleaners and leaders	
		absent_cleaners     = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
		absent_leaders      = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date,staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

		slotes           =[0,2,4,6,8,10,12,14,16,18,20,22]
		slote_durations  =[2,4,6,8,10]
		available_slotes = {}
		#slote wise checking
		for slote in slotes:
			available_durations = []
			for slote_duration in slote_durations:
				slote_start_datetime 			  = cleaning_date.replace(hour=slote,minute=0,second=0,microsecond=0)
				slote_end_datetime                = slote_start_datetime+timedelta(hours=slote_duration)
				slote_start_time 			      = slote_start_datetime.time()
				slote_end_time                    = slote_end_datetime.time()

				#included shift cleaners
				shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(shift_date=cleaning_date).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
				shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(shift_date=cleaning_date).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
				today_shifts        = ShiftSchedule.objects.select_related('staff').filter(shift_date=cleaning_date).values_list('staff',flat=True)
				super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
				super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)

				total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).count()-1
				total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))).count()-1

				if service_type == 'General Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_general_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_general_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Deep Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_deep_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_deep_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Upholstery Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_upholstery_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_upholstery_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Kitchen Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_kitchen_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_kitchen_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Carpet Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_carpet_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(slote_end_datetimee__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_carpet_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(slote_end_datetimee__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Sterilization':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_sterilization_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_sterilization_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Mattress Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_mattress_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_mattress_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Facade Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_facade_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_facade_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Storage Area':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_storagearea_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_storagearea_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Car Parking Umbrella':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_carparkingumbrella_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_carparkingumbrella_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Window Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_window_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_window_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				elif service_type == 'Outdoor Cleaning':
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__is_outdoor_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__is_outdoor_skill=True).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))

				cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

				followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

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

				busy_leaders  = len(set(team_leaders_scheduled))
				busy_cleaners = len(set(team_members_scheduled))

				#slote appending
				if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
					available_durations.append(slote_duration)				
			
			available_slotes[slote] = available_durations

		dropdown_slotes['success']= True
		dropdown_slotes['slotes'] = available_slotes
		return Response(dropdown_slotes,HTTP_200_OK)

class GetMultipleServiceCleaningSlotes(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		dropdown_slotes  = {}

		cleaning_date       = datetime.strptime(request.data.get('cleaning_date'),'%d-%m-%Y')
		number_of_cleaners  = int(request.data.get('number_of_cleaners'))-1
		service_types       = request.data.get('service_types')
		
		#count total cleaners and total leaders
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		total_leaders  = UserProfile.objects.filter(user_type='TEAMINCHARGE')
		for service_type in service_types:
			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				total_leaders 	= total_leaders.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				total_leaders 	= total_leaders.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				total_leaders 	= total_leaders.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				total_leaders 	= total_leaders.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				total_leaders 	= total_leaders.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				total_leaders 	= total_leaders.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				total_leaders 	= total_leaders.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				total_leaders 	= total_leaders.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				total_leaders 	= total_leaders.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				total_leaders 	= total_leaders.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				total_leaders 	= total_leaders.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)
				total_leaders 	= total_leaders.filter(is_outdoor_skill=True)
		
		#absent cleaners and leaders	
		absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
		absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date,staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

		slotes           =[0,2,4,6,8,10,12,14,16,18,20,22]
		slote_durations  =[2,4,6,8,10]
		available_slotes = {}
		#slote wise checking
		for slote in slotes:
			available_durations = []
			for slote_duration in slote_durations:
				slote_start_datetime 			  = cleaning_date.replace(hour=slote,minute=0,second=0,microsecond=0)
				slote_end_datetime                = slote_start_datetime+timedelta(hours=slote_duration)
				slote_start_time 			      = slote_start_datetime.time()
				slote_end_time                    = slote_end_datetime.time()

				#included shift cleaners
				shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(shift_date=cleaning_date).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
				shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(shift_date=cleaning_date).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
				today_shifts        = ShiftSchedule.objects.select_related('staff').filter(shift_date=cleaning_date).values_list('staff',flat=True)
				super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
				super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)

				total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners).count()-1
				total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))).exclude(id__in=absent_leaders).count()

				active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))

				for service_type in service_types:
					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)

				cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

				followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

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

				busy_leaders  = len(set(team_leaders_scheduled))
				busy_cleaners = len(set(team_members_scheduled))

				#slote appending
				if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
					available_durations.append(slote_duration)				
			
			available_slotes[slote] = available_durations

		dropdown_slotes['success']= True
		dropdown_slotes['slotes'] = available_slotes
		return Response(dropdown_slotes,HTTP_200_OK)

class GetMultipleServiceDateCleaningSlotes(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		dropdown_slotes  = {}
		number_of_cleaners  = int(request.data.get('number_of_cleaners'))-1
		cleaning_hours      = float(request.data.get('cleaning_hours'))
		service_types       = request.data.get('service_types')
		     

		#count total cleaners and total leaders
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		total_leaders  = UserProfile.objects.filter(user_type='TEAMINCHARGE')
		for service_type in service_types:
			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				total_leaders 	= total_leaders.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				total_leaders 	= total_leaders.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				total_leaders 	= total_leaders.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				total_leaders 	= total_leaders.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				total_leaders 	= total_leaders.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				total_leaders 	= total_leaders.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				total_leaders 	= total_leaders.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				total_leaders 	= total_leaders.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				total_leaders 	= total_leaders.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				total_leaders 	= total_leaders.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				total_leaders 	= total_leaders.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)
				total_leaders 	= total_leaders.filter(is_outdoor_skill=True)
		

		available_slotes = []
		busy_slotes      = []
		#Test on multiple date 
		cleaning_datetimes      = request.data.get('cleaning_datetimes')
		
		for cleaning_datetime in cleaning_datetimes:
			team_leaders_scheduled      = []
			team_members_scheduled      = []

			slote_start_datetime 			  = datetime.strptime(cleaning_datetime,'%d-%m-%Y %I:%M %p')
			slote_end_datetime                = slote_start_datetime+timedelta(hours=cleaning_hours)
			slote_start_time 			      = slote_start_datetime.time()
			slote_end_time                    = slote_end_datetime.time()
			start_at_date                     = slote_start_datetime.date()
			end_at_date                       = slote_end_datetime.date()

			#absent cleaners and leaders	
			absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(leave_date=start_at_date)|Q(leave_date=end_at_date)).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
			absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(leave_date=start_at_date)|Q(leave_date=end_at_date)).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

			#included shift cleaners
			shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
			shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
			today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).values_list('staff',flat=True)
			super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
			super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)

			total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners).count()-1
			total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))).exclude(id__in=absent_leaders).count()
			
			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				
			for service_type in service_types:
				if service_type == 'General Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
				elif service_type == 'Sterilization':
					active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
				elif service_type == 'Storage Area':
					active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)

				cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

				followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

				#merging
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

			busy_leaders  = len(set(team_leaders_scheduled))
			busy_cleaners = len(set(team_members_scheduled))

			#slote availability				
			if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
				available_slotes.append(datetime.strftime(slote_start_datetime,'%d-%m-%Y %I:%M %p'))	
			else:
				busy_slotes.append(datetime.strftime(slote_start_datetime,'%d-%m-%Y %I:%M %p'))
		

		dropdown_slotes['available_slotes'] = available_slotes
		dropdown_slotes['busy_slotes']      = busy_slotes

		dropdown_slotes['success']          = True
		
		return Response(dropdown_slotes,HTTP_200_OK)


class GetMultipleServiceDateCleaningSlotesAutofix(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		dropdown_slotes  = {}
		number_of_cleaners  = int(request.data.get('number_of_cleaners'))-1
		cleaning_hours       = float(request.data.get('cleaning_hours'))
		service_types       = request.data.get('service_types')
		     

		#count total cleaners and total leaders
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		total_leaders  = UserProfile.objects.filter(user_type='TEAMINCHARGE')
		for service_type in service_types:
			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				total_leaders 	= total_leaders.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				total_leaders 	= total_leaders.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				total_leaders 	= total_leaders.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				total_leaders 	= total_leaders.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				total_leaders 	= total_leaders.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				total_leaders 	= total_leaders.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				total_leaders 	= total_leaders.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				total_leaders 	= total_leaders.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				total_leaders 	= total_leaders.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				total_leaders 	= total_leaders.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				total_leaders 	= total_leaders.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)
				total_leaders 	= total_leaders.filter(is_outdoor_skill=True)
		

		slote_details = {}

		#Test on multiple date for multiple slotes
		cleaning_datetimes      = request.data.get('cleaning_datetimes')
		slote_checkings         = [2,-2,4,-4,6,-6,8,-8,10,-10,12,-12,14,-14,16,-16,18,-18,20,-20,22,-22]

		for cleaning_datetime in cleaning_datetimes:
			actual_cleaningdate = datetime.strptime(cleaning_datetime,'%d-%m-%Y %I:%M %p').date() 
			for slote_checking in slote_checkings:
				team_leaders_scheduled      = []
				team_members_scheduled      = []

				slote_start_datetime 			  = datetime.strptime(cleaning_datetime,'%d-%m-%Y %I:%M %p')+timedelta(hours=slote_checking)
				slote_end_datetime                = slote_start_datetime+timedelta(hours=cleaning_hours)
				slote_start_time 			      = slote_start_datetime.time()
				slote_end_time                    = slote_end_datetime.time()
				start_at_date                     = slote_start_datetime.date()
				end_at_date                       = slote_end_datetime.date()

				#absent cleaners and leaders	
				absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
				absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_at_date)|Q(leave_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

				#included shift cleaners
				shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
				shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time)))).values_list('staff',flat=True)
				today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date))).values_list('staff',flat=True)
				super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
				super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)

				total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners).count()-1
				total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))).exclude(id__in=absent_leaders).count()
				
				if start_at_date == actual_cleaningdate and end_at_date == actual_cleaningdate:				

					#active cleaners
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime))|Q(Q(end_at__gte=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
						
					for service_type in service_types:
						if service_type == 'General Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
						elif service_type == 'Deep Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
						elif service_type == 'Upholstery Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
						elif service_type == 'Kitchen Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						elif service_type == 'Carpet Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
						elif service_type == 'Sterilization':
							active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
						elif service_type == 'Mattress Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
						elif service_type == 'Facade Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
						elif service_type == 'Storage Area':
							active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
						elif service_type == 'Car Parking Umbrella':
							active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
						elif service_type == 'Window Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
						elif service_type == 'Outdoor Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)

						cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
						cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

						followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
						followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

						#merging
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

					busy_leaders  = len(set(team_leaders_scheduled))
					busy_cleaners = len(set(team_members_scheduled))

					#slote availability				
					if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
						slote_details[cleaning_datetime] =	datetime.strftime(slote_start_datetime,'%d-%m-%Y %I:%M %p')
						break
					else:
						slote_details[cleaning_datetime] = 'NOt Available'
				else:
					slote_details[cleaning_datetime] = 'Not Available'

		dropdown_slotes['slote_details']    = slote_details
		dropdown_slotes['success']          = True
		
		return Response(dropdown_slotes,HTTP_200_OK)



def AddressOtpSend(request):
	response_dict = {}
	response_dict['success'] = False

	mobile_no  		= request.GET.get('mobile_number')
	address_otp 	= 12345
	otp_update 		= UserProfile.objects.filter(mobile_number=mobile_no).update(address_otp=address_otp)

	if otp_update:
		response_dict['success'] = True
	else:
		response_dict['Error']   = 'mobile number doesnot exist'
	
	return JsonResponse(response_dict)

def AddressOtpVerify(request):
	response_dict = {}
	response_dict['success'] = False
	
	address_otp    		= request.GET.get('address_otp')
	try:
		customer       		= UserProfile.objects.get(address_otp=address_otp)
	except:
		customer 			= None 
	if not customer:
		response_dict['Error']   = 'Invalid Otp'
		return JsonResponse(response_dict)
				
	customer_addresses	= Address.objects.filter(customer=customer,currently_active=True).select_related('governorate','area')
	if not customer_addresses:
		response_dict['Error']   = 'Address Doesnot Exist'
		return JsonResponse(response_dict)

	response_dict['customer_details']   = UserProfileSerializer(instance=customer).data
	response_dict['customer_addresses'] = AddressSerializer(instance=customer_addresses,many=True).data 
	
	response_dict['success'] = True
	return JsonResponse(response_dict)

def AddressOtpVerifyTest(request):
	response_dict = {}
	response_dict['success'] = False
	
	mobile_number    		= request.GET.get('mobile_number')
	try:
		customer       		= UserProfile.objects.get(mobile_number=mobile_number)
	except:
		customer 			= None 
	
	if not customer:
		response_dict['Error']   = 'Invalid Otp'
		return JsonResponse(response_dict)
				
	customer_addresses	= Address.objects.filter(customer=customer,currently_active=True).select_related('governorate','area')
	if not customer_addresses:
		response_dict['Error']   = 'Address Doesnot Exist'
		return JsonResponse(response_dict)

	response_dict['customer_details']   = UserProfileSerializer(instance=customer).data
	response_dict['customer_addresses'] = AddressSerializer(instance=customer_addresses,many=True).data 
	
	response_dict['success'] = True
	return JsonResponse(response_dict)

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


class ClientMultipleCleaningBookingPhase2(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request): 
		response_dict = {'success':False}

		##multiple services #count total cleaners and total leaders for availability
		total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		total_leaders   = UserProfile.objects.filter(is_general_skill=True,user_type='TEAMINCHARGE')
		
		for service_detail in services.keys():
			service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
			service_type   		= service.name

			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				total_leaders 	= total_leaders.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				total_leaders 	= total_leaders.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				total_leaders 	= total_leaders.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				total_leaders 	= total_leaders.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				total_leaders 	= total_leaders.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				total_leaders 	= total_leaders.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				total_leaders 	= total_leaders.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				total_leaders 	= total_leaders.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				total_leaders 	= total_leaders.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				total_leaders 	= total_leaders.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				total_leaders 	= total_leaders.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)
				total_leaders 	= total_leaders.filter(is_outdoor_skill=True)

		service_dict  = {}

		####allready half done or new quatation####
		try:
			booking_id         = request.data.get('booking_id')
			customerbooking    = CustomerBooking.objects.select_related('evaluation__customer').get(booking_id=booking_id,is_bookingcompleted=False)
		except:
			customerbooking    = None

		if not customerbooking:
			###testing availability ####
			test_schedules_dict = request.data.get('schedule_details')
				
			for key in test_schedules_dict.keys():
				schedule_date           =  test_schedules_dict[key]['date']
				schedule_time           =  test_schedules_dict[key]['time']

				start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
				end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours'])
				start_time              =  start_date_time.time()
				end_time                =  end_date_time.time()

				number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1
				
				#included shift cleaners
				shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
				shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
				today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
				super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
				super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

				#absent cleaners and leaders	

				absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
				absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)
				
				total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners).count()-1
				total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders).count()-1

				active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
				active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
				
				for service_detail in services.keys():
					service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
					service_type   		= service.name
	
					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)

				cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

				followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

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

				busy_leaders  = len(set(team_leaders_scheduled))
				busy_cleaners = len(set(team_members_scheduled))

				#slote appending
				if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
					pass
				else:
					response_dict['Error'] = 'Cleaners are not available'
					return Response(response_dict,HTTP_200_OK)


        	#create user or update user
			try:
				existing_customer    = UserProfile.objects.get(id=request.data.get('customer_id'))
			except:
				existing_customer    = None

			if existing_customer:
				customer_saveupdate_serializer = UserProfileSerializer(data=request.data.get('customer_details'),instance=existing_customer)
			else:
				customer_saveupdate_serializer = UserProfileSerializer(data=request.data.get('customer_details'))


			if customer_saveupdate_serializer.is_valid():   
				
				#username generation and customer_id generation
				if existing_customer:
					user_name                      = existing_customer.username
					new_customer_id                = existing_customer.customer_id
				else:
					user_name                      = generate_random_username()
					customer_id                    = UserProfile.objects.filter(is_active=True,customer_id__isnull=False).aggregate(t=Max('customer_id'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'1000')
					current_customer_id_starting   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2))					
					if current_customer_id_starting == int(str(customer_id)[:4]):
						new_customer_id = int(customer_id)+1
					else:
						new_customer_id   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2)+'1001')

				#contact platform
				contact_platform               = request.data.get('customer_details')['contact_platform']
				contact_platform_list 	       = contact_platform.split(",")
				if contact_platform_list:
					is_whatsapp = False
					is_email    = False
					is_sms      = False
					for contact_platform in contact_platform_list:
						if contact_platform == 'Whatsapp':
							is_whatsapp = True
						elif contact_platform == 'Email':
							is_email    = True
						else:
							is_sms      = True

				savedupdated_customer = customer_saveupdate_serializer.save(is_whatsapp=is_whatsapp,is_sms=is_sms,is_email=is_email,username=user_name,user_type='CUSTOMER',customer_id=new_customer_id)  

				response_dict['customerdetails_success']  = True     
			else: 
				errors= customer_saveupdate_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['customerdetails_Error']=key +':'+ error[0]
				response_dict['customerdetails_Error_List'] = customer_saveupdate_serializer.errors

				response_dict['customerdetails_success']  = False

				return Response(response_dict,HTTP_200_OK)

        	#create address or update address
			try:
				existing_address = Address.objects.get(id=request.data.get('address_id'))
			except:
				existing_address = None

			if existing_address:
				address_saveupdate_serializer = AddressSaveSerializer(data=request.data.get('address_details'),instance=existing_address)
			else:
				address_saveupdate_serializer = AddressSaveSerializer(data=request.data.get('address_details'))

			if address_saveupdate_serializer.is_valid():
				savedupdated_address = address_saveupdate_serializer.save(customer=savedupdated_customer,currently_active=True)

				response_dict['customeraddress_success']  = True
			else:
				errors= address_saveupdate_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['customeraddress_Error']=key +':'+ error[0]
				response_dict['customeraddress_Error_List'] = customer_saveupdate_serializer.errors

				response_dict['customeraddress_success']  = False

				return Response(response_dict,HTTP_200_OK)

        	#create Main Evaluation
			tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

			current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
			
			if current_blc_starting == int(str(tracking_no)[:6]):
				new_tracking_no     = int(tracking_no)+1
				evaluation_no       = 'BLC'+str(new_tracking_no)
			else:
				evaluation_no       = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
				tracking_no         = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')
				
			evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no,customer=savedupdated_customer,total_cost=request.data.get('total_cost'),estimated_cost=request.data.get('estimated_cost'),quatation_status='APPROVED',quatation_approved_date=timezone.now(),payment_method='PREPAID',payment_way='ONLINE',quatation_expiry_date=timezone.now()+timedelta(14))
			
			#create order
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
			

			order      = Order.objects.create(evaluation=evaluation,order_no=evaluation.evaluation_id,payment_status='PENDING',invoice_no=new_invoice_no,order_status='APPROVED_BY_CLIENT',total_amount=evaluation.total_cost,remining_amount=evaluation.total_cost)

			#create booking
			booking_id               = CustomerBooking.objects.filter(is_active=True).aggregate(t=Max('booking_id'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_booking_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_booking_starting == int(str(booking_id)[:4]):
				new_booking_id = int(booking_id)+1
			else:
				new_booking_id = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')
			
			customerbooking = CustomerBooking.objects.create(booking_id=new_booking_id,booking_type='CLEANINGBOOKING',booking_date=timezone.now(),evaluation=evaluation)

			#create evaluation details
			evaluation_details = EvaluationDetails.objects.create(evaluation=evaluation,address=savedupdated_address,status='EVALUATED',total_cost=evaluation.total_cost,estimated_cost=evaluation.total_cost)			

			for service_detail in services.keys():				
				
				#evaluation book
				service_save_serializer                    = EvaluationBookSerializer(data=services[service_detail])
				if service_save_serializer.is_valid():
					saved_service                              = service_save_serializer.save(evaluation_details=evaluation_details,cleaning_policy='ONE TIME SERVICE',cleaning_method='Method1',service_type_id=services[service_detail]['service_type'])
					
					response_dict['service_success']           = True
				else:
					errors= service_save_serializer.errors   
					key=tuple(errors.keys())[0] 
					error=errors[key]
					response_dict['service_Error']=key +':'+ error[0]
					response_dict['service_Error_List'] = service_save_serializer.errors

					response_dict['service_success']  = False

					return Response(response_dict,HTTP_200_OK)
				
				#create scheduler
				schedules_dict = request.data.get('schedule_details')
				for key in schedules_dict.keys():
					schedule_date           =  schedules_dict[key]['date']
					schedule_time           =  schedules_dict[key]['time']
					start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
					end_date_time           =  start_date_time + timedelta(hours=int(schedules_dict[key]['cleaning_hours'])) 	
					start_time              =  start_date_time.time()
					end_time                =  end_date_time.time()

					#schedule
					order_schedule = OrderScheduler.objects.create(order=order,customer_address=savedupdated_address,status='CONFIRMED',evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book=saved_service,no_of_cleaners=int(schedules_dict[key]['no_of_cleaners']),cleaning_hours=int(schedules_dict[key]['cleaning_hours']))
						
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
					active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

			
					#included shift cleaners
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)


					leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
					cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

					
					for service_detail in services.keys():
						service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
						service_type   		= service.name 			
					
						if service_type == 'General Cleaning':
							leaders = leaders.filter(is_general_skill=True)
							cleaners= cleaners.filter(is_general_skill=True).order_by('user_type')
						elif service_type == 'Deep Cleaning':
							leaders = leaders.filter(is_deep_skill=True)
							cleaners= cleaners.filter(is_deep_skill=True).order_by('user_type')
						elif service_type == 'Sterilization':
							leaders = leaders.filter(is_sterilization_skill=True)
							cleaners= cleaners.filter(is_sterilization_skill=True).order_by('user_type')
						elif service_type == 'Upholstery Cleaning':
							leaders = leaders.filter(is_upholstery_skill=True)
							cleaners= cleaners.filter(is_upholstery_skill=True).order_by('user_type')
						elif service_type == 'Kitchen Cleaning':
							leaders = leaders.filter(is_kitchen_skill=True)
							cleaners= cleaners.filter(is_kitchen_skill=True).order_by('user_type')
						elif service_type == 'Carpet Cleaning':
							leaders = leaders.filter(is_carpet_skill=True)
							cleaners= cleaners.filter(is_carpet_skill=True).order_by('user_type')
						elif service_type == 'Mattress Cleaning':
							leaders = leaders.filter(is_mattress_skill=True)
							cleaners= cleaners.filter(is_mattress_skill=True).order_by('user_type')
						elif service_type == 'Outdoor Cleaning':
							leaders = leaders.filter(is_outdoor_skill=True)
							cleaners= cleaners.filter(is_outdoor_skill=True).order_by('user_type')
						elif service_type == 'Storage Area':
							leaders = leaders.filter(is_storagearea_skill=True)
							cleaners= cleaners.filter(is_storagearea_skill=True).order_by('user_type')
						elif service_type == 'Window Cleaning':
							leaders = leaders.filter(is_window_skill=True)
							cleaners= cleaners.filter(is_window_skill=True).order_by('user_type')
						elif service_type == 'Car Parking Umbrella':
							leaders = leaders.filter(is_carparkingumbrella_skill=True)
							cleaners= cleaners.filter(is__skill=True).order_by('user_type')
						elif service_type == 'Facade Cleaning':
							leaders = leaders.filter(is_facade_skill=True)
							cleaners= cleaners.filter(is_facade_skill=True).order_by('user_type')
					
					#cleaning team
					cleaning_team  = CleaningTeam.objects.create(order_scheduler=order_schedule,team_leader=leaders.first(),start_at=start_date_time,end_at=end_date_time,no_of_cleaners=int(schedules_dict[key]['no_of_cleaners']))
					#cleaning team members
					no_of_cleaners = int(schedules_dict[key]['no_of_cleaners'])-1
					cleaning_team_member_array = []
					for i in range(no_of_cleaners):
						cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=cleaners[i],start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))
					cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=leaders.first(),start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))

					CleaningTeamMember.objects.bulk_create(cleaning_team_member_array)

				#create sections
				sections_dict = services[service_detail]['sections']
				for key in sections_dict.keys():
					section_save_serializer                    = EvaluationBookSectionSerializer(data=sections_dict[key])
					if section_save_serializer.is_valid():
						saved_section                          = section_save_serializer.save(evaluation_book=saved_service,section_cleanings=len(schedules_dict))
						response_dict['section_success']       = True
					else:
						errors= section_save_serializer.errors   
						key=tuple(errors.keys())[0] 
						error=errors[key]
						response_dict['section_Error']=key +':'+ error[0]
						response_dict['section_Error_List'] = section_save_serializer.errors

						response_dict['section_success']  = False

						return Response(response_dict,HTTP_200_OK)
					
					#create kenotes
					keynotes_dict = sections_dict[key]['keynotes']
					if keynotes_dict:
						for key in keynotes_dict.keys():
							keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key])
							if keynote_save_serializer.is_valid():
								saved_keynote       = keynote_save_serializer.save(evaluation_section=saved_section)
								
								response_dict['keynote_success']       = True
							else:
								errors= keynote_save_serializer.errors   
								key=tuple(errors.keys())[0] 
								error=errors[key]
								response_dict['keynote_Error']      = key +':'+ error[0]
								response_dict['keynote_Error_List'] = keynote_save_serializer.errors

								response_dict['keynote_success']    = False

								return Response(response_dict,HTTP_200_OK)
				
				service_dict[saved_service.id] = saved_service.service_type.name		
		else:
			evaluation = customerbooking.evaluation
			###testing availability ####
			test_schedules_dict = request.data.get('schedule_details')
			for key in test_schedules_dict.keys():
				schedule_date           =  test_schedules_dict[key]['date']
				schedule_time           =  test_schedules_dict[key]['time']
				start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
				end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours']) 	
				start_time              =  start_date_time.time()
				end_time                =  end_date_time.time()

				number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1

				#included shift cleaners
				shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
				shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
				today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
				super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
				super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

				#absent cleaners and leaders	
				absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
				absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

				total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners).count()-1
				total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders).count()-1

				#same blc cleaners for excluding
				sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

				active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
				active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
				
				for service_detail in services.keys():
					service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
					service_type   		= service.name
	
					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)


				cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

				followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
				followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

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

				busy_leaders  = len(set(team_leaders_scheduled))
				busy_cleaners = len(set(team_members_scheduled))

				#slote appending
				if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
					pass
				else:
					response_dict['Error'] = 'Cleaners are not available'
					return Response(response_dict,HTTP_200_OK)


			order      = Order.objects.get(evaluation=evaluation) 
			#create user or update user
			try:
				existing_customer    = UserProfile.objects.get(id=request.data.get('customer_id'))
			except:
				existing_customer    = None

			if existing_customer:
				customer_saveupdate_serializer = UserProfileSerializer(data=request.data.get('customer_details'),instance=existing_customer)
			else:
				customer_saveupdate_serializer = UserProfileSerializer(data=request.data.get('customer_details'))


			if customer_saveupdate_serializer.is_valid():   
				
				#username generation and customer_id generation
				if existing_customer:
					user_name                      = existing_customer.username
					new_customer_id                = existing_customer.customer_id
				else:
					user_name                      = generate_random_username()
					customer_id                    = UserProfile.objects.filter(is_active=True,customer_id__isnull=False).aggregate(t=Max('customer_id'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'1000')
					current_customer_id_starting   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2))					
					if current_customer_id_starting == int(str(customer_id)[:4]):
						new_customer_id = int(customer_id)+1
					else:
						new_customer_id   = int(str(timezone.now().year)[2:]+str(timezone.now().month).zfill(2)+'1001')

				#contact platform
				contact_platform               = request.data.get('customer_details')['contact_platform']
				contact_platform_list 	       = contact_platform.split(",")
				if contact_platform_list:
					is_whatsapp = False
					is_email    = False
					is_sms      = False
					for contact_platform in contact_platform_list:
						if contact_platform == 'Whatsapp':
							is_whatsapp = True
						elif contact_platform == 'Email':
							is_email    = True
						else:
							is_sms      = True
					savedupdated_customer = customer_saveupdate_serializer.save(is_whatsapp=is_whatsapp,is_sms=is_sms,is_email=is_email,username=user_name,user_type='CUSTOMER',customer_id=new_customer_id)  
					response_dict['customerdetails_success']  = True     
			else: 
				errors= customer_saveupdate_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['customerdetails_Error']=key +':'+ error[0]
				response_dict['customerdetails_Error_List'] = customer_saveupdate_serializer.errors

				response_dict['customerdetails_success']  = False

				return Response(response_dict,HTTP_200_OK)

        	#create address or update address
			try:
				existing_address = Address.objects.get(id=request.data.get('address_id'))
			except:
				existing_address = None

			if existing_address:
				address_saveupdate_serializer = AddressSaveSerializer(data=request.data.get('address_details'),instance=existing_address)
			else:
				address_saveupdate_serializer = AddressSaveSerializer(data=request.data.get('address_details'))

			if address_saveupdate_serializer.is_valid():
				savedupdated_address = address_saveupdate_serializer.save(customer=savedupdated_customer,currently_active=True)

				response_dict['customeraddress_success']  = True
			else:
				errors= address_saveupdate_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['customeraddress_Error']=key +':'+ error[0]
				response_dict['customeraddress_Error_List'] = customer_saveupdate_serializer.errors

				response_dict['customeraddress_success']  = False

				return Response(response_dict,HTTP_200_OK)

			#cost changing Evaluation and Order
			evaluation.total_cost    += request.data.get('total_cost')
			evaluation.estimated_cost += request.data.get('estimated_cost')
			evaluation.save()

			order.total_amount       += request.data.get('total_cost')
			order.remining_amount    += request.data.get('total_cost')
			order.save()
			
			#create evaluation details
			evaluation_details = EvaluationDetails.objects.create(evaluation=evaluation,address=savedupdated_address,status='EVALUATED',total_cost=evaluation.total_cost,estimated_cost=evaluation.total_cost)			
				
			#evaluation book
			for service_detail in services.keys():
				service_save_serializer                    = EvaluationBookSerializer(data=services[service_detail])
				if service_save_serializer.is_valid():
					saved_service                              = service_save_serializer.save(evaluation_details=evaluation_details,cleaning_policy='ONE TIME SERVICE',cleaning_method='Method1',service_type_id=services[service_detail]['service_type'])
					
					response_dict['service_success']           = True
				else:
					errors= service_save_serializer.errors   
					key=tuple(errors.keys())[0] 
					error=errors[key]
					response_dict['service_Error']=key +':'+ error[0]
					response_dict['service_Error_List'] = service_save_serializer.errors

					response_dict['service_success']  = False

					return Response(response_dict,HTTP_200_OK)
				
				#create scheduler
				schedules_dict = request.data.get('schedule_details')
				for key in schedules_dict.keys():
					schedule_date           =  schedules_dict[key]['date']
					schedule_time           =  schedules_dict[key]['time']
					start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
					end_date_time           =  start_date_time + timedelta(hours=int(saved_service.cleaning_hours)) 	
					start_time              =  start_date_time.time()
					end_time                =  end_date_time.time()

					#schedule
					order_schedule = OrderScheduler.objects.create(order=order,status='CONFIRMED',customer_address=savedupdated_address,evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book=saved_service,no_of_cleaners=schedules_dict[key]['no_of_cleaners'],cleaning_hours=schedules_dict[key]['cleaning_hours'])

					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)						

					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
					active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					#included shift cleaners
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)


					leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
					cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

					for service_detail in services.keys():
						service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
						service_type   		= service.name 			
					
						if service_type == 'General Cleaning':
							leaders = leaders.filter(is_general_skill=True)
							cleaners= cleaners.filter(is_general_skill=True).order_by('user_type')
						elif service_type == 'Deep Cleaning':
							leaders = leaders.filter(is_deep_skill=True)
							cleaners= cleaners.filter(is_deep_skill=True).order_by('user_type')
						elif service_type == 'Sterilization':
							leaders = leaders.filter(is_sterilization_skill=True)
							cleaners= cleaners.filter(is_sterilization_skill=True).order_by('user_type')
						elif service_type == 'Upholstery Cleaning':
							leaders = leaders.filter(is_upholstery_skill=True)
							cleaners= cleaners.filter(is_upholstery_skill=True).order_by('user_type')
						elif service_type == 'Kitchen Cleaning':
							leaders = leaders.filter(is_kitchen_skill=True)
							cleaners= cleaners.filter(is_kitchen_skill=True).order_by('user_type')
						elif service_type == 'Carpet Cleaning':
							leaders = leaders.filter(is_carpet_skill=True)
							cleaners= cleaners.filter(is_carpet_skill=True).order_by('user_type')
						elif service_type == 'Mattress Cleaning':
							leaders = leaders.filter(is_mattress_skill=True)
							cleaners= cleaners.filter(is_mattress_skill=True).order_by('user_type')
						elif service_type == 'Outdoor Cleaning':
							leaders = leaders.filter(is_outdoor_skill=True)
							cleaners= cleaners.filter(is_outdoor_skill=True).order_by('user_type')
						elif service_type == 'Storage Area':
							leaders = leaders.filter(is_storagearea_skill=True)
							cleaners= cleaners.filter(is_storagearea_skill=True).order_by('user_type')
						elif service_type == 'Window Cleaning':
							leaders = leaders.filter(is_window_skill=True)
							cleaners= cleaners.filter(is_window_skill=True).order_by('user_type')
						elif service_type == 'Car Parking Umbrella':
							leaders = leaders.filter(is_carparkingumbrella_skill=True)
							cleaners= cleaners.filter(is__skill=True).order_by('user_type')
						elif service_type == 'Facade Cleaning':
							leaders = leaders.filter(is_facade_skill=True)
							cleaners= cleaners.filter(is_facade_skill=True).order_by('user_type')						
		
					#cleaning team
					cleaning_team  = CleaningTeam.objects.create(order_scheduler=order_schedule,team_leader=leaders.first(),start_at=start_date_time,end_at=end_date_time,no_of_cleaners=int(schedules_dict[key]['no_of_cleaners']))
					#cleaning team members
					no_of_cleaners = int(schedules_dict[key]['no_of_cleaners'])-1
					cleaning_team_member_array = []
					for i in range(no_of_cleaners):
						cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=cleaners[i],start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))
					cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=leaders.first(),start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))

					CleaningTeamMember.objects.bulk_create(cleaning_team_member_array)

				#create sections
				sections_dict = services[service_detail]['sections']
				for key in sections_dict.keys():
					section_save_serializer                    = EvaluationBookSectionSerializer(data=sections_dict[key])
					if section_save_serializer.is_valid():
						saved_section                          = section_save_serializer.save(evaluation_book=saved_service,section_cleanings=len(schedules_dict))
						
						response_dict['section_success']       = True
					else:
						errors= section_save_serializer.errors   
						key=tuple(errors.keys())[0] 
						error=errors[key]
						response_dict['section_Error']=key +':'+ error[0]
						response_dict['section_Error_List'] = section_save_serializer.errors

						response_dict['section_success']  = False

						return Response(response_dict,HTTP_200_OK)
					
					#create kenotes
					keynotes_dict = sections_dict[key]['keynotes']
					if keynotes_dict:
						for key in keynotes_dict.keys():
							keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key])
							if keynote_save_serializer.is_valid():
								saved_keynote       = keynote_save_serializer.save(evaluation_section=saved_section)
								
								response_dict['keynote_success']       = True
							else:
								errors= keynote_save_serializer.errors   
								key=tuple(errors.keys())[0] 
								error=errors[key]
								response_dict['keynote_Error']      = key +':'+ error[0]
								response_dict['keynote_Error_List'] = keynote_save_serializer.errors

								response_dict['keynote_success']    = False

								return Response(response_dict,HTTP_200_OK)

				service_dict[saved_service.id] = saved_service.service_type.name				
		
		response_dict['evaluation_book_ids'] = service_dict
		response_dict['booking_id']          = customerbooking.booking_id
		response_dict['success']             = True

		return Response(response_dict,HTTP_200_OK)



class EvaluatorMultipleCleaningBookingTogetherPhase2(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request,evaluation_details_id): 
		response_dict = {'success':False}

		##multiple services #count total cleaners and total leaders for availability
		total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		total_leaders   = UserProfile.objects.filter(is_general_skill=True,user_type='TEAMINCHARGE')
		
		services      = request.data.get("service_details")
		for service_detail in services.keys():
			service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
			service_type   		= service.name

			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				total_leaders 	= total_leaders.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				total_leaders 	= total_leaders.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				total_leaders 	= total_leaders.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				total_leaders 	= total_leaders.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				total_leaders 	= total_leaders.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				total_leaders 	= total_leaders.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				total_leaders 	= total_leaders.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				total_leaders 	= total_leaders.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				total_leaders 	= total_leaders.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				total_leaders 	= total_leaders.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				total_leaders 	= total_leaders.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)
				total_leaders 	= total_leaders.filter(is_outdoor_skill=True)

		#evaluation,evaluation details,order
		evaluation_details = EvaluationDetails.objects.select_related('evaluation').get(id=evaluation_details_id)
		evaluation         = evaluation_details.evaluation
		##order
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

		try:
			order              = Order.objects.get(evaluation=evaluation)
		except:
			order              = Order.objects.create(evaluation=evaluation,order_no=evaluation.evaluation_id,payment_status='PENDING',invoice_no=new_invoice_no)

		###testing availability ####
		test_schedules_dict = list(request.data.get("service_details").values())[0]['schedule_details']
		for key in test_schedules_dict.keys():
			schedule_date           =  test_schedules_dict[key]['date']
			schedule_time           =  test_schedules_dict[key]['time']
			start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
			end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours']) 	
			start_time              =  start_date_time.time()
			end_time                =  end_date_time.time()

			number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1

			#included shift cleaners
			shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
			shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
			today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
			super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
			super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

			#absent cleaners and leaders	
			absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
			absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

			total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners).count()-1
			total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders).count()

			#same blc cleaners for excluding
			sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
			
			for service_detail in services.keys():
				service        		= ServiceType.objects.get(id=int(services[service_detail]['service_type']))
				service_type   		= service.name

				if service_type == 'General Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
				elif service_type == 'Sterilization':
					active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
				elif service_type == 'Storage Area':
					active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)


			cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
			cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

			followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
			followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

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

			busy_leaders  = len(set(team_leaders_scheduled))
			busy_cleaners = len(set(team_members_scheduled))

			print(total_newleaders,"total_newleaders")
			print(team_leaders_scheduled,"team_leaders_scheduled")
			print(busy_leaders,"busy_leaders")

			print(total_newcleaners,"total_newcleaners")
			print(team_members_scheduled,"team_members_scheduled")
			print(busy_cleaners,"busy_cleaners")

			#slote appending
			if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
				pass
			else:
				response_dict['Error'] = 'Cleaners are not available'
				return Response(response_dict,HTTP_200_OK) 

		#Evaluation cost updation
		evaluation.total_cost     += request.data.get('total_cost')
		evaluation.estimated_cost += request.data.get('estimated_cost')
		evaluation.save()

		#order cost updation
		order.total_amount       += request.data.get('total_cost')
		order.remining_amount    += request.data.get('total_cost')
		order.save()
		
		#evaluation details cost updation
		evaluation_details.status         = 'EVALUATED'
		evaluation_details.total_cost     += request.data.get('total_cost')
		evaluation_details.estimated_cost += request.data.get('estimated_cost')			
		evaluation_details.save()

		#evaluation book
		service_dict = {}
		for service_detail in services.keys():
			service_save_serializer                    = EvaluationBookSerializer(data=services[service_detail])
			if service_save_serializer.is_valid():
				saved_service                              = service_save_serializer.save(service_type_id=services[service_detail]['service_type'],evaluation_details=evaluation_details,cleaning_policy=services[service_detail]['cleaning_policy'],cleaning_method='Method1')	
				response_dict['service_success']           = True
			else:
				errors= service_save_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['service_Error']=key +':'+ error[0]
				response_dict['service_Error_List'] = service_save_serializer.errors

				response_dict['service_success']  = False

				return Response(response_dict,HTTP_200_OK)
			
			#create scheduler
			schedules_dict = list(request.data.get("service_details").values())[0]['schedule_details']
			for key in schedules_dict.keys():
				schedule_date           =  schedules_dict[key]['date']
				schedule_time           =  schedules_dict[key]['time']
				start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
				end_date_time           =  start_date_time + timedelta(hours=int(schedules_dict[key]['cleaning_hours'])) 	
				start_time              =  start_date_time.time()
				end_time                =  end_date_time.time()

				#schedule
				order_schedule = OrderScheduler.objects.create(order=order,status='CONFIRMED',customer_address=evaluation_details.address,evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book=saved_service,no_of_cleaners=schedules_dict[key]['no_of_cleaners'],cleaning_hours=schedules_dict[key]['cleaning_hours'])

				# absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
				# absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)						

				# #same blc cleaners for excluding
				# sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

				# active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
				# active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

				# #included shift cleaners
				# shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
				# shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
				# today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
				# super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
				# super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)


				# leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
				# cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

				# for check_service_detail in services.keys():
				# 	service        		= ServiceType.objects.get(id=int(services[check_service_detail]['service_type']))
				# 	service_type   		= service.name 			
				
				# 	if service_type == 'General Cleaning':
				# 		leaders = leaders.filter(is_general_skill=True)
				# 		cleaners= cleaners.filter(is_general_skill=True).order_by('user_type')
				# 	elif service_type == 'Deep Cleaning':
				# 		leaders = leaders.filter(is_deep_skill=True)
				# 		cleaners= cleaners.filter(is_deep_skill=True).order_by('user_type')
				# 	elif service_type == 'Sterilization':
				# 		leaders = leaders.filter(is_sterilization_skill=True)
				# 		cleaners= cleaners.filter(is_sterilization_skill=True).order_by('user_type')
				# 	elif service_type == 'Upholstery Cleaning':
				# 		leaders = leaders.filter(is_upholstery_skill=True)
				# 		cleaners= cleaners.filter(is_upholstery_skill=True).order_by('user_type')
				# 	elif service_type == 'Kitchen Cleaning':
				# 		leaders = leaders.filter(is_kitchen_skill=True)
				# 		cleaners= cleaners.filter(is_kitchen_skill=True).order_by('user_type')
				# 	elif service_type == 'Carpet Cleaning':
				# 		leaders = leaders.filter(is_carpet_skill=True)
				# 		cleaners= cleaners.filter(is_carpet_skill=True).order_by('user_type')
				# 	elif service_type == 'Mattress Cleaning':
				# 		leaders = leaders.filter(is_mattress_skill=True)
				# 		cleaners= cleaners.filter(is_mattress_skill=True).order_by('user_type')
				# 	elif service_type == 'Outdoor Cleaning':
				# 		leaders = leaders.filter(is_outdoor_skill=True)
				# 		cleaners= cleaners.filter(is_outdoor_skill=True).order_by('user_type')
				# 	elif service_type == 'Storage Area':
				# 		leaders = leaders.filter(is_storagearea_skill=True)
				# 		cleaners= cleaners.filter(is_storagearea_skill=True).order_by('user_type')
				# 	elif service_type == 'Window Cleaning':
				# 		leaders = leaders.filter(is_window_skill=True)
				# 		cleaners= cleaners.filter(is_window_skill=True).order_by('user_type')
				# 	elif service_type == 'Car Parking Umbrella':
				# 		leaders = leaders.filter(is_carparkingumbrella_skill=True)
				# 		cleaners= cleaners.filter(is__skill=True).order_by('user_type')
				# 	elif service_type == 'Facade Cleaning':
				# 		leaders = leaders.filter(is_facade_skill=True)
				# 		cleaners= cleaners.filter(is_facade_skill=True).order_by('user_type')						
	
				# #cleaning team
				# cleaning_team  = CleaningTeam.objects.create(order_scheduler=order_schedule,team_leader=leaders.first(),start_at=start_date_time,end_at=end_date_time,no_of_cleaners=int(schedules_dict[key]['no_of_cleaners']))
				# #cleaning team members
				# no_of_cleaners = int(schedules_dict[key]['no_of_cleaners'])-1
				# cleaning_team_member_array = []
				# for i in range(no_of_cleaners):
				# 	cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=cleaners[i],start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))
				# cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=leaders.first(),start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))

				# CleaningTeamMember.objects.bulk_create(cleaning_team_member_array)

			#create sections
			sections_dict = services[service_detail]['sections']
			for key in sections_dict.keys():
				section_save_serializer                    = EvaluationBookSectionSerializer(data=sections_dict[key])
				if section_save_serializer.is_valid():
					saved_section                          = section_save_serializer.save(evaluation_book=saved_service,section_cleanings=len(schedules_dict))
					
					response_dict['section_success']       = True
				else:
					errors= section_save_serializer.errors   
					key=tuple(errors.keys())[0] 
					error=errors[key]
					response_dict['section_Error']=key +':'+ error[0]
					response_dict['section_Error_List'] = section_save_serializer.errors

					response_dict['section_success']  = False

					return Response(response_dict,HTTP_200_OK)
				
				#create kenotes
				keynotes_dict = sections_dict[key]['keynotes']
				if keynotes_dict:
					for key in keynotes_dict.keys():
						keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key])
						if keynote_save_serializer.is_valid():
							saved_keynote       = keynote_save_serializer.save(evaluation_section=saved_section)
							
							response_dict['keynote_success']       = True
						else:
							errors= keynote_save_serializer.errors   
							key=tuple(errors.keys())[0] 
							error=errors[key]
							response_dict['keynote_Error']      = key +':'+ error[0]
							response_dict['keynote_Error_List'] = keynote_save_serializer.errors

							response_dict['keynote_success']    = False

							return Response(response_dict,HTTP_200_OK)

			service_dict[saved_service.id] = services[service_detail]['service_type']				
		
		response_dict['evaluation_book_ids'] = service_dict
		response_dict['success']             = True

		return Response(response_dict,HTTP_200_OK)


class EvaluatorMultipleCleaningBookingLetCustomerPhase2(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request,evaluation_details_id): 
		response_dict = {'success':False}
		
		#evaluation,evaluation details, and order
		evaluation_details = EvaluationDetails.objects.select_related('evaluation').get(id=evaluation_details_id)
		evaluation         = evaluation_details.evaluation

		#customer booking
		#create booking
		try:
			customerbooking = CustomerBooking.objects.get(evaluation=evaluation)
		except:
			booking_id               = CustomerBooking.objects.filter(is_active=True).aggregate(t=Max('booking_id'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_booking_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_booking_starting == int(str(booking_id)[:4]):
				new_booking_id = int(booking_id)+1
			else:
				new_booking_id = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')

			customerbooking = CustomerBooking.objects.create(booking_id=new_booking_id,booking_type='CLEANINGBOOKING',booking_date=timezone.now(),evaluation=evaluation)

		##order
		try:
			order              = Order.objects.get(evaluation=evaluation)
		except:
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
				
			order              = Order.objects.create(evaluation=evaluation,order_no=evaluation.evaluation_id,payment_status='PENDING',invoice_no=new_invoice_no)
		
		services        = request.data.get("service_details")

		#Evaluation cost updation
		evaluation.total_cost      += request.data.get('total_cost')
		evaluation.estimated_cost  += request.data.get('estimated_cost')
		evaluation.quatation_status = 'APPROVED'
		evaluation.save()

		#order cost updation
		order.total_amount         += request.data.get('total_cost')
		order.remining_amount      += request.data.get('total_cost')
		order.order_status          = 'APPROVED_BY_CLIENT'
		order.save()
		
		#evaluation details cost updation
		evaluation_details.status         = 'EVALUATED'
		evaluation_details.total_cost     = request.data.get('total_cost')
		evaluation_details.estimated_cost = request.data.get('estimated_cost')			
		evaluation_details.save()

		service_dict = {}
		#evaluation book
		for service_detail in services.keys():
			service_save_serializer                    = EvaluationBookSerializer(data=services[service_detail])
			if service_save_serializer.is_valid():
				saved_service                              = service_save_serializer.save(evaluation_details=evaluation_details,cleaning_policy='ONE TIME SERVICE',cleaning_method='Method1',service_type_id=services[service_detail]['service_type'])	
				response_dict['service_success']           = True
			else:
				errors= service_save_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['service_Error']=key +':'+ error[0]
				response_dict['service_Error_List'] = service_save_serializer.errors

				response_dict['service_success']  = False

				return Response(response_dict,HTTP_200_OK) 							

			#create sections
			sections_dict = services[service_detail]['sections']
			for key in sections_dict.keys():
				section_save_serializer                    = EvaluationBookSectionSerializer(data=sections_dict[key])
				if section_save_serializer.is_valid():
					saved_section                          = section_save_serializer.save(evaluation_book=saved_service,section_cleanings=1,)
					
					response_dict['section_success']       = True
				else:
					errors= section_save_serializer.errors   
					key=tuple(errors.keys())[0] 
					error=errors[key]
					response_dict['section_Error']=key +':'+ error[0]
					response_dict['section_Error_List'] = section_save_serializer.errors

					response_dict['section_success']  = False

					return Response(response_dict,HTTP_200_OK)
				
				#create kenotes
				keynotes_dict = sections_dict[key]['keynotes']
				if keynotes_dict:
					for key in keynotes_dict.keys():
						keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key])
						if keynote_save_serializer.is_valid():
							saved_keynote       = keynote_save_serializer.save(evaluation_section=saved_section)
							
							response_dict['keynote_success']       = True
						else:
							errors= keynote_save_serializer.errors   
							key=tuple(errors.keys())[0] 
							error=errors[key]
							response_dict['keynote_Error']      = key +':'+ error[0]
							response_dict['keynote_Error_List'] = keynote_save_serializer.errors

							response_dict['keynote_success']    = False

							return Response(response_dict,HTTP_200_OK)

			service_dict[saved_service.id] = saved_service.service_type.name				
		
		response_dict['evaluation_book_ids'] = service_dict
		response_dict['booking_id']          = customerbooking.booking_id
		response_dict['success']             = True

		return Response(response_dict,HTTP_200_OK)

class DuplicateBookingPhase2(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request,evaluation_id):
		response_dict = {}
		
		duplicate_evaluation         = Evaluation.objects.get(id=evaluation_id)		
		duplicate_evaluation_details = EvaluationDetails.objects.filter(is_active=True,evaluation=duplicate_evaluation).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='schedules'),Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='booksections')),to_attr='evaluationbooks'))

		#blc calculation
		tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')
		current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))		
		if current_blc_starting == int(str(tracking_no)[:6]):
			new_tracking_no = int(tracking_no)+1
			evaluation_no   = 'BLC'+str(new_tracking_no)
		else:
			evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
			tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

		#duplicate the evaluation
		new_evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no,customer=duplicate_evaluation.customer,call_attender=duplicate_evaluation.call_attender,quatation_expiry_date=timezone.now()+timedelta(7))
		
		#duplicate the order
		new_order      = Order.objects.create(evaluation=new_evaluation,order_no=new_evaluation.evaluation_id)

		if duplicate_evaluation_details:

			#new evaluation details
			for duplicate_evaluation in duplicate_evaluation_details:
				new_duplicate_evaluation_details = EvaluationDetails.objects.create(evaluation=new_evaluation,address=duplicate_evaluation.address,status=duplicate_evaluation.status)
				
				#new book
				if duplicate_evaluation.evaluationbooks:
					for duplicate_book in duplicate_evaluation.evaluationbooks:
						new_duplicate_book = EvaluationBook.objects.create(evaluation_details=new_duplicate_evaluation_details,cleaning_policy=duplicate_book.cleaning_policy,service_type=duplicate_book.service_type,area_type=duplicate_book.area_type,cleaning_method=duplicate_book.cleaning_method,location_type=duplicate_book.location_type,evaluator_note=duplicate_book.evaluator_note,estimated_cost=duplicate_book.estimated_cost)						

						#new booksection
						if duplicate_book.booksections:
							for duplicate_book_section in duplicate_book.booksections:
								new_duplicate_section = EvaluationBookSection.objects.create(evaluation_book=new_duplicate_book,section_name=duplicate_book_section.section_name,section_name_arabic=duplicate_book_section.section_name_arabic,category=duplicate_book_section.category,dirt_level=duplicate_book_section.dirt_level,quantity=duplicate_book_section.quantity,size=duplicate_book_section.size,unit=duplicate_book_section.unit,age=duplicate_book_section.age,floor=duplicate_book_section.floor,apartment=duplicate_book_section.apartment,room=duplicate_book_section.room,wall_type=duplicate_book_section.wall_type,ceiling_type=duplicate_book_section.ceiling_type,floor_type=duplicate_book_section.floor_type,material=duplicate_book_section.material,colour=duplicate_book_section.colour,cause_of_stain=duplicate_book_section.cause_of_stain,section_cost=duplicate_book_section.section_cost)
							
								#new keynotes
								if duplicate_book_section.sectionkeynotes:
									for duplicate_keynote in duplicate_book_section.sectionkeynotes:	
										new_duplicate_keynote = EvaluationSectionKeynote.objects.create(evaluation_section=new_duplicate_section,sub_area=duplicate_keynote.sub_area,quantity=duplicate_keynote.quantity,)

		response_dict['duplicate_id']= 'paw'+str(new_evaluation.tracking_no)
		response_dict['success']     = True

		return Response(response_dict,HTTP_200_OK)

	def post(self,request,evaluation_id):
		response_dict            = {}
		response_dict['success'] = False

		evaluation              = Evaluation.objects.get(id=evaluation_id)
		order    				= Order.objects.get(evaluation=evaluation)
		services 				= request.data.get('service_details')

		###testing availability ####
		total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		total_leaders   = UserProfile.objects.filter(is_general_skill=True,user_type='TEAMINCHARGE')
		for service_detail in services.keys():
			service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
			service_type   		        = service_book.service_type.name

			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				total_leaders 	= total_leaders.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				total_leaders 	= total_leaders.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				total_leaders 	= total_leaders.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				total_leaders 	= total_leaders.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				total_leaders 	= total_leaders.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				total_leaders 	= total_leaders.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				total_leaders 	= total_leaders.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				total_leaders 	= total_leaders.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				total_leaders 	= total_leaders.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				total_leaders 	= total_leaders.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				total_leaders 	= total_leaders.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)
				total_leaders 	= total_leaders.filter(is_outdoor_skill=True)


		test_schedules_dict = list(request.data.get("service_details").values())[0]['schedule_details']
		for key in test_schedules_dict.keys():
			schedule_date           =  test_schedules_dict[key]['date']
			schedule_time           =  test_schedules_dict[key]['time']
			start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
			end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours'])
			start_time              =  start_date_time.time()
			end_time                =  end_date_time.time() 	

			number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1

			#included shift cleaners
			shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
			shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
			today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
			super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
			super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

			#absent cleaners and leaders	
			absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
			absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

			total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners).count()-1
			total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders).count()

			#same blc cleaners for excluding
			sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
			
			for service_detail in services.keys():
				service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
				service_type   		        = service_book.service_type.name

				if service_type == 'General Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
				elif service_type == 'Sterilization':
					active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
				elif service_type == 'Storage Area':
					active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)


			cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
			cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

			followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
			followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

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

			busy_leaders  = len(set(team_leaders_scheduled))
			busy_cleaners = len(set(team_members_scheduled))

			#slote appending
			if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
				pass
			else:
				response_dict['Error'] = 'Cleaners are not available'
				return Response(response_dict,HTTP_200_OK)


			#saving
			for service_detail in services.keys():
				schedules_dict                  = list(request.data.get("service_details").values())[0]['schedule_details']
				evaluation_details = EvaluationDetails.objects.get(id=services[service_detail]['evaluation_details_id'])
				
				#cleaning policy and cost updations
				service_book                    = EvaluationBook.objects.get(id=services[service_detail]['id'])
				service_book.cleaning_policy    = services[service_detail]['cleaning_policy']
				service_book.save()

				##cost updation
				if service_book.cleaning_policy == 'SUBSCRIPTION':
					service_book.total_cost               = service_book.estimated_cost*len(schedules_dict)
					service_book.estimated_cost           = service_book.estimated_cost*len(schedules_dict)
				else:
					service_book.total_cost            = service_book.estimated_cost
					service_book.estimated_cost        = service_book.estimated_cost
				service_book.save()

				##cost updation
				evaluation_details.estimated_cost     += service_book.estimated_cost
				evaluation_details.total_cost         += service_book.total_cost
				evaluation_details.save()

				evaluation.estimated_cost     		  += service_book.estimated_cost
				evaluation.total_cost         		  += service_book.total_cost
				evaluation.save()

				order.total_amount                    += service_book.total_cost
				order.remining_amount                 += service_book.total_cost
				order.save()

				##cost updation
				try:
					book_sections = EvaluationBookSection.objects.filter(evaluation_book=service_book)
				except:
					book_sections = None
				for section in book_sections:
					section.section_net_cost  = section.section_cost*len(schedules_dict)
					section.section_cleanings = len(schedules_dict)
					section.save()

				for key in schedules_dict.keys():
					schedule_date           =  schedules_dict[key]['date']
					schedule_time           =  schedules_dict[key]['time']
					start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
					end_date_time           =  start_date_time + timedelta(hours=schedules_dict[key]['cleaning_hours']) 	
					start_time              =  start_date_time.time()
					end_time                =  start_date_time.time()

					#schedule
					order_schedule = OrderScheduler.objects.create(order=order,status='CONFIRMED',customer_address=evaluation_details.address,evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book_id=services[service_detail]['id'],no_of_cleaners=schedules_dict[key]['no_of_cleaners'],cleaning_hours=schedules_dict[key]['cleaning_hours'])

					# absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					# absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)						

					# #same blc cleaners for excluding
					# sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					# active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
					# active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					# #included shift cleaners
					# shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					# shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					# today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
					# super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					# super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)


					# leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
					# cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

					# for service_detail in services.keys():
					# 	service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
					# 	service_type   		        = service_book.service_type.name 			
					
					# 	if service_type == 'General Cleaning':
					# 		leaders = leaders.filter(is_general_skill=True)
					# 		cleaners= cleaners.filter(is_general_skill=True).order_by('user_type')
					# 	elif service_type == 'Deep Cleaning':
					# 		leaders = leaders.filter(is_deep_skill=True)
					# 		cleaners= cleaners.filter(is_deep_skill=True).order_by('user_type')
					# 	elif service_type == 'Sterilization':
					# 		leaders = leaders.filter(is_sterilization_skill=True)
					# 		cleaners= cleaners.filter(is_sterilization_skill=True).order_by('user_type')
					# 	elif service_type == 'Upholstery Cleaning':
					# 		leaders = leaders.filter(is_upholstery_skill=True)
					# 		cleaners= cleaners.filter(is_upholstery_skill=True).order_by('user_type')
					# 	elif service_type == 'Kitchen Cleaning':
					# 		leaders = leaders.filter(is_kitchen_skill=True)
					# 		cleaners= cleaners.filter(is_kitchen_skill=True).order_by('user_type')
					# 	elif service_type == 'Carpet Cleaning':
					# 		leaders = leaders.filter(is_carpet_skill=True)
					# 		cleaners= cleaners.filter(is_carpet_skill=True).order_by('user_type')
					# 	elif service_type == 'Mattress Cleaning':
					# 		leaders = leaders.filter(is_mattress_skill=True)
					# 		cleaners= cleaners.filter(is_mattress_skill=True).order_by('user_type')
					# 	elif service_type == 'Outdoor Cleaning':
					# 		leaders = leaders.filter(is_outdoor_skill=True)
					# 		cleaners= cleaners.filter(is_outdoor_skill=True).order_by('user_type')
					# 	elif service_type == 'Storage Area':
					# 		leaders = leaders.filter(is_storagearea_skill=True)
					# 		cleaners= cleaners.filter(is_storagearea_skill=True).order_by('user_type')
					# 	elif service_type == 'Window Cleaning':
					# 		leaders = leaders.filter(is_window_skill=True)
					# 		cleaners= cleaners.filter(is_window_skill=True).order_by('user_type')
					# 	elif service_type == 'Car Parking Umbrella':
					# 		leaders = leaders.filter(is_carparkingumbrella_skill=True)
					# 		cleaners= cleaners.filter(is__skill=True).order_by('user_type')
					# 	elif service_type == 'Facade Cleaning':
					# 		leaders = leaders.filter(is_facade_skill=True)
					# 		cleaners= cleaners.filter(is_facade_skill=True).order_by('user_type')						
		
					# #cleaning team
					# cleaning_team  = CleaningTeam.objects.create(order_scheduler=order_schedule,team_leader=leaders.first(),start_at=start_date_time,end_at=end_date_time)
					# #cleaning team members
					# no_of_cleaners = int(schedules_dict[key]['no_of_cleaners'])-1
					# cleaning_team_member_array = []
					# for i in range(no_of_cleaners):
					# 	cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=cleaners[i],start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))
					# cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=leaders.first(),start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))

					# CleaningTeamMember.objects.bulk_create(cleaning_team_member_array)

		response_dict['success'] = True
		return Response(response_dict,HTTP_200_OK)



class ClientCleaningBookingPhase3(APIView):
	def get(self,request):
		response_dict = {}

		booking_id    = request.GET.get('booking_id')		
		
		customer_booking   = CustomerBooking.objects.select_related('evaluation').get(booking_id=booking_id)
		evaluation_details = EvaluationDetails.objects.filter(evaluation=customer_booking.evaluation).prefetch_related('evaluation_book_evaluation_details__evaluationsection_book')
		order              = Order.objects.select_related('evaluation__customer').get(evaluation=customer_booking.evaluation)

		order_details_serialized    = OrderSerializer(order).data
		customer_details_serialized = EvaluationSerializer(customer_booking.evaluation).data
		address_details_serialized	= EvaluationDetailsSerializer(evaluation_details,many=True).data
		
		response_dict['order_details']           = order_details_serialized
		response_dict['customer_details']        = customer_details_serialized
		response_dict['cleaning_details']        = address_details_serialized
		response_dict['encryption_key']		     = order.evaluation.customer.username

		return Response(response_dict,HTTP_200_OK)

class ClientCleaningBookingMediaSave(APIView):
	def post(self,request):
		
		response_dict = {}
		response_dict['success'] = False

		evaluation_book_id    = request.data.get('evaluation_book_id')
		evaluation_book = EvaluationBook.objects.get(id=evaluation_book_id)

		#To Save Media		
		medias                = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				EvaluationMedia.objects.create(
				        evaluation_book=evaluation_book,
				        media=media,
				        media_type='PHOTO',
						taken_status='CUSTOMER_SEND'
				        )
		
		response_dict['success'] = True
		return Response(response_dict,HTTP_200_OK)


class EvaluatorMultipleCleaningBookingLetCustomerPhase3(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request,evaluation_id): 
		response_dict = {'success':False}

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		
		#evaluation books,sections,and keynotes
		evaluation_details                  = EvaluationDetails.objects.select_related('evaluation').prefetch_related('evaluation_book_evaluation_details__evaluationsection_book__keynotesections').filter(evaluation__evaluation_id=evaluation_id)
		response_dict['evaluation_details'] = EvaluationDetailsSerializer(instance=evaluation_details,many=True).data

		response_dict['success'] = True
		return Response(response_dict,HTTP_200_OK)

	def post(self,request,evaluation_id):
		response_dict            = {}
		response_dict['success'] = False

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id 			= 'BLC'+evaluation_id_encrypted[3:14]

		evaluation              = Evaluation.objects.get(evaluation_id=evaluation_id)
		order    				= Order.objects.get(evaluation=evaluation)
		services 				= request.data.get('service_details')

		###testing availability ####
		total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		total_leaders   = UserProfile.objects.filter(is_general_skill=True,user_type='TEAMINCHARGE')
		for service_detail in services.keys():
			service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
			service_type   		        = service_book.service_type.name

			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				total_leaders 	= total_leaders.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				total_leaders 	= total_leaders.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				total_leaders 	= total_leaders.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				total_leaders 	= total_leaders.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				total_leaders 	= total_leaders.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				total_leaders 	= total_leaders.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				total_leaders 	= total_leaders.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				total_leaders 	= total_leaders.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				total_leaders 	= total_leaders.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				total_leaders 	= total_leaders.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				total_leaders 	= total_leaders.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)
				total_leaders 	= total_leaders.filter(is_outdoor_skill=True)


		test_schedules_dict = list(request.data.get("service_details").values())[0]['schedule_details']
		for key in test_schedules_dict.keys():
			schedule_date           =  test_schedules_dict[key]['date']
			schedule_time           =  test_schedules_dict[key]['time']
			start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
			end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours'])
			start_time              =  start_date_time.time()
			end_time                =  end_date_time.time() 	

			number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1

			#included shift cleaners
			shift_cleaners  = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
			shift_leaders   = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
			today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
			super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
			super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

			#absent cleaners and leaders	
			absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
			absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

			total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners).count()-1
			total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders).count()

			#same blc cleaners for excluding
			sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
			
			for service_detail in services.keys():
				service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
				service_type   		        = service_book.service_type.name

				if service_type == 'General Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
				elif service_type == 'Sterilization':
					active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
				elif service_type == 'Storage Area':
					active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)


			cleaning_active_team_leaders = active_cleaners1.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
			cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

			followup_active_team_leaders = active_cleaners2.filter(member__user_type='TEAMINCHARGE').values_list('member',flat=True)
			followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

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

			busy_leaders  = len(set(team_leaders_scheduled))
			busy_cleaners = len(set(team_members_scheduled))

			#slote appending
			if((total_newcleaners-busy_cleaners)>=number_of_cleaners and (total_newleaders-busy_leaders)>=1):
				pass
			else:
				response_dict['Error'] = 'Cleaners are not available'
				return Response(response_dict,HTTP_200_OK)


			#saving
			for service_detail in services.keys():
				schedules_dict     = list(request.data.get("service_details").values())[0]['schedule_details']
				evaluation_details = EvaluationDetails.objects.get(id=services[service_detail]['evaluation_details_id'])

				sections           = EvaluationBookSection.objects.filter(evaluation_book_id=services[service_detail]['id']).update(section_cleanings=len(schedules_dict),section_net_cost=len(schedules_dict))
				
				for key in schedules_dict.keys():
					schedule_date           =  schedules_dict[key]['date']
					schedule_time           =  schedules_dict[key]['time']
					start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
					end_date_time           =  start_date_time + timedelta(hours=schedules_dict[key]['cleaning_hours']) 	
					start_time              =  start_date_time.time()
					end_time                =  end_date_time.time()

					#schedule
					order_schedule = OrderScheduler.objects.create(order=order,status='CONFIRMED',customer_address=evaluation_details.address,evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book_id=services[service_detail]['id'],no_of_cleaners=schedules_dict[key]['no_of_cleaners'],cleaning_hours=schedules_dict[key]['cleaning_hours'])

					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)						

					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
					active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					#included shift cleaners
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date()))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)


					leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
					cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

					for service_detail in services.keys():
						service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
						service_type   		        = service_book.service_type.name 			
					
						if service_type == 'General Cleaning':
							leaders = leaders.filter(is_general_skill=True)
							cleaners= cleaners.filter(is_general_skill=True).order_by('user_type')
						elif service_type == 'Deep Cleaning':
							leaders = leaders.filter(is_deep_skill=True)
							cleaners= cleaners.filter(is_deep_skill=True).order_by('user_type')
						elif service_type == 'Sterilization':
							leaders = leaders.filter(is_sterilization_skill=True)
							cleaners= cleaners.filter(is_sterilization_skill=True).order_by('user_type')
						elif service_type == 'Upholstery Cleaning':
							leaders = leaders.filter(is_upholstery_skill=True)
							cleaners= cleaners.filter(is_upholstery_skill=True).order_by('user_type')
						elif service_type == 'Kitchen Cleaning':
							leaders = leaders.filter(is_kitchen_skill=True)
							cleaners= cleaners.filter(is_kitchen_skill=True).order_by('user_type')
						elif service_type == 'Carpet Cleaning':
							leaders = leaders.filter(is_carpet_skill=True)
							cleaners= cleaners.filter(is_carpet_skill=True).order_by('user_type')
						elif service_type == 'Mattress Cleaning':
							leaders = leaders.filter(is_mattress_skill=True)
							cleaners= cleaners.filter(is_mattress_skill=True).order_by('user_type')
						elif service_type == 'Outdoor Cleaning':
							leaders = leaders.filter(is_outdoor_skill=True)
							cleaners= cleaners.filter(is_outdoor_skill=True).order_by('user_type')
						elif service_type == 'Storage Area':
							leaders = leaders.filter(is_storagearea_skill=True)
							cleaners= cleaners.filter(is_storagearea_skill=True).order_by('user_type')
						elif service_type == 'Window Cleaning':
							leaders = leaders.filter(is_window_skill=True)
							cleaners= cleaners.filter(is_window_skill=True).order_by('user_type')
						elif service_type == 'Car Parking Umbrella':
							leaders = leaders.filter(is_carparkingumbrella_skill=True)
							cleaners= cleaners.filter(is__skill=True).order_by('user_type')
						elif service_type == 'Facade Cleaning':
							leaders = leaders.filter(is_facade_skill=True)
							cleaners= cleaners.filter(is_facade_skill=True).order_by('user_type')						
		
					#cleaning team
					cleaning_team  = CleaningTeam.objects.create(order_scheduler=order_schedule,team_leader=leaders.first(),start_at=start_date_time,end_at=end_date_time)
					#cleaning team members
					no_of_cleaners = int(schedules_dict[key]['no_of_cleaners'])-1
					cleaning_team_member_array = []
					for i in range(no_of_cleaners):
						cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=cleaners[i],start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))
					cleaning_team_member_array.append(CleaningTeamMember(team=cleaning_team,member=leaders.first(),start_at=start_date_time,end_at=end_date_time,start_time=start_time,end_time=end_time))

					CleaningTeamMember.objects.bulk_create(cleaning_team_member_array)
		response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)

#resubmit order apis
class ReSubmitOrder(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	
	def get(self,request,order_id):
		order = Order.objects.select_related('evaluation').filter(Q(evaluation__quatation_status='REJECTED')|Q(evaluation__quatation_status='EXPIRED')).get(id=order_id)
		if order:
			order.order_status = None
			order.evaluation.quatation_status = 'PENDING'
			order.evaluation.quatation_approved_date     = None
			order.evaluation.quatation_rejected_date     = None
			order.evaluation.created                     = timezone.now()
			order.evaluation.quatation_expiry_date       = timezone.now()+timedelta(14)

			order.evaluation.save()
			order.save()
		
			messages.success(request,"You have Succesfully Re-submitted the Order")

		return redirect('common_items:client-orderdetails',order_id)

#edit order apis
class EditOrderDetails(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	
	def get(self,request,order_id):
		response_dict = {}
		evaluation_book_id               = request.GET.get('evaluation_book_id')
		evaluation_book                  = EvaluationBook.objects.prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes')),to_attr='sections')).get(id=evaluation_book_id)
		response_dict['section_details'] = EvaluationBookSerializer(evaluation_book).data
		return Response(response_dict,HTTP_200_OK)

	def post(self,request,order_id):
		response_dict = {}
		response_dict['success'] = False
		action = request.data.get('action_type')

		order = Order.objects.select_related('evaluation').get(id=order_id)

		if action == 'add_section':                       
			section_save_serializer                    = EvaluationBookSectionSerializer(data=request.data.get('section_details'))
			if section_save_serializer.is_valid():
				evaluation_book__id                    = request.data.get('evaluation_book__id')
				evaluation_book                        = EvaluationBook.objects.select_related('evaluation_details').prefetch_related(Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).get(id=evaluation_book__id)
				total_cleanings                        = evaluation_book.order_scheduler_book_details.count()

				if evaluation_book.cleaning_policy == 'SUBSCRIPTION':
					saved_section                          = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings,section_net_cost=section_save_serializer.validated_data['section_cost']*total_cleanings)
				else:
					saved_section                          = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings,section_net_cost=section_save_serializer.validated_data['section_cost'])

				evaluation_book.estimated_cost     				  += saved_section.section_net_cost
				evaluation_book.total_cost         				  += saved_section.section_net_cost
				evaluation_book.save()

				evaluation_book.evaluation_details.estimated_cost += saved_section.section_net_cost
				evaluation_book.evaluation_details.total_cost     += saved_section.section_net_cost
				evaluation_book.evaluation_details.save()

				order.remining_amount += saved_section.section_net_cost
				order.total_amount    += saved_section.section_net_cost
				order.save()

				order.evaluation.total_cost        += saved_section.section_net_cost
				order.evaluation.estimated_cost    += saved_section.section_net_cost
				order.evaluation.save()

				response_dict['section_success']       = True
				response_dict['success']  = True

			else:
				errors= section_save_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['section_Error']=key +':'+ error[0]
				response_dict['section_Error_List'] = section_save_serializer.errors

				response_dict['section_add_success']  = False

				return Response(response_dict,HTTP_200_OK)

		elif action == 'edit_section':
			section_id        = request.data.get('section_id')
			old_section       = EvaluationBookSection.objects.select_related('evaluation_book__evaluation_details').get(id=section_id)
			old_section_cost  = old_section.section_net_cost

			section_save_serializer        = EvaluationBookSectionSerializer(data=request.data.get('section_details'),instance=old_section)
			if section_save_serializer.is_valid():
				evaluation_book__id                    = request.data.get('evaluation_book__id')
				evaluation_book                        = EvaluationBook.objects.select_related('evaluation_details').prefetch_related(Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).get(id=evaluation_book__id)
				total_cleanings                        = evaluation_book.order_scheduler_book_details.count()

				if evaluation_book.cleaning_policy == 'SUBSCRIPTION':
					saved_section                          = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings,section_net_cost=section_save_serializer.validated_data['section_cost']*total_cleanings)
				else:
					saved_section                          = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings,section_net_cost=section_save_serializer.validated_data['section_cost'])

				evaluation_book.estimated_cost     				  += (old_section_cost-saved_section.section_net_cost)
				evaluation_book.total_cost         				  += (old_section_cost-saved_section.section_net_cost)
				evaluation_book.save()

				evaluation_book.evaluation_details.estimated_cost += (old_section_cost-saved_section.section_net_cost)
				evaluation_book.evaluation_details.total_cost     += (old_section_cost-saved_section.section_net_cost)
				evaluation_book.evaluation_details.save()

				order.remining_amount += (old_section_cost-saved_section.section_net_cost)
				order.total_amount    += (old_section_cost-saved_section.section_net_cost)
				order.save()

				order.evaluation.total_cost   += (old_section_cost-saved_section.section_net_cost)
				order.evaluation.estimated_cost    += (old_section_cost-saved_section.section_net_cost)
				order.evaluation.save()

				#delete and add keynotes
				keynotes     = request.data.get('keynotes')
				new_keynotes = []
				EvaluationSectionKeynote.objects.filter(evaluation_section=saved_section).delete()
				for keynote in keynotes:
					new_keynotes.append(EvaluationSectionKeynote(evaluation_section=saved_section,sub_area=keynote['sub_area'],quantity=keynote['quantity']))
				EvaluationSectionKeynote.objects.bulk_create(new_keynotes)

				response_dict['edit_success']       = True
				response_dict['success']  = True

			else:
				errors= section_save_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['section_Error']=key +':'+ error[0]
				response_dict['section_Error_List'] = section_save_serializer.errors

				response_dict['section_add_success']  = False

				return Response(response_dict,HTTP_200_OK)

		elif action == 'delete_section':
			section_id = request.data.get('section_id')
			saved_section    = EvaluationBookSection.objects.select_related('evaluation_book__evaluation_details').get(id=section_id)
			
			saved_section.evaluation_book.estimated_cost     				  += saved_section.section_net_cost
			saved_section.evaluation_book.total_cost         				  += saved_section.section_net_cost
			saved_section.evaluation_book.save()

			saved_section.evaluation_book.evaluation_details.estimated_cost += saved_section.section_net_cost
			saved_section.evaluation_book.evaluation_details.total_cost     += saved_section.section_net_cost
			saved_section.evaluation_book.evaluation_details.save()

			order.remining_amount += saved_section.section_net_cost
			order.total_amount    += saved_section.section_net_cost
			order.save()

			order.evaluation.total_cost   += saved_section.section_net_cost
			order.evaluation.estimated    += saved_section.section_net_cost
			order.evaluation.save()

			saved_section.delete()

			response_dict['section_delete_success']  = True
			response_dict['success']  = True

			return Response(response_dict,HTTP_200_OK)	
		
		elif action == 'edit_discount':
			#update payment policy and discount
			payment_method      = request.data.get('payment_method')
			discount_amount     = request.data.get('discount_amount')
			old_discount_amount = order.evaluation.discount 
			if order.amount_paid == 0:
				if payment_method == 'PREPAID':
					order.evaluation.before_cleaning_amount = 0
					order.evaluation.after_cleaning_amount  = 0
					order.evaluation.payment_method         = 'PREPAID'

					order.evaluation.discount               = discount_amount
					order.evaluation.total_cost             = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.total_amount                      = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.remining_amount                   = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
				
				elif payment_method == 'BREAKDOWN':
					before_cleaning_amount                  = request.data.get('before_cleaning_amount')
					after_cleaning_amount                   = request.data.get('after_cleaning_amount')
					order.evaluation.before_cleaning_amount = before_cleaning_amount
					order.evaluation.after_cleaning_amount  = after_cleaning_amount
					order.evaluation.payment_method         = 'BREAKDOWN'

					order.evaluation.discount                = discount_amount
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.total_amount                       = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.remining_amount                    = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)

				elif payment_method == 'POSTPAID':
					order.evaluation.before_cleaning_amount = 0
					order.evaluation.after_cleaning_amount  = 0
					order.evaluation.payment_method         = 'POSTPAID'

					order.evaluation.discount                = discount_amount
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.total_amount                       = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
					order.remining_amount                    = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount)
				
				#to check payment completed
				if order.remining_amount == 0:
					order.payment_status = 'COMPLETED'
				
				order.evaluation.save()
				order.save()

				response_dict['success']  = True

		elif action == 'add_cleaning':
			evaluation_book_id = request.data.get('evaluation_book_id')
			evaluation_book    = EvaluationBook.objects.select_related('evaluation_details').get(id=evaluation_book_id) 
			
			cleaning_date 	   = request.data.get('cleaning_date')
			cleaning_time      = request.data.get('cleaning_time')
			cleaning_hours 	   = float(request.data.get('cleaning_hours'))
			start_at           = datetime.strptime(cleaning_date+' '+cleaning_time,'%d-%m-%Y %I:%M %p')
			end_at             = start_at + timedelta(hours=cleaning_hours)
			no_of_cleaners     = request.data.get('no_of_cleaners')

			OrderScheduler.objects.create(order=order,evaluation_details=evaluation_book.evaluation_details,order_scheduler_book=evaluation_book,start_at=start_at,end_at=end_at,customer_address=evaluation_book.evaluation_details.address,status='CONFIRMED',no_of_cleaners=no_of_cleaners)
			
			response_dict['success']  = True

		elif action == 'edit_cleaning':
			schedule_id        = request.data.get('schedule_id')
			old_schedule       = OrderScheduler.objects.get(id=schedule_id)
			old_start_at       = old_schedule.start_at 
			old_end_at         = old_schedule.end_at

			cleaning_date 	   = request.data.get('cleaning_date')
			cleaning_time      = request.data.get('cleaning_time')
			cleaning_hours 	   = float(request.data.get('cleaning_hours'))
			start_at           = datetime.strptime(cleaning_date+' '+cleaning_time,'%d-%m-%Y %I:%M %p')
			end_at             = start_at + timedelta(hours=cleaning_hours)
			no_of_cleaners     = request.data.get('no_of_cleaners')

			cleaning_schedules = OrderScheduler.objects.filter(start_at=old_start_at,end_at=old_end_at,evaluation_details__evaluation=order.evaluation).select_related('evaluation_details__evaluation')
			 
			for cleaning_schedule in cleaning_schedules:	
				#update cleaning schedule
				cleaning_schedule.start_at 							= start_at
				cleaning_schedule.end_at   							= end_at
				cleaning_schedule.no_of_cleaners                    = no_of_cleaners
				cleaning_schedule.cleaning_hours                    = cleaning_hours
				cleaning_schedule.save()

				#delete cleaning team
				CleaningTeam.objects.filter(order_scheduler=cleaning_schedule).delete()

				#delete team member
				CleaningTeamMember.objects.filter(team__order_scheduler=cleaning_schedule).delete()
				
			response_dict['success']  = True

		return Response(response_dict,HTTP_200_OK)



from django.core.mail import send_mail,EmailMultiAlternatives
class EmailTest(APIView):
	def get(self,request):
		response_dict = {}

		#send mail
		msg_html = render_to_string('email/quatation.html',{})
		msg = EmailMultiAlternatives('Bleach Quatation', '', 'notification@bleach-kw.com', ['sonu.george@bleach-kw.com'], bcc=['ansab.m@bleach-kw.com'], cc=['ansabm2015@gmail.com'])
		msg.attach_alternative(msg_html, "text/html")
		msg.send(fail_silently=False)

		response_dict['success'] = True
		return Response(response_dict,HTTP_200_OK)