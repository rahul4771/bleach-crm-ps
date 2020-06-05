from django.conf.urls import include, url
from agent import views 

urlpatterns = [

	url(r'^dashboard/$',views.AgentHome.as_view(),name='agentdash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='agent-orders'),
	url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='agent-feedbacks'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='agent-tickets'),
	url(r'^clients/$',views.ClientDetails.as_view(),name='agent-clients'),

	url(r'^newenquiry/$',views.NewEnquiry.as_view(),name='agent-newenquiry'),
	url(r'^existingenquiry/(?P<enquiry_id>[-\w]+)$',views.ExistingEnquiry.as_view(),name='agent-existingenquiry'),
	url(r'^assignevaluator/(?P<enquiry_id>[-\w]+)$',views.AssignEvaluator.as_view(),name='agent-assignevaluator'),

	url(r'^ajax/getarea/$',views.GetArea,name='ajax-getarea'),
	# url(r'^ajax/getcustomer/info/$',views.GetCustomerInfo,name='ajax-getcustomerinfo'),


]