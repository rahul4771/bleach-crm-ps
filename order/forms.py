from django import forms
from order.models import FollowUpScheduler,OrderScheduler



class OrderSchedulerConfirmationForm(forms.ModelForm):
	class Meta:
		model  = OrderScheduler
		fields = ('status','start_at','end_at')

class FollowUpSchedulerConfirmationForm(forms.ModelForm):
	class Meta:
		model  = FollowUpScheduler
		fields = ('status','start_at','end_at')
