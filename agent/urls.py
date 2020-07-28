from django.conf.urls import include, url
from agent import views 

urlpatterns = [

	url(r'^dashboard/$',views.AgentHome.as_view(),name='agentdash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='agent-orders'),

	url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='agent-feedbacks'),
	url(r'^feedback/details$',views.FeedbackAdvanced.as_view(),name='agent-feedbackadvanced'),	
	url(r'^newfeedback/$',views.AddFeedBack.as_view(),name='new-feedback'),

	url(r'^tickets/$',views.TicketDetails.as_view(),name='agent-tickets'),
	url(r'^ticket/details$',views.TicketAdvanced.as_view(),name='agent-ticketadvanced'),
	url(r'^tickets/register/$',views.TicketRegistration.as_view(),name='agent-ticketregister'),

	url(r'^clients/$',views.ClientDetails.as_view(),name='agent-clients'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='agent-client-orders'),
	url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='agent-client-orderdetails'),

	url(r'^newenquiry/$',views.NewEnquiry.as_view(),name='agent-newenquiry'),
	url(r'^existingenquiry/(?P<enquiry_id>[-\w]+)$',views.ExistingEnquiry.as_view(),name='agent-existingenquiry'),
	

	url(r'^makeevaluation/(?P<enquiry_id>[-\w]+)$',views.MakeEvaluation.as_view(),name='agent-makeevaluation'),
	url(r'^assignevaluator/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.AssignEvaluator.as_view(),name='agent-assignevaluator'),
	
	
	url(r'^makequatation/(?P<enquiry_id>[-\w]+)/$',views.MakeQuatationBase.as_view(),name='agent-makequatation'),
	url(r'^makequatation/phase1/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1.as_view(),name='agent-makequatation1'),
	url(r'^makequatation/phase2/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2.as_view(),name='agent-makequatation2'),


	url(r'^ajax/address/status/$',views.UpdateAddressStatus,name='ajax-updateaddress'),
	url(r'^ajax/getarea/$',views.GetArea,name='ajax-getarea'),
	url(r'^ajax/getcleaningmethods/$',views.GetCleaningMethodsInfo,name='ajax-getcleaningmethod'),
	url(r'^ajax/feedback/order/info/$',views.GetFeedbackOrderInfo,name='get-feedbackorderinfo'),
	url(r'^ajax/ticket/orderscheduler/info/$',views.GetOrderScheduleTicketInfo,name='get-orderscheduleticketInfo'),
	url(r'^ajax/ticket/cleaning/info/$',views.GetCleaningTicketInfo,name='get-cleaningticketInfo'),
	url(r'^ajax/customer/info/$',views.GetCustomerInfo,name='get-customerInfo'),
	url(r'^ajax/clientdata/',views.ClientData,name='get-clientData'),
	url(r'^ajax/ticketdata/',views.TicketData,name='get-TicketData'),
	url(r'^ajax/feedbackdata/',views.FeedBackData,name='get-FeedBackData'),

]