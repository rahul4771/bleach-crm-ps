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
	
	url(r'^leave-users-list/$',views.UsersList.as_view(),name='api-leave-users-list'),

	url(r'^order-details/(?P<order_id>\d+)/$',views.OrderDetailsAPI.as_view(),name='api-order-details'),
	url(r'^visit-details/(?P<visit_id>\d+)/$',views.VisitDetailsAPI.as_view(),name='api-visit-details'),
	url(r'^ticket-details/(?P<ticket_id>\d+)/$',views.TicketDetailsAPI.as_view(),name='api-ticket-details'),
	url(r'^ticket-edit/$',views.TicketEditAPI.as_view(),name='api-ticket-edit'),
	url(r'^ticket-submit/$',views.TicketSubmitAPI.as_view(),name='api-ticket-submit'),
	url(r'^investigation-form/$',views.InvestigationFormAPI.as_view(),name='api-investigation-form'),
	url(r'^agent-investigation-check/$',views.AgentInvestigationChecckAPI.as_view(),name='api-investigation-check'),

	url(r'^items-collect/$',views.ItemCollectAPI.as_view(),name='api-items-collect'),
	url(r'^leave-scheduler/$',views.LeaveScheduleAPI.as_view(),name='api-leaveschedule'),
	url(r'^leave-scheduler/popup/$',views.LeaveSchedulePopupAPI.as_view(),name='api-leaveschedulepopup'),
	url(r'^leave-scheduler-delete/(?P<leave_id>\d+)/$',views.DeleteLeaveSchedule.as_view(),name='api-leaveschedule-delete'),
	url(r'^shift-scheduler/$',views.ShiftScheduleAPI.as_view(),name='api-shiftschedule'),
	url(r'^shift-scheduler-delete/(?P<shift_id>\d+)/$',views.DeleteShiftSchedule.as_view(),name='api-shiftschedule-delete'),

	url(r'^booking-expiry-check/$',views.BookingExpiryCheckAPI.as_view(),name='api-booking-expiry-check'),
	url(r'^booking-expiry/$',views.BookingExpiryAPI.as_view(),name='api-booking-expiry'),

	url(r'^discount-settings/$',views.DiscountSettingsAPI.as_view(),name='api-discount-settings'),

	url(r'^section-verification-updation/$',views.SectionVerificationUpdationAPI.as_view(),name='api-section-verification-updation'),
	url(r'^resource-skills/$',views.ResourceSkillsAPI.as_view(),name='api-resource-skills'),

	url(r'^soa-mail/$',views.SOAMailAPI.as_view(),name='api-soa-mail'),
	url(r'^invoice-mail-sms/$',views.InvoiceSMSMailAPI.as_view(),name='api-invoice-mail'),

	url(r'^payment/response/credit/$',views.PaymentResponseCredit.as_view(),name='api-responsecredit'),
	url(r'^daily-sales-list/$',views.DailySalesAPI.as_view(),name='api-daily-sales'),
	url(r'^daily-sales-breakdown-list/$',views.DailySalesBreakDownAPI.as_view(),name='api-daily-sales-breakdown'),
	url(r'^daily-sales-chart/$',views.DailySalesChartAPI.as_view(),name='api-daily-sales-chart'),
	url(r'^payment-policy-edit/$',views.PaymentPolicyEditAPI.as_view(),name='api-payment-policy-edit'),
	url(r'^cleaning-team-data/$',views.CleaningTeamAPI.as_view(),name='api-cleaning-team-data'),
	# url(r'^cleaning-export/$',views.CleaningsExport.as_view(),name='api-cleaning-export'),

	#inventory
	url(r'^inventory-lines/$',views.InventoryLinesAPI.as_view(),name='api-inventory-lines'),
	url(r'^inventory-segments/$',views.InventorySegmentsAPI.as_view(),name='api-inventory-segments'),
	url(r'^inventory-values/$',views.InventoryValuesAPI.as_view(),name='api-inventory-values'),
	url(r'^inventory-items/$',views.InventoryItemsAPI.as_view(),name='api-inventory-items'),
	url(r'^inventory-supplier-items/$',views.InventorySupplierItemsAPI.as_view(),name='api-inventory-supplier-items'),
	url(r'^inventory-bundle-items/$',views.InventoryBundleItemsAPI.as_view(),name='api-inventory-bundle-items'),
	url(r'^inventory-service-ingredients/$',views.InventoryServiceRecipeAPI.as_view(),name='api-inventory-service-ingredients'),
	url(r'^inventory-service-area/$',views.InventoryServiceAreaAPI.as_view(),name='api-inventory-service-area'),
	url(r'^inventory-service-items/$',views.InventoryServiceItemsAPI.as_view(),name='api-inventory-service-items'),
	url(r'^inventory-item-quantity-check/$',views.ItemQuantityCheck.as_view(),name='api-inventory-item-quantity-check'),

	###Team Leader Mobile app API'S
	url(r'^login/$',views.LoginAPI.as_view(),name='api-login'),
	url(r'^tl/home/$',views.TlHomeAPI.as_view(),name='api-stlhome'),
	
	url(r'^tl/cleanings/$',views.TlCleanings.as_view(),name='api-stlcleanings'),
	
	url(r'^tl/cleaning/details/(?P<team_id>\d+)/$',views.TlCleaningDetails.as_view(),name='api-cleaningdetails'),
	url(r'^check-in/$',views.CheckInAPI.as_view(),name='api-check-in'),
	url(r'^backup-check-in/$',views.BackupCheckInAPI.as_view(),name='api-backupcheck-in'),
	url(r'^check-out/$',views.CheckOutAPI.as_view(),name='api-check-out'),

	url(r'^tl/followupcleaning/details/(?P<team_id>\d+)/$',views.TlFollowupCleaningDetails.as_view(),name='api-followupdetails'),
	url(r'^tl/followupcleaning/checkin/$',views.TlFollowupCleaningCheckin.as_view(),name='api-followupcheckin'),
	url(r'^tl/followupcleaning/checkout/$',views.TlFollowupCleaningCheckout.as_view(),name='api-followupcheckout'),

	url(r'^check-in/checklist/$',views.CheckinChecklist.as_view(),name='api-check-in'),

	###Team members swap
	url(r'^team/search/$',views.TeamSerachAPI.as_view(),name='api-team-search'),
	url(r'^team/swapcheck/$',views.TeamSwapCheckAPI.as_view(),name='api-swap-check'),
	url(r'^team/swap/$',views.TeamSwapAPI.as_view(),name='api-swap'),
]
