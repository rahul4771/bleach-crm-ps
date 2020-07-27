from django.db import models
from user.models import UserProfile
from order.models import OrderScheduler,FollowUpScheduler,Order

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
	order_scheduler = models.ForeignKey(OrderScheduler,blank=True,null=True,related_name='cleaning_team_order_scheduler')
	team_leader 	= models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_team_leader')
	start_at 		= models.DateTimeField(blank=True,null=True)
	end_at 			= models.DateTimeField(blank=True,null=True)
	check_in 		= models.DateTimeField(blank=True,null=True)
	check_out 	    = models.DateTimeField(blank=True,null=True)
	no_of_cleaners  = models.IntegerField(blank=True,null=True)
	drop_off_driver = models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_drop_off')
	pick_up_driver  = models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_pick_up')
	created_by      = models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaningteam_created_by')
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team_leader.name)

	def __str__(self):
		return self.team_leader.name

#For Tracking Medias Uploaded by Team Leader on Site

class CleaningTeamMedia(models.Model):
	team 					 = models.ForeignKey('CleaningTeam',blank=False,null=False,related_name='media_cleaningteam')
	media                    = models.FileField(upload_to='cleaning/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=True,null=True,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=True,null=True,choices=MEDIA_TAKEN_CHOICES)
	is_active          		 = models.BooleanField(null=False,blank=True,default=True)
	created            		 = models.DateTimeField(auto_now_add=True)
	updated           		 = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team.team_leader.name)

	def __str__(self):
		return self.team.team_leader.name

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
		return str(self.cleaning_team.team_leader.name)

	def __str__(self):
		return self.cleaning_team.team_leader.name

#To Save Cleaning Team Members Details

class CleaningTeamMember(models.Model):
	team 			= models.ForeignKey('CleaningTeam',blank=False,null=False,related_name='cleaning_member_team')
	member 			= models.ForeignKey(UserProfile,blank=True,null=True,related_name='cleaning_member_user')
	start_at 		= models.DateTimeField(blank=True,null=True)
	end_at 			= models.DateTimeField(blank=True,null=True)
	
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team)

	def __str__(self):
		return str(self.team)

#Followup team for different Followup Schedules

class FollowUpTeam(models.Model):
	followup_scheduler = models.ForeignKey(FollowUpScheduler,blank=True,null=True,related_name='followupteam_followupschedule')
	team_leader 	   = models.ForeignKey(UserProfile,blank=True,null=True,related_name='followupteam_team_leader')
	name			   = models.CharField(max_length=50,blank=False,null=False)
	start_at 		   = models.DateTimeField(blank=True,null=True)
	end_at 			   = models.DateTimeField(blank=True,null=True)
	check_in 		   = models.DateTimeField(blank=True,null=True)
	check_out 		   = models.DateTimeField(blank=True,null=True)
	drop_off_driver    = models.ForeignKey(UserProfile,blank=True,null=True,related_name='followupteam_drop_off')
	pick_up_driver     = models.ForeignKey(UserProfile,blank=True,null=True,related_name='followupteam_pick_up')
	no_of_cleaners     = models.IntegerField(blank=True,null=True,default=1)
	created_by         = models.ForeignKey(UserProfile,blank=True,null=True,related_name='followupteam_created_by')
	is_active          = models.BooleanField(null=False,blank=True,default=True)
	created            = models.DateTimeField(auto_now_add=True)
	updated            = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team_leader.name)

	def __str__(self):
		return self.team_leader.name

#For Tracking Medias Uploaded by Followup Team Leader on Site

class FollowUpTeamMedia(models.Model):
	team 					 = models.ForeignKey('FollowUpTeam',blank=False,null=False)
	media                    = models.FileField(upload_to='followup/',blank=True,null=True)
	media_type 				 = models.CharField(max_length=20,blank=True,null=True,choices=MEDIA_CHOICES)
	taken_status 			 = models.CharField(max_length=20,blank=True,null=True,choices=MEDIA_TAKEN_CHOICES)
	is_active          		 = models.BooleanField(null=False,blank=True,default=True)
	created            		 = models.DateTimeField(auto_now_add=True)
	updated           		 = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team.team_leader.name)

	def __str__(self):
		return self.team.team_leader.name

#Tasks assigned to Followup Team

class FollowUpTeamTask(models.Model):
	followup_team 			 = models.ForeignKey('FollowUpTeam',blank=False,null=False)
	discription 			 = models.CharField(max_length=500,blank=True,null=True)
	is_completed     		 = models.BooleanField(null=False,blank=True,default=False)
	start_time 				 = models.DateTimeField(blank=True,null=True)
	end_time                 = models.DateTimeField(blank=True,null=True)
	is_active          		 = models.BooleanField(null=False,blank=True,default=True)
	created            		 = models.DateTimeField(auto_now_add=True)
	updated           		 = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.followup_team.team_leader.name)

	def __str__(self):
		return self.followup_team.team_leader.name


#To Save Followup Team Members Details

class FollowUpTeamMember(models.Model):
	team 			= models.ForeignKey('FollowUpTeam',blank=False,null=False,related_name='followup_member_team')
	member 			= models.ForeignKey(UserProfile,blank=True,null=True,related_name='followup_member')
	start_at 		= models.DateTimeField(blank=True,null=True)
	end_at 			= models.DateTimeField(blank=True,null=True)
	is_active       = models.BooleanField(null=False,blank=True,default=True)
	created         = models.DateTimeField(auto_now_add=True)
	updated         = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.team.team_leader.name)

	def __str__(self):
		return str(self.team.team_leader.name)		
