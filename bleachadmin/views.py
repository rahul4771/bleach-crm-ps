from django.shortcuts import render
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsAdmin
# Create your views here.

class AdminHome(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/home/home.html',{})

class ClientDetails(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/client/clients.html',{})		

class TicketDetails(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/ticket/tickets.html',{})		

class OrderDetails(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/order/orders.html',{})		

class FeedbackDetails(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/feedback/feedbacks.html',{})

class ResourceManagement(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/resource/resources.html',{})

class PaymentDetails(IsAdmin,View):
	def get(self,request):
		return render(request,'admin/payment/payments.html',{})		
