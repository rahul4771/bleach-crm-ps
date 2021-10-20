from evaluator.models import Evaluation,EvaluationDetails
from order.models import Order,OrderScheduler
from customer.models import CustomerBooking
from datetime import datetime,timedelta,date
from django.utils import timezone
from django.db.models import Prefetch,Q
import requests

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