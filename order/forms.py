from django import forms
from order.models import Investigation,OrderScheduler,Promocode
from user.models import UserProfile

from django.db.models import Q



class InvestigationForm(forms.ModelForm):
	class Meta:
		model  = Investigation
		fields = ('order_schedule','ticket_types','investigator','notes')
		
	def __init__(self,*args,**kwargs):
		super(InvestigationForm, self).__init__(*args, **kwargs)

		self.fields['order_schedule'] = forms.ModelChoiceField(
		    queryset=OrderScheduler.objects.filter(is_active=True),label='Cleaning Job',required=True,widget=forms.Select(attrs={'class':'order_schedule'}))
		self.fields['investigator'] = forms.ModelChoiceField(
			queryset=UserProfile.objects.filter(user_type='QUALITYCONTROLL',is_active=True),required=True,widget=forms.Select(attrs={'class':'userprofile'}))

class PromocodeForm(forms.ModelForm):
	starting_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), 
                                 input_formats=('%d-%m-%Y',))
	expiry_date   = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), 
                               input_formats=('%d-%m-%Y',))
	class Meta:
		model =	Promocode
		fields= ('promocode','promocode_type','percentage','price','percentage_upto_price','starting_date','expiry_date','total_usage')	
