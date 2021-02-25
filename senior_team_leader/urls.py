from django.conf.urls import include, url
from senior_team_leader import views 

urlpatterns = [

	url(r'^dashboard/$',views.StlHome.as_view(),name='stldash-board'),
	url(r'^active-subscriptions/$',views.ActiveSubscriptions.as_view(),name='stl-active-subscriptions'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='stl-orders'),
	url(r'^order-details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='stl-order-details'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='stl-client-orders'),

	url(r'^tickets/$',views.TicketDetails.as_view(),name='stl-tickets'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='stl-ticketadvanced'),
	
	url(r'^assigncleaning/team/(?P<scheduler_id>[-\w]+)/$',views.AssigncleaningTeam.as_view(),name='assign-cleaningteam'),
	url(r'^assignfollowup/team/(?P<scheduler_id>[-\w]+)/$',views.AssignFollowupTeam.as_view(),name='assign-followupteam'),
	url(r'^leave-scheduler/$',views.LeaveScheduler.as_view(),name='stl-leave-scheduler'),
	
	url(r'^ajax/cleaning/info$',views.GetCleaningInfo,name='ajax-getcleaninginfo'),
	url(r'^ajax/followup/info$',views.GetFollowupInfo,name='ajax-getfollowupinfo'),
]