from django.conf.urls import include, url
from senior_team_leader import views 

urlpatterns = [

	url(r'^dashboard/$',views.StlHome.as_view(),name='stldash-board'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='stl-tickets'),
]