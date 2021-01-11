from django.conf.urls import include, url
from qualitycontroll import views 

urlpatterns = [

	url(r'^dashboard/$',views.QcHome.as_view(),name='qcdash-board'),

	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),

	]