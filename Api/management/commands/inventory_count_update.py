from bleachinventory.models import InventoryItem,QuantityStoreDetails
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'INV COUNT UPDATE'
    def handle(self, *args, **kwargs):
        items= [
            {
            "Item Code": "MSPPHD102",
            "Item Discription": "SAFETY CAP BLUE",
            "Store Actual SOH": 3
            },
            {
            "Item Code": "MSPPBD103",
            "Item Discription": "SAFETY BELT",
            "Store Actual SOH": 5
            },
            {
            "Item Code": "MSSETX101",
            "Item Discription": "APPLICATOR CLOTH 35CM",
            "Store Actual SOH": 24
            },
            {
            "Item Code": "EQTLSQ101",
            "Item Discription": "WINDOW SQUEEZEE 35CM",
            "Store Actual SOH": 72
            },
            {
            "Item Code": "EQTLHL101",
            "Item Discription": "APPLICATOR T HOLDER 35CM",
            "Store Actual SOH": 30
            },
            {
            "Item Code": "EQTLBU101",
            "Item Discription": "BUCKET",
            "Store Actual SOH": 24
            },
            {
            "Item Code": "EQTLSQ102",
            "Item Discription": "FLOOR SQUEEZE 44CM",
            "Store Actual SOH": 56
            },
            {
            "Item Code": "EQTLBU102",
            "Item Discription": "FULL SET TTS WRINGER BUCKET",
            "Store Actual SOH": 3
            },
            {
            "Item Code": "EQTLLD102",
            "Item Discription": "ALUMINUM LONG LADDER",
            "Store Actual SOH": 5
            },
            {
            "Item Code": "MSHOWL101",
            "Item Discription": 'LOCTEK 32"-65" TV WALL MOUNT BRACKET',
            "Store Actual SOH": 2
            },
            {
            "Item Code": "EQTLLD101",
            "Item Discription": "ALUMINUM SHORT LADDER",
            "Store Actual SOH": 10
            },
            {
            "Item Code": "EQACEX101",
            "Item Discription": "BRENNENSTUHL 50 MTRS. 3 SWITCH EXTENSION CORD",
            "Store Actual SOH": 2
            },
            {
            "Item Code": "EQACPD103",
            "Item Discription": '3M "17 Red pad',
            "Store Actual SOH": 25
            },
            {
            "Item Code": "EQACPD105",
            "Item Discription": '3M "17 Black pad',
            "Store Actual SOH": 0
            },
            {
            "Item Code": "CHRCPN101",
            "Item Discription": "THINNER - PAINT REMOVER",
            "Store Actual SOH": 0
            },
            {
            "Item Code": "XXXXXX101",
            "Item Discription": "All purpose cleaner 5L",
            "Store Actual SOH": 32
            },
            {
            "Item Code": "XXXXXX102",
            "Item Discription": "Glass cleaner 5L",
            "Store Actual SOH": 3
            },
            {
            "Item Code": "XXXXXX103",
            "Item Discription": "Cement remover 5L",
            "Store Actual SOH": 0
            },
            {
            "Item Code": "XXXXXX105",
            "Item Discription": "Air Freshener 5L",
            "Store Actual SOH": 12
            },
            {
            "Item Code": "XXXXXX109",
            "Item Discription": "Spot remover 1L",
            "Store Actual SOH": 7
            },
            {
            "Item Code": "XXXXXX110",
            "Item Discription": "Carpet shampoo 5L",
            "Store Actual SOH": 35
            },
            {
            "Item Code": "XXXXXX115",
            "Item Discription": "Degreaser 5L",
            "Store Actual SOH": 15
            },
            {
            "Item Code": "XXXXXX117",
            "Item Discription": "Air Freshener 1L",
            "Store Actual SOH": 2
            },
            {
            "Item Code": "BLFGPK120",
            "Item Discription": "SPECIAL CARE PACK CLOTHS & PADS",
            "Store Actual SOH": 0
            }
        ]

        for item in items:
            inventoryitem = InventoryItem.objects.filter(item_code__exact=item['Item Code']).first()
            inventoryitem.total_quantity=item['Store Actual SOH']
            inventoryitem.save()

            QuantityStoreDetails.objects.filter(quantity_item=inventoryitem,item_store__store_name__exact='Warehouse').update(quantity=item['Store Actual SOH'])
            QuantityStoreDetails.objects.filter(quantity_item=inventoryitem,item_store__store_name__exact='MAIN OFFICE').update(quantity=0)

            print(inventoryitem.total_quantity,inventoryitem.name)