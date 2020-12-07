from django.db import models
from order.models import Order,PaymentSubscriptionDetails
from user.models import UserProfile

# Create your models here.

PAYMENT_MODE_CHOICES = (
	('CASH','CASH'),
	('CHEQUE','CHEQUE'),
	('BANK','BANK'),
	('ONLINECREDIT','ONLINECREDIT'),
	)

PAYMENT_GATEWAY_CHOICES = (
	('CREDITCARD','CREDITCARD'),
	('DEBITCARD','DEBITCARD'),
	)

#Payment History of Customers...There may be multiple payment history for single order(in case of subscription,down payment)
class PaymentHistory(models.Model):
	order 						 = models.ForeignKey(Order,blank=False,null=False,related_name='history_order')
	receipt_no                   = models.IntegerField(blank=True,null=True)
	amount_paid 				 = models.FloatField(blank=True,null=True)
	payment_mode 				 = models.CharField(max_length=100,blank=True,null=True,choices=PAYMENT_MODE_CHOICES)
	received_by 				 = models.ForeignKey(UserProfile,blank=True,null=True,related_name='payment_history_received_by')
	paid_date 					 = models.DateTimeField(blank=True,null=True)
	history_payment_subscription = models.ForeignKey(PaymentSubscriptionDetails,blank=True,null=True,related_name='historypaymentsubscription')

	check_no            		 = models.CharField(max_length=100,blank=True,null=True)
	check_date 					 = models.DateField(blank=True,null=True)
	
	bank_name 					 = models.CharField(max_length=100,blank=True,null=True)
	bank_no                      = models.CharField(max_length=100,blank=True,null=True)

	payment_id                   = models.CharField(max_length=100,blank=True,null=True)
	ref                          = models.CharField(max_length=100,blank=True,null=True)
	business_logic_post_date     = models.CharField(max_length=100,blank=True,null=True)
	track_id                     = models.CharField(max_length=100,blank=True,null=True)
	transaction_id               = models.CharField(max_length=100,blank=True,null=True)
	payment_gateway              = models.CharField(max_length=100,blank=True,null=True,choices=PAYMENT_GATEWAY_CHOICES)

	is_active      				 = models.BooleanField(null=False,blank=True,default=True)
	created       			     = models.DateTimeField(auto_now_add=True)
	updated    				     = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order.id)

	def __str__(self):
		return str(self.order.order_no)
