from django.db import models
from user.models import UserProfile
from order.models import Order
# Create your models here.

PAYMENT_MODE_CHOICES = (
	('CASH','CASH'),
	('CHECK','CHECK'),
	('OTHER','OTHER')
	)


#Invoice Details of Each Order

class Invoice(models.Model):
	invoice_number               = models.CharField(max_length=30,blank=False,null=False)
	order 		                 = models.ForeignKey(Order,blank=False,null=False,related_name='invoice_order')
	total_amount                 = models.IntegerField(blank=True,null=True)
	amount_paid                  = models.IntegerField(blank=True,null=True)
	is_subscription              = models.BooleanField(blank=True,null=False)
	subscription_start           = models.DateTimeField(blank=True,null=True)
	subscription_gap             = models.IntegerField(blank=True,null=True)
	subscription_end             = models.DateTimeField(blank=True,null=True)
	no_of_cleanings              = models.IntegerField(blank=True,null=True)
	no_of_cleaning_completed     = models.IntegerField(blank=True,null=True)
	no_of_down_payments          = models.IntegerField(blank=True,null=True)
	no_of_down_payments_complete = models.IntegerField(blank=True,null=True)
	down_payment_deadend         = models.DateTimeField(blank=True,null=True)
	is_active      				 = models.BooleanField(null=False,blank=True,default=True)
	created       			     = models.DateTimeField(auto_now_add=True)
	updated    				     = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.invoice_number)

	def __str__(self):
		return self.invoice_number

#Payment History of Customers...There may be multiple payment history for single order(in case of subscription,down payment)

class PaymentHistory(models.Model):
	invoice 					 = models.ForeignKey(Invoice,blank=False,null=False,related_name='payment_history_invoice')
	amount_paid 				 = models.FloatField(blank=True,null=True)
	payment_mode 				 = models.CharField(max_length=100,blank=True,null=True,choices=PAYMENT_MODE_CHOICES)
	received_by 				 = models.ForeignKey(UserProfile,blank=False,null=False,related_name='payment_history_received_by')
	paid_date 					 = models.DateTimeField(blank=True,null=True)
	check_no            		 = models.CharField(max_length=100,blank=True,null=True)
	check_date 					 = models.CharField(max_length=100,blank=True,null=True)
	bank_name 					 = models.CharField(max_length=100,blank=True,null=True)
	is_active      				 = models.BooleanField(null=False,blank=True,default=True)
	created       			     = models.DateTimeField(auto_now_add=True)
	updated    				     = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.invoice.invoice_number)

	def __str__(self):
		return self.invoice.invoice_number