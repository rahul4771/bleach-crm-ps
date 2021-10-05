import random
import string
from django.shortcuts import render,redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth import logout as auth_logout
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,ServiceType,LocationType,CleaningType,CleaningMethod,AreaType
from order.models import Order, OrderScheduler, Investigation, FollowUp, FollowUpScheduler, Question, FeedBack
from user.models import UserProfile, Address, Governorate, Area #for creating data
from senior_team_leader.models import CleaningTeam, CleaningTeamMember, FollowUpTeam, FollowUpTeamMember, CleaningTeamTask
from datetime import datetime, date, timedelta
import pandas as pd
from django.utils import timezone
from django.db.models import Max
from django import db
# Create your views here.

#Login in Page
class Signin(View):  
	def get(self,request):
		if request.user.is_authenticated:
			messages.success(request, "Welcome " + request.user.name)	

			if request.user.user_type == 'AGENT':
				return redirect('agent:agentdash-board')
			if request.user.user_type == 'ADMIN':
				return redirect('bleach_admin:admindash-board')

			if request.user.user_type == 'EVALUATOR':
				return redirect('evaluator:evaluatordash-board')

			if request.user.user_type == 'SENIORTEAMLEADER':	
				return redirect('stl:stldash-board')

			if request.user.user_type == 'TEAMINCHARGE':	
				return redirect('tl:tldash-board')

			if request.user.user_type == 'ACCOUNTANT':	
				return redirect('accountant:accountantdash-board')

			if request.user.user_type == 'QUALITYCONTROLL':	
				return redirect('qc:qcdash-board')

			if request.user.user_type == 'SALESADMIN':	
				return redirect('bleach_salesadmin:salesadmindash-board')

			if request.user.user_type == 'BOOKINGOFFICER':	
				return redirect('booking-officer:bookingofficerdash-board')

			if request.user.user_type == 'INVENTORYADMIN' or request.user.user_type == 'INVENTORYUSER':	
				return redirect('bleach-inventory:inventorydash-board')
		else:		
			return render(request,'user/login.html',{})

		return render(request,'user/login.html',{})	
	
	def post(self,request):  
		user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
			
		if user:
			login(request, user)
			messages.success(request, "Welcome " + user.name)	

			if user.user_type == 'AGENT':
				return redirect('agent:agentdash-board')


			if user.user_type == 'ADMIN':
				return redirect('bleach_admin:admindash-board')

			if user.user_type == 'EVALUATOR':
				return redirect('evaluator:evaluatordash-board')

			if user.user_type == 'SENIORTEAMLEADER':	
				return redirect('stl:stldash-board')

			if user.user_type == 'OPERATIONSUPERVISOR':	
				return redirect('op-supervisor:op-supervisor-dash-board')

			if user.user_type == 'TECHNICALSUPERVISOR':	
				return redirect('tech-supervisor:tech-supervisor-dash-board')

			if user.user_type == 'TEAMINCHARGE':	
				return redirect('tl:tldash-board')

			if user.user_type == 'ACCOUNTANT':	
				return redirect('accountant:accountantdash-board')

			if request.user.user_type == 'QUALITYCONTROLL':	
				return redirect('qc:qcdash-board')		
		else:
			messages.error(request, "Username or Password Invalid")

		return redirect('login')

#Logout Page
class logout(View):
	def get(self,request):
		auth_logout(request)
		return redirect('login')			

def list_function(list):
    length = len(list)-1
    list_data = list[random.randint(0,length)]
    return list_data

def testcalendar(request):
    return render(request,"agent/resource/test.html")