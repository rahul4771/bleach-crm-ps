from django.conf.urls import include, url
from accountant import views 

urlpatterns = [

	url(r'^dashboard/$',views.AccountantHome.as_view(),name='accountantdash-board'),
	url(r'^payments/$',views.PaymentDetails.as_view(),name='accountant-payments'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='accountant-orders'),
	url(r'^clients/$',views.ClientDetails.as_view(),name='accountant-clients'),

]