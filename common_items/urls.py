from django.conf.urls import include, url
from common_items import views 

#all users urls

urlpatterns = [
		url(r'^orders/$',views.OrderDetails.as_view(),name='orders'),
		url(r'^clients/$',views.ClientDetails.as_view(),name='clients'),
		url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='client-orders'),
		url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='client-orderdetails'),
		url(r'^tickets/$',views.TicketDetails.as_view(),name='tickets'),
		url(r'^tickets/edit/(?P<ticket_id>[-\w]+)/(?P<order_id>[-\w]+)/$',views.TicketDetailsEdit.as_view(),name='tickets-edit'),
		url(r'^ticket/details/(?P<client_id>[-\w]+)/(?P<followup_id>[-\w]+)/$',views.TicketAdvanced.as_view(),name='ticketadvanced'),
		url(r'^tickets/register/$',views.TicketRegistration.as_view(),name='ticketregister'),
		url(r'^tickets/order/register/(?P<orderid>[-\w]+)/$',views.OrderTicketRegistration.as_view(),name='orderticketregister'),
		
		url(r'^customer-bookings/$',views.CustomerBookingsList.as_view(),name='customer-bookings'),
		url(r'^payments/$',views.PaymentDetails.as_view(),name='payments'),
		url(r'^active-subscriptions/$',views.ActiveSubscriptions.as_view(),name='active-subscriptions'),
		url(r'^daily-sales/$',views.DailySales.as_view(),name='daily-sales'),
		url(r'^makequatation/phase1/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1Edit.as_view(),name='makequatation1edit'),
		url(r'^resources/$',views.ResourceManagement.as_view(),name='resource-management'),
		url(r'^booking/(?P<evaluation_detail_id>[-\w]+)/$',views.Booking.as_view(),name='booking'),
		url(r'^newfeedback/order/(?P<orderid>[-\w]+)/$',views.AddFeedBackOrder.as_view(),name='new-feedback-order'),
		url(r'^reorder$',views.Reorder.as_view(),name='reorder'),
		
		url(r'^editcleaning/team/(?P<scheduler_id>[-\w]+)/$',views.EditcleaningTeam.as_view(),name='edit-cleaningteam'),

		url(r'^newenquiry/$',views.NewEnquiry.as_view(),name='newenquiry'),
		url(r'^existingenquiry/(?P<enquiry_id>[-\w]+)$',views.ExistingEnquiry.as_view(),name='existingenquiry'),
		url(r'^assignevaluator/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.AssignEvaluator.as_view(),name='assignevaluator'),
		url(r'^makeevaluation/(?P<enquiry_id>[-\w]+)$',views.MakeEvaluation.as_view(),name='makeevaluation'),
		url(r'^makequatation/(?P<enquiry_id>[-\w]+)/$',views.MakeQuatationBase.as_view(),name='makequatation'),
		url(r'^makequatation/phase1/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1.as_view(),name='makequatation1'),
		url(r'^makequatation/phase2/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2.as_view(),name='makequatation2'),
		url(r'^makequatation/phase2/edit/(?P<evaluation_detail_id>[-\w]+)$',views.MakeQuatationPhase2Edit.as_view(),name='makequatation2edit'),
		url(r'^makequatation/phase1/edit/(?P<enquiry_id>[-\w]+)/(?P<evaluation_id>[-\w]+)/$',views.MakeQuatationPhase1Edit.as_view(),name='makequatation1edit'),

		url(r'^assigncleaning/team/(?P<scheduler_id>[-\w]+)/$',views.AssigncleaningTeam.as_view(),name='assign-cleaningteam'),#New logic applied
		url(r'^editcleaning/team/(?P<scheduler_id>[-\w]+)/$',views.EditcleaningTeam.as_view(),name='edit-cleaningteam'),#New logic applied
		url(r'^resetcleaning/team/(?P<scheduler_id>[-\w]+)/$',views.ResetcleaningTeam.as_view(),name='reset-cleaningteam'),
		# url(r'^resetfollowup/team/(?P<scheduler_id>[-\w]+)/$',views.ResetFollowUpTeam.as_view(),name='reset-followupteam'),#done and tested
		url(r'^assignfollowup/team/(?P<scheduler_id>[-\w]+)/$',views.AssignFollowupTeam.as_view(),name='assign-followupteam'),#New logic applied
		url(r'^editfollowup/team/(?P<scheduler_id>[-\w]+)/$',views.EditFollowupTeam.as_view(),name='edit-followupteam'),#New logic applied

		url(r'^callback-list/$',views.CallBackList.as_view(),name='callback-list'),

		url(r'^resources-new/$',views.ResourceManagementOld.as_view(),name='resource-management-new'),
		url(r'^productivity/$',views.Productivity.as_view(),name='productivity'),
	
		url(r'^feedbacks/$',views.FeedbackDetails.as_view(),name='feedbacks'),
		url(r'^feedback/details/(?P<client_id>[-\w]+)/(?P<order_id>[-\w]+)/$',views.FeedbackAdvanced.as_view(),name='feedbackadvanced'),
		url(r'^newfeedback/order/(?P<orderid>[-\w]+)/$',views.AddFeedBackOrder.as_view(),name='new-feedback-order'),

		url(r'^leave-scheduler/$',views.LeaveScheduler.as_view(),name='leave-scheduler'),	

		url(r'^promocodes/$',views.PromocodeView.as_view(),name='promocode'),

		url(r'^ajax/resourcestoggle/',views.ResourcesToggle,name='resource-toggle'),
	]