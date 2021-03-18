from rest_framework import serializers
from user.models import UserProfile,Address,Governorate,Area

class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model  = UserProfile
		fields = ('name','gender','email','nationality','mobile_number','date_day','date_month','date_year','sms_preference')	

class AddressSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Address
		fields = ('governorate','area','block','avenue','building','street','floor','apartment')
