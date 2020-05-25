from django.shortcuts import render
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsSeniorTeamLeader
# Create your views here.

class StlHome(IsSeniorTeamLeader,View):
	def get(self,request):
		return render(request,'stl/home/home.html',{})

class TicketDetails(IsSeniorTeamLeader,View):
	def get(self,request):
		return render(request,'stl/ticket/tickets.html',{})		
		

