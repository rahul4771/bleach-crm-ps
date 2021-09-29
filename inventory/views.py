from django.shortcuts import render,redirect
from django.views import View
from bleach_crm_ps.permissions import IsInventoryAdmin,IsInventoryAdminUser
from inventory.models import ItemHistory,Category,Segment,Line,Attribute,AttributeValue,ItemAttributes,InventoryItem,ItemUnit,InventoryItemImages,Bundle,BundleItems, BundleItemUnits, Store,Supplier,SupplierItems,ServiceRecipe,ServiceRecipeIngredients,ServiceRecipeItems,PurchaseOrder,PurchaseOrderItems
from django.contrib import messages
import re
from datetime import date,datetime,timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField,Prefetch
from order.models import OrderScheduler
from senior_team_leader.models import CleaningTeam,CleaningTeamMember
from evaluator.models import EvaluationBookSection,EvaluationSectionKeynote,EvaluationSectionAddons
# Create your views here.

class InventoryHome(IsInventoryAdmin,View):
    def get(self,request):
        items = InventoryItem.objects.filter(status=True)
        recent_items = items.order_by('-id')
        purchase_items = items.filter(Q(item_status='out_of_stock') | Q(item_status='about_to_finish')).prefetch_related(Prefetch('unit_item',queryset=ItemUnit.objects.all(),to_attr='units'))
        return render(request,'inventory/home.html',{"recent_items":recent_items,"purchase_items":purchase_items})

# Category.
class InventoryCategory(IsInventoryAdmin,View):
    def get(self,request):

        search = request.GET.get('search')

        if search:
            categories       = Category.objects.filter(Q(name__icontains=search)|Q(category_code__icontains=search)).annotate(segments_count=Count('segment_category'),lines_count=Count('line_category'))
        else:
            categories       = Category.objects.all().annotate(segments_count=Count('segment_category'),lines_count=Count('line_category'))
        
        category_latest  = categories.last()
        if category_latest:
            code_number  =  int(re.findall(r'(\d+)', category_latest.category_code)[0]) + 1
            new_category_code = 'CAT'+str(code_number)
        else:
            new_category_code = 'CAT9001'

        

        return render(request,'inventory/category.html',{"categories":categories,"new_category_code":new_category_code,"search_query":search})

    def post(self,request):

        action = request.POST.get('action')

        if action == 'add_category':
            category_name   = request.POST.get('category_name')
            category_status = request.POST.get('category_status')
            category_id = request.POST.get('category_id')

            category_id_exists = Category.objects.filter(category_id=category_id).first()
            if category_id_exists:
                messages.error(request,"Category Id exists !")

            else:
                category_latest = Category.objects.all().last()
                if category_latest:
                    code_number  =  int(re.findall(r'(\d+)', category_latest.category_code)[0]) + 1
                    category_code = 'CAT'+str(code_number)
                else:
                    category_code = 'CAT9001'

                Category.objects.create(name=category_name,category_code=category_code,category_id=category_id,status=category_status)

                messages.success(request,"Category Added Successfully !")

        if action == 'edit_category':
            print("edit")
            # category = Category.objects.get(id=int(category_id))
            category_id = request.POST.get('category_edit_id')
            name     = request.POST.get('category_name')
            status     = request.POST.get('category_status')
            category = Category.objects.get(id=int(category_id))
            category.name     = name
            category.status   = status
            category.save()
            messages.success(request,"Category Updated Successfully !")
        
        if action == 'delete_category':
            category_id = request.POST.get('category_id')
            Category.objects.get(id=int(category_id)).delete()
            messages.success(request,"Category Deleted Successfully !")

        return redirect('inventory:inventory-category')

# Attribute.
class InventoryAttribute(IsInventoryAdmin,View):
    def get(self,request):
        search = request.GET.get('search')

        categories = Category.objects.all()
        
        if search:
            attributes = Attribute.objects.filter(name__icontains=search).annotate(value_count=Count('value_attribute'))
        else:
            attributes = Attribute.objects.all().annotate(value_count=Count('value_attribute'))

        #PAGINATION CLIENTS
        no_of_entries = request.GET.get('no_of_entries')
        if not no_of_entries:
            no_of_entries = 20

        page = request.GET.get('page',1)
        paginator=Paginator(attributes,no_of_entries)
        try:
            attributes=paginator.page(page)
        except PageNotAnInteger:
            attributes=paginator.page(1)
        except EmptyPage:
            attributes = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = attributes.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # Get our new page range. In the latest versions of Django page_range returns
        # an iterator. Thus pass it to list, to make our slice possible again.
        page_range = list(paginator.page_range)[start_index:end_index]
        entry_per_page=(attributes.end_index())-(attributes.start_index())+1

        return render(request,'inventory/attribute.html',{"attributes":attributes,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"search_query":search,"categories":categories})

    def post(self,request):
        action = request.POST.get('action')

        if action == 'add_attribute':
            # category = Category.objects.get(id=int(category_id))
            name     = request.POST.get('attribute')
            category_id = request.POST.get('attribute_category')
            segment_id = request.POST.get('attribute_segment')
            line_id = request.POST.get('attribute_line')
            # attribute_type     = request.POST.get('attribute_type')
            status     = request.POST.get('status')

            print(category_id,segment_id,line_id,"print vals")

            if category_id:
                category = Category.objects.get(id=int(category_id))
            else:
                category = None

            if segment_id:
                segment = Segment.objects.get(id=int(segment_id))
            else:
                segment = None

            if line_id:
                line = Line.objects.get(id=int(line_id))
            else:
                line = None


            Attribute.objects.create(attribute_category=category,attribute_segment=segment,attribute_line=line,name=name,status=status)
            messages.success(request,"Attribute Added Successfully !")

        if action == 'edit_attribute':
            print("edit")
            # category = Category.objects.get(id=int(category_id))
            attribute_id = request.POST.get('attribute_edit_id')
            name     = request.POST.get('attribute')
            attribute_type     = request.POST.get('attribute_type')
            attribute_category = request.POST.get('attribute_category')
            attribute_segment  = request.POST.get('attribute_segment')
            attribute_line     = request.POST.get('attribute_line')
            status     = request.POST.get('status')

            print(attribute_id,name,attribute_type,status,"lop")

            attribute = Attribute.objects.get(id=int(attribute_id))
            category = Category.objects.get(id=int(attribute_category))
            segment = Segment.objects.get(id=int(attribute_segment))
            line = Line.objects.get(id=int(attribute_line))

            # attribute.category = category
            attribute.name     = name
            attribute.attribute_type = attribute_type

            if category:
                attribute.attribute_category = category
            if segment:
                attribute.attribute_segment = segment
            if line:
                attribute.attribute_line = line

            attribute.status   = status
            attribute.save()
            messages.success(request,"Attribute Updated Successfully !")

        if action == 'delete_attribute':
            attribute_id = request.POST.get('object_id')
            Attribute.objects.get(id=int(attribute_id)).delete()
            messages.success(request,"Attribute Deleted Successfully !")

        if action == 'add_value':
            attribute_id = request.POST.get('value_attribute_id')
            value_name   = request.POST.get('value_name')
            value_status = request.POST.get('value_status')

            attribute = Attribute.objects.get(id=int(attribute_id))

            AttributeValue.objects.create(attribute=attribute,name=value_name,status=value_status)

            messages.success(request,"Value Added Successfully !")

        if action == 'edit_value':
            value_id = request.POST.get('edit_value_id')
            value_name   = request.POST.get('value_name')
            value_status = request.POST.get('value_status')

            value = AttributeValue.objects.get(id=int(value_id))

            value.name = value_name
            value.status = value_status
            value.save()

            messages.success(request,"Value Updated Successfully !")

        if action == 'delete_value':
            value_id = request.POST.get('object_id')
            AttributeValue.objects.get(id=int(value_id)).delete()
            messages.success(request,"Value Deleted Successfully !")

        return redirect('inventory:inventory-attribute')
# value.
class InventoryValue(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/value.html',{})

# bundle.
class InventoryBundle(IsInventoryAdmin,View):
    def get(self,request):

        items = InventoryItem.objects.all()

        search = request.GET.get('search')

        if search:
            bundles       = Bundle.objects.filter(Q(name__icontains=search)|Q(bundle_code__icontains=search)).prefetch_related(Prefetch('item_bundle',queryset=BundleItems.objects.all(),to_attr='bundle_items')).annotate(items_count=Count('item_bundle'))
        else:
            bundles       = Bundle.objects.all().prefetch_related(Prefetch('item_bundle',queryset=BundleItems.objects.all(),to_attr='bundle_items')).annotate(items_count=Count('item_bundle'))
        
        bundle_latest  = bundles.last()
        if bundle_latest:
            code_number  =  int(re.findall(r'(\d+)', bundle_latest.bundle_code)[0]) + 1
            new_bundle_code = 'BUNDLE'+str(code_number)
        else:
            new_bundle_code = 'BUNDLE9001'

        #PAGINATION CLIENTS
        no_of_entries = request.GET.get('no_of_entries')
        if not no_of_entries:
            no_of_entries = 20

        page = request.GET.get('page',1)
        paginator=Paginator(bundles,no_of_entries)
        try:
            bundles=paginator.page(page)
        except PageNotAnInteger:
            bundles=paginator.page(1)
        except EmptyPage:
            bundles = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = bundles.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # Get our new page range. In the latest versions of Django page_range returns
        # an iterator. Thus pass it to list, to make our slice possible again.
        page_range = list(paginator.page_range)[start_index:end_index]
        entry_per_page=(bundles.end_index())-(bundles.start_index())+1

        return render(request,'inventory/bundle.html',{"bundle_code":new_bundle_code,"bundles":bundles,"items":items,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,})

    def post(self,request):
        action =request.POST.get('action')

        if action == 'add_bundle':
            name = request.POST.get('bundle_name')

            bundles       = Bundle.objects.all()
            bundle_latest  = bundles.last()
            if bundle_latest:
                code_number  =  int(re.findall(r'(\d+)', bundle_latest.bundle_code)[0]) + 1
                new_bundle_code = 'BUNDLE'+str(code_number)
            else:
                new_bundle_code = 'BUNDLE9001'

            status = request.POST.get('bundle_status')

            Bundle.objects.create(name=name,bundle_code=new_bundle_code,status=status)

            messages.success(request,"Bundle Created Successfully !")

        if action == 'edit_bundle':
            name = request.POST.get('bundle_name')
            status = request.POST.get('bundle_status')
            bundle_id = request.POST.get('bundle_edit_id')

            bundle = Bundle.objects.get(id=int(bundle_id))

            bundle.name = name
            bundle.status = status
            bundle.save()

            messages.success(request,"Bundle updated Successfully !")

        if action == 'delete_bundle':
            bundle_id = request.POST.get('bundle_delete_id')

            bundle = Bundle.objects.prefetch_related(Prefetch('item_bundle',queryset=BundleItems.objects.all().prefetch_related(Prefetch('bundle_unit_bundle_item',queryset=BundleItemUnits.objects.all(),to_attr='bundle_item_units')),to_attr='bundle_items')).get(id=int(bundle_id))
            
            for item in bundle.bundle_items:
                for unit in item.bundle_item_units:
                    item_unit = ItemUnit.objects.get(id=int(unit.item_unit.id))
                    item_unit.status = 'active'
                    item_unit.save()

            bundle.delete()
            
            messages.success(request,"Bundle deleted Successfully !")

        if action == 'add_item':
            bundle_id = request.POST.get('item_bundle_id')
            item = request.POST.get('item')
            item_count = request.POST.get('item_count')

            bundle = Bundle.objects.get(id=int(bundle_id))
            inventory_item = InventoryItem.objects.get(id=int(item))

            inventory_item_unit_count = ItemUnit.objects.filter(item=inventory_item).count()

            total_item_price = 0

            used_units = []

            if int(inventory_item_unit_count) >= int(item_count) :
                selected_units = ItemUnit.objects.filter(item=inventory_item,status='active')[:int(item_count)]

                for unit in selected_units:
                    total_item_price += float(unit.unit_price)
                    unit.status = 'out_of_order'
                    unit.save()
                    used_units.append(unit)

                item_count = item_count

            else:
                selected_units = ItemUnit.objects.filter(item=inventory_item,status='active')[:int(inventory_item_unit_count)]

                for unit in selected_units:
                    total_item_price += float(unit.unit_price)
                    unit.status = 'out_of_order'
                    unit.save()
                    used_units.append(unit)

                item_count = inventory_item_unit_count

            bundleitem = BundleItems.objects.create(bundle=bundle,item=inventory_item,item_price=total_item_price,item_count=item_count)

            for unit in used_units:
                BundleItemUnits.objects.create(bundle_item=bundleitem,item_unit=unit,unit_price=unit.unit_price)
            
            bundle.bundle_items_count += int(item_count)
            bundle_price = bundle.bundle_price
            bundle.bundle_price = float(bundle_price)+float(total_item_price)
            bundle.save()
            
            messages.success(request,"Item Added successfully !")

        
        if action == 'edit_item':
            bundle_id = request.POST.get('item_bundle_id')
            bundle_item_id = request.POST.get('edit_item_id')
            item = request.POST.get('item')
            item_count = request.POST.get('item_count')

            bundle = Bundle.objects.get(id=int(bundle_id))
            inventory_item = InventoryItem.objects.get(id=int(item))

            inventory_item_unit_count = ItemUnit.objects.filter(item=inventory_item).count()

            total_item_price = 0

            used_units = []

            if int(inventory_item_unit_count) >= int(item_count) :
                selected_units = ItemUnit.objects.filter(item=inventory_item,status='active')[:int(item_count)]

                for unit in selected_units:
                    total_item_price += float(unit.unit_price)
                    unit.status = 'out_of_order'
                    unit.save()
                    used_units.append(unit)

                item_count = item_count

            else:
                selected_units = ItemUnit.objects.filter(item=inventory_item,status='active')[:int(inventory_item_unit_count)]

                for unit in selected_units:
                    total_item_price += float(unit.unit_price)
                    unit.status = 'out_of_order'
                    unit.save()
                    used_units.append(unit)

                item_count = inventory_item_unit_count

            bundleitem = BundleItems.objects.get(id=int(bundle_item_id))

            #clearing old units
            old_bundleitemunits = BundleItemUnits.objects.filter(bundle_item=bundleitem)
            for unit in old_bundleitemunits:
                item_unit = ItemUnit.objects.get(id=int(unit.item_unit.id))
                item_unit.status = 'active'
                item_unit.save()

            # bundle.bundle_items_count = int(bundleitem.bundle.bundle_items_count) - 1
            bundle.bundle_price = float(bundleitem.bundle.bundle_price) - float(bundleitem.item_price)
            bundle.save()
            
            BundleItemUnits.objects.filter(bundle_item=bundleitem).delete()
            
            #removing item price from bundle
            # bundle.bundle_price = float(bundle.bundle_price) - float(bundleitem.item_price)
            # bundle.save()

            #saving new bundle item
            bundleitem.item = inventory_item
            bundleitem.item_price = total_item_price
            bundleitem.item_count = item_count
            bundleitem.save()

            #creating new units
            for unit in used_units:
                BundleItemUnits.objects.create(bundle_item=bundleitem,item_unit=unit,unit_price=unit.unit_price)
            
            #updating bundle
            bundle.bundle_items_count += int(item_count)
            bundle_price = bundle.bundle_price
            bundle.bundle_price = float(bundle_price)+float(total_item_price)
            bundle.save()
            
            messages.success(request,"Item Updated successfully !")
        
        
        if action == 'delete_item':
            item_id = request.POST.get('bundle_delete_id')
            bundleitem = BundleItems.objects.prefetch_related(Prefetch('bundle_unit_bundle_item',queryset=BundleItemUnits.objects.all(),to_attr='bundle_units')).get(id=int(item_id))
            bundle = Bundle.objects.get(id=int(bundleitem.bundle.id))

            for unit in bundleitem.bundle_units:
                item_unit = ItemUnit.objects.get(id=int(unit.item_unit.id))
                item_unit.status = 'active'
                item_unit.save()

                # bundleitem.item_price = float(bundleitem.item_price) - float(unit.unit_price)
                # bundleitem.item_count = int(bundleitem.item_count) - 1

            bundle.bundle_items_count = int(bundleitem.bundle.bundle_items_count) - int(bundleitem.item_count)
            bundle.bundle_price = float(bundleitem.bundle.bundle_price) - float(bundleitem.item_price)
            bundle.save()

            bundleitem.delete()
            messages.success(request,"Item Deleted successfully !")


        return redirect('inventory:inventory-bundle')

class InventoryItems(IsInventoryAdmin,View):
    def get(self,request,item_id):
        inventory_item = InventoryItem.objects.prefetch_related(Prefetch('image_item',queryset=InventoryItemImages.objects.all(),to_attr='item_images')).annotate(unit_count=Sum(Case(When(unit_item__status='active',then=1),default=0,output_field=IntegerField())),total_unit_price=Sum(Case(When(unit_item__status='active',then='unit_item__unit_price'),default=0,output_field=FloatField()))).get(id=item_id)
        categories = Category.objects.all()
        item_units = ItemUnit.objects.filter(item=inventory_item)
        item_history = ItemHistory.objects.filter(item=inventory_item)

        stores = Store.objects.filter(status=True)

        available_item_units = item_units.filter(status='active').count()
        reserve_units = inventory_item.reserve_count

        if int(available_item_units) < int(reserve_units) and int(available_item_units) > 0:
            inventory_item.item_status = 'about_to_finish'
        elif int(available_item_units) == 0 :
            inventory_item.item_status = 'out_of_stock'
        else:
            inventory_item.item_status = 'available'
        inventory_item.save()

        attributes = Attribute.objects.filter(attribute_category=inventory_item.item_category,attribute_segment=inventory_item.item_segment,attribute_line=inventory_item.item_line,status=True).prefetch_related(Prefetch('value_attribute',queryset=AttributeValue.objects.filter(status=True),to_attr='attribute_values'))

        try:
            item_attributes = ItemAttributes.objects.filter(item=inventory_item)
        except:
            item_attributes = None

        units       = ItemUnit.objects.all()
        unit_latest  = units.last()
        if unit_latest:
            code_number  =  int(re.findall(r'(\d+)', unit_latest.unit_code)[0]) + 1
            new_unit_code = 'UNIT'+str(code_number)
        else:
            new_unit_code = 'UNIT9001'

        return render(request,'inventory/item.html',{"stores":stores,"item_attributes":item_attributes,"inventory_item":inventory_item,"attributes":attributes,"categories":categories,"item_units":item_units,"item_history":item_history,"new_unit_code":new_unit_code})

    def post(self,request,item_id):
        action =request.POST.get('action')

        if action == 'edit_item_details':
            category_id = request.POST.get('item_category')
            segment_id = request.POST.get('item_segment')
            line_id = request.POST.get('item_line')
            print(category_id,segment_id,line_id,"ids")

            if category_id:
                category = Category.objects.get(id=int(category_id))
            else:
                category = None

            if segment_id:
                segment = Segment.objects.get(id=int(segment_id))
            else:
                segment = None

            if line_id:
                line = Line.objects.get(id=int(line_id))
            else:
                line = None

            item = InventoryItem.objects.get(id=item_id)

            item.name = request.POST.get('item_name')
            item.item_category = category
            item.item_segment = segment
            item.item_line = line
            item.description = request.POST.get('description')
            item.reserve_count = request.POST.get('reserve')
            item.save()

            messages.success(request,"Item Details Updated !")

        if action == 'attribute_edit':
            attribute_ids = request.POST.getlist('attribute_ids')
            print(attribute_ids,"ids")

            item = InventoryItem.objects.get(id=item_id)

            for attr_id in attribute_ids:
                attribute = Attribute.objects.get(id=int(attr_id))
                attribute_value_id = request.POST.get('attribute_value'+attr_id+'')

                print(attribute,attribute_value_id,"cad")
                attribute_value = AttributeValue.objects.get(id=int(attribute_value_id))

                ItemAttributes.objects.get_or_create(item=item,attribute=attribute)
                item_attribute = ItemAttributes.objects.get(item=item,attribute=attribute)
                item_attribute.attribute_value = attribute_value
                item_attribute.save()
                
            messages.success(request,"Attributes updated !")


        if action == "add_unit":
            store_id = request.POST.get('store')
            serial_number = request.POST.get('serial_number')
            purchase_date = request.POST.get('purchase_date')
            expiry_date = request.POST.get('expiry_date')
            
            no_expiry = request.POST.get('no_expiry')
            if no_expiry == 'on':
                expiry = True
            else:
                expiry = True
            unit_price = request.POST.get('unit_price')
            status = request.POST.get('unit_status')

            store = Store.objects.get(id=int(store_id))

            item = InventoryItem.objects.get(id=item_id)

            item_code = item.item_code

            latest_unit_code = ItemUnit.objects.filter(unit_code__contains=item_code).last()

            if latest_unit_code:
                code = latest_unit_code.unit_code.split("-")[1]
                new_unit_code = item_code + '-' + str(int(code)+1)
            else:
                new_unit_code = item_code + '-1'
            print(new_unit_code,"lop")

            if not expiry_date:
                ItemUnit.objects.create(
                item = item,
                name='name',
                store=store,
                unit_code = new_unit_code,
                unit_serial_number = serial_number,
                purchase_date = purchase_date,
                no_expiry = expiry,
                unit_price = unit_price,
                status = status
                )
            else:
                ItemUnit.objects.create(
                item = item,
                name='name',
                store=store,
                unit_code = new_unit_code,
                unit_serial_number = serial_number,
                purchase_date = purchase_date,
                expiry_date = expiry_date,
                no_expiry = expiry,
                unit_price = unit_price,
                status = status
                )
            messages.success(request,"Unit Added Successfully !")

        if action == "edit_unit":
            unit_id = request.POST.get('edit_unit_id')
            store_id = request.POST.get('store')
            serial_number = request.POST.get('serial_number')
            purchase_date = request.POST.get('purchase_date')
            expiry_date = request.POST.get('expiry_date')
            no_expiry = request.POST.get('no_expiry')
            if no_expiry == 'on':
                expiry = True
            else:
                expiry = True
            unit_price = request.POST.get('unit_price')
            status = request.POST.get('unit_status')
            print(no_expiry,"nox")

            item = InventoryItem.objects.get(id=item_id)
            store = Store.objects.get(id=int(store_id))

            unit = ItemUnit.objects.get(id=int(unit_id))
            
            unit.store = store
            unit.unit_serial_number = serial_number
            unit.purchase_date = purchase_date
            if expiry_date:
                unit.expiry_date = expiry_date
            unit.expiry = expiry
            unit.unit_price = unit_price
            unit.status = status
            unit.save()

            messages.success(request,"Unit Updated Successfully !")

        if action == 'delete_unit':
            unit_id = request.POST.get('unit_id_delete')
            unit = ItemUnit.objects.get(id=int(unit_id)).delete()
            messages.success(request,"Unit Deleted Successfully !")

        if action == 'add_image':
            image = request.FILES.get('item_image')

            inventory_item = InventoryItem.objects.get(id=item_id)

            inventory_images = InventoryItemImages.objects.filter(inventory_item__id=item_id)
            
            if inventory_images:
                InventoryItemImages.objects.create(inventory_item=inventory_item,item_image=image)
            else:
                InventoryItemImages.objects.create(inventory_item=inventory_item,item_image=image,is_default_image=True)

            messages.success(request,"Image Added successfully!")

        if action == 'set_default_image':
            image_id = request.POST.get('imageid')

            inventory_item_image = InventoryItemImages.objects.get(id=image_id)
            InventoryItemImages.objects.filter(inventory_item__id=item_id).update(is_default_image=False)
            inventory_item_image.is_default_image = True
            inventory_item_image.save()

            messages.success(request,"Image set as default!")

        if action == 'delete_image':
            image_id = request.POST.get('item_image_id')

            delete_image = InventoryItemImages.objects.get(id=image_id)
            if delete_image.is_default_image == True:
                default_image = InventoryItemImages.objects.filter(inventory_item__id=item_id).first()
                if default_image:
                    default_image.is_default_image = True
                    default_image.save()
                else:
                    pass
            else:
                pass

            delete_image.delete()

            messages.success(request,"Image Deleted successfully!")

        return redirect('inventory:inventory-item',item_id)

class InventorySupplier(IsInventoryAdmin,View):
    def get(self,request):

        search = request.GET.get('search')

        if search:
            suppliers = Supplier.objects.filter(Q( Q(supplier_name__icontains=search) | Q(supplier_id__icontains=search) | Q(contact__icontains=search) ))
        else:
            suppliers = Supplier.objects.all()

        items = InventoryItem.objects.all()
        
        suppliers_latest  = suppliers.last()
        if suppliers_latest:
            code_number  =  int(re.findall(r'(\d+)', suppliers_latest.supplier_id)[0]) + 1
            new_supplier_id = 'SUP'+str(code_number)
        else:
            new_supplier_id = 'SUP9001'

        #PAGINATION CLIENTS
        no_of_entries = request.GET.get('no_of_entries')
        if not no_of_entries:
            no_of_entries = 20

        page = request.GET.get('page',1)
        paginator=Paginator(suppliers,no_of_entries)
        try:
            suppliers=paginator.page(page)
        except PageNotAnInteger:
            suppliers=paginator.page(1)
        except EmptyPage:
            suppliers = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = suppliers.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # Get our new page range. In the latest versions of Django page_range returns
        # an iterator. Thus pass it to list, to make our slice possible again.
        page_range = list(paginator.page_range)[start_index:end_index]
        entry_per_page=(suppliers.end_index())-(suppliers.start_index())+1

        return render(request,'inventory/supplier.html',{"suppliers":suppliers,"supplier_id":new_supplier_id,"items":items,"search_query":search,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries})

    def post(self,request):
        action =request.POST.get('action')

        if action == 'add_supplier':
            # category = Category.objects.get(id=int(category_id))
            name     = request.POST.get('supplier_name')
            contact = request.POST.get('contact')
            other_contact = request.POST.get('other_contact')
            address = request.POST.get('address')
            terms = request.POST.get('terms')
            status     = request.POST.get('status')

            suppliers    = Supplier.objects.all()
        
            supplier_latest  = suppliers.last()
            if supplier_latest:
                code_number  =  int(re.findall(r'(\d+)', supplier_latest.supplier_id)[0]) + 1
                new_supplier_id = 'SUP'+str(code_number)
            else:
                new_supplier_id = 'SUP9001'

            supplier_name_check = Supplier.objects.filter(supplier_name__icontains=name).first()

            if supplier_name_check:
                messages.error(request,"Supplier Name Exists !")
            else:
                Supplier.objects.create(supplier_name=name,supplier_id=new_supplier_id,contact=contact,address=address,terms=terms,status=status)
                messages.success(request,"Supplier Added Successfully !")

        if action == 'edit_supplier':
            supplier_id = request.POST.get('supplier_edit_id')
            name     = request.POST.get('supplier_name')
            contact = request.POST.get('contact')
            other_contact = request.POST.get('other_contact')
            address = request.POST.get('address')
            terms = request.POST.get('terms')
            status     = request.POST.get('status')

            supplier = Supplier.objects.get(id=int(supplier_id))

            supplier_name_check = Supplier.objects.filter(supplier_name__icontains=name).exclude(id=int(supplier_id)).first()

            if supplier_name_check:
                messages.error(request,"Supplier Name Exists !")
            else:
                supplier.supplier_name= name
                supplier.contact = contact
                supplier.other_contact = other_contact
                supplier.address = address
                supplier.terms = terms
                supplier.status = status

                supplier.save()
                messages.success(request,"Supplier Updated Successfully !")

        if action == 'delete_supplier':
            supplier_id = request.POST.get('supplier_id_delete')
            supplier = Supplier.objects.get(id=int(supplier_id)).delete()
            messages.success(request,"Supplier Deleted Successfully !")

        if action == 'add_item':
            print("pop")
            supplier_id = request.POST.get('item_supplier_id')
            item = request.POST.get('item')
            item_price = request.POST.get('supplier_item_price')
            item_count = request.POST.get('supplier_item_count')

            supplier_items_latest = SupplierItems.objects.all().last()

            if supplier_items_latest:
                code_number  =  int(re.findall(r'(\d+)', supplier_items_latest.supplier_item_id)[0]) + 1
                new_supplier_item_id = 'SPITM'+str(code_number)
            else:
                new_supplier_item_id = 'SPITM9001'

            supplier = Supplier.objects.get(id=int(supplier_id))

            product = InventoryItem.objects.get(id=int(item))

            SupplierItems.objects.create(supplier=supplier,item=product,item_price=item_price,supplier_item_id=new_supplier_item_id,item_count=item_count)

            messages.success(request,"Item Added Successfully !")

        if action == 'edit_item':
            print("ppp")
            supplier_item_id = request.POST.get('item_edit_id')
            item = request.POST.get('item')
            item_price = request.POST.get('supplier_item_price')
            item_count = request.POST.get('supplier_item_count')

            supplieritem = SupplierItems.objects.get(id=int(supplier_item_id))

            product = InventoryItem.objects.get(id=int(item))

            print(supplieritem,product,"kop")

            supplieritem.item = product
            supplieritem.item_price = item_price
            supplieritem.item_count = item_count
            supplieritem.save()

            messages.success(request,"Item Updated Successfully !")

        if action == 'delete_item':
            supplier_item_id = request.POST.get('supplier_id_delete')

            supplieritem = SupplierItems.objects.get(id=int(supplier_item_id)).delete()

            messages.success(request,"Item Deleted Successfully !")

        return redirect('inventory:inventory-supplier')

class InventoryStore(IsInventoryAdmin,View):
    def get(self,request):
        search = request.GET.get('search')

        if search:
            stores = Store.objects.filter(Q( Q(store_name__icontains=search) | Q(store_code__icontains=search)))
        else:
            stores = Store.objects.all()
        
        store_latest  = stores.last()
        if store_latest:
            code_number  =  int(re.findall(r'(\d+)', store_latest.store_code)[0]) + 1
            new_store_code = 'STORE'+str(code_number)
        else:
            new_store_code = 'STORE9001'

        return render(request,'inventory/store.html',{"stores":stores,"store_code":new_store_code,"search_query":search})

    def post(self,request):
        action =request.POST.get('action')

        if action == 'add_store':
            # category = Category.objects.get(id=int(category_id))
            name     = request.POST.get('store_name')
            address = request.POST.get('store_address')
            contact = request.POST.get('store_contact')
            status     = request.POST.get('store_status')

            stores    = Store.objects.all()
        
            store_latest  = stores.last()
            if store_latest:
                code_number  =  int(re.findall(r'(\d+)', store_latest.store_code)[0]) + 1
                new_store_code = 'STORE'+str(code_number)
            else:
                new_store_code = 'STORE9001'


            Store.objects.create(store_name=name,address=address,store_code=new_store_code,contact=contact,status=status)
            messages.success(request,"Store Added Successfully !")

        if action == 'edit_store':
            store_id = request.POST.get('store_edit_id')
            name     = request.POST.get('store_name')
            address = request.POST.get('store_address')
            contact = request.POST.get('store_contact')
            status     = request.POST.get('store_status')

            store = Store.objects.get(id=int(store_id))
            store.store_name = name
            store.address = address
            store.contact = contact
            store.status = status
            store.save()
            messages.success(request,"Store Updated  Successfully !")

        if action == 'delete_store':
            store_id = request.POST.get('store_id_delete')
            Store.objects.get(id=int(store_id)).delete()
            messages.success(request,"Store Deleted Successfully !")
        return redirect('inventory:inventory-store')

class InventoryInv(IsInventoryAdmin,View):
    def get(self,request):
        search = request.GET.get('search')

        if search:
            inventory_items       = InventoryItem.objects.filter(Q(name__icontains=search)|Q(item_code__icontains=search))
        else:
            inventory_items       = InventoryItem.objects.all()

        for item in inventory_items:
            available_item_units = ItemUnit.objects.filter(item=item,status='active').count()
            reserve_units = item.reserve_count

            if int(available_item_units) < int(reserve_units) and int(available_item_units) > 0:
                item.item_status = 'about_to_finish'
            elif int(available_item_units) == 0 :
                item.item_status = 'out_of_stock'
            else:
                item.item_status = 'available'
            item.save()
        
        # inventory_latest  = inventory_items.last()
        # if inventory_latest:
        #     code_number  =  int(re.findall(r'(\d+)', inventory_latest.item_code)[0]) + 1
        #     new_item_code = 'ITEM'+str(code_number)
        # else:
        #     new_item_code = 'ITEM9001'

        categories  = Category.objects.all()

        return render(request,'inventory/inventory.html',{"categories":categories,"items":inventory_items,"search_query":search,})

    def post(self,request):
        action =request.POST.get('action')

        if action == 'add_item':
            # category = Category.objects.get(id=int(category_id))
            name     = request.POST.get('item_name')
            category_id = request.POST.get('item_category')
            segment_id = request.POST.get('item_segment')
            line_id = request.POST.get('item_line')
            description = request.POST.get('item_description')
            reserve = request.POST.get('item_reserve')
            status     = request.POST.get('item_status')
            reusable     = request.POST.get('item_reusable')
            item_add_type     = request.POST.get('itemadd_type')
            unit_measure     = request.POST.get('unit_measure')

            if category_id:
                category = Category.objects.get(id=int(category_id))
            else:
                category = None

            if segment_id:
                segment = Segment.objects.get(id=int(segment_id))
            else:
                segment = None

            if line_id:
                line = Line.objects.get(id=int(line_id))
            else:
                line = None

            items    = InventoryItem.objects.all()
        
            # item_latest  = items.last()
            # if item_latest:
                # code_number  =  int(re.findall(r'(\d+)', item_latest.item_code)[0]) + 1
            #     new_item_code = 'ITEM'+str(code_number)
            # else:
            #     new_item_code = 'ITEM9001'

            # item code generation
            item_code_series = str(category.category_id)+str(segment.segment_id)+str(line.line_id)

            latest_item_code = InventoryItem.objects.filter(item_code__contains=item_code_series).last()

            if latest_item_code:
                new_item_code = item_code_series + str(int(latest_item_code.item_code[6:])+1)
            else:
                new_item_code = item_code_series + '101'
            print(new_item_code,"lop")

            inv_item = InventoryItem.objects.create(item_category=category,item_segment=segment,item_line=line,name=name,item_code=new_item_code,description=description,reserve_count=reserve,is_reusable=reusable,item_add_type=item_add_type,measuring_unit=unit_measure)
            messages.success(request,"Item Added Successfully !")
            return redirect('inventory:inventory-item',inv_item.id)

        if action == 'edit_item':
            print("edit")
            name     = request.POST.get('item_name')
            item_id = request.POST.get('item_edit_id')
            category_id = request.POST.get('item_category')
            segment_id = request.POST.get('item_segment')
            line_id = request.POST.get('item_line')
            description = request.POST.get('item_description')
            reserve = request.POST.get('item_reserve')
            status     = request.POST.get('item_status')
            reusable     = request.POST.get('item_reusable')

            if category_id:
                category = Category.objects.get(id=int(category_id))
            else:
                category = None

            if segment_id:
                segment = Segment.objects.get(id=int(segment_id))
            else:
                segment = None

            if line_id:
                line = Line.objects.get(id=int(line_id))
            else:
                line = None

            item = InventoryItem.objects.get(id=int(item_id))

            current_item_code_series = item.item_code[:6]

            new_item_code_series = str(category.category_id)+str(segment.segment_id)+str(line.line_id)

            # checking if code series changed
            if current_item_code_series == new_item_code_series:
                pass
                print("match")
            else:

                latest_item_code = InventoryItem.objects.filter(item_code__contains=new_item_code_series).last()

                if latest_item_code:
                    new_item_code = new_item_code_series + str(int(latest_item_code.item_code[6:])+1)
                else:
                    new_item_code = new_item_code_series + '1001'
                print(new_item_code,"lop")

                item.item_code = new_item_code

            item.item_category = category
            item.item_segment = segment
            item.item_line = line
            item.name = name
            item.description = description
            item.reserve_count   = reserve
            item.status = status
            item.is_reusable = reusable
            item.save()
            messages.success(request,"Item Updated Successfully !")
        
        if action == 'delete_item':
            item_id = request.POST.get('item_id')
            InventoryItem.objects.get(id=int(item_id)).delete()
            messages.success(request,"Item Deleted Successfully !")

        return redirect('inventory:inventory-inv')

class InventoryOrder(IsInventoryAdmin,View):
    def get(self,request):
        search = request.GET.get('search')
        order_date = request.GET.get('order_date')          

        if order_date:
            order_date = datetime.strptime(order_date,'%d-%m-%Y')
        else:
            order_date = date.today()

        print(search,order_date,"ser")

        if search:
            orders = OrderScheduler.objects.filter(start_at__date=order_date).filter(Q(order_scheduler_book__service_type__icontains=search)|Q(cleaning_team_order_scheduler__team_leader__name__icontains=search)).filter(Q(work_status='CLEANING_TEAM_ASSIGNED')|Q(work_status='CLEANING_IN_PROGRESS')|Q(work_status='CLEANING_FULFILLED')).prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).order_by('-start_at')
        else:
            orders = OrderScheduler.objects.filter(start_at__date=order_date).filter(Q(work_status='CLEANING_TEAM_ASSIGNED')|Q(work_status='CLEANING_IN_PROGRESS')|Q(work_status='CLEANING_FULFILLED')).prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).order_by('-start_at')
        
        #PAGINATION ORDERS
        no_of_entries = request.GET.get('no_of_entries')
        if not no_of_entries:
            no_of_entries = 20

        page = request.GET.get('page',1)
        paginator=Paginator(orders,no_of_entries)
        try:
            orders=paginator.page(page)
        except PageNotAnInteger:
            orders=paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = orders.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # Get our new page range. In the latest versions of Django page_range returns
        # an iterator. Thus pass it to list, to make our slice possible again.
        page_range = list(paginator.page_range)[start_index:end_index]
        entry_per_page=(orders.end_index())-(orders.start_index())+1

        return render(request,'inventory/order.html',{"no_of_entries":no_of_entries,"page_range":page_range,"entry_per_page":entry_per_page,"visits":orders,"search_query":search,"order_date":order_date})

class InventoryUsers(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/users.html',{})

class InventoryCheckout(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/checkout.html',{})

class InventoryCreateCheckout(IsInventoryAdmin,View):
    def get(self,request,visit_id):
        visit = OrderScheduler.objects.select_related('order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='team_members')),to_attr='cleaning_team'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections')).get(id=int(visit_id))
        return render(request,'inventory/createCheckout.html',{"visit":visit})

class InventoryPurchaseOrder(IsInventoryAdmin,View):
    def get(self,request):
        search = request.GET.get('search')

        if search:
            purchase_orders = PurchaseOrder.objects.filter(is_order_completed=True).filter(Q( Q(purchase_order_id__icontains = search) | Q(supplier__supplier_name__icontains = search) )) .annotate(total_units=Sum('purchase_order_purchase_order_item__item_count'),total_price=Sum('purchase_order_purchase_order_item__total_price'))
        else:
            purchase_orders = PurchaseOrder.objects.filter(is_order_completed=True).annotate(total_units=Sum('purchase_order_purchase_order_item__item_count'),total_price=Sum('purchase_order_purchase_order_item__total_price'))
        
        return render(request,'inventory/purchaseOrder.html',{"purchase_orders":purchase_orders,"search_query":search})

    def post(self,request):
        action = request.POST.get('action')

        if action == 'delete_order':
            order_id = request.POST.get('order_id')
            PurchaseOrder.objects.get(id=int(order_id)).delete()
            messages.success(request,"Purchase Order Deleted successfully!")

        return redirect('inventory:inventory-purchaseorder')

class PurchaseOrderItemsPage(IsInventoryAdmin,View):
    def get(self,request,purchase_order_id):
        stores = Store.objects.filter(status=True)
        purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.all(),to_attr='purchase_order_items')).get(id=int(purchase_order_id))
        shipment_status = request.GET.get('shipment_status')
        if shipment_status == 'complete':
            purchase_order.is_received = True
            purchase_order.save()

            for item in purchase_order.purchase_order_items:
                item.is_received = True
                item.save()

        if shipment_status == 'incomplete':
            purchase_order.is_received = False
            purchase_order.save()       

        print(shipment_status,"ship")
        return render(request,"inventory/purchaseorderitems.html",{"purchase_order":purchase_order,"stores":stores})

    def post(self,request,purchase_order_id):
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        action = request.POST.get('action')
        if action == 'add_quantity_to_inventory':
            products = request.POST.getlist('product_id')
            item_counts = request.POST.getlist('item_count')
            print(products,item_counts,"cts")

            loopcount = 0
            for product in products:
                item = InventoryItem.objects.get(id=int(product))
                print(item,item_counts[loopcount], "itm")
                ItemHistory.objects.create(purchase_order=purchase_order,item=item,quantity=item_counts[loopcount],added_by=request.user)
                loopcount += 1

            messages.success(request,"Quantity added to Inventory")

        if action == 'add_unit_to_inventory':
            item_id = request.POST.get('item_id')
            store_id = request.POST.get('store')
            serial_number = request.POST.get('store')
            purchase_date = request.POST.get('purchase_date')
            expiry_date = request.POST.get('expiry_date')
            
            no_expiry = request.POST.get('no_expiry')
            if no_expiry == 'on':
                expiry = True
            else:
                expiry = True

            no_expiry = request.POST.get('no_expiry')
            unit_price = request.POST.get('unit_price')
            unit_status = request.POST.get('unit_status')

            store = Store.objects.get(id=int(store_id))

            item = InventoryItem.objects.get(id=item_id)

            item_code = item.item_code

            latest_unit_code = ItemUnit.objects.filter(unit_code__contains=item_code).last()

            if latest_unit_code:
                code = latest_unit_code.unit_code.split("-")[1]
                new_unit_code = item_code + '-' + str(int(code)+1)
            else:
                new_unit_code = item_code + '-1'
            print(new_unit_code,"lop")

            if not expiry_date:
                ItemUnit.objects.create(
                purchase_order = purchase_order,
                item = item,
                name='name',
                store=store,
                unit_code = new_unit_code,
                unit_serial_number = serial_number,
                purchase_date = purchase_date,
                no_expiry = expiry,
                unit_price = unit_price,
                status = unit_status
                )
            else:
                ItemUnit.objects.create(
                purchase_order = purchase_order,
                item = item,
                name='name',
                store=store,
                unit_code = new_unit_code,
                unit_serial_number = serial_number,
                purchase_date = purchase_date,
                expiry_date = expiry_date,
                no_expiry = expiry,
                unit_price = unit_price,
                status = unit_status
                )

            messages.success(request,"Unit added to Inventory")

        return redirect('inventory:inventory-purchaseorderitems', purchase_order_id)

class InventoryPurchaseOrderPage(View):
    def get(self,request,purchase_order_id):
        purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.all(),to_attr='purchase_order_items')).get(id=int(purchase_order_id))
        return render(request,'inventory/purchaseorderpage.html',{"purchase_order":purchase_order})

class InventoryCreatePurchaseOrder(View):
    def get(self,request):

        purchase_order = PurchaseOrder.objects.filter(is_order_completed=False,initiated_by=request.user).last()

        if not purchase_order:
            
            todate = datetime.now()
            print(todate.year+todate.month,"ic")

            purchase_order_latest = PurchaseOrder.objects.all().last()
            if purchase_order_latest:
                code_number =  re.findall(r'(\d+)', purchase_order_latest.purchase_order_id)[0]
                code_number = int(code_number[-4:])+1
                print(code_number,"coda")
                new_item_code = 'BLPO'+str(todate.year)+''+str(todate.month)+''+ str(code_number)
            else:
                new_item_code = 'BLPO'+str(todate.year)+''+str(todate.month)+'1001'
            
            print(new_item_code,"ic")
            purchase_order = PurchaseOrder.objects.create(purchase_order_id=new_item_code,initiated_by=request.user)

        suppliers = Supplier.objects.filter(status=True)

        supplier_id = request.GET.get('supplier_id')
        if supplier_id :
            supplier = Supplier.objects.get(id=int(supplier_id))
            purchase_order.supplier = supplier
            purchase_order.save()
        else:
            supplier = None

        items = SupplierItems.objects.all()
        purchase_order_items = PurchaseOrderItems.objects.filter(purchase_order=purchase_order,purchase_order__supplier=purchase_order.supplier)

        return render(request,'inventory/createpo.html',{"items":items,"suppliers":suppliers,"supplier":supplier,"purchase_order":purchase_order,"purchase_order_items":purchase_order_items})

    def post(self,request):
        action = request.POST.get('action')
        print(action,"act")

        if action == 'add_item':
            purchase_order_id = request.POST.get('purchase_order_id')
            product = request.POST.get('item')
            
            unit_price = request.POST.get('unit_price')
            unit_count = request.POST.get('item_count')
            total_price = request.POST.get('total_price')
            print(product,unit_price,unit_count,total_price,"kok")

            purchase_order = PurchaseOrder.objects.get(id=int(purchase_order_id))
            product = SupplierItems.objects.get(id=int(product))

            PurchaseOrderItems.objects.create(purchase_order=purchase_order,product=product,unit_price=unit_price,item_count=unit_count,total_price=total_price)
            
            messages.success(request,"Item Added successfully!")

        if action == 'order_close':
            purchase_order_id = request.POST.get('purchase_order_id')

            discount = request.POST.get('discount')
            tax = request.POST.get('tax')
            shipping_charges = request.POST.get('shipping_charges')
            other_charges = request.POST.get('other_charges')

            purchase_order = PurchaseOrder.objects.get(id=int(purchase_order_id))
            purchase_order.discount = discount
            purchase_order.tax = tax
            purchase_order.shipping_charge = shipping_charges
            purchase_order.other_charge = other_charges

            purchase_order.is_order_completed = True
            purchase_order.save()
            messages.success(request,"Order Completed successfully!")
            return redirect('inventory:inventory-purchaseorderpage',purchase_order.id)

        if action == 'edit_item':
            purchase_order_item_id = request.POST.get('item_edit_id')
            
            product = request.POST.get('item')
            
            unit_price = request.POST.get('unit_price')
            unit_count = request.POST.get('item_count')
            total_price = request.POST.get('total_price')
            print(product,unit_price,unit_count,total_price,"kok")

            product = SupplierItems.objects.get(id=int(product))

            order_item = PurchaseOrderItems.objects.get(id=int(purchase_order_item_id))
            order_item.product = product
            order_item.item_count = unit_count
            order_item.unit_price = unit_price
            order_item.total_price = total_price
            order_item.save()
            
            messages.success(request,"Item Updated successfully!")

        
        if action == 'delete_item':
            order_item_id = request.POST.get('item_id')
            PurchaseOrderItems.objects.get(id=int(order_item_id)).delete()
            messages.success(request,"Item Deleted successfully!")

        if action == 'reset':
            purchase_order_id = request.POST.get('purchase_order_id')

            purchase_order = PurchaseOrder.objects.get(id=int(purchase_order_id))

            purchase_order.is_order_completed = False
            purchase_order.supplier = None
            purchase_order.discount = 0.000
            purchase_order.tax = 0.000
            purchase_order.shipping_charge = 0.000
            purchase_order.other_charge = 0.000
            purchase_order.save()

            PurchaseOrderItems.objects.filter(purchase_order=purchase_order).delete()

            messages.success(request,"Purchase Order Reset successfully!")


        return redirect('inventory:inventory-createpurchaseorder')

class InventoryEditPurchaseOrder(IsInventoryAdmin,View):
    def get(self,request,purchase_order_id):

        purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.all(),to_attr='purchase_order_items')).annotate(total_order_price=Sum('purchase_order_purchase_order_item__total_price')).get(id=int(purchase_order_id))

        suppliers = Supplier.objects.filter(status=True)

        supplier_id = request.GET.get('supplier_id')
        if supplier_id :
            supplier = Supplier.objects.get(id=int(supplier_id))
            purchase_order.supplier = supplier
            purchase_order.save()
        else:
            supplier = None

        items = SupplierItems.objects.filter(supplier=purchase_order.supplier)

        print(items,"im")

        # purchase_order_items = PurchaseOrderItems.objects.filter(purchase_order=purchase_order,purchase_order__supplier=purchase_order.supplier).annotate(total_price=Sum('total_price'))

        return render(request,'inventory/editpo.html',{"items":items,"suppliers":suppliers,"supplier":supplier,"purchase_order":purchase_order})

    def post(self,request,purchase_order_id):
            action = request.POST.get('action')
            print(action,"act")

            if action == 'add_item':
                purchase_order_id = request.POST.get('purchase_order_id')
                product = request.POST.get('item')
                
                unit_price = request.POST.get('unit_price')
                unit_count = request.POST.get('item_count')
                total_price = request.POST.get('total_price')
                print(product,unit_price,unit_count,total_price,"kok")

                purchase_order = PurchaseOrder.objects.get(id=int(purchase_order_id))
                product = SupplierItems.objects.get(id=int(product))

                PurchaseOrderItems.objects.create(purchase_order=purchase_order,product=product,unit_price=unit_price,item_count=unit_count,total_price=total_price)
                
                messages.success(request,"Item Added successfully!")

            if action == 'edit_item':
                purchase_order_item_id = request.POST.get('item_edit_id')
                
                product = request.POST.get('item')
                
                unit_price = request.POST.get('unit_price')
                unit_count = request.POST.get('item_count')
                total_price = request.POST.get('total_price')
                print(product,unit_price,unit_count,total_price,"kok")

                product = SupplierItems.objects.get(id=int(product))

                order_item = PurchaseOrderItems.objects.get(id=int(purchase_order_item_id))
                order_item.product = product
                order_item.item_count = unit_count
                order_item.unit_price = unit_price
                order_item.total_price = total_price
                order_item.save()
                
                messages.success(request,"Item Updated successfully!")

            
            if action == 'delete_item':
                order_item_id = request.POST.get('item_id')
                PurchaseOrderItems.objects.get(id=int(order_item_id)).delete()
                messages.success(request,"Item Deleted successfully!")

            if action == 'order_update':
                print("vupdate")
                discount = request.POST.get('discount')
                tax = request.POST.get('tax')
                shipping_charges = request.POST.get('shipping_charges')
                other_charges = request.POST.get('other_charges')

                purchase_order = PurchaseOrder.objects.get(id=int(purchase_order_id))
                purchase_order.discount = discount
                purchase_order.tax = tax
                purchase_order.shipping_charge = shipping_charges
                purchase_order.other_charge = other_charges

                purchase_order.is_order_completed = True
                purchase_order.save()
                messages.success(request,"Order Updated successfully!")
                return redirect('inventory:inventory-purchaseorder')

            return redirect('inventory:inventory-editpurchaseorder',purchase_order_id)

class InventoryViewPurchaseOrder(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/viewpo.html',{})

class InventoryCheckedIn(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/checkin.html',{})

class InventoryOrderDetails(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/orderdetails.html',{})

class InventoryServices(IsInventoryAdmin,View):
    def get(self,request):
        items = InventoryItem.objects.all()
        return render(request,'inventory/services.html',{"items":items})

    def post(self,request):
        action =request.POST.get('action')

        if action == 'add_ingredient':
            service_type = request.POST.get('service_type')
            ingredient = request.POST.get('ingredient')
            print(ingredient,"itm")
            item_count = request.POST.get('item_count')
            # unit_price = request.POST.get('unit_price')
            item_status = request.POST.get('item_status')
            recipe_type = request.POST.get('recipe_type')

            # inventoryitem = InventoryItem.objects.get(id=int(item))

            ServiceRecipe.objects.get_or_create(service=service_type)

            get_servicetype = ServiceRecipe.objects.get(service=service_type)          

            ServiceRecipeIngredients.objects.create(service_or_person=recipe_type,service_type=get_servicetype,ingredient=ingredient,quantity=item_count,status=item_status)

            messages.success(request,"Ingredient Added successfully!")

        if action == 'update_size':
            service_name = request.POST.get('service_name')
            area = request.POST.get('area')

            ServiceRecipe.objects.get_or_create(service=service_name)

            service = ServiceRecipe.objects.get(service=service_name)
            service.area_size = area
            service.save()
            messages.success(request,"ServiceType Area Size updated successfully!")

        if action == 'edit_ingredient':
            service_ingredient_id = request.POST.get('item_edit_id')
            ingredient = request.POST.get('ingredient')
            item_count = request.POST.get('item_count')
            # unit_price = request.POST.get('unit_price')
            item_status = request.POST.get('item_status')
            recipe_type = request.POST.get('recipe_type')

            # inventoryitem = InventoryItem.objects.get(id=int(item))

            serviceingredient = ServiceRecipeIngredients.objects.get(id=int(service_ingredient_id))

            serviceingredient.service_or_person = recipe_type
            serviceingredient.ingredient = ingredient
            serviceingredient.quantity = item_count
            serviceingredient.status = item_status
            serviceingredient.save()

            messages.success(request,"Ingredient Updated successfully!")

        if action == 'delete_ingredient':
            ingredient_id = request.POST.get('object_id')

            ServiceRecipeIngredients.objects.filter(id=int(ingredient_id)).delete()
            messages.success(request,"Ingredient Deleted successfully!")

        if action == 'add_item':
            ingredient_id = request.POST.get('ingredient_id')
            item_id = request.POST.get('item')

            ingredient = ServiceRecipeIngredients.objects.get(id=int(ingredient_id))
            item = InventoryItem.objects.get(id=int(item_id))

        return redirect('inventory:inventory-services')

class InventorySegment(IsInventoryAdmin,View):
    def get(self,request,category_id):
        search = request.GET.get('search')

        if search:
            category = Category.objects.prefetch_related(Prefetch('segment_category',queryset=Segment.objects.filter(name__icontains=search).annotate(lines_count=Count('line_segment')),to_attr='segments'),Prefetch('line_category',queryset=Line.objects.all(),to_attr='lines')).get(id=int(category_id))
        else:
            category = Category.objects.prefetch_related(Prefetch('segment_category',queryset=Segment.objects.all().annotate(lines_count=Count('line_segment')),to_attr='segments'),Prefetch('line_category',queryset=Line.objects.all(),to_attr='lines')).get(id=int(category_id))
        # for segment in category.segments:

        #PAGINATION CLIENTS
        no_of_entries = request.GET.get('no_of_entries')
        if not no_of_entries:
            no_of_entries = 20

        page = request.GET.get('page',1)
        paginator=Paginator(category.segments,no_of_entries)
        try:
            category.segments=paginator.page(page)
        except PageNotAnInteger:
            category.segments=paginator.page(1)
        except EmptyPage:
            category.segments = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = category.segments.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # Get our new page range. In the latest versions of Django page_range returns
        # an iterator. Thus pass it to list, to make our slice possible again.
        page_range = list(paginator.page_range)[start_index:end_index]
        entry_per_page=(category.segments.end_index())-(category.segments.start_index())+1

        return render(request,'inventory/segment.html',{"category":category,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"search_query":search})

    def post(self,request,category_id):
        action =request.POST.get('action')

        if action == 'add_segment':
            category = Category.objects.get(id=int(category_id))
            name     = request.POST.get('segment')
            status     = request.POST.get('status')
            segment_code     = request.POST.get('segment_code')

            segment_id_exists = Segment.objects.filter(segment_id=segment_code).first()
            if segment_id_exists:
                messages.error(request,"Segment Id exists !")
            else:
                Segment.objects.create(category=category,name=name,segment_id=segment_code,status=status)
                messages.success(request,"Segment Added Successfully !")

        if action == 'edit_segment':
            print("edit")
            category = Category.objects.get(id=int(category_id))
            segment_id = request.POST.get('segment_edit_id')
            name     = request.POST.get('segment')
            status     = request.POST.get('status')

            segment = Segment.objects.get(id=int(segment_id))
            segment.category = category
            segment.name     = name
            segment.status   = status
            segment.save()
            messages.success(request,"Segment Updated Successfully !")

        if action == 'delete_segment':
            segment_id = request.POST.get('object_id')
            Segment.objects.get(id=int(segment_id)).delete()
            messages.success(request,"Segment Deleted Successfully !")

        if action == 'add_line':
            segment_id = request.POST.get('line_segment_id')
            line_name   = request.POST.get('line_name')
            line_status = request.POST.get('line_status')
            line_code     = request.POST.get('line_code')

            segment = Segment.objects.get(id=int(segment_id))

            line_id_exists = Line.objects.filter(line_id=line_code).first()
            if line_id_exists:
                messages.error(request,"Line Id exists !")
            else:

                Line.objects.create(category=segment.category,segment=segment,name=line_name,line_id=line_code,status=line_status)

                messages.success(request,"Line Added Successfully !")

        if action == 'edit_line':
            line_id = request.POST.get('edit_line_id')
            line_name   = request.POST.get('line_name')
            line_status = request.POST.get('line_status')

            line = Line.objects.get(id=int(line_id))

            line.name = line_name
            line.status = line_status
            line.save()

            messages.success(request,"Line Updated Successfully !")

        if action == 'delete_line':
            line_id = request.POST.get('object_id')
            Line.objects.get(id=int(line_id)).delete()
            messages.success(request,"Line Deleted Successfully !")
            
        return redirect('inventory:inventory-segment', category_id)
