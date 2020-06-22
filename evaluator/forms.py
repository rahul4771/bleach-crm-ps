from django import forms
from evaluator.models import EvaluationDetails,Evaluation,EvaluationBook,PaymentTrack
from user.models import UserProfile,Address

#Evaluator assignment form
class EvaluationDetailsForm(forms.ModelForm):
	proposed_time = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=forms.TextInput(attrs={'required':'required'}))
	class Meta:
		model  = EvaluationDetails
		fields = ('evaluator','proposed_time','address')	
	
	def __init__(self,*args,enquiry_user_id,**kwargs):
		self.enquiry_user_id = kwargs.pop('enquiry_user_id', None)
		super(EvaluationDetailsForm, self).__init__(*args, **kwargs)

		self.fields['evaluator'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='EVALUATOR'),required=True,widget=forms.Select(attrs={'class':'evaluator','required':'required'}))
		self.fields['address'] = forms.ModelChoiceField(
		    queryset=Address.objects.filter(is_active=True,customer_id=enquiry_user_id,currently_active=True),required=True,widget=forms.Select(attrs={'class':'customer_address','required':'required'}))


#Evaluator assignment form by evaluator
class MyEvaluationDetailsForm(forms.ModelForm):
	proposed_time = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=forms.TextInput(attrs={'required':'required'}))
	class Meta:
		model  = EvaluationDetails
		fields = ('proposed_time','address')	
	
	def __init__(self,*args,enquiry_user_id,**kwargs):
		self.enquiry_user_id = kwargs.pop('enquiry_user_id', None)
		super(MyEvaluationDetailsForm, self).__init__(*args, **kwargs)

		self.fields['address'] = forms.ModelChoiceField(
		    queryset=Address.objects.filter(is_active=True,customer_id=enquiry_user_id,currently_active=True),required=True,widget=forms.Select(attrs={'class':'customer_address','required':'required'}))



class QuatationServiceForm(forms.ModelForm):
	tendative_date = forms.CharField(required=False)
	tendative_dates= forms.CharField(required=False)
	start_time     = forms.CharField(required=True)


	class Meta:
		model = EvaluationBook
		fields = ('service_type','cleaning_method','cleaning_type','dirt_level','location_type','floor_type','number_of_floors','number_of_rooms','set_type','set_size','piece_of_chairs','chair_fabric_type','piece_of_sofas','sofa_fabric_type','size_of_carpet','spot_stain_status','fabric_type','sanitization_type','size_to_be_sanitised','bed_size','bed_type','estimated_cost','discount','total_cost','cleaning_hours','cleaning_policy')
		widgets={
				'service_type':forms.Select(attrs={'class':'service_type','required':'required',}),
				'cleaning_policy':forms.Select(attrs={'class':'cleaning_policy','required':'required',}),
				'total_cost':forms.NumberInput(attrs={'required':'required','min':0,'readonly':True}),
				'estimated_cost':forms.NumberInput(attrs={'required':'required','class':'estimated_cost','min':0}),
				'discount':forms.NumberInput(attrs={'class':'discount','min':0,}),
				'cleaning_hours':forms.NumberInput(attrs={'required':'required'}),
		}
	def __init__(self,*args,**kwargs):
		super(QuatationServiceForm, self).__init__(*args, **kwargs)	

class PaymentTrackForm(forms.ModelForm):

	class Meta:
		model  = PaymentTrack
		fields = ('amount','due_date') 
	
	def __init__(self,*args,**kwargs):
		super(PaymentTrackForm, self).__init__(*args, **kwargs)
		self.fields['due_date']   =	forms.DateField(input_formats=['%d-%m-%Y'],required=False,widget=forms.TextInput())
			