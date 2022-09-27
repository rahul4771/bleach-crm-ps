from django.contrib import admin
from customer.models import CartServiceFloor,CustomerCart,CartService,CartSchedule,CustomerBooking,NewCustomerOtp

# Register your models here.
admin.site.register(CustomerBooking)
admin.site.register(NewCustomerOtp)
admin.site.register(CustomerCart)
admin.site.register(CartService)
admin.site.register(CartSchedule)
admin.site.register(CartServiceFloor)