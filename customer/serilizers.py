from rest_framework import serializers
from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import ServiceType,Evaluation,EvaluationDetails,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote
from order.models import Order
from customer.models import CustomerBooking

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

class EvaluationBookSectionSerializer(serializers.ModelSerializer):
	keynotesections = EvaluationSectionKeynoteSerializer(many=True,read_only=True)
	class Meta:
		model  = EvaluationBookSection
		fields = ('section_name','size','age','wall_type','ceiling_type','floor_type','material','colour','cause_of_stain','cement_residue','oil_residue','hall_size','window_side','new_kitchen','is_highprice_facade','is_highprice_window','vacuuming','section_cost','section_net_cost','keynotesections')

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
	class Meta:
		model  = CustomerBooking
		fields = ('booking_id','booking_type','booking_date',)

class EvaluationSerializer(serializers.ModelSerializer):
	customer                = UserProfileSerializer(read_only=True) 
	booking_evaluation      = CustomerBookingShowSerializer(many=True,read_only=True)
	quatation_approved_date = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p ")
	class Meta:
		model  = Evaluation
		fields = ('customer','quatation_status','quatation_approved_date','payment_method','booking_evaluation')

class OrderSerializer(serializers.ModelSerializer):
	class Meta:
		model  = Order
		fields = ('order_no','invoice_no','order_status','payment_status','total_amount','amount_paid','remining_amount',)

class EvaluationDetailsSerializer(serializers.ModelSerializer): 
	evaluator                          = UserProfileSerializer(read_only=True)
	address                            = AddressSerializer(read_only=True)
	evaluation_book_evaluation_details = EvaluationBookSerializer(many=True,read_only=True)
	proposed_time                      = serializers.DateTimeField(format="%d-%m-%Y %I:%M %p ")
	class Meta:
		model  = EvaluationDetails
		fields = ('id','evaluator','proposed_time','address','evaluation_book_evaluation_details')	
		read_only_fields = ('id',)
class CustomerBookingSerializer(serializers.ModelSerializer):
	evaluation = EvaluationSerializer(read_only=True)
	class Meta:
		model  = CustomerBooking
		fields = ('evaluation','booking_id','booking_type','booking_date',)