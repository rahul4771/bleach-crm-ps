from django.contrib import admin
from bleachadmin.models import ServiceProductivity,ServicePriceRange,Settings

# Register your models here.
admin.site.register(ServiceProductivity)
admin.site.register(ServicePriceRange)
admin.site.register(Settings)