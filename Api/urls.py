from django.conf.urls import include, url
from Api import views 

urlpatterns = [

	url(r'^checkslote/$',views.ApiCheckSlote.as_view(),name='api-checkslote'),
	url(r'^basicdetails/$',views.ApiBasicDetails.as_view(),name='api-basicdetails'),
	url(r'^evaluation-booking/$',views.EvaluationBooking.as_view(),name='api-evaluationbooking'),

	url(r'^payment/response/credit/$',views.PaymentResponseCredit.as_view(),name='api-responsecredit'),
]