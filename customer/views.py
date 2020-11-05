from django.shortcuts import render,redirect
from django.template.loader import render_to_string

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

from agent.views import generate_random_username

import requests

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
	

		return render(request,"customer/newquatation.html",{"order":order,"nonduplicate_schedules":nonduplicate_schedules})

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

		print(request.POST)
		if action == 'Approve':
			#UPDATE EVALUATION APPROVAL
			termsandconditions = request.POST.get('termsandconditions')
			if termsandconditions:
				evaluation_update = Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='APPROVED',payment_way=request.POST.get('payment_way'),quatation_approved_date=timezone.now())
				order_update      = Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='APPROVED_BY_CLIENT')
				
				evaluaation = Evaluation.objects.get(evaluation_id=evaluation_id,customer__username=user_name)

				language = evaluaation.customer.sms_preference
				
				if evaluaation.payment_method == 'PREPAID' or evaluaation.payment_method == 'BREAKDOWN':
					messages.success(request,"Quatation Approved Succesfully")
					url = "https://smsapi.future-club.com/fccsms.aspx"

					if language == 'ENGLISH':

						message = "Dear Customer, Please find the Invoice against the order number "+str(evaluaation.evaluation_id)+"  here http://15.206.173.198/customer/invoice/prw"+str(evaluaation.tracking_no)+""+str(evaluaation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
				
						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
					
					else:

						message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluaation.evaluation_id)+" في هذا الرابط http://15.206.173.198/customer/invoice/prw"+str(evaluaation.tracking_no)+""+str(evaluaation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
				
						querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
					
					headers = {
						'cache-control': "no-cache"
					}

					response = requests.request("GET", url, headers=headers, params=querystring)

					print(response.text,"respo")

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

		return render(request,"customer/invoice.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,})		

class PaymentResponse(View):
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
			payment_history = PaymentHistory.objects.create(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.GET.get('paymentid'),ref=request.GET.get('ref'),business_logic_post_date=request.GET.get('postdate'),track_id=request.GET.get('trackid'),transaction_id=request.GET.get('tranid'))	

			if payment_mode == 'before_cleaning' and order.preamount_paid != order.evaluation.before_cleaning_amount:
				order.preamount_paid   = amount_paid
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

			elif payment_mode == 'after_cleaning' and order.preamount_paid != order.evaluation.before_cleaning_amount:
				order.postamount_paid  = amount_paid
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'prepaid' and order.amount_paid != order.total_amount:
				order.amount_paid      = amount_paid
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid					

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'postpaid' and order.amount_paid != order.total_amount:
				order.amount_paid      = amount_paid
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()
			order.save()

			#payment receipt sms
			url = "https://smsapi.future-club.com/fccsms.aspx"

			if order.evaluation.customer.sms_preference == 'ENGLISH':

				message = "Dear Customer, We have successfully received your payment of amount "+ str(amount_paid) +" KD, (Transaction ID: "+ str(request.GET.get('tranid')) +", Ref ID: "+ str(request.GET.get('ref')) +") against the order number "+ str(order.order_no) +". Please find the Payment receipt here http://15.206.173.198/customer/payment/receipt/pvw"+ str(order.evaluation.tracking_no) +""+str(payment_history.id)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
			
			else:
				message = "عزيزي العميل، لقد تلقينا مدفوعاتك بنجاح مقابل رقم الطلب "+ order.order_no +". يرجى العثور على إيصال الدفع هنا http://15.206.173.198/customer/payment/receipt/pvw"+request.GET.get('paymentid')+". لأي مساعدة يرجى الاتصال بنا على9651882707 شكرا لاختيارك بليتش الكويت"
 

				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

			headers = {
				'cache-control': "no-cache"
			}

			response = requests.request("GET", url, headers=headers, params=querystring)

			print(response.text)

			#feedback sms
			# cleaning_team_detail = CleaningTeam.objects.select_related('order_scheduler__order').get(is_active=True,id=team_id)

			# order_feedback = Order.objects.select_related('evaluation__customer').filter(is_active=True,order_no=cleaning_team_detail.order_scheduler.order.order_no, payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
					
			# for ord in order_feedback:
			# 	order_data = ord

			# if order_feedback:

			# 	url = "https://www.fast2sms.com/dev/bulk"

			# 	if order_data.evaluation.customer.sms_preference == 'ENGLISH':

			# 		message = "Dear Customer, Thank you for choosing Bleach Kuwait. Kindly share your feedback for the order number "+ order_data.order_no +" here [feedback link]. For any assistance please contact us on +9651882707."
			# 		querystring = {"authorization":"B1XzkADlQ6r7YnMH0KVtux8b4JCjpw52OoRecmyNs9ghv3fWSFvXKzWsxVGZbfOQA2jSylrJ5YuRMDdk","sender_id":"FSTSMS","message":message,"language":"english","route":"p","numbers":"8848953520"}
				
			# 	else:
			# 		message = "عزيزينا العميل نرجوا أن تكون خدماتنا خازت على رضاكم و شكراً لاختياركم بليتش لخدمات التنظيف.  نرجوا التكرم بإنجاز الاستبيان الخاص بالطلب رقم "+ order_data.order_no +" (Feedback Link) وذلك لضمان جودة الخدمة. لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
			# 		querystring = {"authorization":"B1XzkADlQ6r7YnMH0KVtux8b4JCjpw52OoRecmyNs9ghv3fWSFvXKzWsxVGZbfOQA2jSylrJ5YuRMDdk","sender_id":"FSTSMS","message":message,"language":"arabic","route":"p","numbers":"8848953520"}

			# 	headers = {
			# 		'cache-control': "no-cache"
			# 	}

			# 	response = requests.request("GET", url, headers=headers, params=querystring)

			# 	print(response.text,",ess")

			# else:
			# 	pass


			return redirect('customer:payment-receipt','pvw'+str(evaluation_id_encrypted[0:11])+str(payment_history.id))
		else:

			#payment fail sms
			url = "https://smsapi.future-club.com/fccsms.aspx"

			if order.evaluation.customer.sms_preference == 'ENGLISH':

				message = "Dear Customer, Your payment against the order number "+ order.order_no +" has failed (Payment ID : "+str(request.GET.get('paymentid'))+", Ref. ID: "+ str(request.GET.get('ref')) +"). Click here to try again http://15.206.173.198/customer/invoice/prw"+str(order.evaluation.tracking_no)+""+str(order.evaluation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
			
			else:
				message = "عزيزي العميلفشل الدفع الخاص بك مقابل رقم الطلب "+ order.order_no +". اضغط هنا للمحاولة مرة أخرى http://15.206.173.198/customer/invoice/prw"+str(order.evaluation.tracking_no)+""+str(order.evaluation.customer.username)+" أي مساعدة يرجى الاتصال بنا على . +9651882707 شكرا لاختيارك بليتش الكويت"

				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+order.evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

			headers = {
				'cache-control': "no-cache"
			}

			response = requests.request("GET", url, headers=headers, params=querystring)

			print(response.text)

			return redirect('/customer/payment/failed/?udf1='+evaluation_id_encrypted+'&paymentid='+request.GET.get('paymentid')+'&ref='+request.GET.get('ref'))

class PaymentFailedResponse(View):
	def get(self,request):

		payment_id   = request.GET.get('paymentid')
		reference_id = request.GET.get('ref')

		evaluation_id_encrypted = request.GET.get("udf1")

		#for back to invoice
		try:
			order = Order.objects.get(order_no='BLC'+evaluation_id_encrypted[0:9]).select_related('evaluation__customer')
		except:
			order = None

		return render(request,"customer/paymentfailed.html",{'payment_id':payment_id,'evaluation_id_encrypted':evaluation_id_encrypted,'reference_id':reference_id,'order':order})			

class PaymentReceipt(View):
	def get(self,request,payment_id):

		original_payment_id    = payment_id[14:]
		evaluation_id 		   = 'BLC'+payment_id[3:14]
		print(original_payment_id)
		print(evaluation_id)

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

		return render(request,"customer/receipt-voucher.html",{'payment_history':payment_history,'nonduplicate_schedules':nonduplicate_schedules,})




#for download

# from django.core.files.storage import FileSystemStorage
# from django.http import HttpResponse
# from django.template.loader import render_to_string

# from weasyprint import HTML

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
    

	html_string = render_to_string('customer/newquatation.html', {"order":order,"nonduplicate_schedules":nonduplicate_schedules})

	html = HTML(string=html_string,base_url=request.build_absolute_uri())
	html.write_pdf(target='/home/pdf/tmp/quatation/quatation.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/quatation/')
	with fs.open('quatation.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="quatation.pdf"'
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
		response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
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
		response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
		return response
	return response	