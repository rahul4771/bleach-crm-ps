from rest_framework import serializers
from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import ServiceType,Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote,EvaluationSectionAddons
from order.models import Order
from customer.models import CustomerBooking,CartService,CartSchedule
from bleachadmin.models import ServicePriceRange

class ServiceTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = ServiceType
		fields= ('name',)

class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model  = UserProfile
		fields = ('id','name','gender','email','mobile_number','date_day','date_month','date_year','sms_preference')	
		read_only_fields =('id',)

class AddressSaveSerializer(serializers.ModelSerializer): 
	class Meta:
		model  = Address
		fields = ('governorate','area','block','avenue','building','street','floor','apartment')
		
class EvaluationSectionKeynoteSerializer(serializers.ModelSerializer):
	class Meta:
		model  = EvaluationSectionKeynote
		fields = ('sub_area','quantity')

class EvaluationSectionAddonSerializer(serializers.ModelSerializer):
	class Meta:
		model  = EvaluationSectionAddons
		fields = ('name','addon_cost','quantity','addon_net_cost','size','other_details')

class EvaluationBookSectionSerializer(serializers.ModelSerializer):
	keynotesections = EvaluationSectionKeynoteSerializer(many=True,read_only=True)
	addonsections   = EvaluationSectionAddonSerializer(many=True,read_only=True)
	class Meta:
		model  = EvaluationBookSection
		fields = ('section_name','size','age','wall_type','ceiling_type','floor_type','material','colour','cause_of_stain','cement_residue','oil_residue','hall_size','window_side','new_kitchen','is_cabinet','is_highprice_facade','is_highprice_window','vacuuming','section_cost','section_net_cost','sectiononly_cost','sectiononly_net_cost','upholstery_type','age_of_stain','keynotesections','addonsections')

class EvaluationBookSerializer(serializers.ModelSerializer):
	evaluationsection_book = EvaluationBookSectionSerializer(many=True,read_only=True)
	service_type           = ServiceTypeSerializer(read_only=True)
	class Meta:
		model = EvaluationBook
		fields = ('id','service_type','cleaning_policy','area_type','location_type','total_cost','estimated_cost','evaluator_note','evaluationsection_book')
		read_only_fields = ('id',)

##for data showing
class GovernorateSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Governorate
		fields = ('id','name')

class AreaSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Area
		fields = ('id','name')

class AddressSerializer(serializers.ModelSerializer): 
	governorate = GovernorateSerializer(read_only=True)
	area        = AreaSerializer(read_only=True)
	customer    = UserProfileSerializer(read_only=True)
	class Meta:
		model  = Address
		fields = ('id','governorate','area','block','avenue','building','street','floor','apartment','customer')
		read_only_fields =('id',)

class CustomerBookingShowSerializer(serializers.ModelSerializer):
	booking_date      = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p ")
	class Meta:
		model  = CustomerBooking
		fields = ('booking_id','booking_type','booking_date',)

class EvaluationSerializer(serializers.ModelSerializer):
	customer                = UserProfileSerializer(read_only=True) 
	booking_evaluation      = CustomerBookingShowSerializer(many=True,read_only=True)
	quatation_approved_date = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p ")
	class Meta:
		model  = Evaluation
		fields = ('customer','quatation_status','quatation_approved_date','payment_method','booking_evaluation','estimated_cost','total_cost','discount')
		read_only_fields = ('estimated_cost','total_cost','discount')

class OrderSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Order
		fields = ('id','order_no','invoice_no','order_status','payment_status','total_amount','amount_paid','remining_amount','preamount_paid')
		read_only_fields = ('id','preamount_paid',)
		
class EvaluationDetailsSerializer(serializers.ModelSerializer): 
	evaluator                          = UserProfileSerializer(read_only=True)
	address                            = AddressSerializer(read_only=True)
	evaluation_book_evaluation_details = EvaluationBookSerializer(many=True,read_only=True)
	proposed_time                      = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p ")
	evaluation                         = EvaluationSerializer(read_only=True)
	class Meta:
		model  = EvaluationDetails
		fields = ('id','evaluator','proposed_time','address','evaluation','evaluation_book_evaluation_details')	
		read_only_fields = ('id','evaluation')

class CustomerBookingSerializer(serializers.ModelSerializer):
	evaluation        = EvaluationSerializer(read_only=True)
	class Meta:
		model  = CustomerBooking
		fields = ('evaluation','booking_id','booking_type','booking_date',)

class ServicePriceRangeShowSerializer(serializers.ModelSerializer):
    class Meta:
        model   = ServicePriceRange
        fields  = ('minimum_area','maximum_area','price','is_newkitchen','is_cabinet','is_highprice_facade','is_highprice_window','upholstery_type')

class CartServiceSerializer(serializers.ModelSerializer):
	class Meta:
		model  = CartService
		fields = ('cart','service_type','cleaning_policy','area_type','cleaning_method','location_type','section_name','category','dirt_level','quantity','size','unit','age','floor','apartment','room','wall_type','ceiling_type','floor_type','material','colour','cause_of_stain','age_of_stain','cement_residue','oil_residue','hall_size','window_side','new_kitchen','is_cabinet','is_highprice_facade','is_highprice_window','upholstery_type','vacuuming','total_cost','addon_name','addon_category','addon_size','addon_price','addon_productivity')

class CartServiceShowSerializer(serializers.ModelSerializer):
	service_type = ServiceTypeSerializer(read_only=True)
	service_price_range = ServicePriceRangeShowSerializer(read_only=True)
	class Meta:
		model  = CartService
		fields = ('id','service_type','service_price_range','section_name','size','unit','addon_name','addon_category','addon_size','addon_price','total_cost')

class CartScheduleSerializer(serializers.ModelSerializer):	
	class Meta:
		model  = CartSchedule
		fields = ('cart','start_at','end_at','no_of_cleaners','cleaning_hours','hourly_cleaning_duration')