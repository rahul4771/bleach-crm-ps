from django.db import models
from evaluator.models import Evaluation
# Create your models here.

BOOKING_CHOICES=(
	('EVALUATIONBOOKING','EVALUATIONBOOKING'),
	('CLEANINGBOOKING','CLEANINGBOOKING')
	)

class CustomerBooking(models.Model):
	booking_id   = models.CharField(max_length=100,blank=False,null=False)
	booking_type = models.CharField(max_length=100,blank=False,null=False,choices=BOOKING_CHOICES)
	booking_date = models.DateTimeField(auto_now=True)
	evaluation   = models.ForeignKey(Evaluation,blank=False,null=False,related_name='booking_evaluation',on_delete=models.CASCADE)
	is_bookingcompleted       = models.BooleanField(null=False,blank=True,default=False)

	is_active    = models.BooleanField(null=False,blank=True,default=True)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.booking_id)

	def __str__(self):
		return self.booking_id
