from django.conf.urls import include, url
from customer import views 

#all users urls

urlpatterns = [

		url(r'^quatation/(?P<evaluation_id>[-\w]+)$',views.Quatation.as_view(),name='quatation'),
		url(r'^subscription/quatation/(?P<evaluation_id>[-\w]+)$',views.SubscriptionQuatation.as_view(),name='subscriptionquatation'),
		url(r'^tc/$',views.TermsandConditions.as_view(),name='tc'),
		url(r'^invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerInvoice.as_view(),name='invoice'),
		url(r'^subscription/invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerSubscriptionInvoice.as_view(),name='subscriptioninvoice'),
		
		url(r'^statement-of-account$',views.statement_of_account,name='statement-of-account'),

		url(r'^payment/response/$',views.PaymentResponseDebit.as_view(),name='response'),
		url(r'^payment/receipt/(?P<payment_id>[-\w]+)$',views.PaymentReceipt.as_view(),name='payment-receipt'),
		url(r'^payment/failed/$',views.PaymentFailedResponse.as_view(),name='payment-failed'),

		url(r'^order/details/(?P<order_id>[-\w]+)/(?P<service_id>[-\w]+)/(?P<section_id>[-\w]+)$',views.CustomerOrderDetails.as_view(),name='customer-order-details'),
		url(r'^feedback-page/(?P<order_id>[-\w]+)$',views.CustomerFeedback.as_view(),name='customer-feedback'),

		url(r'^quatation/download/(?P<evaluation_id>[-\w]+)$',views.quatation_html_to_pdf_view,name='quatation-download'),
		url(r'^invoice/download/(?P<evaluation_id>[-\w]+)$',views.invoice_html_to_pdf_view,name='invoice-download'),
		url(r'^payment/receipt/download/(?P<payment_id>[-\w]+)$',views.receipt_html_to_pdf_view,name='payment-receipt-download'),
		url(r'^order-detail/download/(?P<order_id>[-\w]+)/(?P<service_id>[-\w]+)/(?P<section_id>[-\w]+)$',views.orderdetail_html_to_pdf_view,name='order-detail-download'),
		url(r'^terms-and-conditions/download$',views.termsandconditions_to_pdf,name='terms-conditions-download'),
	]