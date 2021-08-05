from django.contrib import admin
from inventory.models import Category,Line,Segment,Attribute,AttributeValue
# Register your models here.

admin.site.register(Category)
# admin.site.register(InventoryItem)
# admin.site.register(ItemUnit)
admin.site.register(Line)
admin.site.register(Segment)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
