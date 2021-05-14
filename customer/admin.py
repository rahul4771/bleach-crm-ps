from django.contrib import admin
from customer.models import CustomerBooking,NewCustomerOtp

# Register your models here.
admin.site.register(CustomerBooking)
admin.site.register(NewCustomerOtp)