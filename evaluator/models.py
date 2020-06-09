from django.db import models
from user.models import UserProfile,Address
# Create your models here.

GENDER_CHOICES=(
	('MALE','MALE'),
	('FEMALE','FEMALE')
	)


CLEANING_CHOICES=(
	('ONE TIME SERVICE','ONE_TIME_SERVICE'),
	('SUBSCRIPTION','SUBSCRIPTION'),
	)


QUATATION_CHOICES=(
	('REJECTED','REJECTED'),
	('APPROVED','APPROVED'),
	('ASK_FOR_DISCOUNT','ASK_FOR_DISCOUNT'),
	('PENDING','PENDING')
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

EVALUATION_STATUS =(
('EVALUATING','EVALUATING'),
('EVALUATED','EVALUATED'),
('TOBEEVALUATED','TOBEEVALUATED'),
('ONHOLD','ONHOLD')
	)


#Different cleaning service types.Eg:General Cleaning,Carpet Cleaning etc

class ServiceType(models.Model):
	name 			= models.CharField(max_length=100,blank=False,null=False)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

#Different cleaning location types.Eg:Office,Villa,Apartment etc

class LocationType(models.Model):
	name 				= models.CharField(max_length=100,blank=False,null=False)
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)    	

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

#Different Cleaning Types.Eg:Floor Cleaning,Windoe Cleaning etc

class CleaningType(models.Model):
	name 				= models.CharField(max_length=100,blank=False,null=False)
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

#Different Cleaning Methods.Eg:Extraction,Shampooing

class CleaningMethod(models.Model):	
	name 				= models.CharField(max_length=100,blank=False,null=False)
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

#Store the Customer Enquiry Details and Assigned Evaluator Details.

class Evaluation(models.Model):
	evaluation_id		= models.CharField(max_length=100,blank=False,null=False)
	tracking_no         = models.IntegerField(blank=False,null=False)
	call_attender 		= models.ForeignKey(UserProfile,blank=False,null=False,related_name='attender_evaluation')
	attender_notes 		= models.CharField(max_length=500,blank=True,null=True)
	customer			= models.ForeignKey(UserProfile,blank=False,null=False,related_name='customer_evaluation')
	
	cleaning_hours		= models.FloatField(default=0,blank=True,null=True)
	number_of_cleaners	= models.IntegerField(blank=True,null=True)
	estimated_price		= models.FloatField(blank=True,null=True)
	discount_price		= models.FloatField(blank=True,null=True)
	preffered_gender 	= models.CharField(max_length=20,blank=True,null=True,choices=GENDER_CHOICES)

	quatation_status	= models.CharField(max_length=50,blank=True,null=True,choices=QUATATION_CHOICES)
	quatation_approved_date = models.DateTimeField(blank=True,null=True)
	cleaning_policy		= models.CharField(max_length=20,blank=True,null=True,choices=CLEANING_CHOICES)

	subscription_start 	= models.DateTimeField(blank=True,null=True)
	subscription_days_gap=models.IntegerField(blank=True,null=True)
	subscription_end 	= models.DateTimeField(blank=True,null=True)
	no_of_cleanings 	= models.IntegerField(blank=True,null=True)
	
	is_downpayment		= models.BooleanField(null=False,blank=True,default=False)
	no_of_down_payments = models.IntegerField(blank=True,null=True)
	down_payment_deadend= models.DateTimeField(blank=True,null=True)

	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.evaluation_id)

	def __str__(self):
		return self.evaluation_id

#Store the Onsite Details by the Evaluator

class EvaluationDetails(models.Model):
	evaluation 			= models.ForeignKey('Evaluation',blank=True,null=True,related_name='evaluation_details')
	evaluator           = models.ForeignKey(UserProfile,blank=True,null=True,related_name='evaluator_evaluation')
	proposed_time		= models.DateTimeField(blank=True,null=True)
	check_in			= models.DateTimeField(blank=True,null=True)
	check_out			= models.DateTimeField(blank=True,null=True)
	evaluator_note		= models.CharField(max_length=500,blank=True,null=True)
	number_of_cleaners  = models.IntegerField(blank=True,null=True)
	address 			= models.ForeignKey(Address,blank=True,null=True,related_name='evaluation_details_address')
	evaluator_note		= models.CharField(max_length=500,blank=True,null=True)
	estimated_cost      = models.FloatField(blank=True,null=True)
	cleaning_hours 		= models.FloatField(blank=True,null=True)
	status		        = models.CharField(max_length=20,blank=True,null=True,default='TOBEEVALUATED',choices=EVALUATION_STATUS)
	
	
	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)

#For Multiple Cleaning evaluation details
class EvaluationBook(models.Model):
	evaluation_details 	= models.ForeignKey('EvaluationDetails',blank=True,null=True,related_name='evaluation_book_evaluation_details')	
	location_type		= models.ForeignKey('LocationType',blank=True,null=True,related_name='evaluation_book_location_type')
	service_type		= models.ForeignKey('ServiceType',blank=True,null=True,related_name='evaluation_details_service_type')
	cleaning_type 		= models.ForeignKey('CleaningType',blank=True,null=True,related_name='evaluation_book_details_cleaning_type')
	cleaning_method 	= models.ForeignKey('CleaningMethod',blank=True,null=True,related_name='evaluation_book_cleaning_method')
	fabric_type 		= models.CharField(max_length=20,blank=True,null=True,choices=FABRIC_TYPE_CHOICES)
	spot_stain_status	= models.BooleanField(blank=True,null=False)
	size_of_carpet 		= models.CharField(max_length=100,blank=True,null=True)
	piece_of_chairs 	= models.IntegerField(blank=True,null=True)
	set_type 			= models.CharField(max_length=20,blank=True,null=True,choices=SET_TYPE_CHOICES)
	sanitization_type 	= models.CharField(max_length=20,blank=True,null=True,choices=SANITIZATION_TYPE_CHOICES)
	size_to_be_sanitised= models.CharField(max_length=100,blank=True,null=True)
	bed_type 			= models.CharField(max_length=20,blank=True,null=True,choices=BED_TYPE_CHOICES)
	
	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.evaluation_details.id)

	def __str__(self):
		return str(self.evaluation_details.id)
#For Tracking Medias Uploaded by Evaluator on Site

class EvaluationMedia(models.Model):
	evaluation_details 		 = models.ForeignKey('EvaluationDetails',blank=False,null=False)
	media                    = models.FileField(upload_to='evaluation/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_TAKEN_CHOICES)

	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return str(self.evaluation_details.id)

	def __str__(self):
		return str(self.evaluation_details.id)		