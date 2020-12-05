from django import forms
from evaluator.models import EvaluationDetails,Evaluation,EvaluationBook
from user.models import UserProfile,Address

class EvaluationDetailsForm(forms.ModelForm):
	proposed_time = forms.CharField(widget=forms.TextInput(attrs={'required':'required'}))
	class Meta:
		model  = EvaluationDetails
		fields = ('evaluator','address','attender_note')	
	
	def __init__(self,*args,enquiry_user_id,evaluation_id,**kwargs):
		self.enquiry_user_id = kwargs.pop('enquiry_user_id', None)
		self.evaluation_id   = kwargs.pop('evaluation_id',None)
		
		super(EvaluationDetailsForm, self).__init__(*args, **kwargs)


#Evaluator assignment form by evaluator
class MyEvaluationDetailsForm(forms.ModelForm):
	proposed_time = forms.CharField(widget=forms.TextInput(attrs={'required':'required'}))
	class Meta:
		model  = EvaluationDetails
		fields = ('address','attender_note')	
	
	def __init__(self,*args,enquiry_user_id,evaluation_id,**kwargs):
		self.enquiry_user_id = kwargs.pop('enquiry_user_id', None)
		self.evaluation_id   = kwargs.pop('evaluation_id',None)

		super(MyEvaluationDetailsForm, self).__init__(*args, **kwargs)



class QuatationServiceForm(forms.ModelForm):
	tendative_date = forms.CharField(required=False)
	tendative_dates= forms.CharField(required=False)
	tendative_time = forms.CharField(required=True)
	section_counter= forms.CharField()

	class Meta:
		model = EvaluationBook
		fields = ('service_type','cleaning_method','area_type','location_type','number_of_cleaners','cleaning_hours','estimated_cost','discount','total_cost','cleaning_policy','evaluator_note')
	
	def __init__(self,*args,**kwargs):
		super(QuatationServiceForm, self).__init__(*args, **kwargs)	
		self.fields['service_type'].required    	= True
		self.fields['cleaning_method'].required 	= True
		self.fields['area_type'].required 			= True
		self.fields['area_type'].required 			= True
		self.fields['cleaning_policy'].required 	= True

		self.fields['number_of_cleaners'].required  = True
		self.fields['cleaning_hours'].required 		= True
		self.fields['estimated_cost'].required 		= True
		self.fields['total_cost'].required      	= True