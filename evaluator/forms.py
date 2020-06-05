from django import forms
from evaluator.models import EvaluationDetails
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