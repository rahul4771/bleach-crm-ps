from django.conf.urls import include, url
from customer import views 

#all users urls

urlpatterns = [

		url(r'^quatation/(?P<evaluation_id>[-\w]+)$',views.Quatation.as_view(),name='quatation'),
		url(r'^tc/$',views.TermsandConditions.as_view(),name='tc'),
		url(r'^invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerInvoice.as_view(),name='invoice'),
		url(r'^payment/response/$',views.PaymentResponse.as_view(),name='response'),
		url(r'^payment/receipt/(?P<payment_id>[-\w]+)$',views.PaymentReceipt.as_view(),name='payment-receipt'),
		url(r'^payment/failed/$',views.PaymentFailedResponse.as_view(),name='payment-failed'),
		url(r'^order/details/(?P<order_id>[-\w]+)$',views.CustomerOrderDetails.as_view(),name='customer-order-details'),

		url(r'^quatation/download/(?P<evaluation_id>[-\w]+)$',views.quatation_html_to_pdf_view,name='quatation-download'),
		url(r'^invoice/download/(?P<evaluation_id>[-\w]+)$',views.invoice_html_to_pdf_view,name='invoice-download'),
		url(r'^payment/receipt/download/(?P<payment_id>[-\w]+)$',views.receipt_html_to_pdf_view,name='payment-receipt-download'),
	]