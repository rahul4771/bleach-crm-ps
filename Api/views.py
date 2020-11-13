from django.shortcuts import render

from evaluator.models import Evaluation,EvaluationDetails
from user.models import UserProfile

from Api.serializers import UserProfileSerializer, EvaluationSerializer
from agent.views import generate_random_username

from django.utils import timezone 
from datetime import timedelta,date,datetime
from django.db.models import Q
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