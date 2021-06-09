from django.conf.urls import include, url
from common_items import views 

#all users urls

urlpatterns = [
		url(r'^orders/$',views.OrderDetails.as_view(),name='orders'),
		url(r'^clients/$',views.ClientDetails.as_view(),name='clients'),
		url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='client-orders'),
		url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='client-orderdetails'),
		url(r'^tickets/$',views.TicketDetails.as_view(),name='tickets'),
		url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='ticketadvanced'),
		url(r'^customer-bookings/$',views.CustomerBookingsList.as_view(),name='customer-bookings'),
		url(r'^payments/$',views.PaymentDetails.as_view(),name='payments'),
		url(r'^active-subscriptions/$',views.ActiveSubscriptions.as_view(),name='active-subscriptions'),
		url(r'^daily-sales/$',views.DailySales.as_view(),name='daily-sales'),
		url(r'^makequatation/phase1/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1Edit.as_view(),name='makequatation1edit'),
		url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),

		url(r'^resources-new/$',views.ResourceManagementTest.as_view(),name='resource-management-new'),
		url(r'^productivity-test/$',views.ProductivityTest.as_view(),name='productivity-test'),
	
		url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='feedbacks'),
		url(r'^feedback/details/(?P<client_id>[-\w]+)/(?P<order_id>[-\w]+)/$',views.FeedbackAdvanced.as_view(),name='feedbackadvanced'),

		url(r'^leave-scheduler/$',views.LeaveScheduler.as_view(),name='leave-scheduler'),	

		url(r'^promocodes/$',views.PromocodeView.as_view(),name='promocode'),

		url(r'^ajax/resourcestoggle/',views.ResourcesToggle,name='resource-toggle'),
	]