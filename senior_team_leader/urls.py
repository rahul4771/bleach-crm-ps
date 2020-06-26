from django.conf.urls import include, url
from senior_team_leader import views 

urlpatterns = [

	url(r'^dashboard/$',views.StlHome.as_view(),name='stldash-board'),
	url(r'^tickets/$',views.TicketDetails.as_view(),name='stl-tickets'),
	
	url(r'^assigncleaning/team/(?P<scheduler_id>[-\w]+)/$',views.AssigncleaningTeam.as_view(),name='assign-cleaningteam'),
	url(r'^assignfollowup/team/(?P<scheduler_id>[-\w]+)/$',views.AssignFollowupTeam.as_view(),name='assign-followupteam'),

	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),
]