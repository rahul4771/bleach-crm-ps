from django.core.management.base import BaseCommand
from django.utils import timezone
from order.models import Order


class Command(BaseCommand):
    help = "Generates missing invoice numbers for the latest orders based on previous valid invoices."

    def handle(self , *args , **kwargs):
        reference_order_no = "BLC20250310182"  # The reference order
        reference_order = Order.objects.filter(order_no=reference_order_no).first()
        last_invoice_no = Order.objects.filter(
            invoice_no__isnull=False , id__lte=reference_order.id
        ).order_by('-id').first().invoice_no
        updated_last_invoice_no = ""
        current_year = str(timezone.now().year)
        orders_to_update = Order.objects.filter(id__gt=reference_order.id).exclude(invoice_no__isnull=True).order_by(
            'id')
        for o in orders_to_update:
            if not updated_last_invoice_no:
                new_invoice_no = (
                    str(timezone.now().year) + str(int(last_invoice_no[4:]) + 1).zfill(
                        len(last_invoice_no[4:])) if last_invoice_no and current_year == last_invoice_no[:4]
                    else current_year + '00001'
                )
                updated_last_invoice_no = new_invoice_no
                o.invoice_no = new_invoice_no
                o.save()
            else:
                new_invoice_no = (
                    str(timezone.now().year) + str(int(updated_last_invoice_no[4:]) + 1).zfill(
                        len(updated_last_invoice_no[
                            4:])) if updated_last_invoice_no and current_year == updated_last_invoice_no[:4]
                    else current_year + '00001'
                )
                updated_last_invoice_no = new_invoice_no
                o.invoice_no = new_invoice_no
                o.save()
