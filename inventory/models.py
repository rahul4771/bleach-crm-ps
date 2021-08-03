from django.db import models

# Create your models here.

ATTRIBUTE_TYPE_CHOICES=(
	('CATEGORY','CATEGORY'),
	('SEGMENT','SEGMENT'),
	('LINE','LINE')
	)

class Category(models.Model):
    name            =   models.CharField(max_length=100,blank=False,null=False)
    category_code   =   models.CharField(max_length=50,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Segment(models.Model):
    category        =   models.ForeignKey(Category,blank=False,null=False,related_name='segment_category')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Line(models.Model):
    category        =   models.ForeignKey(Category,blank=False,null=False,related_name='line_category')
    segment         =   models.ForeignKey(Segment,blank=False,null=False,related_name='line_segment')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Item(models.Model):
    category        =   models.ForeignKey(Category,blank=False,null=False,related_name='item_category')
    name            =   models.CharField(max_length=100,blank=False,null=False)
    item_code       =   models.CharField(max_length=50,blank=False,null=False)
    quantity        =   models.CharField(max_length=10,blank=False,null=False)
    unit_price      =   models.CharField(max_length=10,blank=False,null=False)
    status          =   models.BooleanField(default=True,blank=False,null=False)

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

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name

class Value(models.Model):
    Attribute           =   models.ForeignKey(Attribute,blank=True,null=True,related_name='value_attribute')
    name                =   models.CharField(max_length=100,blank=False,null=False)
    status              =   models.BooleanField(default=True,blank=False,null=False)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return self.name



