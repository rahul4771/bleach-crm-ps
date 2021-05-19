from rest_framework import serializers
from customer.serilizers import AddressSerializer
from order.models import Order,OrderScheduler,FollowUpScheduler,FollowUp
from evaluator.models import EvaluationDetails
from user.models import UserProfile
from senior_team_leader.models import CleaningTeam,FollowUpTeam



class UserProfileShowSerializer(serializers.ModelSerializer):
	class Meta:
		model  = UserProfile
		fields = ('id','name','gender','email','mobile_number','profile_image')	


class OrderShowSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Order
		fields = ('order_no','order_status','payment_status')

class EvaluationDetailsShowSerializer(serializers.ModelSerializer): 
	evaluator          = UserProfileShowSerializer(read_only=True) 
	class Meta:
		model  = EvaluationDetails
		fields = ('evaluator',)

class CleaningTeamShowSerializer(serializers.ModelSerializer):
	team_leader = UserProfileShowSerializer(read_only=True)
	class Meta:
		model = CleaningTeam
		fields= ('team_leader',)


class CleaningScheduleSerializer(serializers.ModelSerializer):
	start_at           = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	end_at             = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	customer_address   = AddressSerializer(read_only=True)
	evaluation_details = EvaluationDetailsShowSerializer(read_only=True)
	order              = OrderShowSerializer(read_only=True)
	cleaning_team_order_scheduler = CleaningTeamShowSerializer(many=True,read_only=True)
	class Meta:
		model  = OrderScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','no_of_cleaners','cleaning_hours','evaluation_details','order','cleaning_team_order_scheduler')





class FollowupSerializer(serializers.ModelSerializer):
	class Meta:		
		model  = FollowUp
		fields = ('ticket_no','no_of_cleaners','cleaning_hours')

class FollowUpTeamShowSerializer(serializers.ModelSerializer):
	team_leader = UserProfileShowSerializer(read_only=True)
	class Meta:
		model = FollowUpTeam
		fields= ('team_leader',)


class FollowupScheduleSerializer(serializers.ModelSerializer):
	customer_address = AddressSerializer(read_only=True)
	start_at = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	end_at   = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	followupteam_followupschedule = FollowUpTeamShowSerializer(many=True,read_only=True)
	class Meta:		
		model  = FollowUpScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','followupteam_followupschedule')

