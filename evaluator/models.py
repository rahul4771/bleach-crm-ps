from django.db import models
from user.models import UserProfile,Address
# Create your models here.

GENDER_CHOICES=(
	('MALE','MALE'),
	('FEMALE','FEMALE')
	)


PAYMENT_CHOICES=(
	('ONE_TIME','ONE_TIME'),
	('SUBSCRIPTION','SUBSCRIPTION'),
	('DOWN_PAYMENT','DOWN_PAYMENT')
	)


QUATATION_CHOICES=(
	('REJECTED','REJECTED'),
	('APPROVED','APPROVED'),
	('ASK_FOR_DISCOUNT','ASK_FOR_DISCOUNT')
	)

FABRIC_TYPE_CHOICES=(
	('SYNTHETIC','SYNTHETIC'),
	('NATURAL','NATURAL'))

SET_TYPE_CHOICES=(
	('SMALL_SET','SMALL_SET'),
	('MEDIUM_SET','MEDIUM_SET'),
	('LARGE_SET','LARGE_SET')
	)

SANITIZATION_TYPE_CHOICES=(
	('SANITIZATION','SANITIZATION'),
	('DISINFECTION','DISINFECTION'),
	('STERILIZATION','STERILIZATION'))

BED_TYPE_CHOICES=(
	('SINGLE_BED','SINGLE_BED'),
	('QUEEN_BED','QUEEN_BED'),
	('KIND_BED','KIND_BED'))

MEDIA_TAKEN_CHOICES = (
	('CUSTOMER_SEND','CUSTOMER_SEND'),
	('AGENT_TAKEN','AGENT_TAKEN'),
	)

MEDIA_CHOICES = (
	('PHOTO','PHOTO'),
	('VIDEO','VIDEO'),
	('AUDIO','AUDIO')
	)

class ServiceType(models.Model):
	name 			= models.CharField(max_length=100,blank=False,null=False)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

class LocationType(models.Model):
	name 				= models.CharField(max_length=100,blank=False,null=False)
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)    	

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

class CleaningType(models.Model):
	name 				= models.CharField(max_length=100,blank=False,null=False)
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

class CleaningMethod(models.Model):	
	name 				= models.CharField(max_length=100,blank=False,null=False)
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

class Evaluation(models.Model):
	evaluation_id		= models.CharField(max_length=100,blank=False,null=False)
	call_attender 		= models.ForeignKey(UserProfile,blank=False,null=False,related_name='attender_evaluation')
	attender_notes 		= models.CharField(max_length=500,blank=True,null=True)
	customer			= models.ForeignKey(UserProfile,blank=False,null=False,related_name='customer_evaluation')
	
	evaluator           = models.ForeignKey(UserProfile,blank=True,null=True,related_name='evaluator_evaluation')
	prposed_time		= models.DateTimeField(blank=True,null=True)
	check_in			= models.DateTimeField(blank=True,null=True)
	check_out			= models.DateTimeField(blank=True,null=True)
	
	evaluator_note		= models.CharField(max_length=500,blank=True,null=True)
	cleaning_hours		= models.FloatField(default=0,blank=True,null=True)
	number_of_cleaners	= models.IntegerField(blank=True,null=True)
	estimated_price		= models.FloatField(blank=True,null=True)
	discount_price		= models.FloatField(blank=True,null=True)
	preffered_gender 	= models.CharField(max_length=20,blank=True,null=True,choices=GENDER_CHOICES)

	quatation_status	= models.CharField(max_length=50,blank=True,null=True,choices=QUATATION_CHOICES)
	payment_policy		= models.CharField(max_length=20,blank=True,null=True,choices=PAYMENT_CHOICES)

	subscription_start 	= models.DateTimeField(blank=True,null=True)
	subscription_end 	= models.DateTimeField(blank=True,null=True)
	no_of_cleanings 	= models.IntegerField(blank=True,null=True)
	no_of_down_payments = models.IntegerField(blank=True,null=True)
	down_payment_deadend= models.DateTimeField(blank=True,null=True)

	def __unicode__(self):
		return str(self.evaluation_id)

	def __str__(self):
		return self.evaluation_id


class EvaluationDetails(models.Model):
	evaluation 			= models.ForeignKey('Evaluation',blank=True,null=True,related_name='evaluation_details')
	service_type		= models.ForeignKey('ServiceType',blank=True,null=True,related_name='evaluation_details_service_type')
	location_type		= models.ForeignKey('LocationType',blank=True,null=True,related_name='evaluation_details_location_type')
	address 			= models.ForeignKey(Address,blank=True,null=True,related_name='evaluation_details_address')
	evaluator_note		= models.CharField(max_length=500,blank=True,null=True)
	estimated_cost      = models.FloatField(blank=True,null=True)
	cleaning_hours 		= models.FloatField(blank=True,null=True)
	number_of_cleaners  = models.IntegerField(blank=True,null=True)
	cleaning_type 		= models.ForeignKey('CleaningType',blank=True,null=True,related_name='evaluation_details_cleaning_type')
	cleaning_method 	= models.ForeignKey('CleaningMethod',blank=True,null=True,related_name='evaluation_details_cleaning_method')
	fabric_type 		= models.CharField(max_length=20,blank=True,null=True,choices=FABRIC_TYPE_CHOICES)
	spot_stain_status	= models.BooleanField(blank=True,null=False)
	size_of_carpet 		= models.CharField(max_length=100,blank=True,null=True)
	piece_of_chairs 	= models.IntegerField(blank=True,null=True)
	set_type 			= models.CharField(max_length=20,blank=True,null=True,choices=SET_TYPE_CHOICES)
	sanitization_type 	= models.CharField(max_length=20,blank=True,null=True,choices=SANITIZATION_TYPE_CHOICES)
	size_to_be_sanitised= models.CharField(max_length=100,blank=True,null=True)
	bed_type 			= models.CharField(max_length=20,blank=True,null=True,choices=BED_TYPE_CHOICES)
	
	def __unicode__(self):
		return str(self.evaluation.evaluation_id)

	def __str__(self):
		return self.evaluation.evaluation_id

class EvaluationMedia(models.Model):
	evaluation_details 			 	 = models.ForeignKey('EvaluationDetails',blank=False,null=False)
	media                    = models.FileField(upload_to='evaluation/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_TAKEN_CHOICES)

	def __unicode__(self):
		return str(self.evaluation_details.evaluation.evaluation_no)

	def __str__(self):
		return self.evaluation_details.evaluation.evaluation_no		