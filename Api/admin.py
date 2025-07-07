from django.contrib import admin
from Api.models import XeroConnection, OrderScheduler # Add OrderScheduler here

# Register your models here.
admin.site.register(XeroConnection)
admin.site.register(OrderScheduler)  # Register OrderScheduler