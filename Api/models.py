from django.db import models

# Create your models here.
class XeroConnection(models.Model):
    code                = models.TextField(blank=True,null=True)
    access_token        = models.TextField(blank=True,null=True)
    refresh_token       = models.TextField(blank=True,null=True)
    tenant_id           = models.TextField(blank=True,null=True)
    client_id           = models.TextField(blank=True,null=True)
    client_secret       = models.TextField(blank=True,null=True)
    client_encoded      = models.TextField(blank=True,null=True)

    is_active           = models.BooleanField(null=False,blank=True,default=True)
    created             = models.DateTimeField(auto_now_add=True)
    updated             = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.code)

    def __str__(self):
        return str(self.code)