from django.db import models

# Create your models here.

UNIT_STATUS_CHOICES=(
	('Active','active'),
	('Out of Order','out_of_order'),
	('Expired','expired')
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

class ItemUnit(models.Model):
    item            =   models.ForeignKey(InventoryItem,blank=False,null=False,related_name='unit_item')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    unit_code       =   models.CharField(max_length=50,blank=False,null=False)
    purchase_date   =   models.DateField(blank=True,null=True)
    expiry_date     =   models.DateField(blank=True,null=True)
    unit_price      =   models.CharField(max_length=10,blank=False,null=False)
    status          =   models.CharField(max_length=50,default='Active',blank=False,null=False,choices=UNIT_STATUS_CHOICES)
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



