from django.conf.urls import include, url
from qualitycontroll import views 

urlpatterns = [
	url(r'^dashboard/$',views.QcHome.as_view(),name='qcdash-board'),

	url(r'^investigation/(?P<investigation_id>[-\w]+)/$',views.InvestigationTask.as_view(),name='investigation'),

    url(r'^followup/(?P<investigation_id>[-\w]+)/$',views.Followup.as_view(),name='follow-up'),
    url(r'^cashback/(?P<investigation_id>[-\w]+)/$',views.Cashback.as_view(),name='cash-back'),
    url(r'^buyback-promocode/(?P<investigation_id>[-\w]+)/$',views.BuyBackPromoCode.as_view(),name='buy-back-promo-code'),

    url(r'^internal-report/(?P<investigation_id>[-\w]+)/$',views.InternalReport.as_view(),name='internal-report'),
]


