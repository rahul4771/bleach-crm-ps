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

			if request.user.user_type == 'TEAMLEADER':	
				return redirect('tl:tldash-board')

			if request.user.user_type == 'ACCOUNTANT':	
				return redirect('accountant:accountantdash-board')

			if request.user.user_type == 'QUALITYCONTROLL':	
				return redirect('qc:qcdash-board')
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

			if user.user_type == 'TEAMLEADER':	
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

def adddata(request):
	# startdate = pd.to_datetime('12-12-2020')
	# daterange = pd.date_range(startdate, periods=100)
	# print("rt")

	# print(daterange,"drg")
	# for dt in daterange:
	# 	print(dt,"ert")
	# 	print(dt.strftime("%Y-%m-%d"),"str")

	# usr = UserProfile.objects.get(username='bleachagent1')

	# evaluations=[]
	# saved_evaluations=[]
	# eval_details = []
	# eval_book = []
	# customers = []
	# address = []
	# agents = []
	# evaluators = []
	# dated = []
	# stype = []
	# ltype = []
	# clmethod = []
	# artype = []

	# serv_type = ServiceType.objects.all()
	# for ser in serv_type:
	# 	stype.append(ser)
  
	# loc_type = LocationType.objects.all()
	# for loc in loc_type:
	# 	ltype.append(loc)

	# area_type = AreaType.objects.all()
	# for area in area_type:
	# 	artype.append(area)
	
	# clean_method = CleaningMethod.objects.all()
	# for clm in clean_method:
	# 	clmethod.append(clm)
 
	# gender = ["MALE","FEMALE"]
	# payment = ['PREPAID','POSTPAID','BREAKDOWN']
	# customer_types = ['INDIVIDUAL','RETAIL','CORPORATE']
	# cleaning_choices = ['ONE_TIME_SERVICE','SUBSCRIPTION']
	# order_status = ['APPROVED_BY_CLIENT','ORDER_IN_PROGRESS','ORDER_CANCELLED','ORDER_CLOSED']
	# payment_status = ['PENDING','COMPLETED']

	# for i in range(1,8):
	# 	random_gender = list_function(gender)
	# 	random_cust_type = list_function(customer_types)
	# 	customers.append(UserProfile(
	# 	name = 'agent'+str(i),
	# 	user_type = 'AGENT',
	# 	username = 'bleachagent'+str(i),
	# 	gender = random_gender,
	# 	nationality = 'Kuwait',
	# 	mobile_number = random.randint(61111111,99999999)
	# 	))
	
	# for i in range(1,6):
	# 	random_gender = list_function(gender)
	# 	random_cust_type = list_function(customer_types)
	# 	customers.append(UserProfile(
	# 	name = 'Evaluator'+str(i),
	# 	user_type = 'EVALUATOR',
	# 	username = 'bleachevaluator'+str(i),
	# 	gender = random_gender,
	# 	nationality = 'Kuwait',
	# 	mobile_number = random.randint(61111111,99999999)
	# 	))
  
	# for i in range(1,6):
	# 	random_gender = list_function(gender)
	# 	random_cust_type = list_function(customer_types)
	# 	customers.append(UserProfile(
	# 	name = 'STL'+str(i),
	# 	user_type = 'SENIORTEAMLEADER',
	# 	username = 'stl'+str(i),
	# 	gender = random_gender,
	# 	nationality = 'Kuwait',
	# 	mobile_number = random.randint(61111111,99999999)
	# 	))
  
	# for i in range(1,6):
	# 	random_gender = list_function(gender)
	# 	random_cust_type = list_function(customer_types)
	# 	customers.append(UserProfile(
	# 	name = 'TL'+str(i),
	# 	user_type = 'TEAMLEADER',
	# 	username = 'tl'+str(i),
	# 	gender = random_gender,
	# 	nationality = 'Kuwait',
	# 	mobile_number = random.randint(61111111,99999999)
	# 	))

	# for i in range(1,6):
	# 	random_gender = list_function(gender)
	# 	random_cust_type = list_function(customer_types)
	# 	customers.append(UserProfile(
	# 	name = 'CLEANER'+str(i),
	# 	user_type = 'CLEANER',
	# 	username = 'cln'+str(i),
	# 	gender = random_gender,
	# 	nationality = 'Kuwait',
	# 	mobile_number = random.randint(61111111,99999999)
	# 	))

	# tracking_no=0
	# governorates = []
	# areas = []
	# orders = []
	# gar = {}
 
	# gov = Governorate.objects.all()
	# for g in gov:
	# 	gov_areas = Area.objects.filter(governorate=g)
	# 	governorates.append(g)
	# 	gar[g] = gov_areas
	# 	areas.append(gar)

	# for i in range(1,200):
	# 	random_gender = list_function(gender)
	# 	random_cust_type = list_function(customer_types)
	# 	customers.append(UserProfile(
	# 	name = 'customer'+str(i),
	# 	user_type = 'CUSTOMER',
	# 	username = 'user'+str(i),
	# 	gender = random_gender,
	# 	customer_type = random_cust_type,
	# 	nationality = 'Kuwait',
	# 	sms_preference = 'ENGLISH',
	# 	mobile_number = random.randint(61111111,99999999)
	# 	))
	
	# UserProfile.objects.bulk_create(customers)
	# customers = []
 
	# customer_addr = UserProfile.objects.filter(user_type="CUSTOMER",is_active=True)
	# for customer in customer_addr:
	# 	random_gov = list_function(governorates)
	# 	random_areas = list_function(gar[random_gov])
	# 	address.append(Address(
	# 		customer = customer,governorate = random_gov,area = random_areas,block = random.randint(10,500),
	# 		avenue = ''.join(random.sample(string.ascii_lowercase, k=6)),
	# 		building = ''.join(random.sample(string.ascii_lowercase, k=5)),
	# 		street = ''.join(random.sample(string.digits + string.ascii_uppercase, k=3)),
	# 		floor = random.randint(1,50),
	# 		apartment = ''.join(random.sample(string.ascii_lowercase, k=6)),
	# 		currently_active = True, is_active	= True
	# 		))
	# Address.objects.bulk_create(address)
 
	# tracking_no = Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or 10000
	# for date in  daterange:
	# 	for i in range(random.randint(1,3),random.randint(6,8)):
	# 		print(i,"eye")
	# 		customer = UserProfile.objects.filter(user_type="CUSTOMER",is_active=True)
	# 		agent = UserProfile.objects.filter(user_type="AGENT",is_active=True)
	# 		for cus in  customer:
	# 			customers.append(cus)
	# 		for ag in agent:
	# 			agents.append(ag)
	# 		agt = list_function(agents)
	# 		cst = list_function(customers)
	# 		gen = list_function(gender)
	# 		pay = list_function(payment)
	# 		tracking_no += 1 #Evaluation.objects.filter(is_active=True,tracking_no__isnull=False).aggregate(t=Max('tracking_no'))['t'] or 10000		
	# 		evaluation_id  = 'BLC2'+str(timezone.now().year)+str(timezone.now().month).zfill(2)+str(tracking_no+1)
	# 		call_attender = agt
	# 		customer = cst
	# 		estimated_cost = random.randint(5000,20000)
	# 		discount = random.randint(500,1000)
	# 		total_cost = int(estimated_cost-discount)
	# 		preffered_gender = gen
	# 		quatation_status = 'REJECTED'
	# 		quatation_approved_date = date.strftime("%Y-%m-%d")
	# 		payment_method = pay
	# 		is_active = True
	# 		if pay == 'BREAKDOWN':
	# 			before_cleaning_amount = random.randint(500,total_cost)
	# 			after_cleaning_amount = int(total_cost - before_cleaning_amount)	
	# 		else:
	# 			before_cleaning_amount = None
	# 			after_cleaning_amount = None

	# 		evaluations.append(Evaluation(
	# 				tracking_no=tracking_no,evaluation_id=evaluation_id,call_attender=call_attender,
	# 				customer=customer,estimated_cost=estimated_cost,discount=discount,total_cost=total_cost,
	# 				quatation_status=quatation_status,quatation_approved_date=quatation_approved_date,payment_method=payment_method,
    #  				is_active=is_active,before_cleaning_amount=before_cleaning_amount,after_cleaning_amount=after_cleaning_amount))
	# 	# print(evaluations)
	# 	Evaluation.objects.bulk_create(evaluations)
		
	# evals = Evaluation.objects.filter(quatation_status = 'REJECTED',is_active=True)
	# # print(evals,"evs")
	# # for ev in evals:
		
	# evaluator = UserProfile.objects.filter(user_type="EVALUATOR",is_active=True)
	# for eval in evaluator:
	# 	evaluators.append(eval)
	# 	evr = list_function(evaluators)

	# 	eval_details.append(EvaluationDetails(
	# 			evaluation=ev,evaluator=evr,
	# 			estimated_cost=ev.estimated_cost,discount=ev.discount,total_cost=ev.total_cost,
	# 			status="EVALUATED",is_active=True))
	# EvaluationDetails.objects.bulk_create(eval_details)
	
	# ev_details = EvaluationDetails.objects.filter(is_active=True)

	# for evd in ev_details:
	# 	rand_clean_choices = list_function(cleaning_choices)
	# 	rand_ser_type = list_function(stype)
	# 	rand_location_type = list_function(ltype)
	# 	rand_area_type = list_function(artype)
	# 	rand_clean_method = list_function(clmethod)

	# 	eval_book.append(EvaluationBook(
	# 		evaluation_details = evd, cleaning_policy = rand_clean_choices, area_type = rand_area_type,
	# 		service_type = rand_ser_type, cleaning_method = rand_clean_method, location_type = rand_location_type,
	# 		number_of_cleaners = random.randint(2,10), estimated_cost = evd.estimated_cost, discount = evd.discount,
	# 		total_cost = evd.total_cost, is_active = True
	# 	))
	# EvaluationBook.objects.bulk_create(eval_book)

	# for ev in evals:
	# 	rand_ord_status = list_function(order_status)
	# 	rand_payment_status = list_function(payment_status)
	# 	rand_evaluators = list_function(evaluators)
	# 	ord = ''.join(random.sample('ORD2' + string.digits, k=6))
	# 	while Order.objects.filter(order_no=ord).exists():
	# 		ord = ''.join(random.sample('ORD2' + string.digits, k=6))
	# 	orders.append(Order(
	# 		evaluation = ev, order_no = ord, order_status = 'APPROVED_BY_CLIENT',
	# 		payment_status = rand_payment_status, created_by = rand_evaluators
	# 	))
	# Order.objects.bulk_create(orders)

	# ords = Order.objects.filter(evaluation__quatation_status='APPROVED')
	# orderschedules = []
	# for ord in ords:
	# 	orderschedules.append(OrderScheduler(
	# 		order = ord, is_active=True
	# 	))
	# OrderScheduler.objects.bulk_create(orderschedules)
 
	# followup_apprv = ["True","False"]
	# ordscheds = OrderScheduler.objects.all()
	# inv = []
	# for ordsched in ordscheds:
	# 	rand_followup_approve = list_function(followup_apprv)
	# 	inv.append(Investigation(
	# 		order = ordsched.order, order_schedule = ordsched, is_followup_approved = rand_followup_approve, is_active = True
	# 	))
	# Investigation.objects.bulk_create(inv)
 
	# FOLLOWUP_STATUS = ['FOLLOWUP_CANCELLED','FOLLOWUP_CLOSED']
	# followups = []
	# investigations = Investigation.objects.filter(is_followup_approved=True)
	# for invest in investigations:
	# 	random_followup_status = list_function(FOLLOWUP_STATUS)
	# 	followups.append(FollowUp(
	# 		investigation = invest, status = random_followup_status, is_active = True
	# 	))
	# FollowUp.objects.bulk_create(followups)
 
	# questions = []
	# for i in range(1,10):
	# 	questions.append(Question(
	# 		question = ''.join(random.sample(string.ascii_lowercase, k=20)), is_active = True
	# 	))
	# Question.objects.bulk_create(questions)
	
	# qstns = []
	# qsts = Question.objects.all()
	# for qst in qsts:
	# 	qstns.append(qst)
  
	# feedbacks = []
	# for ord in ords:
	# 	feedbacks.append(FeedBack(
	# 		order = ord, question = list_function(qstns), rating = random.randint(1,5),
   	# 		response_date = ord.evaluation.quatation_approved_date, is_active = True
	# 	))
	# FeedBack.objects.bulk_create(feedbacks)
	# todate = date.today() - timedelta(days=40)
	# prevdate = date.today() - timedelta(days=50)
	# tickets = FollowUp.objects.filter(investigation__order__evaluation__quatation_approved_date__month__lte=6)
	# for t in tickets:
	# 	print(t.investigation.order.evaluation.quatation_approved_date,"pl")
	# cleanteam = []
	# teamleaders = []
	# tl = UserProfile.objects.filter(is_active=True,user_type='TEAMLEADER')
	# for t in tl:
	# 	teamleaders.append(t)
	
	# for ordsch in ordscheds:
	# 	print(ordsch.order,ordsch.order.evaluation.quatation_approved_date,"dt")
	# 	cln_date = ordsch.order.evaluation.quatation_approved_date + timedelta(days=7)
	# 	begin = timezone.now().replace(year=cln_date.year,month=cln_date.month,day=cln_date.day,hour=random.randint(10,12),minute=0,second=0,microsecond=0,tzinfo=None)
	# 	end = timezone.now().replace(year=cln_date.year,month=cln_date.month,day=cln_date.day,hour=random.randint(13,18),minute=0,second=0,microsecond=0,tzinfo=None)
	# 	cleanteam.append(CleaningTeam(
	# 		order_scheduler = ordsch,
	# 		team_leader = list_function(teamleaders),
   	# 		start_at = begin,
	# 		end_at = end,
	# 		check_in = begin,
	# 		check_out = end,
	# 		is_active = True
	# 	))
	# CleaningTeam.objects.bulk_create(cleanteam)
	
	# cleaningteams = CleaningTeam.objects.filter(is_active=True)
	
	# cleanerslist = []
	# cleanteammembers = []
	# cleaners = UserProfile.objects.filter(is_active=True,user_type='CLEANER')
	# for cleaner in cleaners:
	# 	cleanerslist.append(cleaner)
	
	# for cl in cleaningteams:

	# 	for i in range(1,3):
	# 		cleanteammembers.append(CleaningTeamMember(
	# 			team = cl, member=list_function(cleanerslist),start_at= cl.start_at,end_at=cl.end_at))
	# CleaningTeamMember.objects.bulk_create(cleanteammembers)
	
	# cleantasks=[]
	# for cln in cleaningteams:
	# 	cleantasks.append(CleaningTeamTask(
	# 		cleaning_team = cln, is_completed = True, start_time = cln.start_at, end_time = cln.end_at, is_active = True
	# 	))
	# CleaningTeamTask.objects.bulk_create(cleantasks)

	return render(request,"createdata.html")

def testcalendar(request):
    return render(request,"agent/resource/test.html")