from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin

from user.models import UserProfile,Governorate,Area,Address,LeaveSchedule,ShiftSchedule,Shift,CustomerOTP
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
        (('Personal info'), {'fields': ('user_type','is_team_leader','is_investigator','name','name_arabic','gender','nationality','bleach_mobile_number','company','job_title','mobile_number','date_day','date_month','date_year','phone_number','sms_preference','is_sms','is_email','is_whatsapp','customer_id','bamboo_employee_id','profile_image','credit_amount','is_general_skill','is_deep_skill','is_upholstery_skill','is_kitchen_skill','is_sterilization_skill','is_carpet_skill','is_mattress_skill','is_facade_skill','is_storagearea_skill','is_carparkingumbrella_skill','is_outdoor_skill','is_window_skill','address_otp','universal_shift_start','universal_shift_end','is_onlineevaluator','is_credit','xero_account_id')}),

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

    search_fields = ['name', 'username', 'mobile_number']
    list_display = ('username', 'name', 'mobile_number')

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
admin.site.register(LeaveSchedule)       
admin.site.register(ShiftSchedule)
admin.site.register(Shift)
admin.site.register(CustomerOTP)