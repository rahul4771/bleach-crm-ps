from django.db import models

# Create your models here.

UNIT_STATUS_CHOICES=(
	('active','active'),
	('out_of_order','out_of_order'),
	('expired','expired')
	)

class Category(models.Model):
    name            =   models.CharField(max_length=100,blank=False,null=False)
    category_code   =   models.CharField(max_length=50,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)
    # created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Segment(models.Model):
    category        =   models.ForeignKey(Category,blank=False,null=False,related_name='segment_category')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)
    # created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Line(models.Model):
    category        =   models.ForeignKey(Category,blank=False,null=False,related_name='line_category')
    segment         =   models.ForeignKey(Segment,blank=False,null=False,related_name='line_segment')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)
    # created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    item_category   =   models.ForeignKey(Category,blank=False,null=False,related_name='item_category')
    item_segment    =   models.ForeignKey(Segment,blank=True,null=True,related_name='item_segment')
    item_line       =   models.ForeignKey(Line,blank=True,null=True,related_name='item_line')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    item_code       =   models.CharField(max_length=50,blank=False,null=False)
    description     =   models.TextField(max_length=1000,blank=True,null=True)
    reserve_count   =   models.CharField(max_length=10,blank=True,null=True)
    status          =   models.BooleanField(default=True,blank=False,null=False)

    # created         =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class InventoryItemImages(models.Model):
    inventory_item  = models.ForeignKey(InventoryItem,blank=False,null=False,related_name='image_item')
    item_image      = models.FileField(upload_to='inventory_item_images/',blank=True,null=True,max_length=1000)
    created         = models.DateTimeField(auto_now_add=True)   

    def __unicode__(self):
        return str(self.inventory_item.name)

    def __str__(self):
        return self.inventory_item.name

class ItemUnit(models.Model):
    item            =   models.ForeignKey(InventoryItem,blank=False,null=False,related_name='unit_item')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    unit_code       =   models.CharField(max_length=50,blank=False,null=False)
    purchase_date   =   models.DateField(blank=True,null=True)
    expiry_date     =   models.DateField(blank=True,null=True)
    unit_price      =   models.CharField(max_length=10,blank=False,null=False)
    status          =   models.CharField(max_length=50,default='active',blank=False,null=False,choices=UNIT_STATUS_CHOICES)
    # created         =   models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    # attribute_type      =   models.CharField(max_length=100,blank=False,null=False,choices=ATTRIBUTE_TYPE_CHOICES)
    attribute_category  =   models.ForeignKey(Category,blank=True,null=True,related_name='attribute_category')
    attribute_segment   =   models.ForeignKey(Segment,blank=True,null=True,related_name='attribute_segment')
    attribute_line      =   models.ForeignKey(Line,blank=True,null=True,related_name='attribute_line')
    name                =   models.CharField(max_length=100,blank=False,null=False)
    status              =   models.BooleanField(default=True,blank=False,null=False)
    # created             =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute           =   models.ForeignKey(Attribute,blank=True,null=True,related_name='value_attribute')
    name                =   models.CharField(max_length=100,blank=False,null=False)
    status              =   models.BooleanField(default=True,blank=False,null=False)
    # created             =   models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

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

class ServiceRecipe(models.Model):
    service_type        = models.CharField(max_length=100,blank=False,null=False)
    item                = models.ForeignKey(InventoryItem,blank=True,null=True,related_name='service_item')
    item_price          = models.CharField(default=0,max_length=100,blank=True,null=True)
    item_count          = models.IntegerField(default=0,null=True,blank=True)
    status              = models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.item.name)

    def __str__(self):
        return self.item.name


