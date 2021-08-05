from django.contrib import admin
from inventory.models import Category,Item,Line,Segment,Attribute,AttributeValue
# Register your models here.

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Line)
admin.site.register(Segment)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
