from rest_framework import serializers

from user.models import UserProfile,Address,Governorate,Area 

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = ('name','gender','email','nationality','customer_type','company','job_title','mobile_number','phone_number','civil_id_number','sms_preference','is_whatsapp','is_email','is_sms')   
    
    def __init__(self,*args,**kwargs):
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

        self.fields['name'].required          = True
        self.fields['gender'].required        = True
        self.fields['email'].required         = True
        self.fields['mobile_number'].required = True
        self.fields['nationality'].required   = True  
        

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
  
