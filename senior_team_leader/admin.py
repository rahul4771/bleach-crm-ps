from django.contrib import admin
from senior_team_leader.models import CleaningTeam,CleaningTeamMedia,CleaningTeamTask,CleaningTeamMember,FollowUpTeam,FollowUpTeamTask,FollowUpTeamMedia,FollowUpTeamMember

# Register your models here.
class CleaningTeamMediaInline(admin.TabularInline):
	model   = CleaningTeamMedia
	extra	= 1

class CleaningTeamAdmin(admin.ModelAdmin):
	inlines = (CleaningTeamMediaInline,)

class CleaningTeamMediaAdmin(admin.ModelAdmin):
	radio_fields = {"media_type":admin.HORIZONTAL,"taken_status":admin.HORIZONTAL}

admin.site.register(CleaningTeam,CleaningTeamAdmin)
admin.site.register(CleaningTeamMedia,CleaningTeamMediaAdmin)

admin.site.register(CleaningTeamTask)
admin.site.register(CleaningTeamMember)

class FollowUpTeamMediaInline(admin.TabularInline):
	model   = FollowUpTeamMedia
	extra	= 1

class FollowUpTeamAdmin(admin.ModelAdmin):
	inlines = (FollowUpTeamMediaInline,)

class FollowUpTeamMediaAdmin(admin.ModelAdmin):
	radio_fields = {"media_type":admin.HORIZONTAL,"taken_status":admin.HORIZONTAL}

admin.site.register(FollowUpTeam,FollowUpTeamAdmin)
admin.site.register(FollowUpTeamMedia,FollowUpTeamMediaAdmin)

admin.site.register(FollowUpTeamTask)
admin.site.register(FollowUpTeamMember)