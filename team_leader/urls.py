from django.conf.urls import include, url
from team_leader import views 

urlpatterns = [

	url(r'^dashboard/$',views.TlHome.as_view(),name='tldash-board'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='tl-tickets'),
]