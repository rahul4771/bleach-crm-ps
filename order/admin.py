from django.contrib import admin
from order.models import Order,OrderScheduler,FollowUp,FollowUpScheduler,Question,FeedBack,Investigation,InvestigationMedia
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
	radio_fields = {"order_status":admin.VERTICAL,"payment_status":admin.VERTICAL}

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderScheduler)

class InvestigationMediaInline(admin.TabularInline):
	model = InvestigationMedia
	extra = 1

class InvestigationAdmin(admin.ModelAdmin):
	inlines = (InvestigationMediaInline,)

class InvestigationMediaAdmin(admin.ModelAdmin):
	radio_fields = {"media_type":admin.HORIZONTAL,"taken_status":admin.HORIZONTAL}


admin.site.register(Investigation,InvestigationAdmin)
admin.site.register(InvestigationMedia,InvestigationMediaAdmin)



admin.site.register(FollowUp)
admin.site.register(FollowUpScheduler)

class FeedBackAdmin(admin.ModelAdmin):
	radio_fields = {"question":admin.VERTICAL}


admin.site.register(FeedBack,FeedBackAdmin)
admin.site.register(Question)