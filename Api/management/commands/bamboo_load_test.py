import requests
import json
import pandas as pd
from django.core.management.base import BaseCommand
from user.models import UserProfile
from django.db.models import Q

class Command(BaseCommand):
    help = 'bamboo testing'
    def handle(self, *args, **kwargs):

        # url = "https://api.bamboohr.com/api/gateway.php/bleachkw/v1/employees/directory"

        # headers = {
        #     "Accept": "application/json",
        #     "Authorization": "Basic MjI4ZmQ2Y2EwNzUwZmRmZWMyYjRhMWJkZjYzMmExODdhNDAxMDg4YTo="
        # }

        # response = requests.request("GET", url, headers=headers)
        # data = response.json()

        # user_data = []

        # for userdata in data['employees']:

        #     if userdata['jobTitle'] == 'Team Leader' or userdata['jobTitle'] == 'Cleaner' or userdata['jobTitle'] == 'Team In-Charge':
            
        #         user_data_dict = {
        #             'bamboo employee id' : userdata['id'],
        #             'display name' : userdata['displayName'],
        #             'first name' : userdata['firstName'],
        #             'last name' : userdata['lastName'],
        #             'job title' : userdata['jobTitle']
        #         }
        #         user_data.append(user_data_dict)

        system_users = UserProfile.objects.filter(is_active=True).filter(Q( Q(user_type='CLEANER') | Q(user_type='TEAMINCHARGE'))).values('name','bamboo_employee_id')

        df = pd.DataFrame(system_users)
        df = df[['bamboo_employee_id', 'name']]

        with pd.ExcelWriter('/home/pdf/tmp/crm_system_users.xls') as writer:
            df.to_excel(writer,sheet_name='crm system users')

        print(system_users,"dataframe")