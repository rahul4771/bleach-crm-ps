from django.core.management.base import BaseCommand
from bleachinventory.models import InventoryItem, QuantityStoreDetails
from django.db.models import Sum

class Command(BaseCommand):
    def handle(self, *args, **options):
        any_item = InventoryItem.objects.all()  # Retrieve all InventoryItem instances
        for item in any_item:  # Iterate over each InventoryItem instance
            if item.item_add_type == 'quantity':  # Check if the item type is 'quantity'
                # Get the quantity details for the current item by filtering QuantityStoreDetails based on the item name
                store_counts = QuantityStoreDetails.objects.filter(quantity_item__name=item.name)
                # Aggregate the total quantity for the item, setting it to 0 if no quantities are found
                count_val = store_counts.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                old_quantity = item.total_quantity  # Store the old total quantity of the item

                # Only proceed if the new aggregated quantity is different from the old quantity
                if float(old_quantity) != float(count_val):
                    # Print the item name, old quantity, and the new quantity for logging/debugging purposes
                    print(f"item name - {item.name} - old quantity: {old_quantity} || updated quantity: {item.total_quantity}")
                    item.total_quantity = count_val  # Update the item's total quantity with the new aggregated quantity
                    item.save()  # Save the changes to the database
                else:
                    print("already updated!!")  # Print a message if the quantities are already up-to-date
