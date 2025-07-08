from django.conf.urls import include, url
from team_leader import views 

app_name = 'team_leader'


urlpatterns = [

	url(r'^dashboard/$',views.TlHome.as_view(),name='tldash-board'),

	url(r'^tickets/$',views.TicketDetails.as_view(),name='tl-tickets'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='tl-ticketadvanced'),
	url(r'^items/$',views.ItemsList.as_view(),name='tl-items'),
	url(r'^cleaning/(?P<team_id>[-\w]+)/$',views.Cleaning.as_view(),name='cleaning'),
	url(r'^followupcleaning/(?P<team_id>[-\w]+)/$',views.FollowupCleaning.as_view(),name='followupcleaning'),

	url(r'^ajax/keynote/status/$',views.UpdateKeynoteStatus,name='ajax-updatekeynote'),
]