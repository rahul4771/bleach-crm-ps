from evaluator.models import Evaluation,EvaluationDetails
from order.models import Order,OrderScheduler
from customer.models import CustomerBooking
from datetime import datetime,timedelta,date
from django.db.models import Sum,When,Case,IntegerField
import requests

def quotationexpiry():
    expiry_date=datetime.now()+timedelta(1)
    expiry_date_start = expiry_date.replace(hour=0,minute=0,second=0,microsecond=0)
    expiry_date_end = expiry_date_start+timedelta(1)
    
    evaluations = Evaluation.objects.filter(quatation_status='APPROVED',quatation_expiry_date__range=(expiry_date_start,expiry_date_end),is_active=True)
    
    for evaluation in evaluations:

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
    expired_schedules = OrderScheduler.objects.select_related('order__evaluation').filter(is_active=True,order__evaluation__quatation_status__isnull=False,order__payment_status='PENDING',created__lt=timezone.now()-timedelta(minutes=5),work_status='CLEANING_TEAM_ASSIGNED').prefetch_related('order__evaluation__booking_evaluation').annotate(customerbooking=Sum(Case(When(order__evaluation__booking_evaluation__booking_type='CLEANINGBOOKING',then=1),default=0,output_field=IntegerField()))).filter(customerbooking__gte=1)
    expired_schedules.delete()