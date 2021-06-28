from django.conf.urls import include, url
from customer import views 

#all users urls

urlpatterns = [

		url(r'^quatation/(?P<evaluation_id>[-\w]+)$',views.Quatation.as_view(),name='quatation'),
		url(r'^subscription/quatation/(?P<evaluation_id>[-\w]+)$',views.SubscriptionQuatation.as_view(),name='subscriptionquatation'),
		url(r'^tc/$',views.TermsandConditions.as_view(),name='tc'),
		url(r'^invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerInvoice.as_view(),name='invoice'),
		url(r'^subscription/invoice/(?P<evaluation_id>[-\w]+)$',views.CustomerSubscriptionInvoice.as_view(),name='subscriptioninvoice'),
		url(r'^booking/invoice/(?P<evaluation_id>[-\w]+)$',views.BleachCustomerInvoice.as_view(),name='bookinginvoice'),

		url(r'^statement-of-account/(?P<client_id>[-\w]+)$',views.statement_of_account,name='statement-of-account'),
		url(r'^statement-of-account-test/$',views.statement_of_account_old,name='statement-of-account-test'),

		url(r'^payment/response/$',views.PaymentResponseDebit.as_view(),name='response'),
		url(r'^payment/receipt/(?P<payment_id>[-\w]+)$',views.PaymentReceipt.as_view(),name='payment-receipt'),
		url(r'^payment/failed/$',views.PaymentFailedResponse.as_view(),name='payment-failed'),

		url(r'^order/details/(?P<order_id>[-\w]+)/(?P<service_id>[-\w]+)/(?P<section_id>[-\w]+)$',views.CustomerOrderDetails.as_view(),name='customer-order-details'),
		url(r'^feedback-page/(?P<order_id>[-\w]+)$',views.CustomerFeedback.as_view(),name='customer-feedback'),

		url(r'^quatation/download/(?P<evaluation_id>[-\w]+)$',views.quatation_html_to_pdf_view,name='quatation-download'),
		url(r'^invoice/download/(?P<evaluation_id>[-\w]+)$',views.invoice_html_to_pdf_view,name='invoice-download'),
		url(r'^payment/receipt/download/(?P<payment_id>[-\w]+)$',views.receipt_html_to_pdf_view,name='payment-receipt-download'),
		url(r'^order-detail/download/(?P<order_id>[-\w]+)/(?P<service_id>[-\w]+)/(?P<section_id>[-\w]+)$',views.orderdetail_html_to_pdf_view,name='order-detail-download'),
		url(r'^terms-and-conditions/download$',views.termsandconditions_to_pdf,name='terms-conditions-download'),

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
		
		url(r'^ajax/getcleaningslotes$',views.GetCleaningSlotes.as_view(),name='ajax-cleaningslotes'),#done not tested
		url(r'^ajax/getmultipleservicecleaningslotes$',views.GetMultipleServiceCleaningSlotes.as_view(),name='ajax-multipleservicecleaningslotes'),#done not tested
		url(r'^ajax/multipleservice/multipledates/cleaningslotes/$',views.GetMultipleServiceDateCleaningSlotes.as_view(),name='ajax-multipleservicedatecleaningslotes'),#done not tested
		url(r'^ajax/multipleservice/multipledates/cleaningslotes/autofix/$',views.GetMultipleServiceDateCleaningSlotesAutofix.as_view(),name='ajax-multipleservicedatecleaningslotes-autofix'),#done not tested
		url(r'^ajax/addressotpsend$',views.AddressOtpSend,name='ajax-addressotpsend'),
		url(r'^ajax/addressotpverify$',views.AddressOtpVerify,name='ajax-addressotpverify'),
		
		#booking cleaning
		url(r'^bookingphase1$',views.ClientCleaningBookingPhase1.as_view(),name='clientcleaningbookingphase1'),
		
		url(r'^bookingmultiplephase2$',views.ClientMultipleCleaningBookingPhase2.as_view(),name='clientcleaningmultiplebookingphase2'),#done not tested
		url(r'^evaluatorbookingmultiplephase2/together/(?P<evaluation_details_id>[-\w]+)/$',views.EvaluatorMultipleCleaningBookingTogetherPhase2.as_view(),name='evaluatorclientcleaningmultiplebookingtogetherphase2'),#done not tested
		url(r'^evaluatorbookingmultiplephase2/customer/(?P<evaluation_details_id>[-\w]+)/$',views.EvaluatorMultipleCleaningBookingLetCustomerPhase2.as_view(),name='evaluatorclientcleaningmultiplebookingcustomerphase2'),#done not tested
		url(r'^duplicatebookingphase2/(?P<evaluation_id>[-\w]+)/$',views.DuplicateBookingPhase2.as_view(),name='duplicatebookingphase2'),#done not tested
		
		url(r'^bookingphase3$',views.ClientCleaningBookingPhase3.as_view(),name='clientcleaningbookingphase3'),
		url(r'^bookingmediasave$',views.ClientCleaningBookingMediaSave.as_view(),name='clientcleaningbookingmediasave'),
		url(r'^evaluatorbookingmultiplephase3/customer/(?P<evaluation_id>[-\w]+)$',views.EvaluatorMultipleCleaningBookingLetCustomerPhase3.as_view(),name='evaluatorclientcleaningmultiplebookingcustomerphase3'),#done not tested

		#edit order
		url(r'^editorder$',views.EditOrderDetails.as_view(),name='edit-order'), 


		url(r'^emailtest$',views.EmailTest.as_view(),name='email-test'),
		url(r'^cart$',views.Cart.as_view(),name='cart'),
	]