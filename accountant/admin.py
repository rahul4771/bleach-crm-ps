from django.contrib import admin
from accountant.models import PaymentHistory,DailySales,AdditionalChargeHistory
# Register your models here.

class PaymentHistoryAdmin(admin.ModelAdmin):
	search_fields=['order__order_no']
    
admin.site.register(PaymentHistory,PaymentHistoryAdmin)
admin.site.register(DailySales)
admin.site.register(AdditionalChargeHistory)

