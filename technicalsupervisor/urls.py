from django.conf.urls import include, url
from technicalsupervisor import views 

app_name = 'technicalsupervisor'


urlpatterns = [

	url(r'^dashboard/$',views.TechnicalSupervisorHome.as_view(),name='tech-supervisor-dash-board'),
	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='tech-supervisor-orders'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='tech-supervisor-tickets'),
	url(r'^order-details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='tech-supervisor-order-details'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='tech-supervisor-client-orders'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='tech-supervisor-ticketadvanced'),
]