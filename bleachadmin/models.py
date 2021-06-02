from django.db import models
from evaluator.models import ServiceType

SERVICEDIVISION_CHOICES = (('SOFA','SOFA'),
					 ('CHAIR','CHAIR'),
					 ('CURTAIN','CURTAIN'))


class ServiceProductivity(models.Model):
	# service_type     = models.ForeignKey(ServiceType,blank=True,null=True,related_name='productivity_service_type')
	perhour_cleaning = models.CharField(max_length=100,blank=True,null=True)

	is_newkitchen       = models.BooleanField(null=False,blank=True,default=False)
	is_highprice_facade = models.BooleanField(null=False,blank=True,default=False)
	is_highprice_window = models.BooleanField(null=False,blank=True,default=False)
	upholstery_type     = models.CharField(max_length=50,blank=True,null=True,choices=SERVICEDIVISION_CHOICES)

	is_active    = models.BooleanField(null=False,blank=True,default=True)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.created)

	def __str__(self):
		return self.created

class ServicePriceRange(models.Model):
	# service_type     = models.ForeignKey(ServiceType,blank=True,null=True,related_name='pricerange_service_type')
	name             = models.CharField(max_length=100,blank=True,null=True)
	minimum_area     = models.FloatField(blank=True,null=True)
	maximum_area     = models.FloatField(blank=True,null=True)
	price            = models.FloatField(blank=True,null=True)
	unit_price       = models.FloatField(blank=True,null=True)

	is_newkitchen       = models.BooleanField(null=False,blank=True,default=False)
	is_highprice_facade = models.BooleanField(null=False,blank=True,default=False)
	is_highprice_window = models.BooleanField(null=False,blank=True,default=False)
	upholstery_type     = models.CharField(max_length=50,blank=True,null=True,choices=SERVICEDIVISION_CHOICES)

	is_active    = models.BooleanField(null=False,blank=True,default=True)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.price)

	def __str__(self):
		return self.price