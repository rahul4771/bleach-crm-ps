from django.db import models
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook
from user.models import UserProfile,Address

import cv2
import os
from bleach_crm_ps.settings import MEDIA_ROOT
from django.utils import timezone
from django.db.models import Max
# Create your models here.

ORDER_STATUS = (
	('APPROVED_BY_CLIENT','APPROVED_BY_CLIENT'),
	('ORDER_IN_PROGRESS','ORDER_IN_PROGRESS'),
	('ORDER_CANCELLED','ORDER_CANCELLED'),
	('ORDER_CLOSED','ORDER_CLOSED')
	)

FOLLOWUP_STATUS = ( 
	('TICKET_RISED','TICKET_RISED'),
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

INVOICE_CHOICES = (
	('CANCELLED','CANCELLED'),
	('ACTIVE','ACTIVE'),
	)


INVESTIGATION_CATEGORY_CHOICES = (
	('SERVICEQUALITY','SERVICEQUALITY'),
	('DAMAGE','DAMAGE'),
	)

PROMOCODE_TYPE_CHOICES =(
	('PERCENTAGE','PERCENTAGE'),
	('AMOUNT','AMOUNT'),
	)
#Store the Order Details.DownPayment,Subscription and Direct Cleaning Comes Under a Single Order

class Order(models.Model):
	evaluation 		= models.ForeignKey(Evaluation,blank=False,null=False,related_name='evaluation_order')
	order_no   		= models.CharField(max_length=20,blank=False,null=False)
	order_status 	= models.CharField(max_length=50,blank=True,null=True,choices=ORDER_STATUS)

	invoice_no      = models.CharField(max_length=20,blank=True,null=True)
	invoice_status  = models.CharField(max_length=50,blank=True,null=True,choices=INVOICE_CHOICES)

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
	order 			    = models.ForeignKey('Order',blank=False,null=False,related_name='ordersubscription')
	actual_amount       = models.FloatField(blank=True,null=True)
	discount            = models.FloatField(blank=True,null=True)
	amount              = models.FloatField(blank=True,null=True)
	is_paid             = models.BooleanField(null=False,blank=True,default=False)
	paid_date 			= models.DateTimeField(blank=True,null=True)
	monthyear           = models.CharField(max_length=100,blank=True,null=True)
	
	is_active           = models.BooleanField(null=False,blank=True,default=True)
	created             = models.DateTimeField(auto_now_add=True)
	updated             = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)



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

	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order.order_no)

	def __str__(self):
		return str(self.order.order_no)



#If the Customer is not Satisfied and reported a complaint. An Investigation team is assigned for Investigation

class Investigation(models.Model):
	order 				 = models.ForeignKey('Order',blank=False,null=False,related_name='investigation_orders')
	ticket_types         = models.CharField(max_length=5000,blank=True,null=True)
	order_schedule		 = models.ForeignKey('OrderScheduler',blank=False,null=False,related_name='investigations_orderschedule')	
	investigator    	 = models.ForeignKey(UserProfile,blank=True,null=True)
	assigned_by          = models.ForeignKey(UserProfile,blank=True,null=True,related_name='investigation_assigned_by')
	scheduled_at 		 = models.DateTimeField(blank=True,null=True)
	check_in 		     = models.DateTimeField(blank=True,null=True)
	check_out 		     = models.DateTimeField(blank=True,null=True)
	notes 				 = models.CharField(max_length=5000,blank=True,null=True)


	is_followup_approved           = models.BooleanField(null=False,blank=True,default=False)
	is_buybackgiftpromo_approved   = models.BooleanField(null=False,blank=True,default=False)
	is_paybackdiscount_approved    = models.BooleanField(null=False,blank=True,default=False)
	is_internalreporting_approved  = models.BooleanField(null=False,blank=True,default=False)
	
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

class Reporting(models.Model):
	investigation   = models.ForeignKey('Investigation',blank=False,null=False,related_name='reporting_investigation')
	title           = models.CharField(max_length=1000,blank=True,null=True)
	notes           = models.CharField(max_length=5000,blank=True,null=True)

	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return str(self.investigation.id)

	def __str__(self):
		return str(self.investigation.id)

class ReportingMedia(models.Model):
	reporting                       = models.ForeignKey('Reporting',blank=False,null=False,related_name='reporting_media')
	media                           = models.FileField(upload_to='reporting/',blank=True,null=True)
	
	is_active          		        = models.BooleanField(null=False,blank=True,default=True)
	created            		        = models.DateTimeField(auto_now_add=True)
	updated           		        = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.reporting.investigation.id)

	def __str__(self):
		return str(self.reporting.investigation.id)


class PaybackDiscount(models.Model):
	investigation   = models.ForeignKey('Investigation',blank=False,null=False,related_name='paybackdiscount_investigation')
	total_cost      = models.FloatField(blank=True,null=True)
	
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return str(self.investigation.id)

	def __str__(self):
		return str(self.investigation.id)

class PaybackDiscountDetails(models.Model):
	paybackdiscount = models.ForeignKey('PaybackDiscount',blank=False,null=False,related_name='paybackdiscount_details')
	category        = models.CharField(max_length=100,blank=True,null=True,choices=INVESTIGATION_CATEGORY_CHOICES)
	name            = models.CharField(max_length=1000,blank=True,null=True)
	cost            = models.FloatField(blank=True,null=True)
	
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return str(self.paybackdiscount.investigation.id)

	def __str__(self):
		return str(self.paybackdiscount.investigation.id)

class PaybackDiscountDetailsMedia(models.Model):
	paybackdiscount 	    		= models.ForeignKey('PaybackDiscount',blank=False,null=False,related_name='paybackdiscount_media')
	media                           = models.FileField(upload_to='paybackdiscount/',blank=True,null=True)
	
	is_active          		        = models.BooleanField(null=False,blank=True,default=True)
	created            		        = models.DateTimeField(auto_now_add=True)
	updated           		        = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.paybackdiscount.investigation.id)

	def __str__(self):
		return str(self.paybackdiscount.investigation.id)

class BuybackPromocodeGift(models.Model):
	investigation   				= models.ForeignKey('Investigation',blank=False,null=False,related_name='buybackpromocodegift_investigation')
	total_cost      				= models.FloatField(blank=True,null=True)
	
	is_active          		        = models.BooleanField(null=False,blank=True,default=True)
	created            		        = models.DateTimeField(auto_now_add=True)
	updated           		        = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.investigation.id)

	def __str__(self):
		return str(self.investigation.id)

class BuybackPromocodeGiftDetails(models.Model):
	buybackpromocodegift 			= models.ForeignKey('BuybackPromocodeGift',blank=False,null=False,related_name='buybackpromocodegiftdetails')
	category        	 			= models.CharField(max_length=100,blank=True,null=True,choices=INVESTIGATION_CATEGORY_CHOICES)
	name            	 			= models.CharField(max_length=1000,blank=True,null=True)
	cost       				     	= models.FloatField(blank=True,null=True)
	
	is_active          		        = models.BooleanField(null=False,blank=True,default=True)
	created            		        = models.DateTimeField(auto_now_add=True)
	updated           		        = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.buybackpromocodegift.investigation.id)

	def __str__(self):
		return str(self.buybackpromocodegift.investigation.id)

class BuybackPromocodeGiftDetailsMedia(models.Model):
	buybackpromocodegift 			= models.ForeignKey('BuybackPromocodeGift',blank=False,null=False,related_name='buybackpromocodegift_media')
	media                           = models.FileField(upload_to='buybackpromocodegift/',blank=True,null=True)
	
	is_active          		        = models.BooleanField(null=False,blank=True,default=True)
	created            		        = models.DateTimeField(auto_now_add=True)
	updated           		        = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.buybackpromocodegift.id)

	def __str__(self):
		return str(self.buybackpromocodegift.id)


#Followup details for followup order.Followup granded by Investigator

class FollowUp(models.Model): 
	ticket_no       = models.CharField(max_length=500,blank=True,null=True)
	investigation   = models.ForeignKey('Investigation',blank=False,null=False,related_name='followup_investigation') 
	instructions    = models.CharField(max_length=500,blank=True,null=True)
	status      	= models.CharField(max_length=100,blank=True,null=True,choices=FOLLOWUP_STATUS)
	no_of_cleaners  = models.IntegerField(blank=True,null=True)
	cleaning_hours  = models.IntegerField(blank=True,null=True)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def save(self,*args, **kwargs):
		last_ticket_no  		 = FollowUp.objects.filter(is_active=True).aggregate(t=Max('ticket_no'))['t']
		current_ticket_starting = str(timezone.now().year)		
		if last_ticket_no:
			if current_ticket_starting == last_ticket_no[0:4]:
				new_ticket_no 		 = str(int(last_ticket_no[4:]) + 1 )
				new_ticket_no 		 = last_ticket_no[0:-(len(new_ticket_no))]+new_ticket_no
			else:
				new_ticket_no 		 = str(timezone.now().year)+'00001'
		else:
			new_ticket_no 		 = str(timezone.now().year)+'00001'

		if not self.ticket_no:
			self.ticket_no = new_ticket_no

		super(FollowUp, self).save(*args, **kwargs)
	
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

class FollowUpSection(models.Model):
	follow_up 			= models.ForeignKey('FollowUp',blank=False,null=False,related_name='follow_up_of_section')
	section_name 		= models.CharField(max_length=100,blank=False,null=False)
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

	section_cost     = models.FloatField(blank=True,null=True)
	section_cleanings= models.FloatField(blank=True,null=True)
	section_net_cost = models.FloatField(blank=True,null=True)

	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		for field_name in ['size','wall_type','ceiling_type','floor_type','material','colour','cause_of_stain']:
			val = getattr(self, field_name, False)
			if val:
				setattr(self, field_name, val.title())
		super(FollowUpSection, self).save(*args, **kwargs)

	def __unicode__(self):
		return str(self.follow_up)

	def __str__(self):
		return str(self.follow_up)	


class FollowUpSectionKeynote(models.Model):
	followup_section = models.ForeignKey('FollowUpSection',blank=False,null=False,related_name='keynotesectionsfollowup')
	sub_area 		   = models.CharField(max_length=100,blank=True,null=True)
	quantity 		   = models.CharField(max_length=100,blank=True,null=True)
	completion_status  = models.BooleanField(null=False,blank=True,default=False)

	is_active            = models.BooleanField(null=False,blank=True,default=True)
	created              = models.DateTimeField(auto_now_add=True)
	updated              = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.followup_section)

	def __str__(self):
		return str(self.followup_section)

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

class Promocode(models.Model):
	promocode 				= models.CharField(max_length=500,blank=False,null=False)
	promocode_type          = models.CharField(max_length=500,blank=True,null=True,choices=PROMOCODE_TYPE_CHOICES)
	percentage              = models.FloatField(blank=True,null=True)
	price 					= models.FloatField(blank=True,null=True)
	percentage_upto_price   = models.FloatField(blank=True,null=True)
	starting_date			= models.DateField(blank=True,null=True)
	expiry_date  			= models.DateField(blank=True,null=True)
	total_usage  			= models.IntegerField(blank=True,null=True)
	total_used   			= models.IntegerField(blank=True,null=True,default=0)

	is_active          	= models.BooleanField(null=False,blank=True,default=True)
	created            	= models.DateTimeField(auto_now_add=True)
	updated            	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.promocode)

	def __str__(self):
		return self.promocode