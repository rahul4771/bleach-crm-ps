from django.shortcuts import render
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsEvaluator
# Create your views here.

class EvaluatorHome(IsEvaluator,View):
	def get(self,request):
		return render(request,'evaluator/home/home.html',{})

class ClientDetails(IsEvaluator,View):
	def get(self,request):
		return render(request,'evaluator/client/clients.html',{})		
		

class OrderDetails(IsEvaluator,View):
	def get(self,request):
		return render(request,'evaluator/order/orders.html',{})		


class ResourceManagement(IsEvaluator,View):
	def get(self,request):
		return render(request,'evaluator/resource/resources.html',{})

class TicketDetails(IsEvaluator,View):
	def get(self,request):
		return render(request,'evaluator/ticket/tickets.html',{})
