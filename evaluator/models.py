from django.db import models
from user.models import UserProfile,Address
from django.db.models.signals import post_delete
from django.dispatch import receiver

import cv2
import os
from bleach_crm_ps.settings import MEDIA_ROOT
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
	('APPROVED','APPROVED'),
	('PENDING','PENDING'),
	('REJECTED','REJECTED'),
	('EXPIRED','EXPIRED')
	)

DIRTLEVEL_CHOICES=(
	('LOW','LOW'),
	('MEDIUM','MEDIUM'),
	('HIGH','HIGH')
	)

FLOOR_CHOICES=(
	('CERAMIC','CERAMIC'),
	('WOOD','WOOD'),
	('CONCRETE','CONCRETE')
	)

FABRIC_TYPE_CHOICES=(
	('SYNTHETIC','SYNTHETIC'),
	('NATURAL','NATURAL'))

SET_SIZE_CHOICES=(
	('SMALL_SET','SMALL_SET'),
	('MEDIUM_SET','MEDIUM_SET'),
	('LARGE_SET','LARGE_SET')
	)

SET_TYPE_CHOICES=(
	('TYPE1','TYPE1'),
	('TYPE2','TYPE2'),
	('TYPE3','TYPE3')
	)


SANITIZATION_TYPE_CHOICES=(
	('SANITIZATION','SANITIZATION'),
	('DISINFECTION','DISINFECTION'),
	('STERILIZATION','STERILIZATION'))

BED_SIZE_CHOICES=(
	('SINGLE_BED','SINGLE_BED'),
	('DOUBLE_BED','DOUBLE_BED'),
	('QUEEN_BED','QUEEN_BED'),
	('KIND_BED','KIND_BED'))

BED_TYPE_CHOICES=(
	('TYPE1','TYPE1'),
	('TYPE2','TYPE2'),
	('TYPE3','TYPE3'))

SPOT_STAIN_CHOICES=(
	('SPOT','SPOT'),
	('STAIN','STAIN')
	)

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
('ONHOLD','ONHOLD'),
	)


PAYMENT_CHOICES =(
	('PREPAID','PREPAID'),
	('POSTPAID','POSTPAID'),
	('BREAKDOWN','BREAKDOWN'),
	)

PAYMENT_WAYS =(
	('ONLINE','ONLINE'),
	('CASH/CHEQUE','CASH/CHEQUE'),
	)

#Different cleaning service types.Eg:General Cleaning,Carpet Cleaning etc

class ServiceType(models.Model):
	name 			= models.CharField(max_length=100,blank=False,null=False)
	name_arabic     = models.CharField(max_length=100,blank=False,null=False)
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
	service_type 		= models.ForeignKey('ServiceType',blank=True,null=True,related_name='method_service_type')
	
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name

class AreaType(models.Model):	
	name 				= models.CharField(max_length=100,blank=False,null=False)
	
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.name)

	def __str__(self):
		return self.name		

class CleaningSection(models.Model):	
	name 				= models.CharField(max_length=100,blank=False,null=False)
	service_type 		= models.ForeignKey('ServiceType',blank=True,null=True)
	
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
	tracking_no         = models.CharField(max_length=20,blank=False,null=False)

	call_attender 		= models.ForeignKey(UserProfile,blank=False,null=False,related_name='attender_evaluation')
	attender_notes 		= models.CharField(max_length=500,blank=True,null=True)
	customer			= models.ForeignKey(UserProfile,blank=False,null=False,related_name='customer_evaluation')

	estimated_cost		= models.FloatField(blank=True,null=True,default=0)
	discount			= models.FloatField(blank=True,null=True,default=0)
	total_cost          = models.FloatField(blank=True,null=True,default=0)

	quatation_status		= models.CharField(max_length=50,blank=True,null=True,choices=QUATATION_CHOICES)
	quatation_approved_date = models.DateTimeField(blank=True,null=True)
	quatation_rejected_date = models.DateTimeField(blank=True,null=True)

	quatation_expiry_date   = models.DateTimeField(blank=True,null=True)
	
	payment_method			= models.CharField(max_length=20,blank=True,null=True,choices=PAYMENT_CHOICES)
	payment_way             = models.CharField(max_length=20,blank=True,null=True,choices=PAYMENT_WAYS)
	before_cleaning_amount	= models.FloatField(blank=True,null=True)
	after_cleaning_amount	= models.FloatField(blank=True,null=True)

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
	address 			= models.ForeignKey(Address,blank=True,null=True,related_name='evaluation_details_address')
	
	evaluator_note		= models.CharField(max_length=500,blank=True,null=True)
	estimated_cost      = models.FloatField(blank=True,null=True,default=0)
	discount            = models.FloatField(blank=True,null=True,default=0)
	total_cost          = models.FloatField(blank=True,null=True,default=0)
	
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
	
	cleaning_policy		= models.CharField(max_length=20,blank=True,null=True,choices=CLEANING_CHOICES)
	service_type		= models.ForeignKey('ServiceType',blank=True,null=True,related_name='evaluation_details_service_type')
	area_type	 		= models.CharField(max_length=100,blank=True,null=True)
	cleaning_method 	= models.CharField(max_length=100,blank=True,null=True)
	location_type		= models.CharField(max_length=100,blank=True,null=True)

	number_of_cleaners  = models.IntegerField(blank=True,null=True)
	estimated_cost      = models.FloatField(blank=True,null=True)
	discount            = models.FloatField(blank=True,null=True,default=0)
	total_cost          = models.FloatField(blank=True,null=True)
	cleaning_hours 		= models.FloatField(blank=True,null=True)
	evaluator_note		= models.CharField(max_length=500,blank=True,null=True)
	
	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)
#For Tracking Medias Uploaded by Evaluator on Site

class EvaluationMedia(models.Model):
	evaluation_book 		 = models.ForeignKey('EvaluationBook',blank=False,null=False,related_name='evaluationbookmedia')
	media                    = models.FileField(upload_to='evaluationbook/',blank=True,null=True,max_length=1000)
	media_type 				 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_TAKEN_CHOICES)

	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)
	

	def __unicode__(self):
		return str(self.evaluation_book.id)

	def __str__(self):
		return str(self.evaluation_book.id)	

	def save(self,*args, **kwargs):
		super(EvaluationMedia, self).save(*args, **kwargs)

		file_path = os.path.abspath(os.path.join(MEDIA_ROOT, self.media.name))
		img       = cv2.imread(file_path)
		cv2.imwrite(file_path, img, [cv2.IMWRITE_JPEG_QUALITY,20])

		

@receiver(post_delete, sender=EvaluationMedia)
def submission_delete(sender, instance, **kwargs):
    instance.media.delete(False) 		

# file_path = os.path.abspath(os.path.join(MEDIA_ROOT, self.media.name))
# print(file_path,"file pathhhhhhhhhhhhhhh")
# img       = cv2.imread(file_path,0)
# cv2.imwrite(img, [cv2.IMWRITE_JPEG_QUALITY,20])
    

class EvaluationBookSection(models.Model):
	evaluation_book = models.ForeignKey('EvaluationBook',blank=False,null=False,related_name='evaluationsection_book')
	section_name 	= models.CharField(max_length=100,blank=False,null=False)
	section_name_arabic = models.CharField(max_length=100,blank=False,null=False)
	category		= models.CharField(max_length=100,blank=True,null=True)
	dirt_level		= models.CharField(max_length=100,blank=True,null=True)

	quantity    	= models.CharField(max_length=100,blank=True,null=True)
	size        	= models.CharField(max_length=100,blank=True,null=True)
	unit        	= models.CharField(max_length=100,blank=True,null=True)
	age         	= models.CharField(max_length=100,blank=True,null=True)
	
	floor       	= models.CharField(max_length=100,blank=True,null=True)
	apartment   	= models.CharField(max_length=100,blank=True,null=True)
	room        	= models.CharField(max_length=100,blank=True,null=True)
	
	wall_type   	= models.CharField(max_length=100,blank=True,null=True)
	ceiling_type	= models.CharField(max_length=100,blank=True,null=True)
	floor_type  	= models.CharField(max_length=100,blank=True,null=True)
	material    	= models.CharField(max_length=100,blank=True,null=True)
	colour      	= models.CharField(max_length=100,blank=True,null=True)
	cause_of_stain	= models.CharField(max_length=100,blank=True,null=True)

	section_cost    = models.FloatField(blank=True,null=True)

	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		for field_name in ['size','wall_type','ceiling_type','floor_type','material','colour','cause_of_stain']:
			val = getattr(self, field_name, False)
			if val:
				setattr(self, field_name, val.title())
		super(EvaluationBookSection, self).save(*args, **kwargs)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)	


class EvaluationSectionKeynote(models.Model):
	evaluation_section = models.ForeignKey('EvaluationBookSection',blank=False,null=False,related_name='keynotesections')
	sub_area 		   = models.CharField(max_length=100,blank=True,null=True)
	quantity 		   = models.CharField(max_length=100,blank=True,null=True)
	completion_status  = models.BooleanField(null=False,blank=True,default=False)

	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)