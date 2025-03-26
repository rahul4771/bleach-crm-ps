from django.core.management.base import BaseCommand
from django.utils import timezone
from order.models import Order


class Command(BaseCommand):
    help = "Generates missing invoice numbers for the latest orders based on previous valid invoices."

    def handle(self , *args , **kwargs):
        while True:
            # Get the latest order without an invoice_no
            latest_order = Order.objects.filter(is_active=True).order_by('-id').first()

            if not latest_order or latest_order.invoice_no:
                break  # Exit if no order found or latest order has a valid invoice_no

            # Find the last valid invoice_no from previous orders
            last_valid_order = Order.objects.filter(is_active=True , invoice_no__isnull=False).exclude(
                id=latest_order.id).order_by('-id').first()

            if last_valid_order:
                last_invoice_no = last_valid_order.invoice_no
            else:
                last_invoice_no = f"{timezone.now().year}00001"  # Start fresh if no valid invoice exists

            current_year = str(timezone.now().year)

            if current_year == last_invoice_no[:4]:
                new_invoice_no = current_year + str(int(last_invoice_no[4:]) + 1).zfill(len(last_invoice_no[4:]))
            else:
                new_invoice_no = current_year + "00001"

            # Update latest order's invoice_no
            latest_order.invoice_no = new_invoice_no
            latest_order.save(update_fields=['invoice_no'])
