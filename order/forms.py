from django import forms
from order.models import Investigation,OrderScheduler,SheduledOrderCleanings
from user.models import UserProfile

from django.db.models import Q


class InvestigationForm(forms.ModelForm):
	class Meta:
		model  = Investigation
		fields = ('order_schedule','scheduled_cleaning','investigator','notes')

	def __init__(self,*args,**kwargs):
		super(InvestigationForm, self).__init__(*args, **kwargs)

		self.fields['order_schedule'] = forms.ModelChoiceField(
		    queryset=OrderScheduler.objects.filter(is_active=True),required=True,widget=forms.Select(attrs={'class':'order_schedule'}))
		self.fields['scheduled_cleaning'] = forms.ModelChoiceField(
			queryset=SheduledOrderCleanings.objects.filter(is_active=True),required=True,widget=forms.Select(attrs={'class':'cleaning'}))
		self.fields['investigator'] = forms.ModelChoiceField(
			queryset=UserProfile.objects.filter(Q(Q(is_active=True)&Q(Q(user_type='EVALUATOR')|Q(user_type='SENIORTEAMLEADER')|Q(user_type='TEAMLEADER')))),required=True,widget=forms.Select(attrs={'class':'userprofile'}))				

