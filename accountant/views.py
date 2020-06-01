from django.shortcuts import render
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsAccountant
# Create your views here.

from django.utils import timezone 
from datetime import timedelta,date,datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField
from django.db.models.functions import Cast 
from django.db.models import Prefetch

from user.models import UserProfile,Address
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,FollowUp
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember
from accountant.models import Invoice

class AccountantHome(IsAccountant,View):
	def get(self,request):
		#sales amount
		try:
			invoices         = Invoice.objects.filter(is_active=True).order_by('-id')
		except:
			invoices         = None

		this_week_sales = invoices.filter(status='COMPLETED',created__date__gte=timezone.now().date()-timedelta(6)).aggregate(total=Sum('amount_paid'))['total']
		last_week_sales = invoices.filter(status='COMPLETED',created__date__gte=timezone.now().date()-timedelta(13),created__date__lte=timezone.now().date()-timedelta(6)).aggregate(total=Sum('amount_paid'))['total']		
		this_month_sales=invoices.filter(status='COMPLETED',created__month=timezone.now().month,created__year=timezone.now().year).aggregate(total=Sum('amount_paid'))['total']
		last_month_sales=invoices.filter(status='COMPLETED',created__month=((timezone.now().date()-relativedelta(months=1)).month),created__year=timezone.now().year).aggregate(total=Sum('amount_paid'))['total']	
		
		this_quarter_sales=invoices.filter(status='COMPLETED',created__date__lte=timezone.now().date(),created__date__gte=(timezone.now().date()-relativedelta(months=3,day=1))).aggregate(total=Sum('amount_paid'))['total']
		last_quarter_sales=invoices.filter(status='COMPLETED',created__date__lt=(timezone.now().date()-relativedelta(months=3,day=1)),created__date__gte=(timezone.now().date()-relativedelta(months=6,day=1))).aggregate(total=Sum('amount_paid'))['total']	
		
		#Pending Payments
		try:
			pending_payments = invoices.filter(Q(Q(status='PENDING')|Q(status='ON_HOLD'))).select_related('order__evaluation__customer').prefetch_related(Prefetch('order__evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area'),to_attr='invoice_evaluation_details'))
		except:
			pending_payments = None

		#Pending Payment and Order Count	
		total_pending_amount = pending_payments.aggregate(total=Sum(F('total_amount')-F('amount_paid')))['total']		
		total_pending_orders = pending_payments.count()
		
		return render(request,'accountant/home/home.html',{"this_week_sales":this_week_sales,"last_week_sales":last_week_sales,"this_month_sales":this_month_sales,"last_month_sales":last_month_sales,"this_quarter_sales":this_quarter_sales,"last_quarter_sales":last_quarter_sales,"pending_payments":pending_payments,'total_pending_amount':total_pending_amount,"total_pending_orders":total_pending_orders})

class ClientDetails(IsAccountant,View):
	def get(self,request):

		search                  = request.GET.get('search')

		if search:
			try:
				client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True,name__icontains=search).prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area'),to_attr='customer_address'),Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True,order_status='ORDER_CLOSED'),to_attr='order_evaluation')),to_attr='customer_evaluations'))
			except:
				client_details = None
		else:
			client_details = UserProfile.objects.filter(user_type='CUSTOMER',is_active=True).prefetch_related(Prefetch('address_customer',queryset=Address.objects.filter(is_active=True).select_related('area'),to_attr='customer_address'),Prefetch('customer_evaluation',queryset=Evaluation.objects.filter(is_active=True).prefetch_related(Prefetch('evaluation_order',queryset=Order.objects.filter(is_active=True,order_status='ORDER_CLOSED'),to_attr='order_evaluation')),to_attr='customer_evaluations'))			

		#code must change for optimisation	
		for detail in client_details:
			detail.active_status = False
			if detail.customer_evaluations:
				for evaluation in detail.customer_evaluations:
					if evaluation.order_evaluation:
						detail.active_status = True	

		#To Find active and new client
		try:
			orders = Order.objects.filter(is_active=True).select_related('evaluation__customer')
		except:
			orders = None	

		active_clients_count = orders.filter(~Q(order_status='ORDER_CLOSED')).values_list('evaluation__customer').distinct().count()	
		new_clients_count    = orders.filter(evaluation__created__date__gte=timezone.now().date()-timedelta(30),evaluation__customer__created__date__gte=timezone.now().date()-timedelta(30),).values_list('evaluation__customer').distinct().count()
		
		return render(request,'accountant/client/clients.html',{"client_details":client_details,"search_query":search,"active_clients_count":active_clients_count,"new_clients_count":new_clients_count})		
		

class OrderDetails(IsAccountant,View):
	def get(self,request):

		#Evaluation Details
		search                  = request.GET.get('search')
		
		if search:
			try:
				evaluations = Evaluation.objects.select_related('customer').filter(is_active=True,customer__name__icontains=search).prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_book')),to_attr='details_evaluation'))
			except:
				evaluations = None 
		 
		else:
			try:
				evaluations = Evaluation.objects.filter(is_active=True).select_related('customer').prefetch_related(Prefetch('evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area').prefetch_related(Prefetch('evaluation_book_evaluation_details',queryset=EvaluationBook.objects.filter(is_active=True),to_attr='evaluation_book')),to_attr='details_evaluation'))
			except:
				evaluations = None 
			
		approved_orders_count = evaluations.filter(Q(quatation_status='APPROVED')).count()
		pending_orders_count  =	evaluations.filter(Q(Q(quatation_status='ASK_FOR_DISCOUNT')|Q(quatation_status='PENDING'))).count()
		
		return render(request,'accountant/order/orders.html',{"evaluations":evaluations,"approved_orders_count":approved_orders_count,"pending_orders_count":pending_orders_count,"search_query":search})		


class PaymentDetails(IsAccountant,View):
	def get(self,request):

		#Evaluation Details
		search                  = request.GET.get('search')
		
		#sales amount
		if search:
			try:
				invoices         = Invoice.objects.filter(is_active=True).order_by('-id').select_related('order__evaluation__customer').filter(order__evaluation__customer__name__icontains=search).prefetch_related(Prefetch('order__evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area'),to_attr='invoice_evaluation_details'))
			except:
				invoices         = None
		else:
			try:
				invoices         = Invoice.objects.filter(is_active=True).order_by('-id').select_related('order__evaluation__customer').prefetch_related(Prefetch('order__evaluation__evaluation_details',queryset=EvaluationDetails.objects.filter(is_active=True).select_related('address__area'),to_attr='invoice_evaluation_details'))
			except:
				invoices         = None
		print(invoices)
				
		#Pending Payments
		try:
			pending_payments = invoices.filter(Q(Q(status='PENDING')|Q(status='ON_HOLD')))
		except:
			pending_payments = None

		#Pending Payment and Order Count	
		if pending_payments: 
			total_pending_amount = pending_payments.aggregate(total=Sum(F('total_amount')-F('amount_paid')))['total']		
			total_pending_orders = pending_payments.count()
		else:
			total_pending_amount = 0
			total_pending_orders = 0
				
		return render(request,'accountant/payment/payments.html',{'invoices':invoices,'total_pending_amount':total_pending_amount,'total_pending_orders':total_pending_orders,"search_query":search})

