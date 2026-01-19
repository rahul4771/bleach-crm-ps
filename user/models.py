from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django_countries.fields import CountryField
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

# Create your models here.

USER_TYPE_CHOICES=( 
    ('ADMIN','ADMIN'), 
    ('AGENT','AGENT'),
    ('EVALUATOR','EVALUATOR'),
    ('SENIORTEAMLEADER','SENIORTEAMLEADER'),
    ('TEAMINCHARGE','TEAMINCHARGE'),
    ('CLEANER','CLEANER'),
    ('CUSTOMER','CUSTOMER'),
    ('DRIVER','DRIVER'),
    ('ACCOUNTANT','ACCOUNTANT'),
    ('QUALITYCONTROLL','QUALITYCONTROLL'),
    ('SALESADMIN','SALESADMIN'),
    ('OPERATIONSUPERVISOR','OPERATIONSUPERVISOR'),
    ('TECHNICALSUPERVISOR','TECHNICALSUPERVISOR'),
    ('BOOKINGOFFICER','BOOKINGOFFICER'),
    ('INVENTORYADMIN','INVENTORYADMIN'),
    ('INVENTORYUSER','INVENTORYUSER'),
    ('STOCKCONTROLLER','STOCKCONTROLLER'),
    ('PURCHASINGOFFICER','PURCHASINGOFFICER'),
    ('INVUSER','INVUSER')
)


GENDER_CHOICES=(
	('MALE','MALE'),
	('FEMALE','FEMALE'),
    ('OTHERS','OTHERS')
	)

SMS_LANGUAGE_CHOICES = (
    ('ENGLISH','ENGLISH'),
    ('ARABIC','ARABIC')
    )

CUSTOMER_TYPE_CHOICES = (
    ('INDIVIDUAL','INDIVIDUAL'),
    ('RETAIL','RETAIL'),
    ('CORPORATE','CORPORATE')
    )

LEAVE_TYPES = (
    ('ANNUAL LEAVE','ANNUAL_LEAVE'),
    ('WEEKLY OFF','WEEKLY_OFF'),
    ('SICK LEAVE','SICK_LEAVE'),
    ('UNPAID LEAVE','UNPAID_LEAVE'),
    ('COMPASSIONATE LEAVE','COMPASSIONATE_LEAVE'),
    ('ABSENT','ABSENT')
)

SHIFT_CHOICES =(
    ('SHIFT1','SHIFT1'),
    ('SHIFT2','SHIFT2')
)

#profile image Size Validator
def validate_image(image):
    file_size = image.file.size

    limit_mb = 5
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError("Max size of file is %s MB" % limit_mb)

class CustomUserManager(BaseUserManager):
    def _create_user(self, username, password, 
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        now = timezone.now() 
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True,
                                 **extra_fields)


class UserProfile(AbstractUser):
    name			= models.CharField(max_length=100,blank=False,null=False)
    name_arabic     = models.CharField(max_length=100,blank=True,null=True)
    bleach_mobile_number = models.CharField(max_length=10,blank=True,null=True)
    user_type 		= models.CharField(max_length=20,blank=True,null=True,choices=USER_TYPE_CHOICES)
    is_team_leader  = models.BooleanField(null=False,blank=True,default=False)
    is_investigator = models.BooleanField(null=False,blank=True,default=False)
    gender 	  		= models.CharField(max_length=20,blank=True,null=True,choices=GENDER_CHOICES)
    nationality		= CountryField(null=True,blank=True)
    company 		= models.CharField(max_length=100,blank=True,null=True)
    job_title 		= models.CharField(max_length=100,blank=True,null=True)
    mobile_number 	= models.CharField(max_length=10,blank=True,null=True,unique=True)
    phone_number 	= models.CharField(max_length=10,blank=True,null=True)
    profile_image	= models.ImageField(upload_to='profile_photo/',blank=True,null=True,validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png']),validate_image],)
    customer_type   = models.CharField(max_length=20,blank=True,null=True,choices=CUSTOMER_TYPE_CHOICES)

    date_day        = models.CharField(max_length=2,blank=False,null=False)
    date_month      = models.CharField(max_length=2,blank=False,null=False)
    date_year       = models.CharField(max_length=4,blank=True,null=True)
    
    sms_preference  = models.CharField(max_length=20,blank=True,null=True,choices=SMS_LANGUAGE_CHOICES)
    is_whatsapp     = models.BooleanField(null=False,blank=True,default=False)
    is_sms          = models.BooleanField(null=False,blank=True,default=False)
    is_email        = models.BooleanField(null=False,blank=True,default=False)
    customer_id     = models.CharField(max_length=12,blank=True,null=True)
    credit_amount   = models.FloatField(blank=True,null=True,default=0)
    is_credit       = models.BooleanField(null=False,blank=True,default=False)

    is_general_skill       = models.BooleanField(null=False,blank=True,default=False)
    is_deep_skill          = models.BooleanField(null=False,blank=True,default=False)
    is_upholstery_skill    = models.BooleanField(null=False,blank=True,default=False)
    is_kitchen_skill       = models.BooleanField(null=False,blank=True,default=False)
    is_sterilization_skill = models.BooleanField(null=False,blank=True,default=False)
    is_carpet_skill        = models.BooleanField(null=False,blank=True,default=False)
    is_mattress_skill      = models.BooleanField(null=False,blank=True,default=False)
    is_facade_skill        = models.BooleanField(null=False,blank=True,default=False)
    is_storagearea_skill   = models.BooleanField(null=False,blank=True,default=False)
    is_rope_access_skill   = models.BooleanField(null=False,blank=True,default=False)
    is_carparkingumbrella_skill = models.BooleanField(null=False,blank=True,default=False)
    is_outdoor_skill            = models.BooleanField(null=False,blank=True,default=False)
    is_window_skill             = models.BooleanField(null=False,blank=True,default=False)

    universal_shift_start       = models.TimeField(blank=True,null=True)
    universal_shift_end         = models.TimeField(blank=True,null=True)

    is_onlineevaluator          = models.BooleanField(null=False,blank=True,default=True)

    address_otp                 = models.CharField(max_length=100,blank=True,null=True)

    xero_account_id             = models.CharField(max_length=100,blank=True,null=True)

    bamboo_employee_id          = models.CharField(max_length=20,blank=True,null=True)


    created_by      = models.ForeignKey('self', on_delete=models.PROTECT,blank=True,null=True)
    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)

    objects=CustomUserManager()

    def __unicode__(self):
        if self.mobile_number:
            return str(self.mobile_number)
        else:
            return str(self.username)

    def __str__(self):
        if self.mobile_number:
            return self.mobile_number
        else:
            return self.username

class Governorate(models.Model):
    name            = models.CharField(max_length=100,blank=False,null=False)
    name_arabic     = models.CharField(max_length=100,blank=False,null=False)

    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name


class Area(models.Model):        
    name            = models.CharField(max_length=100,blank=False,null=False)
    name_arabic     = models.CharField(max_length=100,blank=False,null=False)
    governorate     = models.ForeignKey('Governorate',on_delete=models.PROTECT,blank=False,null=False)
    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s" % str(self.name)

    def __str__(self):
        return self.name


class Address(models.Model):
    customer        = models.ForeignKey('UserProfile',on_delete=models.PROTECT,blank=False,null=False,related_name='address_customer')
    governorate     = models.ForeignKey('Governorate',on_delete=models.PROTECT,blank=False,null=False)
    area            = models.ForeignKey('Area',on_delete=models.PROTECT,blank=False,null=False)
    location        = models.CharField(max_length=100,blank=False,null=False)
    gps_location    = models.TextField(max_length=500,blank=True,null=True)
    block           = models.CharField(max_length=100,blank=False,null=False)
    avenue          = models.CharField(max_length=100,blank=True,null=True)
    building        = models.CharField(max_length=100,blank=False,null=False)
    street          = models.CharField(max_length=100,blank=False,null=False)
    floor           = models.CharField(max_length=100,blank=True,null=True)
    apartment       = models.CharField(max_length=100,blank=False,null=False)
    currently_active= models.BooleanField(null=False,blank=True,default=True)
    
    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        for field_name in ['block','avenue','building','street','floor','apartment']:
            val = getattr(self, field_name, False)
            if val:
                setattr(self, field_name, val.title())
        super(Address, self).save(*args, **kwargs)

    def __unicode__(self):
        
        try:
            return_string = str(self.customer.customer_id+'-'+self.area.name+'-'+self.customer.name)
        except:
            return_string = str(self.area.name+'-'+self.customer.name)
        
        return return_string

    def __str__(self):
        try:
            return_string = str(self.customer.customer_id+'-'+self.area.name+'-'+self.customer.name)
        except:
            return_string = str(self.area.name+'-'+self.customer.name)
        
        return return_string    

class LeaveSchedule(models.Model):
    staff           = models.ForeignKey('UserProfile',on_delete=models.PROTECT,blank=False,null=False,related_name='leave_staff')
    leave_date      = models.DateField(blank=False,null=False)
    leave_type      = models.CharField(max_length=50,blank=False,null=False,choices=LEAVE_TYPES)
    bamboo_leave_id = models.CharField(max_length=10,blank=True,null=True)
    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
    	return str(self.staff.username+self.leave_date)

    def __str__(self):
    	return self.staff.username+str(self.leave_date)

class ShiftSchedule(models.Model):
    staff           = models.ForeignKey('UserProfile',on_delete=models.PROTECT,blank=False,null=False,related_name='shift_staff')
    
    shift_date      = models.DateField(blank=False,null=False)
    
    shift1          = models.BooleanField(null=False,blank=True,default=False)
    shift2          = models.BooleanField(null=False,blank=True,default=False)
    shift3          = models.BooleanField(null=False,blank=True,default=False)
    
    shift1_start_at = models.TimeField(blank=True,null=True)
    shift1_end_at   = models.TimeField(blank=True,null=True)
    shift2_start_at = models.TimeField(blank=True,null=True)
    shift2_end_at   = models.TimeField(blank=True,null=True)
    shift3_start_at = models.DateTimeField(blank=True,null=True)
    shift3_end_at   = models.DateTimeField(blank=True,null=True)

    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.staff.name)

    def __str__(self):
        return self.staff.name

class Shift(models.Model):
    shift    = models.CharField(max_length=20,blank=True,null=True,choices=SHIFT_CHOICES)
    start_at = models.TimeField(blank=True,null=True)
    end_at   = models.TimeField(blank=True,null=True)

    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.shift)

    def __str__(self):
        return self.shift

class CustomerOTP(models.Model):
    mobile_number 	= models.CharField(max_length=10,blank=True,null=True,unique=True)
    otp             = models.CharField(max_length=10,blank=True,null=True)

    def __unicode__(self):
        return str(self.mobile_number)

    def __str__(self):
        return self.mobile_number