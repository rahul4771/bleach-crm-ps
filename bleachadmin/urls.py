from django.conf.urls import include, url
from bleachadmin import views 

urlpatterns = [

	url(r'^dashboard/$',views.AdminHome.as_view(),name='admindash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='admin-orders'),
	url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='admin-feedbacks'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='admin-tickets'),

	url(r'^clients/$',views.ClientDetails.as_view(),name='admin-clients'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='admin-client-orders'),
	url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='admin-client-orderdetails'),

	url(r'^payments/$',views.PaymentDetails.as_view(),name='admin-payments'),
	url(r'^ajax/sales-data/',views.SalesLocationData,name='sales-data'),
	url(r'^ajax/sales-data2/',views.SalesCleaningTypeData,name='sales-data2'),
	url(r'^ajax/sales-data3/',views.SalesGovernorateData,name='sales-data3'),
]