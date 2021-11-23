from django.conf.urls import include, url
from senior_team_leader import views 

urlpatterns = [

	url(r'^dashboard/$',views.StlHome.as_view(),name='stldash-board'),
	url(r'^active-subscriptions/$',views.ActiveSubscriptions.as_view(),name='stl-active-subscriptions'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='stl-orders'),
	url(r'^order-details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='stl-order-details'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='stl-client-orders'),
	url(r'^cleaning-export/$',views.CleaningsExport.as_view(),name='cleaning-export'),

	#qualitycontrol
	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),
	# url(r'^newinvestigation/(?P<investigation_id>[-\w]+)/$',views.NewInvestigationTask.as_view(),name='newinvestigation'),


    url(r'^ajax/removefollowupsection/',views.RemoveFollowupSection,name='removefollowupbooksection'),
	url(r'^followup/(?P<investigation_id>[-\w]+)/$',views.Followup.as_view(),name='follow-up'),
	url(r'^followup-edit/(?P<investigation_id>[-\w]+)/$',views.FollowupEdit.as_view(),name='follow-up-edit'),
	url(r'^followup-delete/(?P<investigation_id>[-\w]+)/$',views.FollowupDelete.as_view(),name='follow-up-delete'),
    
	url(r'^cashback/(?P<investigation_id>[-\w]+)/$',views.Cashback.as_view(),name='cash-back'),
	url(r'^cashback-edit/(?P<investigation_id>[-\w]+)/$',views.CashbackEdit.as_view(),name='cash-back-edit'),
	url(r'^cashback-delete/(?P<investigation_id>[-\w]+)/$',views.CashbackDelete.as_view(),name='cash-back-delete'),

	url(r'^buyback-promocode/(?P<investigation_id>[-\w]+)/$',views.BuyBackPromoCode.as_view(),name='buy-back-promo-code'),
    url(r'^buyback-promocode-edit/(?P<investigation_id>[-\w]+)/$',views.BuyBackPromoCodeEdit.as_view(),name='buy-back-promo-code-edit'),
	url(r'^buyback-promocode-delete/(?P<investigation_id>[-\w]+)/$',views.BuyBackPromoCodeDelete.as_view(),name='buy-back-promo-code-delete'),

    url(r'^internal-report/(?P<investigation_id>[-\w]+)/$',views.InternalReport.as_view(),name='internal-report'),
	url(r'^internal-report-edit/(?P<investigation_id>[-\w]+)/$',views.InternalReportEdit.as_view(),name='internal-report-edit'),
	url(r'^internal-report-delete/(?P<investigation_id>[-\w]+)/$',views.InternalReportDelete.as_view(),name='internal-report-delete'),

	
	
	url(r'^tickets/$',views.TicketDetails.as_view(),name='stl-tickets'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='stl-ticketadvanced'),

	url(r'^leave-scheduler/$',views.LeaveScheduler.as_view(),name='stl-leave-scheduler'),
	
	url(r'^ajax/cleaning/info$',views.GetCleaningInfo,name='ajax-getcleaninginfo'),
	url(r'^ajax/followup/info$',views.GetFollowupInfo,name='ajax-getfollowupinfo'),
]