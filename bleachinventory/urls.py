from django.conf.urls import include, url
from bleachinventory import views

urlpatterns = [

url(r'^dashboard/$',views.InventoryHome.as_view(),name='inventorydash-board'),
url(r'^category/$',views.InventoryCategory.as_view(),name='inventory-category'),
url(r'^attribute/$',views.InventoryAttribute.as_view(),name='inventory-attribute'),
url(r'^value/$',views.InventoryValue.as_view(),name='inventory-value'),
url(r'^bundle/$',views.InventoryBundle.as_view(),name='inventory-bundle'),
url(r'^item/(?P<item_id>[-\w]+)/$',views.InventoryItems.as_view(),name='inventory-item'),
url(r'^supplier/$',views.InventorySupplier.as_view(),name='inventory-supplier'),
url(r'^store/$',views.InventoryStore.as_view(),name='inventory-store'),
url(r'^inventory/$',views.InventoryInv.as_view(),name='inventory-inv'),
url(r'^order/$',views.InventoryOrder.as_view(),name='inventory-order'),
url(r'^users/$',views.InventoryUsers.as_view(),name='inventory-users'),
url(r'^checkout/$',views.InventoryCheckout.as_view(),name='inventory-checkout'),
url(r'^createcheckout/(?P<visit_id>[-\w]+)/$',views.InventoryCreateCheckout.as_view(),name='inventory-createcheckout'),
url(r'^purchaseOrder/$',views.InventoryPurchaseOrder.as_view(),name='inventory-purchaseorder'),
url(r'^purchaseOrder/items/(?P<purchase_order_id>[-\w]+)/$',views.PurchaseOrderItemsPage.as_view(),name='inventory-purchaseorderitems'),
url(r'^purchaseorderpage/(?P<purchase_order_id>[-\w]+)/$',views.InventoryPurchaseOrderPage.as_view(),name='inventory-purchaseorderpage'),
url(r'^createpo/$',views.InventoryCreatePurchaseOrder.as_view(),name='inventory-createpurchaseorder'),
url(r'^editpo/(?P<purchase_order_id>[-\w]+)/$',views.InventoryEditPurchaseOrder.as_view(),name='inventory-editpurchaseorder'),
url(r'^viewpo/$',views.InventoryViewPurchaseOrder.as_view(),name='inventory-viewpurchaseorder'),
url(r'^checked-in/$',views.InventoryCheckedIn.as_view(),name='inventory-checked-in'),
url(r'^orderdetails/$',views.InventoryOrderDetails.as_view(),name='inventory-order-details'),
url(r'^services/$',views.InventoryServices.as_view(),name='inventory-services'),
url(r'^segment/(?P<category_id>[-\w]+)/$',views.InventorySegment.as_view(),name='inventory-segment'),





















]