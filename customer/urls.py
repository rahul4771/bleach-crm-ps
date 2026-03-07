from django.conf.urls import include, url
from customer import views 

app_name = 'customer'


#all users urls

urlpatterns = [

		url(r'^quatation/(?P<evaluation_id>[-\w]+)$',views.Quatation.as_view(),name='quatation'),
		url(r'^subscription/quatation/(?P<evaluation_id>[-\w]+)$',views.SubscriptionQuatation.as_view(),name='subscriptionquatation'),
		url(r'^tc/$',views.TermsandConditions.as_view(),name='tc'),
		url(r'^invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerInvoice.as_view(),name='invoice'),
		url(r'^subscription/invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerSubscriptionInvoice.as_view(),name='subscriptioninvoice'),
		url(r'^booking/invoice/(?P<evaluation_id>[-\w]+)$',views.BleachCustomerInvoice.as_view(),name='bookinginvoice'),

		url(r'^statement-of-account/(?P<client_id>[-\w]+)$',views.statement_of_account,name='statement-of-account'),

		url(r'^payment/response/$',views.PaymentResponseDebit.as_view(),name='response'),
		url(r'^payment/receipt/(?P<payment_id>[-\w]+)$',views.PaymentReceipt.as_view(),name='payment-receipt'),
		url(r'^payment/failed/$',views.PaymentFailedResponse.as_view(),name='payment-failed'),

		url(r'^order/details/(?P<order_id>[-\w]+)/(?P<service_id>[-\w]+)/(?P<section_id>[-\w]+)$',views.CustomerOrderDetails.as_view(),name='customer-order-details'),
		url(r'^feedback-page/(?P<order_id>[-\w]+)$',views.CustomerFeedback.as_view(),name='customer-feedback'),

		url(r'^quatation/download/(?P<evaluation_id>[-\w]+)$',views.quatation_html_to_pdf_view,name='quatation-download'),
		url(r'^quatation/download-pdf/(?P<evaluation_id>[-\w]+)$',views.download_quatation_as_pdf,name='quatation-download-pdf'),
		url(r'^purchaseorder/download/(?P<purchase_order_id>[-\w]+)$',views.purchaseorder_html_to_pdf_view,name='purchaseorder-download'),
		url(r'^requestorder/download/(?P<request_order_id>[-\w]+)$',views.requestorder_html_to_pdf_view,name='requestorder-download'),
		url(r'^invoice/download/(?P<evaluation_id>[-\w]+)$',views.invoice_html_to_pdf_view,name='invoice-download'),
		url(r'^payment/receipt/download/(?P<payment_id>[-\w]+)$',views.receipt_html_to_pdf_view,name='payment-receipt-download'),
		url(r'^order-detail/download/(?P<order_id>[-\w]+)/(?P<service_id>[-\w]+)/(?P<section_id>[-\w]+)$',views.orderdetail_html_to_pdf_view,name='order-detail-download'),
		url(r'^terms-and-conditions/download$',views.termsandconditions_to_pdf,name='terms-conditions-download'),
		url(r'^stock-out/download/(?P<visit_id>[-\w]+)/$',views.stockout,name='stockout-download'),
		url(r'^customer-evaluation-booking/download/(?P<booking_id>[-\w]+)$',views.customer_booking_html_to_pdf_view,name='customer-evaluation-booking-download'),
		url(r'^edit-customer/$',views.EditCustomerProfile.as_view(),name='edit-customer'),
		url(r'^add-promocode/$',views.addpromocode,name='add-promocode'),

		##actual evaluation booking related urls
		url(r'^ajax/evaluationslotes$',views.GetEvaluationBookingSlotes.as_view(),name='ajax-getevaluationslotes'),
		url(r'^booking/evaluation/phase1$',views.CustomerBookingPhase1.as_view(),name='customerbookingphase1'),
		url(r'^booking/evaluation/phase2$',views.CustomerBookingEvaluationPhase2.as_view(),name='customerbookingevaluationphase2'),
		url(r'^booking/evaluation/phase3$',views.CustomerBookingEvaluationPhase3.as_view(),name='customerbookingevaluationphase3'),

		##actual cleaning booking related urls
		url(r'^ajax/countries$',views.GetCountries.as_view(),name='ajax-countries'),
		url(r'^ajax/mobilecheck$',views.ExistingMobileCheck.as_view(),name='ajax-checkmobile'),
		url(r'^ajax/getgovernorates$',views.GetGovernorates.as_view(),name='ajax-governorates'),
		url(r'^ajax/getareas$',views.GetAreas.as_view(),name='ajax-areas'),
		url(r'^ajax/getservicetypes$',views.GetServiceTypes.as_view(),name='ajax-servicetypes'),
		url(r'^ajax/getareatypes$',views.GetAreaTypes.as_view(),name='ajax-getareatypes'),
		url(r'^ajax/getservicesizeprice$',views.GetServiceSizePrice.as_view(),name='ajax-getservicesizeprice'),
		url(r'^ajax/getserviceproductivity$',views.GetServiceProductivity.as_view(),name='ajax-serviceproductivity'),
		url(r'^ajax/getstagingserviceproductivity$',views.GetStagingServiceProductivity.as_view(),name='ajax-staging-serviceproductivity'),
		url(r'^ajax/getserviceaddons$',views.GetServiceAddOns.as_view(),name='ajax-serviceaddons'),
		
		url(r'^ajax/getmultipleservicecleaningslotes$',views.GetMultipleServiceCleaningSlotes.as_view(),name='ajax-multipleservicecleaningslotes'),#New logic applied latest 8 to 22 logic
		url(r'^ajax/multipleservice/multipledates/cleaningslotes/$',views.GetMultipleServiceDateCleaningSlotes.as_view(),name='ajax-multipleservicedatecleaningslotes'),#New logic applied 8 to 22 logic
		url(r'^ajax/multipleservice/multipledates/cleaningslotes/autofix/$',views.GetMultipleServiceDateCleaningSlotesAutofix.as_view(),name='ajax-multipleservicedatecleaningslotes-autofix'),#New logic applied 8 t0 22 logic 
		url(r'^availablecleaners/$',views.GetAvailableCleaners.as_view(),name='available-cleaners'),#New logic applied 8 t0 22 logic
		
		url(r'^subscription/slotes/$',views.GetSubscriptionSlotes.as_view(),name='subscription-slotes'),
		url(r'^availablecleaners/group/subscription/$',views.GetAvailableCleanersGroupSubscription.as_view(),name='available-cleaners-group-subscription'),#New logic applied 8 t0 22 logic
		url(r'^group/subscription/save/$',views.GroupSubscriptionSave.as_view(),name='group-subscription-save'),#New logic applied 8 t0 22 logic 
		
		url(r'^ajax/addressotpsend$',views.AddressOtpSend,name='ajax-addressotpsend'),
		url(r'^ajax/addressotpverify$',views.AddressOtpVerify,name='ajax-addressotpverify'),

		
		#booking cleaning
		url(r'^bookingphase1$',views.ClientCleaningBookingPhase1.as_view(),name='clientcleaningbookingphase1'),
		
		url(r'^bookingmultiplephase2$',views.ClientMultipleCleaningBookingPhase2.as_view(),name='clientcleaningmultiplebookingphase2'),#New Logic Applied atomic applied 8 to 22 logic applied 8 to 22 logic applied
		url(r'^evaluatorbookingmultiplephase2/together/(?P<evaluation_details_id>[-\w]+)/$',views.EvaluatorMultipleCleaningBookingTogetherPhase2.as_view(),name='evaluatorclientcleaningmultiplebookingtogetherphase2'),#New Logic Applied atomic applied 8 to 22 logic applied
		url(r'^evaluatorbookingmultiplephase2/customer/(?P<evaluation_details_id>[-\w]+)/$',views.EvaluatorMultipleCleaningBookingLetCustomerPhase2.as_view(),name='evaluatorclientcleaningmultiplebookingcustomerphase2'), #atomic applied
		url(r'^duplicatebookingphase2/(?P<evaluation_id>[-\w]+)/$',views.DuplicateBookingPhase2.as_view(),name='duplicatebookingphase2'),#New Logic Applied atomic applied 8 to 22 logic applied
		
		url(r'^bookingphase3$',views.ClientCleaningBookingPhase3.as_view(),name='clientcleaningbookingphase3'),
		url(r'^bookingmediasave$',views.ClientCleaningBookingMediaSave.as_view(),name='clientcleaningbookingmediasave'),
		url(r'^evaluatorbookingmultiplephase3/customer/(?P<evaluation_id>[-\w]+)$',views.EvaluatorMultipleCleaningBookingLetCustomerPhase3.as_view(),name='evaluatorclientcleaningmultiplebookingcustomerphase3'),#New Logic Applied atomic applied 8 to 22 logic applied

		#order edits
		url(r'^service/add-delete/(?P<evaluation_details_id>[-\w]+)$',views.AddDeleteService.as_view(),name='add-delete-service'),
		url(r'^editorder/(?P<order_id>[-\w]+)$',views.EditOrderDetails.as_view(),name='edit-order'),
		url(r'^service/cancellrequest/$',views.ServiceCancellationRequest.as_view(),name='cancell-service'),
		url(r'^service/cancell/$',views.ServiceCancellation.as_view(),name='cancell-service-submit'),
		url(r'^resubmitorder/(?P<order_id>[-\w]+)$',views.ReSubmitOrder.as_view(),name='resubmit-order'),

		url(r'^emailtest$',views.EmailTest.as_view(),name='email-test'),
		# url(r'^cart$',views.Cart.as_view(),name='cart'),
		
		#website APIs
		url(r'^find-dates/$',views.FindDates.as_view(),name='find-dates'),
		url(r'^cart/(?P<token>\w+)/$',views.CartAPI.as_view(),name='customer-cart'),
		url(r'^cart/schedule/(?P<token>\w+)/$',views.CartScheduleAPI.as_view(),name='customer-cart-schedule'),
        url(r'^add-user-email/$', views.UserEmailView.as_view(), name='add-user-email')
	]