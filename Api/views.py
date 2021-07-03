from django.shortcuts import render
from django.template.loader import render_to_string
from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule,Shift
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking
from bleachadmin.models import ServicePriceRange
from django.core.mail import send_mail,EmailMultiAlternatives
from Api.serializers import UserProfileSerializer, EvaluationSerializer, LeaveScheduleSerializer, LeaveUsersSerializer,ShiftScheduleSerializer
from agent.views import generate_random_username

import re
import random
import string
import functools
import operator
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta,date,datetime
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from django.db.models.functions import Cast,TruncDate,ExtractMonth,ExtractYear,Concat
from django.db.models import Prefetch
from dateutil.relativedelta import relativedelta
import pandas as pd

from datetime import date
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK 
from rest_framework import status

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

		if slot_count_check > 1:
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

		print(evaluation_details.evaluation.evaluation_id,"evid")

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

		response_dict["agent_notes"]=evaluation_details.attender_note
		response_dict["customer"]=evaluation_details.evaluation.customer.name 
		response_dict["customer_mobile"]=evaluation_details.evaluation.customer.mobile_number 
		response_dict["location"]=evaluation_details.address.location 
		response_dict["customer_address"]=separator.join(address_list)
		response_dict["evaluation_date"]=proposed_date.strftime('%d-%m-%Y')
		response_dict["evaluation_time"]=proposed_time.strftime('%I:%M %p')
		response_dict["evaluation_slot"]=proposed_time.strftime('%H:%M')
		response_dict["agent_evaluation_notes"]=evaluation_details.attender_note 
		
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
		print(payment_result)
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
			order_closing_check = Order.objects.select_related('evaluation__customer').filter(is_active=True,order_no=evaluation_id,payment_status='COMPLETED').order_by('-id').prefetch_related(Prefetch('order_scheduler_order',queryset=OrderScheduler.objects.filter(is_active=True)),Prefetch('investigation_orders',queryset=Investigation.objects.filter(is_active=True).prefetch_related(Prefetch('followup_investigation',queryset=FollowUp.objects.filter(is_active=True))))).annotate(cleaning_count=Count('order_scheduler_order'),followup_count=Count('investigation_orders'),completed_followup_count=Sum(Case(When(investigation_orders__followup_investigation__status='FOLLOWUP_CLOSED',then=1),default=0,output_field=IntegerField())),completed_cleaning_count=Sum(Case(When(order_scheduler_order__work_status='CLEANING_FULFILLED',then=1),default=0,output_field=IntegerField()))).filter(cleaning_count=F('completed_cleaning_count'),followup_count=F('completed_followup_count'))
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
class LeaveUsersList(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}

		try:
			staffs = UserProfile.objects.filter(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))
		except:
			staffs = None
		
		staff_serializer = LeaveUsersSerializer(staffs,many=True).data
		response_dict["staffs"]=staff_serializer
		return Response(response_dict,HTTP_200_OK)

#get existing leave schedules and add new leaveschedules
class LeaveScheduleAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}

		try:
			leaveschedules = LeaveSchedule.objects.filter(is_active=True)
		except:
			leaveschedules = None

		print(leaveschedules,"lvsched")
		leaveschedule_serializer = LeaveScheduleSerializer(leaveschedules,many=True).data
		response_dict["staffs"]=leaveschedule_serializer
		return Response(response_dict,HTTP_200_OK)
	
	def post(self,request):
		response_dict = {'success':False}

		for schedule in request.data:
			serializer = LeaveScheduleSerializer(data=schedule)
			
			if serializer.is_valid(): 
				serializer.save()
   
			else: 
				errors= serializer.errors   
				key=tuple(errors.keys())[0] 
				error=errors[key]
				response_dict['Error']=key +':'+ error[0]
				response_dict['Error_List'] = serializer.errors

		response_dict['success']  = True  

		return Response(response_dict,HTTP_200_OK)

#Get Existing Shift
class ShiftScheduleAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}

		try:
			shiftschedules = ShiftSchedule.objects.filter(is_active=True)
		except:
			shiftschedules = None

		shiftschedule_serializer = ShiftScheduleSerializer(shiftschedules,many=True).data

		response_dict["staffs"]  = shiftschedule_serializer
		response_dict["success"]  = True

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
			leavescehdule = LeaveSchedule.objects.get(is_active=True,id=int(leave_id))
		except:
			leaveschedule = None

		if leavescehdule:
			leavescehdule.delete()
			response_dict = {'success':True}  
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

class DailySalesAPI(APIView):
	permission_classes  	=   (AllowAny,)
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

		generalcleaning_month = 0
		upholsterycleaning_month = 0
		deepcleaning_month = 0
		carpetcleaning_month = 0
		kitchencleaning_month = 0
		sterilization_month = 0
		cleaning_amount_month = 0

		todate = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

		for date in daterange:
			start_date_day = date
			end_date_day   = date+timedelta(1)

			print(date.strftime("%A"),"dt")
			generalcleaning = 0
			upholsterycleaning = 0
			deepcleaning = 0
			carpetcleaning = 0
			kitchencleaning = 0
			sterilization = 0
			cleaning_amount = 0
			evaluator_amount = 0
			others = 0

			list_item = {}
		
			for evaluator in evaluators:
				eval_dict = {""+str(evaluator.name)+str(evaluator.id)+"":0}
				list_item.update(eval_dict)

			print(list_item,"elist")
			
			if date < todate:
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluator__id').order_by('end_at')
			else:
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluator__id').order_by('end_at')

			print(orderschedules.count(),"countt")
			
			found = set()
			schedules_list = []

			for schedule in orderschedules:

				#if schedule[4] not in found:
				schedules_list.append(schedule)
				#found.add(schedule[4])

			for schedule in schedules_list:

				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()

				order_amount = schedule[1]
				cleaning_amount += float(order_amount/schedule_count)
				
				#fine,promocode, write off calc
				if schedule[6] != None:
					cleaning_amount -= float(schedule[6]/schedule_count)
				if schedule[7] != None:
					cleaning_amount -= float(schedule[7]/schedule_count)
				if schedule[8] != None:
					cleaning_amount += float(schedule[8]/schedule_count)

				#adding amount to evaluators dict
				if schedule[9] != None:
					for x, y in list_item.items():
						evaluator_id = int(re.search(r'\d+', x).group(0))
						print(evaluator_id,"loll")
						if int(evaluator_id) == int(schedule[9]):
							print("evade",evaluator_id)
							evaluator_amount += float(order_amount/schedule_count)

							#fine,promocode, write off calc
							if schedule[6] != None:
								evaluator_amount -= float(schedule[6]/schedule_count)
							if schedule[7] != None:
								evaluator_amount -= float(schedule[7]/schedule_count)
							if schedule[8] != None:
								evaluator_amount += float(schedule[8]/schedule_count)

							eval_dict = {""+x+"":evaluator_amount}
							print(date,eval_dict,"evdict")
					list_item.update(eval_dict)
				else:
					others += float(order_amount/schedule_count)

					#fine,promocode, write off calc
					if schedule[6] != None:
						others -= float(schedule[6]/schedule_count)
					if schedule[7] != None:
						others -= float(schedule[7]/schedule_count)
					if schedule[8] != None:
						others += float(schedule[8]/schedule_count)						

				#cleaning type wise amount addition
				if schedule[2] == 'General Cleaning':
					generalcleaning += float(order_amount/schedule_count)

					if schedule[6] != None:
						generalcleaning -= float(schedule[6]/schedule_count)
					if schedule[7] != None:
						generalcleaning -= float(schedule[7]/schedule_count)
					if schedule[8] != None:
						generalcleaning += float(schedule[8]/schedule_count)										

				if schedule[2] == 'Upholstery Cleaning':
					upholsterycleaning += float(order_amount/schedule_count)

					if schedule[6] != None:
						upholsterycleaning -= float(schedule[6]/schedule_count)
					if schedule[7] != None:
						upholsterycleaning -= float(schedule[7]/schedule_count)
					if schedule[8] != None:
						upholsterycleaning += float(schedule[8]/schedule_count)

				if schedule[2] == 'Deep Cleaning':
					deepcleaning += float(order_amount/schedule_count)

					if schedule[6] != None:
						deepcleaning -= float(schedule[6]/schedule_count)
					if schedule[7] != None:
						deepcleaning -= float(schedule[7]/schedule_count)
					if schedule[8] != None:
						deepcleaning += float(schedule[8]/schedule_count)

				if schedule[2] == 'Kitchen Cleaning':
					kitchencleaning += float(order_amount/schedule_count)

					if schedule[6] != None:
						kitchencleaning -= float(schedule[6]/schedule_count)
					if schedule[7] != None:
						kitchencleaning -= float(schedule[7]/schedule_count)
					if schedule[8] != None:
						kitchencleaning += float(schedule[8]/schedule_count)

				if schedule[2] == 'Carpet Cleaning':
					carpetcleaning += float(order_amount/schedule_count)

					if schedule[6] != None:
						carpetcleaning -= float(schedule[6]/schedule_count)
					if schedule[7] != None:
						carpetcleaning -= float(schedule[7]/schedule_count)
					if schedule[8] != None:
						carpetcleaning += float(schedule[8]/schedule_count)
				
				if schedule[2] == 'Sterilization':
					sterilization += float(order_amount/schedule_count)

					if schedule[6] != None:
						sterilization -= float(schedule[6]/schedule_count)
					if schedule[7] != None:
						sterilization -= float(schedule[7]/schedule_count)
					if schedule[8] != None:
						sterilization += float(schedule[8]/schedule_count)
			
			
			if data_type == 'service':
				list_item = {
					'Date': str(date.date()),
					'Day': date.strftime("%A"),
					'GeneralCleaning':generalcleaning,
					'UpholsteryCleaning':upholsterycleaning,
					'KitchenCleaning':kitchencleaning,
					'CarpetCleaning':carpetcleaning,
					'DeepCleaning':deepcleaning,
					'Sterilization':sterilization,
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

			generalcleaning_month += generalcleaning
			upholsterycleaning_month += upholsterycleaning
			deepcleaning_month += deepcleaning
			kitchencleaning_month += kitchencleaning
			carpetcleaning_month += carpetcleaning
			sterilization_month += sterilization
			cleaning_amount_month += cleaning_amount

				
		response_dict = {'success':True,'datatype':data_type,'list':saleslist,'list2':evaluators_list,'list3':evaluator_list_monthly, 'todate':str(today.date()),'month_name':full_month_name,'generalcleaning_month':generalcleaning_month,'upholsterycleaning_month':upholsterycleaning_month,'deepcleaning_month':deepcleaning_month,'kitchencleaning_month':kitchencleaning_month,'carpetcleaning_month':carpetcleaning_month,'sterilization_month':sterilization_month,'cleaning_amount_month':cleaning_amount_month}

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
				print(date,"dtER")
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount').order_by('end_at')
			else:
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount').order_by('end_at')
			
			found = set()
			schedules_list = []

			for schedule in orderschedules:

				if schedule[4] not in found:
					schedules_list.append(schedule)
				found.add(schedule[4])
			print(found,schedules_list,"kio")

			for schedule in schedules_list:

				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()

				order_amount = schedule[1]
				cleaning_amount += float(order_amount/schedule_count)

				if schedule[5] != None:
					cleaning_amount -= float(schedule[5]/schedule_count)
				if schedule[6] != None:
					cleaning_amount -= float(schedule[6]/schedule_count)
				if schedule[7] != None:
					cleaning_amount += float(schedule[7]/schedule_count)
			
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
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):

		visit_count = request.GET.get('visit_count')
		schedule_id = request.GET.get('schedule_id')

		cleaningteam = CleaningTeam.objects.filter(is_active=True,order_scheduler__id=int(schedule_id)).prefetch_related(Prefetch('media_cleaningteam',queryset=CleaningTeamMedia.objects.filter(is_active=True),to_attr='cleaning_team_medias'),Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.select_related('member').filter(is_active=True),to_attr='cleaning_team_members')).first()

		if cleaningteam:

			team_members_list = []
			for team_member in cleaningteam.cleaning_team_members:
				if cleaningteam.team_leader.id != team_member.member.id :
					team_members_list.append({"member_name":team_member.member.name,"member_image":team_member.member.profile_image.url})

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

			cleaning_status = cleaningteam.order_scheduler.work_status

			followup = FollowUp.objects.filter(is_active=True,investigation__order_schedule__id=cleaningteam.order_scheduler.id).last()
			if followup:
				followup_id = followup.id
			else:
				followup_id = None

			customer_id = cleaningteam.order_scheduler.order.evaluation.customer.id
			
			print(cleaning_status,"printest")

			response_dict = {'success':True,"visit_count":visit_count,"schedule_id":schedule_id, "customer_id":customer_id,"followup_id":followup_id,"cleaning_status":cleaning_status,"team_leader":cleaningteam.team_leader.name,"team_leader_image":cleaningteam.team_leader.profile_image.url,"start_at":check_in_time,"end_at":check_out_time,'members':team_members_list, 'before_cleaning_media':before_cleaning_media_list, 'after_cleaning_media':after_cleaning_media_list}

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
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		response_dict = {}
		response_dict['success'] = False

		team_id = request.data.get('team_id')
	
		print(team_id,"zack")
		try:
			cleaning_team_detail = CleaningTeam.objects.select_related('order_scheduler__order').get(is_active=True,id=team_id)
		except:	
			cleaning_team_detail = None

		if not cleaning_team_detail.check_in:
			cleaning_team_detail.check_in                    = timezone.now()
		if not cleaning_team_detail.check_out:
			cleaning_team_detail.order_scheduler.work_status     = 'CLEANING_IN_PROGRESS'
		cleaning_team_detail.save()	
		cleaning_team_detail.order_scheduler.save()

		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				CleaningTeamMedia.objects.create(
						team_id=team_id,
						media=media,
						taken_status='BEFORE_CLEANING'
						)

		if cleaning_team_detail.is_section_updated == True:
			print("send smmsr")
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

				print(message,response.text,"respo")
		response_dict['success'] = True
		response_dict['cleaning_date'] = cleaning_team_detail.start_at.date().strftime('%d-%m-%Y')
		return Response(response_dict,HTTP_200_OK)

class CheckOutAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		response_dict = {}
		response_dict['success'] = False

		team_id = request.data.get('team_id')
	
		print(team_id,"zack")
		try:
			cleaning_team_detail = CleaningTeam.objects.select_related('order_scheduler__order').get(is_active=True,id=team_id)
		except:	
			cleaning_team_detail = None

		#remaining teams
		# cleaning_teams = CleaningTeam.objects.filter(order_scheduler__order_scheduler_book=cleaning_team_detail.order_scheduler.order_scheduler_book).values('order_scheduler__work_status')
		# remaining_team = 0
		# for team in cleaning_teams:
		# 	if team['order_scheduler__work_status'] != 'CLEANING_FULFILLED':
		# 		remaining_team += 1
		
		# print(remaining_team,"rtm")

		#remaining keynotes
		# keynotes = EvaluationSectionKeynote.objects.filter(evaluation_section__evaluation_book=cleaning_team_detail.order_scheduler.order_scheduler_book).values('completion_status')
		# remaining_keynotes = 0
		# if keynotes:
		# 	for key in keynotes:
		# 		if key['completion_status'] == False:
		# 			remaining_keynotes += 1
		# else:
		# 	pass
		# print(remaining_keynotes,"rky")


		cleaning_team_detail.order_scheduler.work_status  		= 'CLEANING_FULFILLED'	
		cleaning_team_detail.check_out                    		= timezone.now()
		
		cleaning_team_detail.order_scheduler.order.order_status = 'ORDER_IN_PROGRESS'
		
		cleaning_team_detail.save()
		cleaning_team_detail.order_scheduler.save()
		cleaning_team_detail.order_scheduler.order.save()	

		#To Save Media
		medias = request.FILES.getlist('media')
		if not medias==['']:
			for media in medias:
				CleaningTeamMedia.objects.create(
						team_id=team_id,
						media=media,
						taken_status='AFTER_CLEANING'
						)

		response_dict['success'] = True
		response_dict['cleaning_date'] = cleaning_team_detail.start_at.date().strftime('%d-%m-%Y')
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
						job_completed -= float(order.evaluation.fine_amount/cleanings_count)

					if order.evaluation.writeback_amount:
						job_completed -= float(order.evaluation.writeback_amount/cleanings_count)

					if order.evaluation.promocode_amount:
						job_completed -= float(order.evaluation.promocode_amount/cleanings_count)
				
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
		order_id = request.data.get('orderid')
		subscription_topay = request.data.get('subscription_topay',None)
		selected_options = request.data.get('selectedoptions')
		print(order_id,selected_options,subscription_topay,"opr")
		options = selected_options.split(",")

		print(options,"oid")

		if subscription_topay:
			Order.objects.filter(id=int(order_id)).update(subscription_topay=int(subscription_topay),subscription_topay_date=timezone.now())

		order = Order.objects.filter(id=int(order_id)).first()

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
		else:
			data = False

		if evaluation.customer.is_email == True or 'EMAIL' in options:
			#send mail
			msg_html = render_to_string('email/invoice.html',{"invoice":order,"address_list":separator.join(address_list),"evaluationbooks":evaluationbooks})
			msg = EmailMultiAlternatives('Bleach Invoice', '', 'notification@bleach-kw.com', [evaluation.customer.email])
			msg.attach_alternative(msg_html, "text/html")
			msg.send(fail_silently=False)
			data=True
		else:
			data = False
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