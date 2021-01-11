from django.conf.urls import include, url
from qualitycontrol import views 

urlpatterns = [

    url(r'^investigation/$',views.investigation,name='investigation'),

]