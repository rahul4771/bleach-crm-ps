from django import forms
from user.models import UserProfile,Address,Governorate,Area

#Customer Details add form
class UserProfileForm(forms.ModelForm):
	class Meta:
		model  = UserProfile
		fields = ('name','gender','email','nationality','company','job_title','mobile_number','phone_number','sms_preference',)	
	
	def __init__(self,*args,**kwargs):
		super(UserProfileForm, self).__init__(*args, **kwargs)

		self.fields['name'].required          = True
		self.fields['gender'].required        = True
		self.fields['email'].required         = True
		self.fields['mobile_number'].required = True
		self.fields['phone_number'].required  = True


#Customer Address add form
class AddressForm(forms.ModelForm):
	class Meta:
		model  = Address
		fields = ('governorate','area','block','avenue','building','street','floor','apartment')	

	def __init__(self,*args,**kwargs):
		super(AddressForm, self).__init__(*args, **kwargs)

		self.fields['governorate'] = forms.ModelChoiceField(
		    queryset=Governorate.objects.filter(is_active=True),required=True,widget=forms.Select(attrs={'class':'governorate'}))
		self.fields['area'] = forms.ModelChoiceField(
			queryset=Area.objects.filter(is_active=True),required=True,widget=forms.Select(attrs={'class':'area'}))
		
