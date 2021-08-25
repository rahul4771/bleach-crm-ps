from django.contrib import admin
from inventory.models import PurchaseOrder,PurchaseOrderItems,Category,Line,Segment,Attribute,AttributeValue,InventoryItem,ItemUnit,InventoryItemImages,Bundle,BundleItems,BundleItemUnits
# Register your models here.

admin.site.register(Category)
admin.site.register(InventoryItem)
admin.site.register(ItemUnit)
admin.site.register(Line)
admin.site.register(Segment)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(InventoryItemImages)
admin.site.register(Bundle)
admin.site.register(BundleItems)
admin.site.register(BundleItemUnits)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItems)
