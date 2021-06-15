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
	
	url(r'^shift-scheduler/$',views.ShiftScheduleAPI.as_view(),name='api-shiftschedule'),
	url(r'^shift-scheduler-delete/(?P<shift_id>\d+)/$',views.DeleteShiftSchedule.as_view(),name='api-shiftschedule-delete'),

	url(r'^payment/response/credit/$',views.PaymentResponseCredit.as_view(),name='api-responsecredit'),
	url(r'^daily-sales-list/$',views.DailySalesAPI.as_view(),name='api-daily-sales'),
	url(r'^daily-sales-chart/$',views.DailySalesChartAPI.as_view(),name='api-daily-sales-chart'),
	url(r'^payment-policy-edit/$',views.PaymentPolicyEditAPI.as_view(),name='api-payment-policy-edit'),
	url(r'^cleaning-team-data/$',views.CleaningTeamAPI.as_view(),name='api-cleaning-team-data'),
]
