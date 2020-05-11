from django.conf.urls import include, url
from agent import views 

urlpatterns = [

	url(r'^dashboard/$',views.AgentHome.as_view(),name='agentdash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),

]