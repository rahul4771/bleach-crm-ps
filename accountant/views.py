from django.shortcuts import render
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsAccountant
# Create your views here.

class AccountantHome(IsAccountant,View):
	def get(self,request):
		return render(request,'accountant/home/home.html',{})

class ClientDetails(IsAccountant,View):
	def get(self,request):
		return render(request,'accountant/client/clients.html',{})		
		

class OrderDetails(IsAccountant,View):
	def get(self,request):
		return render(request,'accountant/order/orders.html',{})		


class PaymentDetails(IsAccountant,View):
	def get(self,request):
		return render(request,'accountant/payment/payments.html',{})

