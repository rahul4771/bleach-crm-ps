from django.core.management.base import BaseCommand
from bleachinventory.models import InventoryItem, QuantityStoreDetails
from django.db.models import Sum

class Command(BaseCommand):
    def handle(self, *args, **options):
        any_item = InventoryItem.objects.all()
        count_val = 0
        for item in any_item:
            if item.item_add_type == 'quantity':
                store_counts = QuantityStoreDetails.objects.filter(quantity_item__name=item.name)
                count_val = store_counts.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
            old_quantity = item.total_quantity
            item.total_quantity = count_val
            item.save()
            print(f"item name - {item.name} - quantity-{old_quantity} || updated - {item.total_quantity}")




