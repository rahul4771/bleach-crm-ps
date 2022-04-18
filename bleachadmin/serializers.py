from rest_framework import serializers
from bleachadmin.models import ServiceAddOns,ServiceProductivity
from agent.serializers import ServiceTypeShowSerializer

class ServiceAddOnsSerializer(serializers.ModelSerializer):
	class Meta:
		model = ServiceAddOns
		fields= ('name','category','size','price','productivity')

class ServiceProductivitySerializer(serializers.ModelSerializer):
	service_type = ServiceTypeShowSerializer(read_only=True)
	class Meta:
		model = ServiceProductivity
		fields= ('__all__')