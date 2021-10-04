from rest_framework import serializers
from customer.serilizers import AddressSerializer,EvaluationSerializer
from order.models import Order,OrderScheduler,FollowUpScheduler,FollowUp
from evaluator.models import EvaluationDetails,EvaluationBook,ServiceType
from user.models import UserProfile
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember

from datetime import timedelta,date,datetime


class ServiceTypeShowSerializer(serializers.ModelSerializer):
	class Meta:
		model = ServiceType
		fields= ('name',)

class UserProfileShowSerializer(serializers.ModelSerializer):
	class Meta:
		model  = UserProfile
		fields = ('id','name','gender','email','mobile_number','profile_image')	

class CleaningTeamMemberShowSerializer(serializers.ModelSerializer):
	member = UserProfileShowSerializer(read_only=True)
	class Meta:
		model = CleaningTeamMember
		fields= ('member',)



class OrderShowSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Order
		fields = ('id','order_no','order_status','payment_status','preamount_paid')

class EvaluationDetailsShowSerializer(serializers.ModelSerializer): 
	evaluator          = UserProfileShowSerializer(read_only=True) 
	evaluation         = EvaluationSerializer(read_only=True)
	class Meta:
		model  = EvaluationDetails
		fields = ('evaluator','evaluation')

class EvaluationBookShowSerializer(serializers.ModelSerializer):
	service_type = ServiceTypeShowSerializer(read_only=True)
	class Meta:
		model = EvaluationBook
		fields = ('cleaning_policy','service_type')

class CleaningTeamShowSerializer(serializers.ModelSerializer):
	team_leader                     = UserProfileShowSerializer(read_only=True)
	cleaning_member_team			= CleaningTeamMemberShowSerializer(many=True,read_only=True)
	created_by                      = UserProfileShowSerializer(read_only=True)
	class Meta:
		model = CleaningTeam
		fields= ('team_leader','created_by','check_in','check_out','cleaning_member_team')

	def to_representation(self,obj):
		td = super(CleaningTeamShowSerializer,self).to_representation(obj)
		try:	
			td['check_in']  = ((obj.check_in)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		except:
			td['check_in']  = None
		try:
			td['check_out'] = ((obj.check_out)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		except:
			td['check_out'] = None
		return(td)



class CleaningScheduleSerializer(serializers.ModelSerializer):
	customer_address     = AddressSerializer(read_only=True)
	evaluation_details   = EvaluationDetailsShowSerializer(read_only=True)
	order                = OrderShowSerializer(read_only=True)
	order_scheduler_book = EvaluationBookShowSerializer(read_only=True)
	cleaning_team_order_scheduler = CleaningTeamShowSerializer(many=True,read_only=True)
	class Meta:
		model  = OrderScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','no_of_cleaners','cleaning_hours','evaluation_details','order','order_scheduler_book','cleaning_team_order_scheduler')
	
	def to_representation(self,obj):
		td = super(CleaningScheduleSerializer,self).to_representation(obj)	
		td['start_at']  = ((obj.start_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		td['end_at'] 	= ((obj.end_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		return(td)



class FollowUpTeamMemberShowSerializer(serializers.ModelSerializer):
	member = UserProfileShowSerializer(read_only=True)
	class Meta:
		model = FollowUpTeamMember
		fields= ('member',) 


class FollowupSerializer(serializers.ModelSerializer):
	class Meta:		
		model   = FollowUp
		fields  = ('ticket_no','no_of_cleaners','cleaning_hours')

class FollowUpTeamShowSerializer(serializers.ModelSerializer):
	team_leader            = UserProfileShowSerializer(read_only=True)
	created_by             = UserProfileShowSerializer(read_only=True)
	followup_member_team   = FollowUpTeamMemberShowSerializer(many=True,read_only=True)	
	class Meta:
		model   = FollowUpTeam
		fields  = ('team_leader','created_by','followup_member_team')


class FollowupScheduleSerializer(serializers.ModelSerializer):
	customer_address              = AddressSerializer(read_only=True)
	follow_up                     = FollowupSerializer(read_only=True)
	followupteam_followupschedule = FollowUpTeamShowSerializer(many=True,read_only=True)
	class Meta:		
		model  = FollowUpScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','follow_up','followupteam_followupschedule')
	
	def to_representation(self,obj):
		td = super(FollowupScheduleSerializer,self).to_representation(obj)	
		td['start_at']  = ((obj.start_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		td['end_at'] 	= ((obj.end_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		return(td)
