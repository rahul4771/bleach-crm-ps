from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin

from user.models import UserProfile,Governorate,Area,Address
# Register your models here.



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ("username",)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = UserProfile
        exclude=[]

class CustomUserAdmin(UserAdmin):
 
    fieldsets = (
        (None, {'fields': ('username', 'password','email')}),
        (('Personal info'), {'fields': ('user_type','name','name_arabic','gender','nationality','bleach_mobile_number','company','job_title','mobile_number','location','date_day','date_month','date_year','phone_number','sms_preference','is_sms','customer_id','profile_image')}),

        (('Permissions'), {'fields': ('is_active', 'is_staff','is_superuser',
                                       'groups', 'user_permissions')}),
        (('dates'), {'fields': ('last_login',  )}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2',)}
        ),
    )

    form      = CustomUserChangeForm 
    add_form  = CustomUserCreationForm


class AreaInline(admin.TabularInline):
    model = Area
    extra = 1

class GovernorateAdmin(admin.ModelAdmin):
    inlines = (AreaInline,)

admin.site.register(UserProfile,CustomUserAdmin)
admin.site.register(Governorate,GovernorateAdmin)
admin.site.register(Area)
admin.site.register(Address)       