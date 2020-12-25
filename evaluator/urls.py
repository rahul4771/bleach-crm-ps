from django.conf.urls import include, url
from evaluator import views 

urlpatterns = [

	url(r'^dashboard/$',views.EvaluatorHome.as_view(),name='evaluatordash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='evaluator-orders'),
	

	url(r'^clients/$',views.ClientDetails.as_view(),name='evaluator-clients'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='evaluator-client-orders'),
	url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='evaluator-client-orderdetails'),

	url(r'^tickets/$',views.TicketDetails.as_view(),name='evaluator-tickets'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='evaluator-ticketadvanced'),

	url(r'^newenquiry/$',views.NewEnquiry.as_view(),name='evaluator-newenquiry'),
	url(r'^existingenquiry/(?P<enquiry_id>[-\w]+)$',views.ExistingEnquiry.as_view(),name='evaluator-existingenquiry'),
	
	url(r'^makeevaluation/(?P<enquiry_id>[-\w]+)$',views.MakeEvaluation.as_view(),name='evaluator-makeevaluation'),
	url(r'^assignevaluator/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.AssignEvaluator.as_view(),name='evaluator-assignevaluator'),
	
	url(r'^makequatation/(?P<enquiry_id>[-\w]+)/$',views.MakeQuatationBase.as_view(),name='evaluator-makequatation'),
	url(r'^makequatation/phase1/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1.as_view(),name='evaluator-makequatation1'),
	url(r'^makequatation/phase2/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2.as_view(),name='evaluator-makequatation2'),
	url(r'^makequatation/phase2/edit/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2Edit.as_view(),name='evaluator-makequatation2edit'),

	url(r'^delete/service/(?P<book_id>[-\w]+)/(?P<evaluation_detail_id>[-\w]+)/$',views.deleteservice,name='evaluator-delete-service'),
	url(r'^delete/section/(?P<url_type>[-\w]+)/(?P<section_id>[-\w]+)/(?P<evaluation_detail_id>[-\w]+)/$',views.deletesection,name='evaluator-delete-section'),		
	
	url(r'^makequatation/assigned/phase1/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeAssignedQuatationPhase1.as_view(),name='evaluator-makeassignedquatation1'),
	url(r'^makequatation/assigned/phase2/(?P<evaluation_detail_id>[-\w]+)$',views.MakeAssignedQuatationPhase2.as_view(),name='evaluator-makeassignedquatation2'),
	url(r'^makequatation/assigned/phase2/edit/(?P<evaluation_detail_id>[-\w]+)$',views.MakeAssignedQuatationPhase2Edit.as_view(),name='evaluator-makeassignedquatation2edit'),

	url(r'^makequatation/phase1/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1Edit.as_view(),name='evaluator-makequatation1edit'),
	url(r'^makequatation/phase2/delete/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2Delete.as_view(),name='evaluator-makequatation2delete'),

	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),
]