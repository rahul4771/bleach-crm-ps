from rest_framework import serializers
from customer.serilizers import AddressSerializer
from order.models import Order,OrderScheduler,FollowUpScheduler,FollowUp
from evaluator.models import EvaluationDetails
from user.models import UserProfile




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


class CleaningScheduleSerializer(serializers.ModelSerializer):
	start_at           = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	end_at             = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	customer_address   = AddressSerializer(read_only=True)
	evaluation_details = EvaluationDetailsShowSerializer(read_only=True)
	order              = OrderShowSerializer(read_only=True)
	class Meta:
		model  = OrderScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','no_of_cleaners','cleaning_hours','evaluation_details')





class FollowupSerializer(serializers.ModelSerializer):
	class Meta:		
		model  = FollowUp
		fields = ('ticket_no','no_of_cleaners','cleaning_hours')

class FollowupScheduleSerializer(serializers.ModelSerializer):
	customer_address = AddressSerializer(read_only=True)
	start_at = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	end_at   = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
	class Meta:		
		model  = FollowUpScheduler
		fields = ('id','start_at','end_at','customer_address','work_status')

