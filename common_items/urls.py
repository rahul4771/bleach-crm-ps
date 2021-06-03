from django.conf.urls import include, url
from common_items import views 

#all users urls

urlpatterns = [

		url(r'^clients/$',views.ClientDetails.as_view(),name='clients'),
		url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='client-orders'),
		url(r'^tickets/$',views.TicketDetails.as_view(),name='tickets'),
		url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='ticketadvanced'),
		
	]