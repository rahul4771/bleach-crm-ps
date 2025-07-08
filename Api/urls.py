from django.conf.urls import include, url
from Api import views 

app_name = 'api'


urlpatterns = [

	url(r'countries/$',views.CountriesAPI.as_view(),name='countries'),

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
	url(r'^items-check-in/$',views.ItemsCheckInAPI.as_view(),name='api-items-check-in'),
	url(r'^leave-scheduler/$',views.LeaveScheduleAPI.as_view(),name='api-leaveschedule'),
	url(r'^leave-update-bamboo-crm/$',views.UpdateCRMBambooLeavesAPI.as_view(),name='api-leave-update-bamboo-crm'),
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
	url(r'^website-inquiry-mail/$',views.WebsiteInquiryMailAPI.as_view(),name='api-website-inquiry-mail'),

	#smstest
	url(r'^sms-test/$',views.SmstestAPI.as_view(),name='api-sms-test'),

	url(r'^payment/response/credit/$',views.PaymentResponseCredit.as_view(),name='api-responsecredit'),
	url(r'^daily-sales-list/$',views.DailySalesAPI.as_view(),name='api-daily-sales'),
	url(r'^daily-sales-breakdown-list/$',views.DailySalesBreakDownAPI.as_view(),name='api-daily-sales-breakdown'),
	url(r'^daily-sales-chart/$',views.DailySalesChartAPI.as_view(),name='api-daily-sales-chart'),
	url(r'^payment-policy-edit/$',views.PaymentPolicyEditAPI.as_view(),name='api-payment-policy-edit'),
	url(r'^cleaning-team-data/$',views.CleaningTeamAPI.as_view(),name='api-cleaning-team-data'),
	url(r'^service-productivity/$',views.ServiceProductivityAPI.as_view(),name='api-service-productivity'),
	
	#website APIS
	url(r'^service-price-ranges/(?P<cleaning_type>\D+)/$',views.ServicePriceRangeAPI.as_view(),name='api-service-price-ranges'),
	url(r'^service-add-ons/(?P<cleaning_type>\D+)/$',views.ServiceAddOnsAPI.as_view(),name='api-service-add-ons'),
	url(r'^customer-addresses/(?P<token>\w+)/$',views.CustomerAddressesAPI.as_view(),name='api-customer-addresses'),
	url(r'^customer-details/(?P<token>\w+)/$',views.CustomerDetailsAPI.as_view(),name='api-customer-details'),
	url(r'^customer-evaluations/(?P<token>\w+)/$',views.CustomerBookedEvaluationsAPI.as_view(),name='api-customer-evaluations'),
	url(r'^customer-orders/(?P<token>\w+)/$',views.CustomerBookedOrdersAPI.as_view(),name='api-customer-orders'),
	url(r'^customer-order-details/(?P<order_id>\d+)/$',views.CustomerBookedOrderDetailsAPI.as_view(),name='api-customer-order-details'),
	url(r'^governorates/$',views.GovernoratesAPI.as_view(),name='api-governorates'),
	url(r'^areas/(?P<governorate_id>\d+)/$',views.AreasAPI.as_view(),name='api-areas'),
	url(r'^location-types/$',views.LocationTypesAPI.as_view(),name='api-location-types'),
	url(r'^mail-subscription/$',views.SubscriptionMailAPI.as_view(),name='api-mail-subscription'),

	#inventory
	url(r'^inventory-lines/$',views.InventoryLinesAPI.as_view(),name='api-inventory-lines'),
	url(r'^inventory-segments/$',views.InventorySegmentsAPI.as_view(),name='api-inventory-segments'),
	url(r'^inventory-values/$',views.InventoryValuesAPI.as_view(),name='api-inventory-values'),
	url(r'^inventory-items/$',views.InventoryItemsAPI.as_view(),name='api-inventory-items'),
	# url(r'^inventory-attribute-values/$',views.InventoryAttributeValuesAPI.as_view(),name='api-inventory-attribute-values'),
	url(r'^inventory-supplier-items/$',views.InventorySupplierItemsAPI.as_view(),name='api-inventory-supplier-items'),
	url(r'^inventory-items-list/$',views.InventoryItemsListAPI.as_view(),name='api-inventory--items-list'),
	url(r'^inventory-bundle-items/$',views.InventoryBundleItemsAPI.as_view(),name='api-inventory-bundle-items'),
	url(r'^inventory-service-ingredients/$',views.InventoryServiceRecipeAPI.as_view(),name='api-inventory-service-ingredients'),
	url(r'^inventory-service-area/$',views.InventoryServiceAreaAPI.as_view(),name='api-inventory-service-area'),
	url(r'^inventory-service-items/$',views.InventoryServiceItemsAPI.as_view(),name='api-inventory-service-items'),
	url(r'^inventory-item-quantity-check/$',views.ItemQuantityCheck.as_view(),name='api-inventory-item-quantity-check'),
	url(r'^inventory-checkout-item-add/$',views.CheckOutItemAdd.as_view(),name='api-inventory-checkout-item-add'),
	url(r'^inventory-checkout-item-edit/$',views.CheckOutItemEdit.as_view(),name='api-inventory-checkout-item-edit'),
	url(r'^inventory-checkout-item-delete/$',views.CheckOutItemDelete.as_view(),name='api-inventory-checkout-item-delete'),
	url(r'^inventory-checkout-item-swap/$',views.CheckOutItemSwap.as_view(),name='api-inventory-checkout-item-swap'),
	url(r'^inventory-checkout-item-units/$',views.CheckOutItemUnitsList.as_view(),name='api-inventory-checkout-item-units'),
	url(r'^inventory-checkout-item-unit-swap/$',views.CheckOutItemUnitSwap.as_view(),name='api-inventory-checkout-item-unit-swap'),
	url(r'^rawmaterials/(?P<inventory_id>\d+)/$',views.InventoryRawMaterialsView.as_view(),name='api-rawmaterial'),
	url(r'^accessory/(?P<inventory_id>\d+)/$',views.InventoryAccessoryView.as_view(),name='api-accessory'),
	url(r'^finished_item/(?P<inventory_id>\d+)/$',views.InventoryFinshedItemView.as_view(),name='api-finished_item'),
	url(r'^external_customers/$',views.ExternalCustomersView.as_view(),name='api-external-customers'),
	url(r'^item_units/$',views.ItemUnitsProduct.as_view(),name='api-item-units'),
	url(r'^item_stores/$',views.ItemStores.as_view(),name='api-item-stores'),
	
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

	url(r'^xero/save/$',views.XeroInfoSaveAPI.as_view(),name='xero-save'),
	url(r'^transactions/daily/$',views.DailyTransactionsAPI.as_view(),name='daily-transactions'),

	###evaluation booking apis
	url(r'^evaluation-booking-customer-otp-generation/$',views.EvaluationBookingCustomerOtpGenerationAPI.as_view(),name='evaluation-booking-customer-otp-generation'),
	url(r'^evaluation-booking-customer-otp-verification/$',views.EvaluationBookingCustomerOtpVerificationAPI.as_view(),name='evaluation-booking-customer-otp-verification'),
	url(r'^evaluation-booking-slots/$',views.GetEvaluationBookingSlots.as_view(),name='evaluation-booking-slots'),
	url(r'^evaluation-booking-submit/$',views.EvaluationBookingAPI.as_view(),name='evaluation-booking-api'),
	url(r'^download-pdf-file/$', views.DownloadFile.as_view(), name='download-pdf-file'),

]
