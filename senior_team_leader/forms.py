from django import forms
from senior_team_leader.models import CleaningTeam,FollowUpTeam
from user.models import UserProfile

#Customer Details add form
class CleaningTeamAssignForm(forms.ModelForm):
	class Meta:
		model   = CleaningTeam
		fields  = ('team_leader','no_of_cleaners','drop_off_driver','pick_up_driver','vehicle_number_drop_off','vehicle_number_pick_up')	
		widgets = {
					'no_of_cleaners':forms.NumberInput(attrs={'readonly':'readonly',}),
		}
	
	def __init__(self,*args,**kwargs):
		super(CleaningTeamAssignForm, self).__init__(*args, **kwargs)
		self.fields['team_leader'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER'),required=True,widget=forms.Select(attrs={'required':'required'}))
		self.fields['drop_off_driver'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='DRIVER'),widget=forms.Select(attrs={'class':'drop_off_driver'}))
		self.fields['pick_up_driver'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='DRIVER'),widget=forms.Select(attrs={'class':'pick_up_driver'}))

#Customer Details add form
class FollowupTeamAssignForm(forms.ModelForm):
	class Meta:
		model   = FollowUpTeam
		fields  = ('team_leader','no_of_cleaners','drop_off_driver','pick_up_driver','vehicle_number_drop_off','vehicle_number_pick_up')	
		widgets = {
					'no_of_cleaners':forms.NumberInput(attrs={'readonly':'readonly',}),
		}

	def __init__(self,*args,**kwargs):
		super(FollowupTeamAssignForm, self).__init__(*args, **kwargs)
		self.fields['team_leader'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER'),required=True,widget=forms.Select(attrs={'required':'required'}))
		self.fields['drop_off_driver'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='DRIVER'),widget=forms.Select(attrs={'class':'drop_off_driver'}))
		self.fields['pick_up_driver'] = forms.ModelChoiceField(
		    queryset=UserProfile.objects.filter(is_active=True,user_type='DRIVER'),widget=forms.Select(attrs={'class':'pick_up_driver'}))
