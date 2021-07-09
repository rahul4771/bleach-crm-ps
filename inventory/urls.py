from django.conf.urls import include, url
from inventory import views

urlpatterns = [

url(r'^dashboard/$',views.InventoryHome.as_view(),name='inventorydash-board'),
url(r'^category/$',views.InventoryCategory.as_view(),name='inventory-category'),
url(r'^attribute/$',views.InventoryAttribute.as_view(),name='inventory-attribute'),
url(r'^value/$',views.InventoryValue.as_view(),name='inventory-value'),
url(r'^bundle/$',views.InventoryBundle.as_view(),name='inventory-bundle'),
url(r'^item/$',views.InventoryItem.as_view(),name='inventory-item'),
url(r'^supplier/$',views.InventorySupplier.as_view(),name='inventory-supppler'),
url(r'^store/$',views.InventoryStore.as_view(),name='inventory-store'),
url(r'^inventory/$',views.InventoryInv.as_view(),name='inventory-inv'),
url(r'^order/$',views.InventoryOrder.as_view(),name='inventory-order'),
url(r'^users/$',views.InventoryUsers.as_view(),name='inventory-users'),












]