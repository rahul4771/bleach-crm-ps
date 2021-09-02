from rest_framework import serializers
from bleachadmin.models import ServiceAddOns

class ServiceAddOnsSerializer(serializers.ModelSerializer):
	class Meta:
		model = ServiceAddOns
		fields= ('name','category','size','price','productivity')