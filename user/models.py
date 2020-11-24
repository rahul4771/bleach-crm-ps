from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django_countries.fields import CountryField
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.

USER_TYPE_CHOICES=( 
    ('ADMIN','ADMIN'), 
    ('AGENT','AGENT'),
    ('EVALUATOR','EVALUATOR'),
    ('SENIORTEAMLEADER','SENIORTEAMLEADER'),
    ('TEAMLEADER','TEAMLEADER'),
    ('CLEANER','CLEANER'),
    ('CUSTOMER','CUSTOMER'),
    ('DRIVER','DRIVER'),
    ('ACCOUNTANT','ACCOUNTANT'),
)


GENDER_CHOICES=(
	('MALE','MALE'),
	('FEMALE','FEMALE')
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
    bleach_mobile_number = models.CharField(max_length=10,blank=True,null=True)
    user_type 		= models.CharField(max_length=20,blank=True,null=True,choices=USER_TYPE_CHOICES)
    gender 	  		= models.CharField(max_length=20,blank=True,null=True,choices=GENDER_CHOICES)
    nationality		= CountryField(null=True,blank=True)
    company 		= models.CharField(max_length=100,blank=True,null=True)
    job_title 		= models.CharField(max_length=100,blank=True,null=True)
    mobile_number 	= models.CharField(max_length=10,blank=True,null=True,unique=True)
    phone_number 	= models.CharField(max_length=10,blank=True,null=True)
    profile_image	= models.ImageField(upload_to='profile_photo/',blank=True,null=True,validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png']),validate_image],)
    customer_type   = models.CharField(max_length=20,blank=True,null=True,choices=CUSTOMER_TYPE_CHOICES)
    civil_id_number = models.CharField(max_length=100,blank=True,null=True)
    
    sms_preference  = models.CharField(max_length=20,blank=True,null=True,choices=SMS_LANGUAGE_CHOICES)
    is_whatsapp     = models.BooleanField(null=False,blank=True,default=False)
    is_sms          = models.BooleanField(null=False,blank=True,default=False)
    is_email        = models.BooleanField(null=False,blank=True,default=False)

    created_by      = models.ForeignKey('self',blank=True,null=True)
    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)

    objects=CustomUserManager()


    def __unicode__(self):
    	return str(self.username)

    def __str__(self):
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
    governorate     = models.ForeignKey('Governorate',blank=False,null=False)
    is_active       = models.BooleanField(null=False,blank=True,default=True)
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s" % str(self.name)

    def __str__(self):
        return self.name


class Address(models.Model):
    customer        = models.ForeignKey('UserProfile',blank=False,null=False,related_name='address_customer')
    governorate     = models.ForeignKey('Governorate',blank=False,null=False)
    area            = models.ForeignKey('Area',blank=False,null=False)
    block           = models.CharField(max_length=100,blank=True,null=True)
    avenue          = models.CharField(max_length=100,blank=True,null=True)
    building        = models.CharField(max_length=100,blank=True,null=True)
    street          = models.CharField(max_length=100,blank=True,null=True)
    floor           = models.CharField(max_length=100,blank=True,null=True)
    apartment       = models.CharField(max_length=100,blank=True,null=True)
    currently_active= models.BooleanField(null=False,blank=True)
    
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
        return str(self.area.name)

    def __str__(self):
        return self.area.name    