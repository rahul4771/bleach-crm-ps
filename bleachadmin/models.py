from django.db import models
from evaluator.models import ServiceType

class ServiceProductivity(models.Model):
	service_type     = models.ForeignKey(ServiceType,blank=True,null=True,related_name='productivity_service_type')
	perhour_cleaning = models.CharField(max_length=100,blank=True,null=True)
	perunit_price    = models.FloatField(blank=True,null=True)

	is_active    = models.BooleanField(null=False,blank=True,default=True)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.service_type.name)

	def __str__(self):
		return self.service_type.name

class ServicePriceRange(models.Model):
	service_type     = models.ForeignKey(ServiceType,blank=True,null=True,related_name='pricerange_service_type')
	minimum_area     = models.FloatField(blank=True,null=True)
	maximum_area     = models.FloatField(blank=True,null=True)
	price            = models.FloatField(blank=True,null=True)

	is_active    = models.BooleanField(null=False,blank=True,default=True)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.service_type.name)

	def __str__(self):
		return self.service_type.name