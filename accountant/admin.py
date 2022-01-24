from django.contrib import admin
from accountant.models import PaymentHistory
# Register your models here.

class PaymentHistoryAdmin(admin.ModelAdmin):
	search_fields=['order__order_no']
    
admin.site.register(PaymentHistory,PaymentHistoryAdmin)

