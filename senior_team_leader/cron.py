from datetime import datetime,timedelta,date
from api.serializers import LeaveScheduleSerializer
import pandas as pd
from user.models import LeaveSchedule,UserProfile
from django.utils import timezone
from django.db.models import Prefetch,Q
import requests
import json

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

    	datelist = pd.date_range(timeoff_start, timeoff_end)

    	if timeoff['type']['name'] == 'Sick Leave 100%' :
    		leave_type = 'SICK LEAVE'
    	else:
    		leave_type = timeoff['type']['name']
    		leave_type = leave_type.upper()

    	print(leave_type,"ltt")

    	for timeoffdate in datelist:
    		try:
    			leaveschedule = LeaveSchedule.objects.get(is_active=True,staff__bamboo_employee_id=int(timeoff['employeeId']),leave_date=timeoffdate)
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
    					"staff"      : bleach_employee.id
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