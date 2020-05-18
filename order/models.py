from django.db import models
from evaluator.models import Evaluation,EvaluationDetails
from user.models import UserProfile,Address
# Create your models here.

ORDER_STATUS = (
	('APPROVED_BY_CLIENT','APPROVED_BY_CLIENT'),
	('ORDER_IN_PROGRESS','ORDER_IN_PROGRESS'),
	('ORDER_CANCELLED','ORDER_CANCELLED'),
	('ORDER_CLOSED','ORDER_CLOSED')
	)

FOLLOWUP_STATUS = (
	('APPROVED_BY_CLIENT','APPROVED_BY_CLIENT'),
	('INVESTIGATOR_ASSIGNED','INVESTIGATOR_ASSIGNED'),
	('INVESTIGATOR_APPROVED','INVESTIGATOR_APPRVED'),
	('FOLLOWUP_IN_PROGRESS','FOLLOWUP_IN_PROGRESS'),
	('FOLLOWUP_CANCELLED','FOLLOWUP_CANCELLED'),
	('FOLLOWUP_CLOSED','FOLLOWUP_CLOSED')
	)
 
ORDER_SHEDULER_STATUS = ( 
	('CLEANING_TEAM_ASSIGNED','CLEANING_TEAM_ASSIGNED'),
	('CLEANING_IN_PROGRESS','CLEANING_IN_PROGRESS'),
	('CLEANING_FULFILLED','CLEANING_FULFILLED'),
	('INVESTIGATION_ASSIGNED','INVESTIGATION_ASSIGNED'),
	('INVESTIGATION_IN_PROGRESS','INVESTIGATION_IN_PROGRESS'),
	('INVESTIGATION_COMPLETED','INVESTIGATION_COMPLETED'),
	)

FOLLOWUP_SHEDULER_STATUS = (
	('FOLLOW_UP_TEAM_ASSIGNED','FOLLOW_UP_TEAM_ASSIGNED'),
	('FOLLOW_UP_CLEANING_IN_PROGRESS','FOLLOW_UP_CLEANING_IN_PROGRESS'),
	('FOLLOW_UP_CLEANING_FULFILLED','FOLLOW_UP_CLEANING_FULFILLED'),
	)


PAYMENT_STATUS = (
	('DOWN_PAYMENT_PENDING','DOWN_PAYMENT_PENDING'),
	('DOWN_PAYMENT_FULFILLED','DOWN_PAYMENT_PENDING_FULFILLED'),
	('OUT_STANDING_PENDING','OUT_STANDING_PENDING'),
	('OUT_STANDING_FULFILLED','OUT_STANDING_FULFILLED'),
	('SUBSCRIPTION_PENDING','SUBSCRIPTION_PENDING'),
	('SUBSCRIPTION_FULFILLED','SUBSCRIPTION_FULFILLED')
	)

MEDIA_TAKEN_CHOICES = (
	('CUSTOMER_SEND','CUSTOMER_SEND'),
	('BEFORE_CLEANING','BEFORE_CLEANING'),
	('AFTER_CLEANING','AFTER_CLEANING')
	)

MEDIA_CHOICES = (
	('PHOTO','PHOTO'),
	('VIDEO','VIDEO'),
	('AUDIO','AUDIO')
	)

#date confirmation like
SCHEDULER_CHOICES = (
	('WAITING','WAITING'),
	('CONFIRMED','CONFIRMED'),
	('HOLDING','HOLDING'),
	('CANCELLED','CANCELLED')
	)
#Store the Order Details.DownPayment,Subscription and Direct Cleaning Comes Under a Single Order

class Order(models.Model):
	evaluation 		= models.ForeignKey(Evaluation,blank=False,null=False)
	order_no   		= models.CharField(max_length=20,blank=False,null=False)
	order_status 	= models.CharField(max_length=20,blank=True,null=True,choices=ORDER_STATUS)
	payment_status  = models.CharField(max_length=20,blank=True,null=True,choices=PAYMENT_STATUS)
	instructions	= models.CharField(max_length=500,blank=True,null=True)
	created_by      = models.ForeignKey(UserProfile,blank=True,null=True)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order_no)

	def __str__(self):
		return self.order_no


#Devide an Order into a number of Schedules.This is to handle multiple days cleaning,multiple address cleaning Subscription Cleaning etc...

class OrderScheduler(models.Model):
	order 			   = models.ForeignKey('Order',blank=False,null=False)
	evaluation_details = models.ForeignKey(EvaluationDetails,blank=True,null=True)
	start_at		   = models.DateTimeField(blank=True,null=True)
	end_at			   = models.DateTimeField(blank=True,null=True)
	#cleaning_type & other details
	customer_address= models.ForeignKey(Address,blank=True,null=True)
	work_status 	= models.CharField(max_length=20,blank=True,null=True,choices=ORDER_SHEDULER_STATUS)
	status      	= models.CharField(max_length=20,blank=True,null=True,default='WAITING',choices=SCHEDULER_CHOICES)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order.order_no)

	def __str__(self):
		return self.order.order_no

#If the Customer is not Satisfied and reported a complaint. An Investigation team is assigned for Investigation

class Investigation(models.Model):
	order 				 = models.ForeignKey('Order',blank=False,null=False)
	order_schedule		 = models.ForeignKey('OrderScheduler',blank=False,null=False)	
	problem 			 = models.CharField(max_length=100,blank=True,null=True)
	description     	 = models.CharField(max_length=500,blank=True,null=True)
	investigator    	 = models.ForeignKey(UserProfile,blank=True,null=True)
	sheduled_at 		 = models.DateTimeField(blank=True,null=True)
	notes 				 = models.CharField(max_length=500,blank=True,null=True)
	is_followup_approved = models.BooleanField(null=False,blank=True,default=False)
	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order.order_no)

	def __str__(self):
		return self.order.order_no


#For Tracking Medias Uploaded by Investigator on Site

class InvestigationMedia(models.Model):
	investigation 			 = models.ForeignKey('Investigation',blank=False,null=False)
	media                    = models.FileField(upload_to='investigation/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_TAKEN_CHOICES)

	def __unicode__(self):
		return str(self.investigation.order.order_no)

	def __str__(self):
		return self.investigation.order.order_no

#Followup details for followup order.Followup granded by Investigator

class FollowUp(models.Model): 
	investigation   = models.ForeignKey('INVESTIGATION',blank=False,null=False) 
	instructions    = models.CharField(max_length=500,blank=True,null=True)
	status      	= models.CharField(max_length=20,blank=True,null=True,choices=FOLLOWUP_STATUS)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.investigation.order.order_no)

	def __str__(self):
		return self.investigation.order.order_no

#Devide an Followup into a number of Schedules.This is to handle multiple days cleaning,multiple address cleaning Subscription Cleaning etc...


class FollowUpScheduler(models.Model):
	follow_up 			= models.ForeignKey('FollowUp',blank=False,null=False,related_name='follow_up_of_scheduler')
	#cleaning_type & other details
	start_at		    = models.DateTimeField(blank=True,null=True)
	end_at			    = models.DateTimeField(blank=True,null=True)
	customer_address	= models.ForeignKey(Address,blank=True,null=True)
	work_status 	    = models.CharField(max_length=20,blank=True,null=True,choices=FOLLOWUP_SHEDULER_STATUS)
	status      		= models.CharField(max_length=20,blank=True,null=True,default='WAITING',choices=SCHEDULER_CHOICES)
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.follow_up.investigation.order.order_no)

	def __str__(self):
		return self.follow_up.investigation.order.order_no

#Questions asked by Agent to Customer, after cleaning.

class Question(models.Model):
	question 			= models.CharField(max_length=500,blank=False,null=False)
	is_active          	= models.BooleanField(null=False,blank=True,default=True)
	created            	= models.DateTimeField(auto_now_add=True)
	updated            	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.question)

	def __str__(self):
		return self.question

#Storing Feedback of Customer, after cleaning

class FeedBack(models.Model):
	order 				= models.ForeignKey('Order',blank=False,null=False,related_name='feed_backs_order')
	question			= models.ForeignKey('Question',blank=False,null=False)
	rating				= models.IntegerField(blank=True,null=True)
	response_date		= models.DateTimeField(blank=True,null=True)
	is_active          	= models.BooleanField(null=False,blank=True,default=True)
	created            	= models.DateTimeField(auto_now_add=True)
	updated            	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order.order_no)

	def __str__(self):
		return self.order.order_no