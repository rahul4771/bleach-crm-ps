from django.shortcuts import render,redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth import logout as auth_logout
# Create your views here.

#Login in Page
class Signin(View):  
	def get(self,request):
		return render(request,'user/login.html',{})
	def post(self,request):  
		user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
			
		if user:
			login(request, user)
			messages.success(request, "Welcome " + user.username)	

			if user.user_type == 'AGENT':
				return redirect('agent:agentdash-board')


			if user.user_type == 'ADMIN':
				return redirect('bleach_admin:admindash-board')

			if user.user_type == 'EVALUATOR':
				return redirect('evaluator:evaluatordash-board')

			if user.user_type == 'SENIORTEAMLEADER':	
				return redirect('stl:stldash-board')

			if user.user_type == 'TEAMLEADER':	
				return redirect('tl:tldash-board')

			if user.user_type == 'ACCOUNTANT':	
				return redirect('accountant:accountantdash-board')		
		else:
			messages.error(request, "Username or Password Invalid")

		return redirect('login')

#Logout Page
class logout(View):
	def get(self,request):
		auth_logout(request)
		return redirect('login')		