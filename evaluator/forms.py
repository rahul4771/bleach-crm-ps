from django import forms
from evaluator.models import EvaluationDetails,Evaluation,EvaluationBook
from user.models import UserProfile,Address

#Customer Details add form
class EvaluationDetailsForm(forms.ModelForm):
	proposed_time = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M %p'],widget=forms.TextInput(attrs={'class':'date_time_pick'}))
	class Meta:
		model  = EvaluationDetails
		fields = ('evaluator','proposed_time','address')	
	
	def __init__(self,*args,enquiry_user_id,**kwargs):
		self.enquiry_user_id = kwargs.pop('enquiry_user_id', None)
		super(EvaluationDetailsForm, self).__init__(*args, **kwargs)

		self.fields['evaluator'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='EVALUATOR'),required=True,widget=forms.Select(attrs={'class':'evaluator'}))
		self.fields['address'] = forms.ModelChoiceField(
		    queryset=Address.objects.filter(is_active=True,customer_id=enquiry_user_id),required=True,widget=forms.Select(attrs={'class':'customer_address'}))

#Quatation Phase1 form
class QuatationPhase1Form(forms.ModelForm):

	class Meta:
		model  = Evaluation
		fields = ('cleaning_policy','subscription_start','subscription_days_gap','subscription_end','no_of_cleanings','is_downpayment','no_of_down_payments','down_payment_deadend','attender_notes','preffered_gender')
		widgets={
				'is_downpayment':forms.CheckboxInput(attrs={'class':'is_down_payment'}),
				'cleaning_policy':forms.Select(attrs={'class':'cleaning_policy'}),
		}
	def __init__(self,*args,**kwargs):
		super(QuatationPhase1Form, self).__init__(*args, **kwargs)
		self.fields['attender_notes']       =	forms.CharField(required=False,widget=forms.Textarea())
		self.fields['subscription_start']   =	forms.DateField(input_formats=['%d-%m-%Y'],required=False,widget=forms.TextInput(attrs={'class':'date_pick'}))
		self.fields['subscription_end']     =	forms.DateField(input_formats=['%d-%m-%Y'],required=False,widget=forms.TextInput(attrs={'class':'date_pick'}))
		self.fields['down_payment_deadend'] =	forms.DateField(input_formats=['%d-%m-%Y'],required=False,widget=forms.TextInput(attrs={'class':'date_pick'}))	  			


#Quatation Phase2 forms
class QuatationPhase2EstimationForm(forms.ModelForm):

	class Meta:
		model = EvaluationDetails
		fields= ('address','evaluator','evaluator_note','estimated_cost','cleaning_hours','number_of_cleaners')

	def __init__(self,*args,enquiry_id,**kwargs):
		self.enquiry_id = kwargs.pop('enquiry_id', None)
		super(QuatationPhase2EstimationForm, self).__init__(*args, **kwargs)	

		self.fields['address'] = forms.ModelChoiceField(
		    queryset=Address.objects.filter(customer_id=enquiry_id,is_active=True),required=True,widget=forms.Select(attrs={'class':'customer_address'}))
		self.fields['evaluator'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(user_type='EVALUATOR',is_active=True),required=True,widget=forms.Select(attrs={'class':'evaluator'}))

class QuatationPhase2ServiceForm(forms.ModelForm):

	class Meta:
		model = EvaluationBook
		fields = ('cleaning_type','location_type','service_type','cleaning_method','fabric_type','spot_stain_status','size_of_carpet','piece_of_chairs','set_type','sanitization_type','size_to_be_sanitised','bed_type',)
		widgets={
				'cleaning_type':forms.Select(attrs={'class':'cleaning_type'})
		}
	def __init__(self,*args,**kwargs):
		super(QuatationPhase2ServiceForm, self).__init__(*args, **kwargs)	
