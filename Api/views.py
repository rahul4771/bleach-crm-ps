from django.shortcuts import render

from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking

from Api.serializers import UserProfileSerializer, EvaluationSerializer, LeaveScheduleSerializer, LeaveUsersSerializer
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

class DailySalesAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
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
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluator__id').order_by('end_at')
			else:
				orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).values_list('order__order_no','order_scheduler_book__total_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluator__id').order_by('end_at')

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

			

			print(cleaning_status,"printest")

			response_dict = {'success':True,"visit_count":visit_count,"cleaning_status":cleaning_status,"team_leader":cleaningteam.team_leader.name,"team_leader_image":cleaningteam.team_leader.profile_image.url,"start_at":check_in_time,"end_at":check_out_time,'members':team_members_list, 'before_cleaning_media':before_cleaning_media_list, 'after_cleaning_media':after_cleaning_media_list}

		else:

			response_dict = {'success':False}

		return Response(response_dict,HTTP_200_OK)	
