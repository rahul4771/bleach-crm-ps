from django import forms
from order.models import Investigation,OrderScheduler
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