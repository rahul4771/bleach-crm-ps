from django.conf.urls import include, url
from common_items import views 

app_name = 'common_items'
#all users urls

urlpatterns = [

		url(r'^raiseticket/$',views.NewRaiseTicket.as_view(),name='raise-tickets'),
		url(r'^editticket/(?P<ticket_id>[-\w]+)$',views.EditTicket.as_view(),name='edit-tickets'),

		url(r'^newinvestigation/(?P<investigation_id>[-\w]+)/$',views.NewInvestigationTask.as_view(),name='newinvestigation'),

		url(r'^tickets/order/register/(?P<orderid>[-\w]+)/$',views.OrderTicketRegistration.as_view(),name='orderticketregister'),


		url(r'^orders/$',views.OrderDetails.as_view(),name='orders'),
		url(r'^clients/$',views.ClientDetails.as_view(),name='clients'),
		url(r'^client/orders/(?P<client_id>[-\w]+)$',views.ClientOrders.as_view(),name='client-orders'),
		url(r'^client/order/details/(?P<order_id>[-\w]+)$',views.ClientOrderDetails.as_view(),name='client-orderdetails'),
		#test
		url(r'^client/order/details/test/(?P<order_id>[-\w]+)$',views.ClientOrderDetailsTest.as_view(),name='client-orderdetailstest'),
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
		url(r'^newservice/$',views.NewService.as_view(),name='new service'),
		url(r'^newfeedback/order/(?P<orderid>[-\w]+)/$',views.AddFeedBackOrder.as_view(),name='new-feedback-order'),
		url(r'^reorder$',views.Reorder.as_view(),name='reorder'),

		url(r'^cash/collect/$',views.CashCollect.as_view(),name='cashcollect'),
		url(r'^finewriteback/$',views.FineWriteBack.as_view(),name='finewriteback'),

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
		# url(r'^resetfollowup/team/(?P<scheduler_id>[-\w]+)/$',views.ResetFollowUpTeam.as_view(),name='reset-followupteam'),
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

		url(r'^cancell-order/(?P<order_id>[-\w]+)/$',views.OrderCancellation.as_view(),name='cancell-order'),
		url(r'^cancell-book/(?P<evaluation_id>[-\w]+)/$',views.EvaluationBookCancellation.as_view(),name='cancell-book'),
        url(r'^update-visit-datetime/$', views.update_visit_datetime, name='update-visit-datetime'),	
        url(r'^add-service-type/$', views.add_service_type, name='add-service-type'),	
        url(r'^update-service-type/(?P<service_type_id>[-\w]+)/$', views.ServiceTypeAPIView.as_view(), name='update-service-type'),	
        url(r'^add-service-productivity/$', views.ServiceProductivityAPIView.as_view(), name='add-service-productivity'),
        url(r'^update-service-productivity/(?P<productivity_id>[-\w]+)$', views.ServiceProductivityAPIView.as_view(), name='update-service-productivity'),
        url(r'^add-service-price-range/$', views.ProductivityPriceRangeAPIView.as_view(), name='add-service-price-range'),
        url(r'^update-service-price-range/(?P<price_range_id>[-\w]+)$', views.ProductivityPriceRangeAPIView.as_view(), name='update-service-price-range'),
        url(r'^add-service-addons/$', views.ServiceAddOnsAPIView.as_view(), name='add-service-addons'),
        url(r'^update-service-addons/(?P<addon_id>[-\w]+)$', views.ServiceAddOnsAPIView.as_view(), name='update-service-addons'),
        url(r'^staging/productivity/$',views.StagingProductivity.as_view(),name='staging-productivity'),
        url(r'^staging/productivity/get-service-types/$', views.ProductivityServiceTypeAPIView.as_view(), name='get-service-types'),
        url(r'^delete-service-type/(?P<service_type_id>[-\w]+)/$', views.ServiceTypeAPIView.as_view(), name='delete-service-type'),
       	url(r'^delete-service-price-range/(?P<price_range_id>[-\w]+)/$', views.ProductivityPriceRangeAPIView.as_view(), name='delete-service-price-range'),
        url(r'^delete-service-addons/(?P<addon_id>[-\w]+)/$', views.ServiceAddOnsAPIView.as_view(), name='delete-service-addons'),
		url(r'^delete-productivity/(?P<productivity_id>[-\w]+)/$', views.ServiceProductivityAPIView.as_view(), name='delete-productivity'),
        url(r'^add-measurement-unit/$', views.MeasurementUnitsAPIView.as_view(), name='add-measurement-unit'),
		url(r'^update-measurement-unit/(?P<measurement_unit_id>[-\w]+)$', views.MeasurementUnitsAPIView.as_view(), name='update-measurement-unit'),
        url(r'^delete-measurement-unit/(?P<measurement_unit_id>[-\w]+)$', views.MeasurementUnitsAPIView.as_view(), name='delete-measurement-unit'),
        url(r'^create-service-group/$', views.ServiceGroupAPIView.as_view(), name='create-service-group'),
        url(r'^staging/productivity/get-service-groups/$', views.ServiceGroupAPIView.as_view(), name='get-service-groups'),
        url(r'^delete-service-group/(?P<service_group_id>[-\w]+)/$', views.ServiceGroupAPIView.as_view(), name='delete-group-type'),
        url(r'^update-service-group/(?P<service_group_id>[-\w]+)/$', views.ServiceGroupAPIView.as_view(), name='update-service-group'),
    
        ]
