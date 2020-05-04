from django.db import models
from user.models import UserProfile
from order.models import OrderScheduler,FollowUpScheduler

MEDIA_TAKEN_CHOICES = (
	('BEFORE_CLEANING','BEFORE_CLEANING'),
	('AFTER_CLEANING','AFTER_CLEANING')
	)

MEDIA_CHOICES = (
	('PHOTO','PHOTO'),
	('VIDEO','VIDEO'),
	('AUDIO','AUDIO') 
	)

#Cleaning team for different Order Schedules

class CleaningTeam(models.Model):
	order_scheduler = models.ForeignKey(OrderScheduler,blank=True,null=True)
	team_leader 	= models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_team_leader')
	name			= models.CharField(max_length=50,blank=True,null=True)
	start_at 		= models.DateTimeField(blank=True,null=True)
	end_at 			= models.DateTimeField(blank=True,null=True)
	drop_off_driver = models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_drop_off')
	pick_up_driver  = models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_pick_up')
	created_by      = models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_created_by')
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.order_scheduler.order)

	def __str__(self):
		return self.order_scheduler.order

#For Tracking Medias Uploaded by Team Leader on Site

class CleaningTeamMedia(models.Model):
	team 					 = models.ForeignKey('CleaningTeam',blank=False,null=False)
	media                    = models.FileField(upload_to='cleaning/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_TAKEN_CHOICES)
	is_active          		 = models.BooleanField(null=False,blank=True,default=True)
	created            		 = models.DateTimeField(auto_now_add=True)
	updated           		 = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team.name)

	def __str__(self):
		return self.team.name

#Tasks assigned to Cleaning Team

class CleaningTeamTask(models.Model):
	cleaning_team 			 = models.ForeignKey('CleaningTeam',blank=False,null=False)
	discription 			 = models.CharField(max_length=500,blank=True,null=True)
	is_completed     		 = models.BooleanField(null=False,blank=True,default=False)
	start_time 				 = models.DateTimeField(blank=True,null=True)
	end_time                 = models.DateTimeField(blank=True,null=True)
	is_active          = models.BooleanField(null=False,blank=True,default=True)
	created            = models.DateTimeField(auto_now_add=True)
	updated            = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.cleaning_team.name)

	def __str__(self):
		return self.cleaning_team.name

#To Save Cleaning Team Members Details

class CleaningTeamMember(models.Model):
	team 			= models.ForeignKey('CleaningTeam',blank=False,null=False)
	member 			= models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaning_member')
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team.order_scheduler.order)

	def __str__(self):
		return self.team.order_scheduler.order

#Followup team for different Followup Schedules

class FollowUpTeam(models.Model):
	followup_scheduler = models.ForeignKey(FollowUpScheduler,blank=True,null=True)
	team_leader 	   = models.ForeignKey(UserProfile,blank=True,null=True,related_name='followupteam_team_leader')
	name			   = models.CharField(max_length=50,blank=True,null=True)
	start_at 		   = models.DateTimeField(blank=True,null=True)
	end_at 			   = models.DateTimeField(blank=True,null=True)
	created_by         = models.ForeignKey(UserProfile,blank=True,null=True,related_name='followupteam_created_by')
	is_active          = models.BooleanField(null=False,blank=True,default=True)
	created            = models.DateTimeField(auto_now_add=True)
	updated            = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.followup_scheduler.follow_up.order)

	def __str__(self):
		return self.followup_scheduler.follow_up.order

#For Tracking Medias Uploaded by Followup Team Leader on Site

class FollowUpTeamMedia(models.Model):
	team 					 = models.ForeignKey('FollowUpTeam',blank=False,null=False)
	media                    = models.FileField(upload_to='followuo/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=False,null=False,choices=MEDIA_TAKEN_CHOICES)
	is_active          		 = models.BooleanField(null=False,blank=True,default=True)
	created            		 = models.DateTimeField(auto_now_add=True)
	updated           		 = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team.name)

	def __str__(self):
		return self.team.name

#Tasks assigned to Followup Team

class FollowUpTeamTask(models.Model):
	followup_team 			 = models.ForeignKey('FollowUpTeam',blank=False,null=False)
	discription 			 = models.CharField(max_length=500,blank=True,null=True)
	is_completed     		 = models.BooleanField(null=False,blank=True,default=False)
	start_time 				 = models.DateTimeField(blank=True,null=True)
	end_time                 = models.DateTimeField(blank=True,null=True)
	is_active          = models.BooleanField(null=False,blank=True,default=True)
	created            = models.DateTimeField(auto_now_add=True)
	updated            = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.followup_team.name)

	def __str__(self):
		return self.followup_team.name


#To Save Followup Team Members Details

class FollowUpTeamMember(models.Model):
	team 			= models.ForeignKey('FollowUpTeam',blank=False,null=False)
	member 			= models.ForeignKey(UserProfile,blank=True,null=True,related_name='followup_member')
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team.followup_scheduler.follow_up.order)

	def __str__(self):
		return self.team.followup_scheduler.follow_up.order		