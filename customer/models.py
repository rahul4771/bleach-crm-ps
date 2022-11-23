from django.db import models
from evaluator.models import Evaluation,ServiceType
from user.models import UserProfile,Address
from bleachadmin.models import ServicePriceRange
# Create your models here.

BOOKING_CHOICES=(
	('EVALUATIONBOOKING','EVALUATIONBOOKING'),
	('CLEANINGBOOKING','CLEANINGBOOKING')
	)

CLEANING_CHOICES=(
	('ONE TIME SERVICE','ONE_TIME_SERVICE'),
	('SUBSCRIPTION','SUBSCRIPTION'),
	)

SERVICEDIVISION_CHOICES = (('SOFA','SOFA'),
					 ('CHAIR','CHAIR'),
					 ('CURTAIN','CURTAIN'))

class CustomerBooking(models.Model):
	booking_id   = models.CharField(max_length=100,blank=False,null=False)
	booking_type = models.CharField(max_length=100,blank=False,null=False,choices=BOOKING_CHOICES)
	booking_date = models.DateTimeField(auto_now=True)
	evaluation   = models.ForeignKey(Evaluation,blank=False,null=False,related_name='booking_evaluation',on_delete=models.CASCADE)
	is_bookingcompleted       = models.BooleanField(null=False,blank=True,default=False)
	is_assistance_needed      = models.BooleanField(null=False,blank=True,default=False)

	is_active    = models.BooleanField(null=False,blank=True,default=True)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.booking_id)

	def __str__(self):
		return self.booking_id

class NewCustomerOtp(models.Model):
	mobile_number= models.CharField(max_length=10,blank=True,null=True) 
	customer_otp = models.CharField(max_length=100,blank=True,null=True)

	is_active    = models.BooleanField(null=False,blank=True,default=True)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.mobile_number)

	def __str__(self):
		return self.mobile_number

class CustomerCart(models.Model):
	customer 			= models.ForeignKey(UserProfile,blank=False,null=False,on_delete=models.CASCADE,related_name='cart_customer')
	cart_id_value		= models.CharField(max_length=10,blank=False,null=False)
	customer_address	= models.ForeignKey(Address,blank=True,null=True)
	total_cost  		= models.CharField(max_length=10,default=0,blank=False,null=False)
	is_scheduled		= models.BooleanField(default=False)
	no_of_visits		= models.IntegerField(default=0,null=False,blank=False)
	

	is_active    		= models.BooleanField(null=False,blank=True,default=True)
	created      		= models.DateTimeField(auto_now_add=True)
	updated      		= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.customer.name)

	def __str__(self):
		return self.customer.name

class CartService(models.Model):
	cart				= models.ForeignKey('CustomerCart',blank=False,null=False,on_delete=models.CASCADE,related_name='cart_service')
	service_type		= models.ForeignKey(ServiceType,blank=True,null=True,related_name='cart_service_type')
	service_price_range = models.ForeignKey(ServicePriceRange,blank=True,null=True,related_name='cart_service_price_range')
	cleaning_policy		= models.CharField(max_length=20,blank=True,null=True,choices=CLEANING_CHOICES)
	area_type	 		= models.CharField(max_length=100,blank=True,null=True)
	cleaning_method 	= models.CharField(max_length=100,blank=True,null=True)
	location_type		= models.CharField(max_length=100,blank=True,null=True)

	section_name 		= models.CharField(max_length=100,blank=False,null=False)
	category			= models.CharField(max_length=100,blank=True,null=True)
	dirt_level			= models.CharField(max_length=100,blank=True,null=True)

	quantity    		= models.CharField(max_length=100,blank=True,null=True)
	size        		= models.CharField(max_length=100,blank=True,null=True)
	unit        		= models.CharField(max_length=100,blank=True,null=True)
	age         		= models.CharField(max_length=100,blank=True,null=True)
	
	floor       		= models.CharField(max_length=100,blank=True,null=True)
	apartment   		= models.CharField(max_length=100,blank=True,null=True)
	room        		= models.CharField(max_length=100,blank=True,null=True)
	
	wall_type   		= models.CharField(max_length=100,blank=True,null=True)
	ceiling_type		= models.CharField(max_length=100,blank=True,null=True)
	floor_type  		= models.CharField(max_length=100,blank=True,null=True)
	material    		= models.CharField(max_length=100,blank=True,null=True)
	colour      		= models.CharField(max_length=100,blank=True,null=True)
	cause_of_stain		= models.CharField(max_length=100,blank=True,null=True)
	age_of_stain		= models.CharField(max_length=100,blank=True,null=True)

	cement_residue      = models.BooleanField(null=False,blank=True,default=False)
	oil_residue         = models.BooleanField(null=False,blank=True,default=False)
	hall_size           = models.CharField(max_length=100,blank=True,null=True)
	window_side         = models.CharField(max_length=100,blank=True,null=True)
	new_kitchen         = models.BooleanField(null=False,blank=True,default=False)
	is_cabinet          = models.BooleanField(null=False,blank=True,default=False)
	is_highprice_facade = models.BooleanField(null=False,blank=True,default=False)
	is_highprice_window = models.BooleanField(null=False,blank=True,default=False)
	upholstery_type     = models.CharField(max_length=50,blank=True,null=True,choices=SERVICEDIVISION_CHOICES)
	vacuuming        	= models.BooleanField(null=False,blank=True,default=False)

	addon_name          = models.CharField(max_length=100,blank=True,null=True)
	addon_category      = models.CharField(max_length=100,blank=True,null=True)
	addon_size          = models.CharField(max_length=100,blank=True,null=True)
	addon_price         = models.FloatField(blank=True,null=True)
	addon_productivity  = models.FloatField(blank=True,null=True)

	total_cost          = models.FloatField(blank=True,null=True,default=0)

	is_active    		= models.BooleanField(null=False,blank=True,default=True)
	created      		= models.DateTimeField(auto_now_add=True)
	updated      		= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		if self.service_type:
			return str(self.cart.customer.name+'-'+self.service_type.name)
		else:
			return str(self.cart.customer.name)

	def __str__(self):
		if self.service_type:
			return self.cart.customer.name+'-'+self.service_type.name
		else:
			return self.cart.customer.name

class CartServiceFloor(models.Model):
	cartService			= models.ForeignKey('CartService',blank=False,null=False,on_delete=models.CASCADE,related_name='cart_service_floor')
	section_name 		= models.CharField(max_length=100,blank=False,null=False)
	size        		= models.CharField(max_length=100,blank=True,null=True)
	unit        		= models.CharField(max_length=100,blank=True,null=True)
	service_price_range = models.ForeignKey(ServicePriceRange,blank=True,null=True,related_name='cart_service_floor_price_range')
	
	bathrooms       	= models.CharField(max_length=100,blank=True,null=True)
	windows   			= models.CharField(max_length=100,blank=True,null=True)
	rooms        		= models.CharField(max_length=100,blank=True,null=True)
	
	wall_type   		= models.CharField(max_length=100,blank=True,null=True)
	ceiling_type		= models.CharField(max_length=100,blank=True,null=True)
	floor_type  		= models.CharField(max_length=100,blank=True,null=True)
	section_cost        = models.FloatField(blank=True,null=True,default=0)
	
	def __unicode__(self):
		if self.cartService.service_type:
			return str(self.cartService.cart.customer.name+'-'+self.cartService.service_type.name)
		else:
			return str(self.cartService.cart.customer.name)

	def __str__(self):
		if self.cartService.service_type:
			return self.cartService.cart.customer.name+'-'+self.cartService.service_type.name
		else:
			return self.cartService.cart.customer.name

class CartSchedule(models.Model):
	cart					= models.ForeignKey('CustomerCart',blank=False,null=False,on_delete=models.CASCADE,related_name='cart_schedule')
	start_at		   	 	= models.DateTimeField(blank=True,null=True)
	end_at			   	 	= models.DateTimeField(blank=True,null=True)

	no_of_cleaners       	= models.IntegerField(null=True,blank=True)
	cleaning_hours       	= models.FloatField(null=True,blank=True)
	hourly_cleaning_duration= models.FloatField(null=True,blank=True)

	is_active    			= models.BooleanField(null=False,blank=True,default=True)
	created      			= models.DateTimeField(auto_now_add=True)
	updated      			= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.cart.customer.name+'-'+self.start_at)

	def __str__(self):
		return self.cart.customer.name+'-'+str(self.start_at)

class SubscriptionMail(models.Model):
	customer_email     = models.EmailField(max_length=254,null=False,blank=False)
	subscription_date  = models.DateField(auto_now=False, auto_now_add=True)
	
	def __unicode__(self):
		return str(self.customer_email)

	def __str__(self):
		return str(self.customer_email)