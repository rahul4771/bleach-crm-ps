from django.db import models
from user.models import UserProfile
from order.models import Order
# Create your models here.

PAYMENT_MODE_CHOICES = (
	('CASH','CASH'),
	('CHECK','CHECK'),
	('OTHER','OTHER'),
	)

#Payment History of Customers...There may be multiple payment history for single order(in case of subscription,down payment)

class PaymentHistory(models.Model):
	order 						 = models.ForeignKey(Order,blank=False,null=False,related_name='history_order')
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
		return str(self.order.id)

	def __str__(self):
		return self.order.id