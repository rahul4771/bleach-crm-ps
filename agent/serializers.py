from rest_framework import serializers
from customer.serilizers import AddressSerializer,EvaluationSerializer
from order.models import Order,OrderScheduler,FollowUpScheduler,FollowUp
from evaluator.models import EvaluationDetails,EvaluationBook,ServiceType
from user.models import UserProfile
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember


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
		fields = ('order_no','order_status','payment_status')

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
		fields= ('team_leader','created_by','cleaning_member_team')


class CleaningScheduleSerializer(serializers.ModelSerializer):
	start_at             = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	end_at               = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	customer_address     = AddressSerializer(read_only=True)
	evaluation_details   = EvaluationDetailsShowSerializer(read_only=True)
	order                = OrderShowSerializer(read_only=True)
	order_scheduler_book = EvaluationBookShowSerializer(read_only=True)
	cleaning_team_order_scheduler = CleaningTeamShowSerializer(many=True,read_only=True)
	class Meta:
		model  = OrderScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','no_of_cleaners','cleaning_hours','evaluation_details','order','order_scheduler_book','cleaning_team_order_scheduler')





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
	followup_member_team   = FollowUpTeamMemberShowSerializer(many=True,read_only=True)
	class Meta:
		model   = FollowUpTeam
		fields  = ('team_leader','followup_member_team')


class FollowupScheduleSerializer(serializers.ModelSerializer):
	customer_address              = AddressSerializer(read_only=True)
	start_at                      = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	end_at                        = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	follow_up                     = FollowupSerializer(read_only=True)
	followupteam_followupschedule = FollowUpTeamShowSerializer(many=True,read_only=True)
	class Meta:		
		model  = FollowUpScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','follow_up','followupteam_followupschedule')

