from django.conf.urls import include, url
from qualitycontroll import views 

urlpatterns = [
	url(r'^dashboard/$',views.QcHome.as_view(),name='qcdash-board'),

	url(r'^orders/$',views.OrderDetails.as_view(),name='qc-orders'),
	url(r'^order-details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='qc-order-details'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='qc-client-orders'),

	url(r'^tickets/$',views.TicketDetails.as_view(),name='qc-tickets'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='qc-ticketadvanced'),

	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),

    url(r'^followup/(?P<investigation_id>[-\w]+)/$',views.Followup.as_view(),name='follow-up'),
    url(r'^cashback/(?P<investigation_id>[-\w]+)/$',views.Cashback.as_view(),name='cash-back'),
	url(r'^cashback-edit/(?P<investigation_id>[-\w]+)/$',views.CashbackEdit.as_view(),name='cash-back-edit'),
	url(r'^buyback-promocode/(?P<investigation_id>[-\w]+)/$',views.BuyBackPromoCode.as_view(),name='buy-back-promo-code'),
    url(r'^buyback-promocode-edit/(?P<investigation_id>[-\w]+)/$',views.BuyBackPromoCodeEdit.as_view(),name='buy-back-promo-code-edit'),

    url(r'^internal-report/(?P<investigation_id>[-\w]+)/$',views.InternalReport.as_view(),name='internal-report'),
	url(r'^internal-report-edit/(?P<investigation_id>[-\w]+)/$',views.InternalReportEdit.as_view(),name='internal-report-edit'),
]


