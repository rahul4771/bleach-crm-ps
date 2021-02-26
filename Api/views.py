from django.shortcuts import render

from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,EvaluationBookSection,EvaluationSectionKeynote,CleaningMethod,CleaningSection,ServiceType,AreaType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory

from Api.serializers import UserProfileSerializer, EvaluationSerializer, LeaveScheduleSerializer, LeaveUsersSerializer
from agent.views import generate_random_username

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

class PaymentResponseCredit(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def post(self,request):
		evaluation_id = request.POST.get('req_merchant_defined_data1')
		payment_mode  = request.POST.get('req_merchant_defined_data2')
		amount_paid   = float(request.POST.get('req_amount'))

		try:
			order = Order.objects.select_related('evaluation').get(order_no=evaluation_id)
		except:
			order = None


		payment_result = request.POST.get('decision')
		print(payment_result)
		if order and payment_result == 'ACCEPT':
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
				order.postamount_paid    = amount_paid
				order.amount_paid       += amount_paid
				order.remining_amount    = order.remining_amount-amount_paid

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

		return Response(HTTP_200_OK)	

#get list of staff for leave scheduler
class LeaveUsersList(APIView):
	permission_classes  	=   (AllowAny,)
	authentication_classes  = ()

	def get(self,request):
		response_dict = {"success":False}

		try:
			staffs = UserProfile.objects.filter(is_active=True).filter(Q(user_type='TEAMINCHARGE')|Q(user_type='CLEANER'))
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
		