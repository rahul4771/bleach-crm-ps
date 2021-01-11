from django.conf.urls import include, url
from qualitycontroll import views 

urlpatterns = [

	url(r'^investigation/$',views.investigation,name='investigation'),
    url(r'^followup/$',views.Followup.as_view(),name='follow-up'),
    url(r'^cashback/$',views.Cashback.as_view(),name='cash-back'),

]