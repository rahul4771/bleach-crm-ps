from django.db import models
from user.models import UserProfile
# Create your models here.

UNIT_STATUS_CHOICES=(
	('active','active'),
	('out_of_order','out_of_order'),
	('expired','expired')
	)

ITEM_STATUS_CHOICES=(
	('available','Available'),
	('out_of_stock','out_of_stock'),
	('about_to_finish','about_to_finish')
	)

class Category(models.Model):
    name            =   models.CharField(max_length=100,blank=False,null=False)
    category_code   =   models.CharField(max_length=50,blank=False,null=False)
    category_id     =   models.CharField(max_length=50,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)
    created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Segment(models.Model):
    category        =   models.ForeignKey(Category,blank=False,null=False,related_name='segment_category')
    segment_id      =   models.CharField(max_length=50,blank=False,null=False)
    name            =   models.CharField(max_length=100,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)
    created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Line(models.Model):
    category        =   models.ForeignKey(Category,blank=False,null=False,related_name='line_category')
    segment         =   models.ForeignKey(Segment,blank=False,null=False,related_name='line_segment')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    line_id         =   models.CharField(max_length=50,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)
    created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name


class Store(models.Model):
    store_name          = models.CharField(max_length=100,blank=False,null=False)
    store_code          = models.CharField(max_length=50,blank=False,null=False)
    address             = models.TextField(max_length=1000,blank=False,null=False)
    contact             = models.CharField(max_length=50,blank=False,null=False)
    status              = models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.store_name)

    def __str__(self):
        return self.store_name


class InventoryItem(models.Model):
    item_category   =   models.ForeignKey(Category,blank=False,null=False,related_name='item_category')
    item_segment    =   models.ForeignKey(Segment,blank=True,null=True,related_name='item_segment')
    item_line       =   models.ForeignKey(Line,blank=True,null=True,related_name='item_line')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    item_code       =   models.CharField(max_length=50,blank=False,null=False)
    description     =   models.TextField(max_length=1000,blank=True,null=True)
    reserve_count   =   models.CharField(max_length=10,blank=True,null=True)
    is_reusable     =   models.BooleanField(blank=False,null=False)
    item_status     =   models.CharField(max_length=50,blank=True,null=True,choices=ITEM_STATUS_CHOICES)
    status          =   models.BooleanField(default=True,blank=False,null=False)
    created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class InventoryItemImages(models.Model):
    inventory_item  = models.ForeignKey(InventoryItem,blank=False,null=False,related_name='image_item')
    item_image      = models.FileField(upload_to='inventory_item_images/',blank=True,null=True,max_length=1000)
    is_default_image= models.BooleanField(default=False,blank=False,null=False)
    created         = models.DateTimeField(auto_now_add=True)   

    def __unicode__(self):
        return str(self.inventory_item.name)

    def __str__(self):
        return self.inventory_item.name

class ItemUnit(models.Model):
    item            =   models.ForeignKey(InventoryItem,blank=False,null=False,related_name='unit_item')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    unit_code       =   models.CharField(max_length=50,blank=False,null=False)
    store           =   models.ForeignKey(Store,blank=True,null=True,related_name='unit_store')
    purchase_date   =   models.DateField(blank=True,null=True)
    expiry_date     =   models.DateField(blank=True,null=True)
    no_expiry       =   models.BooleanField(default=False,blank=False,null=False)
    unit_price      =   models.CharField(max_length=10,blank=False,null=False)
    status          =   models.CharField(max_length=50,default='active',blank=False,null=False,choices=UNIT_STATUS_CHOICES)
    created         =   models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.item.name)

    def __str__(self):
        return self.item.name

class Attribute(models.Model):
    # attribute_type      =   models.CharField(max_length=100,blank=False,null=False,choices=ATTRIBUTE_TYPE_CHOICES)
    attribute_category  =   models.ForeignKey(Category,blank=True,null=True,related_name='attribute_category')
    attribute_segment   =   models.ForeignKey(Segment,blank=True,null=True,related_name='attribute_segment')
    attribute_line      =   models.ForeignKey(Line,blank=True,null=True,related_name='attribute_line')
    name                =   models.CharField(max_length=100,blank=False,null=False)
    status              =   models.BooleanField(default=True,blank=False,null=False)
    created             =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute           =   models.ForeignKey(Attribute,blank=True,null=True,related_name='value_attribute')
    name                =   models.CharField(max_length=100,blank=False,null=False)
    is_selected         =   models.BooleanField(default=False,blank=False,null=False)
    status              =   models.BooleanField(default=True,blank=False,null=False)
    created             =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class ItemAttributes(models.Model):
    item                =   models.ForeignKey(InventoryItem,blank=True,null=True,related_name='inventory_item')
    attribute           =   models.ForeignKey(Attribute,blank=True,null=True,related_name='inventory_item_attribute')
    attribute_value     =   models.ForeignKey(AttributeValue,blank=True,null=True,related_name='inventory_item_attribute_value')
    created             =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.item.name)

    def __str__(self):
        return self.item.name


class Bundle(models.Model):
    name                =   models.CharField(max_length=100,blank=False,null=False)
    bundle_code         =   models.CharField(max_length=50,blank=False,null=False)
    bundle_items_count  =   models.IntegerField(default=0,null=True,blank=True)
    bundle_price        =   models.CharField(default=0,max_length=100,blank=False,null=False)
    status              =   models.BooleanField(default=True,blank=False,null=False)
    created             =   models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class BundleItems(models.Model):
    bundle              = models.ForeignKey(Bundle,blank=True,null=True,related_name='item_bundle')
    item                = models.ForeignKey(InventoryItem,blank=True,null=True,related_name='inventory_item_bundle')
    item_price          = models.CharField(default=0,max_length=100,blank=True,null=True)
    item_count          = models.IntegerField(default=0,null=True,blank=True)
    created             = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.bundle.name)

    def __str__(self):
        return self.bundle.name

class BundleItemUnits(models.Model):
    bundle_item         = models.ForeignKey(BundleItems,blank=True,null=True,related_name='bundle_unit_bundle_item')
    item_unit           = models.ForeignKey(ItemUnit,blank=True,null=True,related_name='unit_item_bundle')
    unit_price          = models.CharField(default=0,max_length=100,blank=False,null=False)
    created             = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.bundle_item.bundle.name)

    def __str__(self):
        return self.bundle_item.bundle.name

class Supplier(models.Model):
    supplier_name       = models.CharField(max_length=100,blank=False,null=False)
    supplier_id         = models.CharField(max_length=50,blank=False,null=False)
    contact             = models.CharField(max_length=50,blank=False,null=False)
    other_contact       = models.CharField(max_length=50,blank=False,null=False)
    address             = models.TextField(max_length=500,blank=False,null=False)
    terms               = models.TextField(max_length=1000,blank=False,null=False)
    status              = models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.supplier_name)

    def __str__(self):
        return self.supplier_name

class SupplierItems(models.Model):
    supplier            = models.ForeignKey(Supplier,blank=True,null=True,related_name='item_supplier')
    item                = models.CharField(max_length=100,blank=False,null=False)
    supplier_item_id    = models.CharField(max_length=50,blank=False,null=False)
    item_price          = models.CharField(default=0,max_length=100,blank=True,null=True)
    item_count          = models.IntegerField(default=0,null=True,blank=True)
    created             = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.supplier.supplier_name)

    def __str__(self):
        return self.supplier.supplier_name

# class SupplierItemUnits(models.Model):
#     supplier_item         = models.ForeignKey(SupplierItems,blank=True,null=True,related_name='supplier_unit_supplier_item')
#     item_unit           = models.ForeignKey(ItemUnit,blank=True,null=True,related_name='unit_item_supplier')
#     unit_price          = models.CharField(default=0,max_length=100,blank=False,null=False)
#     created             = models.DateTimeField(auto_now_add=True)

#     def __unicode__(self):
#         return str(self.supplier_item.bundle.name)

#     def __str__(self):
#         return self.supplier_item.bundle.name

class ServiceRecipe(models.Model):
    service             = models.CharField(max_length=100,blank=True,null=True)
    area_size           = models.CharField(default=0,max_length=50,blank=True,null=True)

    def __unicode__(self):
        return str(self.service)

    def __str__(self):
        return self.service

class ServiceRecipeItems(models.Model):
    service_or_person   = models.CharField(max_length=50,blank=False,null=False)
    service_type        = models.ForeignKey(ServiceRecipe,blank=True,null=True,related_name='item_recipe')
    item                = models.ForeignKey(InventoryItem,blank=True,null=True,related_name='service_item')
    item_price          = models.CharField(default=0,max_length=100,blank=True,null=True)
    item_count          = models.IntegerField(default=0,null=True,blank=True)
    status              = models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.service_type.service)

    def __str__(self):
        return self.service_type.service

class PurchaseOrder(models.Model):
    supplier            = models.ForeignKey(Supplier,blank=True,null=True,related_name='supplier_purchase_order')
    purchase_order_id   = models.CharField(max_length=50,blank=False,null=False)
    status              = models.BooleanField(default=True,blank=False,null=False)
    initiated_by        = models.ForeignKey(UserProfile,blank=True,null=True,related_name='initiated_by_purchase_order')
    discount            = models.CharField(max_length=10,blank=True,null=True)
    tax                 = models.CharField(max_length=10,blank=True,null=True)
    shipping_charge     = models.CharField(max_length=10,blank=True,null=True)
    other_charge        = models.CharField(max_length=10,blank=True,null=True)
    is_order_completed  = models.BooleanField(default=False,blank=False,null=False)
    created             = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.purchase_order_id)

    def __str__(self):
        return self.purchase_order_id


class PurchaseOrderItems(models.Model):
    purchase_order      = models.ForeignKey(PurchaseOrder,blank=True,null=True,related_name='purchase_order_purchase_order_item')
    product             = models.ForeignKey(SupplierItems,blank=True,null=True,related_name='product_purchase_order_item')
    item_count          = models.IntegerField(default=0,null=True,blank=True)
    unit_price          = models.CharField(default=0,max_length=100,blank=True,null=True)
    total_price         = models.CharField(default=0,max_length=100,blank=True,null=True)
    created             = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.purchase_order.purchase_order_id)

    def __str__(self):
        return self.purchase_order.purchase_order_id

