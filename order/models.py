from django.db import models
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook
from user.models import UserProfile,Address

import cv2
import os
from bleach_crm_ps.settings import MEDIA_ROOT
# Create your models here.

ORDER_STATUS = (
	('APPROVED_BY_CLIENT','APPROVED_BY_CLIENT'),
	('ORDER_IN_PROGRESS','ORDER_IN_PROGRESS'),
	('ORDER_CANCELLED','ORDER_CANCELLED'),
	('ORDER_CLOSED','ORDER_CLOSED')
	)

FOLLOWUP_STATUS = ( 
	('TICKET_RISED','TICKET_RISED'),
	('INVESTIGATOR_APPROVED','INVESTIGATOR_APPROVED'),
	('FOLLOWUP_IN_PROGRESS','FOLLOWUP_IN_PROGRESS'),
    ('FOLLOWUP_CANCELLED','FOLLOWUP_CANCELLED'),
	('FOLLOWUP_CLOSED','FOLLOWUP_CLOSED')
	)
 
#remove last 3 options 
ORDER_SHEDULER_STATUS = ( 
	('CLEANING_TEAM_ASSIGNED','CLEANING_TEAM_ASSIGNED'),
	('CLEANING_IN_PROGRESS','CLEANING_IN_PROGRESS'),
	('CLEANING_FULFILLED','CLEANING_FULFILLED'),
	)

FOLLOWUP_SHEDULER_STATUS = (
	('FOLLOW_UP_TEAM_ASSIGNED','FOLLOW_UP_TEAM_ASSIGNED'),
	('FOLLOW_UP_CLEANING_IN_PROGRESS','FOLLOW_UP_CLEANING_IN_PROGRESS'),
	('FOLLOW_UP_CLEANING_FULFILLED','FOLLOW_UP_CLEANING_FULFILLED'),
	)


PAYMENT_STATUS = (
	('PENDING','PENDING'),
	('ON_HOLD','ON_HOLD'),
	('COMPLETED','COMPLETED')
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

SUBSCRIPTION_POLICY_CHOICES = (
	('PREMONTHSUBSCRIPTION','PREMONTHSUBSCRIPTION'),
	('POSTMONTHSUBSCRIPTION','POSTMONTHSUBSCRIPTION')
	)


#Store the Order Details.DownPayment,Subscription and Direct Cleaning Comes Under a Single Order

class Order(models.Model):
	evaluation 		= models.ForeignKey(Evaluation,blank=False,null=False,related_name='evaluation_order')
	order_no   		= models.CharField(max_length=20,blank=False,null=False)
	order_status 	= models.CharField(max_length=50,blank=True,null=True,choices=ORDER_STATUS)

	payment_status         = models.CharField(max_length=50,blank=True,null=True,default='PENDING',choices=PAYMENT_STATUS)
	payment_completed_date = models.DateTimeField(blank=True,null=True)
	total_amount           = models.FloatField(blank=True,null=True,default=0)
	amount_paid            = models.FloatField(blank=True,null=True,default=0)
	remining_amount        = models.FloatField(blank=True,null=True,default=0)
	preamount_paid		   = models.FloatField(blank=True,null=True,default=0)
	postamount_paid		   = models.FloatField(blank=True,null=True,default=0)
	
	
	instructions		   = models.CharField(max_length=5000,blank=True,null=True)
	
	feedback_notes  	= models.CharField(max_length=5000,blank=True,null=True)
	is_feedback_marked	= models.BooleanField(null=False,blank=True,default=False)
	feedback_marked_date= models.DateTimeField(blank=True,null=True)

	created_by      = models.ForeignKey(UserProfile,blank=True,null=True)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order_no)

	def __str__(self):
		return self.order_no


#Devide an Order into a number of Schedules.This is to handle multiple days cleaning,multiple address cleaning Subscription Cleaning etc...
class PaymentSubscriptionDetails(models.Model):
	amount              = models.IntegerField(blank=True,null=True)
	subscription_policy = models.CharField(max_length=100,blank=True,null=True,choices=SUBSCRIPTION_POLICY_CHOICES)
	is_paid             = models.BooleanField(null=False,blank=True,default=True)
	paid_date 			= models.DateTimeField(blank=True,null=True)
	
	is_active           = models.BooleanField(null=False,blank=True,default=True)
	created             = models.DateTimeField(auto_now_add=True)
	updated             = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.subscription_policy)

	def __str__(self):
		return str(self.subscription_policy)



class OrderScheduler(models.Model):
	order 			     = models.ForeignKey('Order',blank=False,null=False,related_name='order_scheduler_order')
	evaluation_details   = models.ForeignKey(EvaluationDetails,blank=True,null=True,related_name='order_scheduler_evaluationdetails')
	order_scheduler_book = models.ForeignKey(EvaluationBook,blank=True,null=True,related_name='order_scheduler_book_details')
	payment_subscription = models.ForeignKey('PaymentSubscriptionDetails',blank=True,null=True,related_name='paymentsubscription')

	start_at		   	 = models.DateTimeField(blank=True,null=True)
	end_at			   	 = models.DateTimeField(blank=True,null=True)
	customer_address	 = models.ForeignKey(Address,blank=True,null=True)
	work_status 		 = models.CharField(max_length=50,blank=True,null=True,choices=ORDER_SHEDULER_STATUS)
	status      		 = models.CharField(max_length=20,blank=True,null=True,default='WAITING',choices=SCHEDULER_CHOICES)

	complaint            = models.CharField(max_length=5000,blank=True,null=True)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)



#If the Customer is not Satisfied and reported a complaint. An Investigation team is assigned for Investigation

class Investigation(models.Model):
	order 				 = models.ForeignKey('Order',blank=False,null=False,related_name='investigation_orders')
	order_schedule		 = models.ForeignKey('OrderScheduler',blank=False,null=False,related_name='investigations_orderschedule')	
	investigator    	 = models.ForeignKey(UserProfile,blank=True,null=True)
	assigned_by          = models.ForeignKey(UserProfile,blank=True,null=True,related_name='investigation_assigned_by')
	sheduled_at 		 = models.DateTimeField(blank=True,null=True)
	check_in 		     = models.DateTimeField(blank=True,null=True)
	check_out 		     = models.DateTimeField(blank=True,null=True)
	notes 				 = models.CharField(max_length=5000,blank=True,null=True)
	is_followup_approved = models.BooleanField(null=False,blank=True,default=False)
	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)

#For Tracking Medias Uploaded by Investigator on Site

class InvestigationMedia(models.Model):
	investigation 			 = models.ForeignKey('Investigation',blank=False,null=False,related_name='investigation_media')
	media                    = models.FileField(upload_to='investigation/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=True,null=True,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=True,null=True,choices=MEDIA_TAKEN_CHOICES)
	is_active            	 = models.BooleanField(null=False,blank=True,default=True)
	
	def save(self,*args, **kwargs):
		super(InvestigationMedia, self).save(*args, **kwargs)
		
		file_path = os.path.abspath(os.path.join(MEDIA_ROOT, self.media.name))
		img       = cv2.imread(file_path)
		cv2.imwrite(file_path, img, [cv2.IMWRITE_JPEG_QUALITY,20])

	def __unicode__(self):
		return str(self.investigation.id)

	def __str__(self):
		return str(self.investigation.id)

#Followup details for followup order.Followup granded by Investigator

class FollowUp(models.Model): 
	investigation   = models.ForeignKey('Investigation',blank=False,null=False,related_name='followup_investigation') 
	instructions    = models.CharField(max_length=500,blank=True,null=True)
	status      	= models.CharField(max_length=100,blank=True,null=True,choices=FOLLOWUP_STATUS)
	no_of_cleaners  = models.IntegerField(blank=True,null=True)
	cleaning_hours  = models.IntegerField(blank=True,null=True)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)

#Devide an Followup into a number of Schedules.This is to handle multiple days cleaning,multiple address cleaning Subscription Cleaning etc...


class FollowUpScheduler(models.Model):
	follow_up 			= models.ForeignKey('FollowUp',blank=False,null=False,related_name='follow_up_of_scheduler')
	#cleaning_type & other details get from Investigation Model 
	start_at		    = models.DateTimeField(blank=True,null=True)
	end_at			    = models.DateTimeField(blank=True,null=True)
	customer_address	= models.ForeignKey(Address,blank=True,null=True)
	work_status 	    = models.CharField(max_length=50,blank=True,null=True,choices=FOLLOWUP_SHEDULER_STATUS)
	status      		= models.CharField(max_length=50,blank=True,null=True,default='WAITING',choices=SCHEDULER_CHOICES)
	
	is_active       	= models.BooleanField(null=False,blank=True,default=True)
	created         	= models.DateTimeField(auto_now_add=True)
	updated         	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)

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
