from rest_framework import serializers

from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule
from evaluator.models import Evaluation
from order.models import Promocode

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = ('name','gender','email','nationality','customer_type','company','job_title','mobile_number','phone_number','date_of_birth','sms_preference','is_whatsapp','is_email','is_sms')   
    
    def __init__(self,*args,**kwargs):
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

        self.fields['name'].required          = True
        self.fields['gender'].required        = True
        self.fields['email'].required         = True
        self.fields['date_of_birth'].required = True
        self.fields['mobile_number'].required = True
        self.fields['nationality'].required   = True  

class LeaveUsersSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = UserProfile
        fields = ('id','name','user_type','photo_url') 

    def get_photo_url(self, car):
        request = self.context.get('request')
        try:
            photo_url = car.profile_image.url
            return photo_url
        except:
            return None

class LeaveScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveSchedule
        fields = ('id','staff','leave_date','leave_type')      

class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:      
        model = Governorate   
        fields = ('name',)  

class AreaSerializer(serializers.ModelSerializer):
    class Meta:      
        model = Area   
        fields = ('name',)
        
class AddressSerializer(serializers.ModelSerializer): 
    governorate     = GovernorateSerializer(read_only=True)
    area            = AreaSerializer(read_only=True)
    class Meta: 
        model  = Address 
        fields = ('governorate','area','block','avenue','building','street','floor','apartment',) 

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ('evaluation_id','customer__mobile','evaluation_details__evaluator','evaluation_details__proposed_time','evaluation_details__address')
  
