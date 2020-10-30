from django.conf.urls import include, url
from order import views 

urlpatterns = [

	url(r'^quotation_data/$',views.quotation_data,name='quotation_data'),
	url(r'^send-invoice/',views.sendinvoice,name='send-invoice'),
	url(r'^send-quotation/',views.sendquotation,name='send-quotation'),

	
]