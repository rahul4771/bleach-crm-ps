from django.conf.urls import include, url
from evaluator import views 

urlpatterns = [

	url(r'^dashboard/$',views.EvaluatorHome.as_view(),name='evaluatordash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='evaluator-orders'),
	url(r'^clients/$',views.ClientDetails.as_view(),name='evaluator-clients'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='evaluator-tickets'),

]