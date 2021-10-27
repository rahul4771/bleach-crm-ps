from django.shortcuts import render
import json
from django.template.loader import render_to_string
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule,Shift
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,EvaluationSectionAddons,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question,FollowUpSection,FollowUpSectionKeynote,Reporting,PaybackDiscount,PaybackDiscountDetails
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia,FollowUpTeamMedia
from accountant.models import PaymentHistory
from customer.models import CustomerBooking
from bleachadmin.models import ServicePriceRange,Settings
from django.core.mail import send_mail,EmailMultiAlternatives
from Api.serializers import DiscountSettingSerializer,UserProfileSerializer, EvaluationSerializer, LeaveScheduleSerializer, UsersListSerializer,ShiftScheduleSerializer,OccupiedMembersSerializer,InventoryLineSerializer,InventorySegmentSerializer,InventoryValueSerializer,InventoryBundleItemSerializer,InventoryItemUnitSerializer,InventorySupplierItemSerializer
from agent.views import generate_random_username
from bleachinventory.models import Line,Segment,Category,Attribute,AttributeValue,Bundle,BundleItems,InventoryItem,ItemUnit,SupplierItems,ServiceRecipe,ServiceRecipeIngredients,ServiceRecipeItems
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

from datetime import date
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK 
from rest_framework import status
from rest_framework.authentication import TokenAuthentication 
from rest_framework.authtoken.models import Token


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
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}
		month = int(request.GET.get('month'))
		year  = int(request.GET.get('year'))

		try:
			leaveschedules = LeaveSchedule.objects.filter(is_active=True,leave_date__month=month,leave_date__year=year)
		except:
			leaveschedules = None
		leaveschedule_serializer = LeaveScheduleSerializer(leaveschedules,many=True).data

		occupied_members           = CleaningTeamMember.objects.select_related('team__order_scheduler').filter( Q(Q(is_active=True) & Q(Q(Q(start_at__month=month)&Q(start_at__year=year)) | Q(Q(end_at__month=month)&Q(end_at__year=year))) ) )
		occupied_member_serializer = OccupiedMembersSerializer(occupied_members,many=True).data

		response_dict["staffs"]    = leaveschedule_serializer
		response_dict["occupied"]  = occupied_member_serializer

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
		
		actions = request.data.get('actions')
		actions_list = actions.split(",")
			
		print(visit_id,ticket_types,notes,investigationmedias,"lodat")
		
		visit = OrderScheduler.objects.get(id=int(visit_id))
		order = visit.order

		investigation = Investigation.objects.create(order=order,order_schedule=visit,ticket_types=ticket_types)

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
				secondary_investigator = request.data.get('secondary_investigator')
				print(secondary_investigator,"sec")
				investigator = UserProfile.objects.get(id=int(secondary_investigator))

				investigationdata = Investigation.objects.select_related('investigator','assigned_by','secondary_investigator','order__evaluation__customer').get(id=investigation.id,is_active=True)
				investigationdata.secondary_investigator = investigator
				investigationdata.secondary_investigation_created = datetime.now()
				investigationdata.save()
				
				msg_html = render_to_string('email/rise_ticket_request2.html',{'investigationdata':investigationdata})
				msg      = EmailMultiAlternatives('Ticket Rised', '', 'notification@bleach-kw.com', [investigationdata.secondary_investigator.email])
				msg.attach_alternative(msg_html, "text/html")
				msg.send(fail_silently=False)

		response_dict = {'success':True}

		return Response(response_dict,HTTP_200_OK)

class InvestigationFormAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		investigation_id = request.data.get('investigation_id')

		investigation = Investigation.objects.get(id=int(investigation_id))
		
		secondary_investigation_notes = request.data.get('notes')

		investigation.secondary_investigation_notes = secondary_investigation_notes
		investigation.save()
		
		#save media
		secondary_investigationmedias = request.FILES.getlist('media')
		if not investigation_medias == ['']:
			for image in investigation_medias:
				InvestigationMedia.objects.create(
					investigation = investigation,
					media = image,
					media_type = 'PHOTO',
					taken_status = 'SECONDARY_INVESTIGATION',
					is_active = True
				)

		# is_followup = request.data.get('is_followup')

		# if is_followup == True:

		# 	total_cost	= request.data.get('total_cost')
		# 	no_of_cleaners = request.data.get('number_of_cleaners')
		# 	cleaning_hours = request.data.get('cleaning_hours')
			
		# 	tendative_date = request.data.get('tendative_date').split(',')

		# 	tendative_time = request.data.get('tendative_time')

		# 	follow_up = FollowUp.objects.select_related('investigation__order__evaluation__customer').get(investigation_id=investigation_id,is_active=True)
		# 	follow_up.status         = 'FOLLOWUP_IN_PROGRESS'
		# 	follow_up.followup_notes = request.POST.get('investigator_notes')
		# 	follow_up.no_of_cleaners = no_of_cleaners
		# 	follow_up.cleaning_hours = cleaning_hours
		# 	follow_up.total_cost = total_cost
		# 	follow_up.save()

		# 	for date in tendative_date:
		# 		print(date)
		# 		start_date_time = datetime.strptime(date+' '+tendative_time,'%d-%m-%Y %I:%M %p')
		# 		end_date_time   = start_date_time + timedelta(hours=float(cleaning_hours))
		# 		followup_schedule_array.append(FollowUpScheduler(follow_up=follow_up,status='CONFIRMED',start_at=start_date_time,end_at=end_date_time,customer_address=investigation.order_schedule.customer_address))

		# 	#to save sections
		# 	no_of_sections         = int(request.POST.get('section_counter'))
		# 	section_array          = []
		# 	for i in range(no_of_sections):
		# 		section_name  = request.POST.get('section'+str(i))
		# 		size          = request.POST.get('size'+str(i))
				
		# 		wall_type     = request.POST.get('walltype'+str(i))
		# 		ceiling_type  = request.POST.get('ceilingtype'+str(i))
		# 		floor_type    = request.POST.get('floortype'+str(i))
				
		# 		section_cost  = request.POST.get('sectioncost'+str(i))

		# 		try:
		# 			section_name_arabic = Translator().translate(section_name,src='en', dest='ar').text
		# 		except:
		# 			section_name_arabic = section_name
				
		# 		section = FollowUpSection.objects.create(follow_up=follow_up,section_name=section_name,section_name_arabic=section_name_arabic,size=size,wall_type=wall_type,ceiling_type=ceiling_type,floor_type=floor_type,section_net_cost=section_cost)

		# 		#to save keynotes
		# 		try:
		# 			no_of_keynotes = int(request.POST.get('section'+str(i)+'-keynote_counter'))
		# 		except:
		# 			no_of_keynotes = None

		# 		keynote_array = []
		# 		if no_of_keynotes:
		# 			for j in range(no_of_keynotes):
		# 				keynote = request.POST.get('section'+str(i)+'_keynote'+str(j))
		# 				quantity= request.POST.get('section'+str(i)+'_quantity'+str(j))
		# 				if keynote and quantity:
		# 					keynote_array.append(FollowUpSectionKeynote(followup_section=section,sub_area=keynote,quantity=quantity))
		# 			#bulk_create keynote
		# 			FollowUpSectionKeynote.objects.bulk_create(keynote_array)

		# 	FollowUpScheduler.objects.bulk_create(followup_schedule_array)

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
					'size' : section.size,
					'floor_type' : section.floor_type,
					'wall_type' : section.wall_type,
					'ceiling_type' : section.ceiling_type,
					'section_net_cost' :section.section_net_cost,
					'keynotes' : keynotes,
					'addons' : sectionaddons
			}

			sections.append(section_dict)

		response_dict['sections'] = sections
		print(response_dict,"dict")

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
			# generalcleaning = 0
			# upholsterycleaning = 0
			# deepcleaning = 0
			# carpetcleaning = 0
			# kitchencleaning = 0
			# sterilization = 0
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
			
			# if date < todate:
			orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','order_scheduler_book__estimated_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluator__id','order_scheduler_book__evaluation_details__evaluation__discount').order_by('end_at')
			# else:
			# 	orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','order_scheduler_book__estimated_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluator__id','order_scheduler_book__evaluation_details__evaluation__discount').order_by('end_at')

			print(orderschedules.count(),"countt")
			
			found = set()
			schedules_list = []

			for schedule in orderschedules:

				#if schedule[4] not in found:
				schedules_list.append(schedule)
				#found.add(schedule[4])

			for schedule in schedules_list:

				#schedule count of order
				order_schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0]).count()

				#schedule count of evaluation book
				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()

				order_amount     = schedule[1]
				cleaning_amount += float(order_amount/schedule_count)
				
				#fine,promocode, write off calc
				if schedule[6] > 0:
					cleaning_amount -= float(schedule[6]/order_schedule_count)
				if schedule[7] > 0:
					cleaning_amount -= float(schedule[7]/order_schedule_count)
				if schedule[8] > 0:
					cleaning_amount += float(schedule[8]/order_schedule_count)
				if schedule[10] > 0:
					cleaning_amount -= float(schedule[10]/order_schedule_count)

				#adding amount to evaluators dict
				if schedule[9] != None:
					for x, y in list_item.items():
						evaluator_id = int(re.search(r'\d+', x).group(0))
						print(evaluator_id,"loll")
						if int(evaluator_id) == int(schedule[9]):
							print("evade",evaluator_id)
							evaluator_amount += float(order_amount/schedule_count)

							#fine,promocode, write off calc
							if schedule[6] > 0:
								evaluator_amount -= float(schedule[6]/order_schedule_count)
							if schedule[7] > 0:
								evaluator_amount -= float(schedule[7]/order_schedule_count)
							if schedule[8] > 0:
								evaluator_amount += float(schedule[8]/order_schedule_count)
							if schedule[10] > 0:
								evaluator_amount -= float(schedule[10]/order_schedule_count)
							

							eval_dict = {""+x+"":evaluator_amount}
							print(date,eval_dict,"evdict")
					list_item.update(eval_dict)
				else:
					others += float(order_amount/schedule_count)

					#fine,promocode, write off calc
					if schedule[6] > 0:
						others -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						others -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						others += float(schedule[8]/order_schedule_count)	
					if schedule[10] > 0:
						others -= float(schedule[10]/order_schedule_count)
					

				if date == '05-07-2021' and schedule[0] == 'BLC20210610161':
					print(schedule[2],schedule[0], float(order_amount/schedule_count)-float(schedule[6]/order_schedule_count)-float(schedule[7]/order_schedule_count)+float(schedule[8]/order_schedule_count)-float(schedule[10]/order_schedule_count),"service")
				
				#cleaning type wise amount addition
				if schedule[2] == 'General Cleaning':
					detailed_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						detailed_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						detailed_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						detailed_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Deep Cleaning':
					detailed_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						detailed_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						detailed_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						detailed_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Facade Cleaning':
					detailed_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						detailed_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						detailed_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						detailed_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Storage Area':
					detailed_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						detailed_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						detailed_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						detailed_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Car Parking Umbrella':
					detailed_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						detailed_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						detailed_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						detailed_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Window Cleaning':
					detailed_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						detailed_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						detailed_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						detailed_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Outdoor Cleaning':
					detailed_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						detailed_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						detailed_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						detailed_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						detailed_cleaning -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Upholstery Cleaning':
					special_care += float(order_amount/schedule_count)

					if schedule[6] > 0:
						special_care -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						special_care -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						special_care += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						special_care -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Mattress Cleaning':
					special_care += float(order_amount/schedule_count)

					if schedule[6] > 0:
						special_care -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						special_care -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						special_care += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						special_care -= float(schedule[10]/order_schedule_count)
					

				if schedule[2] == 'Carpet Cleaning':
					special_care += float(order_amount/schedule_count)

					if schedule[6] > 0:
						special_care -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						special_care -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						special_care += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						special_care -= float(schedule[10]/order_schedule_count)
					

				

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
					kitchen_cleaning += float(order_amount/schedule_count)

					if schedule[6] > 0:
						kitchen_cleaning -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						kitchen_cleaning -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						kitchen_cleaning += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						kitchen_cleaning -= float(schedule[10]/order_schedule_count)
					

				# if schedule[2] == 'Carpet Cleaning':
				# 	carpetcleaning += float(order_amount/schedule_count)

				# 	if schedule[6] != None:
				# 		carpetcleaning -= float(schedule[6]/schedule_count)
				# 	if schedule[7] != None:
				# 		carpetcleaning -= float(schedule[7]/schedule_count)
				# 	if schedule[8] != None:
				# 		carpetcleaning += float(schedule[8]/schedule_count)
				
				if schedule[2] == 'Sterilization':
					infection_control += float(order_amount/schedule_count)

					if schedule[6] > 0:
						infection_control -= float(schedule[6]/order_schedule_count)
					if schedule[7] > 0:
						infection_control -= float(schedule[7]/order_schedule_count)
					if schedule[8] > 0:
						infection_control += float(schedule[8]/order_schedule_count)
					if schedule[10] > 0:
						infection_control -= float(schedule[10]/order_schedule_count)
					
			
			
			if data_type == 'service':
				list_item = {
					'Date': str(date.date()),
					'Day': date.strftime("%A"),
					'DetailedCleaning':detailed_cleaning,
					'SpecialCare':special_care,
					'KitchenCleaning':kitchen_cleaning,
					'InfectionControl':infection_control,
					# 'GeneralCleaning':generalcleaning,
					# 'UpholsteryCleaning':upholsterycleaning,
					# 'KitchenCleaning':kitchencleaning,
					# 'CarpetCleaning':carpetcleaning,
					# 'DeepCleaning':deepcleaning,
					# 'Sterilization':sterilization,
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

		today = datetime.now()

		sales_date = request.GET.get('sales_date')
		sales_date = datetime.strptime(sales_date,'%d-%m-%Y')
		sales_day_name = sales_date.strftime("%A")

		start_date_day = sales_date.replace(hour=0,minute=0,second=0,microsecond=0)
		end_date_day   = start_date_day+timedelta(1)
		end_date_day   = end_date_day.replace(hour=0,minute=0,second=0,microsecond=0)
		
		print(start_date_day,end_date_day,"smonthlist")
	
		# if date < todate:
		orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).order_by('end_at')
		# else:
		# 	orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',end_at__range=(start_date_day,end_date_day)).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','order_scheduler_book__estimated_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluator__id','order_scheduler_book__evaluation_details__evaluation__discount').order_by('end_at')

		print(orderschedules,"countt")
		
		saleslist = []

		total_day_sales = 0

		for schedule in orderschedules:
			#schedule count of order
			order_schedule_count = OrderScheduler.objects.filter(order__order_no=schedule.order.order_no).count()

			#schedule count of evaluation book
			schedule_count = OrderScheduler.objects.filter(order__order_no=schedule.order.order_no,order_scheduler_book__id=schedule.order_scheduler_book.id).count()

			order_amount     = schedule.order_scheduler_book.estimated_cost
			cleaning_amount  = float(order_amount/schedule_count)
			
			#fine,promocode, write off calc
			if schedule.order.evaluation.promocode_amount > 0:
				cleaning_amount -= float(schedule.order.evaluation.promocode_amount/order_schedule_count)
			if schedule.order.evaluation.writeback_amount > 0:
				cleaning_amount -= float(schedule.order.evaluation.writeback_amount/order_schedule_count)
			if schedule.order.evaluation.fine_amount > 0:
				cleaning_amount += float(schedule.order.evaluation.fine_amount/order_schedule_count)
			if schedule.order.evaluation.discount > 0:
				cleaning_amount -= float(schedule.order.evaluation.discount/order_schedule_count)

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

			# if date < todate:
			# 	print(date,"dtER")
			orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).filter(Q(Q(work_status = 'CLEANING_TEAM_ASSIGNED') | Q(work_status = 'CLEANING_IN_PROGRESS') | Q(work_status='CLEANING_FULFILLED'))).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','order_scheduler_book__estimated_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluation__discount').order_by('end_at')
			# else:
			# 	orderschedules = OrderScheduler.objects.filter(is_active=True,order__evaluation__quatation_status='APPROVED',start_at__range=(start_date_day,end_date_day)).exclude( Q(Q(Q(order__evaluation__payment_method='PREPAID')&~Q(order__payment_status='COMPLETED'))|Q(Q(order__evaluation__payment_method='BREAKDOWN')&Q(order__preamount_paid=0))) ).values_list('order__order_no','order_scheduler_book__estimated_cost','order_scheduler_book__service_type__name','order_scheduler_book__cleaning_policy','order_scheduler_book__id','order_scheduler_book__evaluation_details__evaluation__promocode_amount','order_scheduler_book__evaluation_details__evaluation__writeback_amount','order_scheduler_book__evaluation_details__evaluation__fine_amount','order_scheduler_book__evaluation_details__evaluation__discount').order_by('end_at')
			
			found = set()
			schedules_list = []

			for schedule in orderschedules:

				# if schedule[4] not in found:
				schedules_list.append(schedule)
				# found.add(schedule[4])
			# print(found,schedules_list,"kio")

			for schedule in schedules_list:

				order_schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0]).count()

				schedule_count = OrderScheduler.objects.filter(order__order_no=schedule[0],order_scheduler_book__id=schedule[4]).count()

				order_amount = schedule[1]
				cleaning_amount += float(order_amount/schedule_count)

				if schedule[5] > 0:
					cleaning_amount -= float(schedule[5]/order_schedule_count)
				if schedule[6] > 0:
					cleaning_amount -= float(schedule[6]/order_schedule_count)
				if schedule[7] > 0:
					cleaning_amount += float(schedule[7]/order_schedule_count)
				if schedule[8] > 0:
					cleaning_amount -= float(schedule[8]/order_schedule_count)
			
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

			if cleaningteam.check_in_notes:
				check_in_notes = cleaningteam.check_in_notes
			else:
				check_in_notes = 'No Notes'

			if cleaningteam.check_out_notes:
				check_out_notes = cleaningteam.check_out_notes
			else:
				check_out_notes = 'No Notes'

			cleaning_status = cleaningteam.order_scheduler.work_status

			followup = FollowUp.objects.filter(is_active=True,investigation__order_schedule__id=cleaningteam.order_scheduler.id).last()
			if followup:
				followup_id = followup.id
			else:
				followup_id = None

			customer_id = cleaningteam.order_scheduler.order.evaluation.customer.id
			
			print(cleaning_status,"printest")

			response_dict = {'success':True,"visit_count":visit_count,"schedule_id":schedule_id, "customer_id":customer_id,"followup_id":followup_id,"cleaning_status":cleaning_status,"team_leader":cleaningteam.team_leader.name,"team_leader_image":cleaningteam.team_leader.profile_image.url,"assigned_by":cleaningteam.created_by.name,"assigned_by_image":cleaningteam.created_by.profile_image.url,"assigned_by_usertype":cleaningteam.created_by.user_type,"start_at":check_in_time,"end_at":check_out_time,'members':team_members_list, 'before_cleaning_media':before_cleaning_media_list, 'after_cleaning_media':after_cleaning_media_list,'checkin_notes':check_in_notes,'checkout_notes':check_out_notes}

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
		print("runo")
		response_dict = {}
		response_dict['success'] = False

		team_id        = request.data.get('team_id')
		check_in_notes = request.data.get('check_in_notes')
	
		print(team_id,"zack")
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

		team_id         = request.data.get('team_id')
		check_out_notes = request.data.get('check_out_notes')
	
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

		if check_out_notes:
			cleaning_team_detail.check_out_notes = check_out_notes
		
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
		data = False
		
		order_id = request.data.get('orderid')
		subscription_topay = request.data.get('subscription_topay',None)
		selected_options = request.data.get('selectedoptions')
		print(order_id,selected_options,subscription_topay,"opr")
		options = selected_options.split(",")

		print(options,"oid")

		if subscription_topay:
			Order.objects.filter(id=int(order_id)).update(subscription_topay=int(subscription_topay),subscription_topay_date=timezone.now())
			data=True
		
		if selected_options:
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

class InventoryItemsAPI(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {}
		item_id = request.GET.get('item_id')
		print(item_id,"attrsed")
		try:
			item_units = ItemUnit.objects.filter(item__id=int(item_id),status='active')
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
			items.append(item_dict)
		response_dict['items']=items
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
		action = request.GET.get('action')
		
		print(ingredient_id,"attrsed3")
		try:
			ingredient = ServiceRecipeIngredients.objects.get(id=int(ingredient_id))

			if action == 'add_item':
				ingredient_items_exist = ServiceRecipeItems.objects.filter(ingredient=ingredient)
				print("add")
				item = InventoryItem.objects.get(id=int(item_id))
				
				if ingredient_items_exist:
					ServiceRecipeItems.objects.create(ingredient=ingredient,item=item)
				else:
					ServiceRecipeItems.objects.create(ingredient=ingredient,item=item,is_swapped_item=True)

			if action == 'edit_item':
				ingredient_item = ServiceRecipeItems.objects.get(id=int(ingredient_item_id))
				item = InventoryItem.objects.get(id=int(item_id))
				ingredient_item.item = item
				ingredient_item.save()

			if action == 'delete_item':
				ServiceRecipeItems.objects.get(id=int(ingredient_item_id)).delete()

			response_dict['ingredient'] = ingredient.ingredient
			items = ServiceRecipeItems.objects.filter(ingredient=ingredient)
		except:
			ingredient = None
			items = None

		items_list = []
		if items:
			for item in items:
				list_item = {
					'item_id' : item.id,
					'item_name' : item.item.name,
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
	