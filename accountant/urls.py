from django.conf.urls import include, url
from accountant import views 

urlpatterns = [

	url(r'^dashboard/$',views.AccountantHome.as_view(),name='accountantdash-board'),
	url(r'^payments/$',views.PaymentDetails.as_view(),name='accountant-payments'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='accountant-orders'),

	url(r'^clients/$',views.ClientDetails.as_view(),name='accountant-clients'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='accountant-client-orders'),
	url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='accountant-client-orderdetails'),

	url(r'^cash/collect/$',views.CashCollect.as_view(),name='accountant-cashcollect'),

	url(r'^generate/link/$',views.PaymentLinkGeneration.as_view(),name='accountant-paymentlink'),

	url(r'^ajax/cashcollect/order/info/$',views.GetCashCollectOrderInfo,name='get-cashorderInfo'),

]