from django.conf.urls import include, url
from order import views 

urlpatterns = [

	url(r'^quotation_data$',views.quotation_data,name='quotation_data'),
	url(r'^quotation_data_policy/$',views.quotation_data_policy,name='quotation_data_policy'),
	url(r'^send-invoice/',views.sendinvoice,name='send-invoice'),
	url(r'^send-quotation/',views.sendquotation,name='send-quotation'),
	url(r'^send-receipt/',views.sendreceipt,name='send-receipt'),
	url(r'^send-feedback-link/',views.sendfeedbacklink,name='send-feedback-link'),

	
]