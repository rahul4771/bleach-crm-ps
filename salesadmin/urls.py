
from django.conf.urls import include, url
from salesadmin import views 

urlpatterns = [

	url(r'^dashboard/$',views.AdminHome.as_view(),name='salesadmindash-board'),
	url(r'^active-subscriptions/$',views.ActiveSubscriptions.as_view(),name='salesadmin-active-subscriptions'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='salesadmin-orders'),
	url(r'^daily-sales/$',views.DailySales.as_view(),name='salesadmin-daily-sales'),

	url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='salesadmin-feedbacks'),
	url(r'^feedback/details/(?P<client_id>[-\w]+)/(?P<order_id>[-\w]+)/$',views.FeedbackAdvanced.as_view(),name='salesadmin-feedbackadvanced'),	

	url(r'^tickets/$',views.TicketDetails.as_view(),name='salesadmin-tickets'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='salesadmin-ticketadvanced'),
	url(r'^ticket/approve/(?P<ticket_id>[-\w]+)$',views.TicketApprove.as_view(),name='salesadmin-ticketapprove'),

	url(r'^clients/$',views.ClientDetails.as_view(),name='salesadmin-clients'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='salesadmin-client-orders'),
	url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='salesadmin-client-orderdetails'),

	url(r'^promocodes/$',views.PromocodeView.as_view(),name='salesadmin-promocode'),

	url(r'^makequatation/phase1/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1Edit.as_view(),name='salesadmin-makequatation1edit'),
	url(r'^makequatation/phase2/delete/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2Delete.as_view(),name='salesadmin-makequatation2delete'),

	url(r'^makequatation/duplicate/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationDuplicate.as_view(),name='salesadmin-makequatation1duplicate'),	
	url(r'^makequatation/phase1/duplicate/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1DuplicateEdit.as_view(),name='salesadmin-makequatation1duplicateedit'),

	url(r'^delete/service/(?P<book_id>[-\w]+)/(?P<evaluation_detail_id>[-\w]+)/$',views.deleteservice,name='salesadmin-delete-service'),
	url(r'^delete/section/(?P<section_id>[-\w]+)/(?P<evaluation_detail_id>[-\w]+)/$',views.deletesection,name='salesadmin-delete-section'),

	url(r'^payments/$',views.PaymentDetails.as_view(),name='salesadmin-payments'),
	url(r'^payment-policy/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.AdminPaymentEdit.as_view(),name='salesadmin-payment-edit'),
	url(r'^ajax/sales-data/',views.SalesLocationData,name='sales-data'),
	url(r'^ajax/sales-data2/',views.SalesCleaningTypeData,name='sales-data2'),
	url(r'^ajax/sales-data3/',views.SalesGovernorateData,name='sales-data3'),
	url(r'^ajax/sales-curve-data/',views.SalesData,name='sales-curve-data'),
	url(r'^ajax/sales-target-data/',views.SalesTargetData,name='sales-target-data'),
	url(r'^ajax/sales-target-daily/',views.SalesTargetDaily,name='sales-target-daily'),
	url(r'^ajax/payment-data/',views.PaymentData,name='payment-data'),
	url(r'^ajax/evaluation-calendar-date/',views.evaluationcalendardate,name='evaluation-calendar-date'),
	url(r'^ajax/cleaning-calendar-date/',views.cleaningcalendardate,name='cleaning-calendar-date'),

	url(r'^cancel-order-form/(?P<order_id>[-\w]+)/$',views.OrderCancellation.as_view(),name='salesadmin-cancel-form'),	
]