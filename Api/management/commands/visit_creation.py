from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from order.models import OrderScheduler, Order
from evaluator.models import EvaluationDetails, EvaluationBook
from user.models import Address

class Command(BaseCommand):
    help = "Create OrderScheduler entries"

    def handle(self, *args, **kwargs):
        try:
            # Fetch required objects
            order = Order.objects.get(order_no='BLC20250310227')
            evaluation_details = EvaluationDetails.objects.get(evaluation=order)
            customer_address = Address.objects.get(id=8187)
            order_scheduler_books = EvaluationBook.objects.filter(id__in=[17054, 17055, 17056, 17057])

            # Define schedule times
            start_datetime = datetime.strptime('15/04/2025 8:00 AM', '%d/%m/%Y %I:%M %p')
            end_datetime = start_datetime + timedelta(hours=10)

            # Create OrderScheduler entries
            order_schedules = [
                OrderScheduler(
                    order=order,
                    status='CONFIRMED',
                    customer_address=customer_address,
                    evaluation_details=evaluation_details,
                    start_at=start_datetime,
                    end_at=end_datetime,
                    order_scheduler_book=book,
                    no_of_cleaners=10,
                    cleaning_hours=10,
                    hourly_cleaning_duration=1
                ) for book in order_scheduler_books
            ]

            OrderScheduler.objects.bulk_create(order_schedules)
            self.stdout.write(self.style.SUCCESS('Successfully created OrderScheduler entries'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
