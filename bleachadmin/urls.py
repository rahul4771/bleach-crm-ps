from django.conf.urls import include, url
from bleachadmin import views 

urlpatterns = [

	url(r'^dashboard/$',views.AdminHome.as_view(),name='admindash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='admin-orders'),

	url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='admin-feedbacks'),
	url(r'^feedback/details/(?P<client_id>[-\w]+)/(?P<order_id>[-\w]+)/$',views.FeedbackAdvanced.as_view(),name='admin-feedbackadvanced'),	

	url(r'^tickets/$',views.TicketDetails.as_view(),name='admin-tickets'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='admin-ticketadvanced'),
	url(r'^ticket/approve/(?P<ticket_id>[-\w]+)$',views.TicketApprove.as_view(),name='admin-ticketapprove'),
	# url(r'^ticket/buybackpromogift/approve/(?P<buybackpromogift_id>[-\w]+)$',views.BuybackPromocodeGiftApprove.as_view(),name='admin-buybackpromogift'),	

	url(r'^clients/$',views.ClientDetails.as_view(),name='admin-clients'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='admin-client-orders'),
	url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='admin-client-orderdetails'),

	url(r'^promocodes/$',views.PromocodeView.as_view(),name='admin-promocode'),
	

	url(r'^payments/$',views.PaymentDetails.as_view(),name='admin-payments'),
	url(r'^ajax/sales-data/',views.SalesLocationData,name='sales-data'),
	url(r'^ajax/sales-data2/',views.SalesCleaningTypeData,name='sales-data2'),
	url(r'^ajax/sales-data3/',views.SalesGovernorateData,name='sales-data3'),
	url(r'^ajax/sales-curve-data/',views.SalesData,name='sales-curve-data'),
	url(r'^ajax/sales-target-data/',views.SalesTargetData,name='sales-target-data'),
	url(r'^ajax/sales-target-daily/',views.SalesTargetDaily,name='sales-target-daily'),
	url(r'^ajax/payment-data/',views.PaymentData,name='payment-data'),
	url(r'^ajax/evaluation-calendar-date/',views.evaluationcalendardate,name='evaluation-calendar-date'),
	url(r'^ajax/cleaning-calendar-date/',views.cleaningcalendardate,name='cleaning-calendar-date'),
]