from django import forms
from bleachadmin.models import ServiceProductivity,ServicePriceRange

class ProductivityForm(forms.ModelForm):
	class Meta:
		model  = ServiceProductivity
		fields = ('service_type','perhour_cleaning')

	def __init__(self,*args,**kwargs):
		super(ProductivityForm, self).__init__(*args, **kwargs)

		self.fields['service_type'].required    	= True
		self.fields['perhour_cleaning'].required    = True
		
class ServicePriceRangeForm(forms.ModelForm):
	class Meta:
		model = ServicePriceRange
		fields= ('service_type','name','minimum_area','maximum_area','price','unit_price','is_newkitchen','is_highprice_facade','is_highprice_window','upholstery_type')