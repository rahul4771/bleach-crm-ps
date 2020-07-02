from django.conf.urls import include, url
from evaluator import views 

urlpatterns = [

	url(r'^dashboard/$',views.EvaluatorHome.as_view(),name='evaluatordash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='evaluator-orders'),
	url(r'^clients/$',views.ClientDetails.as_view(),name='evaluator-clients'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='evaluator-tickets'),

	url(r'^newenquiry/$',views.NewEnquiry.as_view(),name='evaluator-newenquiry'),
	url(r'^existingenquiry/(?P<enquiry_id>[-\w]+)$',views.ExistingEnquiry.as_view(),name='evaluator-existingenquiry'),
	
	url(r'^makeevaluation/(?P<enquiry_id>[-\w]+)$',views.MakeEvaluation.as_view(),name='evaluator-makeevaluation'),
	url(r'^assignevaluator/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.AssignEvaluator.as_view(),name='evaluator-assignevaluator'),
	
	url(r'^makequatation/(?P<enquiry_id>[-\w]+)/$',views.MakeQuatationBase.as_view(),name='evaluator-makequatation'),
	url(r'^makequatation/phase1/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1.as_view(),name='evaluator-makequatation1'),
	url(r'^makequatation/phase2/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2.as_view(),name='evaluator-makequatation2'),

	url(r'^makequatation/assigned/phase1/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeAssignedQuatationPhase1.as_view(),name='evaluator-makeassignedquatation1'),
	url(r'^makequatation/assigned/phase2/(?P<evaluation_detail_id>[-\w]+)$',views.MakeAssignedQuatationPhase2.as_view(),name='evaluator-makeassignedquatation2'),

	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),
]