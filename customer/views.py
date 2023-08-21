from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import HttpResponse,JsonResponse
from django_countries import countries
from django.core.mail import send_mail,EmailMultiAlternatives
from django.views import View

from bleach_crm_ps.utils import get_error
from agent.views import generate_random_username

from googletrans import Translator

from dateutil.relativedelta import relativedelta
import random
import string
import functools
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db import transaction
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast,TruncDate,ExtractMonth,ExtractYear,Concat
from django.db.models import Prefetch
from django.contrib import messages

from bleachinventory.models import PurchaseOrder,PurchaseOrderItems,CheckOutItems,RequestOrder,RequestOrderItems
from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType,EvaluationSectionAddons
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,Promocode,CancellOrderAmountHistory,XeroInvoice
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking,CustomerCart,CartService,CartSchedule,CartServiceFloor
from Api.models import XeroConnection
from bleachadmin.models import ServiceProductivity,ServicePriceRange,ServiceAddOns
from agent.forms import UserProfileForm,AddressForm
from evaluator.forms import QuatationServiceFormCustomer
from itertools import chain
from agent.views import generate_random_username

import requests
import logging

#restframe work 
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK 
from rest_framework import status
from rest_framework.authentication import TokenAuthentication 
from rest_framework.authtoken.models import Token
from bleach_crm_ps.api_permissions import IsCustomerPermission
from customer.serilizers import UserProfileEditSerializer,CartServiceShowSerializer,CartServiceSerializer,CartScheduleSerializer,UserProfileSerializer,AddressSerializer,AddressSaveSerializer,EvaluationBookSerializer,EvaluationBookSectionSerializer,EvaluationSectionKeynoteSerializer,EvaluationSerializer,OrderSerializer,EvaluationDetailsSerializer,CustomerBookingSerializer,EvaluationSectionAddonSerializer
from bleachadmin.serializers import ServiceAddOnsSerializer
from agent.serializers import UserProfileShowSerializer
from Api.serializers import ServicePriceRangeSerializer,OrderScheduleShowSerializer,EvaluationBookAPISerializer,SectionAPISerializer,EvaluationDetailsAPISerializer

logger = logging.getLogger(__name__)

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
		evaluation_id           = 'BLC'+evaluation_id_encrypted[3:14]
		user_name               =  evaluation_id_encrypted[14:]


		order                   = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate'),to_attr='orderschedules')).annotate(customerbooking=Sum(Case(When(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING',then=1),default=0,output_field=IntegerField()))).get(is_active=True,order_no=evaluation_id,evaluation__customer__username=user_name)


		nonduplicate_schedules  = []
		#Remove duplicates for subscription
		duplicate_schedules     = []
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

		#service details
		try:
			order_details = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='booksections')),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(customerbooking=Sum(Case(When(Q( Q(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING')&Q(evaluation__booking_evaluation__is_bookingcompleted=False) ),then=1),default=0,output_field=IntegerField()))).get(is_active=True,evaluation__evaluation_id=evaluation_id,evaluation__customer__username=user_name)
		except:
			order_details = None

		price_ranges 		= ServicePriceRange.objects.filter(is_active=True)

		return render(request,"customer/quotation.html",{"order":order,"order_details":order_details,"nonduplicate_schedules":nonduplicate_schedules,"price_ranges":price_ranges})

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
				order             = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(Q(is_active=True)&~Q(work_status='CLEANING_CANCELLED')),to_attr='bookschedules')),to_attr='orderschedules')).annotate(customerbooking=Sum(Case(When(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING',then=1),default=0,output_field=IntegerField()))).get(order_no=evaluation_id)

				if order.invoice_no:
					new_invoice_no = order.invoice_no
				else:
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

				#Save Individual cleaning price

				servicebooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation=order.evaluation)
				print(servicebooks,"evbooks")

				if servicebooks:
					cleaning_cost_sum          = 0
					total_cleanings            = len(order.orderschedules)
					discount_cost_sum          = 0
					additional_charge_cost_sum = 0
					count2                     = 0
					
					#new code
					
					for book in servicebooks:
						book_schedules = OrderScheduler.objects.filter(is_active=True,order_scheduler_book=book)
						print(book_schedules,"shedul")
						book_schedules_count = book_schedules.count()

						count                      = 0

						for schedule in book_schedules:
							count                                += 1
							count2                               += 1
							
							#service cost update
							if int(count) == int(book_schedules_count):
								schedule.cleaning_cost           = round(book.total_cost-cleaning_cost_sum,2)
								cleaning_cost_sum                 = 0
							else:
								schedule.cleaning_cost           = round(book.total_cost/book_schedules_count,2)
								cleaning_cost_sum                += schedule.cleaning_cost
							
							#discount and additional cost update	
							if total_cleanings != count2:
								schedule.discount_cost           = round(order.evaluation.discount/total_cleanings,2)
								schedule.additional_charge_cost  = round(order.evaluation.additional_charge/total_cleanings,2)
								discount_cost_sum                += schedule.discount_cost
								additional_charge_cost_sum       += schedule.additional_charge_cost
							else:	
								schedule.discount_cost           = round(order.evaluation.discount-discount_cost_sum,2)
								schedule.additional_charge_cost  = round(order.evaluation.additional_charge-additional_charge_cost_sum,2)
							
							schedule.save()
							
					#new code

				#sms and email
				evaluaation = Evaluation.objects.get(evaluation_id=evaluation_id,customer__username=user_name)

				evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluaation).first()
				address = evaluationdetails.address

				evaluationbooks = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True),to_attr='sections'))

				if address.floor == None and address.avenue == None:
					address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
				
				elif address.floor == None:
					address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
				
				elif address.avenue == None:
					address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
				
				else:
					address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

				separator = ", "
				
				language = evaluaation.customer.sms_preference
				
				#INVOICE MAIL AND SMS FOR PREPAID AND BREAK DOWN
				if evaluaation.payment_method == 'PREPAID' or evaluaation.payment_method == 'BREAKDOWN':
					messages.success(request,"Quatation Approved Succesfully")
					
					#Sms
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
					else:
						pass

					#send mail
					if evaluaation.customer.is_email == True :

						price_ranges 		= ServicePriceRange.objects.filter(is_active=True)
						
						msg_html = render_to_string('email/invoice.html',{"invoice":order,"address_list":separator.join(address_list),"evaluationbooks":evaluationbooks,"price_ranges":price_ranges})
						msg = EmailMultiAlternatives('Bleach Invoice', '', 'notification@bleach-kw.com', [evaluaation.customer.email])
						msg.attach_alternative(msg_html, "text/html")
						msg.send(fail_silently=False)

					###############################################################
					#Xero Integration
					xero                        = XeroConnection.objects.first()
					##xero Update Access Token and Refresh Token
					header                      = {
													'Authorization': 'Basic '+xero.client_encoded,
													'Content-Type': 'application/x-www-form-urlencoded'
														}
					body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
					token_response              = requests.post('https://identity.xero.com/connect/token',
															data=body,
															headers=header 
														).json()
					access_token                = token_response['access_token']
					refresh_token               = token_response['refresh_token']

					xero.access_token  = access_token
					xero.refresh_token = refresh_token
					xero.save()

					##Xero Contact
					if not order.evaluation.customer.xero_account_id:
						##Xero Create Customer ID and Save
						contact_data                = {
														"Name":order.evaluation.customer.name,
														"ContactNumber":order.evaluation.customer.mobile_number,
														"EmailAddress":order.evaluation.customer.email,
														"ContactStatus":"ACTIVE",
														"IsCustomer":True,
														"DefaultCurrency":"KWD"
																	}
														
						header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

						create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
																json=contact_data,
																headers=header 
															).json()

						order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
						order.evaluation.customer.save()

					#Xero Invoice
					if order.evaluation.payment_method == 'PREPAID':
						Amount = order.evaluation.total_cost 
						##Invoice Line Item 
						LineItems                 = []
						LineItems.append({
							"Description":"ONE TIME SERVICE",
							"Quantity":"1",
							"UnitAmount":Amount,
							"AccountCode":1207004,
							"TaxType":"NONE"
										}
							)
						InvoiceNumber  = order.invoice_no

						payment_policy = 'PREPAID'
					elif order.evaluation.payment_method == 'BREAKDOWN':
						
						Amount = order.evaluation.before_cleaning_amount 
						##Invoice Line Item 
						LineItems                 = []
						LineItems.append({
							"Description":"ONE TIME SERVICE",
							"Quantity":"1",
							"UnitAmount":Amount,
							"AccountCode":1207004,
							"TaxType":"NONE"
										}
							)
						InvoiceNumber  = order.invoice_no+'A'
						
						payment_policy = 'BEFORE CLEANING'
					else:
						pass

					invoice_data              = 	{
													"Type":"ACCREC",
													"Contact":{
														"ContactID":order.evaluation.customer.xero_account_id
													},
													"Date":order.created.strftime('%Y-%m-%d'),
													"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
													"LineAmountTypes":"NoTax",
													"InvoiceNumber":InvoiceNumber,
													"Reference":order.order_no,
													"Status":"SUBMITTED",
													"LineItems":LineItems
													}

					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
					print(create_invoice)
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

					###################################################################

					#Redirect to Invoice
					new_evaluation_id_encrypted = 'prw'+evaluation_id_encrypted[3:]
					if order.customerbooking:
						return redirect('customer:bookinginvoice',new_evaluation_id_encrypted)
					else:
						if evaluaation.payment_method == 'SUBSCRIPTION':
							return redirect('customer:subscriptioninvoice',new_evaluation_id_encrypted)
						else:
							return redirect('customer:invoice',new_evaluation_id_encrypted)

				else:
					messages.success(request,"Quatation Approved Succesfully")

					return redirect('customer:quatation',evaluation_id_encrypted)

				Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(quatation_status='APPROVED',quatation_approved_date=timezone.now())

				Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='APPROVED_BY_CLIENT')
				
				if order.customerbooking:
					return redirect('customer:bookinginvoice',evaluation_id_encrypted)
				else:
					if evaluaation.payment_method == 'SUBSCRIPTION':
						return redirect('customer:subscriptioninvoice',evaluation_id_encrypted)
					else:
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


		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,order_no=evaluation_id,evaluation__customer__username=user_name)

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

		#service details
		try:
			order_details = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='booksections')),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(customerbooking=Sum(Case(When(Q( Q(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING')&Q(evaluation__booking_evaluation__is_bookingcompleted=False) ),then=1),default=0,output_field=IntegerField()))).get(is_active=True,evaluation__evaluation_id=evaluation_id,evaluation__customer__username=user_name)
		except:
			order_details = None

		price_ranges 		= ServicePriceRange.objects.filter(is_active=True)

		return render(request,"customer/quotation.html",{"order":order,"order_details":order_details,"nonduplicate_schedules":nonduplicate_schedules,"per_job_cost":per_job_cost,"price_ranges":price_ranges,})
 
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
				order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='invoice_evaluation_details'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('order_scheduler_book').order_by('start_at').prefetch_related(Prefetch('order_scheduler_book__order_scheduler_book_details',queryset=OrderScheduler.objects.filter(Q(is_active=True)&~Q(work_status='CLEANING_CANCELLED')),to_attr='bookschedules')),to_attr='orderschedules')).annotate(customerbooking=Sum(Case(When(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING',then=1),default=0,output_field=IntegerField()))).get(order_no=evaluation_id)

				if order.invoice_no:
					new_invoice_no = order.invoice_no 
				else:
					last_invoice_no  		 = Order.objects.filter(is_active=True).aggregate(t=Max('invoice_no'))['t']
					current_invoice_starting = str(timezone.now().year)		
					if current_invoice_starting == last_invoice_no[0:4] and last_invoice_no:
						new_invoice_no 		 = str(int(last_invoice_no[4:]) + 1 )
						new_invoice_no 		 = last_invoice_no[0:-(len(new_invoice_no))]+new_invoice_no
					else:
						new_invoice_no 		 = str(timezone.now().year)+'00001'
				
				order_update      = Order.objects.filter(order_no=evaluation_id,evaluation__customer__username=user_name).update(order_status='APPROVED_BY_CLIENT',invoice_no=new_invoice_no)
				
								
				#Save Individual cleaning price

				servicebooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation=order.evaluation)
				print(servicebooks,"evbooks")

				if servicebooks:
					cleaning_cost_sum          = 0
					total_cleanings            = len(order.orderschedules)
					discount_cost_sum          = 0
					additional_charge_cost_sum = 0
					count2                     = 0
					
					#new code
					
					for book in servicebooks:
						book_schedules = OrderScheduler.objects.filter(is_active=True,order_scheduler_book=book)
						
						book_schedules_count = book_schedules.count()

						count                      = 0

						for schedule in book_schedules:
							count                                += 1
							count2                               += 1
							
							#service cost update
							if int(count) == int(book_schedules_count):
								schedule.cleaning_cost           = round(book.total_cost-cleaning_cost_sum,2)
								cleaning_cost_sum                 = 0
							else:
								schedule.cleaning_cost           = round(book.total_cost/book_schedules_count,2)
								cleaning_cost_sum                += schedule.cleaning_cost
							
							#discount and additional cost update	
							if total_cleanings != count2:
								schedule.discount_cost           = round(order.evaluation.discount/total_cleanings,2)
								schedule.additional_charge_cost  = round(order.evaluation.additional_charge/total_cleanings,2)
								discount_cost_sum                += schedule.discount_cost
								additional_charge_cost_sum       += schedule.additional_charge_cost
							else:	
								schedule.discount_cost           = round(order.evaluation.discount-discount_cost_sum,2)
								schedule.additional_charge_cost  = round(order.evaluation.additional_charge-additional_charge_cost_sum,2)
							
							schedule.save()

				###############################################################
				#If Advance Amount Integrate with Xero
				if order.subscription_topay > 0:
					#Xero Integration
					xero                        = XeroConnection.objects.first()
					##xero Update Access Token and Refresh Token
					header                      = {
													'Authorization': 'Basic '+xero.client_encoded,
													'Content-Type': 'application/x-www-form-urlencoded'
														}
					body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
					token_response              = requests.post('https://identity.xero.com/connect/token',
															data=body,
															headers=header 
														).json()
					access_token                = token_response['access_token']
					refresh_token               = token_response['refresh_token']

					xero.access_token  = access_token
					xero.refresh_token = refresh_token
					xero.save()

					##Xero Contact
					if not order.evaluation.customer.xero_account_id:
						##Xero Create Customer ID and Save
						contact_data                = {
														"Name":order.evaluation.customer.name,
														"ContactNumber":order.evaluation.customer.mobile_number,
														"EmailAddress":order.evaluation.customer.email,
														"ContactStatus":"ACTIVE",
														"IsCustomer":True,
														"DefaultCurrency":"KWD"
																	}
														
						header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

						create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
																json=contact_data,
																headers=header 
															).json()

						order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
						order.evaluation.customer.save()

					#Xero Invoice
					Amount = order.subscription_topay 
					##Invoice Line Item 
					LineItems        = []
					LineItems.append({
						"Description":"SUBSCRIPTION",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1207004,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber  = order.invoice_no+'A'

					payment_policy = 'SUBSCRIPTION'

					invoice_data        = 	{
												"Type":"ACCREC",
												"Contact":{
													"ContactID":order.evaluation.customer.xero_account_id
												},
												"Date":order.created.strftime('%Y-%m-%d'),
												"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
												"LineAmountTypes":"NoTax",
												"InvoiceNumber":InvoiceNumber,
												"Reference":order.order_no,
												"Status":"AUTHORISED",
												"LineItems":LineItems
											}

					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

				###################################################################
				return redirect('customer:subscriptioninvoice',evaluation_id_encrypted)
			
			else:
				messages.error(request,"Please Read Terms & Conditions and Agree")
				return redirect('customer:subscriptionquatation',evaluation_id_encrypted)

		return redirect('customer:subscriptionquatation',evaluation_id_encrypted)

class EditCustomerProfile(APIView):
	permission_classes     = (IsAuthenticated,)
	authentication_classes = (TokenAuthentication,)

	def post(self,request):
		response_dict = {'success':False}

		customer_id = request.data.get('id')
		customer    = UserProfile.objects.get(id=customer_id,is_active=True)

		customer_edit_serializer     = UserProfileEditSerializer(instance=customer,data=request.data)

		if customer_edit_serializer.is_valid():
			customer_edit_serializer.save()
			
			response_dict['success']   = True
			response_dict['message']   = 'Customer Profile Updated Succesfully'

		else:
			response_dict['message']   = get_error(customer_edit_serializer)

		return Response(response_dict, HTTP_200_OK)

class BleachCustomerInvoice(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='booksections')),to_attr='evaluationbooks')),to_attr='evaluationdetails')).annotate(customerbooking=Sum(Case(When(Q( Q(evaluation__booking_evaluation__booking_type='CLEANINGBOOKING')&Q(evaluation__booking_evaluation__is_bookingcompleted=False) ),then=1),default=0,output_field=IntegerField()))).get(is_active=True,evaluation__evaluation_id=evaluation_id,evaluation__customer__username=user_name)

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

		price_ranges 		= ServicePriceRange.objects.filter(is_active=True)

		price_ranges 		= ServicePriceRange.objects.filter(is_active=True)

		return render(request,"customer/bleach-invoice.html",{'order':order,'firstname':firstname,'lastname':lastname,'customer_ip_address':customer_ip_address,"price_ranges":price_ranges,"price_ranges":price_ranges,})		

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

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,evaluation__evaluation_id=evaluation_id,evaluation__customer__username=user_name)

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

		price_ranges 		= ServicePriceRange.objects.filter(is_active=True)

		return render(request,"customer/customer_invoice.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,'firstname':firstname,'lastname':lastname,'customer_ip_address':customer_ip_address,"price_ranges":price_ranges})		

	def post(self,request,evaluation_id):

		action            = request.POST.get('action_type')
		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		if action == 'CASH/CHEQUE':
			Evaluation.objects.filter(evaluation_id=evaluation_id,customer__username=user_name).update(payment_way='CASH/CHEQUE')
			messages.success(request,"Cash/Cheque payment method approved !")
			print("Cash or check")
		return redirect('customer:invoice',evaluation_id_encrypted)


class CustomerSubscriptionInvoice(View):
	def get(self,request,evaluation_id):

		#evaluation id decryption
		evaluation_id_encrypted = evaluation_id
		evaluation_id = 'BLC'+evaluation_id_encrypted[3:14]
		user_name     =  evaluation_id_encrypted[14:]

		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='evaluationbooksection')),to_attr='orderschedules')).get(is_active=True,evaluation__evaluation_id=evaluation_id,evaluation__customer__username=user_name)

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
		
		price_ranges 		= ServicePriceRange.objects.filter(is_active=True)

		return render(request,"customer/customer_invoice_subscription.html",{'order':order,'nonduplicate_schedules':nonduplicate_schedules,'firstname':firstname,'lastname':lastname,'customer_ip_address':customer_ip_address,"completed_jobs_count":completed_jobs_count,"price_ranges":price_ranges,})

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

		logger.info(evaluation_id_encrypted)
		logger.info(amount_paid)
		logger.info(order_status)

		#Booking through Website - Order Creation
		if order_status == 'CUSTOMER_BOOKING' :
			customer_cart = CustomerCart.objects.prefetch_related(Prefetch('cart_service',queryset=CartService.objects.filter(is_active=True).prefetch_related(Prefetch('cart_service_floor',queryset=CartServiceFloor.objects.all(),to_attr='cart_service_floors')),to_attr='cart_services'),Prefetch('cart_schedule',queryset=CartSchedule.objects.filter(is_active=True),to_attr='cart_schedules')).get(id=int(evaluation_id_encrypted))
			logger.info("customer booking")

			#Evaluation
			tracking_no  = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')
			current_blc_starting = int(str(timezone.now().year)+str(timezone.now().month).zfill(2))				
			if current_blc_starting == int(str(tracking_no)[:6]):
				new_tracking_no = int(tracking_no)+1
				evaluation_no   = 'BLC'+str(new_tracking_no)
			else:
				evaluation_no = 'BLC'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10001'
				tracking_no   = int(str(timezone.now().year)+str(timezone.now().month).zfill(2)+'10000')

			if customer_cart.promocode:
				promocode = Promocode.objects.filter(promocode=customer_cart.promocode,is_active=True).first()
				promocode.total_used += 1
				promocode.save()

				is_promocode_applied = True
			else:
				is_promocode_applied = False

			evaluation = Evaluation.objects.create(evaluation_id=evaluation_no,tracking_no=int(tracking_no)+1,customer=customer_cart.customer,estimated_cost=customer_cart.total_cost,discount=customer_cart.cart_discount,promocode_amount=customer_cart.promocode_amount,is_promocode_applied=is_promocode_applied,total_cost=customer_cart.final_cost,payment_method='PREPAID',payment_way='ONLINE',quatation_status='APPROVED',quatation_approved_date=timezone.now(),quatation_expiry_date=timezone.now()+timedelta(14))

			print(evaluation.evaluation_id,"evalid")

			#Booking Number
			booking_id               = CustomerBooking.objects.filter(is_active=True).aggregate(t=Max('booking_id'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_booking_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_booking_starting == int(str(booking_id)[:4]):
				new_booking_id = int(booking_id)+1
			else:
				new_booking_id = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')

			#Customer Booking
			customerbooking = CustomerBooking.objects.create(booking_id=new_booking_id,booking_type='CLEANINGBOOKING',evaluation=evaluation,is_bookingcompleted=True)

			#order
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

			order       = Order.objects.create(evaluation=evaluation,order_no=evaluation.evaluation_id,invoice_no=new_invoice_no,order_status='APPROVED_BY_CLIENT',total_amount=customer_cart.final_cost,remining_amount=customer_cart.final_cost)

			if amount_paid == 0:
				order.amount_paid       = 0
				order.remining_amount   = 0			
				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()
				order.save()

			customer_address = Address.objects.get( id=int(request.GET.get('udf5')) )
			
			#Evaluation_details
			evaluation_details = EvaluationDetails.objects.create(evaluation=evaluation,address=customer_address,estimated_cost=customer_cart.total_cost,total_cost=customer_cart.total_cost)

			#Evaluation Books,Sections,Schedules 
			for cart_service in customer_cart.cart_services:
				evaluation_book    = EvaluationBook.objects.create(evaluation_details=evaluation_details,service_type=cart_service.service_type, cleaning_policy=cart_service.cleaning_policy,area_type=cart_service.area_type,cleaning_method=cart_service.cleaning_method,location_type=cart_service.location_type,estimated_cost=cart_service.total_cost,total_cost=cart_service.total_cost)
				
				if cart_service.cart_service_floors:
					
					for floor in cart_service.cart_service_floors:
						
						evaluationbooksection = EvaluationBookSection.objects.create(evaluation_book=evaluation_book,section_name=floor.section_name,size=floor.size,unit=floor.unit,wall_type=floor.wall_type,floor_type=floor.floor_type,ceiling_type=floor.ceiling_type,section_cost=floor.section_cost,
						section_net_cost=floor.section_cost,sectiononly_cost=floor.section_cost,sectiononly_net_cost=floor.section_cost,section_cleanings=len(customer_cart.cart_schedules))
						
						keynotes_list = []

						keynotes_list.append(EvaluationSectionKeynote(evaluation_section=evaluationbooksection,sub_area="bathrooms",quantity=floor.bathrooms))
						keynotes_list.append(EvaluationSectionKeynote(evaluation_section=evaluationbooksection,sub_area="windows",quantity=floor.windows))
						keynotes_list.append(EvaluationSectionKeynote(evaluation_section=evaluationbooksection,sub_area="rooms",quantity=floor.rooms))
						
						EvaluationSectionKeynote.objects.bulk_create(keynotes_list)

						# floor.delete()
				else:
					evaluation_section = EvaluationBookSection.objects.create(evaluation_book=evaluation_book,section_name=cart_service.section_name,category=cart_service.category,dirt_level=cart_service.dirt_level,quantity=cart_service.quantity,size=cart_service.size,unit=cart_service.unit,
											age=cart_service.age,floor=cart_service.floor,apartment=cart_service.apartment,room=cart_service.room,wall_type=cart_service.wall_type,ceiling_type=cart_service.ceiling_type,floor_type=cart_service.floor_type,material=cart_service.material,colour=cart_service.colour,
											cause_of_stain=cart_service.cause_of_stain,age_of_stain=cart_service.age_of_stain,cement_residue=cart_service.cement_residue,oil_residue=cart_service.oil_residue,hall_size=cart_service.hall_size,window_side=cart_service.window_side,new_kitchen=cart_service.new_kitchen,
											is_cabinet=cart_service.is_cabinet,is_highprice_facade=cart_service.is_highprice_facade,is_highprice_window=cart_service.is_highprice_window,upholstery_type=cart_service.upholstery_type,vacuuming=cart_service.vacuuming,section_cost=cart_service.total_cost,
											section_net_cost=cart_service.total_cost,sectiononly_cost=cart_service.total_cost,sectiononly_net_cost=cart_service.total_cost,section_cleanings=len(customer_cart.cart_schedules))
				
				if cart_service.addon_name:
					EvaluationSectionAddons.objects.create(evaluation_section=evaluation_section,name=cart_service.addon_name,addon_cost=cart_service.addon_price,quantity=1,addon_net_cost=cart_service.addon_price,size=cart_service.addon_size)
				
				cleaning_cost_sum          = 0
				total_cleanings            = len(customer_cart.cart_schedules)
				count                      = 0
				cart_schedules             = []

				for cart_schedule in customer_cart.cart_schedules:
					count                                += 1
					
					#schedule cleaning cost calculation
					if int(count) == int(total_cleanings): #final iteration
						#sum of previous cleaning cost subtracted from book total to adjust the division amount properly.
						cleaning_cost           = round(evaluation_book.total_cost-cleaning_cost_sum,2)
						cleaning_cost_sum       = 0
					else: #iterations before the final iteration
						cleaning_cost           = round(evaluation_book.total_cost/total_cleanings,2)
						cleaning_cost_sum       += float(cleaning_cost)

					cart_schedules.append(OrderScheduler(order=order,evaluation_details=evaluation_details,order_scheduler_book=evaluation_book,start_at=cart_schedule.start_at,end_at=cart_schedule.end_at,customer_address=customer_address,status='CONFIRMED',no_of_cleaners=cart_schedule.no_of_cleaners,cleaning_hours=cart_schedule.cleaning_hours,hourly_cleaning_duration=cart_schedule.hourly_cleaning_duration,cleaning_cost=cleaning_cost))

				OrderScheduler.objects.bulk_create(cart_schedules)


		#Booking From CRM System
		else:
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
				order.remining_amount   = float(order.remining_amount)-float(amount_paid)
				order.subscription_topay= 0
				order.is_advance        = False
				#to check payment completed
				if order.remining_amount == 0:
					order.payment_status         = 'COMPLETED'
					order.payment_completed_date = timezone.now()					
			
			elif payment_mode == 'before_cleaning' and order.preamount_paid != order.evaluation.before_cleaning_amount:
				order.preamount_paid   = amount_paid
				order.amount_paid      = amount_paid
				order.remining_amount  = float(order.remining_amount)-float(amount_paid)

			elif payment_mode == 'after_cleaning' and order.postamount_paid != order.evaluation.after_cleaning_amount:
				order.postamount_paid  += amount_paid
				order.amount_paid      += amount_paid
				order.remining_amount   = float(order.remining_amount)-float(amount_paid)

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'prepaid' and order.amount_paid != order.total_amount:
				order.amount_paid       += amount_paid
				order.remining_amount   = float(order.remining_amount)-float(amount_paid)			

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'postpaid' and order.amount_paid != order.total_amount:
				order.amount_paid      += amount_paid
				order.remining_amount   = float(order.remining_amount)-float(amount_paid)

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()
			order.save()

			##########################################################################################
			#Xero Integration
			xero          = XeroConnection.objects.first()
			#Update Access Token and Refresh Token
			header                      = {
											'Authorization': 'Basic '+xero.client_encoded,
											'Content-Type': 'application/x-www-form-urlencoded'
												}
			body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
			token_response              = requests.post('https://identity.xero.com/connect/token',
													data=body,
													headers=header 
												).json()
			access_token                = token_response['access_token']
			refresh_token               = token_response['refresh_token']

			xero.access_token  = access_token
			xero.refresh_token = refresh_token
			xero.save()

			header                      = {
											'xero-tenant-id': xero.tenant_id,
											'Authorization': 'Bearer '+access_token,
											'Accept': 'application/json',
											'Content-Type': 'application/json'
												}

			
			#payment policy setup
			if payment_mode == 'postpaid':
				payment_policy = 'POSTPAID'
			elif payment_mode == 'prepaid':
				payment_policy = 'PREPAID'
			elif payment_mode == 'before_cleaning':
				payment_policy = 'BEFORE CLEANING'
			elif payment_mode == 'after_cleaning':
				payment_policy = 'AFTER CLEANING'
			elif payment_mode == 'subscription':
				payment_policy = 'SUBSCRIPTION'

			#Invoice Authorize
			if payment_policy == 'PREPAID':
				BankCharge = .250
				Amount     = float(order.evaluation.total_cost)  
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				LineItems.append({
					"Description":"BANK CHARGE",
					"Quantity":"1",
					"UnitAmount":-BankCharge,
					"AccountCode":3202014,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no

				invoice_data        = 	{
									"Type":"ACCREC",
									"LineAmountTypes":"NoTax",
									"InvoiceNumber":InvoiceNumber,
									"Reference":order.order_no,
									"Status":"AUTHORISED",
									"LineItems":LineItems
								}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()
				
				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None
				
				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
				
				#Delete Unwanted invoice
				InvoiceNumber  = order.invoice_no+'A'

				invoice_data        = 	{
									"Type":"ACCREC",
									"LineAmountTypes":"NoTax",
									"InvoiceNumber":InvoiceNumber,
									"Reference":order.order_no,
									"Status":"DELETED"
								}

				##xero Delete Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				delete_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()

			if payment_policy == 'BEFORE CLEANING':
				#Before Invoice
				BankCharge = .250
				Amount     = float(order.evaluation.before_cleaning_amount) 
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				LineItems.append({
					"Description":"BANK CHARGE",
					"Quantity":"1",
					"UnitAmount":-BankCharge,
					"AccountCode":3202014,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no+'A'

				invoice_data        = 	{
									"Type":"ACCREC",
									"LineAmountTypes":"NoTax",
									"InvoiceNumber":InvoiceNumber,
									"Reference":order.order_no,
									"Status":"AUTHORISED",
									"LineItems":LineItems
								}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()
				
				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None
				
				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
				
				#Delete Unwanted invoice
				InvoiceNumber  = order.invoice_no

				invoice_data        = 	{
									"Type":"ACCREC",
									"LineAmountTypes":"NoTax",
									"InvoiceNumber":InvoiceNumber,
									"Reference":order.order_no,
									"Status":"DELETED"
								}
				##xero Delete Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				delete_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()

			if payment_policy == 'AFTER CLEANING':
				#Before Invoice
				BankCharge = .250
				Amount     = float(order.evaluation.after_cleaning_amount)
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				LineItems.append({
					"Description":"BANK CHARGE",
					"Quantity":"1",
					"UnitAmount":-BankCharge,
					"AccountCode":3202014,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no+'B'

				invoice_data   = 	{
									"Type":"ACCREC",
									"LineAmountTypes":"NoTax",
									"InvoiceNumber":InvoiceNumber,
									"Reference":order.order_no,
									"Status":"AUTHORISED",
									"LineItems":LineItems
								}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()
				
				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None
				
				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
			
			if payment_policy == 'POSTPAID':
				BankCharge = .250
				Amount     = float(order.evaluation.total_cost) 
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				LineItems.append({
					"Description":"BANK CHARGE",
					"Quantity":"1",
					"UnitAmount":-BankCharge,
					"AccountCode":3202014,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no

				invoice_data        = 	{
									"Type":"ACCREC",
									"LineAmountTypes":"NoTax",
									"InvoiceNumber":InvoiceNumber,
									"Reference":order.order_no,
									"Status":"AUTHORISED",
									"LineItems":LineItems
								}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()
				
				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None
				
				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
				
				#Delete Unwanted invoice
				InvoiceNumber  = order.invoice_no+'A'

				invoice_data        = 	{
									"Type":"ACCREC",
									"LineAmountTypes":"NoTax",
									"InvoiceNumber":InvoiceNumber,
									"Reference":order.order_no,
									"Status":"DELETED"
								}
				##xero Delete Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				delete_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()

			if payment_policy == 'SUBSCRIPTION':
				try:
					xero_invoice  = XeroInvoice.objects.filter(order=order,payment_policy=payment_policy,is_paid=False).last()
				except:
					xero_invoice  = None
				
				if xero_invoice:
					BankCharge = .250
					Amount     = float(order.subscription_topay) 
					##Invoice Line Item 
					LineItems                 = []
					LineItems.append({
						"Description":"ONE TIME SERVICE",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1207004,
						"TaxType":"NONE"
									}
						)
					LineItems.append({
						"Description":"BANK CHARGE",
						"Quantity":"1",
						"UnitAmount":-BankCharge,
						"AccountCode":3202014,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber       = xero_invoice.invoice_no

					invoice_data        = 	{
										"Type":"ACCREC",
										"LineAmountTypes":"NoTax",
										"InvoiceNumber":InvoiceNumber,
										"Reference":order.order_no,
										"Status":"AUTHORISED",
										"LineItems":LineItems
									}

					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
					
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
				
				
			#Payment Add 
			payment_date        = timezone.now().date()
			payment_date_string = datetime.strftime(payment_date,'%Y-%m-%d')

			if payment_policy == 'PREPAID' or payment_policy == 'POSTPAID' or payment_policy == 'BEFORE CLEANING' or payment_policy == 'AFTER CLEANING':
				
				try:
					xero_invoice = XeroInvoice.objects.get(order=order,payment_policy=payment_policy)
				except:
					xero_invoice = None

				if xero_invoice:
					bank_charge  = .250

					#Payment Update
					payment_data = {
								"Invoice":{
									"InvoiceNumber":xero_invoice.invoice_no
								},
								"Account":{
									"Code":"1201023"
								},
								"Date":payment_date_string,
								"Amount":float(amount_paid)-bank_charge,
								"Reference":payment_history.transaction_id
								}

					update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
														json=payment_data,
														headers=header 
													).json()


					try:
						created_payment = update_payment['Status']
					except:
						created_payment = None

					if created_payment == 'OK':
						xero_invoice.is_paid   = True
						xero_invoice.paid_date = payment_date
						xero_invoice.save()

						payment_history.is_xero_marked = True
						payment_history.save()

			if payment_policy == 'SUBSCRIPTION':
				try:
					xero_invoice = XeroInvoice.objects.filter(order=order,payment_policy=payment_policy,is_paid=False).last()
				except:
					xero_invoice = None

				if xero_invoice:
					bank_charge  = .250
					
					#Payment Update
					payment_data = {
								"Invoice":{
									"InvoiceNumber":xero_invoice.invoice_no
								},
								"Account":{
									"Code":"1201023"
								},
								"Date":payment_date_string,
								"Amount":float(amount_paid)-bank_charge,
								"Reference":payment_history.transaction_id
								}

					update_payment          = requests.put('https://api.xero.com/api.xro/2.0/Payments',
														json=payment_data,
														headers=header 
													).json()

					try:
						created_payment = update_payment['Status']
					except:
						created_payment = None

					if created_payment == 'OK':
						xero_invoice.is_paid   = True
						xero_invoice.paid_date = payment_date
						xero_invoice.save()
						
						payment_history.is_xero_marked = True
						payment_history.save()

				########################################################################################

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
			order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,order_no=evaluation_id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(Q( Q(cleaning_count=F('completed_cleaning_count')) & Q(followup_count=F('completed_followup_count')) & ~Q(cleaning_count=0) ) )
			if order_closing_check:
				closing_order	= Order.objects.get(is_active=True,order_no=evaluation_id)
				closing_order.order_status = 'ORDER_CLOSED'
				closing_order.save()

			if order_status == 'CUSTOMER_BOOKING' :
				#customer booking temp data clearing
				customer_cart = CustomerCart.objects.prefetch_related(Prefetch('cart_service',queryset=CartService.objects.filter(is_active=True).prefetch_related(Prefetch('cart_service_floor',queryset=CartServiceFloor.objects.all(),to_attr='cart_service_floors')),to_attr='cart_services'),Prefetch('cart_schedule',queryset=CartSchedule.objects.filter(is_active=True),to_attr='cart_schedules')).get(id=evaluation_id_encrypted)
				for cart_service in customer_cart.cart_services:
					if cart_service.cart_service_floors:
						for floor in cart_service.cart_service_floors:
							floor.delete()

					cart_service.delete()	

				for cart_schedule in customer_cart.cart_schedules:
					cart_schedule.delete()

				customer_cart.is_scheduled = False
				customer_cart.total_cost = 0
				customer_cart.cart_discount = 0
				customer_cart.promocode = None
				customer_cart.promocode_amount = 0
				customer_cart.final_cost = 0
				customer_cart.save()

			#pay and book &&& others
			# pay_and_book = request.POST.get('udf4')
			# if pay_and_book:
			if order_status == 'CUSTOMER_BOOKING':
				# return redirect('http://testwww.bleach-kw.com:8080/my/orders')
				return redirect('https://www.bleach-kw.com/my/orders')
				# return(pay_and_book)
			else:
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

			if order_status == 'CUSTOMER_BOOKING' :
				#customer booking temp data clearing
				customer_cart = CustomerCart.objects.prefetch_related(Prefetch('cart_service',queryset=CartService.objects.filter(is_active=True).prefetch_related(Prefetch('cart_service_floor',queryset=CartServiceFloor.objects.all(),to_attr='cart_service_floors')),to_attr='cart_services'),Prefetch('cart_schedule',queryset=CartSchedule.objects.filter(is_active=True),to_attr='cart_schedules')).get(id=evaluation_id_encrypted)
				for cart_service in customer_cart.cart_services:
					if cart_service.cart_service_floors:
						for floor in cart_service.cart_service_floors:
							floor.delete()
							
					cart_service.delete()	

				for cart_schedule in customer_cart.cart_schedules:
					cart_schedule.delete()

				customer_cart.is_scheduled = False
				customer_cart.total_cost = 0
				customer_cart.cart_discount = 0
				customer_cart.promocode = None
				customer_cart.promocode_amount = 0
				customer_cart.final_cost = 0
				customer_cart.save()
			
			#pay and book &&& others
			# pay_and_book = request.POST.get('udf4')
			# if pay_and_book:
			if order_status == 'CUSTOMER_BOOKING':
				# return redirect('http://testwww.bleach-kw.com:8080/my/orders')
				return redirect('https://www.bleach-kw.com/my/orders')
			else:
				return redirect('customer:payment-receipt','pvw'+str(evaluation_id_encrypted[0:11])+str(payment_history.id))

		#promocode applied and the entire order cost is covered. so the final amount is 0
		elif order and order_status == 'CUSTOMER_BOOKING' and payment_result == 'ZEROPAYMENT':
			#customer booking temp data clearing
			customer_cart = CustomerCart.objects.prefetch_related(Prefetch('cart_service',queryset=CartService.objects.filter(is_active=True).prefetch_related(Prefetch('cart_service_floor',queryset=CartServiceFloor.objects.all(),to_attr='cart_service_floors')),to_attr='cart_services'),Prefetch('cart_schedule',queryset=CartSchedule.objects.filter(is_active=True),to_attr='cart_schedules')).get(id=evaluation_id_encrypted)
			for cart_service in customer_cart.cart_services:
				if cart_service.cart_service_floors:
					for floor in cart_service.cart_service_floors:
						floor.delete()
						
				cart_service.delete()	

			for cart_schedule in customer_cart.cart_schedules:
				cart_schedule.delete()

			customer_cart.is_scheduled = False
			customer_cart.total_cost = 0
			customer_cart.cart_discount = 0
			customer_cart.promocode = None
			customer_cart.promocode_amount = 0
			customer_cart.final_cost = 0
			customer_cart.save()

			# return redirect('http://testwww.bleach-kw.com:8080/my/orders')
			return redirect('https://www.bleach-kw.com/my/orders')

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

			return redirect('/customer/payment/failed/?udf1='+order.order_no[3:]+''+order.evaluation.customer.username+'&paymentid='+request.GET.get('paymentid')+'&ref='+request.GET.get('ref'))


class PaymentFailedResponse(View):
	def get(self,request):

		payment_id   = request.GET.get('paymentid')
		reference_id = request.GET.get('ref')

		evaluation_id_encrypted = request.GET.get("udf1")

		#for back to invoice
		order = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate'),to_attr='orderschedules')).get(order_no='BLC'+evaluation_id_encrypted[0:11])
	
		try:
			customer_booking = CustomerBooking.objects.get(evaluation=order.evaluation,is_active=True,booking_type='CLEANINGBOOKING')
		except:
			customer_booking = None

		if customer_booking:
			# return redirect('http://testwww.bleach-kw.com:8080/cart')
			return redirect('https://www.bleach-kw.com/cart')
		else:
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
		
		if payment_history.order.orderschedules:
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
	
	order 			= Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='booksections')),to_attr='evaluationbooks')),to_attr='evaluationdetails')).get(is_active=True,order_no=evaluation_id,evaluation__customer__username=user_name)
	price_ranges 	= ServicePriceRange.objects.filter(is_active=True)	
	html_string = render_to_string("customer/downloads/quatation.html",{"order":order,"price_ranges":price_ranges})

	html     = HTML(string=html_string,base_url=request.build_absolute_uri())
	main_doc = html.render()

	main_doc.write_pdf(target='/home/pdf/tmp/quatation/quatation.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/quatation/')
	with fs.open('quatation.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+evaluation_id+'_quatation.pdf"'
		return response
	return response


def purchaseorder_html_to_pdf_view(request,purchase_order_id):

	purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.select_related('product').all(),to_attr='purchase_order_items')).get(id=int(purchase_order_id))
	
	items_total_price = 0

	for item in purchase_order.purchase_order_items:
		items_total_price += float(item.total_price)

	items_final_price = float(items_total_price)+float(purchase_order.tax)+float(purchase_order.shipping_charge)+float(purchase_order.other_charge)-float(purchase_order.discount)

	html_string = render_to_string('customer/downloads/purchaseorderpage.html',{"purchase_order":purchase_order,"items_total_price":items_total_price,"items_final_price":items_final_price})
	
	html     = HTML(string=html_string,base_url=request.build_absolute_uri())
	main_doc = html.render()

	main_doc.write_pdf(target='/home/pdf/tmp/purchaseorder/purchaseorder.pdf');
	fs=FileSystemStorage('/home/pdf/tmp/purchaseorder/')
	
	with fs.open('purchaseorder.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+purchase_order.purchase_order_id+'_purchaseorder.pdf"'
		return response
	return response

def requestorder_html_to_pdf_view(request,request_order_id):
	request_order = RequestOrder.objects.prefetch_related(Prefetch('items_request_order',queryset=RequestOrderItems.objects.all(),to_attr='request_order_items')).get(id=request_order_id)

	html_string = render_to_string('customer/downloads/requestorderpage.html',{"request_order":request_order})
	
	html     = HTML(string=html_string,base_url=request.build_absolute_uri())
	main_doc = html.render()

	main_doc.write_pdf(target='/home/pdf/tmp/requestorder/requestorder.pdf');
	fs=FileSystemStorage('/home/pdf/tmp/requestorder/')
	
	with fs.open('requestorder.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+request_order.request_order_id+'_requestorder.pdf"'
		return response
	return response

def stockout(request,visit_id):
	visit = OrderScheduler.objects.select_related('order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='team_members')),to_attr='cleaning_team')).get(id=int(visit_id))
	check_out_items = CheckOutItems.objects.filter(visit=visit)
	html_string = render_to_string("customer/downloads/stock-out-sheet.html",{"visit":visit,"check_out_items":check_out_items})

	html = HTML(string=html_string,base_url=request.build_absolute_uri())
	html.write_pdf(target='/home/pdf/tmp/stockout/stockout.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/stockout/')
	with fs.open('stockout.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+visit.order.order_no+'_'+str(visit.start_at)+'_stockout.pdf"'
		return response
	return response
	# return render(request,"customer/downloads/stock-out-sheet.html",{"visit":visit,"check_out_items":check_out_items})


def orderdetail_html_to_pdf_view(request,order_id,service_id,section_id):

	order           = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True).select_related('evaluation_details','order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationbookmedia',queryset=EvaluationMedia.objects.filter(is_active=True),to_attr='evaluationmedia'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes')),to_attr='evaluationbooksection'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True,member__user_type='CLEANER'),to_attr='cleaning_team_members')),to_attr='cleaning_team'),Prefetch('investigations_orderschedule',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True),to_attr='investigationmedias'),Prefetch('followup_investigation',queryset = FollowUp.objects.filter(is_active=True).prefetch_related(Prefetch('follow_up_of_scheduler',queryset=FollowUpScheduler.objects.filter(is_active=True).prefetch_related(Prefetch('followupteam_followupschedule',queryset=FollowUpTeam.objects.filter(is_active=True).prefetch_related(Prefetch('followup_member_team',queryset=FollowUpTeamMember.objects.filter(is_active=True),to_attr='followupmembers')),to_attr='followupteams')),to_attr='follow_up_schedules')),to_attr='followups')),to_attr='investigations')),to_attr='orderschedules'),Prefetch('feed_backs_order',FeedBack.objects.filter(is_active=True).select_related('question'),to_attr='feedbacks')).get(is_active=True,id=order_id)
	
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

	order           = Order.objects.select_related('evaluation__customer').prefetch_related(Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='booksections')),to_attr='evaluationbooks')),to_attr='evaluationdetails')).get(is_active=True,order_no=evaluation_id,evaluation__customer__username=user_name)
	price_ranges 	= ServicePriceRange.objects.filter(is_active=True)
	html_string = render_to_string("customer/downloads/invoice.html",{'order':order,'price_ranges':price_ranges})

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
	
	html_string = render_to_string('customer/downloads/receipt-voucher.html', {'payment_history':payment_history,'nonduplicate_schedules':nonduplicate_schedules,})

	html = HTML(string=html_string,base_url=request.build_absolute_uri())
	html.write_pdf(target='/home/pdf/tmp/receipt/receipt.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/receipt/')
	with fs.open('receipt.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+payment_history.order.order_no+'_receipt.pdf"'
		return response
	return response	

def customer_booking_html_to_pdf_view(request,booking_id):

	try:
		customer_booking = CustomerBooking.objects.get(booking_id=booking_id)
		evaluation_details = EvaluationDetails.objects.filter(evaluation=customer_booking.evaluation).first()
		evaluation_end_time = evaluation_details.proposed_time + timedelta(hours=1)
	except:
		customer_booking = None
		evaluation_details = None
		evaluation_end_time = None
	
	html_string = render_to_string("customer/downloads/customer_booking_receipt.html",{"booking":customer_booking,"evaluation_details":evaluation_details,"evaluation_end_time":evaluation_end_time})

	html     = HTML(string=html_string,base_url=request.build_absolute_uri())
	main_doc = html.render()

	main_doc.write_pdf(target='/home/pdf/tmp/customer_booking/customer_evaluation_booking_receipt.pdf');

	fs = FileSystemStorage('/home/pdf/tmp/customer_booking/')
	with fs.open('customer_evaluation_booking_receipt.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+booking_id+'_quatation.pdf"'
		return response
	return response

def soa_calculate(n,collection):
    collection_sum = sum(collection)
    result           = [int(n/collection_sum*i) for i in collection]
    result_sum       = sum(result)
    result[-1]      += round((n-result_sum),3)
    return(result)

def statement_of_account(request,client_id):

	# if request.method == 'POST':
	# 	start_date = request.POST.get('start_date')
	# 	end_date = request.POST.get('end_date')

	# 	list_data_check = request.POST.get('list_data_check')
	# 	print(list_data_check,"ch")

	# 	if start_date and end_date:
	# 		start_date = datetime.strptime(start_date,'%Y-%m-%d')
	# 		end_date = datetime.strptime(end_date,'%Y-%m-%d')

	# 		start_date = start_date.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
	# 		end_date = end_date+timedelta(1)

	# print(start_date,end_date,"mlpp")
	customer = UserProfile.objects.get(is_active=True,id=int(client_id))
	address = Address.objects.filter(customer__id=int(client_id)).first()

	
	# opening balance calc
	opening_balance_customer_orders = Order.objects.filter(is_active=True).order_by('evaluation__quatation_approved_date').filter(evaluation__customer__id=int(client_id),evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='evaluationdetails'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
	
	opening_debit = 0
	opening_credit = 0 
	opening_balance = 0

	for order in opening_balance_customer_orders:
		if order.evaluation.payment_method != 'SUBSCRIPTION' and order.completed_cleaning_count >= 1 :
			opening_credit += float(order.total_amount)

			for payment in order.paymenthistory:
				opening_debit += float(payment.amount_paid)

		elif order.evaluation.payment_method == 'SUBSCRIPTION' and order.order_status == 'ORDER_IN_PROGRESS' or order.order_status == 'ORDER_CLOSED':

			evaluationbooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation__id=order.evaluation.id)
			evaluationbooks_count = evaluationbooks.count()

			job_completed = 0
			job_remaining = 0

			for book in evaluationbooks:
				cleanings_count = OrderScheduler.objects.filter(is_active=True,order__id=order.id,order_scheduler_book__id=book.id).count()
				if cleanings_count > 0:
					completed_cleanings = OrderScheduler.objects.filter(is_active=True,order__id=order.id,order_scheduler_book__id=book.id,work_status='CLEANING_FULFILLED')
					completed_cleanings_count = completed_cleanings.count()
					print(cleanings_count,order.order_status,"moppp")
					total_cost = book.total_cost

					per_cleaning_amount = float(book.total_cost/cleanings_count)
					job_completed += float(per_cleaning_amount*completed_cleanings_count)
					# job_remaining += float(book.total_cost - job_completed)	

					if order.evaluation.fine_amount:
						job_completed += float(order.evaluation.fine_amount/cleanings_count)

					if order.evaluation.writeback_amount:
						job_completed -= float(order.evaluation.writeback_amount/cleanings_count)

					if order.evaluation.promocode_amount:
						job_completed -= float(order.evaluation.promocode_amount/cleanings_count)

					if order.evaluation.additional_charge:
						job_completed += float(order.evaluation.additional_charge/cleanings_count)

					if order.evaluation.discount:
						job_completed -= float(order.evaluation.discount/cleanings_count)

			opening_credit += float(job_completed)

			for payment in order.paymenthistory:
				opening_debit += float(payment.amount_paid)

		else:
			pass
	
	
	# soa date range
	# if list_data_check == 'on':
	customer_orders = Order.objects.filter(is_active=True).order_by('evaluation__quatation_approved_date').filter(evaluation__customer__id=int(client_id),evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='evaluationdetails'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
	# else:
	# 	customer_orders = Order.objects.filter(is_active=True,created__range=(start_date,end_date)).order_by('evaluation__quatation_approved_date').filter(evaluation__customer__id=int(client_id),evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True,created__range=(start_date,end_date)),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='evaluationdetails'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))

	accounts_list = []

	debit = 0
	credit = 0 
	balance = 0
		
	for order in customer_orders:
		# if order.evaluation.payment_method != 'SUBSCRIPTION' and order.order_status == 'ORDER_CLOSED':
		if order.evaluation.payment_method != 'SUBSCRIPTION' and order.completed_cleaning_count >= 1 :
			accounts_list.append({
						"date":order.created.date(),
						"invoice_no":order.order_no,
						"details":"Cleaning Services",
						"amount":order.total_amount,
						"credit":order.total_amount,
						"debit":""
					})
			credit += float(order.total_amount)
			
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
							"date":payment.paid_date.date(),
							"invoice_no":payment.payment_mode,
							"details":details,
							"amount":"",
							"credit":"",
							"debit":payment.amount_paid
						})
					debit += float(payment.amount_paid)

		elif order.evaluation.payment_method == 'SUBSCRIPTION' and order.order_status == 'ORDER_IN_PROGRESS' or order.order_status == 'ORDER_CLOSED':
			
			evaluationbooks = EvaluationBook.objects.filter(is_active=True,evaluation_details__evaluation__id=order.evaluation.id)
			evaluationbooks_count = evaluationbooks.count()

			job_completed = 0
			job_remaining = 0

			# miscellaneous amouunt calc
			if order.evaluation.fine_amount:
				fine_amount = order.evaluation.fine_amount
			else:
				fine_amount = 0
				# job_completed += float(order.evaluation.fine_amount/cleanings_count)

			if order.evaluation.writeback_amount:
				writeback_amount = order.evaluation.writeback_amount
				# job_completed -= float(order.evaluation.writeback_amount/cleanings_count)
			else:
				writeback_amount = 0

			if order.evaluation.promocode_amount:
				promocode_amount = order.evaluation.promocode_amount
				# job_completed -= float(order.evaluation.promocode_amount/cleanings_count)
			else:
				promocode_amount = 0

			if order.evaluation.additional_charge:
				additional_charge = order.evaluation.additional_charge
				# job_completed += float(order.evaluation.additional_charge/cleanings_count)
			else:
				additional_charge = 0

			if order.evaluation.discount:
				discount = order.evaluation.discount
				# job_completed += float(order.evaluation.additional_charge/cleanings_count)
			else:
				discount = 0

			if order.evaluation.cancelled_amount:
				cancelled_amount = order.evaluation.cancelled_amount
				# job_completed -= float(order.evaluation.discount/cleanings_count)
			else:
				cancelled_amount = 0
			
			order_miscellaneous_amount = float(fine_amount)+float(additional_charge)-float(writeback_amount)-float(promocode_amount)-float(cancelled_amount)-float(discount)

			book_amounts = []

			#book amount list
			bookcount = 0
			for book in evaluationbooks:
				book_amounts.append(book.total_cost)
				print(book.total_cost,book_amounts,"rarr")

			#misc amount split for books
			divided_amounts = soa_calculate(order_miscellaneous_amount,book_amounts)

			#final book amount calc
			for book in evaluationbooks:
				cleanings_count = OrderScheduler.objects.filter(is_active=True,order__id=order.id,order_scheduler_book__id=book.id).exclude(work_status='CLEANING_CANCELLED').count()
				if cleanings_count > 0:
					completed_cleanings = OrderScheduler.objects.filter(is_active=True,order__id=order.id,order_scheduler_book__id=book.id,work_status='CLEANING_FULFILLED')
					completed_cleanings_count = completed_cleanings.count()
					print(completed_cleanings_count,cleanings_count,"moppperrr")
					# cleaning_ratio = int(completed_cleanings_count / cleanings_count)
					
					# cleaning_ratios.append(cleaning_ratio)

					# print(cleanings_count,order.order_status,cleaning_ratio,"mopppyy")
					# total_cost = book.total_cost
					

					# per_cleaning_amount = float(book.total_cost/cleanings_count)
					# job_completed += float(per_cleaning_amount*completed_cleanings_count)
					# job_remaining += float(book.total_cost - job_completed)	

				
					print(book_amounts[bookcount],divided_amounts[bookcount],"roomer")
					book_amounts[bookcount] = ((book_amounts[bookcount] + divided_amounts[bookcount]) * completed_cleanings_count) / cleanings_count

				bookcount += 1 

			print(book_amounts,"amts")

			for i in range(0,len(book_amounts)):
				job_completed += book_amounts[i]

			accounts_list.append({
						"date":order.created.date(),
						"invoice_no":order.order_no,
						"details":"Cleaning Services",
						"amount":order.total_amount,
						"credit":job_completed,
						"debit":""
					})
			credit += float(job_completed)

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
							"date":payment.paid_date.date(),
							"invoice_no":payment.payment_mode,
							"details":details,
							"amount":"",
							"credit":"",
							"debit":payment.amount_paid
						})
				debit += float(payment.amount_paid)
		else:
			pass

	print(balance,opening_credit,opening_debit,"belenc")
	balance = credit - debit
	opening_balance = float(opening_credit - opening_debit) - float(balance)
	
	
	return render(request,"customer/soa_test.html",{"customer":customer,"address":address,"orders":accounts_list,"opening_balance":opening_balance,"opening_credit":opening_credit,"opening_debit":opening_debit})

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
				
				#if after coupon apply amount is 0 or less, Subscription,Prepaid,Postpaid
				if discount_amount <= 0 and evaluation.payment_method != 'BREAKDOWN':

					evaluation.total_cost = 0.000
					evaluation.is_promocode_applied = True
					evaluation.promocode_amount = order.total_amount
					evaluation.save()

					promocode_amount = 0.000
					discount_amount = 0.000

					order.total_amount       = 0.000
					order.remining_amount    = 0.000
					order.payment_status     = 'COMPLETED'
					order.subscription_topay =0.000
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
								order.total_amount               = evaluation.before_cleaning_amount
								order.remining_amount            = 0.000
								order.payment_status             = 'COMPLETED'
								order.save()

								evaluation.total_cost            = evaluation.before_cleaning_amount
								evaluation.promocode_amount      = evaluation.after_cleaning_amount
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
						order.total_amount    = discount_amount
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

				#Xero Integration
				xero                        = XeroConnection.objects.first()
				##xero Update Access Token and Refresh Token
				header                      = {
												'Authorization': 'Basic '+xero.client_encoded,
												'Content-Type': 'application/x-www-form-urlencoded'
													}
				body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
				token_response              = requests.post('https://identity.xero.com/connect/token',
														data=body,
														headers=header 
													).json()
				access_token                = token_response['access_token']
				refresh_token               = token_response['refresh_token']

				xero.access_token  = access_token
				xero.refresh_token = refresh_token
				xero.save()

				if evaluation.payment_method == 'PREPAID' or evaluation.payment_method == 'POSTPAID':
					if evaluation.payment_method == 'PREPAID':
						Amount = order.evaluation.total_cost 
						##Invoice Line Item 
						LineItems                 = []
						LineItems.append({
							"Description":"ONE TIME SERVICE",
							"Quantity":"1",
							"UnitAmount":Amount,
							"AccountCode":1207004,
							"TaxType":"NONE"
										}
							)
						InvoiceNumber  = order.invoice_no
						payment_policy = 'PREPAID'

						
					if evaluation.payment_method == 'POSTPAID':
						Amount = order.evaluation.total_cost 
						##Invoice Line Item 
						LineItems                 = []
						LineItems.append({
							"Description":"ONE TIME SERVICE",
							"Quantity":"1",
							"UnitAmount":Amount,
							"AccountCode":1207004,
							"TaxType":"NONE"
										}
							)
						InvoiceNumber  = order.invoice_no
						payment_policy = 'POSTPAID'

					invoice_data        = 	{
										"Type":"ACCREC",
										"LineAmountTypes":"NoTax",
										"InvoiceNumber":InvoiceNumber,
										"Reference":order.order_no,
										"Status":"SUBMITTED",
										"LineItems":LineItems
									}
					
					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

				if evaluation.payment_method == 'BREAKDOWN':
					#Before Invoice
					Amount = order.evaluation.before_cleaning_amount
					##Invoice Line Item 
					LineItems                 = []
					LineItems.append({
						"Description":"ONE TIME SERVICE",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1207004,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber  = order.invoice_no+'A'
					payment_policy = 'BEFORE CLEANING'


					invoice_data        = 	{
										"Type":"ACCREC",
										"LineAmountTypes":"NoTax",
										"InvoiceNumber":InvoiceNumber,
										"Reference":order.order_no,
										"Status":"SUBMITTED",
										"LineItems":LineItems
									}

					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

					#After Invoice
					Amount = order.evaluation.after_cleaning_amount
					##Invoice Line Item 
					LineItems                 = []
					LineItems.append({
						"Description":"ONE TIME SERVICE",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1207004,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber  = order.invoice_no+'B'
					payment_policy = 'AFTER CLEANING'

					invoice_data        = 	{
										"Type":"ACCREC",
										"LineAmountTypes":"NoTax",
										"InvoiceNumber":InvoiceNumber,
										"Reference":order.order_no,
										"Status":"AUTHORISED",
										"LineItems":LineItems
									}

					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
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
				elif service_price_range.upholstery_type == 'CURTAIN':
					service_price_range_dict['unit_price'] = service_price_range.unit_price
				else:
					pass
			elif service_price_range.service_type.name == 'Window Cleaning':
				service_price_range_dict['is_highprice_window'] = service_price_range.is_highprice_window
			elif service_price_range.service_type.name == 'Facade Cleaning':
				service_price_range_dict['is_highprice_facade'] = service_price_range.is_highprice_facade 
			elif service_price_range.service_type.name == 'Kitchen Cleaning':
				service_price_range_dict['is_newkitchen']       = service_price_range.is_newkitchen
				service_price_range_dict['is_cabinet']          = service_price_range.is_cabinet

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
				service_productivity['max_hours'] 		 = serviceproductivity.max_hours
				service_productivity['min_hours'] 		 = serviceproductivity.min_hours
				service_productivity['min_cleaners']     = serviceproductivity.min_cleaners
				service_productivity['max_cleaners']     = serviceproductivity.max_cleaners

		
		elif service_type         == 'Window Cleaning':
			serviceproductivities = ServiceProductivity.objects.select_related('service_type').filter(service_type__name=service_type)
			for serviceproductivity in serviceproductivities:
				if serviceproductivity.is_highprice_window:
					service_productivity['highpricewindow_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				else:
					service_productivity['lowpricewindow_perhour_cleaning']  = serviceproductivity.perhour_cleaning
				service_productivity['max_hours'] 		 = serviceproductivity.max_hours
				service_productivity['min_hours'] 		 = serviceproductivity.min_hours
				service_productivity['min_cleaners']     = serviceproductivity.min_cleaners
				service_productivity['max_cleaners']     = serviceproductivity.max_cleaners
		
		elif service_type         == 'Facade Cleaning':
			serviceproductivities = ServiceProductivity.objects.select_related('service_type').filter(service_type__name=service_type)
			for serviceproductivity in serviceproductivities:
				if serviceproductivity.is_highprice_facade:
					service_productivity['highpricefacade_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				else:
					service_productivity['lowpricefacade_perhour_cleaning']  = serviceproductivity.perhour_cleaning
				service_productivity['max_hours'] 		 = serviceproductivity.max_hours
				service_productivity['min_hours'] 		 = serviceproductivity.min_hours
				service_productivity['min_cleaners']     = serviceproductivity.min_cleaners
				service_productivity['max_cleaners']     = serviceproductivity.max_cleaners
		
		elif service_type         == 'Kitchen Cleaning':
			serviceproductivities = ServiceProductivity.objects.select_related('service_type').filter(service_type__name=service_type)
			for serviceproductivity in serviceproductivities:
				if serviceproductivity.is_newkitchen and not serviceproductivity.is_cabinet:
					service_productivity['newkitchenwithout_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				elif not serviceproductivity.is_newkitchen and not serviceproductivity.is_cabinet:
					service_productivity['oldkitchenwithoutcabinet_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				elif serviceproductivity.is_newkitchen and serviceproductivity.is_cabinet:
					service_productivity['newkitchenwithcabinet_perhour_cleaning'] = serviceproductivity.perhour_cleaning
				elif not serviceproductivity.is_newkitchen and serviceproductivity.is_cabinet:
					service_productivity['oldkitchenwithcabinet_perhour_cleaning'] = serviceproductivity.perhour_cleaning	
				
				service_productivity['max_hours'] 		 = serviceproductivity.max_hours
				service_productivity['min_hours'] 		 = serviceproductivity.min_hours
				service_productivity['min_cleaners']     = serviceproductivity.min_cleaners
				service_productivity['max_cleaners']     = serviceproductivity.max_cleaners

		elif service_type         == 'Kitchen Appliances':
			
			addon_name         = request.GET.get('addon_name')
			addon_category     = request.GET.get('addon_category',None)
			if addon_category == 'null':
				addon_category     = None

			service_addon       = ServiceAddOns.objects.get(service_type__name='Kitchen Cleaning',name__iexact=addon_name,category__iexact=addon_category)
			
			service_productivity[''+service_addon.name+''] = service_addon.productivity
			service_productivity['addon_category'] = service_addon.category
			service_productivity['max_hours'] 		 = 8
			service_productivity['min_hours'] 		 = 2
			service_productivity['min_cleaners']     = 1
			service_productivity['max_cleaners']     = 10
		else:
			serviceproductivity = ServiceProductivity.objects.select_related('service_type').get(service_type__name=service_type)
			service_productivity['perhour_cleaning'] = serviceproductivity.perhour_cleaning
			service_productivity['max_hours'] 		 = serviceproductivity.max_hours
			service_productivity['min_hours'] 		 = serviceproductivity.min_hours
			service_productivity['min_cleaners']     = serviceproductivity.min_cleaners
			service_productivity['max_cleaners']     = serviceproductivity.max_cleaners

		return JsonResponse(service_productivity)



class GetServiceAddOns(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict        = {}
		service_type         = request.GET.get('service_type')

		service_addons       = ServiceAddOns.objects.select_related('service_type').filter(service_type__name=service_type)

		print(service_addons)
		response_dict['service_addons'] = ServiceAddOnsSerializer(instance=service_addons,many=True).data
		response_dict['success']        = True

		return Response(response_dict,HTTP_200_OK)



class GetMultipleServiceCleaningSlotes(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		dropdown_slotes  = {}

		cleaning_date       = datetime.strptime(request.data.get('cleaning_date'),'%d-%m-%Y')
		number_of_cleaners  = int(request.data.get('number_of_cleaners'))-1
		service_types       = request.data.get('service_types')
		gender              = request.data.get('gender')

		#count total cleaners and total leaders
		if gender:
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE'))&Q(gender=gender))
			total_leaders  = UserProfile.objects.filter(user_type='TEAMINCHARGE',gender=gender)
		else:
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
			elif service_type == 'Kitchen Appliances':
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
		if gender:
			absent_cleaners   = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))&Q(staff__gender=gender)).values_list('staff',flat=True)
			absent_leaders    = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date,staff__user_type='TEAMINCHARGE',staff__gender=gender).values_list('staff',flat=True)	
		else:
			absent_cleaners   = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
			absent_leaders    = LeaveSchedule.objects.select_related('staff').filter(leave_date=cleaning_date,staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

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
				if gender:
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(shift_date=cleaning_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))&Q(staff__gender=gender)).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(shift_date=cleaning_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime))).filter(staff__user_type='TEAMINCHARGE',staff__gender=gender).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(is_active=True,staff__gender=gender).filter(Q(shift_date=cleaning_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE'))&Q(gender=gender))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',gender=gender).exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)
				else:
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(shift_date=cleaning_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(shift_date=cleaning_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(shift_date=cleaning_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)

		
				#(applying 8 to 22 leave logic)
				leavestart_at_datetime1  = slote_start_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime1    = slote_start_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
				leavestart_at_datetime2  = slote_end_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime2    = slote_end_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
		
				if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
					total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners)
					total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))).exclude(id__in=absent_leaders)
				else:
					total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))		

				new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
				new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))

				if gender:				
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__gender=gender).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__gender=gender).filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				else:
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))

				for service_type in service_types:
					
					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Kitchen Appliances':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
						new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

				new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
				new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)
				
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

				#(applying 8 to 22 leave logic)
				if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
					for absent_cleaner in new_absent_cleaners:
						team_members_scheduled.append(absent_cleaner)
					for absent_leader in new_absent_leaders:
						team_leaders_scheduled.append(absent_leader)					

				total_newcleaners = total_newcleaners.exclude(id__in=team_members_scheduled)
				total_newleaders = total_newleaders.exclude(id__in=team_leaders_scheduled)

				#slote appending
				if total_newcleaners and total_newleaders:
					if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
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
			elif service_type == 'Kitchen Appliances':
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
		combined_slots   = []

		#Test on multiple date
		shift_availability_check = request.data.get('shift_availability_check') 
		policy = request.data.get('policy') 
		cleaning_datetimes       = request.data.get('cleaning_datetimes')
		
		for cleaning_datetime in cleaning_datetimes:
			team_leaders_scheduled      = []
			team_members_scheduled      = []

			if policy == 'onetime':
				slote_start_datetime 			  = datetime.strptime(cleaning_datetime[0]+' '+cleaning_datetime[1],'%d-%m-%Y %I:%M %p')
				slote_end_datetime                = datetime.strptime(cleaning_datetime[0]+' '+cleaning_datetime[2],'%d-%m-%Y %I:%M %p')
				slote_start_time 			      = slote_start_datetime.time()
				slote_end_time                    = slote_end_datetime.time()
				start_at_date                     = slote_start_datetime.date()
				end_at_date                       = slote_end_datetime.date()
			else:
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
			if shift_availability_check:
				shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
				shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
				today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
				super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
				super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)

				#(applying 8 to 22 leave logic)
				leavestart_at_datetime1  = slote_start_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime1    = slote_start_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
				leavestart_at_datetime2  = slote_end_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime2    = slote_end_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
		
				if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
					total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners)
					total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))).exclude(id__in=absent_leaders)
				else:
					total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))

				active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))

				new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
				new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))	
			
			#excluded shift cleaners
			else:
				#(applying 8 to 22 leave logic)
				leavestart_at_datetime1  = slote_start_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime1    = slote_start_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
				leavestart_at_datetime2  = slote_end_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime2    = slote_end_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
		
				if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
					total_newcleaners = total_cleaners.exclude(id__in=absent_cleaners)
					total_newleaders  = total_leaders.exclude(id__in=absent_leaders)
				else:
					total_newcleaners = total_cleaners
					total_newleaders  = total_leaders

				active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
				active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))

				new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners)
				new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders)

			for service_type in service_types:					
				if service_type == 'General Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
				elif service_type == 'Kitchen Appliances':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
				elif service_type == 'Sterilization':
					active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
				elif service_type == 'Storage Area':
					active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
					new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
					new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

				new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
				new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)

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

			#(8 to 22 leave logic applied)
			if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
				for absent_cleaner in new_absent_cleaners:
					team_members_scheduled.append(absent_cleaner)
				for absent_leader in new_absent_leaders:
					team_leaders_scheduled.append(absent_leader)

			total_newcleaners = total_newcleaners.exclude(id__in=team_members_scheduled)
			total_newleaders = total_newleaders.exclude(id__in=team_leaders_scheduled)

			#slote availability				
			if total_newcleaners and total_newleaders:
					if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
						available_slotes.append(datetime.strftime(slote_start_datetime,'%d-%m-%Y %I:%M %p'))	

						combined_slots_dict = {
							"date" : datetime.strftime(slote_start_datetime,'%d-%m-%Y'),
							"time" : datetime.strftime(slote_start_datetime,'%I:%M %p'),
							"is_available" : True
						}

						combined_slots.append(combined_slots_dict)

					else:
						busy_slotes.append(datetime.strftime(slote_start_datetime,'%d-%m-%Y %I:%M %p'))

						combined_slots_dict = {
							"date" : datetime.strftime(slote_start_datetime,'%d-%m-%Y'),
							"time" : datetime.strftime(slote_start_datetime,'%I:%M %p'),
							"is_available" : False
						}
						
						combined_slots.append(combined_slots_dict)
					
			else:
				busy_slotes.append(datetime.strftime(slote_start_datetime,'%d-%m-%Y %I:%M %p'))
		

		dropdown_slotes['available_slotes'] = available_slotes
		dropdown_slotes['busy_slotes']      = busy_slotes
		dropdown_slotes['combined_slots']   = combined_slots
		dropdown_slotes['success']          = True
		
		return Response(dropdown_slotes,HTTP_200_OK)


class GetMultipleServiceDateCleaningSlotesAutofix(APIView):  
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
			elif service_type == 'Kitchen Appliances':
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
		shift_availability_check= request.data.get('shift_availability_check')
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
				if shift_availability_check:
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=slote_start_time)&Q(shift1_end_at__gte=slote_start_time))&Q(Q(shift1_start_at__lte=slote_end_time)&Q(shift1_end_at__gte=slote_end_time))) | Q(Q(Q(shift2_start_at__lte=slote_start_time)&Q(shift2_end_at__gte=slote_start_time))&Q(Q(shift2_start_at__lte=slote_end_time)&Q(shift2_end_at__gte=slote_end_time))) | Q(Q(Q(shift3_start_at__lte=slote_start_datetime)&Q(shift3_end_at__gte=slote_start_datetime))&Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_at_date)|Q(shift_date=end_at_date)|Q(Q(shift3_start_at__lte=slote_end_datetime)&Q(shift3_end_at__gte=slote_end_datetime)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=slote_start_time)&Q(universal_shift_end__gte=slote_start_time))&Q(Q(universal_shift_start__lte=slote_end_time)&Q(universal_shift_end__gte=slote_end_time))).values_list('id',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = slote_start_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = slote_start_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = slote_end_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = slote_end_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
		
					if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
						total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))).exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
						total_newleaders  = total_leaders.filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))
					
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))

				#excluded shift cleaners
				else:
					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = slote_start_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = slote_start_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = slote_end_datetime.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = slote_end_datetime.replace(hour=22,minute=0,second=0,microsecond=0)
		
					if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
						total_newcleaners = total_cleaners.exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners
						total_newleaders  = total_leaders

					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners)
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders)

				if start_at_date == actual_cleaningdate and end_at_date == actual_cleaningdate:				

					#active cleaners
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=slote_start_datetime)&Q(start_at__lt=slote_end_datetime))|Q(Q(end_at__gt=slote_start_datetime)&Q(end_at__lte=slote_end_datetime))|Q(Q(start_at__lte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__gte=slote_end_datetime))|Q(Q(start_at__gte=slote_start_datetime)&Q(end_at__gte=slote_start_datetime)&Q(start_at__lte=slote_end_datetime)&Q(end_at__lte=slote_end_datetime))))
	
					for service_type in service_types:					
						if service_type == 'General Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
						elif service_type == 'Deep Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
						elif service_type == 'Upholstery Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
						elif service_type == 'Kitchen Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
						elif service_type == 'Kitchen Appliances':
							active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
						elif service_type == 'Carpet Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
						elif service_type == 'Sterilization':
							active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
						elif service_type == 'Mattress Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
						elif service_type == 'Facade Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
						elif service_type == 'Storage Area':
							active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
						elif service_type == 'Car Parking Umbrella':
							active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
							new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
						elif service_type == 'Window Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
						elif service_type == 'Outdoor Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

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

					new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
					new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)

					#(8 to 22 leave logic applied)
					if (leavestart_at_datetime1 <= slote_start_datetime and leaveend_at_datetime1 > slote_start_datetime) or (leavestart_at_datetime2 < slote_end_datetime and leaveend_at_datetime2 >= slote_end_datetime):
						for absent_cleaner in new_absent_cleaners:
							team_members_scheduled.append(absent_cleaner)
						for absent_leader in new_absent_leaders:
							team_leaders_scheduled.append(absent_leader)

					total_newcleaners = total_newcleaners.exclude(id__in=team_members_scheduled)
					total_newleaders  = total_newleaders.exclude(id__in=team_leaders_scheduled)

					#slote availability				
					if total_newcleaners and total_newleaders:
						if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
							slote_details[cleaning_datetime] =	datetime.strftime(slote_start_datetime,'%d-%m-%Y %I:%M %p')
							break
					else:
						slote_details[cleaning_datetime] = 'NOt Available'
				else:
					slote_details[cleaning_datetime] = 'Not Available'

		dropdown_slotes['slote_details']    = slote_details
		dropdown_slotes['success']          = True
		
		return Response(dropdown_slotes,HTTP_200_OK)


class GetAvailableCleaners(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request):
		response_dict            = {}
		response_dict['success'] = False

		cleaning_datetime_start      = datetime.strptime(request.data.get('cleaning_datetime_start'),'%d-%m-%Y %I:%M %p')
		cleaning_datetime_end        = datetime.strptime(request.data.get('cleaning_datetime_end'),'%d-%m-%Y %I:%M %p')
		service_types                = request.data.get('service_types')
		
		team_leaders_scheduled      = []
		team_members_scheduled      = []
		#absent cleaners and leaders
		cleaning_date1   = cleaning_datetime_start.date()
		cleaning_date2   = cleaning_datetime_end.date()	
		absent_cleaners  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=cleaning_date1)|Q(leave_date=cleaning_date2))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)

		#included shift cleaners
		shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=cleaning_date1)|Q(shift_date=cleaning_date2)|Q(Q(shift3_start_at__lte=cleaning_datetime_end)&Q(shift3_end_at__gte=cleaning_datetime_end)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=cleaning_datetime_start.time())&Q(shift1_end_at__gte=cleaning_datetime_start.time()))&Q(Q(shift1_start_at__lte=cleaning_datetime_end.time())&Q(shift1_end_at__gte=cleaning_datetime_end.time()))) | Q(Q(Q(shift2_start_at__lte=cleaning_datetime_start.time())&Q(shift2_end_at__gte=cleaning_datetime_start.time()))&Q(Q(shift2_start_at__lte=cleaning_datetime_end.time())&Q(shift2_end_at__gte=cleaning_datetime_end.time()))) | Q(Q(Q(shift3_start_at__lte=cleaning_datetime_start)&Q(shift3_end_at__gte=cleaning_datetime_start))&Q(Q(shift3_start_at__lte=cleaning_datetime_end)&Q(shift3_end_at__gte=cleaning_datetime_end))) ).values_list('staff',flat=True)
		today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=cleaning_date1)|Q(shift_date=cleaning_date2)|Q(Q(shift3_start_at__lte=cleaning_datetime_end)&Q(shift3_end_at__gte=cleaning_datetime_end)))).values_list('staff',flat=True)
		super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=cleaning_datetime_start.time())&Q(universal_shift_end__gte=cleaning_datetime_start.time()))&Q(Q(universal_shift_start__lte=cleaning_datetime_end.time())&Q(universal_shift_end__gte=cleaning_datetime_end.time())) ).values_list('id',flat=True)
		

		#Active cleaners
		new_absent_cleaners = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))

		active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=cleaning_datetime_start)&Q(start_at__lt=cleaning_datetime_end))|Q(Q(end_at__gt=cleaning_datetime_start)&Q(end_at__lte=cleaning_datetime_end))|Q(Q(start_at__lte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__gte=cleaning_datetime_end))|Q(Q(start_at__gte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__lte=cleaning_datetime_end))))
		active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=cleaning_datetime_start)&Q(start_at__lt=cleaning_datetime_end))|Q(Q(end_at__gt=cleaning_datetime_start)&Q(end_at__lte=cleaning_datetime_end))|Q(Q(start_at__lte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__gte=cleaning_datetime_end))|Q(Q(start_at__gte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__lte=cleaning_datetime_end))))		
		
		for service_type in service_types:
					
			if service_type == 'General Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
			elif service_type == 'Kitchen Appliances':
				active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
				active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
				new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)

		new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)

		cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)
		followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

		#merging
		for active_team_member in cleaning_active_cleaners:
			team_members_scheduled.append(active_team_member)
		for active_team_member in followup_active_cleaners:
			team_members_scheduled.append(active_team_member)

		#(8 -22 leave logic applied)
		leavestart_at_datetime1  = cleaning_datetime_start.replace(hour=8,minute=0,second=0,microsecond=0)
		leaveend_at_datetime1    = cleaning_datetime_start.replace(hour=22,minute=0,second=0,microsecond=0)
		leavestart_at_datetime2  = cleaning_datetime_end.replace(hour=8,minute=0,second=0,microsecond=0)
		leaveend_at_datetime2    = cleaning_datetime_end.replace(hour=22,minute=0,second=0,microsecond=0)

		if (leavestart_at_datetime1 <= cleaning_datetime_start and leaveend_at_datetime1 > cleaning_datetime_start) or (leavestart_at_datetime2 < cleaning_datetime_end and leaveend_at_datetime2 >= cleaning_datetime_end):		
			for absent_cleaner in new_absent_cleaners:
				team_members_scheduled.append(absent_cleaner)

		#count total cleaners and total leaders
		total_cleaners = UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
		for service_type in service_types:
			if service_type == 'General Cleaning':
				total_cleaners 	= total_cleaners.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
			elif service_type == 'Kitchen Appliances':
				total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				total_cleaners 	= total_cleaners.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)

		#(8 to 22 logic applied)
		if (leavestart_at_datetime1 <= cleaning_datetime_start and leaveend_at_datetime1 > cleaning_datetime_start) or (leavestart_at_datetime2 < cleaning_datetime_end and leaveend_at_datetime2 >= cleaning_datetime_end):		
			total_cleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners)
		else:
			total_cleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					
		available_cleaners = total_cleaners.exclude(id__in=team_members_scheduled)

		response_dict['available_cleaners'] = UserProfileShowSerializer(instance=available_cleaners,many=True).data
		response_dict['success'] 			= True

		return Response(response_dict,HTTP_200_OK)


class GetSubscriptionSlotes(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict            = {}
		response_dict['success'] = False

		book_id                          = request.GET.get('book_id')
		order_schedules                  = OrderScheduler.objects.filter(order_scheduler_book__id=book_id)
		
		response_dict['subscriptions']   = OrderScheduleShowSerializer(instance=order_schedules,many=True).data

		response_dict['success']         = True

		return Response(response_dict,HTTP_200_OK)

class GetAvailableCleanersGroupSubscription(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request):
		response_dict            = {}
		response_dict['success'] = False

		service_types                = request.data.get('service_types')
		subscription_details         = request.data.get('subscription_details')
		
		available_cleaners_list      = []
		
		for subscription_detail in subscription_details:
			cleaning_datetime_start      = datetime.strptime(subscription_detail['cleaning_datetime_start'],'%d-%m-%Y %I:%M %p')
			cleaning_datetime_end        = datetime.strptime(subscription_detail['cleaning_datetime_end'],'%d-%m-%Y %I:%M %p')
			
			team_leaders_scheduled      = []
			team_members_scheduled      = []
			#absent cleaners and leaders
			cleaning_date1   = cleaning_datetime_start.date()
			cleaning_date2   = cleaning_datetime_end.date()	
			absent_cleaners  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=cleaning_date1)|Q(leave_date=cleaning_date2))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)

			#included shift cleaners
			shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=cleaning_date1)|Q(shift_date=cleaning_date2)|Q(Q(shift3_start_at__lte=cleaning_datetime_end)&Q(shift3_end_at__gte=cleaning_datetime_end)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=cleaning_datetime_start.time())&Q(shift1_end_at__gte=cleaning_datetime_start.time()))&Q(Q(shift1_start_at__lte=cleaning_datetime_end.time())&Q(shift1_end_at__gte=cleaning_datetime_end.time()))) | Q(Q(Q(shift2_start_at__lte=cleaning_datetime_start.time())&Q(shift2_end_at__gte=cleaning_datetime_start.time()))&Q(Q(shift2_start_at__lte=cleaning_datetime_end.time())&Q(shift2_end_at__gte=cleaning_datetime_end.time()))) | Q(Q(Q(shift3_start_at__lte=cleaning_datetime_start)&Q(shift3_end_at__gte=cleaning_datetime_start))&Q(Q(shift3_start_at__lte=cleaning_datetime_end)&Q(shift3_end_at__gte=cleaning_datetime_end))) ).values_list('staff',flat=True)
			today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=cleaning_date1)|Q(shift_date=cleaning_date2)|Q(Q(shift3_start_at__lte=cleaning_datetime_end)&Q(shift3_end_at__gte=cleaning_datetime_end)))).values_list('staff',flat=True)
			super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=cleaning_datetime_start.time())&Q(universal_shift_end__gte=cleaning_datetime_start.time()))&Q(Q(universal_shift_start__lte=cleaning_datetime_end.time())&Q(universal_shift_end__gte=cleaning_datetime_end.time())) ).values_list('id',flat=True)
			

			#Active cleaners
			new_absent_cleaners = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))

			active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=cleaning_datetime_start)&Q(start_at__lt=cleaning_datetime_end))|Q(Q(end_at__gt=cleaning_datetime_start)&Q(end_at__lte=cleaning_datetime_end))|Q(Q(start_at__lte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__gte=cleaning_datetime_end))|Q(Q(start_at__gte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__lte=cleaning_datetime_end))))
			active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=cleaning_datetime_start)&Q(start_at__lt=cleaning_datetime_end))|Q(Q(end_at__gt=cleaning_datetime_start)&Q(end_at__lte=cleaning_datetime_end))|Q(Q(start_at__lte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__gte=cleaning_datetime_end))|Q(Q(start_at__gte=cleaning_datetime_start)&Q(end_at__gte=cleaning_datetime_start)&Q(start_at__lte=cleaning_datetime_end)&Q(end_at__lte=cleaning_datetime_end))))		
			
			for service_type in service_types:
						
				if service_type == 'General Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
				elif service_type == 'Kitchen Appliances':
					active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
				elif service_type == 'Sterilization':
					active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
				elif service_type == 'Storage Area':
					active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
					active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
					new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)

			new_absent_cleaners          = new_absent_cleaners.values_list('id',flat=True)

			cleaning_active_cleaners     = active_cleaners1.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)
			followup_active_cleaners     = active_cleaners2.filter(Q(Q(member__user_type='TEAMINCHARGE')|Q(member__user_type='CLEANER'))).values_list('member',flat=True)

			#merging
			for active_team_member in cleaning_active_cleaners:
				team_members_scheduled.append(active_team_member)
			for active_team_member in followup_active_cleaners:
				team_members_scheduled.append(active_team_member)

			#(8 -22 leave logic applied)
			leavestart_at_datetime1  = cleaning_datetime_start.replace(hour=8,minute=0,second=0,microsecond=0)
			leaveend_at_datetime1    = cleaning_datetime_start.replace(hour=22,minute=0,second=0,microsecond=0)
			leavestart_at_datetime2  = cleaning_datetime_end.replace(hour=8,minute=0,second=0,microsecond=0)
			leaveend_at_datetime2    = cleaning_datetime_end.replace(hour=22,minute=0,second=0,microsecond=0)

			if (leavestart_at_datetime1 <= cleaning_datetime_start and leaveend_at_datetime1 > cleaning_datetime_start) or (leavestart_at_datetime2 < cleaning_datetime_end and leaveend_at_datetime2 >= cleaning_datetime_end):		
				for absent_cleaner in new_absent_cleaners:
					team_members_scheduled.append(absent_cleaner)

			#count total cleaners and total leaders
			total_cleaners = UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			for service_type in service_types:
				if service_type == 'General Cleaning':
					total_cleaners 	= total_cleaners.filter(is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					total_cleaners 	= total_cleaners.filter(is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					total_cleaners 	= total_cleaners.filter(is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				elif service_type == 'Kitchen Appliances':
					total_cleaners 	= total_cleaners.filter(is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					total_cleaners 	= total_cleaners.filter(is_carpet_skill=True)
				elif service_type == 'Sterilization':
					total_cleaners 	= total_cleaners.filter(is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					total_cleaners 	= total_cleaners.filter(is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					total_cleaners 	= total_cleaners.filter(is_facade_skill=True)
				elif service_type == 'Storage Area':
					total_cleaners 	= total_cleaners.filter(is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					total_cleaners 	= total_cleaners.filter(is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					total_cleaners 	= total_cleaners.filter(is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					total_cleaners 	= total_cleaners.filter(is_outdoor_skill=True)

			#(8 to 22 logic applied)
			if (leavestart_at_datetime1 <= cleaning_datetime_start and leaveend_at_datetime1 > cleaning_datetime_start) or (leavestart_at_datetime2 < cleaning_datetime_end and leaveend_at_datetime2 >= cleaning_datetime_end):		
				total_cleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))).exclude(id__in=absent_cleaners)
			else:
				total_cleaners = total_cleaners.filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
						
			available_cleaners = total_cleaners.exclude(id__in=team_members_scheduled).values_list('id',flat=True)

			available_cleaners_list.append(available_cleaners)

		final_available_cleaners_list  = list(set.intersection(*map(set,available_cleaners_list)))
		final_available_cleaners       = UserProfile.objects.filter(id__in=final_available_cleaners_list)

		response_dict['available_cleaners'] = UserProfileShowSerializer(instance=final_available_cleaners,many=True).data
		response_dict['success'] 			= True

		return Response(response_dict,HTTP_200_OK)

class GroupSubscriptionSave(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request):
		response_dict             = {}
		response_dict['success']  = False

		assigned_cleaners         = request.data.get('assigned_cleaners')
		assigned_leader           = request.data.get('team_leader')
		schedules                 = request.data.get('schedules')

		for schedule in schedules:
			order_schedule            = OrderScheduler.objects.get(id=schedule)
			start_at_datetime         = order_schedule.start_at
			end_at_datetime           = order_schedule.end_at
			start_at_time             = start_at_datetime.time()
			end_at_time               = end_at_datetime.time()
	
			#same blc cleaners for excluding
			sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=order_schedule.evaluation_details.evaluation).filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime))|Q(Q(end_at__gte=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

			active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
			active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_at_datetime)&Q(start_at__lt=end_at_datetime))|Q(Q(end_at__gt=start_at_datetime)&Q(end_at__lte=end_at_datetime))|Q(Q(start_at__lte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__gte=end_at_datetime))|Q(Q(start_at__gte=start_at_datetime)&Q(end_at__gte=start_at_datetime)&Q(start_at__lte=end_at_datetime)&Q(end_at__lte=end_at_datetime)))).values_list("member",flat=True)

			#check cleaners	& leaders	
			check_cleaners      = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id__in=assigned_cleaners)
			check_tl            = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(id=assigned_leader)

			if	check_cleaners.count() >= len(assigned_cleaners) and check_tl:
				cleaning_team = CleaningTeam.objects.create(order_scheduler=order_schedule,team_leader_id=assigned_leader,start_at=start_at_datetime,end_at=end_at_datetime)
				
				#cleaners
				assigned_cleaners_list   = []
				for cleaner in assigned_cleaners:
					assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member_id=cleaner,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				assigned_cleaners_list.append(CleaningTeamMember(team=cleaning_team,member=cleaning_team.team_leader,start_at=start_at_datetime,end_at=end_at_datetime,start_time=start_at_time,end_time=end_at_time))
				#bulk create
				cleaning_team_members_assign = CleaningTeamMember.objects.bulk_create(assigned_cleaners_list)

				if cleaning_team_members_assign:
					#update cleaners count
					order_scheduler.no_of_cleaners = len(assigned_cleaners)+1
					order_scheduler.work_status    = 'CLEANING_TEAM_ASSIGNED'
					order_scheduler.save()

				response_dict['success']  = True
			else:
				response_dict['success']  = False
				response_dict['error']    = 'Some Cleanings Not Updated ! Please Check that Manually'


		return Response(response_dict,HTTP_200_OK)


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
		
		with transaction.atomic():
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
				elif service_type == 'Kitchen Appliances':
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
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

					#absent cleaners and leaders	

					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):					
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
					
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))

					for service_detail in services.keys():
						service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
						service_type   		= service.name
		
						if service_type == 'General Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
						elif service_type == 'Deep Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
						elif service_type == 'Upholstery Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
						elif service_type == 'Kitchen Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
						elif service_type == 'Kitchen Appliances':
							active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
						elif service_type == 'Carpet Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
						elif service_type == 'Sterilization':
							active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
						elif service_type == 'Mattress Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
						elif service_type == 'Facade Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
						elif service_type == 'Storage Area':
							active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
						elif service_type == 'Car Parking Umbrella':
							active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
							new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
						elif service_type == 'Window Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
						elif service_type == 'Outdoor Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

					new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
					new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)

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

					#(applying 8 to 22 leave logic)
					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						for absent_cleaner in new_absent_cleaners:
							team_members_scheduled.append(absent_cleaner)
						for absent_leader in new_absent_leaders:
							team_leaders_scheduled.append(absent_leader)

					total_newcleaners = total_newcleaners.exclude(id__in=team_members_scheduled)
					total_newleaders = total_newleaders.exclude(id__in=team_leaders_scheduled)

					#slote appending
					if total_newcleaners and total_newleaders:
						if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
							pass
						else:
							response_dict['Error'] = 'Cleaners are not available'
							return Response(response_dict,HTTP_200_OK)
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

						active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
						active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)


						#included shift cleaners
						shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
						super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

						#(applying 8 to 22 leave logic)
						leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
						leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
						leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
						leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

						if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
							leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
							cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						else:
							leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
							cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

						
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
							elif service_type == 'Kitchen Appliances':
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
							for key1 in keynotes_dict.keys():
								keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key1])
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
						
						#create add-ons
						try:
							addons_dict = sections_dict[key]['addons']
						except:
							addons_dict = None
						if addons_dict:
							for key2 in addons_dict.keys():
								addons_save_serializer = EvaluationSectionAddonSerializer(data=addons_dict[key2])
								if addons_save_serializer.is_valid():
									saved_addon       = addons_save_serializer.save(evaluation_section=saved_section)
									
									response_dict['addon_success']       = True
								else:
									errors= addons_save_serializer.errors   
									key=tuple(errors.keys())[0] 
									error=errors[key]
									response_dict['addon_Error']      = key +':'+ error[0]
									response_dict['addon_Error_List'] = addons_save_serializer.errors

									response_dict['addon_success']    = False

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
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

					#absent cleaners and leaders	
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))

					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
					
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))

					for service_detail in services.keys():
						service        		= ServiceType.objects.get(id=services[service_detail]['service_type'])
						service_type   		= service.name
		
						if service_type == 'General Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
						elif service_type == 'Deep Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
						elif service_type == 'Upholstery Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
						elif service_type == 'Kitchen Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
						elif service_type == 'Kitchen Appliances':
							active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
						elif service_type == 'Carpet Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
						elif service_type == 'Sterilization':
							active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
						elif service_type == 'Mattress Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
						elif service_type == 'Facade Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
						elif service_type == 'Storage Area':
							active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
						elif service_type == 'Car Parking Umbrella':
							active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
							new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
						elif service_type == 'Window Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
						elif service_type == 'Outdoor Cleaning':
							active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
							active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
							new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
							new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)


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

					#(applying 8 to 22 logic)
					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						for absent_cleaner in new_absent_cleaners:
							team_members_scheduled.append(absent_cleaner)
						for absent_leader in new_absent_leaders:
							team_leaders_scheduled.append(absent_leader)

					total_newcleaners = total_newcleaners.exclude(id__in=team_members_scheduled)
					total_newleaders  = total_newleaders.exclude(id__in=team_leaders_scheduled)

					#slote appending
					if total_newcleaners and total_newleaders:
						if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
							pass
						else:
							response_dict['Error'] = 'Cleaners are not available'
							return Response(response_dict,HTTP_200_OK)
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

						active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
						active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

						#included shift cleaners
						shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
						super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)


						#(applying 8 to 22 leave logic)
						leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
						leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
						leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
						leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

						if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
							leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
							cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						else:
							leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
							cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

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
							elif service_type == 'Kitchen Appliances':
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
						try:
							keynotes_dict = sections_dict[key]['keynotes']
						except:
							keynotes_dict = None
						if keynotes_dict:
							for key1 in keynotes_dict.keys():
								keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key1])
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

						#create add-ons
						try:
							addons_dict = sections_dict[key]['addons']
						except:
							addons_dict = None
						if addons_dict:
							for key2 in addons_dict.keys():
								addons_save_serializer = EvaluationSectionAddonSerializer(data=addons_dict[key2])
								if addons_save_serializer.is_valid():
									saved_addon       = addons_save_serializer.save(evaluation_section=saved_section)
									
									response_dict['addon_success']       = True
								else:
									errors= addons_save_serializer.errors   
									key=tuple(errors.keys())[0] 
									error=errors[key]
									response_dict['addon_Error']      = key +':'+ error[0]
									response_dict['addon_Error_List'] = addons_save_serializer.errors

									response_dict['addon_success']    = False

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
		with transaction.atomic():
			response_dict = {'success':False}
			
			##multiple services #count total cleaners and total leaders for availability
			total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders   = UserProfile.objects.filter(user_type='TEAMINCHARGE')
			
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
				elif service_type == 'Kitchen Appliances':
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
				order           = Order.objects.get(evaluation=evaluation)
			except:
				order           = None
				
			if not order:		
				order       = Order.objects.create(evaluation=evaluation,order_no=evaluation.evaluation_id,payment_status='PENDING',invoice_no=new_invoice_no)


			###testing availability ####
			shift_availability_check = request.data.get('shift_availability_check')
			
			test_schedules_dict = list(request.data.get("service_details").values())[0]['schedule_details']
			for key in test_schedules_dict.keys():
				schedule_date           =  test_schedules_dict[key]['date']
				schedule_time           =  test_schedules_dict[key]['time']
				start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
				end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours']) 	
				start_time              =  start_date_time.time()
				end_time                =  end_date_time.time()

				number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1

				#considering shift
				if shift_availability_check:
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

					#absent cleaners and leaders	
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
					
					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
					
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))
				
				#not considering shift
				else:
					#absent cleaners and leaders	
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						total_newcleaners = total_cleaners.exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners
						total_newleaders  = total_leaders
					
					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
					
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners)
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders)

				for service_detail in services.keys():
					service        		= ServiceType.objects.get(id=int(services[service_detail]['service_type']))
					service_type   		= service.name

					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Kitchen Appliances':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
						new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

				new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
				new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)

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

				#(8 to 22 logic applied)
				if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
					for absent_cleaner in new_absent_cleaners:
						team_members_scheduled.append(absent_cleaner)
					for absent_leader in new_absent_leaders:
						team_leaders_scheduled.append(absent_leader)

				#slote appending
				if total_newcleaners and total_newleaders:
					if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
						pass
					else:
						response_dict['Error'] = 'Cleaners are not available'
						return Response(response_dict,HTTP_200_OK)
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
					order_schedule = OrderScheduler.objects.create(order=order,status='CONFIRMED',customer_address=evaluation_details.address,evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book=saved_service,no_of_cleaners=schedules_dict[key]['no_of_cleaners'],cleaning_hours=schedules_dict[key]['cleaning_hours'],hourly_cleaning_duration=schedules_dict[key]['hourly_cleaning_duration'])

				#create sections
				sections_dict = services[service_detail]['sections']
				for key in sections_dict.keys():
					section_save_serializer                    = EvaluationBookSectionSerializer(data=sections_dict[key])
					if section_save_serializer.is_valid():
						
						if services[service_detail]['cleaning_policy'] == 'SUBSCRIPTION':
							saved_section                          = section_save_serializer.save(evaluation_book=saved_service,section_cleanings=len(schedules_dict),section_net_cost=section_save_serializer.validated_data['section_cost']*len(schedules_dict))
						else:
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
					try:
						keynotes_dict = sections_dict[key]['keynotes']
					except:
						keynotes_dict = None
					if keynotes_dict:
						for key1 in keynotes_dict.keys():
							keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key1])
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
					
					#create add-ons
					try:
						addons_dict = sections_dict[key]['addons']
					except:
						addons_dict = None
					if addons_dict:
						for key2 in addons_dict.keys():
							addons_save_serializer = EvaluationSectionAddonSerializer(data=addons_dict[key2])
							if addons_save_serializer.is_valid():
								saved_addon       = addons_save_serializer.save(evaluation_section=saved_section)
								
								response_dict['addon_success']       = True
							else:
								errors= addons_save_serializer.errors   
								key=tuple(errors.keys())[0] 
								error=errors[key]
								response_dict['addon_Error']      = key +':'+ error[0]
								response_dict['addon_Error_List'] = addons_save_serializer.errors

								response_dict['addon_success']    = False

								return Response(response_dict,HTTP_200_OK)

				service_dict[saved_service.id] = services[service_detail]['service_type']				

			response_dict['evaluation_book_ids'] = service_dict
			response_dict['success']             = True

		return Response(response_dict,HTTP_200_OK)


class EvaluatorMultipleCleaningBookingLetCustomerPhase2(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request,evaluation_details_id): 

		with transaction.atomic():
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
			evaluation.save()

			#order cost updation
			order.total_amount         += request.data.get('total_cost')
			order.remining_amount      += request.data.get('total_cost')
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
					try:
						keynotes_dict = sections_dict[key]['keynotes']
					except:
						keynotes_dict = None					
					if keynotes_dict:
						for key1 in keynotes_dict.keys():
							keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key1])
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

					#create add-ons
					try:
						addons_dict = sections_dict[key]['addons']
					except:
						addons_dict = None
					if addons_dict:
						for key2 in addons_dict.keys():
							addons_save_serializer = EvaluationSectionAddonSerializer(data=addons_dict[key2])
							if addons_save_serializer.is_valid():
								saved_addon       = addons_save_serializer.save(evaluation_section=saved_section)
								
								response_dict['addon_success']       = True
							else:
								errors= addons_save_serializer.errors   
								key=tuple(errors.keys())[0] 
								error=errors[key]
								response_dict['addon_Error']      = key +':'+ error[0]
								response_dict['addon_Error_List'] = addons_save_serializer.errors

								response_dict['addon_success']    = False

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
		
		with transaction.atomic():
			response_dict = {}
			
			duplicate_evaluation         = Evaluation.objects.get(id=evaluation_id)		
			duplicate_evaluation_details = EvaluationDetails.objects.filter(is_active=True,evaluation=duplicate_evaluation).prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True).prefetch_related(Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='schedules'),Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='booksections')),to_attr='evaluationbooks'))

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
			call_attender  = UserProfile.objects.get(id=request.GET.get('user_id'))
			new_evaluation = Evaluation.objects.create(tracking_no=int(tracking_no)+1,evaluation_id=evaluation_no,customer=duplicate_evaluation.customer,call_attender=call_attender,quatation_expiry_date=timezone.now()+timedelta(7))
			
			#duplicate the order
			new_order      = Order.objects.create(evaluation=new_evaluation,order_no=new_evaluation.evaluation_id)

			if duplicate_evaluation_details:

				#new evaluation details
				for duplicate_evaluation in duplicate_evaluation_details:
					new_duplicate_evaluation_details = EvaluationDetails.objects.create(evaluation=new_evaluation,address=duplicate_evaluation.address,status=duplicate_evaluation.status)
					
					#new book
					if duplicate_evaluation.evaluationbooks:
						for duplicate_book in duplicate_evaluation.evaluationbooks:
							if duplicate_book.cleaning_policy == 'SUBSCRIPTION':
								new_duplicate_book = EvaluationBook.objects.create(evaluation_details=new_duplicate_evaluation_details,cleaning_policy=duplicate_book.cleaning_policy,service_type=duplicate_book.service_type,area_type=duplicate_book.area_type,cleaning_method=duplicate_book.cleaning_method,location_type=duplicate_book.location_type,estimated_cost=duplicate_book.estimated_cost/len(duplicate_book.schedules))						
							else:
								new_duplicate_book = EvaluationBook.objects.create(evaluation_details=new_duplicate_evaluation_details,cleaning_policy=duplicate_book.cleaning_policy,service_type=duplicate_book.service_type,area_type=duplicate_book.area_type,cleaning_method=duplicate_book.cleaning_method,location_type=duplicate_book.location_type,estimated_cost=duplicate_book.estimated_cost)
							#new booksection
							if duplicate_book.booksections:
								for duplicate_book_section in duplicate_book.booksections:
									new_duplicate_section = EvaluationBookSection.objects.create(evaluation_book=new_duplicate_book,section_name=duplicate_book_section.section_name,section_name_arabic=duplicate_book_section.section_name_arabic,category=duplicate_book_section.category,dirt_level=duplicate_book_section.dirt_level,quantity=duplicate_book_section.quantity,size=duplicate_book_section.size,unit=duplicate_book_section.unit,age=duplicate_book_section.age,floor=duplicate_book_section.floor,apartment=duplicate_book_section.apartment,room=duplicate_book_section.room,wall_type=duplicate_book_section.wall_type,ceiling_type=duplicate_book_section.ceiling_type,floor_type=duplicate_book_section.floor_type,material=duplicate_book_section.material,colour=duplicate_book_section.colour,cause_of_stain=duplicate_book_section.cause_of_stain,section_cost=duplicate_book_section.section_cost)
								
									#new keynotes
									if duplicate_book_section.sectionkeynotes:
										for duplicate_keynote in duplicate_book_section.sectionkeynotes:	
											new_duplicate_keynote = EvaluationSectionKeynote.objects.create(evaluation_section=new_duplicate_section,sub_area=duplicate_keynote.sub_area,quantity=duplicate_keynote.quantity,)

									#new addons
									if duplicate_book_section.sectionaddons:
										for duplicate_addon in duplicate_book_section.sectionaddons:	
											new_duplicate_addon = EvaluationSectionAddons.objects.create(evaluation_section=new_duplicate_section,name=duplicate_addon.name,addon_cost=duplicate_addon.addon_cost,quantity=duplicate_addon.quantity,addon_net_cost=duplicate_addon.addon_net_cost,size=duplicate_addon.size,other_details=duplicate_addon.other_details)

			response_dict['evaluation_id'] = new_order.evaluation.evaluation_id[3:14]
			response_dict['success']       = True

		return Response(response_dict,HTTP_200_OK)

	def post(self,request,evaluation_id):
		
		with transaction.atomic():
			response_dict            = {}
			response_dict['success'] = False

			evaluation              = Evaluation.objects.get(evaluation_id=evaluation_id)
			order    				= Order.objects.get(evaluation=evaluation)
			services 				= request.data.get('service_details')

			###testing availability ####
			total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders   = UserProfile.objects.filter(user_type='TEAMINCHARGE')
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
				elif service_type == 'Kitchen Appliances':
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


			shift_availability_check = request.data.get('shift_availability_check')
			test_schedules_dict = list(request.data.get("service_details").values())[0]['schedule_details']
			for key in test_schedules_dict.keys():
				schedule_date           =  test_schedules_dict[key]['date']
				schedule_time           =  test_schedules_dict[key]['time']
				start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
				end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours'])
				start_time              =  start_date_time.time()
				end_time                =  end_date_time.time() 	

				number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1

				#Considering Shift
				if shift_availability_check:
					#included shift cleaners
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

					#absent cleaners and leaders	
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))

					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
				
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))

				else:
					#absent cleaners and leaders	
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						total_newcleaners = total_cleaners.exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners
						total_newleaders  = total_leaders

					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
				
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners)
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders)

				for service_detail in services.keys():
					service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
					service_type   		        = service_book.service_type.name

					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Kitchen Appliances':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
						new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

				new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
				new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)
				
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

				#(applying 8 to 22 logic)
				if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
					for absent_cleaner in new_absent_cleaners:
						team_members_scheduled.append(absent_cleaner)
					for absent_leader in new_absent_leaders:
						team_leaders_scheduled.append(absent_leader)


				total_newcleaners = total_newcleaners.exclude(id__in=team_members_scheduled)
				total_newleaders = total_newleaders.exclude(id__in=team_leaders_scheduled)
				
				#slote appending
				if total_newcleaners and total_newleaders:
						if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
							pass
						else:
							response_dict['Error'] = 'Cleaners are not available'
							return Response(response_dict,HTTP_200_OK)
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
					service_book.total_cost               = service_book.estimated_cost
					service_book.estimated_cost           = service_book.estimated_cost
				service_book.save()

				print(service_book.cleaning_policy,"cleaning_policy")
				print(len(schedules_dict),"No of Cleanings")
				print(service_book.total_cost,"Total Cost")
				print(service_book.estimated_cost,"Estimated Cost")

				##cost updation
				evaluation_details.estimated_cost     += int(service_book.estimated_cost)
				evaluation_details.total_cost         += int(service_book.total_cost)

				evaluation.estimated_cost     		  += int(service_book.estimated_cost)
				evaluation.total_cost         		  += int(service_book.total_cost)
				evaluation.quatation_status            = 'PENDING'

				order.total_amount                    += int(service_book.total_cost)
				order.remining_amount                 += int(service_book.total_cost)

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

					evaluation_details.save()
					evaluation.save()
					order.save()

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
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
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
		evaluation_id           = 'BLC'+evaluation_id_encrypted[3:14]
		
		#evaluation books,sections,and keynotes
		evaluation_details                  = EvaluationDetails.objects.select_related('evaluation').prefetch_related('evaluation_book_evaluation_details__evaluationsection_book__keynotesections').filter(evaluation__evaluation_id=evaluation_id)
		order_details                       = Order.objects.get(evaluation__evaluation_id=evaluation_id)
		try:
			customer_booking                    = CustomerBooking.objects.select_related('evaluation').get(evaluation__evaluation_id=evaluation_id)
		except:
			customer_booking                    = None

		response_dict['evaluation_details'] = EvaluationDetailsSerializer(instance=evaluation_details,many=True).data
		response_dict['order_details']      = OrderSerializer(instance=order_details).data
		response_dict['discount_details']   = EvaluationSerializer(instance=order_details.evaluation).data

		response_dict['evaluation_id']      = evaluation_details.first().evaluation.id
		response_dict['secret_code']        = str(order_details.evaluation.evaluation_id[3:14])+str(order_details.evaluation.customer.username)

		if customer_booking:
			response_dict['booking_status'] = customer_booking.is_bookingcompleted		
	
		response_dict['success']            = True
		
		return Response(response_dict,HTTP_200_OK)

	def post(self,request,evaluation_id):

		with transaction.atomic():
			response_dict            = {}
			response_dict['success'] = False

			#evaluation id decryption
			evaluation_id_encrypted = evaluation_id
			evaluation_id 			= 'BLC'+evaluation_id_encrypted[3:14]

			evaluation              = Evaluation.objects.get(evaluation_id=evaluation_id)
			order    				= Order.objects.get(evaluation=evaluation)
			services 				= request.data.get('service_details')
			gender                  = request.data.get('gender')

			###testing availability ####
			if gender:
				total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE'))&Q(gender=gender))
				total_leaders   = UserProfile.objects.filter(is_general_skill=True,user_type='TEAMINCHARGE',gender=gender)
			else:
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
				elif service_type == 'Kitchen Appliances':
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
				if gender:
					shift_cleaners  = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))&Q(staff__gender=gender)).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					shift_leaders   = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE',staff__gender=gender).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(is_active=True,staff__gender=gender).filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE'))&Q(gender=gender))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE',gender=gender).exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)
				else:	
					shift_cleaners  = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					shift_leaders   = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

				#absent cleaners and leaders	
				if gender:
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))&Q(staff__gender=gender)).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE',staff__gender=gender).values_list('staff',flat=True)
				else:
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)


				#(applying 8 to 22 leave logic)
				leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
				leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
				leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

				if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
					total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners)
					total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders)
				else:
					total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
					total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))

				#same blc cleaners for excluding
				sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

				if gender:
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(member__gender=gender).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(member__gender=gender).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
				else:
					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))

				new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
				new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))
				
				for service_detail in services.keys():
					service_book        		= EvaluationBook.objects.get(id=services[service_detail]['id'])
					service_type   		        = service_book.service_type.name

					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Kitchen Appliances':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
						new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

				new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
				new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)

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

				#(applying 8 to 22 leave logic)
				if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
					for absent_cleaner in new_absent_cleaners:
						team_members_scheduled.append(absent_cleaner)
					for absent_leader in new_absent_leaders:
						team_leaders_scheduled.append(absent_leader)

				total_newcleaners = total_newcleaners.exclude(id__in=team_members_scheduled)
				total_newleaders = total_newleaders.exclude(id__in=team_leaders_scheduled)

				#slote appending
				if total_newcleaners and total_newleaders:
						if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
							pass
						else:
							response_dict['Error'] = 'Cleaners are not available'
							return Response(response_dict,HTTP_200_OK)
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

						active_cleaners1 	= CleaningTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners).values_list("member",flat=True)
						active_cleaners2 	= FollowUpTeamMember.objects.filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

						#included shift cleaners
						shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
						super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
						super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

						#(applying leave logic of 8 to 22)
						if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
							leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_leaders))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
							cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2)|Q(id__in=absent_cleaners))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						else:
							leaders             = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
							cleaners            = UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(Q(Q(id__in=active_cleaners1)|Q(id__in=active_cleaners2))).filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))

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
							elif service_type == 'Kitchen Appliances':
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

						#cleaning team assigned status in scheduler
						order_schedule.work_status = 'CLEANING_TEAM_ASSIGNED'
						order_schedule.save()
			
			#update cost details
			discount = float(request.data.get('discount'))
			if discount:
				evaluation.discount   += discount
				evaluation.total_cost -= discount

				order.total_amount    -= discount
				order.remining_amount -= discount

			#update quatation status
			evaluation.quatation_status = 'APPROVED'
			order.order_status          = 'APPROVED_BY_CLIENT'
			evaluation.save()
			order.save()

			#update customer booking completion
			CustomerBooking.objects.filter(evaluation=evaluation).update(is_bookingcompleted=True)
			

			response_dict['secret_code']        = str(evaluation.evaluation_id[3:14])+str(evaluation.customer.username)
			response_dict['order_no']           = evaluation.evaluation_id
			response_dict['order_status']       = order.order_status
			response_dict['payment_status']     = order.payment_status
			
			response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)


class AddDeleteService(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request,evaluation_details_id):
		response_dict = {}
		response_dict = {'success':False}

		#evaluation books,sections,keynotes and order details
		evaluation_details                  = EvaluationDetails.objects.select_related('evaluation').prefetch_related('evaluation_book_evaluation_details__evaluationsection_book__keynotesections').get(id=evaluation_details_id)
		order_details                       = Order.objects.get(evaluation=evaluation_details.evaluation)

		response_dict['evaluation_details'] = EvaluationDetailsSerializer(instance=evaluation_details).data
		response_dict['order_details']      = OrderSerializer(instance=order_details).data

		#deleting schedules
		OrderScheduler.objects.filter(order__evaluation=evaluation_details.evaluation).delete()

		response_dict['success']            = True

		return Response(response_dict,HTTP_200_OK)

	def post(self,request,evaluation_details_id):
		
		with transaction.atomic():
		
			response_dict = {'success':True}
			##multiple services #count total cleaners and total leaders for availability
			total_cleaners 	= UserProfile.objects.filter(Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))
			total_leaders   = UserProfile.objects.filter(user_type='TEAMINCHARGE')
			
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
				elif service_type == 'Kitchen Appliances':
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
			evaluation_details 			= EvaluationDetails.objects.select_related('evaluation').get(id=evaluation_details_id)
			evaluation         			= evaluation_details.evaluation
			order              			= Order.objects.get(evaluation=evaluation)
			
		
			###testing availability ####
			shift_availability_check 	= request.data.get('shift_availability_check')
			
			test_schedules_dict 		= list(request.data.get("service_details").values())[0]['schedule_details']
			for key in test_schedules_dict.keys():
				schedule_date           =  test_schedules_dict[key]['date']
				schedule_time           =  test_schedules_dict[key]['time']
				start_date_time         =  datetime.strptime(schedule_date+' '+schedule_time,'%d-%m-%Y %I:%M %p')
				end_date_time           =  start_date_time + timedelta(hours=test_schedules_dict[key]['cleaning_hours']) 	
				start_time              =  start_date_time.time()
				end_time                =  end_date_time.time()

				number_of_cleaners      = test_schedules_dict[key]['no_of_cleaners']-1

				#considering shift
				if shift_availability_check:
					shift_cleaners      = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					shift_leaders       = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).filter(staff__user_type='TEAMINCHARGE').filter(Q(Q(Q(shift1_start_at__lte=start_time)&Q(shift1_end_at__gte=start_time))&Q(Q(shift1_start_at__lte=end_time)&Q(shift1_end_at__gte=end_time))) | Q(Q(Q(shift2_start_at__lte=start_time)&Q(shift2_end_at__gte=start_time))&Q(Q(shift2_start_at__lte=end_time)&Q(shift2_end_at__gte=end_time))) | Q(Q(Q(shift3_start_at__lte=start_date_time)&Q(shift3_end_at__gte=start_date_time))&Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					today_shifts        = ShiftSchedule.objects.select_related('staff').filter(Q(Q(shift_date=start_date_time.date())|Q(shift_date=end_date_time.date())|Q(Q(shift3_start_at__lte=end_date_time)&Q(shift3_end_at__gte=end_date_time)))).values_list('staff',flat=True)
					super_shift_cleaners= UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='CLEANER')|Q(user_type='TEAMINCHARGE')))).exclude(id__in=today_shifts).filter( Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time)) ).values_list('id',flat=True)
					super_shift_leaders = UserProfile.objects.filter(is_active=True,user_type='TEAMINCHARGE').exclude(id__in=today_shifts).filter(Q(Q(universal_shift_start__lte=start_time)&Q(universal_shift_end__gte=start_time))&Q(Q(universal_shift_start__lte=end_time)&Q(universal_shift_end__gte=end_time))).values_list('id',flat=True)

					#absent cleaners and leaders	
					absent_cleaners 	= LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  	= LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)).exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)).exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners.filter(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners))
						total_newleaders  = total_leaders.filter(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders))
					
					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
					
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners).filter(Q(Q(id__in=shift_cleaners)|Q(id__in=super_shift_cleaners)))
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders).filter(Q(Q(id__in=shift_leaders)|Q(id__in=super_shift_leaders)))
				
				#not considering shift
				else:
					#absent cleaners and leaders	
					absent_cleaners = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).values_list('staff',flat=True)
					absent_leaders  = LeaveSchedule.objects.select_related('staff').filter(Q(Q(leave_date=start_date_time.date())|Q(leave_date=end_date_time.date()))).filter(staff__user_type='TEAMINCHARGE').values_list('staff',flat=True)

					#(applying 8 to 22 leave logic)
					leavestart_at_datetime1  = start_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime1    = start_date_time.replace(hour=22,minute=0,second=0,microsecond=0)
					leavestart_at_datetime2  = end_date_time.replace(hour=8,minute=0,second=0,microsecond=0)
					leaveend_at_datetime2    = end_date_time.replace(hour=22,minute=0,second=0,microsecond=0)

					if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
						total_newcleaners = total_cleaners.exclude(id__in=absent_cleaners)
						total_newleaders  = total_leaders.exclude(id__in=absent_leaders)
					else:
						total_newcleaners = total_cleaners
						total_newleaders  = total_leaders
					
					#same blc cleaners for excluding
					sameblc_cleaners    = CleaningTeamMember.objects.select_related('team__order_scheduler__evaluation_details__evaluation').filter(team__order_scheduler__evaluation_details__evaluation=evaluation).filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lte=end_date_time))|Q(Q(end_at__gte=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).values_list("member",flat=True)

					active_cleaners1 	= CleaningTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time)))).exclude(member__id__in=sameblc_cleaners)
					active_cleaners2 	= FollowUpTeamMember.objects.select_related('member').filter(Q(Q(Q(start_at__gte=start_date_time)&Q(start_at__lt=end_date_time))|Q(Q(end_at__gt=start_date_time)&Q(end_at__lte=end_date_time))|Q(Q(start_at__lte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__gte=end_date_time))|Q(Q(start_at__gte=start_date_time)&Q(end_at__gte=start_date_time)&Q(start_at__lte=end_date_time)&Q(end_at__lte=end_date_time))))
					
					new_absent_cleaners     = UserProfile.objects.filter(id__in=absent_cleaners)
					new_absent_leaders      = UserProfile.objects.filter(id__in=absent_leaders)

				for service_detail in services.keys():
					service        		= ServiceType.objects.get(id=int(services[service_detail]['service_type']))
					service_type   		= service.name

					if service_type == 'General Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_general_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_general_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_general_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_general_skill=True)
					elif service_type == 'Deep Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_deep_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_deep_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_deep_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_deep_skill=True)
					elif service_type == 'Upholstery Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_upholstery_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_upholstery_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_upholstery_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_upholstery_skill=True)
					elif service_type == 'Kitchen Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Kitchen Appliances':
						active_cleaners1 	= active_cleaners1.filter(member__is_kitchen_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_kitchen_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_kitchen_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_kitchen_skill=True)
					elif service_type == 'Carpet Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_carpet_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carpet_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carpet_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_carpet_skill=True)
					elif service_type == 'Sterilization':
						active_cleaners1 	= active_cleaners1.filter(member__is_sterilization_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_sterilization_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_sterilization_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_sterilization_skill=True)
					elif service_type == 'Mattress Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_mattress_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_mattress_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_mattress_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_mattress_skill=True)
					elif service_type == 'Facade Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_facade_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_facade_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_facade_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_facade_skill=True)
					elif service_type == 'Storage Area':
						active_cleaners1 	= active_cleaners1.filter(member__is_storagearea_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_storagearea_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_storagearea_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_storagearea_skill=True)
					elif service_type == 'Car Parking Umbrella':
						active_cleaners1 	= active_cleaners1.filter(member__is_carparkingumbrella_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_carparkingumbrella_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_carparkingumbrella_skill=True)
						new_absent_leaders = new_absent_leaders.filter(is_carparkingumbrella_skill=True)
					elif service_type == 'Window Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_window_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_window_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_window_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_window_skill=True)
					elif service_type == 'Outdoor Cleaning':
						active_cleaners1 	= active_cleaners1.filter(member__is_outdoor_skill=True)
						active_cleaners2 	= active_cleaners2.filter(member__is_outdoor_skill=True)
						new_absent_cleaners = new_absent_cleaners.filter(is_outdoor_skill=True)
						new_absent_leaders  = new_absent_leaders.filter(is_outdoor_skill=True)

				new_absent_cleaners = new_absent_cleaners.values_list('id',flat=True)
				new_absent_leaders  = new_absent_leaders.values_list('id',flat=True)

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

				#(8 to 22 logic applied)
				if (leavestart_at_datetime1 <= start_date_time  and leaveend_at_datetime1 > start_date_time) or (leavestart_at_datetime2 < end_date_time and leaveend_at_datetime2 >= end_date_time):
					for absent_cleaner in new_absent_cleaners:
						team_members_scheduled.append(absent_cleaner)
					for absent_leader in new_absent_leaders:
						team_leaders_scheduled.append(absent_leader)

				#slote appending
				if total_newcleaners and total_newleaders:
					if((total_newcleaners.count()-1)>=number_of_cleaners and (total_newleaders.count())>=1):
						pass
					else:
						response_dict['Error'] = 'Cleaners are not available'
						return Response(response_dict,HTTP_200_OK)
				else:
					response_dict['Error'] = 'Cleaners are not available'
					return Response(response_dict,HTTP_200_OK) 


			#Emptying and Cost Updation
			service_delete_status = request.data.get('seperate')
			if not service_delete_status:
				EvaluationBook.objects.filter(evaluation_details=evaluation_details).delete()

				evaluation.total_cost            -= evaluation_details.total_cost+evaluation.credit_amount+evaluation.discount-evaluation.additional_charge
				evaluation.estimated_cost        -= evaluation_details.estimated_cost
				evaluation.customer.credit_amount = evaluation.credit_amount
				order.total_amount        		 -= evaluation_details.total_cost+evaluation.credit_amount+evaluation.discount-evaluation.additional_charge
				order.remining_amount    		 -= evaluation_details.total_cost+evaluation.credit_amount+evaluation.discount-evaluation.additional_charge
			
				evaluation.discount               = 0
				evaluation.additional_charge	  = 0
				evaluation.credit_amount          = 0
			
				evaluation.customer.save()
				evaluation.save()
				order.save()
			
				evaluation_details.total_cost     = 0
				evaluation_details.estimated_cost = 0			
				evaluation_details.save()

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
					order_schedule = OrderScheduler.objects.create(order=order,status='CONFIRMED',customer_address=evaluation_details.address,evaluation_details=evaluation_details,start_at=start_date_time,end_at=end_date_time,order_scheduler_book=saved_service,no_of_cleaners=schedules_dict[key]['no_of_cleaners'],cleaning_hours=schedules_dict[key]['cleaning_hours'],hourly_cleaning_duration=schedules_dict[key]['hourly_cleaning_duration'])

				#create sections
				sections_dict = services[service_detail]['sections']
				for key in sections_dict.keys():
					section_save_serializer                    = EvaluationBookSectionSerializer(data=sections_dict[key])
					if section_save_serializer.is_valid():
						
						if services[service_detail]['cleaning_policy'] == 'SUBSCRIPTION':
							saved_section                          = section_save_serializer.save(evaluation_book=saved_service,section_cleanings=len(schedules_dict),section_net_cost=section_save_serializer.validated_data['section_cost']*len(schedules_dict))
						else:
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
					try:
						keynotes_dict = sections_dict[key]['keynotes']
					except:
						keynotes_dict = None
					if keynotes_dict:
						for key1 in keynotes_dict.keys():
							keynote_save_serializer = EvaluationSectionKeynoteSerializer(data=keynotes_dict[key1])
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
					
					#create add-ons
					try:
						addons_dict = sections_dict[key]['addons']
					except:
						addons_dict = None
					if addons_dict:
						for key2 in addons_dict.keys():
							addons_save_serializer = EvaluationSectionAddonSerializer(data=addons_dict[key2])
							if addons_save_serializer.is_valid():
								saved_addon       = addons_save_serializer.save(evaluation_section=saved_section)
								
								response_dict['addon_success']       = True
							else:
								errors= addons_save_serializer.errors   
								key=tuple(errors.keys())[0] 
								error=errors[key]
								response_dict['addon_Error']      = key +':'+ error[0]
								response_dict['addon_Error_List'] = addons_save_serializer.errors

								response_dict['addon_success']    = False

								return Response(response_dict,HTTP_200_OK)

				service_dict[saved_service.id] = services[service_detail]['service_type']				

			#Xero Updation
			payment_method = order.evaluation.payment_method
			if payment_method in ['PREPAID','POSTPAID','BREAKDOWN'] and order.evaluation.quatation_status == 'APPROVED':
				invoice_data = {}

				#Xero Integration
				xero          = XeroConnection.objects.first()
				#Update Access Token and Refresh Token
				header                      = {
												'Authorization': 'Basic '+xero.client_encoded,
												'Content-Type': 'application/x-www-form-urlencoded'
													}
				body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
				token_response              = requests.post('https://identity.xero.com/connect/token',
														data=body,
														headers=header 
													).json()
				access_token                = token_response['access_token']
				refresh_token               = token_response['refresh_token']

				xero.access_token  = access_token
				xero.refresh_token = refresh_token
				xero.save()	

				#Prepaid
				if payment_method == 'PREPAID':
					Amount = order.evaluation.total_cost 
					##Invoice Line Item 
					LineItems                 = []
					LineItems.append({
						"Description":"ONE TIME SERVICE",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1207004,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber  = order.invoice_no
					payment_policy = 'PREPAID'

					invoice_data       = 	{
												"Type":"ACCREC",
												"Date":order.created.strftime('%Y-%m-%d'),
												"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
												"LineAmountTypes":"NoTax",
												"InvoiceNumber":InvoiceNumber,
												"Reference":order.order_no,
												"Status":"SUBMITTED",
												"LineItems":LineItems
												}

					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
			
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

						#Remove Before Breakdown
						InvoiceNumber      = order.invoice_no+'A'
						invoice_data       = 	{
												"Type":"ACCREC",
												"LineAmountTypes":"NoTax",
												"InvoiceNumber":InvoiceNumber,
												"Reference":order.order_no,
												"Status":"DRAFT"
												}

						##xero Delete Invoice
						header                      = {
														'xero-tenant-id': xero.tenant_id,
														'Authorization': 'Bearer '+access_token,
														'Accept': 'application/json',
														'Content-Type': 'application/json'
															}

						delete_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																json=invoice_data,
																headers=header 
															).json()

						try:
							delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							delete_invoice.delete()
						except:
							delete_invoice = None

				#Breakdown Before
				if payment_method == 'BREAKDOWN':
					Amount = order.evaluation.before_cleaning_amount 
					##Invoice Line Item 
					LineItems                 = []
					LineItems.append({
						"Description":"ONE TIME SERVICE",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1207004,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber  = order.invoice_no+'A'
					payment_policy = 'BEFORE CLEANING'

					invoice_data       = 	{
												"Type":"ACCREC",
												"Date":order.created.strftime('%Y-%m-%d'),
												"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
												"LineAmountTypes":"NoTax",
												"InvoiceNumber":InvoiceNumber,
												"Reference":order.order_no,
												"Status":"SUBMITTED",
												"LineItems":LineItems
												}

					##xero Create Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()
			
					try:
						created_invoice = create_invoice['Status']
					except:
						created_invoice = None
					
					if created_invoice == 'OK':
						try:
							update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							update_xero_invoice.amount           = Amount
							update_xero_invoice.xero_marked_date = timezone.now().date()
							update_xero_invoice.payment_policy   = payment_policy
							update_xero_invoice.save()
						except:
							XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

						#Remove Prepaid
						InvoiceNumber      = order.invoice_no
						invoice_data       = 	{
												"Type":"ACCREC",
												"LineAmountTypes":"NoTax",
												"InvoiceNumber":InvoiceNumber,
												"Reference":order.order_no,
												"Status":"DRAFT"
												}

						##xero Delete Invoice
						header                      = {
														'xero-tenant-id': xero.tenant_id,
														'Authorization': 'Bearer '+access_token,
														'Accept': 'application/json',
														'Content-Type': 'application/json'
															}

						delete_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																json=invoice_data,
																headers=header 
															).json()

						try:
							delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
							delete_invoice.delete()
						except:
							delete_invoice = None

				#Post Paid
				if payment_method == 'POSTPAID':
					#Remove Prepaid Invoice
					InvoiceNumber      = order.invoice_no
					invoice_data       = 	{
											"Type":"ACCREC",
											"LineAmountTypes":"NoTax",
											"InvoiceNumber":InvoiceNumber,
											"Reference":order.order_no,
											"Status":"DRAFT"
											}

					##xero Delete Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					delete_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()

					try:
						delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
						delete_invoice.delete()
					except:
						delete_invoice = None	


					#Remove First Case Breakdown
					InvoiceNumber      = order.invoice_no+'A'
					invoice_data       = 	{
											"Type":"ACCREC",
											"LineAmountTypes":"NoTax",
											"InvoiceNumber":InvoiceNumber,
											"Reference":order.order_no,
											"Status":"DRAFT"
											}

					##xero Delete Invoice
					header                      = {
													'xero-tenant-id': xero.tenant_id,
													'Authorization': 'Bearer '+access_token,
													'Accept': 'application/json',
													'Content-Type': 'application/json'
														}

					delete_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
															json=invoice_data,
															headers=header 
														).json()

					try:
						delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
						delete_invoice.delete()
					except:
						delete_invoice = None

			response_dict['evaluation_book_ids'] = service_dict
			response_dict['success']             = True
		
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
		evaluation_book                  = EvaluationBook.objects.prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='addons')),to_attr='sections')).get(id=evaluation_book_id)
		response_dict['section_details'] = EvaluationBookSerializer(evaluation_book).data
		return Response(response_dict,HTTP_200_OK)

	def post(self,request,order_id):
		response_dict = {}
		response_dict['success'] = False
		action = request.data.get('action_type')

		order = Order.objects.select_related('evaluation').prefetch_related('order_scheduler_order').annotate(total_cleanings_count=Count('order_scheduler_order'),completed_cleanings_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),remaining_cleanings_count= F('total_cleanings_count') - F('completed_cleanings_count')).get(id=order_id)

		if action == 'add_section':                       
			section_save_serializer                    = EvaluationBookSectionSerializer(data=request.data.get('section_details'))
			if section_save_serializer.is_valid():
				evaluation_book__id                    = request.data.get('evaluation_book__id')
				evaluation_book                        = EvaluationBook.objects.select_related('evaluation_details').prefetch_related(Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).get(id=evaluation_book__id)
				total_cleanings                        = evaluation_book.order_scheduler_book_details.count()

				if evaluation_book.cleaning_policy == 'SUBSCRIPTION':
					saved_section                          = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings)
				else:
					saved_section                          = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings)

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

				#keynotes
				keynotes     = request.data.get('keynotes')
				new_keynotes = []
				for keynote in keynotes:
					new_keynotes.append(EvaluationSectionKeynote(evaluation_section=saved_section,sub_area=keynote['sub_area'],quantity=keynote['quantity']))
				EvaluationSectionKeynote.objects.bulk_create(new_keynotes)

				#addons
				addons     = request.data.get('addons')
				new_addons = []
				for addon in addons:
					new_addons.append(EvaluationSectionAddons(evaluation_section=saved_section,name=addon['name'],addon_cost=addon['addon_cost'],quantity=addon['quantity'],addon_net_cost=addon['addon_net_cost'],size=addon['size'],other_details=addon['other_details']))
				EvaluationSectionAddons.objects.bulk_create(new_keynotes)

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
				evaluation_book__id                                = request.data.get('evaluation_book__id')
				evaluation_book                                    = EvaluationBook.objects.select_related('evaluation_details').prefetch_related(Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).get(id=evaluation_book__id)
				total_cleanings                                    = evaluation_book.order_scheduler_book_details.count()

				if evaluation_book.cleaning_policy == 'SUBSCRIPTION':
					saved_section                                  = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings,section_net_cost=section_save_serializer.validated_data['section_net_cost']*total_cleanings,sectiononly_net_cost=section_save_serializer.validated_data['sectiononly_cost']*total_cleanings)
				else:
					saved_section                                  = section_save_serializer.save(evaluation_book_id=evaluation_book__id,section_cleanings=total_cleanings)

				evaluation_book.estimated_cost     				  += (saved_section.section_net_cost-old_section_cost)
				evaluation_book.total_cost         				  += (saved_section.section_net_cost-old_section_cost)
				evaluation_book.save()

				evaluation_book.evaluation_details.estimated_cost += (saved_section.section_net_cost-old_section_cost)
				evaluation_book.evaluation_details.total_cost     += (saved_section.section_net_cost-old_section_cost)
				evaluation_book.evaluation_details.save()

				order.remining_amount 							  += (saved_section.section_net_cost-old_section_cost)
				order.total_amount    							  += (saved_section.section_net_cost-old_section_cost)
				order.save()

				order.evaluation.total_cost        				  += (saved_section.section_net_cost-old_section_cost)
				order.evaluation.estimated_cost    			      += (saved_section.section_net_cost-old_section_cost)
				order.evaluation.save()

				#delete and add keynotes
				keynotes     = request.data.get('keynotes')
				new_keynotes = []
				EvaluationSectionKeynote.objects.filter(evaluation_section=saved_section).delete()
				for keynote in keynotes:
					new_keynotes.append(EvaluationSectionKeynote(evaluation_section=saved_section,sub_area=keynote['sub_area'],quantity=keynote['quantity']))
				EvaluationSectionKeynote.objects.bulk_create(new_keynotes)

				#delete and add addons
				addons       = request.data.get('addons')
				new_addons   = []
				EvaluationSectionAddons.objects.filter(evaluation_section=saved_section).delete()
				for addon in addons:
					new_addons.append(EvaluationSectionAddons(evaluation_section=saved_section,name=addon['name'],addon_cost=addon['addon_cost'],quantity=addon['quantity'],addon_net_cost=addon['addon_net_cost'],size=addon['size'],other_details=addon['other_details']))
				EvaluationSectionAddons.objects.bulk_create(new_addons)

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
			
			saved_section.evaluation_book.estimated_cost     				  -= saved_section.section_net_cost
			saved_section.evaluation_book.total_cost         				  -= saved_section.section_net_cost
			saved_section.evaluation_book.save()

			saved_section.evaluation_book.evaluation_details.estimated_cost -= saved_section.section_net_cost
			saved_section.evaluation_book.evaluation_details.total_cost     -= saved_section.section_net_cost
			saved_section.evaluation_book.evaluation_details.save()

			order.remining_amount -= saved_section.section_net_cost
			order.total_amount    -= saved_section.section_net_cost
			order.save()

			order.evaluation.total_cost        -= saved_section.section_net_cost
			order.evaluation.estimated_cost    -= saved_section.section_net_cost
			order.evaluation.save()

			saved_section.delete()

			response_dict['section_delete_success']  = True
			response_dict['success']  = True

			return Response(response_dict,HTTP_200_OK)	
		
		elif action == 'edit_discount':
			#update payment policy and discount
			payment_method        = request.data.get('payment_method')
			discount_amount       = request.data.get('discount_amount')
			additional_charge     = request.data.get('additional_charge')

			old_payment_method    = order.evaluation.payment_method
			print(discount_amount,"discount_amount")
			if order.amount_paid == 0:
				if payment_method == 'PREPAID':
					order.evaluation.before_cleaning_amount = 0
					order.evaluation.after_cleaning_amount  = 0
					order.evaluation.payment_method         = 'PREPAID'

					order.evaluation.discount               = discount_amount
					order.evaluation.additional_charge      = additional_charge
					order.evaluation.total_cost             = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.total_amount                      = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.remining_amount                   = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
				
				elif payment_method == 'BREAKDOWN':
					before_cleaning_amount                  = request.data.get('before_cleaning_amount')
					after_cleaning_amount                   = request.data.get('after_cleaning_amount')
					order.evaluation.before_cleaning_amount = before_cleaning_amount
					order.evaluation.after_cleaning_amount  = after_cleaning_amount
					order.evaluation.payment_method         = 'BREAKDOWN'

					order.evaluation.discount                = discount_amount
					order.evaluation.additional_charge       = additional_charge
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.total_amount                       = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.remining_amount                    = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)

				elif payment_method == 'POSTPAID':
					order.evaluation.before_cleaning_amount = 0
					order.evaluation.after_cleaning_amount  = 0
					order.evaluation.payment_method         = 'POSTPAID'

					order.evaluation.discount                = discount_amount
					order.evaluation.additional_charge       = additional_charge
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.total_amount                       = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.remining_amount                    = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
				
				else:
					order.evaluation.discount                = discount_amount
					order.evaluation.additional_charge       = additional_charge
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.total_amount                       = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.remining_amount                    = (order.evaluation.estimated_cost-order.evaluation.cancelled_amount-order.evaluation.credit_amount-discount_amount+additional_charge)


				#to check payment completed
				if order.remining_amount == 0:
					order.payment_status = 'COMPLETED'

				if payment_method in ['PREPAID','POSTPAID','BREAKDOWN'] and order.evaluation.quatation_status == 'APPROVED':
					invoice_data = {}

					#Xero Integration
					xero          = XeroConnection.objects.first()
					#Update Access Token and Refresh Token
					header                      = {
													'Authorization': 'Basic '+xero.client_encoded,
													'Content-Type': 'application/x-www-form-urlencoded'
														}
					body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
					token_response              = requests.post('https://identity.xero.com/connect/token',
															data=body,
															headers=header 
														).json()
					access_token                = token_response['access_token']
					refresh_token               = token_response['refresh_token']

					xero.access_token  = access_token
					xero.refresh_token = refresh_token
					xero.save()

					##Xero Create Customer ID and Save
					contact_data                = {
													"Name":order.evaluation.customer.name,
													"ContactNumber":order.evaluation.customer.mobile_number,
													"EmailAddress":order.evaluation.customer.email,
													"ContactStatus":"ACTIVE",
													"IsCustomer":True,
													"DefaultCurrency":"KWD"
																}
													
					header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

					create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
															json=contact_data,
															headers=header 
														).json()

					order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
					order.evaluation.customer.save()	

					#Prepaid
					if payment_method == 'PREPAID':
						Amount = order.evaluation.total_cost 
						##Invoice Line Item 
						LineItems                 = []
						LineItems.append({
							"Description":"ONE TIME SERVICE",
							"Quantity":"1",
							"UnitAmount":Amount,
							"AccountCode":1207004,
							"TaxType":"NONE"
										}
							)
						InvoiceNumber  = order.invoice_no
						payment_policy = 'PREPAID'

						invoice_data       = 	{
													"Type":"ACCREC",
													"Contact":{
														"ContactID":order.evaluation.customer.xero_account_id
																},
													"Date":order.created.strftime('%Y-%m-%d'),
													"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
													"LineAmountTypes":"NoTax",
													"InvoiceNumber":InvoiceNumber,
													"Reference":order.order_no,
													"Status":"SUBMITTED",
													"LineItems":LineItems
													}

						##xero Create Invoice
						header                      = {
														'xero-tenant-id': xero.tenant_id,
														'Authorization': 'Bearer '+access_token,
														'Accept': 'application/json',
														'Content-Type': 'application/json'
															}

						create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																json=invoice_data,
																headers=header 
															).json()
				
						try:
							created_invoice = create_invoice['Status']
						except:
							created_invoice = None
						
						if created_invoice == 'OK':
							try:
								update_xero_invoice                  = XeroInvoice.objects.get(order=before_order,invoice_no=InvoiceNumber)
								update_xero_invoice.amount           = Amount
								update_xero_invoice.xero_marked_date = timezone.now().date()
								update_xero_invoice.payment_policy   = payment_policy
								update_xero_invoice.save()
							except:
								XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

							if old_payment_method == 'BREAKDOWN':
								#Remove Before
								##Invoice Line Item 
								LineItems                 = []
								LineItems.append({
									"Description":"ONE TIME SERVICE",
									"Quantity":"1",
									"UnitAmount":0,
									"AccountCode":1207004,
									"TaxType":"NONE"
												}
									)
								InvoiceNumber      = order.invoice_no+'A'
								invoice_data       = 	{
														"Type":"ACCREC",
														"LineAmountTypes":"NoTax",
														"InvoiceNumber":InvoiceNumber,
														"Reference":order.order_no,
														"LineItems":LineItems,
														"Status":"DRAFT"
														}

								##xero Create Invoice
								header                      = {
																'xero-tenant-id': xero.tenant_id,
																'Authorization': 'Bearer '+access_token,
																'Accept': 'application/json',
																'Content-Type': 'application/json'
																	}

								create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																		json=invoice_data,
																		headers=header 
																	).json()

								try:
									delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
									delete_invoice.delete()
								except:
									delete_invoice = None

					#Breakdown Before
					if payment_method == 'BREAKDOWN':
						Amount = order.evaluation.before_cleaning_amount 
						##Invoice Line Item 
						LineItems                 = []
						LineItems.append({
							"Description":"ONE TIME SERVICE",
							"Quantity":"1",
							"UnitAmount":Amount,
							"AccountCode":1207004,
							"TaxType":"NONE"
										}
							)
						InvoiceNumber  = order.invoice_no+'A'
						payment_policy = 'BEFORE CLEANING'

						invoice_data       = 	{
													"Type":"ACCREC",
													"Contact":{
														"ContactID":order.evaluation.customer.xero_account_id
																},
													"Date":order.created.strftime('%Y-%m-%d'),
													"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
													"LineAmountTypes":"NoTax",
													"InvoiceNumber":InvoiceNumber,
													"Reference":order.order_no,
													"Status":"SUBMITTED",
													"LineItems":LineItems
													}

						##xero Create Invoice
						header                      = {
														'xero-tenant-id': xero.tenant_id,
														'Authorization': 'Bearer '+access_token,
														'Accept': 'application/json',
														'Content-Type': 'application/json'
															}

						create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																json=invoice_data,
																headers=header 
															).json()
						print(create_invoice)
				
						try:
							created_invoice = create_invoice['Status']
						except:
							created_invoice = None
						
						if created_invoice == 'OK':
							try:
								update_xero_invoice                  = XeroInvoice.objects.get(order=before_order,invoice_no=InvoiceNumber)
								update_xero_invoice.amount           = Amount
								update_xero_invoice.xero_marked_date = timezone.now().date()
								update_xero_invoice.payment_policy   = payment_policy
								update_xero_invoice.save()
							except:
								XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

							if old_payment_method == 'PREPAID':
								#Remove
								##Invoice Line Item 
								LineItems                 = []
								LineItems.append({
									"Description":"ONE TIME SERVICE",
									"Quantity":"1",
									"UnitAmount":0,
									"AccountCode":1207004,
									"TaxType":"NONE"
												}
									)
								InvoiceNumber      = order.invoice_no
								invoice_data       = 	{
														"Type":"ACCREC",
														"LineAmountTypes":"NoTax",
														"InvoiceNumber":InvoiceNumber,
														"Reference":order.order_no,
														"LineItems":LineItems,
														"Status":"DRAFT"
														}

								##xero Create Invoice
								header                      = {
																'xero-tenant-id': xero.tenant_id,
																'Authorization': 'Bearer '+access_token,
																'Accept': 'application/json',
																'Content-Type': 'application/json'
																	}

								create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																		json=invoice_data,
																		headers=header 
																	).json()

								try:
									delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
									delete_invoice.delete()
								except:
									delete_invoice = None

					#Post Paid
					if payment_method == 'POSTPAID':
						if old_payment_method == 'PREPAID':
							#Remove
							##Invoice Line Item 
							LineItems                 = []
							LineItems.append({
								"Description":"ONE TIME SERVICE",
								"Quantity":"1",
								"UnitAmount":0,
								"AccountCode":1207004,
								"TaxType":"NONE"
											}
								)
							InvoiceNumber      = order.invoice_no
							invoice_data       = 	{
													"Type":"ACCREC",
													"LineAmountTypes":"NoTax",
													"InvoiceNumber":InvoiceNumber,
													"Reference":order.order_no,
													"LineItems":LineItems,
													"Status":"DRAFT"
													}

							##xero Create Invoice
							header                      = {
															'xero-tenant-id': xero.tenant_id,
															'Authorization': 'Bearer '+access_token,
															'Accept': 'application/json',
															'Content-Type': 'application/json'
																}

							create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																	json=invoice_data,
																	headers=header 
																).json()

							try:
								delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
								delete_invoice.delete()
							except:
								delete_invoice = None	

						if old_payment_method == 'BREAKDOWN':
							#Remove First Case
							##Invoice Line Item 
							LineItems                 = []
							LineItems.append({
								"Description":"ONE TIME SERVICE",
								"Quantity":"1",
								"UnitAmount":0,
								"AccountCode":1207004,
								"TaxType":"NONE"
											}
								)
							InvoiceNumber      = order.invoice_no+'A'
							invoice_data       = 	{
													"Type":"ACCREC",
													"LineAmountTypes":"NoTax",
													"InvoiceNumber":InvoiceNumber,
													"Reference":order.order_no,
													"LineItems":LineItems,
													"Status":"DRAFT"
													}

							##xero Create Invoice
							header                      = {
															'xero-tenant-id': xero.tenant_id,
															'Authorization': 'Bearer '+access_token,
															'Accept': 'application/json',
															'Content-Type': 'application/json'
																}

							create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
																	json=invoice_data,
																	headers=header 
																).json()

							try:
								delete_invoice = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
								delete_invoice.delete()
							except:
								delete_invoice = None

				order.evaluation.save()
				order.save()

				response_dict['success']  = True

		elif action == 'submit_quatation':
			#update payment policy and discount
			payment_method      = request.data.get('payment_method')
			discount_amount     = request.data.get('discount_amount')
			additional_charge   = request.data.get('additional_charge') 
			if order.amount_paid == 0:
				if payment_method == 'PREPAID':
					order.evaluation.before_cleaning_amount = 0
					order.evaluation.after_cleaning_amount  = 0
					order.evaluation.payment_method         = 'PREPAID'
					order.evaluation.quatation_status       = 'PENDING'

					order.evaluation.discount               = discount_amount
					order.evaluation.additional_charge      = additional_charge
					order.evaluation.total_cost             = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.total_amount                      = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.remining_amount                   = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
				
				elif payment_method == 'BREAKDOWN':
					before_cleaning_amount                  = request.data.get('before_cleaning_amount')
					after_cleaning_amount                   = request.data.get('after_cleaning_amount')
					order.evaluation.before_cleaning_amount = before_cleaning_amount
					order.evaluation.after_cleaning_amount  = after_cleaning_amount
					order.evaluation.payment_method         = 'BREAKDOWN'
					order.evaluation.quatation_status       = 'PENDING'

					order.evaluation.discount                = discount_amount
					order.evaluation.additional_charge       = additional_charge
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.total_amount                       = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.remining_amount                    = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)

				elif payment_method == 'POSTPAID':
					order.evaluation.before_cleaning_amount = 0
					order.evaluation.after_cleaning_amount  = 0
					order.evaluation.payment_method         = 'POSTPAID'
					order.evaluation.quatation_status       = 'PENDING'

					order.evaluation.discount                = discount_amount
					order.evaluation.additional_charge       = additional_charge
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.evaluation.total_cost              = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.total_amount                       = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
					order.remining_amount                    = (order.evaluation.estimated_cost-order.evaluation.credit_amount-discount_amount+additional_charge)
				
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
			schedule_id             = request.data.get('schedule_id')
			cleaning_schedule       = OrderScheduler.objects.get(id=schedule_id)

			cleaning_date 	   = request.data.get('cleaning_date')
			cleaning_time      = request.data.get('cleaning_time')
			cleaning_hours 	   = float(request.data.get('cleaning_hours'))
			start_at           = datetime.strptime(cleaning_date+' '+cleaning_time,'%d-%m-%Y %I:%M %p')
			end_at             = start_at + timedelta(hours=cleaning_hours)
			no_of_cleaners     = request.data.get('no_of_cleaners')
				
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

		elif action == 'cancell_cleaning':
			schedule_id             = request.data.get('schedule_id')
			reduction_status        = request.data.get('reduction_status')

			cleaning_schedule       = OrderScheduler.objects.select_related('order_scheduler_book','evaluation_details').get(id=schedule_id)

			if cleaning_schedule.order_scheduler_book.cleaning_policy == 'ONE TIME SERVICE':
				cleaning_schedule.delete()
			else:
				if reduction_status == True:
					reduction_amount        = int(request.data.get('reduction_amount'))

					order.evaluation.total_cost                             -= reduction_amount
					order.evaluation.cancelled_amount                       += reduction_amount
					order.total_amount                                      -= reduction_amount
					order.remining_amount                                   -= reduction_amount
										
					order.evaluation.save()
					order.save()


				cleaning_schedule.work_status = 'CLEANING_CANCELLED'
				cleaning_schedule.save()

			#delete cleaning team
			CleaningTeam.objects.filter(order_scheduler=cleaning_schedule).delete()

			#delete team member
			CleaningTeamMember.objects.filter(team__order_scheduler=cleaning_schedule).delete()
				
			response_dict['success']  = True
	
		elif action == 'evaluationbook_note':
			evaluationbook_id = request.data.get('evaluationbook_id')
			note              = request.data.get('note')

			#update book note
			EvaluationBook.objects.filter(id=evaluationbook_id).update(evaluator_note=note)

			response_dict['success']  = True

		elif action == 'evaluator_note':
			evaluator_note                  = request.data.get('evaluator_note')
			
			order.evaluation.evaluator_note = evaluator_note
			order.evaluation.save()
			
			response_dict['success']  = True

		elif action == 'evaluation_media':
			evaluationbook_id = request.data.get('evaluationbook_id')
			taken_status      = request.data.get('taken_status')
			medias            = request.FILES.getlist('media')

			if not medias==['']:
				for media in medias:
					EvaluationMedia.objects.create(
							evaluation_book_id=evaluationbook_id,
							media=media,
							media_type='PHOTO',
							taken_status=taken_status
							)
			
			response_dict['success'] = True

		elif action == 'add_backupteam':
			team_id               = request.data.get('team_id')
			backup_start_at       = datetime.strptime(request.data.get('backup_start_at'),'%d-%m-%Y %I:%M %p')
			backup_end_at         = datetime.strptime(request.data.get('backup_end_at'),'%d-%m-%Y %I:%M %p')
			backup_cleaners       = request.data.get('backup_cleaners')

			#create
			if backup_cleaners != []:
				cleaning_team         = CleaningTeam.objects.select_related('order_scheduler__evaluation_details').get(id=team_id)
				cleaning_teams        = CleaningTeam.objects.filter(order_scheduler__start_at=cleaning_team.order_scheduler.start_at,order_scheduler__end_at=cleaning_team.order_scheduler.end_at,order_scheduler__evaluation_details__evaluation=cleaning_team.order_scheduler.evaluation_details.evaluation)
				
				for cleaning_team in cleaning_teams:
					cleaning_team.backup_start_at =  backup_start_at
					cleaning_team.backup_end_at   =  backup_end_at
					cleaning_team.save()

					backup_cleaners_array = []
					for backup_cleaner in backup_cleaners:
						backup_cleaners_array.append(CleaningTeamMember(team=cleaning_team,member_id=backup_cleaner,start_at=backup_start_at,end_at=backup_end_at,start_time=backup_start_at.time(),end_time=backup_end_at.time(),is_backup_cleaner=True))
					CleaningTeamMember.objects.bulk_create(backup_cleaners_array)

			response_dict['success'] = True

		elif action == 'edit_backupteam':
			team_id               = request.data.get('team_id')
			backup_start_at       = datetime.strptime(request.data.get('backup_start_at'),'%d-%m-%Y %I:%M %p')
			backup_end_at         = datetime.strptime(request.data.get('backup_end_at'),'%d-%m-%Y %I:%M %p')
			backup_cleaners       = request.data.get('backup_cleaners')

			if backup_cleaners != []:
				#create
				cleaning_team         = CleaningTeam.objects.select_related('order_scheduler__evaluation_details').get(id=team_id)
				cleaning_teams        = CleaningTeam.objects.filter(order_scheduler__start_at=cleaning_team.order_scheduler.start_at,order_scheduler__end_at=cleaning_team.order_scheduler.end_at,order_scheduler__evaluation_details__evaluation=cleaning_team.order_scheduler.evaluation_details.evaluation)
				
				for cleaning_team in cleaning_teams:
					cleaning_team.backup_start_at =  backup_start_at
					cleaning_team.backup_end_at   =  backup_end_at
					cleaning_team.save()
					
					#delete
					CleaningTeamMember.objects.filter(team=cleaning_team,is_backup_cleaner=True).delete()

					#update
					backup_cleaners_array = []
					for backup_cleaner in backup_cleaners:
						backup_cleaners_array.append(CleaningTeamMember(team=cleaning_team,member_id=backup_cleaner,start_at=backup_start_at,end_at=backup_end_at,start_time=backup_start_at.time(),end_time=backup_end_at.time(),is_backup_cleaner=True))
					CleaningTeamMember.objects.bulk_create(backup_cleaners_array)
			else:
				#create
				cleaning_team         = CleaningTeam.objects.select_related('order_scheduler__evaluation_details').get(id=team_id)
				cleaning_teams        = CleaningTeam.objects.filter(order_scheduler__start_at=cleaning_team.order_scheduler.start_at,order_scheduler__end_at=cleaning_team.order_scheduler.end_at,order_scheduler__evaluation_details__evaluation=cleaning_team.order_scheduler.evaluation_details.evaluation)

				for cleaning_team in cleaning_teams:
					cleaning_team.backup_start_at =  None
					cleaning_team.backup_end_at   =  None
					cleaning_team.save()

					#delete
					CleaningTeamMember.objects.filter(team=cleaning_team,is_backup_cleaner=True).delete()



			response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)

class ServiceCancellationRequest(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		response_dict={}
		response_dict['success'] = False
		
		service_books            = request.data.get('service_books')
		requester_id             = request.data.get('requester_id')

		for book in service_books:
			EvaluationBook.objects.filter(id=book).update(status='CANCELL_IN_PROGRESS',cancell_requester_id=requester_id)
		
		evaluationbook = EvaluationBook.objects.get(id=service_books[0])
		response_dict['evaluation_id'] = evaluationbook.evaluation_details.evaluation.id
		print(response_dict,"resdict")

		response_dict['success'] = True
		
		return Response(response_dict,HTTP_200_OK)


class ServiceCancellation(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def post(self,request):
		response_dict={}
		response_dict['success'] = False
		
		cancelled_by             = request.data.get('cancelled_by')
		order_id                 = request.data.get('order_id')
		order                    = Order.objects.select_related('evaluation__customer').get(id=order_id)

		
		
		service_books            = request.data.get('service_books')

		for servicebook in service_books:
			service_id   = servicebook['id']
			action_type  = servicebook['action_type']
			
			service_book = EvaluationBook.objects.prefetch_related(Prefetch('order_scheduler_book_details',queryset=OrderScheduler.objects.filter(~Q(work_status='CLEANING_FULFILLED')),to_attr="schedules")).get(id=service_id)
				
			if action_type == 'CANCELL':
				service_book.status              = 'CANCELLED'
				service_book.cancelled_by__id    = cancelled_by
				
				for scheduler in service_book.schedules:
					scheduler.work_status = 'CLEANING_CANCELLED'
					scheduler.save()

			elif action_type == 'REJECT':
				service_book.status = None

			elif action_type == 'PAYBACK':
				service_book.status              = 'CANCELLED'
				service_book.cancelled_by__id    = cancelled_by
				amount                = float(servicebook['amount'])			
				
				cancell_order_history = CancellOrderAmountHistory.objects.create(order_id=order_id,return_amount=amount,amount_return_method='CASHBACK')

				for scheduler in service_book.schedules:
					scheduler.work_status = 'CLEANING_CANCELLED'
					scheduler.save()

			elif action_type == 'CREDIT':
				service_book.status              = 'CANCELLED'
				service_book.cancelled_by__id    = cancelled_by
				amount = float(servicebook['amount'])		

				CancellOrderAmountHistory.objects.create(order_id=order_id,return_amount=amount,amount_return_method='CREDIT',is_completed=True)
				
				order.evaluation.customer.credit_amount     += amount
				order.amount_paid                           -= amount
				
				order.evaluation.customer.save()
				order.save()
				for scheduler in service_book.schedules:
					scheduler.work_status = 'CLEANING_CANCELLED'
					scheduler.save()

			elif action_type == 'REDUCTION':
				service_book.status              = 'CANCELLED'
				service_book.cancelled_by__id    = cancelled_by
				amount                           = float(servicebook['amount'])

				order.evaluation.total_cost                             -= amount
				order.evaluation.cancelled_amount                       += amount
				order.total_amount                                      -= amount
				order.remining_amount                                   -= amount

				order.evaluation.save()
				order.save()
				for scheduler in service_book.schedules:
					scheduler.work_status = 'CLEANING_CANCELLED'
					scheduler.save()

			service_book.save()

		#Xero Invoice Updation
		order          = Order.objects.prefetch_related('order_scheduler_order').annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).get(id=order_id)
		payment_method = order.evaluation.payment_method

		if payment_method in ['PREPAID','POSTPAID','BREAKDOWN']:

			#Xero Integration
			xero          = XeroConnection.objects.first()
			#Update Access Token and Refresh Token
			header                      = {
											'Authorization': 'Basic '+xero.client_encoded,
											'Content-Type': 'application/x-www-form-urlencoded'
												}
			body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
			token_response              = requests.post('https://identity.xero.com/connect/token',
													data=body,
													headers=header 
												).json()
			access_token                = token_response['access_token']
			refresh_token               = token_response['refresh_token']

			xero.access_token  = access_token
			xero.refresh_token = refresh_token
			xero.save()	

			#Prepaid
			if payment_method == 'PREPAID' and order.evaluation.quatation_status == 'APPROVED':
				Amount = order.evaluation.total_cost 
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no
				payment_policy = 'PREPAID'

				invoice_data       = 	{
											"Type":"ACCREC",
											"Date":order.created.strftime('%Y-%m-%d'),
											"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
											"LineAmountTypes":"NoTax",
											"InvoiceNumber":InvoiceNumber,
											"Reference":order.order_no,
											"Status":"SUBMITTED",
											"LineItems":LineItems
											}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()
		
				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None
				
				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=before_order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

			#Breakdown Before
			if payment_method == 'BREAKDOWN' and order.evaluation.quatation_status == 'APPROVED':
				Amount = order.evaluation.before_cleaning_amount 
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no+'A'
				payment_policy = 'BEFORE CLEANING'

				invoice_data       = 	{
											"Type":"ACCREC",
											"Date":order.created.strftime('%Y-%m-%d'),
											"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
											"LineAmountTypes":"NoTax",
											"InvoiceNumber":InvoiceNumber,
											"Reference":order.order_no,
											"Status":"SUBMITTED",
											"LineItems":LineItems
											}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()
		
				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None
				
				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=before_order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
				
			#BREAKDOWN AFTER
			if payment_method == 'BREAKDOWN' and order.completed_cleaning_count == order.cleaning_count:
				Amount = order.evaluation.before_cleaning_amount 
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no+'B'
				payment_policy = 'BEFORE CLEANING'

				invoice_data       = 	{
											"Type":"ACCREC",
											"Date":order.created.strftime('%Y-%m-%d'),
											"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
											"LineAmountTypes":"NoTax",
											"InvoiceNumber":InvoiceNumber,
											"Reference":order.order_no,
											"Status":"SUBMITTED",
											"LineItems":LineItems
											}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()

				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None

				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=before_order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
			#POSTPAID
			if payment_method == 'POSTPAID' and order.completed_cleaning_count == order.cleaning_count:
				Amount = order.evaluation.before_cleaning_amount 
				##Invoice Line Item 
				LineItems                 = []
				LineItems.append({
					"Description":"ONE TIME SERVICE",
					"Quantity":"1",
					"UnitAmount":Amount,
					"AccountCode":1207004,
					"TaxType":"NONE"
								}
					)
				InvoiceNumber  = order.invoice_no
				payment_policy = 'BEFORE CLEANING'

				invoice_data       = 	{
											"Type":"ACCREC",
											"Date":order.created.strftime('%Y-%m-%d'),
											"DueDate":(order.created+timedelta(days=14)).strftime('%Y-%m-%d'),
											"LineAmountTypes":"NoTax",
											"InvoiceNumber":InvoiceNumber,
											"Reference":order.order_no,
											"Status":"SUBMITTED",
											"LineItems":LineItems
											}

				##xero Create Invoice
				header                      = {
												'xero-tenant-id': xero.tenant_id,
												'Authorization': 'Bearer '+access_token,
												'Accept': 'application/json',
												'Content-Type': 'application/json'
													}

				create_invoice              = requests.post('https://api.xero.com/api.xro/2.0/Invoices/',
														json=invoice_data,
														headers=header 
													).json()

				try:
					created_invoice = create_invoice['Status']
				except:
					created_invoice = None

				if created_invoice == 'OK':
					try:
						update_xero_invoice                  = XeroInvoice.objects.get(order=before_order,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
		
		response_dict['success'] = True
		
		return Response(response_dict,HTTP_200_OK)


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

class CartAPI(APIView):
	permission_classes        = (IsAuthenticated,)
	authentication_classes    = (TokenAuthentication,)

	def get(self,request,token):
		response_dict = {'success':False}

		user = Token.objects.get(key=token).user

		try:
			cart = CustomerCart.objects.get(customer=user)
		except:
			cart = CustomerCart.objects.create(customer=user)

		#cart discount calculation - 15% of cost upto 75KD
		# discount_amount = float(cart.total_cost) * (15/100)
		# cart.cart_discount = round(discount_amount if discount_amount <= 75 else 75,3)
		# cart.final_cost = round(float(cart.total_cost) - float(discount_amount if discount_amount <= 75 else 75),3)
		# cart.save()
		
		cart.cart_discount = 0
		cart.final_cost = 0 if float(cart.promocode_amount) >= float(cart.total_cost) else float(cart.total_cost)-float(cart.promocode_amount)
		cart.save()

		services = CartService.objects.filter(cart=cart)

		cart_services = CartServiceShowSerializer(services,many=True).data

		customer_data = UserProfileShowSerializer(user,many=False).data

		if cart.promocode:
			promocode = Promocode.objects.filter(promocode=cart.promocode,is_active=True).first()
			
			if promocode.percentage:
				if promocode.percentage_upto_price:
					response_dict['promocode_notes'] = str(cart.promocode_amount)+' KD ('+str(promocode.percentage)+'% off upto '+str(promocode.percentage_upto_price)+' KD)'
				else:
					response_dict['promocode_notes'] = str(cart.promocode_amount)+' KD ('+str(promocode.percentage)+'% off)'
			else:
				response_dict['promocode_notes'] = str(cart.promocode_amount)+' KD'

		response_dict['success'] = True
		response_dict['data'] = cart_services
		response_dict['customer'] = customer_data
		response_dict['cart_id'] = cart.id
		response_dict['cart_items_count'] = services.count()
		response_dict['no_of_visits'] = cart.no_of_visits
		response_dict['customer_ip_address'] = get_client_ip(request)
		response_dict['is_scheduled'] = cart.is_scheduled
		response_dict['discount_amount'] = cart.cart_discount
		response_dict['cart_final_cost'] = cart.final_cost
		response_dict['promocode'] = cart.promocode if cart.promocode else None

		return Response(response_dict,HTTP_200_OK)

	def post(self,request,token):
		response_dict = {'success':False}

		action = request.data.get('action')

		#get user from token
		user = Token.objects.get(key=token).user

		#get or create cart
		try:
			cart = CustomerCart.objects.get(customer=user)
		except:
			cart = CustomerCart.objects.create(customer=user,)

		#APPLY PROMOCODE TO CART TOTAL
		if action == 'apply_promocode':
			try:
				promocode = Promocode.objects.filter(promocode=request.data.get('promo_code'),is_active=True).first()
				
				#checking if promocode usage count is completed or date expired
				if promocode.total_usage == promocode.total_used or promocode.expiry_date <= date.today() :
					response_dict['message'] = 'PromoCode Expired'
				else:
					if promocode.percentage:
						percentage = promocode.percentage
						cart_amount = cart.total_cost
						promocode_amount = float(promocode.percentage/100) * float(cart_amount)

						if promocode.percentage_upto_price and promocode_amount > promocode.percentage_upto_price:
							promocode_amount = promocode.percentage_upto_price

					elif promocode.price:
						promocode_amount = promocode.price

					else:
						promocode_amount = 0

					cart.cart_discount = 0
					cart.promocode = request.data.get('promo_code')

					if float(promocode_amount) >= float(cart.total_cost):
						cart.promocode_amount = float(cart.total_cost)
						cart.final_cost = 0
					else:
						cart.promocode_amount = float(promocode_amount)
						cart.final_cost = float(cart.total_cost)-float(promocode_amount)
					cart.save()
					response_dict['message'] = 'PromoCode Applied'
					response_dict['success']  = True
			except:
				response_dict['message'] = 'PromoCode Does Not Exist'

		#remove promocode
		if action == 'remove_promocode':
			cart.promocode = None
			cart.final_cost = float(cart.final_cost)+float(cart.promocode_amount)
			cart.promocode_amount = 0
			cart.save()
			response_dict['success']  = True
			response_dict['message']  = 'PromoCode removed'

		#ADDING A NEW SERVICE
		if action == 'add_service':

			#saving service details through serializer
			service_data = request.data.get('service_data')

			service_data['cart'] = cart.id

			#getting service price through productivity id 
			if 'floors' in service_data:
				total_cost = 0			
			elif 'addon_price' in service_data:
				total_cost = ServiceAddOns.objects.get(id=request.data.get('productivity_id')).price
			else:
				total_cost = ServicePriceRange.objects.get(id=request.data.get('productivity_id')).price

			service_data['service_price_range'] = request.data.get('productivity_id')
			service_data['total_cost'] = total_cost

			service_data_serializer = CartServiceSerializer(data=service_data)

			if service_data_serializer.is_valid():

				service = service_data_serializer.save()

				#adding floor data
				if 'floors' in service_data:

					for floor in service_data['floors']:
						
						service_price_range = ServicePriceRange.objects.get(id=int(floor['productivity_id']))
						section_cost = service_price_range.price

						CartServiceFloor.objects.create(
							cartService=service,section_name = floor['section_name'], service_price_range=service_price_range,size= floor['size'], unit=floor['unit'], 
							bathrooms=floor['bathrooms'],rooms=floor['rooms'],windows=floor['windows'],wall_type=floor['wall_type'],
							ceiling_type=floor['ceiling_type'], floor_type=floor['floor_type'],section_cost=section_cost
						)

						total_cost += float(section_cost)
						
					service.total_cost = total_cost
					service.save()

				cart.total_cost = float(cart.total_cost)+float(total_cost)
				cart.save()

				#updating promocode amount and final cost
				if cart.promocode:
					promocode = Promocode.objects.filter(promocode=cart.promocode,is_active=True).first()
					
					#checking if promocode usage count is completed or date expired
					if promocode.total_usage == promocode.total_used or promocode.expiry_date <= date.today() :
						response_dict['message'] = 'PromoCode Expired'
					else:
						if promocode.percentage:
							percentage = promocode.percentage
							cart_amount = cart.total_cost
							promocode_amount = float(promocode.percentage/100) * float(cart_amount)

							if promocode.percentage_upto_price and promocode_amount > promocode.percentage_upto_price:
								promocode_amount = promocode.percentage_upto_price

						elif promocode.price:
							promocode_amount = promocode.price

						else:
							promocode_amount = 0

						if float(promocode_amount) >= float(cart.total_cost):
							cart.promocode_amount = float(cart.total_cost)
							cart.final_cost = 0
						else:
							cart.promocode_amount = float(promocode_amount)
							cart.final_cost = float(cart.total_cost)-float(promocode_amount)

						cart.save()

				response_dict['success']  = True				

			else:
				errors= service_data_serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['Error']=key +':'+ error[0]
				response_dict['Error_List'] = service_data_serializer.errors

		#UPDATING EXISTING SERVICE
		# if action == 'edit_service':

		# 	#saving service details through serializer
		# 	service_data = request.data.get('service_data')

		# 	service_data['cart'] = cart.id

		# 	#getting service price through productivity id 
		# 	total_cost = ServicePriceRange.objects.get(id=request.data.get('productivity_id')).price

		# 	service_data['service_price_range'] = request.data.get('productivity_id')
		# 	service_data['total_cost'] = total_cost

		# 	try:
		# 		#getting existing cart service object
		# 		cart_service = CartService.objects.get(id=request.data.get('cart_service_id'))
		# 		previous_service_cost = cart_service.total_cost

		# 		#updating cart service details using serializer
		# 		service_data_serializer = CartServiceSerializer(data=service_data,instance=cart_service)

		# 		if service_data_serializer.is_valid():
		# 			service = service_data_serializer.save()
						
		# 			service.total_cost = total_cost
		# 			service.save()

		# 			cart.total_cost = float(cart.total_cost) - float(previous_service_cost)
		# 			cart.total_cost = float(cart.total_cost) + float(total_cost)
		# 			cart.save()

		# 			response_dict['success']  = True					

		# 		else:
		# 			errors= service_data_serializer.errors   
		# 			key=tuple(errors.keys())[0] 
		# 			error=errors[key]
		# 			response_dict['Error']=key +':'+ error[0]
		# 			response_dict['Error_List'] = service_data_serializer.errors
		# 	except:
		# 		cart_service = None

		#DELETE SERVICE
		if action == 'delete_service':

			try:
				cart_service = CartService.objects.get(id=request.data.get('cart_service_id'))
				service_cost = cart_service.total_cost
				cart_service.delete()

				cart.total_cost = float(cart.total_cost) - float(service_cost)
				cart.save()

				#updating promocode amount and final cost
				if cart.promocode:
					promocode = Promocode.objects.filter(promocode=cart.promocode,is_active=True).first()
					
					#checking if promocode usage count is completed or date expired
					if promocode.total_usage == promocode.total_used or promocode.expiry_date <= date.today() :
						response_dict['message'] = 'PromoCode Expired'
					else:
						if promocode.percentage:
							percentage = promocode.percentage
							cart_amount = cart.total_cost
							promocode_amount = float(promocode.percentage/100) * float(cart_amount)

							if promocode.percentage_upto_price and promocode_amount > promocode.percentage_upto_price:
								promocode_amount = promocode.percentage_upto_price

						elif promocode.price:
							promocode_amount = promocode.price

						else:
							promocode_amount = 0
							
						if float(promocode_amount) >= float(cart.total_cost):
							cart.promocode_amount = float(cart.total_cost)
							cart.final_cost = 0
						else:
							cart.promocode_amount = float(promocode_amount)
							cart.final_cost = float(cart.total_cost)-float(promocode_amount)

						cart.save()

				response_dict['success']  = True
			except:
				cart_service = None

		#RESET CART SCHEDULES
		if action == 'reset_schedules':

			cartschedules = CartSchedule.objects.filter(cart=cart)

			#service total cost update
			cart_services = CartService.objects.filter(cart=cart)

			if cartschedules:
				for service in cart_services:
					service.total_cost = round(float(service.total_cost)/float(cartschedules.count()),3)
					service.save()

				cart.total_cost = round(float(cart.total_cost) / float(cartschedules.count()),3)
				cart.is_scheduled = False
				cart.no_of_visits = 0
				cart.save()

				cartschedules.delete()
			else:
				for service in cart_services:
					service.total_cost = service.total_cost
					service.save()

				cart.total_cost = cart.total_cost
				cart.is_scheduled = False
				cart.no_of_visits = 0
				cart.save()

			response_dict['success']  = True

		return Response(response_dict,HTTP_200_OK)

class FindDates(APIView):
    permission_classes     = (AllowAny,)
    authentication_classes = ()

    def post(self,request):
        response_dict = {"success":False}
        action        = request.data.get('action_type')
    
        #To check given a start date for weekly or list of dates for monthly
        current_date   = datetime.strptime(request.data.get('start_date'),'%d-%m-%Y').date()
        
        #Total Visits
        total_visits      = request.data.get('total_visits') 
        dates             = []


        if action == 'weekly':
            #Days(For Monday-0,Tuesday-2 etc)
            days              = request.data.get('days')
            
            while len(dates) != total_visits:
                #Append Date
                if current_date.weekday() in days:
                    current_week = current_date.isocalendar()[1]
                    dates.append(datetime.strftime(current_date,'%d-%m-%Y'))
                current_date  = current_date+timedelta(days=1)

        elif action == 'daily':
            #Days(For Monday-0,Tuesday-2 etc)
            days              = request.data.get('days')
            
            while len(dates) != total_visits:
                #Append Date
                dates.append(datetime.strftime(current_date,'%d-%m-%Y'))
                current_date  = current_date+timedelta(days=1)

        elif action == 'alternate_daily':
            #Days(For Monday-0,Tuesday-2 etc)
            days              = request.data.get('days')
            
            while len(dates) != total_visits:
                #Append Date
                dates.append(datetime.strftime(current_date,'%d-%m-%Y'))
                current_date  = current_date+timedelta(days=2)

        elif action ==  'alternate_weekly':
            #Days(For Monday-0,Tuesday-2 etc)
            days              = request.data.get('days')

            current_week      = current_date.isocalendar()[1]
            while len(dates) != total_visits:
                #To Skip a Week
                if current_week != current_date.isocalendar()[1]:
                    current_date = current_date+timedelta(days=7)
                    current_week = current_date.isocalendar()[1]
                
                #Append Date
                if current_date.weekday() in days:
                    dates.append(datetime.strftime(current_date,'%d-%m-%Y'))
                current_date  = current_date+timedelta(days=1)

        elif action == 'monthly':
            coming_days   = request.data.get('coming_days') 

            counter = 0
            while len(dates) != total_visits:
                new_dates = list(map(lambda coming_day:
                                datetime.strftime(current_date.replace(day=coming_day)+relativedelta(months=counter),'%d-%m-%Y') 
                                if current_date<=current_date.replace(day=coming_day)+relativedelta(months=counter) else None,
                                coming_days)) 
                new_dates = [new_date for new_date in new_dates if new_date]
                
                #Append Next Month Dates
                for new_date in new_dates:
                    if len(dates) != total_visits and new_date not in dates:
                        dates.append(new_date)
                    elif len(dates) == total_visits:
                        break

                counter      = counter+1

        response_dict['success']  = True
        response_dict['dates']    = dates
        
        return Response(response_dict, HTTP_200_OK)

class CartScheduleAPI(APIView):
	permission_classes        = (IsAuthenticated,)
	authentication_classes    = (TokenAuthentication,)

	def get(self,request,token):
		response_dict = {'success':False}
		user = Token.objects.get(key=token).user
		response_dict['var'] = user.id
		return Response(response_dict,HTTP_200_OK)

	def post(self,request,token):
		response_dict = {'success':False}

		user = Token.objects.get(key=token).user

		try:
			cart = CustomerCart.objects.get(customer=user)
		except:
			cart = CustomerCart.objects.create(customer=user)

		slots = request.data.get('datetimes')

		for slot in slots:
			
			#GETTING CLEANING SLOT DETAILS
			
			start_date_time         =  datetime.strptime(slot,'%d-%m-%Y %I:%M %p')
			end_date_time           =  start_date_time + timedelta(hours=int(request.data.get('cleaning_hours'))) 	
			start_time              =  start_date_time.time()
			end_time                =  end_date_time.time()

			#CREATING CART schedule
			cart_schedule = CartSchedule.objects.create(cart=cart,start_at=start_date_time,end_at=end_date_time,no_of_cleaners=request.data.get('no_of_cleaners'),cleaning_hours=request.data.get('cleaning_hours'))
		
		#service total cost update
		cart_services = CartService.objects.filter(cart=cart)

		for service in cart_services:
			if slots:
				if request.data.get('cleaning_policy') == 'SUBSCRIPTION':
					service.total_cost = round(float(service.total_cost)*float(len(slots)),3)
				else:
					service.total_cost = service.total_cost
			service.cleaning_policy = request.data.get('cleaning_policy')
			service.save()

		#cart total cost update
		cart.is_scheduled = True
		cart.no_of_visits = len(slots)
		if slots:
			if request.data.get('cleaning_policy') == 'SUBSCRIPTION':
				cart.total_cost = round(float(cart.total_cost) * float(len(slots)),3)
			else:
				cart.total_cost = cart.total_cost
		cart.save()

		response_dict['success'] = True
		if slots:
			if request.data.get('cleaning_policy') == 'SUBSCRIPTION':
				response_dict['updated_cost'] = round(float(cart.total_cost) * float(len(slots)),3)
			else:
				response_dict['updated_cost'] = cart.total_cost
		else:
			response_dict['updated_cost'] = cart.total_cost

		return Response(response_dict,HTTP_200_OK)