from django.conf.urls import include, url
from Api import views 

urlpatterns = [

	url(r'^checkslote/$',views.ApiCheckSlote.as_view(),name='api-checkslote'),
	url(r'^basicdetails/$',views.ApiBasicDetails.as_view(),name='api-basicdetails'),
	url(r'^callback-status-update/$',views.CallbackStatusUpdate.as_view(),name='api-callback-status-update'),
	url(r'^evaluation-booking/$',views.EvaluationBooking.as_view(),name='api-evaluationbooking'),
	url(r'^evaluation-update/$',views.EvaluationUpdate.as_view(),name='api-evaluation-update'),
	url(r'^evaluation-details/(?P<evaluation_detail_id>\d+)/$',views.EvaluationDetailsList.as_view(),name='api-evaluation-details'),
	url(r'^evaluation-cancel/(?P<evaluation_detail_id>\d+)/$',views.CancelEvaluation.as_view(),name='api-evaluation-cancel'),
	
	url(r'^leave-users-list/$',views.LeaveUsersList.as_view(),name='api-leave-users-list'),
	url(r'^leave-scheduler/$',views.LeaveScheduleAPI.as_view(),name='api-leaveschedule'),
	url(r'^leave-scheduler-delete/(?P<leave_id>\d+)/$',views.DeleteLeaveSchedule.as_view(),name='api-leaveschedule-delete'),

	url(r'^booking-expiry/$',views.BookingExpiryAPI.as_view(),name='api-booking-expiry'),

	url(r'^discount-settings/$',views.DiscountSettingsAPI.as_view(),name='api-discount-settings'),

	url(r'^section-verification-updation/$',views.SectionVerificationUpdationAPI.as_view(),name='api-section-verification-updation'),
	url(r'^resource-skills/$',views.ResourceSkillsAPI.as_view(),name='api-resource-skills'),

	url(r'^soa-mail/$',views.SOAMailAPI.as_view(),name='api-soa-mail'),
	url(r'^invoice-mail-sms/$',views.InvoiceSMSMailAPI.as_view(),name='api-invoice-mail'),

	url(r'^shift-scheduler/$',views.ShiftScheduleAPI.as_view(),name='api-shiftschedule'),
	url(r'^shift-scheduler-delete/(?P<shift_id>\d+)/$',views.DeleteShiftSchedule.as_view(),name='api-shiftschedule-delete'),

	url(r'^payment/response/credit/$',views.PaymentResponseCredit.as_view(),name='api-responsecredit'),
	url(r'^daily-sales-list/$',views.DailySalesAPI.as_view(),name='api-daily-sales'),
	url(r'^daily-sales-breakdown-list/$',views.DailySalesBreakDownAPI.as_view(),name='api-daily-sales-breakdown'),
	url(r'^daily-sales-chart/$',views.DailySalesChartAPI.as_view(),name='api-daily-sales-chart'),
	url(r'^payment-policy-edit/$',views.PaymentPolicyEditAPI.as_view(),name='api-payment-policy-edit'),
	url(r'^cleaning-team-data/$',views.CleaningTeamAPI.as_view(),name='api-cleaning-team-data'),

	#inventory
	url(r'^inventory-lines/$',views.InventoryLinesAPI.as_view(),name='api-inventory-lines'),
	url(r'^inventory-segments/$',views.InventorySegmentsAPI.as_view(),name='api-inventory-segments'),
	url(r'^inventory-values/$',views.InventoryValuesAPI.as_view(),name='api-inventory-values'),
	url(r'^inventory-items/$',views.InventoryItemsAPI.as_view(),name='api-inventory-items'),
	url(r'^inventory-supplier-items/$',views.InventorySupplierItemsAPI.as_view(),name='api-inventory-supplier-items'),
	url(r'^inventory-bundle-items/$',views.InventoryBundleItemsAPI.as_view(),name='api-inventory-bundle-items'),
	url(r'^inventory-service-items/$',views.InventoryServiceRecipeAPI.as_view(),name='api-inventory-service-items'),
	url(r'^inventory-service-area/$',views.InventoryServiceAreaAPI.as_view(),name='api-inventory-service-area'),

	###Team Leader Mobile app API'S
	url(r'^login/$',views.LoginAPI.as_view(),name='api-login'),
	url(r'^tl/home/$',views.TlHomeAPI.as_view(),name='api-stlhome'),
	
	url(r'^tl/cleanings/$',views.TlCleanings.as_view(),name='api-stlcleanings'),
	
	url(r'^tl/cleaning/details/(?P<team_id>\d+)/$',views.TlCleaningDetails.as_view(),name='api-cleaningdetails'),
	url(r'^check-in/$',views.CheckInAPI.as_view(),name='api-check-in'),
	url(r'^check-out/$',views.CheckOutAPI.as_view(),name='api-check-out'),

	url(r'^tl/followupcleaning/details/(?P<team_id>\d+)/$',views.TlFollowupCleaningDetails.as_view(),name='api-followupdetails'),
	url(r'^tl/followupcleaning/checkin/$',views.TlFollowupCleaningCheckin.as_view(),name='api-followupcheckin'),
	url(r'^tl/followupcleaning/checkout/$',views.TlFollowupCleaningCheckout.as_view(),name='api-followupcheckout'),

	url(r'^check-in/checklist/$',views.CheckinChecklist.as_view(),name='api-check-in'),
]
