from django.conf.urls import include, url
from inventory import views

urlpatterns = [

url(r'^dashboard/$',views.InventoryHome.as_view(),name='inventorydash-board'),
url(r'^category/$',views.InventoryCategory.as_view(),name='inventory-category'),
url(r'^attribute/$',views.InventoryAttribute.as_view(),name='inventory-attribute'),
url(r'^value/$',views.InventoryValue.as_view(),name='inventory-value'),
url(r'^bundle/$',views.InventoryBundle.as_view(),name='inventory-bundle'),
url(r'^item/$',views.InventoryItme.as_view(),name='inventory-item'),







]