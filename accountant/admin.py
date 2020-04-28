from django.contrib import admin
from accountant.models import Invoice,PaymentHistory
# Register your models here.

admin.site.register(Invoice)
admin.site.register(PaymentHistory)
