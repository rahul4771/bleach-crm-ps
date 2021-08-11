from rest_framework import serializers

from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule
from evaluator.models import Evaluation,EvaluationDetails
from order.models import Promocode
from inventory.models import Line,Segment,Category,Attribute,AttributeValue,BundleItems,InventoryItem

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

class ShiftScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftSchedule
        fields = ('id','staff','shift_date','shift1','shift2','shift3','shift1_start_at','shift2_start_at','shift3_start_at','shift1_end_at','shift2_end_at','shift3_end_at',)      

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

class InventoryLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ('id','name','status')

class InventoryValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ('id','name','status')

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ('id','name','status')

class InventoryBundleItemSerializer(serializers.ModelSerializer):
    bundle_item     = InventoryItemSerializer(read_only=True)
    class Meta:
        model = BundleItems
        fields = ('id','bundle_item','item_price','item_count')

class InventorySegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ('id','name')




#Team Leader Mobile app serializers
from order.models import FollowUp
from senior_team_leader.models import OrderScheduler,FollowUpScheduler,CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember
from agent.serializers import UserProfileShowSerializer,EvaluationDetailsShowSerializer,OrderShowSerializer,EvaluationBookShowSerializer

##Cleaning Team API's
class OrderScheduleAPISerializer(serializers.ModelSerializer):
	customer_address     = AddressSerializer(read_only=True)
	evaluation_details   = EvaluationDetailsShowSerializer(read_only=True)
	order                = OrderShowSerializer(read_only=True)
	order_scheduler_book = EvaluationBookShowSerializer(read_only=True)
	class Meta:
		model  = OrderScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','no_of_cleaners','cleaning_hours','evaluation_details','order','order_scheduler_book')
	
	def to_representation(self,obj):
		td = super(OrderScheduleAPISerializer,self).to_representation(obj)	
		td['start_at']  = ((obj.start_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		td['end_at'] 	= ((obj.end_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		return(td)

class CleaningTeamMemberAPISerializer(serializers.ModelSerializer):
	member = UserProfileShowSerializer(read_only=True)
	class Meta:
		model = CleaningTeamMember
		fields= ('member',)



class CleaningTeamAPISerializer(serializers.ModelSerializer):
    team_leader                     = UserProfileShowSerializer(read_only=True)
    order_scheduler                 = OrderScheduleAPISerializer(read_only=True)
    created_by                      = UserProfileShowSerializer(read_only=True)

    cleaning_member_team			= CleaningTeamMemberAPISerializer(many=True,read_only=True)
    class Meta:
        model = CleaningTeam
        fields= ('id','team_leader','created_by','order_scheduler','cleaning_member_team')



##followup team apis    
class FollowupAPISerializer(serializers.ModelSerializer):
	class Meta:		
		model   = FollowUp
		fields  = ('ticket_no','no_of_cleaners','cleaning_hours')



class FollowUpTeamMemberAPISerializer(serializers.ModelSerializer):
	member = UserProfileShowSerializer(read_only=True)
	class Meta:
		model = FollowUpTeamMember
		fields= ('member',) 
    
class FollowupScheduleAPISerializer(serializers.ModelSerializer):
	customer_address              = AddressSerializer(read_only=True)
	follow_up                     = FollowupAPISerializer(read_only=True)
	class Meta:		
		model  = FollowUpScheduler
		fields = ('id','start_at','end_at','customer_address','work_status','follow_up')
	
	def to_representation(self,obj):
		td = super(FollowupScheduleAPISerializer,self).to_representation(obj)	
		td['start_at']  = ((obj.start_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		td['end_at'] 	= ((obj.end_at)+timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")
		return(td)




class FollowUpTeamAPISerializer(serializers.ModelSerializer):
    team_leader            = UserProfileShowSerializer(read_only=True)
    created_by             = UserProfileShowSerializer(read_only=True)
    followup_scheduler     = FollowupScheduleAPISerializer(read_only=True)

    followup_member_team   = FollowUpTeamMemberAPISerializer(many=True,read_only=True)	
    class Meta:
        model   = FollowUpTeam
        fields  = ('id','team_leader','created_by','followup_scheduler','followup_member_team')