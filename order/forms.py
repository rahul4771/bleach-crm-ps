from django import forms
from order.models import Investigation,OrderScheduler
from user.models import UserProfile

from django.db.models import Q



class InvestigationForm(forms.ModelForm):
	sheduled_at = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M %p'],widget=forms.TextInput(attrs={'required':'required','class':'date_time_pick',}))
	class Meta:
		model  = Investigation
		fields = ('order_schedule','investigator','sheduled_at','notes')
		
	def __init__(self,*args,**kwargs):
		super(InvestigationForm, self).__init__(*args, **kwargs)

		self.fields['order_schedule'] = forms.ModelChoiceField(
		    queryset=OrderScheduler.objects.filter(is_active=True),label='Cleaning Job',required=True,widget=forms.Select(attrs={'class':'order_schedule'}))
		self.fields['investigator'] = forms.ModelChoiceField(
			queryset=UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='EVALUATOR')|Q(user_type='SENIORTEAMLEADER')|Q(user_type='TEAMLEADER')))),required=True,widget=forms.Select(attrs={'class':'userprofile'}))