from django.shortcuts import render
from django.views import View

from django.conf import settings
from bleach_crm_ps.permissions import IsTeamLeader
# Create your views here.

class TlHome(IsTeamLeader,View):
	def get(self,request):
		return render(request,'tl/home/home.html',{})

class TicketDetails(IsTeamLeader,View):
	def get(self,request):
		return render(request,'tl/ticket/tickets.html',{})		
		

