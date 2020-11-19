from evaluator.models import Evaluation,EvaluationDetails
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField
from datetime import datetime,timedelta,date
import requests

def quotationexpiry():
    expiry_date=date.today()+timedelta(1)
    
    evaluations = Evaluation.objects.filter(quatation_status='APPROVED',quatation_expiry_date__date=expiry_date,is_active=True)
    
    for evaluation in evaluations:
			
			evaluation.attender_notes = "crontab success"
			evaluation.save()

        # url = "https://smsapi.future-club.com/fccsms.aspx"

        # if evaluation.customer.sms_preference == 'ENGLISH':

        #     message = "Dear Customer, We would like to inform you that the Quotation against the order number "+str(evaluation.evaluation_id)+" will be expired within the next 24 hours. For any assistance please contact us on +9651882707. Thank you for choosing Bleach Kuwait"

        #     querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"L"}

        # else:
        #     message = "عزیزنا العمیل نود تكیركم بأن عرض السعر الخاص بالطلب رقم "+str(evaluation.evaluation_id)+" ستنتهي صلاحیته خلال 24 ساعة. لأي استفسارات یمكنكم التواصل معنا على 9651882707+ لاختیاركم بلیتش لخدمات شكرا.  التنظیف"

        #     querystring = {"UID":"Blkusr","P":"lckw33","S":"BLEACH","G":"965"+evaluation.customer.mobile_number+"","M":message,"IID":"1468","L":"A"}

        # headers = {
        #     'cache-control': "no-cache"
        # }

        # response = requests.request("GET", url, headers=headers, params=querystring)
  