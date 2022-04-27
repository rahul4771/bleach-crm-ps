from django.shortcuts import render
import json
from django.template.loader import render_to_string
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule,Shift
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,EvaluationSectionAddons,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,Reporting,PaybackDiscount,PaybackDiscountDetails,XeroInvoice
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking
from bleachadmin.models import ServicePriceRange,Settings,ServiceProductivity,ServiceAddOns
from bleachadmin.serializers import ServiceProductivitySerializer
from Api.models import XeroConnection
from django.core.mail import send_mail,EmailMultiAlternatives
from Api.serializers import ServiceAddOnsSerializer,ServicePriceRangeSerializer,DiscountSettingSerializer,UserProfileSerializer, EvaluationSerializer, LeaveScheduleSerializer, UsersListSerializer,ShiftScheduleSerializer,OccupiedMembersSerializer,InventoryLineSerializer,InventorySegmentSerializer,InventoryValueSerializer,InventoryBundleItemSerializer,InventoryItemUnitSerializer,InventorySupplierItemSerializer
from agent.views import generate_random_username
from bleachinventory.models import QuantityStoreDetails,ExternalCustomer,Line,Segment,Category,Attribute,AttributeValue,Bundle,BundleItems,InventoryItem,ItemUnit,Supplier,SupplierItems,ServiceRecipe,ServiceRecipeIngredients,ServiceRecipeItems,CheckOutItems,CheckOutItemUnits,ItemHistory,InventoryAccessory,InventoryFinshedItem,Store
import re
import random
import string
import functools
import operator
import xlwt
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast,TruncDate,ExtractMonth,ExtractYear,Concat
from django.db.models import Prefetch
from dateutil.relativedelta import relativedelta
import pandas as pd
from googletrans import Translator
from datetime import date
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK 
from rest_framework import status
from rest_framework.authentication import TokenAuthentication 
from rest_framework.authtoken.models import Token

from agent.serializers import UserProfileShowSerializer


# Create your views here.
class ApiCheckSlote(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()
	
	def post(self,request):
		response_dict = {'success':False}
		
		evaluation_date = request.data.get('evaluation_date')
		try:
			evaluation_date = datetime.strptime(evaluation_date,'%d-%m-%Y')
		except:
			evaluation_date = timezone.now().replace(tzinfo=None)

		evaluation_date_start  = evaluation_date.replace(hour=0,minute=0,second=0,microsecond=0)
		evaluation_date_end    = evaluation_date_start+timedelta(1)

		evaluation_details = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').prefetch_related(Prefetch('evaluator_evaluation',queryset=EvaluationDetails.objects.filter(is_active=True).filter(Q(Q(proposed_time__gte=evaluation_date_start)&Q(proposed_time__lt=evaluation_date_end))),to_attr='evaluationdetails'))


		response_dict['freeslotes'] = {}

		if evaluation_details:
			counter = 1
			for evaluator in evaluation_details:
				if evaluator.evaluationdetails:

					#assigned times
					evaluator_timings_list = []				
					for evaluation in evaluator.evaluationdetails:
						registered_time_slote = evaluation.proposed_time+timedelta(hours=3)
						evaluator_timings_list.append(registered_time_slote.hour)
					
					#free times
					evaluator_freetimings_list = []
					for i in range(8,18):
						if i not in evaluator_timings_list:
							evaluator_freetimings_list.append(i)
					
					response_dict['freeslotes'][counter]= {'evaluator_details':{'name':evaluator.name,'id':evaluator.id},'slotes':evaluator_freetimings_list,}		
				else:
					response_dict['freeslotes'][counter]= {'evaluator_details':{'name':evaluator.name,'id':evaluator.id},'slotes':[8,9,10,11,12,13,14,15,16,17],}


				counter += 1

				response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)
		

class ApiBasicDetails(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		response_dict = {'success':False}
		serializer = UserProfileSerializer(data=request.data)

		if serializer.is_valid():   
			serializer.save(username=generate_random_username(),user_type='CUSTOMER')

			response_dict['success']  = True 
			response_dict['customer'] = serializer.data    
		else: 
		    errors= serializer.errors   
		    key=tuple(errors.keys())[0] 
		    error=errors[key]
		    response_dict['Error']=key +':'+ error[0]
		    response_dict['Error_List'] = serializer.errors

		return Response(response_dict,HTTP_200_OK)

class EvaluationBooking(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}

		evaluation_id = request.GET.get('evaluation_id')
		try:
			evaluation = Evaluation.objects.get(evaluation_id=evaluation_id)
		except:
			evaluation = None

		evaluation_serializer = EvaluationSerializer(evaluation,many=True).data
		response_dict["evaluations"]=evaluation_serializer
		return Response(response_dict,HTTP_200_OK)

class EvaluationUpdate(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):

		evaluation_date = request.GET.get('evaluation_date')
		evaluation_time = request.GET.get('evaluation_time')

		converted_datetime = datetime.strptime(evaluation_date+" "+evaluation_time,'%d-%m-%Y %I:%M %p')

		evaluator_id = request.GET.get('evaluator_id')
		evaluation_detail_id = request.GET.get('evaluation_detail_id')
		agent_notes = request.GET.get('agent_notes')
		print(converted_datetime,evaluator_id,agent_notes,evaluation_detail_id)

		evaluationdetail = EvaluationDetails.objects.get(id=int(evaluation_detail_id))
		evaluator = UserProfile.objects.get(id=int(evaluator_id),user_type='EVALUATOR')

		slot_count_check = EvaluationDetails.objects.filter(is_active=True,proposed_time=converted_datetime).count()

		if slot_count_check > 3:
			response_dict = {"success":False,"alert":"This slot is Filled. Please select another slot."}
		else:
			evaluationdetail.evaluator = evaluator
			evaluationdetail.proposed_time = converted_datetime
			evaluationdetail.attender_note = agent_notes
			evaluationdetail.save()
			
			response_dict = {"success":True}
		return Response(response_dict,HTTP_200_OK)



class EvaluationDetailsList(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,evaluation_detail_id):
		response_dict = {"success":False}

		print(evaluation_detail_id,"evid")
		try:
			evaluation_details = EvaluationDetails.objects.get(id=evaluation_detail_id)
			evaluators = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR').values('id','name')
		except:
			evaluators = None
			evaluation_details = None

		try:
			order = Order.objects.get(is_active=True,evaluation__id=evaluation_details.evaluation.id)
		except:
			order = None

		# print(evaluation_details.evaluation.evaluation_id,"evid")

		try:
			customer_booking = CustomerBooking.objects.get(booking_type='EVALUATIONBOOKING',evaluation__id=evaluation_details.evaluation.id)
			booking_id = customer_booking.booking_id
		except:
			booking_id = None
			customer_booking = None

		# address appending to single item
		if evaluation_details.address.floor  == None and evaluation_details.address.avenue  == None:
			address_list = [evaluation_details.address.apartment, evaluation_details.address.street, evaluation_details.address.building, evaluation_details.address.block, evaluation_details.address.area.name, evaluation_details.address.governorate.name]
		
		elif evaluation_details.address.floor  == None:
			address_list = [evaluation_details.address.apartment, evaluation_details.address.street, evaluation_details.address.building, evaluation_details.address.avenue, evaluation_details.address.block, evaluation_details.address.area.name, evaluation_details.address.governorate.name]
		
		elif evaluation_details.address.avenue  == None:
			address_list = [evaluation_details.address.apartment, evaluation_details.address.floor, evaluation_details.address.street, evaluation_details.address.building, evaluation_details.address.block, evaluation_details.address.area.name, evaluation_details.address.governorate.name]
		
		else:
			address_list = [evaluation_details.address.apartment, evaluation_details.address.floor, evaluation_details.address.street, evaluation_details.address.building, evaluation_details.address.avenue, evaluation_details.address.block, evaluation_details.address.area.name, evaluation_details.address.governorate.name]

		separator = ", "

		proposed_time = evaluation_details.proposed_time+timedelta(hours=3)
		proposed_date = evaluation_details.proposed_time+timedelta(hours=3)
		print(proposed_time.strftime('%I:%M %p'),proposed_date.strftime('%d-%m-%Y'),"evs")
		
		response_dict["booking_id"]=booking_id 
		response_dict["evaluators_list"]=evaluators 
		response_dict["evaluation_id"]=evaluation_details.evaluation.id 
		response_dict["evaluation_detail_id"]=evaluation_details.id 
		response_dict["area"]=evaluation_details.address.area.name 
		response_dict["evaluator"]=evaluation_details.evaluator.name 
		response_dict["evaluator_id"]=evaluation_details.evaluator.id
		response_dict["evaluation_status"]=evaluation_details.status

		if evaluation_details.evaluation.call_attender:
			response_dict["agent"]=evaluation_details.evaluation.call_attender.name 
		
		if evaluation_details.status == 'EVALUATED':
			response_dict["blc_number"]=evaluation_details.evaluation.evaluation_id
		
		if order:
			response_dict["order_id"]=order.id
		else:
			response_dict["order_id"]=0
			
		response_dict["agent_notes"]=evaluation_details.attender_note
		response_dict["customer"]=evaluation_details.evaluation.customer.name 
		response_dict["customer_mobile"]=evaluation_details.evaluation.customer.mobile_number 
		response_dict["location"]=evaluation_details.address.location 
		response_dict["customer_address"]=separator.join(address_list)
		response_dict["evaluation_date"]=proposed_date.strftime('%d-%m-%Y')
		response_dict["evaluation_time"]=proposed_time.strftime('%I:%M %p')
		response_dict["evaluation_slot"]=proposed_time.strftime('%H:%M')
		response_dict["agent_evaluation_notes"]=evaluation_details.attender_note 
		
		response_dict['success'] = True
		
		return Response(response_dict,HTTP_200_OK)


class CallbackStatusUpdate(APIView):
	def get(self,request):

		order_id = request.GET.get('order_id')
		order_callback_status = request.GET.get('callback_status')
		print(order_id,order_callback_status,"rog")

		try:
			order = Order.objects.get(id=int(order_id),is_active=True)
			order.callback_status = order_callback_status
			order.save()
			response_dict = {"success":True}
		except:
			order = None
			response_dict = {"success":False}

		return Response(response_dict,HTTP_200_OK)


class PaymentResponseCredit(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		evaluation_id = request.POST.get('req_merchant_defined_data1')
		payment_mode  = request.POST.get('req_merchant_defined_data2')
		amount_paid   = float(request.POST.get('req_amount'))
		order_status  = request.POST.get("req_merchant_defined_data3")

		try:
			order = Order.objects.select_related('evaluation').get(order_no=evaluation_id)
		except:
			order = None


		payment_result = request.POST.get('decision')
		
		if order and payment_result == 'ACCEPT' and order_status != 'CANCEL_IN_PROGRESS':
			#Receipt Number
			receipt_no               = PaymentHistory.objects.filter(is_active=True,receipt_no__isnull=False).aggregate(t=Max('receipt_no'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_receipt_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_receipt_starting == int(str(receipt_no)[:4]):
				new_receipt_no = int(receipt_no)+1
			else:
				new_receipt_no = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')	

			#payment history
			payment_history = PaymentHistory.objects.create(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.POST.get('echeck_debit_ref_no'),ref=request.POST.get('payer_authentication_xid'),track_id=request.POST.get('req_reference_number'),transaction_id=request.POST.get('transaction_id'),receipt_no=new_receipt_no,payment_gateway='CREDITCARD')

			#payment calculations
			if payment_mode == 'subscription':
				order.amount_paid      += amount_paid
				order.remining_amount   = order.remining_amount-amount_paid
				order.subscription_topay= 0
				order.is_advance        = False
				#to check payment completed
				if order.remining_amount == 0:
					order.payment_status         = 'COMPLETED'
					order.payment_completed_date = timezone.now()

			elif payment_mode == 'before_cleaning' and order.preamount_paid != order.evaluation.before_cleaning_amount:
				order.preamount_paid   = amount_paid
				order.amount_paid      = amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

			elif payment_mode == 'after_cleaning' and order.postamount_paid != order.evaluation.after_cleaning_amount:
				order.postamount_paid   += amount_paid
				order.amount_paid       += amount_paid
				order.remining_amount    = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'prepaid' and order.amount_paid != order.total_amount:
				order.amount_paid     += amount_paid
				order.remining_amount  = order.remining_amount-amount_paid					

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()

			elif payment_mode == 'postpaid' and order.amount_paid != order.total_amount:
				order.amount_paid      += amount_paid
				order.remining_amount  = order.remining_amount-amount_paid

				order.payment_status         = 'COMPLETED'
				order.payment_completed_date = timezone.now()
			order.save()

			# xero          = XeroConnection.objects.first()
			# #Update Access Token and Refresh Token
			# header                      = {
			# 								'Authorization': 'Basic '+xero.client_encoded,
			# 								'Content-Type': 'application/x-www-form-urlencoded'
			# 									}
			# body                        = {"grant_type":"refresh_token","refresh_token":xero.refresh_token}
			# token_response              = requests.post('https://identity.xero.com/connect/token',
			# 										data=body,
			# 										headers=header 
			# 									).json()
			# access_token                = token_response['access_token']
			# refresh_token               = token_response['refresh_token']

			# xero.access_token  = access_token
			# xero.refresh_token = refresh_token
			# xero.save()

			# ##Xero Contact
			# if not order.evaluation.customer.xero_account_id:

			# 	##Xero Create Customer ID and Save
			# 	contact_data                = {
			# 									"Name":order.evaluation.customer.name,
			# 									"ContactNumber":order.evaluation.customer.mobile_number,
			# 									"EmailAddress":order.evaluation.customer.email,
			# 									"ContactStatus":"ACTIVE",
			# 									"IsCustomer":True,
			# 									"DefaultCurrency":"KWD"
			# 												}
												
			# 	header                      = {
			# 								'xero-tenant-id': xero.tenant_id,
			# 								'Authorization': 'Bearer '+access_token,
			# 								'Accept': 'application/json',
			# 								'Content-Type': 'application/json'
			# 									}

			# 	create_contact             = requests.post('https://api.xero.com/api.xro/2.0/Contacts/',
			# 											json=contact_data,
			# 											headers=header 
			# 										).json()

			# 	order.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
			# 	order.evaluation.customer.save() 

			# #Xero Transaction
			# header                      = {
			# 							'xero-tenant-id': xero.tenant_id,
			# 							'Authorization': 'Bearer '+access_token,
			# 							'Accept': 'application/json',
			# 							'Content-Type': 'application/json'
			# 								}

			# ##Transaction Data
			# transaction_data            = {
			# 								"Type": "RECEIVE-OVERPAYMENT",
			# 								"Reference": order.evaluation.evaluation_id,
			# 								"Date":datetime.strftime(timezone.now(),'%Y-%m-%d'),
			# 								"Contact": {
			# 									"ContactID": order.evaluation.customer.xero_account_id,
			# 								},
			# 								"LineItems": [{
			# 									"Description": "CREDITCARD",
			# 									"UnitAmount": amount_paid,
			# 									"AccountCode": "610",
			# 									"TaxType":"NONE"
			# 								}],
			# 								"BankAccount": {
			# 									"Code": "1201023"
			# 								}
			# 								}
											
			# update_transaction          = requests.post('https://api.xero.com/api.xro/2.0/BankTransactions',
			# 										json=transaction_data,
			# 										headers=header 
			# 									)

			# ##Transaction Bank Charge Data
			# transaction_bankcharge_data = {
			# 								"Type": "SPEND",
			# 								"Reference": order.evaluation.evaluation_id,
			# 								"Date":datetime.strftime(timezone.now(),'%Y-%m-%d'),
			# 								"Contact": {
			# 									"ContactID": order.evaluation.customer.xero_account_id,
			# 								},
			# 								"LineItems": [{
			# 									"Description": "Bank Charge",
			# 									"UnitAmount": (amount_paid*.025),
			# 									"AccountCode": "3202014",
			# 									"TaxType":"NONE"
			# 								}],
			# 								"BankAccount": {
			# 									"Code": "1201023"
			# 								}
			# 								}
											
			# update_transaction_bankcharge          	= requests.post('https://api.xero.com/api.xro/2.0/BankTransactions',
			# 											json=transaction_bankcharge_data,
			# 											headers=header 
			# 											)
		
			# try:
			# 	created_transaction = update_transaction['Status']
			# except:
			# 	created_transaction = None

			# if created_transaction == 'OK':
			# 	payment_history.is_xero_marked = True
			# 	payment_history.save()

			#payment receipt sms
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

			####to close order
			order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,order_no=evaluation_id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter( Q( Q(cleaning_count=F('completed_cleaning_count')) & Q(followup_count=F('completed_followup_count')) & ~Q(cleaning_count=0) ) )
			if order_closing_check:
				closing_order	= Order.objects.get(is_active=True,order_no=evaluation_id)
				closing_order.order_status = 'ORDER_CLOSED'
				closing_order.save()

			try:
				booking_completed = CustomerBooking.objects.filter(evaluation=evaluation).update(is_bookingcompleted=True)
			except:
				booking_completed = None

		elif order and payment_result == 'ACCEPT' and order_status == 'CANCEL_IN_PROGRESS':
			#Receipt Number
			receipt_no               = PaymentHistory.objects.filter(is_active=True,receipt_no__isnull=False).aggregate(t=Max('receipt_no'))['t'] or int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10000')
			current_receipt_starting = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2))

			if current_receipt_starting == int(str(receipt_no)[:4]):
				new_receipt_no = int(receipt_no)+1
			else:
				new_receipt_no = int(str(timezone.now().year)[-2:]+str(timezone.now().month).zfill(2)+'10001')

			#payment history
			payment_history = PaymentHistory.objects.create(order=order,amount_paid=amount_paid,payment_mode='ONLINECREDIT',paid_date=timezone.now(),payment_id=request.POST.get('echeck_debit_ref_no'),ref=request.POST.get('payer_authentication_xid'),track_id=request.POST.get('req_reference_number'),transaction_id=request.POST.get('transaction_id'),receipt_no=new_receipt_no,payment_gateway='CREDITCARD')

			order.remining_amount  = 0
			order.amount_paid     += amount_paid
			order.save()
			
		return Response(HTTP_200_OK)	

#get list of staff for leave scheduler
class UsersList(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}

		try:
			staffs = UserProfile.objects.filter(is_active=True).filter(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER')).order_by('name')
		except:
			staffs = None
		
		staff_serializer = UsersListSerializer(staffs,many=True).data
		response_dict["staffs"]=staff_serializer

		return Response(response_dict,HTTP_200_OK)

#get existing leave schedules and add new leaveschedules
class LeaveScheduleAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}
		month = int(request.GET.get('month'))
		year  = int(request.GET.get('year'))

		try:
			leaveschedules = LeaveSchedule.objects.filter(is_active=True,leave_date__month=month,leave_date__year=year).order_by('leave_type')

			leaveschedules = leaveschedules.values('id','staff__id','leave_type','leave_date')
			leaveschedules_df = pd.DataFrame(list(leaveschedules))

			newdf1 = leaveschedules_df.drop_duplicates(
				subset = ['staff__id', 'leave_date'],
				keep = 'first').reset_index(drop = True)
			newdf1 = newdf1.to_dict(orient='records')
		except:
			leaveschedules = None
			newdf1 = []

		occupied_members           = CleaningTeamMember.objects.select_related('team__order_scheduler').filter( Q(Q(is_active=True) & Q(Q(Q(start_at__month=month)&Q(start_at__year=year)) | Q(Q(end_at__month=month)&Q(end_at__year=year))) ) )
		occupied_member_serializer = OccupiedMembersSerializer(occupied_members,many=True).data

		response_dict["staffs"]    = newdf1
		response_dict["occupied"]  = occupied_member_serializer

		return Response(response_dict,HTTP_200_OK)
	
	def post(self,request):
		print("yahhoo")
		response_dict = {'success':False}

		leave_dates_list = []
		bamboo_employee_id = None

		for schedule in request.data:

			serializer = LeaveScheduleSerializer(data=schedule)
			
			if serializer.is_valid(): 
				serializer.save()

				#save leave to bamboo
				staff_details = UserProfile.objects.get(id=int(schedule['staff']))

				bamboo_employee_id = staff_details.bamboo_employee_id

				headers = {
						"Content-Type": "application/json",
						"Authorization": "Basic NDNhMjE5Y2ZlNmYyZGJlMjUwYTllYjdiNWUyNzc0MzM1YzE0Njg1ODo="
					}

				if bamboo_employee_id:

					add_leave_url = "https://api.bamboohr.com/api/gateway.php/bleachkw/v1/employees/"+bamboo_employee_id+"/time_off/request"

					timeOffTypeId = '92'

					payload = {
						"status": "approved",
						"start": schedule['leave_date'],
						"end": schedule['leave_date'],
						"timeOffTypeId": timeOffTypeId,
						"amount" : 1
					}

					print(add_leave_url,payload,"loadss")

					leave_response = requests.request("PUT", add_leave_url, json=payload, headers=headers)

					# if leave_response:

					# 	url = "https://api.bamboohr.com/api/gateway.php/bleachkw/v1/time_off/requests/?start="+leave_date+"&end="+leave_date+"&employeeId="+bamboo_employee_id+"&type="+timeOffTypeId+"&status=approved"

					# 	response = requests.request("GET", url, headers=headers)
					# 	print(response.json(),"jesso")

						

					# 		# leaveschedules = LeaveSchedule.objects.filter(is_active=True,bamboo_leave_id=item['id'])
					# 		# serializer.save()

				response_dict['success']  = True  
			else: 
				errors= serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['Error']=key +':'+ error[0]
				response_dict['Error_List'] = serializer.errors

		return Response(response_dict,HTTP_200_OK)


class LeaveSchedulePopupAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		
		staff_id  	    = request.GET.get('staff_id')
		try:
			occupied_date   = datetime.strptime(request.GET.get('occupied_date'),'%Y-%m-%d')
		except:
			occupied_date   = None

		try:
			cleaning_members = CleaningTeamMember.objects.select_related('team__order_scheduler__order').filter(Q(Q(start_at__date=occupied_date)|Q(end_at__date=occupied_date))&Q(member__id=staff_id))
		except:
			cleaning_members = None

		if cleaning_members:
			response_dict['detials']      = []
			for cleaning_member in cleaning_members:
				details                   = {}
				details['id']             = cleaning_member.team.order_scheduler.id
				details['blc']            = cleaning_member.team.order_scheduler.order.order_no
				details['start_at']       = datetime.strftime(cleaning_member.team.order_scheduler.start_at+timedelta(hours=3),'%d-%m-%Y %H:%M %p')
				details['cleaning_hours'] = cleaning_member.team.order_scheduler.cleaning_hours

				response_dict['detials'].append(details)

		response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)


#Get Existing Shift and add new shift
class ShiftScheduleAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}
		month = int(request.GET.get('month'))
		year  = int(request.GET.get('year'))

		try:
			shiftschedules = ShiftSchedule.objects.filter(is_active=True).filter(Q(Q(shift_date__month=month)&Q(shift_date__year=year))|Q(Q(shift3_start_at__month=month)&Q(shift3_start_at__year=year)))
		except:
			shiftschedules = None

		shiftschedule_serializer = ShiftScheduleSerializer(shiftschedules,many=True).data

		try:
			leaveschedules           = LeaveSchedule.objects.filter( Q(Q(is_active=True) & ~Q(leave_type='ANNUAL LEAVE') & Q(Q(leave_date__month=month)&Q(leave_date__year=year)) ) )
		except:
			leaveschedules           = None

		leaveschedule_serializer   = LeaveScheduleSerializer(leaveschedules,many=True).data

		response_dict["staffs"]    = shiftschedule_serializer
		response_dict["leaves"]    = leaveschedule_serializer
		response_dict["success"]   = True

		return Response(response_dict,HTTP_200_OK)

	def post(self,request):
		response_dict = {'success':False}

		for schedule in request.data:
			print(schedule)
			if schedule['shift1']:
				shift1_start_at  = Shift.objects.get(shift='SHIFT1').start_at
				shift1_end_at    = Shift.objects.get(shift='SHIFT1').end_at
			else:
				shift1_start_at  = None
				shift1_end_at    = None
			
			if schedule['shift2']:
				shift2_start_at = Shift.objects.get(shift='SHIFT2').start_at
				shift2_end_at   = Shift.objects.get(shift='SHIFT2').end_at
			else:
				shift2_start_at = None
				shift2_end_at   = None

			serializer = ShiftScheduleSerializer(data=schedule)
			
			
			if serializer.is_valid():
				serializer.save(shift1_start_at=shift1_start_at,shift2_start_at=shift2_start_at,shift1_end_at=shift1_end_at,shift2_end_at=shift2_end_at)
			else: 
				errors= serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['Error']=key +':'+ error[0]
				response_dict['Error_List'] = serializer.errors

		response_dict['success']  = True  

		return Response(response_dict,HTTP_200_OK)


class CancelEvaluation(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,evaluation_detail_id):
		response_dict = {'success':False}

		try:
			evaluation = EvaluationDetails.objects.get(is_active=True,id=int(evaluation_detail_id))
		except:
			evaluation = None

		print(evaluation_detail_id,evaluation,"lop")
		if evaluation:
			evaluation.status = 'CANCELLED'
			evaluation.save()
			response_dict = {'success':True}  
			return Response(response_dict, HTTP_200_OK)
		else:
			response_dict['reason'] = 'Invalid Id' 

		return Response(response_dict,HTTP_200_OK)



class DeleteLeaveSchedule(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,leave_id):
		response_dict = {'success':False}

		try:
			leaveschedule = LeaveSchedule.objects.get(is_active=True,id=int(leave_id))
		except:
			leaveschedule = None

		if leaveschedule:
			bamboo_employee_id = leaveschedule.staff.bamboo_employee_id
			start_date = leaveschedule.leave_date
			end_date = leaveschedule.leave_date
			print(bamboo_employee_id,start_date,end_date,"datprint")

			leaveschedule.delete()  

			#updating leave status on bamboo hr
				
			headers = {
				"Accept": "application/json",
				"Authorization": "Basic NDNhMjE5Y2ZlNmYyZGJlMjUwYTllYjdiNWUyNzc0MzM1YzE0Njg1ODo="
			}

			#get time off request id
			timeoff_url = "https://api.bamboohr.com/api/gateway.php/bleachkw/v1/time_off/requests/?employeeId="+bamboo_employee_id+"&start="+str(start_date)+"&end="+str(end_date)+""

			timeoffid_response = requests.request("GET", timeoff_url, headers=headers)

			data = timeoffid_response.json()

			print(data[0]['id'],"datar")

			#cancel timeoff status
			url = "https://api.bamboohr.com/api/gateway.php/bleachkw/v1/time_off/requests/"+data[0]['id']+"/status"
			payload = {
				"status": "cancelled",
			}

			headers = {
				"Content-Type": "application/json",
				"Authorization": "Basic NDNhMjE5Y2ZlNmYyZGJlMjUwYTllYjdiNWUyNzc0MzM1YzE0Njg1ODo="
			}

			print(url,payload,"loadss")

			response = requests.request("PUT", url, json=payload, headers=headers)

			response_dict['success'] = True

			return Response(response_dict, HTTP_200_OK)
		else:
			response_dict['reason'] = 'Invalid Id' 

		return Response(response_dict,HTTP_200_OK)


class DeleteShiftSchedule(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,shift_id):
		response_dict = {'success':False}

		try:
			shiftscehdule = ShiftSchedule.objects.get(is_active=True,id=int(shift_id))
		except:
			shiftschedule = None

		if shiftscehdule:
			shiftscehdule.delete()
			response_dict = {'success':True}  
			return Response(response_dict, HTTP_200_OK)
		else:
			response_dict['reason'] = 'Invalid Id' 

		return Response(response_dict,HTTP_200_OK)


class OrderDetailsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,order_id):
		visits = OrderScheduler.objects.filter(is_active=True,order__id=int(order_id))
		response_dict = {'success':False}
		print(visits,"vst")

		visits_list = []
		
		for visit in visits:
			visit_dict = {
				'order_no' : visit.order.order_no,
				'visit_id' : visit.id,
				'start_at' : datetime.strftime(visit.start_at+timedelta(hours=3),'%d-%m-%Y %I:%M %p')
			}
			visits_list.append(visit_dict)

		response_dict['visits'] = visits_list

		return Response(response_dict,HTTP_200_OK)

class TicketSubmitAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		visit_id = request.data.get('visit_id')
		ticket_types = request.data.get('ticket_types')
		notes = request.data.get('notes')
		investigationmedias = request.FILES.getlist('media')
		assigned_by = request.data.get('assigned_by')
		
		actions = request.data.get('actions')
		actions_list = actions.split(",")
			
		print(visit_id,ticket_types,notes,investigationmedias,"lodat")
		
		visit = OrderScheduler.objects.get(id=int(visit_id))
		order = visit.order
		
		assigned_by_user = UserProfile.objects.get(id=int(assigned_by),is_active=True)

		investigation = Investigation.objects.create(order=order,order_schedule=visit,notes=notes,ticket_types=ticket_types,assigned_by=assigned_by_user,scheduled_at=timezone.now())

		FollowUp.objects.create(investigation=investigation,status='TICKET_RISED')

		#save media
		investigation_medias = request.FILES.getlist('media')
		if not investigation_medias == ['']:
			for image in investigation_medias:
				InvestigationMedia.objects.create(
					investigation = investigation,
					media = image,
					media_type = 'PHOTO',
					taken_status = 'CUSTOMER_SEND',
					is_active = True
				)

		for action in actions_list:
			print(action,"act")
			if action == 'Payback':
				print("pop")
				paybackdiscount = PaybackDiscount.objects.create(investigation=investigation,is_active=True)

				paybackdiscount_items = request.data.getlist('paybackdiscount_items')
				print(paybackdiscount_items,"itms")
				item_array = []
				items_total_cost = 0
				for item in paybackdiscount_items:
					items_list = item.split(",")

					if items_list[2] == 'Service Quality':
						category = 'SERVICEQUALITY'
					elif items_list[2] == 'Damage':
						category = 'DAMAGE'
					else:
						category = None

					item_array.append(PaybackDiscountDetails(paybackdiscount=paybackdiscount,category=category,name=items_list[0],cost=items_list[1],is_active=True))

					items_total_cost += float(items_list[1])

				#bulk_create keynote
				PaybackDiscountDetails.objects.bulk_create(item_array)

				paybackdiscount.total_cost = items_total_cost
				paybackdiscount.save()

				#Email
				salesadmin_list = UserProfile.objects.filter(is_active=True).filter(is_active=True,user_type='SALESADMIN').values_list('email',flat=True)
				msg_html = render_to_string('email/ticketapprove.html',{'paybackdiscount':paybackdiscount,'email_user':'salesadmin'})
				msg      = EmailMultiAlternatives('Cash Back Approval', '', 'notification@bleach-kw.com', salesadmin_list)
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)

				admin_list = UserProfile.objects.filter(is_active=True).filter(is_active=True,user_type='ADMIN').values_list('email',flat=True)
				msg_html = render_to_string('email/ticketapprove.html',{'paybackdiscount':paybackdiscount,'email_user':'admin'})
				msg      = EmailMultiAlternatives('Cash Back Approval', '', 'notification@bleach-kw.com', admin_list)
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)

			if action == 'Internal Report':
				print("int rep")
				title = request.data.get('title')
				notes = request.data.get('report_note')

				Reporting.objects.create(investigation=investigation,title=title,notes=notes)

			if action == 'Assign Investigator':
				print(request.data.get('secondary_investigator'),"assign")
				secondary_investigator = request.data.get('secondary_investigator')
				print(secondary_investigator,"sec")
				investigator = UserProfile.objects.get(id=int(secondary_investigator))

				# investigationdata = Investigation.objects.select_related('investigator','assigned_by','secondary_investigator','order__evaluation__customer').get(id=investigation.id,is_active=True)
				investigation.investigator = investigator
				investigation.secondary_investigation_created = datetime.now()
				investigation.save()
				
				# msg_html = render_to_string('email/rise_ticket_request2.html',{'investigationdata':investigationdata})
				# msg      = EmailMultiAlternatives('Ticket Rised', '', 'notification@bleach-kw.com', [investigationdata.investigator.email])
				# msg.attach_alternative(msg_html, "text/html")
				# msg.send(fail_silently=False)
			
			investigation.is_casesandcomplaints_submit = True
			investigation.save()

		response_dict = {'success':True}

		return Response(response_dict,HTTP_200_OK)

class TicketEditAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		followup_id = request.data.get('followup_id')
		
		ticket_types = request.data.get('ticket_types')
		notes = request.data.get('notes')
		investigationmedias = request.FILES.getlist('media')
		assigned_by = request.data.get('assigned_by')
		
		actions = request.data.get('actions')
		actions_list = actions.split(",")
			
		print(ticket_types,notes,investigationmedias,"lodat")
		
		assigned_by_user = UserProfile.objects.get(id=int(assigned_by),is_active=True)

		# investigation = Investigation.objects.create(order=order,order_schedule=visit,notes=notes,ticket_types=ticket_types,assigned_by=assigned_by_user,scheduled_at=timezone.now())

		followup = FollowUp.objects.get(id=int(followup_id))
		investigation = followup.investigation
		InvestigationMedia.objects.filter(investigation=investigation).delete()
		
		#save media
		investigation_medias = request.FILES.getlist('media')
		if not investigation_medias == ['']:
			for image in investigation_medias:
				InvestigationMedia.objects.create(
					investigation = followup.investigation,
					media = image,
					media_type = 'PHOTO',
					taken_status = 'CUSTOMER_SEND',
					is_active = True
				)

		for action in actions_list:
			print(action,"act")
			if action == 'Payback':
				print("pop")
				
				payback_discount_id = request.data.get('paybackdiscount_id')
				if payback_discount_id:
					paybackdiscount = PaybackDiscount.objects.get(id=int(payback_discount_id),investigation=investigation,is_active=True)
				else:
					paybackdiscount = PaybackDiscount.objects.create(investigation=investigation,is_active=True)

				PaybackDiscountDetails.objects.filter(paybackdiscount=paybackdiscount).delete()

				paybackdiscount_items = request.data.getlist('paybackdiscount_items')
				print(paybackdiscount_items,"itms")
				item_array = []
				items_total_cost = 0
				for item in paybackdiscount_items:
					items_list = item.split(",")

					if items_list[2] == 'Service Quality':
						category = 'SERVICEQUALITY'
					elif items_list[2] == 'Damage':
						category = 'DAMAGE'
					else:
						category = None

					item_array.append(PaybackDiscountDetails(paybackdiscount=paybackdiscount,category=category,name=items_list[0],cost=items_list[1],is_active=True))

					items_total_cost += float(items_list[1])

				#bulk_create keynote
				PaybackDiscountDetails.objects.bulk_create(item_array)

				paybackdiscount.total_cost = items_total_cost
				paybackdiscount.save()

				#Email
				salesadmin_list = UserProfile.objects.filter(is_active=True).filter(is_active=True,user_type='SALESADMIN').values_list('email',flat=True)
				msg_html = render_to_string('email/ticketapprove.html',{'paybackdiscount':paybackdiscount,'email_user':'salesadmin'})
				msg      = EmailMultiAlternatives('Cash Back Approval', '', 'notification@bleach-kw.com', salesadmin_list)
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)

				admin_list = UserProfile.objects.filter(is_active=True).filter(is_active=True,user_type='ADMIN').values_list('email',flat=True)
				msg_html = render_to_string('email/ticketapprove.html',{'paybackdiscount':paybackdiscount,'email_user':'admin'})
				msg      = EmailMultiAlternatives('Cash Back Approval', '', 'notification@bleach-kw.com', admin_list)
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)

			if action == 'Internal Report':
				print("int rep")
				title = request.data.get('title')
				notes = request.data.get('report_note')

				Reporting.objects.create(investigation=investigation,title=title,notes=notes)

			if action == 'Assign Investigator':
				secondary_investigator = request.data.get('secondary_investigator')
				print(secondary_investigator,"sec")
				investigator = UserProfile.objects.get(id=int(secondary_investigator))

				# investigationdata = Investigation.objects.select_related('investigator','assigned_by','secondary_investigator','order__evaluation__customer').get(id=investigation.id,is_active=True)
				investigation.investigator = investigator
				investigation.secondary_investigation_created = datetime.now()
				investigation.save()
				
				# msg_html = render_to_string('email/rise_ticket_request2.html',{'investigationdata':investigationdata})
				# msg      = EmailMultiAlternatives('Ticket Rised', '', 'notification@bleach-kw.com', [investigationdata.investigator.email])
				# msg.attach_alternative(msg_html, "text/html")
				# msg.send(fail_silently=False)

			investigation.is_casesandcomplaints_submit = True
			investigation.ticket_types = ticket_types
			investigation.save()

		response_dict = {'success':True}

		return Response(response_dict,HTTP_200_OK)

class InvestigationFormAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		investigation_id = request.data.get('investigation_id')
		print(investigation_id,"invest")
		investigation = Investigation.objects.get(id=int(investigation_id))
		
		secondary_investigation_notes = request.data.get('notes')

		investigation.secondary_investigation_notes = secondary_investigation_notes
		investigation.is_secondary_investigation_completed = True
		investigation.save()
		
		#save media
		secondary_investigationmedias = request.FILES.getlist('media')
		if not secondary_investigationmedias == ['']:
			for image in secondary_investigationmedias:
				InvestigationMedia.objects.create(
					investigation = investigation,
					media = image,
					media_type = 'PHOTO',
					taken_status = 'SECONDARY_INVESTIGATION',
					is_active = True
				)

		followup = FollowUp.objects.get(investigation=investigation,is_active=True)
		followup.status = 'FOLLOWUP_IN_PROGRESS'
		followup.save()

		is_followup = request.data.get('is_followup')

		print(is_followup,"foll")

		if is_followup == 'True':
			print('vaaa')

			total_cost	= request.data.get('total_cost')
			no_of_cleaners = request.data.get('number_of_cleaners')
			cleaning_hours = request.data.get('cleaning_hours')
			
			# tendative_date = request.data.get('tendative_date')

			# tendative_time = request.data.get('tendative_time')

			sections = request.data.get('sections')
			sections = json.loads(sections)

			print(sections,"secs")
			# for section in sections:
			# 	section = dict(section)
			# 	print(section.section_name,"lol")

			print(sections,"secs")

			follow_up = FollowUp.objects.select_related('investigation__order__evaluation__customer').get(investigation_id=investigation_id,is_active=True)
			follow_up.status         = 'FOLLOWUP_IN_PROGRESS'
			# follow_up.followup_notes = request.POST.get('investigator_notes')
			follow_up.no_of_cleaners = no_of_cleaners
			follow_up.cleaning_hours = cleaning_hours
			follow_up.total_cost = total_cost
			follow_up.save()

			# start_date_time = datetime.strptime(tendative_date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
			# end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))

			# for date in tendative_date:
			# 	print(date+' '+tendative_time,"tod")
			# 	start_date_time = datetime.strptime(date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
			# 	end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))
			# 	followup_schedule_array.append(FollowUpScheduler(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address))


			# 	#to save sections
			for section in sections:

				try:
					section_name_arabic = Translator().translate(section['section_name'],src='en', dest='ar').text
				except:
					section_name_arabic = section['section_name']

				new_section = FollowUpSection.objects.create(follow_up=follow_up,section_name=section['section_name'],section_name_arabic=section_name_arabic,size=section['size'],wall_type=section['wall_type'],ceiling_type=section['ceiling_type'],floor_type=section['floor_type'],cause_of_stain=section['cause_of_stain'],material=section['material'],colour=section['color'],age=section['age'],section_net_cost=section['section_net_cost'])
		
				keynote_array = []
				for keynote in section['keynotes']:
					
					keynote_array.append(FollowUpSectionKeynote(followup_section=new_section,sub_area=keynote['sub_area'],quantity=keynote['quantity']))

				FollowUpSectionKeynote.objects.bulk_create(keynote_array)
		

			# FollowUpScheduler.objects.create(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address)

			investigation.is_followup_approved = True
			investigation.save()
			
		response_dict = {'success':True}

		return Response(response_dict,HTTP_200_OK)

class AgentInvestigationChecckAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		investigation_id = request.data.get('investigation_id')

		investigation = Investigation.objects.get(id=int(investigation_id))

		followup = FollowUp.objects.get(investigation=investigation,is_active=True)
		
		tendative_date = request.data.get('tendative_date')

		tendative_time = request.data.get('tendative_time')

		print(tendative_date,tendative_time,"secs")

		start_date_time = datetime.strptime(tendative_date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
		end_date_time   = start_date_time + timedelta(hours=float(followup.cleaning_hours))		

		FollowUpScheduler.objects.create(follow_up=followup,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address)
			
		investigation.is_agent_approved = True
		investigation.save()

		response_dict = {'success':True}

		return Response(response_dict,HTTP_200_OK)

class VisitDetailsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,visit_id):
		response_dict = {'success':False}
		print(visit_id,"oid")
		# try:
		visit = OrderScheduler.objects.select_related('order_scheduler_book','customer_address__area','customer_address__governorate').prefetch_related(Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='evaluationbooksectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections'),Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_team')).get(is_active=True,id=int(visit_id))
		# except:
		#  	visit = None

		response_dict['order_no'] = visit.order.order_no
		response_dict['visit_id'] = visit_id
		response_dict['customer_name'] = visit.order.evaluation.customer.name
		response_dict['customer_number'] = visit.order.evaluation.customer.mobile_number
		response_dict['amount'] = visit.order_scheduler_book.total_cost
		response_dict['order_amount'] = visit.order.total_amount
		response_dict['order_paid_amount'] =visit.order.amount_paid
		response_dict['order_remaining_amount'] = visit.order.remining_amount
		response_dict['payment_status'] = visit.order.payment_status

		response_dict['servicetype'] = visit.order_scheduler_book.service_type.name
		response_dict['cleaning_policy'] = visit.order_scheduler_book.cleaning_policy
		response_dict['start_at'] = datetime.strftime(visit.start_at+timedelta(hours=3),'%d-%m-%Y %I:%M %p')
		response_dict['no_of_cleaners'] = visit.no_of_cleaners

		for team in visit.cleaning_team:
			print(team,"tm")
			response_dict['team_leader'] = team.team_leader.name
			response_dict['team_leader_image'] = team.team_leader.profile_image.url

			members = []
			for member in team.cleaning_team_members:
				members_dict= {
					'member' : member.member.name,
					'member_image' : member.member.profile_image.url
				}
				
				members.append(members_dict)

			response_dict['members'] = members

		sections = []
		for section in visit.order_scheduler_book.sections:
			
			keynotes = []
			for keynote in section.evaluationbooksectionkeynotes:
				keynote_dict = {
					'keynote_id' : keynote.id,
					'sub_area' : keynote.sub_area,
					'quantity' : keynote.quantity
				}
				keynotes.append(keynote_dict)

			sectionaddons = []
			for addon in section.sectionaddons:
				addon_dict = {
					'addon_id' : addon.id,
					'addon_name' : addon.name,
					'quantity' : addon.quantity,
					'addon_net_cost' : addon.addon_net_cost
				}
				sectionaddons.append(addon_dict)

			section_dict= {
					'section_id' : section.id,
					'section_name' : section.section_name,
					'age' : section.age,
					'size' : section.size,
					'floor_type' : section.floor_type,
					'wall_type' : section.wall_type,
					'ceiling_type' : section.ceiling_type,
					'section_net_cost' :section.section_net_cost,
					'upholstery_type' : section.upholstery_type,
					'oil_residue' : section.oil_residue,
					'cement_residue' : section.cement_residue,
					'new_kitchen' : section.new_kitchen,
					'is_cabinet' : section.is_cabinet,
					'is_highprice_facade' : section.is_highprice_facade,
					'is_highprice_window' : section.is_highprice_window,
					'vacuuming' : section.vacuuming,
					'age_of_stain' : section.age_of_stain,
					'color' : section.colour,
					'material' : section.material,
					'cause_of_stain' : section.cause_of_stain,
					'keynotes' : keynotes,
					'addons' : sectionaddons
			}

			sections.append(section_dict)

		response_dict['sections'] = sections
		print(response_dict,"dict")

		return Response(response_dict,HTTP_200_OK)

class TicketDetailsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,ticket_id):
		response_dict = {'success':False}
		print("pop")
		# try:
		followup_details = FollowUp.objects.select_related('investigation__investigator','investigation__order','investigation__order_schedule__customer_address__area','investigation__order_schedule__customer_address__governorate','investigation__order_schedule__order_scheduler_book').prefetch_related(Prefetch('investigation__investigation_media',queryset=InvestigationMedia.objects.filter(is_active=True,taken_status = 'CUSTOMER_SEND'),to_attr='investigationmedias'),Prefetch('investigation__paybackdiscount_investigation',queryset=PaybackDiscount.objects.filter(is_active=True).prefetch_related(Prefetch('paybackdiscount_details',queryset=PaybackDiscountDetails.objects.filter(is_active=True),to_attr='paybackdiscountdetails')),to_attr='paybackdiscounts'),Prefetch('investigation__reporting_investigation',queryset=Reporting.objects.filter(is_active=True),to_attr='reports')).get(is_active=True,id=ticket_id)
		# except:
		#  	visit = None
		print(followup_details,"pop2")

		paybackdiscounts = []
		report_list = []

		if followup_details.investigation.paybackdiscounts:
			
			is_paybackdiscount = True

			for discount in followup_details.investigation.paybackdiscounts:
				response_dict['paybackdiscount_id'] = discount.id

				for detail in discount.paybackdiscountdetails:
					print(detail,"diss")
					discount_dict = {
						'discount_id':detail.id,
						'category':detail.category,
						'name':detail.name,
						'cost':detail.cost
					}
					paybackdiscounts.append(discount_dict)

		else:
			is_paybackdiscount = False
			response_dict['paybackdiscount_id'] = None

		if followup_details.investigation.reports:
			is_report = True
			for report in followup_details.investigation.reports:
				report_dict = {
					'report_id':report.id,
					'title':report.title,
					'notes':report.notes
				}
				report_list.append(report_dict)

		else:
			is_report = False

		if followup_details.investigation.investigator:
			is_investigator = True
			response_dict['investigator_name'] = followup_details.investigation.investigator.name
			response_dict['investigator_id'] = followup_details.investigation.investigator.id
		else:
			is_investigator = False

		medias = []
		if followup_details.investigation.investigationmedias:
			
			for media in followup_details.investigation.investigationmedias:
				medias.append(media.media.url)
		
		response_dict['is_paybackdiscount'] = is_paybackdiscount
		response_dict['is_report'] = is_report
		response_dict['is_investigator'] = is_investigator
		response_dict['followup_id'] = followup_details.id
		response_dict['ticket_types'] = followup_details.investigation.ticket_types
		response_dict['notes'] = followup_details.investigation.notes
		response_dict['medias'] = medias
		response_dict['assigned_by'] = str(followup_details.investigation.assigned_by.id)
		response_dict['paybackdiscounts'] = paybackdiscounts
		response_dict['report'] = report_list
		 	
		print(response_dict,"dictio")

		return Response(response_dict,HTTP_200_OK)

class DailySalesAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		print("heers")
		response_dict = {'success':False}

		today = datetime.now()

		sales_month = request.GET.get('sales_month')
		data_type = request.GET.get('datatype')
		print(sales_month,data_type,"smonthlist")

		month,year = sales_month.split("/")
		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)-relativedelta(days=1)
		daterange  = pd.date_range(monthdate1, monthdate2)

		full_month_name = monthdate1.strftime("%B")
		print(daterange,"dr")
		
		#adding evaluator names to list for table header
		evaluators = UserProfile.objects.filter(is_active=True,user_type='EVALUATOR')
		evaluators_list = []
		for evaluator in evaluators:
			evaluators_list.append(str(evaluator.name)+str(evaluator.id))

		saleslist = []
		evaluator_list_monthly = []

		# generalcleaning_month = 0
		# upholsterycleaning_month = 0
		# deepcleaning_month = 0
		# carpetcleaning_month = 0
		# kitchencleaning_month = 0
		# sterilization_month = 0
		cleaning_amount_month = 0

		detailed_cleaning_month = 0
		special_care_month = 0
		kitchen_cleaning_month = 0
		infection_control_month = 0

		todate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

		for date in daterange:
			start_date_day = date
			end_date_day   = date+timedelta(1)-timedelta(minutes=1)

			print(date.strftime("%A"),"dt")
			
			cleaning_amount = 0
			evaluator_amount = 0
			others = 0

			detailed_cleaning = 0
			special_care = 0
			kitchen_cleaning = 0
			infection_control = 0

			list_item = {}
		
			for evaluator in evaluators:
				eval_dict = {""+str(evaluator.name)+str(evaluator.id)+"":0}
				list_item.update(eval_dict)

			print(list_item,"elist")
			
			if date < todate:
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q( Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','cleaning_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluator__id').order_by('end_at')
			else:
			 	orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','cleaning_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluator__id').order_by('end_at')

			print(orderschedules.count(),"countt")
			
			found = set()
			schedules_list = []

			for schedule in orderschedules:

				#if schedule[4] not in found:
				schedules_list.append(schedule)
				#found.add(schedule[4])

			for schedule in schedules_list:
				if schedule[1] == None:
					order_amount = 0
				else:
					order_amount = schedule[1]

				#schedule count of order
				order_schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0]).count()

				#schedule count of evaluation book
				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()
				
				cleaning_amount += float(order_amount)
				
				#fine,promocode, write off calc
				# if schedule[6] > 0:
				# 	cleaning_amount -= float(schedule[6]/order_schedule_count)
				# if schedule[7] > 0:
				# 	cleaning_amount -= float(schedule[7]/order_schedule_count)
				# if schedule[8] > 0:
				# 	cleaning_amount += float(schedule[8]/order_schedule_count)
				# if schedule[10] > 0:
				# 	cleaning_amount -= float(schedule[10]/order_schedule_count)
				# if schedule[11] > 0:
				# 	cleaning_amount += float(schedule[11]/order_schedule_count)

				#adding amount to evaluators dict
				if schedule[6] != None:
					for x, y in list_item.items():
						evaluator_id = int(re.search(r'\d+', x).group(0))
						print(evaluator_id,"loll")
						if int(evaluator_id) == int(schedule[6]):
							print("evade",evaluator_id)
							evaluator_amount += float(order_amount)

							#fine,promocode, write off calc
							# if schedule[6] > 0:
							# 	evaluator_amount -= float(schedule[6]/order_schedule_count)
							# if schedule[7] > 0:
							# 	evaluator_amount -= float(schedule[7]/order_schedule_count)
							# if schedule[8] > 0:
							# 	evaluator_amount += float(schedule[8]/order_schedule_count)
							# if schedule[10] > 0:
							# 	evaluator_amount -= float(schedule[10]/order_schedule_count)
							# if schedule[11] > 0:
							# 	evaluator_amount += float(schedule[11]/order_schedule_count)
							

							eval_dict = {""+x+"":evaluator_amount}
							print(date,eval_dict,"evdict")
					list_item.update(eval_dict)
				else:
					others += float(order_amount)

					#fine,promocode, write off calc
					# if schedule[6] > 0:
					# 	others -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	others -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	others += float(schedule[8]/order_schedule_count)	
					# if schedule[10] > 0:
					# 	others -= float(schedule[10]/order_schedule_count)
					# if schedule[11] > 0:
					# 	others += float(schedule[11]/order_schedule_count)
					
				
				#cleaning type wise amount addition
				if schedule[2] == 'General Cleaning':
					detailed_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	detailed_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	detailed_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	detailed_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Deep Cleaning':
					detailed_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	detailed_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	detailed_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	detailed_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Facade Cleaning':
					detailed_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	detailed_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	detailed_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	detailed_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Storage Area':
					detailed_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	detailed_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	detailed_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	detailed_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Car Parking Umbrella':
					detailed_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	detailed_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	detailed_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	detailed_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Window Cleaning':
					detailed_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	detailed_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	detailed_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	detailed_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Outdoor Cleaning':
					detailed_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	detailed_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	detailed_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	detailed_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Upholstery Cleaning':
					special_care += float(order_amount)

					# if schedule[6] > 0:
					# 	special_care -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	special_care -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	special_care += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	special_care -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Mattress Cleaning':
					special_care += float(order_amount)

					# if schedule[6] > 0:
					# 	special_care -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	special_care -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	special_care += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	special_care -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Carpet Cleaning':
					special_care += float(order_amount)

					# if schedule[6] > 0:
					# 	special_care -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	special_care -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	special_care += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	special_care -= float(schedule[10]/order_schedule_count)
					

				

				# if schedule[2] == 'Upholstery Cleaning':
				# 	upholsterycleaning += float(order_amount/schedule_count)

				# 	if schedule[6] != None:
				# 		upholsterycleaning -= float(schedule[6]/schedule_count)
				# 	if schedule[7] != None:
				# 		upholsterycleaning -= float(schedule[7]/schedule_count)
				# 	if schedule[8] != None:
				# 		upholsterycleaning += float(schedule[8]/schedule_count)

				# if schedule[2] == 'Deep Cleaning':
				# 	deepcleaning += float(order_amount/schedule_count)

				# 	if schedule[6] != None:
				# 		deepcleaning -= float(schedule[6]/schedule_count)
				# 	if schedule[7] != None:
				# 		deepcleaning -= float(schedule[7]/schedule_count)
				# 	if schedule[8] != None:
				# 		deepcleaning += float(schedule[8]/schedule_count)

				if schedule[2] == 'Kitchen Cleaning':
					kitchen_cleaning += float(order_amount)

					# if schedule[6] > 0:
					# 	kitchen_cleaning -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	kitchen_cleaning -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	kitchen_cleaning += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	kitchen_cleaning -= float(schedule[10]/order_schedule_count)
					

				# if schedule[2] == 'Carpet Cleaning':
				# 	carpetcleaning += float(order_amount/schedule_count)

				# 	if schedule[6] != None:
				# 		carpetcleaning -= float(schedule[6]/schedule_count)
				# 	if schedule[7] != None:
				# 		carpetcleaning -= float(schedule[7]/schedule_count)
				# 	if schedule[8] != None:
				# 		carpetcleaning += float(schedule[8]/schedule_count)
				
				if schedule[2] == 'Sterilization':
					infection_control += float(order_amount)

					# if schedule[6] > 0:
					# 	infection_control -= float(schedule[6]/order_schedule_count)
					# if schedule[7] > 0:
					# 	infection_control -= float(schedule[7]/order_schedule_count)
					# if schedule[8] > 0:
					# 	infection_control += float(schedule[8]/order_schedule_count)
					# if schedule[10] > 0:
					# 	infection_control -= float(schedule[10]/order_schedule_count)
					
			
			
			if data_type == 'service':
				list_item = {
					'Date': str(date.date()),
					'Day': date.strftime("%A"),
					'DetailedCleaning':detailed_cleaning,
					'SpecialCare':special_care,
					'KitchenCleaning':kitchen_cleaning,
					'InfectionControl':infection_control,
					'Total':cleaning_amount
				}
			else:
				evaluator_list_monthly.append(list_item)
				list_item.update( {
					'Date': str(date.date()),
					'Day': date.strftime("%A"),
					'others':others,
					'Total':cleaning_amount
				} )

			saleslist.append(list_item) #cleaningtype list append

			detailed_cleaning_month += detailed_cleaning
			special_care_month += special_care
			kitchen_cleaning_month += kitchen_cleaning
			infection_control_month += infection_control
			# carpetcleaning_month += carpetcleaning
			# sterilization_month += sterilization
			cleaning_amount_month += cleaning_amount

				
		response_dict = {'success':True,'datatype':data_type,'list':saleslist,'list2':evaluators_list,'list3':evaluator_list_monthly, 'todate':str(today.date()),'month_name':full_month_name,'detailed_cleaning_month':detailed_cleaning_month,'special_care_month':special_care_month,'kitchen_cleaning_month':kitchen_cleaning_month,'infection_control_month':infection_control_month,'cleaning_amount_month':cleaning_amount_month}

		return Response(response_dict,HTTP_200_OK)


class DailySalesBreakDownAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		print("heers")
		response_dict = {'success':False}

		todate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

		sales_date = request.GET.get('sales_date')
		sales_date = datetime.strptime(sales_date,'%d-%m-%Y')
		sales_day_name = sales_date.strftime("%A")

		start_date_day = sales_date.replace(hour=0,minute=0,second=0,microsecond=0)
		end_date_day   = start_date_day+timedelta(1)
		end_date_day   = end_date_day.replace(hour=0,minute=0,second=0,microsecond=0)
		
		print(start_date_day,end_date_day,"smonthlist")
	
		if start_date_day < todate:
			orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q( Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).order_by('end_at')
		else:
			orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).order_by('end_at')

		print(orderschedules,"countt")
		
		saleslist = []

		total_day_sales = 0

		for schedule in orderschedules:
			#schedule count of order
			order_schedule_count = OrderScheduler.objects.filter(order__order_no=schedule.order.order_no).count()

			#schedule count of evaluation book
			schedule_count = OrderScheduler.objects.filter(order__order_no=schedule.order.order_no,order_scheduler_book__id=schedule.order_scheduler_book.id).count()

			# order_amount     = schedule.cleaning_cost
			if schedule.cleaning_cost:
				cleaning_amount  = float(schedule.cleaning_cost)
			else:
				cleaning_amount  = 0
			#fine,promocode, write off calc
			# if schedule.order.evaluation.promocode_amount > 0:
			# 	cleaning_amount -= float(schedule.order.evaluation.promocode_amount/order_schedule_count)
			# if schedule.order.evaluation.writeback_amount > 0:
			# 	cleaning_amount -= float(schedule.order.evaluation.writeback_amount/order_schedule_count)
			# if schedule.order.evaluation.fine_amount > 0:
			# 	cleaning_amount += float(schedule.order.evaluation.fine_amount/order_schedule_count)
			# if schedule.order.evaluation.discount > 0:
			# 	cleaning_amount -= float(schedule.order.evaluation.discount/order_schedule_count)
			# if schedule.order.evaluation.additional_charge > 0:
			# 	cleaning_amount += float(schedule.order.evaluation.additional_charge/order_schedule_count)

			total_day_sales += float(cleaning_amount)			

			schedule_dict = {
				'order_no' : schedule.order.order_no,
				'customer'	: schedule.order.evaluation.customer.name,
				'payment_policy' : schedule.order.evaluation.payment_method,
				'net_amount' : cleaning_amount,
				'service_type' : schedule.order_scheduler_book.service_type.name,
				'salesman' : schedule.order.evaluation.call_attender.name
			}

			saleslist.append(schedule_dict)

		sales_status = float(2000) - float(total_day_sales)
	
		response_dict = {'success':True,'list':saleslist,'total_day_sales':total_day_sales,'sales_status':sales_status,'day':sales_day_name}

		return Response(response_dict,HTTP_200_OK)


class DailySalesChartAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {'success':False}
		todate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

		sales_month = request.GET.get('sales_month')
		print(sales_month,"smonth")

		month,year = sales_month.split("/")

		monthdate1 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)
		monthdate2 = datetime(day=1,month=int(month),year=int(year),hour=0,minute=0,second=0,microsecond=0)+relativedelta(months=1)-relativedelta(days=1)
		daterange  = pd.date_range(monthdate1, monthdate2)
		print(daterange,"dr")

		saleslist = []

		for date in daterange:
			start_date_day = date
			end_date_day   = date+timedelta(1)

			print(date.strftime("%A"),"dt")

			cleaning_amount = 0

			if date < todate:
			# 	print(date,"dtER")
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q( Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','cleaning_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id').order_by('end_at')
			else:
			 	orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','cleaning_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id').order_by('end_at')
			
			found = set()
			schedules_list = []

			for schedule in orderschedules:

				# if schedule[4] not in found:
				schedules_list.append(schedule)
				# found.add(schedule[4])
			# print(found,schedules_list,"kio")

			for schedule in schedules_list:
				if schedule[1] == None:
					order_amount = 0
				else:
					order_amount = schedule[1]

				order_schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0]).count()

				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()

				cleaning_amount += float(order_amount)

				# if schedule[5] > 0:
				# 	cleaning_amount -= float(schedule[5]/order_schedule_count)
				# if schedule[6] > 0:
				# 	cleaning_amount -= float(schedule[6]/order_schedule_count)
				# if schedule[7] > 0:
				# 	cleaning_amount += float(schedule[7]/order_schedule_count)
				# if schedule[8] > 0:
				# 	cleaning_amount -= float(schedule[8]/order_schedule_count)
			
			list_item = {
				'date': str(date.date()),
				'totalamount':cleaning_amount
			}

			saleslist.append(list_item)

				
		response_dict = {'success':True,'list':saleslist}

		return Response(response_dict,HTTP_200_OK)

class PaymentPolicyEditAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		
		evaluation_id 			= request.GET.get('evaluation_id')
		payment_method 			= request.GET.get('payment_method')
		before_cleaning_amount	= float(request.GET.get('before_cleaning_amount')or 0)
		after_cleaning_amount	= float(request.GET.get('after_cleaning_amount')or 0)

		print(evaluation_id,payment_method,before_cleaning_amount,after_cleaning_amount,"amts")

		#update payment method
		Evaluation.objects.filter(id=evaluation_id,is_active=True).update(payment_method=payment_method,before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount)
		
		response_dict = {'success':True}

		return Response(response_dict,HTTP_200_OK)

class CleaningTeamAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def get(self,request):

		visit_count = request.GET.get('visit_count')
		schedule_id = request.GET.get('schedule_id')

		cleaningteam = CleaningTeam.objects.filter(is_active=True,order_scheduler__id=int(schedule_id)).prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')).first()

		if cleaningteam:
			cleaning_start_at = (cleaningteam.order_scheduler.start_at+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
			cleaning_end_at   = (cleaningteam.order_scheduler.end_at+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
			cleaning_hours    =  cleaningteam.order_scheduler.cleaning_hours

			team_members_list   = []
			backup_members_list = []
			for team_member in cleaningteam.cleaning_team_members:
				if cleaningteam.team_leader.id != team_member.member.id and not team_member.is_backup_cleaner:
					try:
						image_url = team_member.member.profile_image.url
					except:
						image_url = None
					
					team_members_list.append({"member_name":team_member.member.name,"member_image":image_url})
				
				elif cleaningteam.team_leader.id != team_member.member.id and team_member.is_backup_cleaner:					
					backup_members_list.append(UserProfileShowSerializer(instance=team_member.member).data)

			before_cleaning_media_list = []
			after_cleaning_media_list = []
			for cleaning_media in cleaningteam.cleaning_team_medias:
				if cleaning_media.taken_status == 'BEFORE_CLEANING':
					before_cleaning_media_list.append({"before_cleaning_url":cleaning_media.media.url})
				elif cleaning_media.taken_status == 'AFTER_CLEANING':
					after_cleaning_media_list.append({"after_cleaning_url":cleaning_media.media.url})
				else:
					pass
			
			if cleaningteam.check_in:
				check_in = cleaningteam.check_in + timedelta(hours=3)
				check_in_time = check_in.time().strftime("%I:%M %p")
			else:
				check_in = None
				check_in_time = None
				

			if cleaningteam.check_out:
				check_out = cleaningteam.check_out + timedelta(hours=3)
				check_out_time = check_out.time().strftime("%I:%M %p")
			else:
				check_out = None
				check_out_time = None

			if cleaningteam.check_in_notes:
				check_in_notes = cleaningteam.check_in_notes
			else:
				check_in_notes = 'No Notes'

			if cleaningteam.check_out_notes:
				check_out_notes = cleaningteam.check_out_notes
			else:
				check_out_notes = 'No Notes'

			#backup
			if cleaningteam.backup_start_at:
				backup_start_at          = (cleaningteam.backup_start_at+timedelta(hours=3)).time().strftime("%I:%M %p")
				backup_datetime_start_at = (cleaningteam.backup_start_at+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
			else:
				backup_start_at          = None
				backup_datetime_start_at = None
			
			if cleaningteam.backup_end_at:
				backup_end_at            = (cleaningteam.backup_end_at+timedelta(hours=3)).time().strftime("%I:%M %p")
				backup_datetime_end_at   = (cleaningteam.backup_end_at+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
			else:
				backup_end_at            = None
				backup_datetime_end_at   = None

			if cleaningteam.backup_check_in:
				backup_check_in = (cleaningteam.backup_check_in+timedelta(hours=3)).time().strftime("%I:%M %p")
			else:
				backup_check_in = None

			if cleaningteam.backup_check_out:
				backup_check_out = (cleaningteam.backup_check_out+timedelta(hours=3)).time().strftime("%I:%M %p")
			else:
				backup_check_out = None 
			

			cleaning_status = cleaningteam.order_scheduler.work_status

			followup = FollowUp.objects.filter(is_active=True,investigation__order_schedule__id=cleaningteam.order_scheduler.id).last()
			if followup:
				followup_id = followup.id
			else:
				followup_id = None

			customer_id = cleaningteam.order_scheduler.order.evaluation.customer.id
			
			print(cleaning_status,"printest")

			response_dict = {'success':True,"team_id":cleaningteam.id,"visit_count":visit_count,"schedule_id":schedule_id, "customer_id":customer_id,"followup_id":followup_id,"cleaning_status":cleaning_status,"team_leader":cleaningteam.team_leader.name,"team_leader_image":cleaningteam.team_leader.profile_image.url,"assigned_by":cleaningteam.created_by.name,"assigned_by_image":cleaningteam.created_by.profile_image.url,"assigned_by_usertype":cleaningteam.created_by.user_type,"start_at":check_in_time,"end_at":check_out_time,"cleaning_start_at":cleaning_start_at,"cleaning_end_at":cleaning_end_at,"cleaning_hours":cleaning_hours,'members':team_members_list, 'before_cleaning_media':before_cleaning_media_list, 'after_cleaning_media':after_cleaning_media_list,'checkin_notes':check_in_notes,'checkout_notes':check_out_notes,'backup_start_at':backup_start_at,'backup_end_at':backup_end_at,'backup_check_in':backup_check_in,'backup_check_out':backup_check_out,'backup_datetime_start_at':backup_datetime_start_at,'backup_datetime_end_at':backup_datetime_end_at,'backup_members':backup_members_list}

		else:

			response_dict = {'success':False}

		return Response(response_dict,HTTP_200_OK)	

class SectionVerificationUpdationAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		section_id = request.GET.get('section_id')
		action_type = request.GET.get('action_type')
		price_id = request.GET.get('price_id')
		cleaning_team_id = request.GET.get('cleaning_team_id')

		section = EvaluationBookSection.objects.get(is_active=True,id=int(section_id))

		if action_type == 'verified':
			section.section_verified_by = request.user.id
			section.save()
			response_dict = {'success':True,'action_type':action_type}

		elif action_type == 'updated':
			price_range = ServicePriceRange.objects.get(is_active=True,id=int(price_id))
			
			old_section_price = section.section_net_cost

			section.size = price_range.maximum_area
			section.section_cost = price_range.price
			section.section_net_cost = float(price_range.price*section.section_cleanings)
			section.section_updated_by = request.user.id
			section.section_verified_by = request.user.id
			section.save()

			evaluationbook = EvaluationBook.objects.filter(is_active=True,id=section.evaluation_book.id).first()
			evaluationbook.estimated_cost = float(evaluationbook.estimated_cost-old_section_price+section.section_net_cost)
			evaluationbook.total_cost = float(evaluationbook.total_cost-old_section_price+section.section_net_cost)
			evaluationbook.save()

			evaluation_details = EvaluationDetails.objects.filter(is_active=True,id=evaluationbook.evaluation_details.id).first()
			evaluation_details.estimated_cost = float(evaluation_details.estimated_cost-old_section_price+section.section_net_cost)
			evaluation_details.total_cost = float(evaluation_details.total_cost-old_section_price+section.section_net_cost)
			evaluation_details.save()

			evaluation = Evaluation.objects.filter(is_active=True,id=evaluation_details.evaluation.id).first()
			evaluation.estimated_cost = float(evaluation.estimated_cost-old_section_price+section.section_net_cost)
			evaluation.total_cost = float(evaluation.total_cost-old_section_price+section.section_net_cost)
			evaluation.save()

			order = Order.objects.filter(is_active=True,evaluation__id=evaluation.id).first()
			order.total_amount = float(order.total_amount-old_section_price+section.section_net_cost)
			order.remining_amount = float(order.remining_amount+section.section_net_cost)
			order.save()

			cleaningteam = CleaningTeam.objects.filter(is_active=True,id=int(cleaning_team_id)).first()
			cleaningteam.is_section_updated = True
			cleaningteam.save()
			
			response_dict = {'success':True,'section_size':price_range.maximum_area,'action_type':action_type}

		else:
			response_dict = {'success':False}
		
		print(section_id,action_type,price_id,section,"test")

		

		return Response(response_dict,HTTP_200_OK)	

class CheckInAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		response_dict = {}
		response_dict['success'] = False

		team_id        = request.data.get('team_id')
		check_in_notes = request.data.get('check_in_notes')

		
		print(request.data,"reqdata2")

		try:
			cleaning_team_detail = CleaningTeam.objects.select_related('order_scheduler__order').get(is_active=True,id=team_id)
		except:	
			cleaning_team_detail = None

		if not cleaning_team_detail.check_in:
			cleaning_team_detail.check_in                    = timezone.now()
		if not cleaning_team_detail.check_out:
			cleaning_team_detail.order_scheduler.work_status     = 'CLEANING_IN_PROGRESS'
		
		if check_in_notes:
			cleaning_team_detail.check_in_notes = check_in_notes
		
		#confirm team
		absents                             = request.data.get('absent_list')
		if absents:
			absent_cleaners_list 				= [int(x) for x in absents.split(",")]
			absent_cleaners      				= CleaningTeamMember.objects.filter(is_active=True,id__in=absent_cleaners_list,team__id=team_id)
			absent_cleaners.delete()


			cleaning_team_detail.no_of_cleaners                 = (cleaning_team_detail.no_of_cleaners)-len(absent_cleaners_list)
			cleaning_team_detail.order_scheduler.no_of_cleaners = (cleaning_team_detail.order_scheduler.no_of_cleaners)-len(absent_cleaners_list)

		
		cleaning_team_detail.save()	

		cleaning_team_detail.order_scheduler.save()

		#To Save Media
		medias = request.FILES.getlist('media')
		print(medias,"ilist")
		
		if not medias==['']:
			for media in medias:
				print(media,"ilist")
				CleaningTeamMedia.objects.create(
						team_id=team_id,
						media=media,
						taken_status='BEFORE_CLEANING'
						)

		if cleaning_team_detail.is_section_updated == True:
			evaluaation = cleaning_team_detail.order_scheduler.order.evaluation
			if evaluaation.customer.is_sms == True:

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if evaluaation.customer.sms_preference == 'ENGLISH':

					message = "Dear Customer, Please find the updated Invoice against the order number "+str(evaluaation.evaluation_id)+"  here https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluaation.evaluation_id[3:])+""+str(evaluaation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
			
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
				
				else:

					message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluaation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluaation.evaluation_id[3:])+""+str(evaluaation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
			
					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluaation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
				
				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)

		response_dict['success'] = True
		response_dict['cleaning_date'] = cleaning_team_detail.start_at.date().strftime('%d-%m-%Y')
		return Response(response_dict,HTTP_200_OK)

class BackupCheckInAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		response_dict               = {}
		response_dict['success']    = False

		team_id                     = request.data.get('team_id')

		#confirm backup team
		absent_cleaners_list        = request.data.get('absent_list')
		if absent_cleaners_list:
			absent_cleaners      	= CleaningTeamMember.objects.filter(is_active=True,id__in=absent_cleaners_list,team__id=team_id,is_backup_cleaner=True)
			absent_cleaners.delete()
		
		#backupteam checkin
		CleaningTeam.objects.filter(id=team_id).update(backup_check_in=timezone.now())

		response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)

class CheckOutAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		response_dict = {}
		response_dict['success'] = False
		
		print(request.data,"dataa")
		print(request.data.get('team_id'),request.data.get('check_out_notes'),"dataa222")
		print(request.POST,"POSTT")

		team_id         = request.data.get('team_id')
		check_out_notes = request.data.get('check_out_notes')
	
		try:
			cleaning_team_detail = CleaningTeam.objects.select_related('order_scheduler__order__evaluation','order_scheduler__order_scheduler_book__service_type','order_scheduler__customer_address__customer').get(is_active=True,id=team_id)
		except:	
			cleaning_team_detail = None


		cleaning_team_detail.order_scheduler.work_status  		= 'CLEANING_FULFILLED'	
		cleaning_team_detail.check_out                    		= timezone.now()
		if cleaning_team_detail.backup_check_in:
			cleaning_team_detail.backup_check_out 				= timezone.now()
		
		cleaning_team_detail.order_scheduler.order.order_status = 'ORDER_IN_PROGRESS'

		if check_out_notes:
			cleaning_team_detail.check_out_notes = check_out_notes
		
		cleaning_team_detail.save()
		cleaning_team_detail.order_scheduler.save()
		cleaning_team_detail.order_scheduler.order.save()	

		#To Save Media
		medias = request.FILES.getlist('media')
		print(medias,"medis")
		if not medias==['']:
			for media in medias:
				CleaningTeamMedia.objects.create(
						team_id=team_id,
						media=media,
						taken_status='AFTER_CLEANING'
						)

		language = cleaning_team_detail.order_scheduler.order.evaluation.customer.sms_preference

		evaluation = cleaning_team_detail.order_scheduler.order.evaluation
		#invoice sms
		if cleaning_team_detail.order_scheduler.order.remining_amount > 0 and evaluation.customer.is_sms == True:

			url = "https://smsapi.future-club.com/fccsms.aspx"

			if language == 'ENGLISH':

				message = "Dear Customer, Please find the Invoice against the order number "+str(evaluation.evaluation_id)+"  here https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait."
		
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
			
			else:

				message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"
		
				querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
			
			headers = {
				'cache-control': "no-cache"
			}

			response = requests.request("GET", url, headers=headers, params=querystring)

			print(response.text,"respo")
		else:
			pass


		#feedback sms
		order = Order.objects.select_related('evaluation__customer').filter(is_active=True,id=int(cleaning_team_detail.order_scheduler.order.id)).order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))

		for ord in order:
			order_data = ord

		if order and order_data.evaluation.customer.is_sms == True:   #.completed_cleaning_count == order_data.cleaning_count or order_data.completed_followup_count == order_data.followup_count :

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
		else:
			pass

		####to close order
		try:
			closing_order	= Order.objects.get(is_active=True,order_no=cleaning_team_detail.order_scheduler.order.order_no,payment_status='COMPLETED')
		except:
			closing_order   = None

		if closing_order and order:
			closing_order.order_status = 'ORDER_CLOSED'
			closing_order.save()

		###############################################################
		if order:
			if order_data.evaluation.payment_method == 'POSTPAID' or order_data.evaluation.payment_method == 'BREAKDOWN':
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
				if not order_data.evaluation.customer.xero_account_id:
					##Xero Create Customer ID and Save
					contact_data                = {
													"Name":order_data.evaluation.customer.name,
													"ContactNumber":order_data.evaluation.customer.mobile_number,
													"EmailAddress":order_data.evaluation.customer.email,
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

					order_data.evaluation.customer.xero_account_id = ((create_contact['Contacts'])[0])['ContactID']
					order_data.evaluation.customer.save()

				#Xero Invoice
				if order_data.evaluation.payment_method == 'POSTPAID':
					Amount = order_data.evaluation.total_cost
					##Invoice Line Item 
					LineItems                 = []
					LineItems.append({
						"Description":"ONE TIME SERVICE",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1002,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber = order_data.invoice_no

					payment_policy = 'POSTPAID'

				elif order_data.evaluation.payment_method == 'BREAKDOWN':
					Amount = order_data.evaluation.after_cleaning_amount
					##Invoice Line Item 
					LineItems                 = []
					LineItems.append({
						"Description":"ONE TIME SERVICE",
						"Quantity":"1",
						"UnitAmount":Amount,
						"AccountCode":1002,
						"TaxType":"NONE"
									}
						)
					InvoiceNumber  = order_data.invoice_no+'B'

					payment_policy = 'AFTER CLEANING'
				else:
					pass

				invoice_data              = 	{
												"Type":"ACCREC",
												"Contact":{
													"ContactID":order_data.evaluation.customer.xero_account_id
												},
												"Date":order_data.evaluation.quatation_approved_date.strftime('%Y-%m-%d'),
												"DueDate":order_data.evaluation.quatation_approved_date.strftime('%Y-%m-%d'),
												"LineAmountTypes":"NoTax",
												"InvoiceNumber":InvoiceNumber,
												"Reference":order_data.order_no,
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
						update_xero_invoice                  = XeroInvoice.objects.get(order=order_data,invoice_no=InvoiceNumber)
						update_xero_invoice.amount           = Amount
						update_xero_invoice.xero_marked_date = timezone.now().date()
						update_xero_invoice.payment_policy   = payment_policy
						update_xero_invoice.save()
					except:
						XeroInvoice.objects.create(order=order_data,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)
			###################################################################

		response_dict['success'] = True
		response_dict['cleaning_date'] = cleaning_team_detail.start_at.date().strftime('%d-%m-%Y')
		return Response(response_dict,HTTP_200_OK)


class TeamSerachAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()
	def get(self,request):
		response_dict = {}

		cleaning_date      = datetime.strptime(request.GET.get('cleaning_date'),'%d-%m-%Y')
		blc                = request.GET.get('blc_no')


		cleaning_teams     = CleaningTeam.objects.select_related('order_scheduler__order__evaluation','team_leader').filter(Q(Q(order_scheduler__work_status='CLEANING_TEAM_ASSIGNED')&Q(Q(start_at__date=cleaning_date)|Q(start_at__date=cleaning_date)&Q(order_scheduler__order__order_no__icontains=blc)) ))
		
		teams = []
		if cleaning_teams:
			for cleaning_team in cleaning_teams:
				cleaning_team            = CleaningTeam.objects.get(id=cleaning_team.id)
				teams.append({'blc':cleaning_team.order_scheduler.order.order_no,'start_at':(cleaning_team.order_scheduler.start_at+timedelta(hours=3)).strftime('%d-%m-%Y %I:%M %p'),'end_at':(cleaning_team.order_scheduler.end_at+timedelta(hours=3)).strftime('%d-%m-%Y %I:%M %p'),'team_details':CleaningTeamAPISerializer(instance=cleaning_team).data})

		response_dict['teams']      = teams
		response_dict['success']    = True

		return Response(response_dict,HTTP_200_OK)


class TeamSwapCheckAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()
	def post(self,request):
		response_dict         = {}

		member_id            			  = request.data.get('member_id')

		current_team_id        			  = request.data.get('current_team_id')
		destination_team_id    			  = request.data.get('destination_team_id')

		current_team                      = CleaningTeam.objects.select_related('order_scheduler__order__evaluation').get(id=current_team_id)
		currentcleaning_datetime_start    = (current_team.order_scheduler.start_at+timedelta(hours=3))
		currentcleaning_datetime_end      = (current_team.order_scheduler.end_at+timedelta(hours=3))
		current_teams                     = CleaningTeam.objects.select_related('order_scheduler__order').filter(order_scheduler__order=current_team.order_scheduler.order,order_scheduler__start_at=current_team.order_scheduler.start_at,order_scheduler__end_at=current_team.order_scheduler.end_at).values_list('id',flat=True)

		destination_team                  = CleaningTeam.objects.select_related('order_scheduler__order__evaluation').get(id=destination_team_id)
		destination_date1                 = (destination_team.order_scheduler.start_at+timedelta(hours=3)).date()
		destination_date2                 = (destination_team.order_scheduler.end_at+timedelta(hours=3)).date()
		destinationcleaning_datetime_start= (destination_team.order_scheduler.start_at+timedelta(hours=3))
		destinationcleaning_datetime_end  = (destination_team.order_scheduler.end_at+timedelta(hours=3))
		destination_teams                 = CleaningTeam.objects.select_related('order_scheduler__order','order_scheduler__order_scheduler_book__service_type').filter(order_scheduler__order=destination_team.order_scheduler.order,order_scheduler__start_at=destination_team.order_scheduler.start_at,order_scheduler__end_at=destination_team.order_scheduler.end_at)

		#Cleaning Services
		user             				  = UserProfile.objects.filter(id=member_id)
		for destination_team in destination_teams:
			service_type = destination_team.order_scheduler.order_scheduler_book.service_type.name
			
			if service_type == 'General Cleaning':
				user  = user.filter(is_general_skill=True)
			elif service_type == 'Deep Cleaning':
				user  = user.filter(is_deep_skill=True)
			elif service_type == 'Upholstery Cleaning':
				user  = user.filter(is_upholstery_skill=True)
			elif service_type == 'Kitchen Cleaning':
				user  = user.filter(is_kitchen_skill=True)
			elif service_type == 'Kitchen Appliances':
				user  = user.filter(is_kitchen_skill=True)
			elif service_type == 'Carpet Cleaning':
				user  = user.filter(is_carpet_skill=True)
			elif service_type == 'Sterilization':
				user  = user.filter(is_sterilization_skill=True)
			elif service_type == 'Mattress Cleaning':
				user  = user.filter(is_mattress_skill=True)
			elif service_type == 'Facade Cleaning':
				user  = user.filter(is_facade_skill=True)
			elif service_type == 'Storage Area':
				user  = user.filter(is_storagearea_skill=True)
			elif service_type == 'Car Parking Umbrella':
				user = user.filter(is_carparkingumbrella_skill=True)
			elif service_type == 'Window Cleaning':
				user  = user.filter(is_window_skill=True)
			elif service_type == 'Outdoor Cleaning':
				user  = user.filter(is_outdoor_skill=True)


		#absent/shift/supershift cleaners
		absent_cleaner         = LeaveSchedule.objects.select_related('staff').filter(staff__id=member_id).filter(Q(Q(leave_date=destination_date1)|Q(leave_date=destination_date2)))
		shift_cleaners         = ShiftSchedule.objects.select_related('staff').filter(staff__id=member_id).filter(Q(Q(shift_date=destination_date1)|Q(shift_date=destination_date2)|Q(Q(shift3_start_at__lte=destinationcleaning_datetime_end)&Q(shift3_end_at__gte=destinationcleaning_datetime_end)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=destinationcleaning_datetime_start.time())&Q(shift1_end_at__gte=destinationcleaning_datetime_start.time()))&Q(Q(shift1_start_at__lte=destinationcleaning_datetime_end.time())&Q(shift1_end_at__gte=destinationcleaning_datetime_end.time()))) | Q(Q(Q(shift2_start_at__lte=destinationcleaning_datetime_start.time())&Q(shift2_end_at__gte=destinationcleaning_datetime_start.time()))&Q(Q(shift2_start_at__lte=destinationcleaning_datetime_end.time())&Q(shift2_end_at__gte=destinationcleaning_datetime_end.time()))) | Q(Q(Q(shift3_start_at__lte=destinationcleaning_datetime_start)&Q(shift3_end_at__gte=destinationcleaning_datetime_start))&Q(Q(shift3_start_at__lte=destinationcleaning_datetime_end)&Q(shift3_end_at__gte=destinationcleaning_datetime_end))) )
		if not shift_cleaners:
			super_shift_cleaners   = UserProfile.objects.filter(id=member_id).filter( Q(Q(universal_shift_start__lte=destinationcleaning_datetime_start.time())&Q(universal_shift_end__gte=destinationcleaning_datetime_start.time()))&Q(Q(universal_shift_start__lte=destinationcleaning_datetime_end.time())&Q(universal_shift_end__gte=destinationcleaning_datetime_end.time())) )
		else:
			super_shift_cleaners   = None 
		active_cleaners1 	   = CleaningTeamMember.objects.select_related('member').filter(member__id=member_id).filter(Q(Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(start_at__lt=destinationcleaning_datetime_end))|Q(Q(end_at__gt=destinationcleaning_datetime_start)&Q(end_at__lte=destinationcleaning_datetime_end))|Q(Q(start_at__lte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__gte=destinationcleaning_datetime_end))|Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__lte=destinationcleaning_datetime_end)))).exclude(team__id__in=current_teams)
		active_cleaners2 	   = FollowUpTeamMember.objects.select_related('member').filter(member__id=member_id).filter(Q(Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(start_at__lt=destinationcleaning_datetime_end))|Q(Q(end_at__gt=destinationcleaning_datetime_start)&Q(end_at__lte=destinationcleaning_datetime_end))|Q(Q(start_at__lte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__gte=destinationcleaning_datetime_end))|Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__lte=destinationcleaning_datetime_end))))	

		if (not absent_cleaner and not active_cleaners1	and not active_cleaners2) and (shift_cleaners or super_shift_cleaners) and user:
			
			response_dict['availability'] = True
		else:
			response_dict['availability'] = False
		
		response_dict['success']    = True

		return Response(response_dict,HTTP_200_OK)



class TeamSwapAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()
	def post(self,request):
		response_dict         = {}

		swapping_details      = request.data.get('swapping_details')

		for swapping_detail in swapping_details:

			member_id            			  = swapping_detail['member_id']

			current_team_id        			  = swapping_detail['current_team_id']
			destination_team_id    			  = swapping_detail['destination_team_id']
			current_team_incharge             = swapping_detail['current_team_incharge']
			destination_team_incharge         = swapping_detail['destination_team_incharge']

			current_team                      = CleaningTeam.objects.select_related('order_scheduler__order__evaluation').get(id=current_team_id)
			currentcleaning_datetime_start    = (current_team.order_scheduler.start_at+timedelta(hours=3))
			currentcleaning_datetime_end      = (current_team.order_scheduler.end_at+timedelta(hours=3))
			current_teams                     = CleaningTeam.objects.select_related('order_scheduler__order').filter(order_scheduler__order=current_team.order_scheduler.order,order_scheduler__start_at=current_team.order_scheduler.start_at,order_scheduler__end_at=current_team.order_scheduler.end_at).values_list('id',flat=True)

			destination_team                  = CleaningTeam.objects.select_related('order_scheduler__order__evaluation').get(id=destination_team_id)
			destination_date1                 = (destination_team.order_scheduler.start_at+timedelta(hours=3)).date()
			destination_date2                 = (destination_team.order_scheduler.end_at+timedelta(hours=3)).date()
			destinationcleaning_datetime_start= (destination_team.order_scheduler.start_at+timedelta(hours=3))
			destinationcleaning_datetime_end  = (destination_team.order_scheduler.end_at+timedelta(hours=3))
			destination_teams                 = CleaningTeam.objects.select_related('order_scheduler__order','order_scheduler__order_scheduler_book__service_type').filter(order_scheduler__order=destination_team.order_scheduler.order,order_scheduler__start_at=destination_team.order_scheduler.start_at,order_scheduler__end_at=destination_team.order_scheduler.end_at)

			#Cleaning Services
			user             = UserProfile.objects.filter(id=member_id)
			for destination_team in destination_teams:
				service_type = destination_team.order_scheduler.order_scheduler_book.service_type.name
				
				if service_type == 'General Cleaning':
					user  = user.filter(is_general_skill=True)
				elif service_type == 'Deep Cleaning':
					user  = user.filter(is_deep_skill=True)
				elif service_type == 'Upholstery Cleaning':
					user  = user.filter(is_upholstery_skill=True)
				elif service_type == 'Kitchen Cleaning':
					user  = user.filter(is_kitchen_skill=True)
				elif service_type == 'Kitchen Appliances':
					user  = user.filter(is_kitchen_skill=True)
				elif service_type == 'Carpet Cleaning':
					user  = user.filter(is_carpet_skill=True)
				elif service_type == 'Sterilization':
					user  = user.filter(is_sterilization_skill=True)
				elif service_type == 'Mattress Cleaning':
					user  = user.filter(is_mattress_skill=True)
				elif service_type == 'Facade Cleaning':
					user  = user.filter(is_facade_skill=True)
				elif service_type == 'Storage Area':
					user  = user.filter(is_storagearea_skill=True)
				elif service_type == 'Car Parking Umbrella':
					user = user.filter(is_carparkingumbrella_skill=True)
				elif service_type == 'Window Cleaning':
					user  = user.filter(is_window_skill=True)
				elif service_type == 'Outdoor Cleaning':
					user  = user.filter(is_outdoor_skill=True)


			#absent/shift/supershift cleaners
			absent_cleaner         = LeaveSchedule.objects.select_related('staff').filter(staff__id=member_id).filter(Q(Q(leave_date=destination_date1)|Q(leave_date=destination_date2)))
			shift_cleaners         = ShiftSchedule.objects.select_related('staff').filter(staff__id=member_id).filter(Q(Q(shift_date=destination_date1)|Q(shift_date=destination_date2)|Q(Q(shift3_start_at__lte=destinationcleaning_datetime_end)&Q(shift3_end_at__gte=destinationcleaning_datetime_end)))).filter(Q(Q(staff__user_type='CLEANER')|Q(staff__user_type='TEAMINCHARGE'))).filter(Q(Q(Q(shift1_start_at__lte=destinationcleaning_datetime_start.time())&Q(shift1_end_at__gte=destinationcleaning_datetime_start.time()))&Q(Q(shift1_start_at__lte=destinationcleaning_datetime_end.time())&Q(shift1_end_at__gte=destinationcleaning_datetime_end.time()))) | Q(Q(Q(shift2_start_at__lte=destinationcleaning_datetime_start.time())&Q(shift2_end_at__gte=destinationcleaning_datetime_start.time()))&Q(Q(shift2_start_at__lte=destinationcleaning_datetime_end.time())&Q(shift2_end_at__gte=destinationcleaning_datetime_end.time()))) | Q(Q(Q(shift3_start_at__lte=destinationcleaning_datetime_start)&Q(shift3_end_at__gte=destinationcleaning_datetime_start))&Q(Q(shift3_start_at__lte=destinationcleaning_datetime_end)&Q(shift3_end_at__gte=destinationcleaning_datetime_end))) )
			if not shift_cleaners:
				super_shift_cleaners   = UserProfile.objects.filter(id=member_id).filter( Q(Q(universal_shift_start__lte=destinationcleaning_datetime_start.time())&Q(universal_shift_end__gte=destinationcleaning_datetime_start.time()))&Q(Q(universal_shift_start__lte=destinationcleaning_datetime_end.time())&Q(universal_shift_end__gte=destinationcleaning_datetime_end.time())) )
			else:
				super_shift_cleaners   = None
			active_cleaners1 	   = CleaningTeamMember.objects.select_related('member').filter(member__id=member_id).filter(Q(Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(start_at__lt=destinationcleaning_datetime_end))|Q(Q(end_at__gt=destinationcleaning_datetime_start)&Q(end_at__lte=destinationcleaning_datetime_end))|Q(Q(start_at__lte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__gte=destinationcleaning_datetime_end))|Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__lte=destinationcleaning_datetime_end)))).exclude(team__id__in=current_teams)
			active_cleaners2 	   = FollowUpTeamMember.objects.select_related('member').filter(member__id=member_id).filter(Q(Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(start_at__lt=destinationcleaning_datetime_end))|Q(Q(end_at__gt=destinationcleaning_datetime_start)&Q(end_at__lte=destinationcleaning_datetime_end))|Q(Q(start_at__lte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__gte=destinationcleaning_datetime_end))|Q(Q(start_at__gte=destinationcleaning_datetime_start)&Q(end_at__gte=destinationcleaning_datetime_start)&Q(start_at__lte=destinationcleaning_datetime_end)&Q(end_at__lte=destinationcleaning_datetime_end))))	

			if (not absent_cleaner and not active_cleaners1	and not active_cleaners2) and (shift_cleaners or super_shift_cleaners) and user:
				response_dict['availability']         = True

				#Swap
				for swapping_detail in swapping_details:
					member_id            			  = swapping_detail['member_id']
					current_team_id        			  = swapping_detail['current_team_id']
					destination_team_id    			  = swapping_detail['destination_team_id']

					current_team                      = CleaningTeam.objects.select_related('order_scheduler__order__evaluation').get(id=current_team_id)
					current_teams                     = CleaningTeam.objects.select_related('order_scheduler__order').filter(order_scheduler__order=current_team.order_scheduler.order,order_scheduler__start_at=current_team.order_scheduler.start_at,order_scheduler__end_at=current_team.order_scheduler.end_at)
					destination_team                  = CleaningTeam.objects.select_related('order_scheduler__order__evaluation').get(id=destination_team_id)
					destination_teams                 = CleaningTeam.objects.select_related('order_scheduler__order','order_scheduler__order_scheduler_book__service_type').filter(order_scheduler__order=destination_team.order_scheduler.order,order_scheduler__start_at=destination_team.order_scheduler.start_at,order_scheduler__end_at=destination_team.order_scheduler.end_at)
				
					user                              = UserProfile.objects.get(id=member_id)

					#delete from current team
					for current_team in current_teams:
						CleaningTeamMember.objects.filter(team=current_team,member=user).delete()

						current_team.order_scheduler.no_of_cleaners -= 1
						current_team.no_of_cleaners -= 1
						current_team.team_leader_id  = current_team_incharge
						current_team.order_scheduler.save()
						current_team.save()
					#add to destination team		
					for destination_team in destination_teams:
						CleaningTeamMember.objects.create(team=destination_team,member=user,start_at=destination_team.start_at,end_at=destination_team.end_at,start_time=destination_team.start_at.time(),end_time=destination_team.end_at.time())
						destination_team.order_scheduler.no_of_cleaners += 1
						destination_team.no_of_cleaners += 1
						destination_team.team_leader_id  = destination_team_incharge
						destination_team.order_scheduler.save()
						destination_team.save()
			else:
				response_dict['availability']    = False
			
			response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)



class SOAMailAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		client_id = request.GET.get('client_id')
		customer = UserProfile.objects.get(is_active=True,id=int(client_id))
		address = Address.objects.filter(customer__id=int(client_id)).first()

		selected_options = request.GET.get('selected_options')
		print(selected_options,"opr")
		options = selected_options.split(",")

		orders = Order.objects.filter(is_active=True,evaluation__customer__id=client_id).order_by('created').prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'))
		print(orders,"ods")
		customer_orders = Order.objects.filter(is_active=True).order_by('evaluation__quatation_approved_date').filter(evaluation__customer__id=int(client_id),evaluation__quatation_status='APPROVED',order_status__isnull=False).prefetch_related(Prefetch('history_order',queryset=PaymentHistory.objects.filter(is_active=True),to_attr='paymenthistory'),Prefetch('evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_books')),to_attr='evaluationdetails'),Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True),to_attr='orderschedules')).annotate(cleaning_count=Count('order_scheduler_order'),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField())),cleaning_in_progress_count=Sum(Case(When(Q(Q(order_scheduler_order__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler_order__work_status='CLEANING_IN_PROGRESS')),then=1),default=0,output_field=IntegerField())))
		
		accounts_list = []

			
		total_credit = 0
		total_debit = 0
		total_balance = 0

		for order in customer_orders:
			
			if order.evaluation.payment_method != 'SUBSCRIPTION' and order.order_status == 'ORDER_CLOSED':
				total_balance += float(order.amount_paid)
				accounts_list.append({
							"date":order.created.date(),
							"invoice_no":order.order_no,
							"details":"Cleaning Services",
							"amount":order.total_amount,
							"credit":order.amount_paid,
							"debit":"",
							"balance_amount":total_balance
						})

				total_credit += float(order.amount_paid)

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

						total_balance -= float(payment.amount_paid)
						accounts_list.append({
								"date":payment.created.date(),
								"invoice_no":payment.payment_mode,
								"details":details,
								"amount":"",
								"credit":"",
								"debit":payment.amount_paid,
								"balance_amount":total_balance
							})
						total_debit += float(payment.amount_paid)

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
						job_completed += float(order.evaluation.fine_amount/cleanings_count)

					if order.evaluation.writeback_amount:
						job_completed -= float(order.evaluation.writeback_amount/cleanings_count)

					if order.evaluation.promocode_amount:
						job_completed -= float(order.evaluation.promocode_amount/cleanings_count)

					if order.evaluation.additional_charge:
						job_completed += float(order.evaluation.additional_charge/cleanings_count)

					if order.evaluation.discount:
						job_completed -= float(order.evaluation.discount/cleanings_count)
				
				total_balance += float(job_completed)
				accounts_list.append({
							"date":order.created.date(),
							"invoice_no":order.order_no,
							"details":"Cleaning Services",
							"amount":order.total_amount,
							"credit":job_completed,
							"debit":"",
							"balance_amount":total_balance
				})

				total_credit += float(job_completed)
				
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

						total_balance -= float(payment.amount_paid)
						accounts_list.append({
								"date":payment.created.date(),
								"invoice_no":payment.payment_mode,
								"details":details,
								"amount":"",
								"credit":"",
								"debit":payment.amount_paid,
								"balance_amount":total_balance
							})
						total_debit += float(order.amount_paid)			
			
			else:
				pass

		total_balance = float(total_credit-total_debit)

		print(total_balance,total_credit,total_debit,"cost")
		
		# if client.is_sms == True or 'SMS' in options:
		
		# 	url = "https://smsapi.future-club.com/fccsms.aspx"

		# 	language = client.sms_preference

		# 	if language == 'ENGLISH':
		# 		# print(str(evaluation.id),str(evaluation.evaluation_id),str(evaluation.total_cost),str(evaluation.quatation_expiry_date),str(evaluation.customer.username),str(evaluation.tracking_no),"trerr")

		# 		message = "Dear Customer, Please find the Quotation against the cleaning at "+separator.join(address_list)+" here https://my.bleachkw.com/customer/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"

		# 		querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
			
		# 	else:
		# 		message = "عزيزنا العميل نرجوا الاطلاع على عرض سعر خدمات التنظيف المطلوبة في "+separator.join(address_list)+" https://my.bleachkw.com/customer/quatation/paw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+"  لأي استفسارات يمكنكم التواصل معنا على . 9651882707+ شكراً لاختياركم بليتش لخدمات التنظيف"

		# 		querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

		# 	headers = {
		# 		'cache-control': "no-cache"
		# 	}
			
		# 	response = requests.request("GET", url, headers=headers, params=querystring)

		# 	print(message,"respo")
		# 	print(order_no)
		# 	data=True

		# else:
		# 	data = False

		if customer.is_email == True or 'EMAIL' in options:
			#send mail
			msg_html = render_to_string('email/soa.html',{"customer":customer,"address":address,"orders":accounts_list,"total_balance":total_balance,"total_credit":total_credit,"total_debit":total_debit})
			msg = EmailMultiAlternatives('Bleach Statement of Account', '', 'notification@bleach-kw.com', [customer.email])
			msg.attach_alternative(msg_html, "text/html")
			msg.send(fail_silently=False)
			print(msg,"msg")
			data=True
		else:
			data = False
		return Response(data,HTTP_200_OK)


class InvoiceSMSMailAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		order_id = request.GET.get('order_id')
		
		order = Order.objects.get(is_active=True,id=int(order_id))
		customer = order.evaluation.customer
		print(order,customer,"orid")
		if customer:
			response_dict['customer_mobile'] = customer.mobile_number
			response_dict['customer_email'] = customer.email
			response_dict['success'] = True
		else:
			response_dict['data'] = False
		return Response(response_dict,HTTP_200_OK)

	def post(self,request):
		data = False
		print(request.data,"Data")
		subscription_topay = request.data.get('subscription_topay',None)
		selected_options   = request.data.get('selectedoptions')
		try:
			options        = selected_options.split(",")
		except:
			options        = None

		order_id           = request.data.get('orderid')
		order              = Order.objects.filter(id=int(order_id)).first()

		if subscription_topay:
			Order.objects.filter(id=int(order_id)).update(subscription_topay=float(subscription_topay),subscription_topay_date=timezone.now())
			data=True

			######################################################################################
			#Invoice Send Amount Integrate with Xero
			try:
				last_unpaid_invoice = XeroInvoice.objects.filter(is_paid=False,order=order).last()
			except:
				last_unpaid_invoice = None

			if last_unpaid_invoice:
				InvoiceNumber      = last_unpaid_invoice.invoice_no
			else:
				try:
					last_paid_invoice = XeroInvoice.objects.filter(is_paid=True,order=order).last()
				except:
					last_paid_invoice = None
				
				if last_paid_invoice:
					last_paid_invoice_no    = last_paid_invoice.invoice_no
					last_paid_invoice_no.replace(last_paid_invoice_no[len(last_paid_invoice_no) - 1:], chr(ord(last_paid_invoice_no[-1])+1))
					InvoiceNumber           = last_paid_invoice_no
			
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
			Amount = subscription_topay
			##Invoice Line Item 
			LineItems        = []
			LineItems.append({
				"Description":"SUBSCRIPTION",
				"Quantity":"1",
				"UnitAmount":Amount,
				"AccountCode":1002,
				"TaxType":"NONE"
							}
				)

			payment_policy = 'SUBSCRIPTION'

			invoice_data        = 	{
										"Type":"ACCREC",
										"Contact":{
											"ContactID":order.evaluation.customer.xero_account_id
										},
										"Date":order.evaluation.quatation_approved_date.strftime('%Y-%m-%d'),
										"DueDate":order.evaluation.quatation_approved_date.strftime('%Y-%m-%d'),
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
			
			print(invoice_data,"Invoice Data")
			print(created_invoice,"Invoice")
			if created_invoice == 'OK':
				try:
					update_xero_invoice                  = XeroInvoice.objects.get(order=order,invoice_no=InvoiceNumber)
					update_xero_invoice.amount           = Amount
					update_xero_invoice.xero_marked_date = timezone.now().date()
					update_xero_invoice.payment_policy   = payment_policy
					update_xero_invoice.save()
				except:
					XeroInvoice.objects.create(order=order,invoice_no=InvoiceNumber,amount=Amount,xero_marked_date=timezone.now().date(),payment_policy=payment_policy)

			###################################################################################################################################
		
		if selected_options:
			language = order.evaluation.customer.sms_preference

			evaluation = order.evaluation

			evaluationdetails = EvaluationDetails.objects.filter(evaluation=evaluation).first()
			
			address = evaluationdetails.address

			evaluationbooks = EvaluationBook.objects.filter(evaluation_details=evaluationdetails).prefetch_related(Prefetch('evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True),to_attr='sections'))
			evaluationbook = evaluationbooks.first()

			if address.floor == None and address.avenue == None:
				address_list = [address.apartment, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			elif address.floor == None:
				address_list = [address.apartment, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]
			
			elif address.avenue == None:
				address_list = [address.apartment, address.floor, address.street, address.building, address.block, address.area.name, address.governorate.name]
			
			else:
				address_list = [address.apartment, address.floor, address.street, address.building, address.avenue, address.block, address.area.name, address.governorate.name]

			separator = ", "

			if evaluation.customer.is_sms == True or 'SMS' in options:

				url = "https://smsapi.future-club.com/fccsms.aspx"

				if language == 'ENGLISH':

					if evaluation.payment_method == 'SUBSCRIPTION':

						message = "Dear Customer, Please find the Invoice against the order number "+str(evaluation.evaluation_id)+"  here https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on [Customer Service Number]. Thank you for choosing Bleach Kuwait."

					else:

						message = "Dear Customer, Please find the Invoice against the order number "+str(evaluation.evaluation_id)+"  here https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+". For any assistance please contact us on [Customer Service Number]. Thank you for choosing Bleach Kuwait."

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}
				
				else:
					if evaluation.payment_method == 'SUBSCRIPTION':

						message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/subscription/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على (Customer Service Number).  شكراً لاختياركم بليتش لخدمات التنظيف"

					else:

						message = "عزيزينا العميل نرجوا الاطلاع على الفاتورة الخاصة بالطلب رقم "+str(evaluation.evaluation_id)+" في هذا الرابط https://my.bleachkw.com/customer/invoice/prw"+str(evaluation.tracking_no)+""+str(evaluation.customer.username)+" لأي استفسارات يمكنكم التواصل معنا على (Customer Service Number).  شكراً لاختياركم بليتش لخدمات التنظيف"

					querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}
				
				headers = {
					'cache-control': "no-cache"
				}

				response = requests.request("GET", url, headers=headers, params=querystring)

				print(message,response.text,"respo")
				
				data=True

			if evaluation.customer.is_email == True or 'EMAIL' in options:
				price_ranges 		= ServicePriceRange.objects.filter(is_active=True)
				#send mail
				msg_html = render_to_string('email/invoice.html',{"invoice":order,"address_list":separator.join(address_list),"evaluationbooks":evaluationbooks,"price_ranges":price_ranges})
				msg = EmailMultiAlternatives('Bleach Invoice', '', 'notification@bleach-kw.com', [evaluation.customer.email])
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)
				data=True
			
		return Response(data,HTTP_200_OK)


class ResourceSkillsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		print("got")
		user_id = request.data.get('user_id')
		user = UserProfile.objects.get(is_active=True,id=int(user_id))
		print(user,request.data.get('is_general_skill'),"ko")

		if request.data.get('is_general_skill') == 'True':
			print("yes")
			user.is_general_skill = True
		else:
			print("no")
			user.is_general_skill = False

		if request.data.get('is_deep_skill') == 'True':
			user.is_deep_skill = True
		else:
			user.is_deep_skill = False

		if request.data.get('is_upholstery_skill') == 'True':
			user.is_upholstery_skill = True
		else:
			user.is_upholstery_skill = False

		if request.data.get('is_kitchen_skill') == 'True':
			user.is_kitchen_skill = True
		else:
			user.is_kitchen_skill = False

		if request.data.get('is_sterilization_skill') == 'True':
			user.is_sterilization_skill = True
		else:
			user.is_sterilization_skill = False

		if request.data.get('is_carpet_skill') == 'True':
			user.is_carpet_skill = True
		else:
			user.is_carpet_skill = False

		if request.data.get('is_mattress_skill') == 'True':
			user.is_mattress_skill = True
		else:
			user.is_mattress_skill = False

		if request.data.get('is_facade_skill') == 'True':
			user.is_facade_skill = True
		else:
			user.is_facade_skill = False

		if request.data.get('is_storagearea_skill') == 'True':
			user.is_storagearea_skill = True
		else:
			user.is_storagearea_skill = False

		if request.data.get('is_carparkingumbrella_skill') == 'True':
			user.is_carparkingumbrella_skill = True
		else:
			user.is_carparkingumbrella_skill = False

		if request.data.get('is_outdoor_skill') == 'True':
			user.is_outdoor_skill = True
		else:
			user.is_outdoor_skill = False

		if request.data.get('is_window_skill') == 'True':
			user.is_window_skill = True
		else:
			user.is_window_skill = False

		user.save()

		data=True

		return Response(data,HTTP_200_OK)

class InventorySegmentsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		category_id = request.GET.get('category_id')
		print(category_id,"sed")
		try:
			inventory_segments = Segment.objects.filter(category__id=int(category_id))
		except:
			inventory_segments = None
		
		segment_serializer = InventorySegmentSerializer(inventory_segments,many=True).data
		print(segment_serializer,"sed")	
		response_dict['inventory_segment'] = segment_serializer
		return Response(response_dict,HTTP_200_OK)


class InventoryLinesAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		segment_id = request.GET.get('segment_id')
		print(segment_id,"sed")
		try:
			inventory_lines = Line.objects.filter(segment__id=int(segment_id))
		except:
			inventory_lines = None
		
		line_serializer = InventoryLineSerializer(inventory_lines,many=True).data
		print(line_serializer,"sed")	
		response_dict['inventory_line'] = line_serializer
		return Response(response_dict,HTTP_200_OK)

	def post(self,request):
		response_dict = {}
		
		action =request.data.get('action')

		if action == 'add_line':
			segment_id = request.data.get('segment_id')
			line_name   = request.data.get('line_name')
			line_status = request.data.get('line_status')
			line_code     = request.data.get('line_code')

			segment = Segment.objects.get(id=int(segment_id))

			line_id_exists = Line.objects.filter(line_id=line_code).first()
			if line_id_exists:
				response_dict['alert_message'] = 'Line ID exists !'
			else:

				Line.objects.create(category=segment.category,segment=segment,name=line_name,line_id=line_code,status=line_status)
				response_dict['alert_message'] = 'Line Added !'

			try:
				inventory_lines = Line.objects.filter(segment__id=int(segment_id))
			except:
				inventory_lines = None
			
			line_serializer = InventoryLineSerializer(inventory_lines,many=True).data
			
			response_dict['inventory_line'] = line_serializer

		if action == 'edit_line':
			line_id = request.data.get('line_id')
			line_name   = request.data.get('line_name')
			line_status = request.data.get('line_status')
			
			line = Line.objects.get(id=int(line_id))

			line.name = line_name
			line.status = line_status
			line.save()
			response_dict['alert_message'] = 'Line updated !'

			try:
				inventory_lines = Line.objects.filter(segment__id=line.segment.id)
			except:
				inventory_lines = None
			
			line_serializer = InventoryLineSerializer(inventory_lines,many=True).data
				
			response_dict['inventory_line'] = line_serializer

		if action == 'delete_line':
			line_id = request.data.get('line_id')

			line = Line.objects.get(id=int(line_id))
			segment_id = line.segment.id
			line_items = InventoryItem.objects.filter(item_line=line).count()
			
			if line_items == 0:
				line.delete()
				response_dict['alert_message'] = 'Line Deleted !'			
			else:
				response_dict['alert_message'] = 'Cannot Delete Line !'	

			try:
				inventory_lines = Line.objects.filter(segment__id=int(segment_id))
			except:
				inventory_lines = None
			
			line_serializer = InventoryLineSerializer(inventory_lines,many=True).data
				
			response_dict['inventory_line'] = line_serializer

		return Response(response_dict,HTTP_200_OK)

class InventoryValuesAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		attribute_id = request.GET.get('attribute_id')
		print(attribute_id,"attrsed")
		try:
			inventory_values = AttributeValue.objects.filter(attribute__id=int(attribute_id))
		except:
			inventory_values = None
		
		print(inventory_values,"invo")
		value_serializer = InventoryValueSerializer(inventory_values,many=True).data
		print(value_serializer,"sed")	
		response_dict['inventory_value'] = value_serializer
		return Response(response_dict,HTTP_200_OK)

	def post(self,request):
		response_dict = {}

		action = request.data.get('action')

		if action == 'add_value':
			print("addet")
			attribute_id = request.data.get('value_attribute_id')
			value_name   = request.data.get('value_name')
			value_status = request.data.get('value_status')
			print(attribute_id,value_name,value_status,"attrval")

			attribute = Attribute.objects.get(id=int(attribute_id))

			AttributeValue.objects.create(attribute=attribute,name=value_name,status=value_status)

			try:
				inventory_values = AttributeValue.objects.filter(attribute__id=int(attribute_id))
			except:
				inventory_values = None
			
			print(inventory_values,"invo")
			value_serializer = InventoryValueSerializer(inventory_values,many=True).data
			print(value_serializer,"sed")	
			response_dict['inventory_value'] = value_serializer

		if action == 'edit_value':
			value_id = request.data.get('value_id')
			value_name   = request.data.get('value_name')
			value_status = request.data.get('value_status')

			value = AttributeValue.objects.get(id=int(value_id))

			value.name = value_name
			value.status = value_status
			value.save()

			try:
				inventory_values = AttributeValue.objects.filter(attribute__id=value.attribute.id)
			except:
				inventory_values = None
			
			print(inventory_values,"invo")
			value_serializer = InventoryValueSerializer(inventory_values,many=True).data
			print(value_serializer,"sed")	
			response_dict['inventory_value'] = value_serializer

		if action == 'delete_value':
			print("dletttt")
			value_id = request.data.get('value_id')
			value = AttributeValue.objects.get(id=int(value_id))
			attribute_id = value.attribute.id

			value.delete()

			try:
				inventory_values = AttributeValue.objects.filter(attribute__id=attribute_id)
			except:
				inventory_values = None
			
			print(inventory_values,"invo")
			value_serializer = InventoryValueSerializer(inventory_values,many=True).data
			print(value_serializer,"sed")	
			response_dict['inventory_value'] = value_serializer

		return Response(response_dict,HTTP_200_OK)

class InventoryItemsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		item_id = request.GET.get('item_id')
		print(item_id,"attrsed")
		try:
			item_units = ItemUnit.objects.filter(item__id=int(item_id),is_available=True)
			unit_count = item_units.count()
		except:
			item_units = None
			unit_count = 0
		
		print(unit_count,"invo")
		
		response_dict['inventory_item_unit_count'] = unit_count
		return Response(response_dict,HTTP_200_OK)

class InventoryBundleItemsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		bundle_id = request.GET.get('bundle_id')
		print(bundle_id,"attrsed")
		try:
			inventory_items = BundleItems.objects.filter(bundle__id=int(bundle_id))
		except:
			inventory_items = None
		
		print(inventory_items,"invo")
		items_list = []
		for item in inventory_items:
			list_item = {
				'unit_id' : item.id,
				'item_id' : item.item.id,
				'item_name' : item.item.name,
				'item_price' :item.item_price,
				'item_count' : item.item_count,
			}
			items_list.append(list_item)
		# item_serializer = InventoryBundleItemSerializer(inventory_items,many=True).data
		# print(item_serializer,"sed")	
		response_dict['inventory_item'] = items_list
		return Response(response_dict,HTTP_200_OK)

class InventorySupplierItemsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		supplier_id = request.GET.get('supplier_id')
		print(supplier_id,"attrsed2")
		try:
			supplier_items = SupplierItems.objects.filter(supplier__id=int(supplier_id))
		except:
			supplier_items = None
		
		
		items = []
		for item in supplier_items:
			item_dict = {}
			item_dict['item_id'] = item.id
			item_dict['product_id'] = item.item.id
			item_dict['product_name'] = item.item.name
			item_dict['item_price'] = item.item_price
			item_dict['currency'] = item.supplier.currency
			items.append(item_dict)
		response_dict['items']=items
		return Response(response_dict,HTTP_200_OK)

	def post(self,request):
		response_dict = {}

		action =request.data.get('action')
		if action == 'add_item':
			print("pop")
			supplier_id = request.data.get('item_supplier_id')
			item = request.data.get('item')
			item_price = request.data.get('supplier_item_price')
			item_count = request.data.get('supplier_item_count')
			print(supplier_id,item,item_price,item_count,"itmtest")
			supplier_items_latest = SupplierItems.objects.all().last()

			if supplier_items_latest:
				code_number  =  int(re.findall(r'(\d+)', supplier_items_latest.supplier_item_id)[0]) + 1
				new_supplier_item_id = 'SPITM'+str(code_number)
			else:
				new_supplier_item_id = 'SPITM9001'

			supplier = Supplier.objects.get(id=int(supplier_id))

			product = InventoryItem.objects.get(id=int(item))

			
			item_count_check = SupplierItems.objects.filter(item=product).count()

			if item_count_check >= 1:
				response_dict['message'] = 'Item already exists for a supplier !'
				response_dict['success'] = False
				# messages.error(request,"Item already exists for a supplier !")
			else:
				SupplierItems.objects.create(supplier=supplier,item=product,item_price=item_price,supplier_item_id=new_supplier_item_id,item_count=item_count)
				response_dict['message'] = 'Item Added Successfully !'
				response_dict['success'] = True
				# messages.success(request,"Item Added Successfully !")

		if action == 'edit_item':
			print("ppp")
			supplier_item_id = request.data.get('item_edit_id')
			item = request.data.get('item')
			item_price = request.data.get('supplier_item_price')
			item_count = request.data.get('supplier_item_count')

			supplieritem = SupplierItems.objects.get(id=int(supplier_item_id))

			product = InventoryItem.objects.get(id=int(item))

			print(supplieritem,product,"kop")

			
			item_check = SupplierItems.objects.filter(item=product).exclude(id=int(supplier_item_id))
			print(item_check,"icheckk")
			item_check_count = item_check.count()
			print(item_check,item_check_count,"icheckk")

			if item_check_count >= 1:
				response_dict['message'] = 'Item already exists for a supplier !'
				response_dict['success'] = False
			else:
				supplieritem.item = product
				supplieritem.item_price = item_price
				supplieritem.item_count = item_count
				supplieritem.save()
				
				response_dict['message'] = 'Item Updated !'
				response_dict['success'] = True

		# if action == 'delete_item':
		# 	supplier_item_id = request.data.get('supplier_id_delete')

		# 	supplieritem = SupplierItems.objects.get(id=int(supplier_item_id)).delete()

		# 	response_dict['message'] = 'Item Deleted !'
		# 	response_dict['success'] = True
		return Response(response_dict,HTTP_200_OK)

class InventoryItemsListAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		store_id = request.GET.get('store_id')
		product_id = request.GET.get('product_id')
		print(store_id,"attrsedan")
		# try:
		store = Store.objects.filter(id=int(store_id))
		itemslist = InventoryItem.objects.all().prefetch_related(Prefetch('unit_item',queryset=ItemUnit.objects.filter(is_available=True,store=store),to_attr='item_units'),Prefetch('quantity_store_item',queryset=QuantityStoreDetails.objects.filter(item_store=store),to_attr='quantity_items'))
		
		units = []
		if product_id:
			itemunits = ItemUnit.objects.filter(is_available=True,store=store,item__id=int(product_id))
			
			for unit in itemunits:
				unit_dict={
					'id' : unit.id,
					'unit_code' : unit.unit_code
				}
				units.append(unit_dict)
		
		items = []
		for item in itemslist:
			for unit in item.item_units:
				item_dict = {}
				item_dict['item_id'] = unit.item.id
				item_dict['item_name'] = unit.item.name
				item_dict['item_type'] = unit.item.item_add_type
				item_dict['item_code'] = unit.item.item_code
				items.append(item_dict)

			for qty in item.quantity_items:
				item_dict = {}
				item_dict['item_id'] = qty.quantity_item.id
				item_dict['item_name'] = qty.quantity_item.name
				item_dict['item_type'] = qty.quantity_item.item_add_type
				item_dict['item_code'] = qty.quantity_item.item_code
				items.append(item_dict)

		
		# except:
		# 	store = None
		# 	items = None
		print(items,"iteams")

		res_list = []
		for i in range(len(items)):
			if items[i] not in items[i + 1:]:
				res_list.append(items[i])
		response_dict['items']=res_list
		response_dict['units']=units
		return Response(response_dict,HTTP_200_OK)


class InventoryServiceRecipeAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		service_type = request.GET.get('service_type')
		recipe_category = request.GET.get('recipe_category')
		print(service_type,recipe_category,"attrsed2")
		# try:
		# 	service_items = ServiceRecipeItems.objects.filter(service_type__service=service_type,service_or_person=recipe_category)
		# 	service = ServiceRecipe.objects.get(service=service_type)
		# except:
		# 	service_items = None
		# 	service = None

		try:
			service_ingredients = ServiceRecipeIngredients.objects.filter(service_type__service=service_type,service_or_person=recipe_category)
			service = ServiceRecipe.objects.get(service=service_type)
		except:
			service_ingredients = None
			service = None
		
		print(service_ingredients,"invo")

		items_list = []

		if service_ingredients:
			for item in service_ingredients:
				list_item = {
					'ingredient_id' : item.id,
					'recipe_type' : item.service_or_person,
					'item_name' : item.ingredient,
					'item_count' : item.quantity,
					'status' : item.status
				}

				items_list.append(list_item)
	
		response_dict['service_ingredients'] = items_list

		if service:
			response_dict['area_size'] = service.area_size
			response_dict['staff_count'] = service.staff_count
		else:
			print('pp')
			response_dict['area_size'] = 0
			response_dict['staff_count'] = 0
		return Response(response_dict,HTTP_200_OK)

	def post(self,request):
		response_dict = {}

		action = request.data.get('action')

		if action == 'add_ingredient':
			service_type = request.data.get('service_type')
			ingredient = request.data.get('ingredient')
			print(ingredient,"itm")
			item_count = request.data.get('item_count')
			# unit_price = request.POST.get('unit_price')
			item_status = request.data.get('item_status')
			recipe_type = request.data.get('recipe_type')

			# inventoryitem = InventoryItem.objects.get(id=int(item))

			ServiceRecipe.objects.get_or_create(service=service_type)

			get_servicetype = ServiceRecipe.objects.get(service=service_type)          

			ServiceRecipeIngredients.objects.create(service_or_person=recipe_type,service_type=get_servicetype,ingredient=ingredient,quantity=item_count,status=item_status)

			response_dict['success'] = True

		if action == 'edit_ingredient':
			service_ingredient_id = request.data.get('item_edit_id')
			ingredient = request.data.get('ingredient')
			item_count = request.data.get('item_count')
			# unit_price = request.POST.get('unit_price')
			item_status = request.data.get('item_status')
			recipe_type = request.data.get('recipe_type')

			# inventoryitem = InventoryItem.objects.get(id=int(item))

			serviceingredient = ServiceRecipeIngredients.objects.get(id=int(service_ingredient_id))

			serviceingredient.service_or_person = recipe_type
			serviceingredient.ingredient = ingredient
			serviceingredient.quantity = item_count
			serviceingredient.status = item_status
			serviceingredient.save()

			response_dict['success'] = True

		if action == 'delete_ingredient':
			ingredient_id = request.data.get('object_id')

			ServiceRecipeIngredients.objects.filter(id=int(ingredient_id)).delete()

			response_dict['success'] = True

		return Response(response_dict,HTTP_200_OK)

class InventoryServiceAreaAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		service_type = request.GET.get('service_type')
		area = request.GET.get('area')
		staffcount = request.GET.get('staffcount')
		
		print(service_type,area,staffcount,"attrsed3")
		try:
			service = ServiceRecipe.objects.get(service=service_type)
			if area != 'false' :
				print("do")
				service.area_size = area
			if staffcount != 'false' :
				print("dont")
				service.staff_count = staffcount
			service.save()
		except:
			service = ServiceRecipe.objects.create(service=service_type)
			if area != 'false' :
				service.area_size = area
			if staffcount != 'false' :
				service.staff_count = staffcount
			service.save()
		
		print(service,"invo")

		if service:
			response_dict['area_size'] = service.area_size
			response_dict['staff_count'] = service.staff_count
		else:
			response_dict['area_size'] = 0
			response_dict['staff_count'] = 0
		return Response(response_dict,HTTP_200_OK)

class InventoryServiceItemsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		ingredient_id = request.GET.get('ingredient_id')
		item_id = request.GET.get('item_id')
		ingredient_item_id = request.GET.get('ingredient_item_id')
		ingredient_item_delete_id = request.GET.get('ingredient_item_delete_id')
		action = request.GET.get('action')
		
		print(ingredient_id,ingredient_item_id,"iyyo","attrsed3")
		# try:
		ingredient = ServiceRecipeIngredients.objects.get(id=int(ingredient_id))
		print(ingredient,"ingri")

		if action == 'add_item':
			
			print("add")
			item = InventoryItem.objects.get(id=int(item_id))
			ingredient_items_exist = ServiceRecipeItems.objects.filter(ingredient=ingredient,item=item)
			
			if ingredient_items_exist:
				pass
			else:
				ServiceRecipeItems.objects.create(ingredient=ingredient,item=item)

		if action == 'edit_item':
			print("eddit")
			ingredient_item = ServiceRecipeItems.objects.get(id=int(ingredient_item_id))
			item = InventoryItem.objects.get(id=int(item_id))
			ingredient_item.item = item
			ingredient_item.save()

		if action == 'delete_item':
			ServiceRecipeItems.objects.get(id=int(ingredient_item_delete_id)).delete()

		print(ingredient.ingredient,"ingr")
		response_dict['ingredient'] = ingredient.ingredient
		items = ServiceRecipeItems.objects.filter(ingredient=ingredient)
		# except:
		# 	ingredient = None
		# 	items = None
		# 	response_dict['ingredient'] = None

		items_list = []
		if items:
			for item in items:
				list_item = {
					'ingredient_item_id' : item.id,
					'item_name' : item.item.name,
					'item_id' : item.item.id
				}

				items_list.append(list_item)
	
		response_dict['service_items'] = items_list
		
		return Response(response_dict,HTTP_200_OK)


class DiscountSettingsAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict                     = {}
		discount_settings                 = Settings.objects.filter(is_active=True).first()
		
		discount_setting_serializer       = DiscountSettingSerializer(discount_settings).data
		response_dict['discount_details'] = discount_setting_serializer
		response_dict['success']          = True

		return Response(response_dict,HTTP_200_OK)

##Booking Expiry
class BookingExpiryCheckAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict                     = {}
		order_no                          = request.GET.get('order_no')
		order_scheduler                   = OrderScheduler.objects.select_related('order').filter(order__order_no=order_no).first()

		response_dict['created']          = datetime.strftime((order_scheduler.created+timedelta(hours=3)),'%d-%m-%Y %I:%M:%S %p')
		response_dict['success']          = True

		return Response(response_dict,HTTP_200_OK)


class BookingExpiryAPI(APIView):
	permission_classes  	= (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		response_dict                     = {}
		order_no                          = request.data.get('order_no')

		#delete scheduler
		OrderScheduler.objects.select_related('order').filter(order__order_no=order_no).delete()

		#update booking status
		CustomerBooking.objects.select_related('evaluation').filter(evaluation__evaluation_id=order_no).update(is_bookingcompleted=False)

		response_dict['success']          = True
		
		return Response(response_dict,HTTP_200_OK)

###Team Leader Mobile app API'S
from bleach_crm_ps.api_permissions import IsTeamInchargePermission
from Api.serializers import CleaningTeamAPISerializer,FollowUpTeamAPISerializer

class LoginAPI(APIView):  
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	
	def post(self,request): 
		response_dict = {'success':False}  
		
		get_username  = request.data.get('username')
		get_password  = request.data.get('password')
          
		user = authenticate(username=get_username,password=get_password)
		
		if user:
			t, c= Token.objects.get_or_create(user=user)
			response_dict['success']             = True
			response_dict['token']               = t.key
			
			response_dict['name']                = user.name
			response_dict['profile_image']       = user.profile_image.url
		else:
			response_dict['reason']     = 'Invalid Credentials'
        
		return Response(response_dict, HTTP_200_OK)

class TlHomeAPI(APIView):  
	permission_classes        = (IsAuthenticated,IsTeamInchargePermission)
	authentication_classes    = (TokenAuthentication,)
	
	def get(self,request): 
		response_dict = {'success':False} 

		count_today_start = timezone.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
		count_today_end   = count_today_start+timedelta(1)

		#Cleaning Jobs count
		try:
			cleaning_job	= CleaningTeam.objects.filter(is_active=True,team_leader=request.user)
		except:
			cleaning_job    = None

		today_cleaning_job_count   = cleaning_job.filter(Q(Q(start_at__gte=count_today_start)&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_start)&Q(end_at__lt=count_today_end))).count() 
		week_cleaning_job_count    = cleaning_job.filter(Q(Q(start_at__gte=count_today_end-timedelta(7))&Q(start_at__lt=count_today_end))|Q(Q(end_at__gte=count_today_end-timedelta(7))&Q(end_at__lt=count_today_end))).count()
				

		#Investigation Count
		try:
			investigation          = Investigation.objects.filter(is_active=True,investigator=request.user)
		except:
			investigation          = None	

		today_investigation_count  = investigation.filter(scheduled_at__gte=count_today_start,scheduled_at__lt=count_today_end).count()
		week_investigation_count   = investigation.filter(scheduled_at__gte=count_today_end-timedelta(7),scheduled_at__lt=count_today_end).count()	

		response_dict['today_cleaning_job_count']  = today_cleaning_job_count
		response_dict['week_cleaning_job_count']   = week_cleaning_job_count

		response_dict['today_investigation_count'] = today_investigation_count
		response_dict['week_investigation_count']  = week_investigation_count

		response_dict['success']                   = True


		return Response(response_dict, HTTP_200_OK)

class TlCleanings(APIView):  
	permission_classes        = (IsAuthenticated,IsTeamInchargePermission)
	authentication_classes    = (TokenAuthentication,)
	
	def get(self,request): 
		response_dict = {'success':False}  

		#My cleanings	
		my_cleaning_calendar_date	= request.GET.get('my_cleaning_calendar_date')
		
		try:
			my_cleaning_date = datetime.strptime(my_cleaning_calendar_date,'%d-%m-%Y')
		except:
			my_cleaning_date = timezone.now().replace(tzinfo=None)

		my_cleaning_date_start = my_cleaning_date.replace(hour=0,minute=0,second=0,microsecond=0)
		my_cleaning_date_end   = my_cleaning_date_start+timedelta(1)

			
		my_cleanings  = CleaningTeam.objects.filter(Q(Q(Q(start_at__gte=my_cleaning_date_start)&Q(start_at__lt=my_cleaning_date_end))&Q(team_leader=request.user))).select_related('order_scheduler__order_scheduler_book__service_type','order_scheduler__order__evaluation__customer','order_scheduler__customer_address')
		my_followups  = FollowUpTeam.objects.filter(Q(Q(Q(start_at__gte=my_cleaning_date_start)&Q(start_at__lt=my_cleaning_date_end))&Q(team_leader=request.user))).select_related('followup_scheduler__follow_up__investigation__order__evaluation__customer','followup_scheduler__follow_up__investigation__order_schedule__order_scheduler_book__service_type','followup_scheduler__customer_address')
		

		response_dict['cleanings']          = CleaningTeamAPISerializer(instance=my_cleanings,many=True).data
		response_dict['followup_cleanings'] = FollowUpTeamAPISerializer(instance=my_followups,many=True).data
		
		response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)


class TlCleaningDetails(APIView):  
	permission_classes        = (IsAuthenticated,IsTeamInchargePermission)
	authentication_classes    = (TokenAuthentication,)
	def get(self,request,team_id): 
		response_dict                     = {'success':False}
		
		cleaning_details                  = CleaningTeam.objects.select_related('order_scheduler__order_scheduler_book__service_type','order_scheduler__order__evaluation__customer','order_scheduler__customer_address').prefetch_related(Prefetch('order_scheduler__order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',queryset=EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='booksections')).get(id=team_id)
		response_dict['cleaning_details'] = CleaningTeamAPISerializer(instance=cleaning_details).data
		response_dict['success']          = True

		return Response(response_dict, HTTP_200_OK)


class TlFollowupCleaningDetails(APIView):  
	permission_classes        = (IsAuthenticated,IsTeamInchargePermission)
	authentication_classes    = (TokenAuthentication,)
	def get(self,request,team_id): 
		response_dict                             = {'success':False}

		followupcleaning_details                  = FollowUpTeam.objects.select_related('followup_scheduler__follow_up__investigation__order','followup_scheduler__customer_address').prefetch_related(Prefetch('followup_scheduler__follow_up__follow_up_of_section',queryset=FollowUpSection.filter(is_active=True).prefetch_related(Prefetch('keynotesectionsfollowup',queryset=FollowUpSectionKeynote.objects.filter(is_active=True),to_attr='sectionkeynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections')).get(id=team_id)
		response_dict['followupcleaning_details'] = FollowUpTeamAPISerializer(instance=followupcleaning_details).data
		response_dict['success']                  = True

		return Response(response_dict, HTTP_200_OK) 

class TlFollowupCleaningCheckin(APIView):  
	permission_classes        = (IsAuthenticated,IsTeamInchargePermission)
	authentication_classes    = (TokenAuthentication,)
	def post(self,request):
		response_dict                             = {'success':False}
		team_id                                   = request.data.get('team_id')

		try:
			followup_team_detail = FollowUpTeam.objects.select_related('followup_scheduler__follow_up').get(is_active=True,id=team_id)
		except:	
			followup_team_detail = None

		#update
		if not followup_team_detail.check_in:
			followup_team_detail.check_in                       = timezone.now()
		
		if not followup_team_detail.check_out:
			followup_team_detail.followup_scheduler.work_status     = 'FOLLOW_UP_CLEANING_IN_PROGRESS'
			followup_team_detail.followup_scheduler.follow_up.status= 'FOLLOWUP_IN_PROGRESS'
		
		followup_team_detail.save()	
		followup_team_detail.followup_scheduler.save()
		followup_team_detail.followup_scheduler.follow_up.save()

		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				FollowUpTeamMedia.objects.create(
						team_id=team_id,
						media=media,
						taken_status='BEFORE_CLEANING'
						)

		response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

class TlFollowupCleaningCheckout(APIView):  
	permission_classes        = (IsAuthenticated,IsTeamInchargePermission)
	authentication_classes    = (TokenAuthentication,)
	def post(self,request):
		response_dict                       = {'success':False}
		team_id                             = request.data.get('team_id')

		try:
			followup_team_detail = FollowUpTeam.objects.select_related('followup_scheduler__follow_up').get(is_active=True,id=team_id)
		except:	
			followup_team_detail = None

		#update
		followup_team_detail.check_out                          = timezone.now()
		followup_team_detail.followup_scheduler.work_status     = 'FOLLOW_UP_CLEANING_FULFILLED'
		followup_team_detail.save()
		followup_team_detail.followup_scheduler.save()	

		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				FollowUpTeamMedia.objects.create(
						team_id=team_id,
						media=media,
						taken_status='AFTER_CLEANING'
						)
		
		response_dict['success'] = True
		
		return Response(response_dict, HTTP_200_OK)

class CheckinChecklist(APIView):
	permission_classes        = (IsAuthenticated,IsTeamInchargePermission)
	authentication_classes    = (TokenAuthentication,)
	def post(self,request):
		response_dict            = {'success':False}

		keynote_id     = request.data.get('keynote_id')
		keynote_status = request.data.get('status')
		keynote_type   = request.data.get('keynote_type')

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
		
		response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

# class CleaningsExport(APIView):
# 	permission_classes  	=   (AllowAny,)
# 	authentication_classes  = ()

# 	def post(self,request):
# 		response_dict = {'success':False}

# 		cleaning_ids = request.data.get('json_data')
# 		# cleaning_ids = cleaning_ids.split(",")
# 		print(cleaning_ids[0],"jio")

# 		row_num = 0

# 		font_style = xlwt.XFStyle()
# 		font_style.font.bold = True

# 		response = HttpResponse(content_type='application/ms-excel')
# 		response['Content-Disposition'] = 'attachment; filename="Cleanings.xls"'

# 		wb = xlwt.Workbook(encoding='utf-8')
# 		ws = wb.add_sheet('CLEANING LIST')

# 		columns = ['BLC No.','Customer','Location','Starting Time','Duration','Cleaning Agent','Cleaners']
		
# 		for col_num in range(len(columns)):
# 			ws.write(row_num, col_num, columns[col_num], font_style)

# 		rows = []

# 		for cid in cleaning_ids:
# 			print(cid,"idee")
# 			cleaning_data = OrderScheduler.objects.prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).select_related('team_leader','drop_off_driver','pick_up_driver').prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')),to_attr='cleaning_team')).get(is_active=True,id=int(cid))
# 			cleaning_list = OrderScheduler.objects.values_list('order__order_no','customer_address__customer__name','customer_address__area','start_at' , 'cleaning_hours', 'cleaning_hours', 'cleaning_hours').get(is_active=True,id=int(cid))
			
# 			print(cleaning_data,"dat")

# 			cleaning_list = list(cleaning_list)
# 			print(cleaning_list[2],"lis")

			
# 			for team in cleaning_data.cleaning_team:
# 				cleaning_list[5] = team.team_leader.name

# 				members = ''

# 				for member in team.cleaning_team_members:
# 					members += str(member.member.name) + ','
				
# 				cleaning_list[6] = members

# 			print(members,"mem")
# 			cleaning_list = tuple(cleaning_list)

# 			rows.append(cleaning_list)

# 			print(rows,"rose")

# 		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]

# 		for row in rows:
# 			row_num += 1
# 			for col_num in range(len(row)):
# 				ws.write(row_num, col_num, row[col_num], font_style)

# 		wb.save(response)

# 		return response

		# response_dict['response'] = response
		# responsedata = json.dumps(response_dict)

		# return Response(responsedata,HTTP_200_OK)

class ItemQuantityCheck(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict            = {'success':False}

		item_id     = request.GET.get('item_id')
		quantity 	= request.GET.get('quantity')
		store_id	= request.GET.get('store_id')
		store		= Store.objects.get(id=int(store_id))
		print(item_id,quantity,"qty")

		item = InventoryItem.objects.annotate(quantity_total=Sum('unit_item_history__quantity'),unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField()))).get(id=int(item_id))
		
		unitcount = ItemUnit.objects.filter(item=item,store=store,is_available=True).count()
		
		if item.item_add_type == 'unit':
			item_count = unitcount

			if float(item_count) >= float(quantity) :
				response_dict['item_available'] = True
				response_dict['item_quantity'] = quantity
			else:
				response_dict['item_available'] = False
				response_dict['item_quantity'] = item_count

			response_dict['item_count'] = item_count
		else:
			quantity_store = QuantityStoreDetails.objects.get(quantity_item=item,item_store=store)
			item_count = quantity_store.quantity
			
			print(item_count,"qtt")

			if float(item_count) >= float(quantity) :
				response_dict['item_available'] = True
				response_dict['item_quantity'] = quantity
			else:
				response_dict['item_available'] = False
				response_dict['item_quantity'] = round(float(item_count),2)

			item_count = float(item_count)
			print(round(item_count,3),"roun")
			response_dict['item_count'] = round(item_count,2)

		response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

class CheckOutItemAdd(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = (TokenAuthentication,)
	def get(self,request):
		response_dict            = {'success':False}

		service_item = request.GET.get('item_id')
		visit_id = request.GET.get('visit_id')
		quantity = request.GET.get('quantity')
		unit_id = request.GET.get('unit_id')
		user_id = request.GET.get('user_id')
		
		store_id = request.GET.get('store_id')
		store = Store.objects.get(id=store_id)

		print(service_item,visit_id,"vis")
		visit = OrderScheduler.objects.get(id=int(visit_id))

		item = InventoryItem.objects.get(id=int(service_item))

		combined_checkout_items_id_list = []
		checkout_items_id_list1 = CheckOutItems.objects.filter(visit=visit)
		for checkout_item in checkout_items_id_list1:
			if checkout_item.service_item:
				combined_checkout_items_id_list.append(int(checkout_item.service_item.item.id))
			else:
				combined_checkout_items_id_list.append(int(checkout_item.item.id))

		print(combined_checkout_items_id_list,"idlist")

		if int(service_item) in combined_checkout_items_id_list :
			response_dict['message'] = 'Item Already Added'
			print("itemadddoret")
		else:
			print("itemaddd")
			if item.item_status == 'available' or item.item_status == 'about_to_finish':

				if unit_id:
					itemunit = ItemUnit.objects.get(id=int(unit_id),is_available=True)
					checkout_item = CheckOutItems.objects.create(visit=visit,item=item,units=1,item_unit=itemunit)
					response_dict['message'] = 'Item Added'
				else:
					checkout_item = CheckOutItems.objects.create(visit=visit,item=item,units=quantity)

					#updating itemhistory and store quantity in case of submitted check-out
					if visit.stock_out_items_submitted == True:
						try:
							quantitystore = QuantityStoreDetails.objects.get(item_store=store,quantity_item = checkout_item.item)
							if float(quantitystore.quantity) >= float(quantity):
								quantitystore.quantity = float(quantitystore.quantity) - float(quantity)
								quantitystore.save()
						except:
							quantitystore = QuantityStoreDetails.objects.create(
							item_store = store,
							quantity_item = checkout_item.item
							)

						if float(quantitystore.quantity) >= float(quantity):
							inventory_item = checkout_item.item
							inventory_item.total_quantity = float(inventory_item.total_quantity) - float(quantity)
							inventory_item.save()

							ItemHistory.objects.create(
							item = checkout_item.item,
							quantity = quantity,
							item_action='STOCK OUT',
							quantity_location=store,
							item_remark=checkout_item.visit.order.order_no,
							purchase_date= date.today(),
							added_by = UserProfile.objects.get(id=user_id)
							
							)

							response_dict['message'] = 'Item Added'
						else:
							response_dict['message'] = 'Store quantity low'

				response_dict['checkout_item_id'] = checkout_item.id
				response_dict['item_id'] = checkout_item.item.id
				response_dict['item_name'] = checkout_item.item.name
				response_dict['item_code'] = checkout_item.item.item_code
				
				if checkout_item.item_unit:
					response_dict['unit_code'] = checkout_item.item_unit.unit_code
				else:
					response_dict['unit_code'] = '-'

				response_dict['item_quantity'] = checkout_item.units

				if checkout_item.item.item_add_type == 'unit':
					response_dict['item_unit'] = 'unit'
					response_dict['item_type'] = 'unit'
					
				else:
					response_dict['item_unit'] = checkout_item.item.measuring_unit
					response_dict['item_type'] = 'quantity'
			else:
				response_dict['message'] = 'Out of stock'

			response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

class CheckOutItemEdit(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict            = {'success':False}

		checkout_item_id = request.GET.get('checkout_item_id')
		edit_item_id = request.GET.get('edit_item_id')
		visit_id = request.GET.get('visit_id')
		quantity = request.GET.get('quantity')
		unit_id = request.GET.get('unit_id')
		user_id = request.GET.get('user_id')

		print(visit_id,quantity,"vis")
		visit = OrderScheduler.objects.get(id=int(visit_id))

		if checkout_item_id:
			if unit_id:
				itemunit = ItemUnit.objects.get(id=int(unit_id),is_available=True)
				
				checkout_item = CheckOutItems.objects.get(id=int(checkout_item_id),visit=visit)
				checkout_item.item_unit = itemunit
				checkout_item.units = 1
				checkout_item.save()
			else:
				checkout_item = CheckOutItems.objects.get(id=int(checkout_item_id),visit=visit)
				current_quantity = checkout_item.units
				checkout_item.units = quantity
				checkout_item.save()

				#updating itemhistory and store quantity in case of submitted check-out
				# if visit.stock_out_items_submitted == True:
				# 	quantity_difference = abs(float(current_quantity)-float(quantity))
				# 	try:
				# 		quantitystore = QuantityStoreDetails.objects.get(item_store=store,quantity_item = checkout_item.item)
				# 		quantitystore.quantity = float(quantitystore.quantity) - float(quantity_difference)
				# 		quantitystore.save()
				# 	except:
				# 		QuantityStoreDetails.objects.create(
				# 		item_store = store,
				# 		quantity_item = checkout_item.item,
				# 		quantity = float(quantity_difference)
				# 		)

				# 	inventory_item = checkout_item.item
				# 	inventory_item.total_quantity = float(inventory_item.total_quantity) - float(quantity_difference)
				# 	inventory_item.save()

				# 	ItemHistory.objects.create(
				# 	item = checkout_item.item,
				# 	quantity = quantity_difference,
				# 	item_action='STOCK OUT',
				# 	quantity_location=store,
				# 	item_remark=checkout_item.visit.order.order_no,
				# 	purchase_date= date.today(),
				# 	added_by = UserProfile.objects.get(id=user_id)
					
				# 	)

			response_dict['message'] = 'Item Updated'
		
			
			response_dict['checkout_item_id'] = checkout_item.id
			
			if checkout_item.service_item :
				response_dict['item_id'] = checkout_item.service_item.item.id
				response_dict['item_name'] = checkout_item.service_item.item.name
				response_dict['item_code'] = checkout_item.service_item.item.item_code

				if checkout_item.service_item.item.item_add_type == 'unit':
					response_dict['item_unit'] = 'unit'
					response_dict['item_type'] = 'unit'
				else:
					response_dict['item_unit'] = checkout_item.service_item.item.measuring_unit
					response_dict['item_type'] = 'quantity'

			else:
				response_dict['item_id'] = checkout_item.item.id
				response_dict['item_name'] = checkout_item.item.name
				response_dict['item_code'] = checkout_item.item.item_code

				if checkout_item.item.item_add_type == 'unit':
					response_dict['item_unit'] = 'unit'
					response_dict['item_type'] = 'unit'
				else:
					response_dict['item_unit'] = checkout_item.item.measuring_unit
					response_dict['item_type'] = 'quantity'
			
			if checkout_item.item_unit:
				response_dict['unit_code'] = checkout_item.item_unit.unit_code
			else:
				response_dict['unit_code'] = '-'

			response_dict['item_quantity'] = checkout_item.units
			response_dict['success'] = True

		else:
			response_dict['message'] = 'Out of stock'
		

		return Response(response_dict, HTTP_200_OK)

class CheckOutItemUnitsList(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict         = {'success':False}

		checkout_item_id = request.GET.get('checkout_item_id')
		print(checkout_item_id,"pry")
		checkout_item = CheckOutItems.objects.get(id=int(checkout_item_id))
		print(checkout_item,"unitttrroo")
		
		checkout_item_units = CheckOutItemUnits.objects.filter(checkout_item__id=int(checkout_item_id))
		print(checkout_item_units,"unittt")
		
		# for item units listing in popup
		item_units_list = []
		checkout_unit_id_list = []

		for unit in checkout_item_units:
			checkout_unit_id_list.append(unit.item_unit.id)

			if unit.item_unit.unit_serial_number:
				serial_no = unit.item_unit.unit_serial_number
			else:
				serial_no = '-'

			if unit.item_unit.expiry_date:
				expiry_date = datetime.strftime(unit.item_unit.expiry_date,'%d-%m-%Y')
			else:
				expiry_date = '-'

			item_unit_dict = {
				'item_unit_id' : unit.id,
				'item_unit_code' : unit.item_unit.unit_code,
				'item_unit_serial_no' : serial_no,
				'item_unit_expiry' : expiry_date,
			}
			item_units_list.append(item_unit_dict)

		
		# for unit dropdown
		if checkout_item.service_item:
			units_list = ItemUnit.objects.filter(item=checkout_item.service_item.item,is_available=True)
		else:
			units_list = ItemUnit.objects.filter(item=checkout_item.item,is_available=True)

		print(checkout_unit_id_list,"udroplist")
		unit_dropdown_list = []

		for unit in units_list:

			if unit.id not in checkout_unit_id_list:
				print(unit.id,"eyed")
				unit_dropdown_dict = {
					'unit_id' : unit.id,
					'unit_code' : unit.unit_code
				}

				unit_dropdown_list.append(unit_dropdown_dict)


		response_dict['success'] = True
		response_dict['item_units_list'] = item_units_list
		response_dict['checkout_item_id'] = checkout_item_id
		response_dict['unit_dropdown_list'] = unit_dropdown_list

		return Response(response_dict, HTTP_200_OK)

class CheckOutItemDelete(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict            = {'success':False}

		checkout_item = request.GET.get('item_id')

		visit_id = request.GET.get('visit_id') #for resetting recipe list
		
		deleted_items_list = []

		if visit_id:
			checkout_items = CheckOutItems.objects.filter(visit__id=int(visit_id)).delete()
			visit = OrderScheduler.objects.get(id=int(visit_id))
			visit.stock_out_items_saved = False
			visit.save()
		else:
			checkout_item_id_list = checkout_item.split(",")

			for i in range(0,len(checkout_item_id_list)):
				checkout_item = CheckOutItems.objects.get(id=int(checkout_item_id_list[i]))
				deleted_items_list.append(checkout_item.id)

				checkout_item.delete()
				
		response_dict['deleted_items_list'] = deleted_items_list

		response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

class CheckOutItemSwap(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict            = {'success':False}

		checkout_item = request.GET.get('service_item')
		ingredient_id = request.GET.get('ingredient_id')
		checkout_item_id = request.GET.get('checkout_item_id')
		quantity = request.GET.get('quantity')
		print(checkout_item_id,checkout_item,"mpl")
		checkout = CheckOutItems.objects.get(id=int(checkout_item_id))

		ingredient = ServiceRecipeIngredients.objects.get(id=int(ingredient_id))

		swap_item = ServiceRecipeItems.objects.get(ingredient=ingredient,item__id=int(checkout_item))
		print(swap_item,"swp")

		if float(quantity) > 0 :
			print("rorraaappp")
			if checkout.service_item.item.item_add_type == 'unit':
				print("rorraaa")
				CheckOutItemUnits.objects.filter(checkout_item=checkout).delete()

			if swap_item.item.item_add_type == 'unit':
				itemunits = ItemUnit.objects.filter(item__id=int(swap_item.item.id),is_available=True)[:int(quantity)]

				for unit in itemunits:
					CheckOutItemUnits.objects.create(checkout_item=checkout,item_unit=unit)

			checkout.service_item = swap_item
			checkout.units = quantity
			checkout.is_swapped_item = True
			checkout.save()

			response_dict['ingredient_id'] = ingredient.id
			response_dict['ingredient_name'] = ingredient.ingredient
			response_dict['checkout_item_id'] = checkout.id
			response_dict['item_id'] = checkout.service_item.item.id
			response_dict['item_name'] = checkout.service_item.item.name
			response_dict['item_code'] = checkout.service_item.item.item_code

			if checkout.item_unit:
				response_dict['unit_code'] = checkout.item_unit.unit_code
			else:
				response_dict['unit_code'] = '-'

			if checkout.service_item.item.item_add_type == 'unit':
				response_dict['item_unit'] = 'unit(S)'
				response_dict['item_type'] = 'unit'
			else:
				response_dict['item_unit'] = checkout.service_item.item.measuring_unit
				response_dict['item_type'] = 'quantity'

			# response_dict['item_count'] = checkout_items_count + 1

			response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

class CheckOutItemUnitSwap(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict            = {'success':False}

		checkout_unit_id = request.GET.get('checkout_unit_id')
		swap_unit_id = request.GET.get('swap_unit_id')
		
		swap_unit = ItemUnit.objects.get(id=int(swap_unit_id))

		checkout_unit = CheckOutItemUnits.objects.get(id=int(checkout_unit_id))
		checkout_unit.item_unit = swap_unit
		checkout_unit.save()

		# response_dict['item_count'] = checkout_items_count + 1

		response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

class CheckOutItemSubmit(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict            = {'success':False}

		checkout_item = request.GET.get('item_id')
		checkout_item = CheckOutItems.objects.get(id=int(checkout_item))
		checkout_item_id = checkout_item.id

		checkout_item.delete()
		
		response_dict['checkout_item_id'] = checkout_item_id

		response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)

class ItemCollectAPI(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def post(self,request):
		response_dict            = {'success':True}

		item_ids     = request.data.get('item_ids')
		visit_id     = request.data.get('visit_id')

		print(item_ids,visit_id,"mko")
		
		tl_user = UserProfile.objects.get(id=int(request.data.get('user_id')))

		for item_id in item_ids:
			cleaning_item = CheckOutItems.objects.get(id=item_id)
			cleaning_item.is_collected = True
			cleaning_item.is_collected_by = tl_user
			cleaning_item.save()

		visit = OrderScheduler.objects.get(id=visit_id)
		visit.items_collected = True
		visit.save()

		return Response(response_dict, HTTP_200_OK)

class ItemsCheckInAPI(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict = {'success':True}

		visit_id    = request.GET.get('item_user')

		print(visit_id,"lpo")

		visit = OrderScheduler.objects.prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).get(id=int(visit_id))

		for team in visit.cleaning_team:
			team_leader = team.team_leader.name
			response_dict['team_leader'] = team_leader

		return_items = CheckOutItems.objects.filter(is_checked_in=False,visit=visit)
		

		items_list = []
		item_order_no = visit.order.order_no
		item_visit_id = visit.id

		for item in return_items:

			if item.service_item:
				if item.service_item.item.item_add_type == 'unit':
					if item.item_unit:
						item_code = item.item_unit.unit_code
					else:
						item_code = '-'
				else:
					item_code = item.service_item.item.item_code

				if item.service_item.item.is_reusable == True:
					item_dict = {
						'item_id' : item.id,
						'item_name' : item.service_item.item.name,
						'item_code' : item_code,
						'item_type' : item.service_item.item.item_add_type,
						'quantity' : item.units
					}
					items_list.append(item_dict)
			
			if item.item:
				if item.item.item_add_type == 'unit':
					if item.item_unit:
						item_code = item.item_unit.unit_code
					else:
						item_code = '-'
				else:
					item_code = item.item.item_code

				if item.item.is_reusable == True:
					item_dict = {
						'item_id' : item.id,
						'item_name' : item.item.name,
						'item_code' : item_code,
						'item_type' : item.item.item_add_type,
						'quantity' : item.units
					}
					items_list.append(item_dict)

		response_dict['items_list'] = items_list
		response_dict['order_no'] = item_order_no
		response_dict['visit_id'] = item_visit_id

		print(items_list,"ret")

		return Response(response_dict, HTTP_200_OK)

	def post(self,request):
		
		item_ids    = request.data.get('item_ids')
		item_quantities   = request.data.get('quantities')
		user_id = request.data.get('inventory_user')
		store_id = request.data.get('store_id')
		store = Store.objects.get(id=int(store_id))
		inventory_user = UserProfile.objects.get(id=int(user_id))
		visit_id = request.data.get('visit_id')
		print(item_quantities,"qts")

		count = 0
		
		for item_id in item_ids:
			checkin_item = CheckOutItems.objects.prefetch_related(Prefetch('checkoutitem',CheckOutItemUnits.objects.all(),to_attr="checkin_item_units")).get(id=int(item_id),is_checked_in=False)
			checkout_visit = OrderScheduler.objects.prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).get(id=int(checkin_item.visit.id))

			for team in checkout_visit.cleaning_team:
				team_leader = team.team_leader

			visits = OrderScheduler.objects.filter(order__order_no=checkout_visit.order.order_no,start_at=checkout_visit.start_at,cleaning_team_order_scheduler__team_leader=team_leader)

			print(item_quantities[count],"iom")
			checkin_item.is_checked_in = True
			checkin_item.check_in_user = UserProfile.objects.get(id=int(request.data.get('inventory_user')),is_active=True)
			
			if checkin_item.item and checkin_item.item.item_add_type == 'unit':
				if checkin_item.item_unit:
					inventoryitemunit = ItemUnit.objects.get(id=int(checkin_item.item_unit.id))
					inventoryitemunit.status = 'working'
					inventoryitemunit.store = store
					inventoryitemunit.is_available=True
					inventoryitemunit.save()
					print("pam")
				else:
					for itemunit in checkin_item.checkin_item_units:
						inventoryitemunit = ItemUnit.objects.get(id=int(itemunit.item_unit.id))
						inventoryitemunit.status = 'working'
						inventoryitemunit.store = store
						inventoryitemunit.is_available=True
						inventoryitemunit.save()

			if checkin_item.service_item and checkin_item.service_item.item.item_add_type == 'unit':
				if checkin_item.item_unit:
					inventoryitemunit = ItemUnit.objects.get(id=int(checkin_item.item_unit.id))
					inventoryitemunit.status = 'working'
					inventoryitemunit.store = store
					inventoryitemunit.is_available=True
					inventoryitemunit.save()
				else:
					for itemunit in checkin_item.checkin_item_units:
						print(itemunit.item_unit.id,"itunitid")
						inventoryitemunit = ItemUnit.objects.get(id=int(itemunit.item_unit.id))
						inventoryitemunit.status = 'working'
						inventoryitemunit.store = store
						inventoryitemunit.is_available=True
						inventoryitemunit.save()

			if checkin_item.item and checkin_item.item.item_add_type == 'quantity' and float(item_quantities[count]) > 0:
				print("pam")
				inventoryitem = InventoryItem.objects.get(id=int(checkin_item.item.id))
				inventoryitem.total_quantity = float(inventoryitem.total_quantity) + float(item_quantities[count])
				inventoryitem.save()

				try:
					quantitystore = QuantityStoreDetails.objects.get(item_store=store,quantity_item = checkin_item.item)
					quantitystore.quantity = float(quantitystore.quantity) + float(item_quantities[count])
					quantitystore.save()
				except:
					QuantityStoreDetails.objects.create(
					item_store = store,
					quantity_item = checkin_item.item,
					quantity = float(item_quantities[count])
					)

				ItemHistory.objects.create(
				item = inventoryitem,
				quantity = item_quantities[count],
				item_action='STOCK IN',
				quantity_location=store,
				item_remark=checkin_item.visit.order.order_no,
				purchase_date= date.today(),
				added_by = team_leader
				)

				count += 1

			if checkin_item.service_item and checkin_item.service_item.item.item_add_type == 'quantity' and float(item_quantities[count]) > 0:
				inventoryitem = InventoryItem.objects.get(id=int(checkin_item.service_item.item.id))
				inventoryitem.total_quantity = float(inventoryitem.total_quantity) + float(item_quantities[count])
				inventoryitem.save()

				try:
					quantitystore = QuantityStoreDetails.objects.get(item_store=store,quantity_item = checkin_item.service_item.item)
					quantitystore.quantity = float(quantitystore.quantity) + float(item_quantities[count])
					quantitystore.save()
				except:
					QuantityStoreDetails.objects.create(
					item_store = store,
					quantity_item = checkin_item.service_item.item,
					quantity = float(item_quantities[count])
					)

				ItemHistory.objects.create(
				item = inventoryitem,
				quantity = item_quantities[count],
				item_action='STOCK IN',
				quantity_location=store,
				item_remark=checkin_item.visit.order.order_no,
				purchase_date= date.today(),
				added_by = team_leader
				)

				count += 1

			checkin_item.save()

			for visit in visits:
				visit.stock_in_initiated = True
				visit.save()

		#saving check in status if items are empty
		checkout_visit = OrderScheduler.objects.prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).get(id=int(visit_id))
		
		for team in checkout_visit.cleaning_team:
			team_leader = team.team_leader

		visits = OrderScheduler.objects.filter(order__order_no=checkout_visit.order.order_no,start_at=checkout_visit.start_at,cleaning_team_order_scheduler__team_leader=team_leader)

		for visit in visits:
			visit.stock_in_initiated = True
			visit.save()

		response_dict = {'success':True}

		return Response(response_dict, HTTP_200_OK)


class InventoryRawMaterialsView(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request,inventory_id):
		response_dict            = {'success':False}

		response_dict['success'] = True

		inventory_item     = InventoryItem.objects.get(id=inventory_id)

		if inventory_item.item_type == 'FINISHED GOODS':
			try:
				# inventory_items = InventoryItem.objects.filter(Q(Q(item_type='RAW MATERIALS')|Q(item_type='ASSETS'))).filter(status=True)
				inventory_items = InventoryItem.objects.filter(status=True)
			except:
				inventory_items = None
		else:
			try:
				# inventory_items = InventoryItem.objects.filter(item_type='RAW MATERIALS',status=True)
				inventory_items = InventoryItem.objects.filter(status=True)
			except:
				inventory_items = None

		print(inventory_items,"inventory_items")

		inventoryitem_list = []
		if inventory_items:
			for inventory_item in inventory_items:
				inventoryitem_dict = {
					'accessory_id' : inventory_item.id,
					'accessory_name' : inventory_item.name,
					}
				inventoryitem_list.append(inventoryitem_dict)

		response_dict['inventoryitem_list'] = inventoryitem_list

		return Response(response_dict, HTTP_200_OK)


class InventoryAccessoryView(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request,inventory_id):

		response_dict = {'success':False}

		try:
			inventory_accessories = InventoryAccessory.objects.filter(inventory_item__id=inventory_id,status=True)
		except:
			inventory_accessories = None

		accessories_list = []
		if inventory_accessories:
			for inventory_accessory in inventory_accessories:
				accessory_dict = {
					'accessory_id' : inventory_accessory.id,
					'accessory_name' : inventory_accessory.inventory_accessory.name,
					'count' : inventory_accessory.count
				}
			
				accessories_list.append(accessory_dict)

		response_dict['accessories_list'] = accessories_list

		return Response(response_dict, HTTP_200_OK)

	def post(self,request,inventory_id):

		response_dict = {'success':False}

		action_type   =  request.data.get('action')
			

		if action_type == 'add_accessory':
			accessory_id  =	request.data.get('accessory_id')
			count         =	request.data.get('count')
			
			InventoryAccessory.objects.create(
				inventory_item_id      = inventory_id,
				inventory_accessory_id = accessory_id,
				count                  = count
				)
			
			response_dict['success'] = True

		if action_type == 'edit_accessory':
			id                  = request.data.get('id')
			accessory_id        = request.data.get('accessory_id')
			count               = request.data.get('count')

			accessory           = InventoryItem.objects.get(id=accessory_id)

			inventory_accessory               = InventoryAccessory.objects.get(id=accessory_id)
			inventory_accessory.accessory     = accessory
			inventory_accessory.count         = count
			inventory_accessory.save()

			response_dict['success'] = True

		if action_type == 'delete_accessory':
			id            = request.data.get('id')
			InventoryAccessory.objects.filter(id=id).delete()

			response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)
			
class InventoryFinshedItemView(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request,inventory_id):

		response_dict = {'success':False}

		try:
			inventory_finshed_items = InventoryFinshedItem.objects.filter(inventory_item__id=inventory_id,status=True)
		except:
			inventory_finshed_items = None

		finshed_items_list = []
		if inventory_finshed_items:
			for finshed_item in inventory_finshed_items:
				finshed_item_dict = {
					'finished_item_id' : finshed_item.id,
					'finished_item_name' : finshed_item.inventory_finished_item.name,
					'count' : finshed_item.count
				}
			
				finshed_items_list.append(finshed_item_dict)

		response_dict['finshed_items_list'] = finshed_items_list

		return Response(response_dict, HTTP_200_OK)

	def post(self,request,inventory_id):

		response_dict = {'success':False}

		action_type   =  request.data.get('action')
			

		if action_type == 'add_finished_item':
			finished_item_id  =	request.data.get('finished_item_id')
			count             =	request.data.get('count')
			print(finished_item_id,count,"addsp")
			
			InventoryFinshedItem.objects.create(
				inventory_item_id           = inventory_id,
				inventory_finished_item_id  = finished_item_id,
				count                       = count
				)
			
			response_dict['success'] = True

		if action_type == 'edit_finished_item':
			id                  = request.data.get('id')
			finished_item_id    = request.data.get('finished_item_id')
			count               = request.data.get('count')
			print(id,finished_item_id,count,"editsp")

			finished_item           = InventoryItem.objects.get(id=id)

			inventory_finished_item                           = InventoryFinshedItem.objects.get(id=finished_item_id)
			inventory_finished_item.inventory_finished_item   = finished_item
			inventory_finished_item.count                     = count
			inventory_finished_item.save()

			response_dict['success'] = True

		if action_type == 'delete_finished_item':
			id            = request.data.get('id')
			InventoryFinshedItem.objects.filter(id=id).delete()

			response_dict['success'] = True

		return Response(response_dict, HTTP_200_OK)



class ExternalCustomersView(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict = {'success':False}	
		
		try:
			external_customers   = ExternalCustomer.objects.filter(status=True).values('id','name')
		except:
			external_customers   = []

		print(external_customers,"excs")
		response_dict['external_customers'] = list(external_customers)
		response_dict['success']            = True

		return Response(response_dict, HTTP_200_OK)


class ItemUnitsProduct(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict = {'success':False}	
		
		product_id  = request.GET.get('product_id')
		visit_id = request.GET.get('visit_id')
		store_id = request.GET.get('store_id')
		
		try:
			store= Store.objects.get(id=int(store_id))
		except:
			store=None

		item_units_array = []
		checkout_item_units_array = []

		if store:
			item_units       = ItemUnit.objects.filter(item__id=product_id,store=store,is_available=True)
		else:
			item_units       = ItemUnit.objects.filter(item__id=product_id,is_available=True)

		for item in item_units:
			item_units_array.append({'id':item.id,'unit_code':item.unit_code})

			if visit_id:
				visit = OrderScheduler.objects.get(id=int(visit_id))
				try:
					CheckOutItems.objects.get(visit=visit,item_unit=item)
				except:
					checkout_item_units_array.append({'id':item.id,'unit_code':item.unit_code})

		print(item_units_array,checkout_item_units_array,"uarr")
		print(checkout_item_units_array,"uarr2")
		response_dict['item_units'] = item_units_array
		response_dict['checkout_item_units'] = checkout_item_units_array
		response_dict['success']    = True

		return Response(response_dict, HTTP_200_OK)

class ItemStores(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict = {'success':False}	
		
		stores       = Store.objects.all()
		
		store_array = []

		for store in stores:
			store_array.append({'id':store.id,'store_name':store.store_name})

		print(store_array,"uarr2")
		response_dict['stores'] = store_array
		response_dict['success']    = True

		return Response(response_dict, HTTP_200_OK)


class CheckOutStoreItemsUpdateAPI(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()
	def get(self,request):
		response_dict = {'success':True}

		visit_id    = request.GET.get('item_user')

		print(visit_id,"lpo")

		visit = OrderScheduler.objects.prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).get(id=int(visit_id))

		for team in visit.cleaning_team:
			team_leader = team.team_leader.name
			response_dict['team_leader'] = team_leader

		return_items = CheckOutItems.objects.filter(is_checked_in=False,visit=visit)
		

		items_list = []

		for item in return_items:

			if item.service_item:
				if item.service_item.item.item_add_type == 'unit':
					if item.item_unit:
						item_code = item.item_unit.unit_code
					else:
						item_code = '-'
				else:
					item_code = item.service_item.item.item_code

				if item.service_item.item.is_reusable == True:
					item_dict = {
						'item_id' : item.id,
						'item_name' : item.service_item.item.name,
						'item_code' : item_code,
						'item_type' : item.service_item.item.item_add_type,
						'quantity' : item.units
					}
					items_list.append(item_dict)
			
			if item.item:
				if item.item.item_add_type == 'unit':
					if item.item_unit:
						item_code = item.item_unit.unit_code
					else:
						item_code = '-'
				else:
					item_code = item.item.item_code

				if item.item.is_reusable == True:
					item_dict = {
						'item_id' : item.id,
						'item_name' : item.item.name,
						'item_code' : item_code,
						'item_type' : item.item.item_add_type,
						'quantity' : item.units
					}
					items_list.append(item_dict)

		response_dict['items_list'] = items_list
		response_dict['order_no'] = item.visit.order.order_no,

		print(items_list,"ret")

		return Response(response_dict, HTTP_200_OK)

	def post(self,request):
		
		item_ids    = request.data.get('item_ids')
		item_quantities   = request.data.get('quantities')
		user_id = request.data.get('inventory_user')
		inventory_user = UserProfile.objects.get(id=int(user_id))
		print(item_quantities,"qts")

		count = 0

		for item_id in item_ids:
			checkin_item = CheckOutItems.objects.prefetch_related(Prefetch('checkoutitem',CheckOutItemUnits.objects.all(),to_attr="checkin_item_units")).get(id=int(item_id),is_checked_in=False)
			checkout_visit = OrderScheduler.objects.prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).get(id=int(checkin_item.visit.id))

			for team in checkout_visit.cleaning_team:
				team_leader = team.team_leader

			visits = OrderScheduler.objects.filter(order__order_no=checkout_visit.order.order_no,start_at=checkout_visit.start_at,cleaning_team_order_scheduler__team_leader=team_leader)

			print(item_quantities[count],"iom")
			checkin_item.is_checked_in = True
			checkin_item.check_in_user = UserProfile.objects.get(id=int(request.data.get('inventory_user')),is_active=True)
			
			if checkin_item.item and checkin_item.item.item_add_type == 'unit':
				if checkin_item.item_unit:
					inventoryitemunit = ItemUnit.objects.get(id=int(checkin_item.item_unit.id))
					inventoryitemunit.status = 'working'
					inventoryitemunit.is_available=True
					inventoryitemunit.save()
					print("pam")
				else:
					for itemunit in checkin_item.checkin_item_units:
						inventoryitemunit = ItemUnit.objects.get(id=int(itemunit.item_unit.id))
						inventoryitemunit.status = 'working'
						inventoryitemunit.is_available=True
						inventoryitemunit.save()

			if checkin_item.service_item and checkin_item.service_item.item.item_add_type == 'unit':
				if checkin_item.item_unit:
					inventoryitemunit = ItemUnit.objects.get(id=int(checkin_item.item_unit.id))
					inventoryitemunit.status = 'working'
					inventoryitemunit.is_available=True
					inventoryitemunit.save()
				else:
					for itemunit in checkin_item.checkin_item_units:
						print(itemunit.item_unit.id,"itunitid")
						inventoryitemunit = ItemUnit.objects.get(id=int(itemunit.item_unit.id))
						inventoryitemunit.status = 'working'
						inventoryitemunit.is_available=True
						inventoryitemunit.save()

			if checkin_item.item and checkin_item.item.item_add_type == 'quantity' and float(item_quantities[count]) > 0:
				print("pam")
				inventoryitem = InventoryItem.objects.get(id=int(checkin_item.item.id))
				inventoryitem.total_quantity = float(inventoryitem.total_quantity) + float(item_quantities[count])
				inventoryitem.save()

				ItemHistory.objects.create(
				item = inventoryitem,
				quantity = item_quantities[count],
				item_action='STOCK IN',
				quantity_location=store,
				item_remark=checkin_item.visit.order.order_no,
				purchase_date= date.today(),
				added_by = team_leader
				)

				count += 1

			if checkin_item.service_item and checkin_item.service_item.item.item_add_type == 'quantity' and float(item_quantities[count]) > 0:
				inventoryitem = InventoryItem.objects.get(id=int(checkin_item.service_item.item.id))
				inventoryitem.total_quantity = float(inventoryitem.total_quantity) + float(item_quantities[count])
				inventoryitem.save()

				ItemHistory.objects.create(
				item = inventoryitem,
				quantity = item_quantities[count],
				item_action='STOCK IN',
				quantity_location=store,
				item_remark=checkin_item.visit.order.order_no,
				purchase_date= date.today(),
				added_by = team_leader
				)

				count += 1

			checkin_item.save()

			for visit in visits:
				visit.stock_in_initiated = True
				visit.save()

		response_dict = {'success':True}

		return Response(response_dict, HTTP_200_OK)

class XeroInfoSaveAPI(APIView):
	permission_classes        = (AllowAny,)
	authentication_classes    = ()

	def get(self,request):
		response_dict = {'success':False}
		code          = request.GET.get('code')
		xero          = XeroConnection.objects.first()
		
		#Get access Token and Refresh Token
		header                      = {
											'Authorization': 'Basic '+xero.client_encoded,
											'Content-Type': 'application/x-www-form-urlencoded'
									  }
		body                        = {"grant_type":"authorization_code","code":code,"redirect_uri":"https://my.bleachkw.com/api/xero/save/"}
		token_response              = requests.post('https://identity.xero.com/connect/token',
												data=body,
												headers=header 
											).json()
									
		access_token                = token_response['access_token']
		refresh_token               = token_response['refresh_token']

		#Get Tenant Id
		header                      = {
										'Authorization': 'Bearer '+access_token,
										'Content-Type': 'application/json'
											}
		body                        = {}
		response                    = requests.get('https://api.xero.com/connections',
												data=body,
												headers=header 
											)	
		tenant_response             = json.loads(response.text)[0]	
		tenantid                    = tenant_response['tenantId']
		
		xero.access_token  = access_token
		xero.refresh_token = refresh_token
		xero.tenant_id     = tenantid
		xero.save()

		response_dict = {'success':True}
		return Response(response_dict, HTTP_200_OK)



class DailyTransactionsAPI(APIView):
	def get(self,request):
		response_dict = {'success':False}

		date         = datetime.strptime(request.GET.get('date'),'%d-%m-%Y')
		payments     = PaymentHistory.objects.filter(paid_date__date=date)
		
		response_dict['date']         = datetime.strftime(date,'%Y-%m-%d')
		if payments:
			response_dict['total_debit']  = payments.filter(payment_mode='ONLINECREDIT',payment_gateway='DEBITCARD').aggregate(Sum('amount_paid'))['amount_paid__sum']
			response_dict['total_credit'] = payments.filter(payment_mode='ONLINECREDIT',payment_gateway='CREDITCARD').aggregate(Sum('amount_paid'))['amount_paid__sum']
			response_dict['total_cheque'] = payments.filter(payment_mode='CHEQUE').aggregate(Sum('amount_paid'))['amount_paid__sum']
			response_dict['total_cash']   = payments.filter(payment_mode='CASH').aggregate(Sum('amount_paid'))['amount_paid__sum']
			response_dict['total_bank']   = payments.filter(payment_mode='BANK').aggregate(Sum('amount_paid'))['amount_paid__sum']
		else:
			response_dict['total_debit']  = 0
			response_dict['total_credit'] = 0
			response_dict['total_cheque'] = 0
			response_dict['total_cash']   = 0
			response_dict['total_bank']   = 0

		return Response(response_dict, HTTP_200_OK)

class ServiceProductivityAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}

		try:
			service_productivities = ServiceProductivity.objects.filter(is_active=True)
		except:
			service_productivities = None

		service_productivity_serializer = ServiceProductivitySerializer(service_productivities,many=True).data
		response_dict["service_productivities"]=service_productivity_serializer
		return Response(response_dict,HTTP_200_OK)

class ServicePriceRangeAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,cleaning_type):
		response_dict = {}

		try:
			service_price_ranges = ServicePriceRange.objects.filter(is_active=True,service_type__name__icontains=cleaning_type)
		except:
			service_price_ranges = None

		service_price_range_serializer = ServicePriceRangeSerializer(service_price_ranges,many=True).data
		response_dict["service_price_ranges"]=service_price_range_serializer
		return Response(response_dict,HTTP_200_OK)

class ServiceAddOnsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request,cleaning_type):
		response_dict = {}

		try:
			service_add_ons = ServiceAddOns.objects.filter(is_active=True,service_type__name__icontains=cleaning_type)
		except:
			service_add_ons = None

		service_add_ons_serializer = ServiceAddOnsSerializer(service_add_ons,many=True).data
		response_dict["service_add_ons"]=service_add_ons_serializer
		return Response(response_dict,HTTP_200_OK)
