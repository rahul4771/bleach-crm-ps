from django.core.management.base import BaseCommand
from bleachinventory.models import InventoryItem, QuantityStoreDetails
from django.db.models import Sum

class Command(BaseCommand):
    def handle(self, *args, **options):
        any_item = InventoryItem.objects.all()
        for item in any_item:
            if item.item_add_type == 'quantity':
                store_counts = QuantityStoreDetails.objects.filter(quantity_item__name=item.name)
                count_val = store_counts.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                old_quantity = item.total_quantity

                # Only proceed if count_val is not zero and if the values are different
                if float(old_quantity) != float(count_val):
                    print(f"item name - {item.name} - old quantity: {old_quantity} || updated quantity: {item.total_quantity}")
                    item.total_quantity = count_val
                    item.save()
                else:
                    pass
