from django.conf.urls import include, url
from agent import views 

urlpatterns = [

	url(r'^cleaningcallendar/$',views.CleaningCallendar.as_view(),name='cleaning-callendar'),
	url(r'^cleaningcallendar/availability/$',views.AvailabilityCleaningCallendar.as_view(),name='cleaning-callendar-availability'),#done
	url(r'^cleaningcallendar/cleaning/popup/$',views.CleaningCallendarCleaningPopup.as_view(),name='cleaning-callendar-cleaningpopup'),
	url(r'^cleaningcallendar/cleaning/edit/slotes/$',views.CleaningPopupMultipleServiceCleaningSlotes.as_view(),name='cleaning-callendar-cleaningedit-slotes'),#done
	url(r'^cleaningcallendar/cleaning/edit/save/$',views.CleaningPopupSave.as_view(),name='cleaning-callendar-cleaningedit-save'),#done
	url(r'^cleaningcallendar/followupcleaning/popup/$',views.CleaningCallendarFollowupPopup.as_view(),name='cleaning-callendar-followupcleaningpopup'),
	url(r'^cleaningcallendar/followup/edit/save/$',views.FollowupPopupSave.as_view(),name='cleaning-callendar-followupedit-save'),

	url(r'^dashboard/$',views.AgentHome.as_view(),name='agentdash-board'),
	url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
	url(r'^orders/$',views.OrderDetails.as_view(),name='agent-orders'),
	url(r'^customer-bookings/$',views.CustomerBookingsList.as_view(),name='agent-customer-bookings'),

	url(r'^payment-policy/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.PaymentEdit.as_view(),name='agent-payment-edit'),
	url(r'^active-subscriptions/$',views.ActiveSubscriptions.as_view(),name='agent-active-subscriptions'),
	
	url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='agent-feedbacks'),
	url(r'^feedback/details/(?P<client_id>[-\w]+)/(?P<order_id>[-\w]+)/$',views.FeedbackAdvanced.as_view(),name='agent-feedbackadvanced'),	
	url(r'^newfeedback/$',views.AddFeedBack.as_view(),name='new-feedback'),
	url(r'^newfeedback/order/(?P<orderid>[-\w]+)/$',views.AddFeedBackOrder.as_view(),name='new-feedback-order'),

	
	url(r'^tickets/edit/(?P<ticket_id>[-\w]+)/(?P<order_id>[-\w]+)/$',views.TicketDetailsEdit.as_view(),name='agent-tickets-edit'),
	url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='agent-ticketadvanced'),
	url(r'^tickets/register/$',views.TicketRegistration.as_view(),name='agent-ticketregister'),
	url(r'^tickets/order/register/(?P<orderid>[-\w]+)/$',views.OrderTicketRegistration.as_view(),name='agent-orderticketregister'),
	url(r'^tickets/followup',views.TicketFollowup.as_view(),name='agent-ticketsfollowup'),

	url(r'^clients/$',views.ClientDetails.as_view(),name='agent-clients'),
	url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='agent-client-orders'),
	url(r'^client/testorders/(?P<client_id>[-\w]+)$',views.ClientOrdersTest.as_view(),name='agent-client-orderstest'),
	url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='agent-client-orderdetails'),
	url(r'^client/testorder/details/$',views.ClientOrderDetailsTest.as_view(),name='agent-client-testorderdetails'),

	url(r'^newenquiry/$',views.NewEnquiry.as_view(),name='agent-newenquiry'),
	url(r'^existingenquiry/(?P<enquiry_id>[-\w]+)$',views.ExistingEnquiry.as_view(),name='agent-existingenquiry'),
	

	url(r'^makeevaluation/(?P<enquiry_id>[-\w]+)$',views.MakeEvaluation.as_view(),name='agent-makeevaluation'),
	url(r'^assignevaluator/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.AssignEvaluator.as_view(),name='agent-assignevaluator'),
	
	
	url(r'^makequatation/(?P<enquiry_id>[-\w]+)/$',views.MakeQuatationBase.as_view(),name='agent-makequatation'),
	
	url(r'^makequatation/phase1/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1.as_view(),name='agent-makequatation1'),
	url(r'^makequatation/phase1/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1Edit.as_view(),name='agent-makequatation1edit'),
	url(r'^makequatation/phase1/duplicate/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1DuplicateEdit.as_view(),name='agent-makequatation1duplicateedit'),
	
	url(r'^makequatation/phase2/delete/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2Delete.as_view(),name='agent-makequatation2delete'),

	url(r'^delete/service/(?P<book_id>[-\w]+)/(?P<evaluation_detail_id>[-\w]+)/$',views.deleteservice,name='agent-delete-service'),
	url(r'^delete/section/(?P<section_id>[-\w]+)/(?P<evaluation_detail_id>[-\w]+)/$',views.deletesection,name='agent-delete-section'),		

	url(r'^makequatation/duplicate/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationDuplicate.as_view(),name='agent-makequatation1duplicate'),	


	url(r'^ajax/address/status/$',views.UpdateAddressStatus,name='ajax-updateaddress'),
	url(r'^ajax/getarea/$',views.GetArea,name='ajax-getarea'),
	url(r'^ajax/getaddress/$',views.GetCustomerAddress,name='ajax-getaddress'),
	url(r'^ajax/cleaning/info$',views.GetCleaningInfo,name='ajax-getcleaninginfo'),
	url(r'^ajax/followup/info$',views.GetFollowupInfo,name='ajax-getfollowupinfo'),
	url(r'^ajax/getcleaningmethods/$',views.GetCleaningMethodsInfo,name='ajax-getcleaningmethod'),
	url(r'^ajax/getcleaningsections/$',views.GetCleaningSectionInfo,name='ajax-getcleaningsection'),
	url(r'^ajax/feedback/order/info/$',views.GetFeedbackOrderInfo,name='get-feedbackorderinfo'),
	url(r'^ajax/ticket/orderscheduler/info/$',views.GetOrderScheduleTicketInfo,name='get-orderscheduleticketInfo'),
	url(r'^ajax/ticket/cleaning/info/$',views.GetCleaningTicketInfo,name='get-cleaningticketInfo'),
	url(r'^ajax/customer/info/$',views.GetCustomerInfo,name='get-customerInfo'),
	url(r'^ajax/customer/order/info/$',views.GetCustomerOrderInfo,name='get-customerorderInfo'),
	url(r'^ajax/customer/order/info/feedback/$',views.GetCustomerOrderInfoFeedback,name='get-customerorderInfofeedback'),
	url(r'^ajax/clientdata/',views.ClientData,name='get-clientData'),
	url(r'^ajax/ticketdata/',views.TicketData,name='get-TicketData'),
	url(r'^ajax/feedbackdata/',views.FeedBackData,name='get-FeedBackData'),
	
	url(r'^ajax/removesection/',views.RemoveSection,name='removebooksection'),
	url(r'^ajax/removekeynote/',views.RemoveKeynote,name='removekeynote'),
	url(r'^ajax/paybackdiscount/removekeynote/',views.RemovePaybackDiscountKeynote,name='removepaybackdiscountkeynote'),
	url(r'^ajax/buybackpromo/removekeynote/',views.RemoveBuyBackPromoKeynote,name='removebuybackpromokeynote'),
	url(r'^ajax/removeevaluationmedia/',views.RemoveEvaluationMedia,name='removeevaluationmedia'),
	url(r'^ajax/mobile/validate/',views.MobileNumberValidate,name='mobilenumber-validate'),
	url(r'^ajax/scheduled/dates/',views.CleaningExistingDates,name='scheduled-dates'),
	url(r'^ajax/evaluationdetail/schedules/',views.GetOrdersSchedulesFromEvalDetails,name='evaluationdetais-schedules'),
]