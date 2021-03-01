from django import forms
from bleachadmin.models import ServiceProductivity

class ProductivityForm(forms.ModelForm):
	class Meta:
		model  = ServiceProductivity
		fields = ('service_type','perhour_cleaning','perunit_price')

	def __init__(self,*args,**kwargs):
		super(ProductivityForm, self).__init__(*args, **kwargs)

		self.fields['service_type'].required    	= True
		self.fields['perhour_cleaning'].required    = True
		self.fields['perunit_price'].required    = True
		