from django.conf.urls import include, url
from bleachadmin import views 

urlpatterns = [

	url(r'^dashboard/$',views.AdminHome.as_view(),name='admindash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='admin-orders'),
	url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='admin-feedbacks'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='admin-tickets'),
	url(r'^clients/$',views.ClientDetails.as_view(),name='admin-clients'),
	url(r'^payments/$',views.PaymentDetails.as_view(),name='admin-payments'),

]