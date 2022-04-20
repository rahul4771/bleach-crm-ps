from evaluator.models import Evaluation,EvaluationDetails
from order.models import Order,OrderScheduler
from customer.models import CustomerBooking
from datetime import datetime,timedelta,date
from django.utils import timezone
from django.db.models import Prefetch,Q
import requests
import random
from datetime import datetime

from Api.serializers import LeaveScheduleSerializer
import pandas as pd
from user.models import LeaveSchedule,UserProfile,Governorate
import json

def quotationexpiry():
	expiry_date=datetime.now()+timedelta(1)
	expiry_date_start = expiry_date.replace(hour=0,minute=0,second=0,microsecond=0)
	expiry_date_end = expiry_date_start+timedelta(1)
	
	evaluations = Evaluation.objects.filter(Q(Q(quatation_status='PENDING')|Q(quatation_status='REJECTED'))).filter(quatation_expiry_date__range=(expiry_date_start,expiry_date_end),is_active=True)
	
	for evaluation in evaluations:

		evaluation.quatation_status = 'EXPIRED'
		evaluation.save()

		url = "https://smsapi.future-club.com/fccsms.aspx"

		if evaluation.customer.sms_preference == 'ENGLISH':

			message = "Dear Customer, We would like to inform you that the Quotation against the order number "+str(evaluation.evaluation_id)+" will be expired within the next 24 hours. For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"

			querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

		else:
			message = "عزیزنا العمیل نود تكیركم بأن عرض السعر الخاص بالطلب رقم "+str(evaluation.evaluation_id)+" ستنتهي صلاحیته خلال 24 ساعة. لأي استفسارات یمكنكم التواصل معنا على 9651882707+ لاختیاركم بلیتش لخدمات شكرا.  التنظیف"

			querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

		headers = {
			'cache-control': "no-cache"
		}

		response = requests.request("GET", url, headers=headers, params=querystring)
  
def booking_expiry():
	expired_schedules = OrderScheduler.objects.select_related('order__evaluation').filter(is_active=True,order__evaluation__quatation_status__isnull=False,order__payment_status='PENDING',created__lt=timezone.now()-timedelta(minutes=5),work_status='CLEANING_TEAM_ASSIGNED').prefetch_related(Prefetch('order__evaluation__booking_evaluation',queryset=CustomerBooking.objects.filter(is_active=True),to_attr='bookings'))
	for expired_schedule in expired_schedules:
		if expired_schedule.order.evaluation.bookings:
			expired_schedule.delete()

def loadtimeoffsbamboo():
	#load bamboo timeoffs to bleach code
		
	todate = date.today()
	end_date = todate+timedelta(30)
	print(todate,end_date,"datess")

	url = "https://api.bamboohr.com/api/gateway.php/bleachkw/v1/time_off/requests/?start="+str(todate)+"&end="+str(end_date)+"&status=approved"

	headers = {
		"Accept": "application/json",
		"Authorization": "Basic NDNhMjE5Y2ZlNmYyZGJlMjUwYTllYjdiNWUyNzc0MzM1YzE0Njg1ODo="
	}

	response = requests.request("GET", url, headers=headers)
	data = response.json()

	
	for timeoff in data:
		print(timeoff['type'],timeoff['end'],timeoff['employeeId'],"runtime")
		timeoff_start = datetime.strptime(timeoff['start'],"%Y-%m-%d")
		timeoff_end = datetime.strptime(timeoff['end'],"%Y-%m-%d")
		timeoff_id = timeoff['id']

		datelist = pd.date_range(timeoff_start, timeoff_end)
		
		if timeoff['type']['name'] == 'Sick Leave 100%' :
			leave_type = 'SICK LEAVE'
		elif timeoff['type']['name'] == 'Off Day' :
			leave_type = 'WEEKLY OFF'
		else:
			leave_type = timeoff['type']['name']
			leave_type = leave_type.upper()

		print(leave_type,"ltt")

		for timeoffdate in datelist:
			try:
				leaveschedule = LeaveSchedule.objects.get(is_active=True,staff__bamboo_employee_id=int(timeoff['employeeId']),bamboo_leave_id=timeoff_id,leave_date=timeoffdate)
				print(leaveschedule,"lvshes")
				
			except:
				leaveschedule = None
				
				try:
					bleach_employee = UserProfile.objects.get(bamboo_employee_id=int(timeoff['employeeId']),is_active=True)
					datelist = pd.date_range(timeoff_start, timeoff_end)
					
					schedules=[]
					
					schedule_dict = {
						"leave_type" : leave_type,
						"leave_date" : timeoffdate.date(),
						"staff"      : bleach_employee.id,
						"bamboo_leave_id" : timeoff_id
					}
					schedules.append(schedule_dict)
					print(schedules,"sched")
					
					for schedule in schedules:
						serializer = LeaveScheduleSerializer(data=schedule)
				
						if serializer.is_valid(): 
							print("serialval")
							serializer.save()
				except:
					bleach_employee = None


def deletetimeoffsbamboo():
	#delete bamboo timeoffs to bleach code
		
	todate = date.today()
	end_date = todate+timedelta(30)
	print(todate,end_date,"datess")

	url = "https://api.bamboohr.com/api/gateway.php/bleachkw/v1/time_off/requests/?start="+str(todate)+"&end="+str(end_date)+"&status=canceled"

	headers = {
		"Accept": "application/json",
		"Authorization": "Basic NDNhMjE5Y2ZlNmYyZGJlMjUwYTllYjdiNWUyNzc0MzM1YzE0Njg1ODo="
	}

	response = requests.request("GET", url, headers=headers)
	data = response.json()

	print(data,"deta")

	for timeoff in data:
		print(timeoff['id'],"runtime22")
		
		timeoff_id = timeoff['id']
		
		try:
			leaveschedules = LeaveSchedule.objects.filter(is_active=True,bamboo_leave_id=timeoff_id).delete()
			print(leaveschedule,"lvshes44")
			
		except:
			leaveschedules = None

	