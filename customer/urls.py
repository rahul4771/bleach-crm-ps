from django.conf.urls import include, url
from customer import views 

#all users urls

urlpatterns = [

		url(r'^quatation/(?P<evaluation_id>[-\w]+)$',views.Quatation.as_view(),name='quatation'),
		url(r'^tc/$',views.TermsandConditions.as_view(),name='tc'),
		url(r'^invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerInvoice.as_view(),name='invoice'),
		url(r'^receipt/$',views.PaymentResponse.as_view(),name='receipt'),

	]