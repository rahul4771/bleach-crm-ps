from django.contrib import admin
from bleachadmin.models import ServiceProductivity,ServicePriceRange,Settings,ServiceAddOns

# Register your models here.
admin.site.register(ServiceProductivity)
admin.site.register(ServicePriceRange)
admin.site.register(Settings)
admin.site.register(ServiceAddOns)