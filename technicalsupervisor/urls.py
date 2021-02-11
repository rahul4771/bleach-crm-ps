from django.conf.urls import include, url
from technicalsupervisor import views 

urlpatterns = [

	url(r'^dashboard/$',views.TechnicalSupervisorHome.as_view(),name='tech-supervisor-dash-board'),
	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),

]