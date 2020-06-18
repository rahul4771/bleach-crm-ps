from django import forms
from evaluator.models import EvaluationDetails,Evaluation,EvaluationBook,PaymentTrack
from user.models import UserProfile,Address

#Evaluator assignment form
class EvaluationDetailsForm(forms.ModelForm):
	proposed_time = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M %p'],widget=forms.TextInput(attrs={'class':'date_time_pick','required':'required'}))
	class Meta:
		model  = EvaluationDetails
		fields = ('evaluator','proposed_time','address')	
	
	def __init__(self,*args,enquiry_user_id,**kwargs):
		self.enquiry_user_id = kwargs.pop('enquiry_user_id', None)
		super(EvaluationDetailsForm, self).__init__(*args, **kwargs)

		self.fields['evaluator'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='EVALUATOR'),required=True,widget=forms.Select(attrs={'class':'evaluator','required':'required'}))
		self.fields['address'] = forms.ModelChoiceField(
		    queryset=Address.objects.filter(is_active=True,customer_id=enquiry_user_id),required=True,widget=forms.Select(attrs={'class':'customer_address','required':'required'}))


class QuatationServiceForm(forms.ModelForm):
	tendative_date = forms.CharField(required=False)
	tendative_dates= forms.CharField(required=False)
	start_time     = forms.CharField(required=True)
	end_time       = forms.CharField(required=True)

	class Meta:
		model = EvaluationBook
		fields = ('cleaning_type','cleaning_method','location_type','service_type','fabric_type','spot_stain_status','size_of_carpet','piece_of_chairs','set_type','sanitization_type','size_to_be_sanitised','bed_type','estimated_cost','discount','total_cost','cleaning_hours','cleaning_policy')
		widgets={
				'cleaning_type':forms.Select(attrs={'class':'cleaning_type','required':'required',}),
				'cleaning_policy':forms.Select(attrs={'class':'cleaning_policy','required':'required',}),
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
			