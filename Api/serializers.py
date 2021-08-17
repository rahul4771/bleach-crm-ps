from rest_framework import serializers

from user.models import UserProfile,Address,Governorate,Area,LeaveSchedule,ShiftSchedule
from evaluator.models import Evaluation,EvaluationDetails
from order.models import Promocode
from inventory.models import Line,Segment,Category,Attribute,AttributeValue,BundleItems,InventoryItem,ItemUnit

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
    shift3_start_at = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
    shift3_end_at   = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p")
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

class InventoryItemUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemUnit
        fields = ('id','item','unit_code','status')

class InventoryBundleItemSerializer(serializers.ModelSerializer):
    bundleitem     = InventoryItemSerializer(read_only=True)
    class Meta:
        model = BundleItems
        fields = ('id','bundleitem','item_price','item_count')

class InventorySegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ('id','name')




#Team Leader Mobile app serializers
from datetime import timedelta,date,datetime

from order.models import Order,FollowUp,Investigation,FollowUpSectionKeynote,FollowUpSection
from evaluator.models import EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote
from senior_team_leader.models import OrderScheduler,FollowUpScheduler,CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember
from agent.serializers import UserProfileShowSerializer,ServiceTypeShowSerializer
from customer.serilizers import EvaluationSerializer


class OrderAPISerializer(serializers.ModelSerializer):
    class Meta:
        model  = Order
        fields = ('order_no','order_status','payment_status')

class KeynoteAPISerializer(serializers.ModelSerializer):
    class Meta:
        model  = EvaluationSectionKeynote
        fields = ('id','sub_area','quantity','completion_status')



class EvaluationDetailsAPISerializer(serializers.ModelSerializer):
    evaluator          = UserProfileShowSerializer(read_only=True) 
    evaluation         = EvaluationSerializer(read_only=True)
    class Meta:
        model  = EvaluationDetails
        fields = ('evaluator','evaluation')

class SectionAPISerializer(serializers.ModelSerializer):
    keynotesections = KeynoteAPISerializer(read_only=True,many=True)
    class Meta:
        model  = EvaluationBookSection
        fields = ('section_name','category','dirt_level','size','quantity','unit','age','floor','apartment','room','wall_type','ceiling_type','floor_type','material','colour','cause_of_stain','age_of_stain','cement_residue','oil_residue','hall_size','window_side','new_kitchen','is_highprice_facade','is_highprice_window','upholstery_type','vacuuming','section_cost','section_cleanings','section_net_cost','keynotesections')



class EvaluationBookAPISerializer(serializers.ModelSerializer):
    service_type             = ServiceTypeShowSerializer(read_only=True)
    evaluationsection_book   = SectionAPISerializer(many=True,read_only=True)
    class Meta:
        model = EvaluationBook
        fields = ('cleaning_policy','area_type','location_type','cleaning_method','evaluator_note','service_type','evaluationsection_book')


##Cleaning Team API's
class OrderScheduleAPISerializer(serializers.ModelSerializer):
	customer_address     = AddressSerializer(read_only=True)
	evaluation_details   = EvaluationDetailsAPISerializer(read_only=True)
	order                = OrderAPISerializer(read_only=True)
	order_scheduler_book = EvaluationBookAPISerializer(read_only=True)
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
class InvestigationAPISerializer(serializers.ModelSerializer):
    investigator   = UserProfileShowSerializer(read_only=True)
    assigned_by    = UserProfileShowSerializer(read_only=True)
    order_schedule = OrderScheduleAPISerializer(read_only=True) 
    class Meta:		
        model   = Investigation
        fields  = ('ticket_types','investigator','assigned_by','scheduled_at','notes','order_schedule')

class FollowUpSectionKeynoteSerializer(serializers.ModelSerializer):
    class Meta:		
        model   = FollowUpSectionKeynote
        fields  = ('id','sub_area','quantity','completion_status')

class FollowUpSectionSerializer(serializers.ModelSerializer):
    keynotesectionsfollowup = FollowUpSectionKeynoteSerializer(many=True,read_only=True)
    class Meta:		
        model   = FollowUpSection
        fields  = ('section_name','category','dirt_level','quantity','size','unit','age','floor','apartment','room','wall_type','ceiling_type','floor_type','material','colour','cause_of_stain','section_cost','section_cleanings','section_net_cost','keynotesectionsfollowup')



class FollowupAPISerializer(serializers.ModelSerializer):
    investigation         = InvestigationAPISerializer(read_only=True)
    follow_up_of_section  = FollowUpSectionSerializer(many=True,read_only=True)
    class Meta:		
        model   = FollowUp
        fields  = ('ticket_no','no_of_cleaners','cleaning_hours','investigation','follow_up_of_section')



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