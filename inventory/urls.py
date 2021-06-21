from django.conf.urls import include, url
from inventory import views

urlpatterns = [

url(r'^dashboard/$',views.InventoryHome.as_view(),name='inventorydash-board'),

]