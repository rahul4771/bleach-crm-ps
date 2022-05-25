from django.shortcuts import render,redirect
from django.views import View
from bleach_crm_ps.permissions import IsInventoryAdmin,IsInventoryAdminUser
from bleachinventory.models import QuantityStoreDetails,ExternalCustomer,CheckOutItems,CheckOutItemUnits,ItemHistory,Category,Segment,Line,Attribute,AttributeValue,ItemAttributes,InventoryItem,ItemUnit,InventoryItemImages,Bundle,BundleItems, BundleItemUnits, Store,Supplier,SupplierItems,ServiceRecipe,ServiceRecipeIngredients,ServiceRecipeItems,PurchaseOrder,PurchaseOrderItems,RequestOrder,RequestOrderItems,InventoryAccessory
from user.models import UserProfile
from django.contrib import messages
import re
import math
import xlwt
from datetime import date,datetime,timedelta
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField,Prefetch
from django.db.models.functions import Cast,TruncDate,ExtractMonth,ExtractYear,Concat
from order.models import OrderScheduler
from senior_team_leader.models import CleaningTeam,CleaningTeamMember
from bleachadmin.models import ServicePriceRange
from evaluator.models import EvaluationBookSection,EvaluationSectionKeynote,EvaluationSectionAddons
import functools
import operator
from django.utils import timezone
import pandas as pd

# Create your views here.

class InventoryHome(IsInventoryAdminUser,View):
	def get(self,request):
		
		items = InventoryItem.objects.filter(status=True)
		items_count = items.count()

		# LOAD TOTAL QTY FOR QUANTITY ITEMS
		# for item in items:
		#     if item.item_add_type == 'quantity':
		#         history_total = ItemHistory.objects.filter(item=item).exclude(quantity=None).aggregate(item_total=Sum('quantity'))['item_total']
		#         if history_total == None:
		#             history_total = 0.00
		#         print(history_total,item.name,"itzxc")
		#         item.total_quantity = history_total
		#         item.save()
		
		recent_items = items.order_by('-id')
		
		# todate = date.today()
		# start_date_day = todate
		# end_date_day   = todate+timedelta(1)

		order_date = request.GET.get('order_date')          

		if order_date:
			order_date = datetime.strptime(order_date,'%d-%m-%Y')
		else:
			order_date = date.today()

		print(order_date,"ser")
		
		purchase_items = items.filter(Q(item_status='out_of_stock') | Q(item_status='about_to_finish')).prefetch_related(Prefetch('unit_item',queryset=ItemUnit.objects.all(),to_attr='units'))
		
		found = set()

		combined_visits = []
		
		purchase_orders = PurchaseOrder.objects.filter(is_admin_approved=False,is_received=False,is_rejected=False,status=True,is_order_completed=True)
		po_count        = purchase_orders.count()

		request_orders  = RequestOrder.objects.filter(is_admin_approved=False,is_received=False,is_rejected=False,status=True,is_order_completed=True)
		ro_count        = request_orders.count()

		teamassign_to_date             = (timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)).replace(tzinfo=None)

		calendar_order_schedules_list       = []
		calendar_order_schedules_duplicates = []
		calendar_order_schedules_alls       = CleaningTeam.objects.select_related('team_leader','order_scheduler__order').filter(order_scheduler__start_at__date=order_date).filter(Q(order_scheduler__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler__work_status='CLEANING_IN_PROGRESS')|Q(order_scheduler__work_status='CLEANING_FULFILLED')).annotate(duplicate=Concat('order_scheduler__start_at','order_scheduler__order__id','team_leader__id',output_field=CharField()))
		for calendar_order_schedules_all in calendar_order_schedules_alls:
			if not calendar_order_schedules_all.duplicate in calendar_order_schedules_duplicates:
				calendar_order_schedules_list.append(calendar_order_schedules_all.order_scheduler.id)
				calendar_order_schedules_duplicates.append(calendar_order_schedules_all.duplicate)
		
		print(calendar_order_schedules_list,calendar_order_schedules_duplicates,calendar_order_schedules_alls,"datass")

		orders = OrderScheduler.objects.filter(id__in=calendar_order_schedules_list).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).order_by('-start_at')
		
		return render(request,'inventory/home.html',{"items_count":items_count,"recent_items":recent_items,"purchase_items":purchase_items,"orders":orders,"purchase_orders":purchase_orders,"po_count":po_count,"request_orders":request_orders,"ro_count":ro_count,"order_date":order_date,"orders":orders})

# Category.
class InventoryCategory(IsInventoryAdminUser,View):
	def get(self,request):

		search = request.GET.get('search')

		if search:
			categories       = Category.objects.filter(Q(name__icontains=search)|Q(category_code__icontains=search))
		else:
			categories       = Category.objects.all()
		
		for category in categories:
			category.segments_count = Segment.objects.filter(category=category).count()
			category.lines_count = Line.objects.filter(category=category).count()

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

		return redirect('bleach-inventory:inventory-category')

# Attribute.
class InventoryAttribute(IsInventoryAdminUser,View):
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
				if category_id == '0':
					category = None
				else:
					category = Category.objects.get(id=int(category_id))
			else:
				category = None

			if segment_id:
				if segment_id == '0':
					segment = None
				else:
					segment = Segment.objects.get(id=int(segment_id))
			else:
				segment = None

			if line_id:
				if line_id == '0':
					line = None
				else:
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

			print(attribute_category,attribute_id,name,attribute_type,status,"lop")

			attribute = Attribute.objects.get(id=int(attribute_id))
			
			if attribute_category == '0':
				print("prip")
				category = None
				segment = None
				line = None
			elif attribute_segment == '0':
				category = Category.objects.get(id=int(attribute_category))
				segment = None
				line = None
			elif attribute_line == '0':
				category = Category.objects.get(id=int(attribute_category))
				segment = Segment.objects.get(id=int(attribute_segment))
				line = None
			else:
				print("prip2")
				category = Category.objects.get(id=int(attribute_category))
				segment = Segment.objects.get(id=int(attribute_segment))
				line = Line.objects.get(id=int(attribute_line))

			# attribute.category = category
			attribute.name     = name
			attribute.attribute_type = attribute_type

			
			attribute.attribute_category = category
			
			attribute.attribute_segment = segment
			
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

		return redirect('bleach-inventory:inventory-attribute')
# value.
class InventoryValue(IsInventoryAdminUser,View):
	def get(self,request):
		return render(request,'inventory/value.html',{})

# bundle.
class InventoryBundle(IsInventoryAdminUser,View):
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
					item_unit.status = 'working'
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
				selected_units = ItemUnit.objects.filter(item=inventory_item,is_available=True)[:int(item_count)]

				for unit in selected_units:
					total_item_price += float(unit.unit_price)
					unit.status = 'unavailable'
					unit.save()
					used_units.append(unit)

				item_count = item_count

			else:
				selected_units = ItemUnit.objects.filter(item=inventory_item,is_available=True)[:int(inventory_item_unit_count)]

				for unit in selected_units:
					total_item_price += float(unit.unit_price)
					unit.status = 'unavailable'
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
				selected_units = ItemUnit.objects.filter(item=inventory_item,is_available=True)[:int(item_count)]

				for unit in selected_units:
					total_item_price += float(unit.unit_price)
					unit.status = 'unavailable'
					unit.save()
					used_units.append(unit)

				item_count = item_count

			else:
				selected_units = ItemUnit.objects.filter(item=inventory_item,is_available=True)[:int(inventory_item_unit_count)]

				for unit in selected_units:
					total_item_price += float(unit.unit_price)
					unit.status = 'unavailable'
					unit.save()
					used_units.append(unit)

				item_count = inventory_item_unit_count

			bundleitem = BundleItems.objects.get(id=int(bundle_item_id))

			#clearing old units
			old_bundleitemunits = BundleItemUnits.objects.filter(bundle_item=bundleitem)
			for unit in old_bundleitemunits:
				item_unit = ItemUnit.objects.get(id=int(unit.item_unit.id))
				item_unit.status = 'available'
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
				item_unit.status = 'available'
				item_unit.save()

				# bundleitem.item_price = float(bundleitem.item_price) - float(unit.unit_price)
				# bundleitem.item_count = int(bundleitem.item_count) - 1

			bundle.bundle_items_count = int(bundleitem.bundle.bundle_items_count) - int(bundleitem.item_count)
			bundle.bundle_price = float(bundleitem.bundle.bundle_price) - float(bundleitem.item_price)
			bundle.save()

			bundleitem.delete()
			messages.success(request,"Item Deleted successfully !")


		return redirect('bleach-inventory:inventory-bundle')

class InventoryItems(IsInventoryAdminUser,View):
	def get(self,request,item_id):
		
		inventory_item = InventoryItem.objects.prefetch_related(Prefetch('quantity_store_item',queryset=QuantityStoreDetails.objects.select_related('item_store').all(),to_attr='storequantity'),Prefetch('image_item',queryset=InventoryItemImages.objects.all(),to_attr='item_images')).get(id=item_id)
		supplier_item = SupplierItems.objects.filter(item=inventory_item).first()
		categories = Category.objects.all()
		item_units = ItemUnit.objects.filter(item=inventory_item).prefetch_related(Prefetch('product_request_unit',queryset=RequestOrderItems.objects.filter(is_received=True),to_attr='request_item_unit'),Prefetch('checkoutitem_unit',CheckOutItemUnits.objects.all().select_related('checkout_item__visit').prefetch_related(Prefetch('checkout_item__visit__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')),to_attr='checkout_unit'))
		item_history = ItemHistory.objects.filter(item=inventory_item).order_by('-id')

		stores = Store.objects.filter(status=True)

		available_item_units = item_units.filter(is_available=True).count()
		unavailable_item_units = item_units.filter(is_available=False)

		available_quantity = inventory_item.total_quantity
		if not available_quantity:
			available_quantity = 0
		
		reserve_units = inventory_item.reserve_count


		if inventory_item.item_add_type == 'unit':
			if int(available_item_units) < int(reserve_units) and int(available_item_units) > 0:
				inventory_item.item_status = 'about_to_finish'
			elif int(available_item_units) == 0 :
				inventory_item.item_status = 'out_of_stock'
			else:
				inventory_item.item_status = 'available'
			inventory_item.save()
		else:
			if float(available_quantity) < float(reserve_units) and float(available_quantity) > 0:
				inventory_item.item_status = 'about_to_finish'
			elif float(available_quantity) == 0 :
				inventory_item.item_status = 'out_of_stock'
			else:
				inventory_item.item_status = 'available'
			inventory_item.save()

		attributes = Attribute.objects.filter(status=True).filter(Q (Q(attribute_category=inventory_item.item_category) & Q(attribute_segment=inventory_item.item_segment) & Q(attribute_line=inventory_item.item_line)) | Q(attribute_category=None) | Q( Q(attribute_category=inventory_item.item_category) & Q(attribute_segment=None)) | Q( Q(attribute_category=inventory_item.item_category) & Q(attribute_segment=inventory_item.item_segment) & Q(attribute_line=None)) ).prefetch_related(Prefetch('value_attribute',queryset=AttributeValue.objects.filter(status=True),to_attr='attribute_values'))

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

		purchase_orders = PurchaseOrder.objects.filter(purchase_order_purchase_order_item__product__item__id=int(item_id),purchase_order_purchase_order_item__is_received=False).prefetch_related()

		print(purchase_orders,"orddd")

		#PAGINATION CLIENTS
		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20

		if inventory_item.item_add_type == 'unit':

			page = request.GET.get('page',1)
			paginator=Paginator(item_units,no_of_entries)
			try:
				item_units=paginator.page(page)
			except PageNotAnInteger:
				item_units=paginator.page(1)
			except EmptyPage:
				item_units = paginator.page(paginator.num_pages)

			# Get the index of the current page
			index = item_units.number - 1  # edited to something easier without index
			# This value is maximum index of your pages, so the last page - 1
			max_index = len(paginator.page_range)
			# You want a range of 7, so lets calculate where to slice the list
			start_index = index - 3 if index >= 3 else 0
			end_index = index + 3 if index <= max_index - 3 else max_index
			# Get our new page range. In the latest versions of Django page_range returns
			# an iterator. Thus pass it to list, to make our slice possible again.
			page_range = list(paginator.page_range)[start_index:end_index]
			entry_per_page=(item_units.end_index())-(item_units.start_index())+1

		else:

			page = request.GET.get('page',1)
			paginator=Paginator(item_history,no_of_entries)
			try:
				item_history=paginator.page(page)
			except PageNotAnInteger:
				item_history=paginator.page(1)
			except EmptyPage:
				item_history = paginator.page(paginator.num_pages)

			# Get the index of the current page
			index = item_history.number - 1  # edited to something easier without index
			# This value is maximum index of your pages, so the last page - 1
			max_index = len(paginator.page_range)
			# You want a range of 7, so lets calculate where to slice the list
			start_index = index - 3 if index >= 3 else 0
			end_index = index + 3 if index <= max_index - 3 else max_index
			# Get our new page range. In the latest versions of Django page_range returns
			# an iterator. Thus pass it to list, to make our slice possible again.
			page_range = list(paginator.page_range)[start_index:end_index]
			entry_per_page=(item_history.end_index())-(item_history.start_index())+1


		return render(request,'inventory/item.html',{"supplier_item":supplier_item,"available_item_units":available_item_units,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"stores":stores,"item_attributes":item_attributes,"inventory_item":inventory_item,"attributes":attributes,"categories":categories,"item_units":item_units,"item_history":item_history,"new_unit_code":new_unit_code,"purchase_orders":purchase_orders,"unavailable_units":unavailable_item_units})

	def post(self,request,item_id):
		action = request.POST.get('action')

		if action == 'edit_item_details':
			category_id = request.POST.get('item_category')
			segment_id = request.POST.get('item_segment')
			line_id = request.POST.get('item_line')
			is_reusable = request.POST.get('item_reusable')
			print(category_id,segment_id,line_id,"ids")

			item_unit_data = request.POST.get('item_unit_data')

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

			if is_reusable == 'on':
				item.is_reusable = True
			else:
				item.is_reusable = False

			item.name = request.POST.get('item_name')
			item.item_category = category
			item.item_segment = segment
			item.item_line = line
			item.measuring_unit = item_unit_data
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
			item = InventoryItem.objects.get(id=item_id)

			store_id = request.POST.get('store')
			serial_number = request.POST.get('serial_number')
			print(serial_number,"serl")
			if item.item_type != 'FINISHED GOODS':
				purchase_date = request.POST.get('purchase_date')
				expiry_date = request.POST.get('expiry_date')
			
				no_expiry = request.POST.get('no_expiry')
				if no_expiry == 'on':
					expiry = True
				else:
					expiry = True
			else:
				purchase_date = None
				expiry_date = None
				expiry = False
			
			unit_price = request.POST.get('unit_price')
			status = request.POST.get('unit_status')

			store = Store.objects.get(id=int(store_id))

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

		if action == "add_quantity":
			store_id = request.POST.get('store')
			
			purchase_date = request.POST.get('purchase_date')
			print(purchase_date,"pd")
			
			quantity = request.POST.get('inventory_item_quantity')

			store = Store.objects.get(id=int(store_id))

			item = InventoryItem.objects.get(id=item_id)

			ItemHistory.objects.create(
			item = item,
			purchase_date = purchase_date,
			item_action = 'MANUAL',
			quantity = quantity,
			quantity_location = store,
			added_by = request.user
			)

			try:
				quantitystore = QuantityStoreDetails.objects.get(item_store=store,quantity_item = item)
				quantitystore.quantity = float(quantitystore.quantity) + float(quantity)
				quantitystore.save()
			except:
				QuantityStoreDetails.objects.create(
				item_store = store,
				quantity_item = item,
				quantity = quantity
				)
			
			item.total_quantity = float(item.total_quantity)+float(quantity)
			item.save()

			messages.success(request,"Quantity Added Successfully !")

		if action == 'return_item':
			item = InventoryItem.objects.get(id=item_id)

			store_id = request.POST.get('store')
			store = Store.objects.get(id=int(store_id))

			externaluser = ExternalCustomer.objects.get( id=int(request.POST.get('externaluser')) ) 

			if item.item_add_type == 'unit':
				unit_id = request.POST.get('return_unit')
				itemunit = ItemUnit.objects.get(id=int(unit_id))
				itemunit.status = 'working'
				itemunit.store = store
				itemunit.is_available = True
				itemunit.save()

				messages.success(request,"Item received !")
			else:
				quantity = request.POST.get('return_quantity')

				request_order_item = RequestOrderItems.objects.filter(request_order__requested_by=externaluser,product=item).last()

				if request_order_item:
					ItemHistory.objects.create(
						item = item,
						item_action = 'ITEM RETURN',
						item_remark = request_order_item.request_order.request_order_id,
						quantity = quantity,
						quantity_location = store,
						external_user = request_order_item.request_order.requested_by.name
					)

					try:
						quantitystore = QuantityStoreDetails.objects.get(item_store=store,quantity_item = item)
						quantitystore.quantity = float(quantitystore.quantity) + float(quantity)
						quantitystore.save()
					except:
						QuantityStoreDetails.objects.create(
						item_store = store,
						quantity_item = item,
						quantity = quantity
						)

					item.total_quantity = float(item.total_quantity) + float(quantity)
					item.save()

					messages.success(request,"Item received !")
				else:
					messages.error(request,"No Returns !")

		if action == "edit_unit":
			unit_id = request.POST.get('edit_unit_id')
			store_id = request.POST.get('store')
			serial_number = request.POST.get('serial_number')
			purchase_date = request.POST.get('purchase_date')
			expiry_date = request.POST.get('expiry_date')
			unit_status = request.POST.get('unit_status')
			no_expiry = request.POST.get('no_expiry')
			if no_expiry == 'on':
				expiry = True
			else:
				expiry = True
			unit_price = request.POST.get('unit_price')
			status = request.POST.get('unit_status_update')
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
			if status == 'out_of_order' or status == 'under_repair':
				unit.is_available = False
			if status == 'working':
				unit.is_available = True
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

		return redirect('bleach-inventory:inventory-item',item_id)


class InventoryTransfer(View):
	def get(self,request):
		return render(request,'inventory/inventorytransfer.html',{})
	def post(self,request):
		from_store = request.POST.get('store_id')
		to_store = request.POST.get('store_id2')
		item_ids    = request.POST.getlist('item_id')
		quantities = request.POST.getlist('item_quantity')
		item_units = request.POST.getlist('unit_id')

		store1 = Store.objects.get(id=int(from_store))
		store2 = Store.objects.get(id=int(to_store))

		print(item_units,"ituni")

		for i in range(len(item_ids)):
			print(item_ids[i],"aart")

			item       = InventoryItem.objects.get(id=int(item_ids[i]))

			if item.item_add_type == 'quantity':
				quantity   = quantities[i] #request.POST.get('item_count')
				print(quantity,"qtyy")
				if float(item.total_quantity) >= float(quantity):
					quantitystore1 = QuantityStoreDetails.objects.get(item_store=store1,quantity_item=item)
					if float(quantitystore1.quantity) >= float(quantity):
						quantitystore1.quantity = round(float(quantitystore1.quantity) - float(quantity),2)
						quantitystore1.save()

						try:
							quantitystore2 = QuantityStoreDetails.objects.get(item_store=store2,quantity_item = item)
							quantitystore2.quantity = round(float(quantitystore2.quantity) + float(quantity),2)
							quantitystore2.save()
						except:
							QuantityStoreDetails.objects.create(
							item_store = store2,
							quantity_item = item,
							quantity = quantity
							)

						ItemHistory.objects.create(item=item,item_action='TRANSFER',quantity=quantity,added_by=request.user,item_remark='Inventory Transfer')
		
						messages.success(request,"Inventory Items Transferred Succesfully")
					else:
						messages.error(request,"Required quantity not available for transfer!")

		if item_units:
			unit_items    = ItemUnit.objects.filter(id__in=item_units,is_available=True).update(store=store2)

			messages.success(request,"Inventory Items Transferred Succesfully")
		
		return redirect('bleach-inventory:inventory-transfer')


class ItemDispose(View):
	def get(self,request):
		return render(request,'inventory/itemdispose.html',{})
	def post(self,request):
		from_store = request.POST.get('store_id')

		item_ids    = request.POST.getlist('item_id')
		quantities = request.POST.getlist('item_quantity')
		item_units = request.POST.getlist('unit_id')

		store = Store.objects.get(id=int(from_store))

		for i in range(len(item_ids)):
			item       = InventoryItem.objects.get(id=int(item_ids[i]))
			if item.item_add_type == 'quantity':
				quantity   = quantities[i] #request.POST.get('item_count')

				if float(item.total_quantity) >= float(quantity):
					store_item = QuantityStoreDetails.objects.get(item_store=store,quantity_item=item)
					if float(store_item.quantity) >= float(quantity):
						store_item.quantity = round(float(store_item.quantity) - float(quantity),2)
						store_item.save()

						item.total_quantity = round(float(item.total_quantity) - float(quantity),2)
						item.save()

						ItemHistory.objects.create(item=item,item_action='DISPOSE',quantity=quantity,quantity_location = store,added_by=request.user,item_remark='Disposed')

						messages.success(request,"Inventory Items Disposed Succesfully")
					else:
						messages.error(request,"Required quantity not available to dispose!")

		if item_units:
			unit_items    = ItemUnit.objects.filter(id__in=item_units,is_available=True).update(status='disposed',is_available=False)

			messages.success(request,"Inventory Items Disposed Succesfully")
		
		return redirect('bleach-inventory:item-dispose')


class InventorySupplier(IsInventoryAdminUser,View):
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
			currency     = request.POST.get('currency')

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
				Supplier.objects.create(supplier_name=name,supplier_id=new_supplier_id,contact=contact,currency=currency,address=address,terms=terms,status=status)
				messages.success(request,"Supplier Added Successfully !")

		if action == 'edit_supplier':
			supplier_id = request.POST.get('supplier_edit_id')
			name     = request.POST.get('supplier_name')
			contact = request.POST.get('contact')
			other_contact = request.POST.get('other_contact')
			address = request.POST.get('address')
			terms = request.POST.get('terms')
			status     = request.POST.get('status')
			currency     = request.POST.get('currency')

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
				supplier.currency = currency
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

			
			item_count_check = SupplierItems.objects.filter(item=product).count()

			if item_count_check >= 1:
				messages.error(request,"Item already exists for a supplier !")
			else:
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

			
			item_check_count = SupplierItems.objects.filter(item=product).count()

			if item_check_count >= 2:
				messages.error(request,"Item already exists for another supplier !")
			else:
				supplieritem.item = product
				supplieritem.item_price = item_price
				supplieritem.item_count = item_count
				supplieritem.save()

				messages.success(request,"Item Updated Successfully !")

		if action == 'delete_item':
			supplier_item_id = request.POST.get('supplier_id_delete')

			supplieritem = SupplierItems.objects.get(id=int(supplier_item_id)).delete()

			messages.success(request,"Item Deleted Successfully !")

		return redirect('bleach-inventory:inventory-supplier')

class InventoryStore(IsInventoryAdminUser,View):
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
		return redirect('bleach-inventory:inventory-store')

class InventoryInv(IsInventoryAdminUser,View):
	def get(self,request):
		
		
		# inv_items = InventoryItem.objects.filter(status=True,item_add_type='quantity')

		# for item in inv_items:
		# 	item_stores_count = QuantityStoreDetails.objects.filter(quantity_item=item).count()

		# 	if item_stores_count == 1 :
				
		# 		item_store = QuantityStoreDetails.objects.get(quantity_item=item)
		# 		item_store.quantity = item.total_quantity
		# 		item_store.save()

		
		
		# df = pd.read_excel('Book2.xls')

		# for index, row in df.iterrows():
		# 	x = list(row)
		# 	print (x,"xalg")
			
		# 	categories       = Category.objects.all()
		# 	category_latest  = categories.last()
		# 	if category_latest:
		# 		code_number  =  int(re.findall(r'(\d+)', category_latest.category_code)[0]) + 1
		# 		new_category_code = 'CAT'+str(code_number)
		# 	else:
		# 		new_category_code = 'CAT9001'

		# 	try:
		# 		category = Category.objects.get(name=x[1],status=True)
		# 	except:
		# 		category = Category.objects.create(name=x[1],category_code=new_category_code,status=True)

		# 	try:
		# 		segment = Segment.objects.get(name=x[2],category=category,status=True)
		# 	except:
		# 		segment = Segment.objects.create(name=x[2],category=category,status=True)

		# 	try:
		# 		line = Line.objects.get(name=x[3],category=category,segment=segment,status=True)
		# 	except:
		# 		line = Line.objects.create(name=x[3],category=category,segment=segment,status=True)

		#unit code, item code reset

		# InventoryItem.objects.filter(status=True).update(item_code='000000000')
		# items = InventoryItem.objects.filter(status=True)

		# for item in items:
		# 	item_code_series = str(item.item_category.category_id)+str(item.item_segment.segment_id)+str(item.item_line.line_id)
		# 	print(item_code_series,"itcs")

		# 	latest_item_code = InventoryItem.objects.filter(item_code__contains=item_code_series).last()
		# 	print(latest_item_code,"lic")

		# 	if latest_item_code and str(item_code_series) in str(latest_item_code.item_code):
		# 		print("exist")
		# 		new_item_code = item_code_series + str(int(latest_item_code.item_code[6:])+1)
		# 		print(new_item_code,"newit")
		# 	else:
		# 		print("not exist")
			
		# 		new_item_code = item_code_series + '101'
		# 		print(new_item_code,"newit")

		# 	InventoryItem.objects.filter(id=item.id,item_category=item.item_category,item_segment=item.item_segment,item_line=item.item_line).update(item_code=new_item_code)
		
		
		# items2 = InventoryItem.objects.filter(status=True,item_add_type='unit')
		# ItemUnit.objects.all().update(unit_code='000000000-0')

		# for item in items2:

		# 	item_code = item.item_code
		# 	print(item_code,"itc")

		# 	itemunits = ItemUnit.objects.filter(item=item)

		# 	for unit in itemunits:
		# 		latest_unit_code = ItemUnit.objects.filter(unit_code__contains=item_code).last()
		# 		print(latest_unit_code,"ltst")

		# 		if latest_unit_code:
		# 			code = latest_unit_code.unit_code.split("-")[1]
		# 			new_unit_code = item_code + '-' + str(int(code)+1)
		# 		else:
		# 			print("newc")
		# 			new_unit_code = item_code + '-1'

		# 		unit.unit_code = new_unit_code
		# 		unit.save()



		# 	InventoryItem.objects.filter(name__iexact=x[0]).update(item_category=category,item_segment=segment,item_line=line)

		
		# Category.objects.filter(status=True).update(category_id='XX')
		# Segment.objects.filter(status=True).update(segment_id='XX')
		# Line.objects.filter(status=True).update(line_id='XX')

		# df1 = pd.read_excel('CODE.xls',sheet_name=0,header=None)

		# for index, row in df1.iterrows():
		# 	x = list(row)
		# 	print (x[0],x[1],"xalg22")

		# 	try:
		# 		category = Category.objects.get(name=x[0],status=True)
		# 		category.category_id = x[1]
		# 		category.save()
		# 	except:
		# 		category = None

		# df2 = pd.read_excel('CODE.xls',sheet_name=1,header=None)

		# for index, row in df2.iterrows():
		# 	x = list(row)
		# 	print (x,"xalg")

		# 	try:
		# 		segment = Segment.objects.get(name=x[0],status=True)
		# 		segment.segment_id = x[1]
		# 		segment.save()
		# 	except:
		# 		segment = None

		# df3 = pd.read_excel('CODE.xls',sheet_name=2,header=None)

		# for index, row in df3.iterrows():
		# 	x = list(row)
		# 	print (x,"xalg")

		# 	try:
		# 		line = Line.objects.get(name=x[0],status=True)
		# 		line.line_id = x[1]
		# 		line.save()
		# 	except:
		# 		line = None
		
		
		
		
		# category = Category.objects.get(name='X')
		# segment = Segment.objects.get(name='X')
		# line = Line.objects.get(name='X')
		
		# InventoryItem.objects.filter(status=True).update(item_category=category,item_segment=segment,item_line=line)



		# ItemUnit.objects.exclude(status='available').update(is_available=False)
		# ItemUnit.objects.filter(Q(status='available')|Q(status='unavailable')).update(status='working')

		# histories = ItemHistory.objects.filter(Q(item_action='STOCK OUT')|Q(item_action='STOCK IN'))
		# for item in histories:
		# 	team = CleaningTeam.objects.filter(visit__order__order_no=)

		# qty_items = InventoryItem.objects.filter(item_add_type='quantity')
		# store = Store.objects.filter(store_name='AL-RAI STORE').first()
		# for item in qty_items:
		# 	QuantityStoreDetails.objects.create(item_store=store,quantity_item=item,quantity=item.total_quantity)
			
		# ItemHistory.objects.all().update(quantity_location=store)
			

		#item and store quantity match
		# items = InventoryItem.objects.filter(status=True,item_add_type='quantity')
		# store = Store.objects.get(store_name='AL-RAI STORE')

		# for item in items:
			
		# 	try:
		# 		quantitystore = QuantityStoreDetails.objects.get(quantity_item=item,item_store=store)
		# 		quantitystore.quantity = item.total_quantity
		# 		quantitystore.save()
		# 	except:
		# 		quantitystore = None
		########################################
		
		search = request.GET.get('search')
		item_type = request.GET.get('item_type',None)

		try:
			item_category = request.GET.get('item_category')
			item_category = int(item_category)
		except:
			item_category = ''

		try:
			item_segment = request.GET.get('item_segment')
			item_segment = int(item_segment)
		except:
			item_segment = ''

		try:
			item_line = request.GET.get('item_line')
			item_line = int(item_line)
		except:
			item_line = ''

		try:
			item_status = request.GET.get('item_status')
		except:
			item_status = ''

		try:
			item_supplier = request.GET.get('item_supplier')
			if not item_supplier == 'NOSUPPLIER':
				item_supplier = int(item_supplier)
		except:
			item_supplier = ''

		try:
			item_store = request.GET.get('item_store')
			item_store = int(item_store)
		except:
			item_store = ''

		print(item_category,item_segment,item_line,item_status,"mkk")
		suppliers = Supplier.objects.filter(status=True)
		stores = Store.objects.all()

		if search:
			inventory_items                 = InventoryItem.objects.filter(Q(name__icontains=search)|Q(item_code__icontains=search)).annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))

			inventory_items_rawmaterials    = InventoryItem.objects.filter(item_type='RAW MATERIALS').filter(Q(name__icontains=search)|Q(item_code__icontains=search)).annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))
		
			inventory_items_assets          = InventoryItem.objects.filter(item_type='ASSETS').filter(Q(name__icontains=search)|Q(item_code__icontains=search)).annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))
		
			inventory_items_finishedgoods   = InventoryItem.objects.filter(item_type='FINISHED GOODS').filter(Q(name__icontains=search)|Q(item_code__icontains=search)).annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))

		else:
			inventory_items                 = InventoryItem.objects.all().annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))

			inventory_items_rawmaterials    = InventoryItem.objects.filter(item_type='RAW MATERIALS').annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))
		
			inventory_items_assets          = InventoryItem.objects.filter(item_type='ASSETS').annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))
		
			inventory_items_finishedgoods   = InventoryItem.objects.filter(item_type='FINISHED GOODS').annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField())))

		# inventory_items.filter(measuring_unit='number').update(measuring_unit='piece')

		for item in inventory_items:
			
			reserve_units = item.reserve_count
			
			if item.item_add_type == 'unit':
				available_item_units = ItemUnit.objects.filter(item=item,is_available=True).count()

				if int(available_item_units) < int(reserve_units) and int(available_item_units) > 0:
					item.item_status = 'about_to_finish'
				elif int(available_item_units) == 0 :
					item.item_status = 'out_of_stock'
				else:
					item.item_status = 'available'
				item.save()
			else:
				available_item_units = item.total_quantity

				if float(available_item_units) < float(reserve_units) and float(available_item_units) > 0:
					item.item_status = 'about_to_finish'
				elif float(available_item_units) == 0 :
					item.item_status = 'out_of_stock'
				else:
					item.item_status = 'available'
				item.save()

		categories  = Category.objects.all()

		filters = []

		if item_category:
			case1 = Q(item_category__id=item_category)
			filters.append(case1)

		if item_segment:
			case2 = Q(item_segment__id=item_segment)
			filters.append(case2)

		if item_line:
			case3 = Q(item_line__id=item_line)
			filters.append(case3)

		if item_status:
			case4 = Q(item_status=item_status)
			filters.append(case4)

		if item_supplier :
			if item_supplier == 'NOSUPPLIER':
				case5 = Q(product_supplier__supplier__id=None)
			else:
				case5 = Q(product_supplier__supplier__id=item_supplier)
			filters.append(case5)

		if item_store:
			
			case6 = Q( Q(Q(unit_item__store__id=item_store)&Q(unit_item__is_available=True)) | Q(quantity_store_item__item_store__id=item_store)&Q(quantity_store_item__quantity__gt=0))
			
			filters.append(case6)

		if item_category or item_segment or item_line or item_status or item_supplier or item_store:
			filters = functools.reduce(operator.and_,filters)

			inventory_items = inventory_items.filter(filters)

		#PAGINATION CLIENTS
		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20

		page1 = request.GET.get('page1',1)
		paginator1=Paginator(inventory_items,no_of_entries)
		try:
			inventory_items = paginator1.page(page1)
		except PageNotAnInteger:
			inventory_items = paginator1.page(1)
		except EmptyPage:
			inventory_items = paginator1.page(paginator1.num_pages)

		#page2
		page2 = request.GET.get('page2',1) 

		paginator2=Paginator(inventory_items_rawmaterials,no_of_entries)

		try: 
			inventory_items_rawmaterials=paginator2.page(page2) 
		except PageNotAnInteger:
			inventory_items_rawmaterials=paginator2.page(1) 
		except EmptyPage:
			inventory_items_rawmaterials=paginator2.page(paginator2.num_pages) 

		#page3
		page3 = request.GET.get('page3',1) 

		paginator3=Paginator(inventory_items_assets,no_of_entries)

		try: 
			inventory_items_assets=paginator3.page(page3) 
		except PageNotAnInteger:
			inventory_items_assets=paginator3.page(1) 
		except EmptyPage:
			inventory_items_assets=paginator3.page(paginator3.num_pages)

		#page4
		page4 = request.GET.get('page4',1) 

		paginator4=Paginator(inventory_items_finishedgoods,no_of_entries)

		try: 
			inventory_items_finishedgoods=paginator4.page(page4) 
		except PageNotAnInteger:
			inventory_items_finishedgoods=paginator4.page(1) 
		except EmptyPage:
			inventory_items_finishedgoods=paginator4.page(paginator4.num_pages)

		# Get the index of the current page
		index1 = inventory_items.number - 1  # edited to something easier without index
		index2 = inventory_items_rawmaterials.number - 1
		index3 = inventory_items_assets.number - 1
		index4 = inventory_items_finishedgoods.number - 1
		# This value is maximum index of your pages, so the last page - 1
		max_index1 = len(paginator1.page_range)
		max_index2 = len(paginator2.page_range)
		max_index3 = len(paginator3.page_range)
		max_index4 = len(paginator4.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index1 = index1 - 3 if index1 >= 3 else 0
		end_index1 = index1 + 3 if index1 <= max_index1 - 3 else max_index1

		start_index2 = index2 - 3 if index2 >= 3 else 0
		end_index2 = index2 + 3 if index2 <= max_index2 - 3 else max_index2

		start_index3 = index3 - 3 if index3 >= 3 else 0
		end_index3 = index3 + 3 if index3 <= max_index3 - 3 else max_index3

		start_index4 = index4 - 3 if index4 >= 3 else 0
		end_index4   = index4 + 3 if index4 <= max_index4 - 3 else max_index4
		# Get our new page range. In the latest versions of Django page_range returns
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range1 = list(paginator1.page_range)[start_index1:end_index1]
		page_range2 = list(paginator2.page_range)[start_index2:end_index2]
		page_range3 = list(paginator3.page_range)[start_index3:end_index3]
		page_range4 = list(paginator4.page_range)[start_index4:end_index4]

		entry_per_page1=(inventory_items.end_index())-(inventory_items.start_index())+1
		entry_per_page2 = (inventory_items_rawmaterials.end_index())-(inventory_items_rawmaterials.start_index())+1
		entry_per_page3 = (inventory_items_assets.end_index())-(inventory_items_assets.start_index())+1
		entry_per_page4 = (inventory_items_finishedgoods.end_index())-(inventory_items_finishedgoods.start_index())+1

		return render(request,'inventory/inventory.html',{"stores":stores,"item_store":item_store,"suppliers":suppliers,"item_type":item_type,"categories":categories,"items":inventory_items,"inventory_items_rawmaterials":inventory_items_rawmaterials,"inventory_items_assets":inventory_items_assets,"inventory_items_finishedgoods":inventory_items_finishedgoods,"search_query":search,"page_range1":page_range1,"page_range2":page_range2,"page_range3":page_range3,"page_range4":page_range4,"entry_per_page1":entry_per_page1,"entry_per_page2":entry_per_page2,"entry_per_page3":entry_per_page3,"entry_per_page4":entry_per_page4,"no_of_entries":no_of_entries,"item_category":item_category,"item_segment":item_segment,"item_line":item_line,"item_status":item_status,"item_supplier":item_supplier})

	def post(self,request):
		action =request.POST.get('action')

		if action == 'add_item':
			# category = Category.objects.get(id=int(category_id))
			item_type       = request.POST.get('item_type')
			name            = request.POST.get('item_name')
			category_id     = request.POST.get('item_category')
			segment_id      = request.POST.get('item_segment')
			line_id         = request.POST.get('item_line')
			description     = request.POST.get('item_description')
			reserve         = request.POST.get('item_reserve')
			status          = request.POST.get('item_status')
			reusable        = request.POST.get('item_reusable')
			supplier_id		= request.POST.get('item_supplier')
			item_price		= request.POST.get('item_price')
			
			# item_package     = request.POST.get('item_package')
			# if item_package == 'on':
			#     is_package = True
			# else:
			#     is_package = False
			
			item_add_type   = request.POST.get('itemadd_type')
			
			if item_add_type == 'quantity':
				unit_measure    = request.POST.get('unit_measure')
			else:
				unit_measure    = None

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
		
			item_code_series = str(category.category_id)+str(segment.segment_id)+str(line.line_id)

			latest_item_code = InventoryItem.objects.filter(item_code__contains=item_code_series).last()

			if latest_item_code:
				new_item_code = item_code_series + str(int(latest_item_code.item_code[6:])+1)
			else:
				new_item_code = item_code_series + '101'
			print(new_item_code,"lop")

			inv_item = InventoryItem.objects.create(item_type=item_type,item_category=category,item_segment=segment,item_line=line,name=name,item_code=new_item_code,description=description,reserve_count=reserve,is_reusable=reusable,item_add_type=item_add_type,measuring_unit=unit_measure)
			
			if supplier_id:
				supplier_items_latest = SupplierItems.objects.all().last()

				if supplier_items_latest:
					code_number  =  int(re.findall(r'(\d+)', supplier_items_latest.supplier_item_id)[0]) + 1
					new_supplier_item_id = 'SPITM'+str(code_number)
				else:
					new_supplier_item_id = 'SPITM9001'

				supplier = Supplier.objects.get(id=int(supplier_id))
				SupplierItems.objects.create(supplier=supplier,item=inv_item,item_price=item_price,supplier_item_id=new_supplier_item_id)
			
			messages.success(request,"Item Added Successfully !")
			return redirect('bleach-inventory:inventory-item',inv_item.id)

		if action == 'edit_item':
			print("edit")
			item_type= request.POST.get('item_type')
			name     = request.POST.get('item_name')
			item_id = request.POST.get('item_edit_id')
			category_id = request.POST.get('item_category')
			segment_id = request.POST.get('item_segment')
			line_id = request.POST.get('item_line')
			description = request.POST.get('item_description')
			reserve = request.POST.get('item_reserve')
			status     = request.POST.get('item_status')
			reusable     = request.POST.get('item_reusable')
			item_add_type     = request.POST.get('itemadd_type')
			unit_measure     = request.POST.get('unit_measure')
			# item_package     = request.POST.get('item_package')
			# if item_package == 'on':
			#     is_package = True
			# else:
			#     is_package = False

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

			item.item_type      = item_type
			item.item_category  = category
			item.item_segment   = segment
			item.item_line      = line
			item.name           = name
			item.description    = description
			item.reserve_count  = reserve
			item.status         = status
			item.is_reusable    = reusable
			item.item_add_type  = item_add_type
			item.measuring_unit = unit_measure
			item.save()
			messages.success(request,"Item Updated Successfully !")
		
		if action == 'delete_item':
			item_id = request.POST.get('item_id')
			InventoryItem.objects.get(id=int(item_id)).delete()
			messages.success(request,"Item Deleted Successfully !")

			if request.POST.get('return_to') == 'dashboard':
				return redirect('bleach-inventory:inventorydash-board')

		return redirect('bleach-inventory:inventory-inv')

class InventoryOrder(IsInventoryAdminUser,View):
	def get(self,request):
		search = request.GET.get('search')
		order_date = request.GET.get('order_date')          

		if order_date:
			order_date = datetime.strptime(order_date,'%d-%m-%Y')
		else:
			order_date = date.today()

		print(search,order_date,"ser")
		
		calendar_order_schedules_list       = []
		calendar_order_schedules_duplicates = []
		# orders       = CleaningTeam.objects.select_related('team_leader','order_scheduler__order').filter(order_scheduler__start_at__date=order_date).filter(Q(order_scheduler__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler__work_status='CLEANING_IN_PROGRESS')|Q(order_scheduler__work_status='CLEANING_FULFILLED')).annotate(duplicate=Concat('order_scheduler__start_at','order_scheduler__order__id','team_leader__id',output_field=CharField()))
		orders       = CleaningTeam.objects.filter(order_scheduler__start_at__date=order_date).filter(Q(order_scheduler__work_status='CLEANING_TEAM_ASSIGNED')|Q(order_scheduler__work_status='CLEANING_IN_PROGRESS')|Q(order_scheduler__work_status='CLEANING_FULFILLED')).annotate(duplicate=Concat('order_scheduler__start_at','order_scheduler__order__id','team_leader__id',output_field=CharField()))
		# for calendar_order_schedules_all in calendar_order_schedules_alls:
		# 	if not calendar_order_schedules_all.duplicate in calendar_order_schedules_duplicates:
		# 		calendar_order_schedules_list.append(calendar_order_schedules_all.order_scheduler.id)
		# 		calendar_order_schedules_duplicates.append(calendar_order_schedules_all.duplicate)
		
		# if search:
		# 	orders = OrderScheduler.objects.filter(id__in=calendar_order_schedules_list).filter(Q(order_scheduler_book__service_type__icontains=search)|Q(cleaning_team_order_scheduler__team_leader__name__icontains=search)).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).order_by('-start_at')
		# else:
		# 	orders = OrderScheduler.objects.filter(id__in=calendar_order_schedules_list).select_related('order__evaluation__customer','customer_address','order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team')).order_by('-start_at')

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

class InventoryUsers(IsInventoryAdminUser,View):
	def get(self,request):
		return render(request,'inventory/users.html',{})

class PendingItems(IsInventoryAdminUser,View):
	def get(self,request):
		search = request.GET.get('search')

		# if search:
		# 	checkout_items = CheckOutItems.objects.filter(is_checked_in=False,visit__stock_in_initiated=True).filter(Q(service_item__item__is_reusable=True)|Q(item__is_reusable=True)).filter(Q(visit__order__order_no__icontains=search)|Q(is_collected_by__name__icontains=search)|Q(service_item__item__name__icontains=search)|Q(item__name__icontains=search)|Q(service_item__item__item_code__icontains=search)|Q(item__item_code__icontains=search)).select_related('visit').prefetch_related(Prefetch('visit__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team'))
		# else:
		# 	checkout_items = CheckOutItems.objects.filter(is_checked_in=False,visit__stock_in_initiated=True).filter(Q(service_item__item__is_reusable=True)|Q(item__is_reusable=True)).select_related('visit').prefetch_related(Prefetch('visit__cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True),to_attr='cleaning_team'))
		
		checkout_items = CleaningTeam.objects.all()
		
		#PAGINATION ITEMS
		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1)
		paginator=Paginator(checkout_items,no_of_entries)
		try:
			checkout_items=paginator.page(page)
		except PageNotAnInteger:
			checkout_items=paginator.page(1)
		except EmptyPage:
			checkout_items = paginator.page(paginator.num_pages)

		# Get the index of the current page
		index = checkout_items.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]
		entry_per_page=(checkout_items.end_index())-(checkout_items.start_index())+1
		
		return render(request,'inventory/pending.html',{"checkout_items":checkout_items,"page_range":page_range,"entry_per_page":entry_per_page,"no_of_entries":no_of_entries,"search_query":search})        

class InventoryCheckout(IsInventoryAdminUser,View):
	def get(self,request):
		return render(request,'inventory/checkout.html',{})

class InventoryCreateCheckout(IsInventoryAdminUser,View):
	def get(self,request,visit_id):
		store_id = request.GET.get('store_id')
		
		if store_id:
			store = Store.objects.get(id=int(store_id))
		else:
			# store = Store.objects.get(id=1)
			store = Store.objects.get(store_name='AL-RAI STORE')
		
		checkout_visit = OrderScheduler.objects.select_related('order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='team_members')),to_attr='cleaning_team'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections')).get(id=int(visit_id))
		
		for team in checkout_visit.cleaning_team:
			team_leader = team.team_leader

		visits = OrderScheduler.objects.filter(order__order_no=checkout_visit.order.order_no,start_at=checkout_visit.start_at,cleaning_team_order_scheduler__team_leader=team_leader).select_related('order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='team_members')),to_attr='cleaning_team'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections'))
		
		print(visits,"vissts")

		# items = InventoryItem.objects.filter(Q(item_status='available')|Q(item_status='about_to_finish'))

		itemslist = InventoryItem.objects.filter(Q(item_status='available')|Q(item_status='about_to_finish')).prefetch_related(Prefetch('unit_item',queryset=ItemUnit.objects.filter(is_available=True,store=store),to_attr='item_units'),Prefetch('quantity_store_item',queryset=QuantityStoreDetails.objects.filter(item_store=store),to_attr='quantity_items'))
		
		items = []
		found = set()

		for item in itemslist:
			for unit in item.item_units:
				if unit.item not in found:
					items.append(unit.item)
					found.add(unit.item)

			for qty in item.quantity_items:
				if qty.quantity_item not in found and qty.quantity > 0:
					items.append(qty.quantity_item)
					found.add(qty.quantity_item)

		print(items,"its")
		# service = visit.order_scheduler_book.service_type
		price_ranges = None
		stock_out = request.GET.get('stockout')
		print(stock_out,"stk")
		max_area = 0
		cleaners = 0

		check_out_items = CheckOutItems.objects.filter(visit=checkout_visit).prefetch_related(Prefetch('checkoutitem',queryset=CheckOutItemUnits.objects.all(),to_attr='checkoutitem_units')).order_by('service_item__ingredient__id')
		
		
		if stock_out == 'order' and checkout_visit.stock_out_items_saved == False:
			
			checkout_items = CheckOutItems.objects.filter(visit__id=int(visit_id)).delete()
		

		if store and stock_out != 'order':

			if checkout_visit.stock_out_items_saved == False:
				CheckOutItems.objects.filter(visit=checkout_visit).delete()
				
				cleaners_items_count_list = []
				items_list = []

				for visit in visits: 
					# visit.stock_out_items_saved = True
					# visit.save()

					service = visit.order_scheduler_book.service_type
					price_ranges = ServicePriceRange.objects.filter(is_active=True,service_type=service)

					for section in visit.order_scheduler_book.sections:
					
						if section.size:
							if section.size.isnumeric() == True:
								max_area += float(section.size)
								print(max_area,"mx")
							else:
								print("mok")
								if visit.order_scheduler_book.service_type.name == 'Upholstery Cleaning':
									
									for price_range in price_ranges:
										if price_range.name == section.size and price_range.service_type == section.evaluation_book.service_type and price_range.upholstery_type == section.upholstery_type:
											max_area += float(price_range.maximum_area)
								else:
									for price_range in price_ranges:
										if price_range.name == section.size and price_range.service_type == section.evaluation_book.service_type and section.evaluation_book.service_type.name != 'Mattress Cleaning' and price_range.is_newkitchen == section.new_kitchen and price_range.is_cabinet == section.is_cabinet and price_range.is_highprice_facade == section.is_highprice_facade and price_range.is_highprice_window == section.is_highprice_window:
											max_area += float(price_range.maximum_area)
				
					cleaners += visit.no_of_cleaners

					service_recipe_ingredients = ServiceRecipeIngredients.objects.filter(service_type__service=service).prefetch_related(Prefetch('item_ingredient',queryset=ServiceRecipeItems.objects.all(),to_attr='service_recipe_items'))

					# recommended quantity calc
						
					for ingredient in service_recipe_ingredients:
						service_quantity = ingredient.quantity

						recommended_quantity = 0

						if ingredient.service_or_person == 'service':
							
							service_area = ingredient.service_type.area_size
							
							if service_area != '0':
								recommended_quantity = float(math.ceil(float(max_area) / float(service_area)) * float(service_quantity))

						else:
							service_person = ingredient.service_type.staff_count

							if service_person != '0':
								
								quantity_per_person = float(service_quantity) / float(service_person)

								recommended_quantity = float(cleaners) * float(quantity_per_person)

						# items_list = []
						
						for service_item in ingredient.service_recipe_items:    

							
							item = InventoryItem.objects.annotate(quantity_total=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField()))).get(id=int(service_item.item.id))
							
							
							if service_item.item.item_add_type == 'unit':

								itemstore = ItemUnit.objects.filter(item=item,store=store).count()
								# if itemstore > 0:
								item_dict = {
									'item_id' : item.id,
									'item_name' : item.name,
									'total_quantity' : float(item.quantity_total),
									'item_type' : item.item_add_type,
									'service' : visit.order_scheduler_book.service_type.name,
									'service_item_id' : service_item.id,
									'recommended_quantity' : recommended_quantity
								}
								print(item.quantity_total,"qx")

								items_list.append(item_dict) 
							else:
								itemstore = QuantityStoreDetails.objects.filter(item_store=store,quantity_item=item).first()

								if itemstore:
									
									item_dict = {
										'item_id' : item.id,
										'item_name' : item.name,
										'total_quantity' : float(itemstore.quantity),
										'item_type' : item.item_add_type,
										'service' : visit.order_scheduler_book.service_type.name,
										'service_item_id' : service_item.id,
										'recommended_quantity' : recommended_quantity
									}
									print(item.total_quantity,"qx2")

									items_list.append(item_dict)  

								if itemstore:
									
									item_dict = {
										'item_id' : item.id,
										'item_name' : item.name,
										'total_quantity' : float(itemstore.quantity),
										'item_type' : item.item_add_type,
										'service' : visit.order_scheduler_book.service_type.name,
										'service_item_id' : service_item.id,
										'recommended_quantity' : recommended_quantity
									}
									print(item.total_quantity,"qx2")

									items_list.append(item_dict)
				

				#removng duplicate item counts for same service
				service_combined_list = []

				service_found = set()
				for i in items_list:
					if i['service'] not in service_found:
						service_dicts = [item for item in items_list if item['service'] == i['service']]
						service_found.add(i['service'])

						item_found = set()

						for service_item in service_dicts:
							if service_item['item_id'] not in item_found:
								
								item_dicts = [item for item in service_dicts if item['item_id'] == service_item['item_id']]
								
								maxQuantity = max(item_dicts, key=lambda x:x['recommended_quantity'])
								
								item_found.add(service_item['item_id'])
								service_combined_list.append(maxQuantity)				

				print(service_combined_list,"eye66")

				newlist = sorted(service_combined_list, key=lambda d: d['total_quantity'], reverse=True) 
						
				# variable_recommended_quantity = recommended_quantity

				print(items_list,"itlist44")
				print(newlist,"newitlist44")

				
				for item in newlist:
					
					if int(item['recommended_quantity']) != 0:

						service_item = ServiceRecipeItems.objects.get(id=int(item['service_item_id']))

						#unit items service ingredient count check if all added
						existing_qty_count = CheckOutItems.objects.filter(visit=checkout_visit,service_item__item__item_add_type='unit',service_item__ingredient=service_item.ingredient,is_checked_out=False).count()

						#quantity items ingredient total calc for adding
						
						existing_qty_total = CheckOutItems.objects.filter(visit=checkout_visit,service_item__item__item_add_type='quantity',service_item__ingredient=service_item.ingredient,is_checked_out=False).aggregate(qty_total=Sum('units'))['qty_total']
						if existing_qty_total == None:
							existing_qty_total = 0

						print(existing_qty_total,"existtt")

						#case1
						if item['total_quantity'] > 0 and float(item['total_quantity']) >= float(item['recommended_quantity']):
							
							try:
								checkout_item = CheckOutItems.objects.get(visit=checkout_visit,service_item=service_item,service_item__ingredient=service_item.ingredient,is_checked_out=False)
								
							except:
								
								if service_item.item.item_add_type == 'quantity' and float(item['recommended_quantity']) > float(existing_qty_total) :
									
									CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,units=math.ceil(float(item['recommended_quantity'])),is_swapped_item=False)
								
								if service_item.item.item_add_type == 'unit':
									
									itemunits = ItemUnit.objects.filter(item=service_item.item,store=store).order_by('-is_available')[:int(item['recommended_quantity'])]
									
									for unit in itemunits:
										try:
											CheckOutItems.objects.get(visit=checkout_visit,item_unit=unit,is_checked_out=False)
										except:
											if int(existing_qty_count) < int(item['recommended_quantity']):
												if unit.is_available == True:
													CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,item_unit=unit,units=1,is_swapped_item=False)
												else:
													CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,item_unit=unit,units=0,recommended_quantity=math.ceil(item['recommended_quantity']),is_swapped_item=False)
			

						#case2
						elif item['total_quantity'] > 0 and float(item['total_quantity']) < float(item['recommended_quantity']) :
							
							try:
								checkout_item = CheckOutItems.objects.get(visit=checkout_visit,service_item=service_item,service_item__ingredient=service_item.ingredient,is_checked_out=False)
							except:
								if service_item.item.item_add_type == 'quantity' and float(item['recommended_quantity']) > float(existing_qty_total):
									
									CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,units=math.ceil(item['total_quantity']),recommended_quantity=math.ceil(item['recommended_quantity']),is_swapped_item=False)
									

								if service_item.item.item_add_type == 'unit':
									itemunits = ItemUnit.objects.filter(item=service_item.item,store=store).order_by('-is_available')[:int(item['total_quantity'])]
									print(itemunits,"rrr3")
									for unit in itemunits:
										try:
											CheckOutItems.objects.get(visit=checkout_visit,item_unit=unit,is_checked_out=False)
										except:
											if int(existing_qty_count) < int(item['recommended_quantity']):
												if unit.is_available == True:
													CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,item_unit=unit,units=1,recommended_quantity=math.ceil(item['recommended_quantity']),is_swapped_item=False)
												else:
													CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,item_unit=unit,units=0,recommended_quantity=math.ceil(item['recommended_quantity']),is_swapped_item=False)   

						else:
							print(item['total_quantity'],item['recommended_quantity'],"rebut")
							try:
								checkout_item = CheckOutItems.objects.get(visit=checkout_visit,service_item=service_item,service_item__ingredient=service_item.ingredient,is_checked_out=False)
							except:
								# if service_item.item.item_add_type == 'quantity':
								# 	CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,units=math.ceil(item['total_quantity']),recommended_quantity=math.ceil(item['recommended_quantity']),is_swapped_item=False)
							
								if service_item.item.item_add_type == 'unit':
									if int(existing_qty_count) < int(item['recommended_quantity']):
										try:
											CheckOutItems.objects.get(visit=checkout_visit,service_item=service_item,is_checked_out=False)
										except:
											CheckOutItems.objects.create(visit=checkout_visit,service_item=service_item,units=math.ceil(item['total_quantity']),recommended_quantity=math.ceil(item['recommended_quantity']),is_swapped_item=False)
				

		return render(request,'inventory/createCheckout.html',{"store":store,"max_area":max_area,"cleaners":cleaners,"stock_out":stock_out,"price_ranges":price_ranges,"visit":checkout_visit,"visits":visits,"items":items,"check_out_items":check_out_items})

	def post(self,request,visit_id):
		checkout_visit = OrderScheduler.objects.select_related('order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='team_members')),to_attr='cleaning_team'),Prefetch('order_scheduler_book__evaluationsection_book',queryset=EvaluationBookSection.objects.filter(is_active=True).prefetch_related(Prefetch('keynotesections',EvaluationSectionKeynote.objects.filter(is_active=True),to_attr='keynotes'),Prefetch('addonsections',queryset=EvaluationSectionAddons.objects.filter(is_active=True),to_attr='sectionaddons')),to_attr='sections')).get(id=int(visit_id))
		
		for team in checkout_visit.cleaning_team:
			team_leader = team.team_leader

		visits = OrderScheduler.objects.filter(order__order_no=checkout_visit.order.order_no,start_at=checkout_visit.start_at,cleaning_team_order_scheduler__team_leader=team_leader)
		
		print(visits,"vissts")

		action = request.POST.get('action')

		if action == 'reset_list':
			print("ress")
			checkout_items = CheckOutItems.objects.filter(visit=checkout_visit).delete()

			for visit in visits:
				visit.stock_out_items_saved = False
				visit.save()

			messages.success(request,"List Reset!")
			return redirect('/bleach-inventory/createcheckout/'+visit_id+'/?stockout=stockout')

		if action == 'save_checkout_list':

			for visit in visits:
				visit.stock_out_items_saved = True
				visit.save()

			checkout_items=CheckOutItems.objects.filter(visit=checkout_visit,is_checked_out=False)	
			for item in checkout_items:
				if item.units == '0' :
					item.delete()

			messages.success(request,"Check Out List saved !")
			return redirect('bleach-inventory:inventory-order')


		if action == 'submit_checkout_list':
			# quantities = request.POST.get('quantities')
			
			# quantities = quantities.split(",")
			store_id = request.POST.get('store_id')
			store = Store.objects.get(id=int(store_id))
			print(store,"storra")

			checkout_items=CheckOutItems.objects.filter(visit=checkout_visit,is_checked_out=False)

			count = 0
				
			for item in checkout_items:

				if item.units == '0' :
					item.delete()

				else:

					count += 1

					if item.item and item.item.item_add_type == 'unit':
		
						if item.item_unit:
							itemunit = ItemUnit.objects.get(id=int(item.item_unit.id))
							itemunit.status = 'working'
							itemunit.is_available=False
							itemunit.save()

					if item.item and item.item.item_add_type == 'quantity':

						try:
							store_item     = QuantityStoreDetails.objects.get(item_store=store,quantity_item=item.item)
						except:
							store_item     = None
						
						inventoryitem = InventoryItem.objects.prefetch_related(Prefetch('unit_item',queryset=ItemUnit.objects.filter(is_available=True),to_attr='item_units')).get(id=int(item.item.id))
						
						print(inventoryitem.total_quantity,"krok")
						if float(store_item.quantity) >= float(item.units):
							
							inventoryitem.total_quantity = round(float(inventoryitem.total_quantity) - float(item.units),2)
							inventoryitem.save()

							store_item.quantity = round(float(store_item.quantity) - float(item.units),2)
							store_item.save()

							ItemHistory.objects.create(item=inventoryitem,quantity=float(item.units),quantity_location=store,item_action='STOCK OUT',item_remark=checkout_visit.order.order_no,added_by=team_leader)

						else:
							messages.error(request,"Quantity limit exceeded !")
							return redirect('bleach-inventory:inventory-createcheckout',visit_id)

					if item.service_item and item.service_item.item.item_add_type == 'unit':
						
						if item.item_unit:
							itemunit = ItemUnit.objects.get(id=int(item.item_unit.id))
							itemunit.status = 'working'
							itemunit.is_available=False
							itemunit.save()

					if item.service_item and item.service_item.item.item_add_type == 'quantity':
						
						try:
							store_item     = QuantityStoreDetails.objects.get(item_store=store,quantity_item=item.service_item.item)
						except:
							store_item     = None

						inventoryitem = InventoryItem.objects.prefetch_related(Prefetch('unit_item',queryset=ItemUnit.objects.filter(is_available=True),to_attr='item_units')).get(id=int(item.service_item.item.id))
						
						if float(store_item.quantity) >= float(item.units):
							inventoryitem.total_quantity = round(float(inventoryitem.total_quantity) - float(item.units),2)
							inventoryitem.save()

							store_item.quantity = round(float(store_item.quantity) - float(item.units),2)
							store_item.save()

							ItemHistory.objects.create(item=inventoryitem,quantity=float(item.units),quantity_location=store,item_action='STOCK OUT',item_remark=checkout_visit.order.order_no,added_by=team_leader)

					item.is_checked_out = True
					item.checked_out_date = date.today()
					item.is_checked_out_by = request.user
					item.save()

			if count > 0 :
				for visit in visits:
					print("visittest")
					visit.stock_out_items_saved = True
					visit.stock_out_items_submitted = True
					visit.save()

				messages.success(request,"Check Out List submitted !")
			else:
				messages.error(request,"Not enough items to Check Out !")
			return redirect('bleach-inventory:inventory-order')
	
		return redirect('bleach-inventory:inventory-createcheckout',visit_id)

class InventoryPurchaseOrder(IsInventoryAdminUser,View):
	def get(self,request):
		search = request.GET.get('search')

		purchase_order_type = request.GET.get('purchase_order_type',None)
		print(purchase_order_type,"potyip")

		if search:
			purchase_orders_pending = PurchaseOrder.objects.filter(is_order_completed=True,is_received=False).filter(Q( Q(purchase_order_id__icontains = search) | Q(supplier__supplier_name__icontains = search) )).annotate(total_units=Sum('purchase_order_purchase_order_item__item_count'), total_added_units=Sum('purchase_order_purchase_order_item__added_item_count'), total_price=Sum('purchase_order_purchase_order_item__total_price')).order_by('-id')
			purchase_orders_received = PurchaseOrder.objects.filter(is_order_completed=True,is_received=True).filter(Q( Q(purchase_order_id__icontains = search) | Q(supplier__supplier_name__icontains = search) )).annotate(total_units=Sum('purchase_order_purchase_order_item__item_count'), total_added_units=Sum('purchase_order_purchase_order_item__added_item_count'), total_price=Sum('purchase_order_purchase_order_item__total_price')).order_by('-id')
		else:
			purchase_orders_pending = PurchaseOrder.objects.filter(is_order_completed=True,is_received=False).annotate(total_units=Sum('purchase_order_purchase_order_item__item_count'), total_added_units=Sum('purchase_order_purchase_order_item__added_item_count'), total_price=Sum('purchase_order_purchase_order_item__total_price')).order_by('-id')
			purchase_orders_received = PurchaseOrder.objects.filter(is_order_completed=True,is_received=True).annotate(total_units=Sum('purchase_order_purchase_order_item__item_count'), total_added_units=Sum('purchase_order_purchase_order_item__added_item_count'), total_price=Sum('purchase_order_purchase_order_item__total_price')).order_by('-id')
		
		#PAGINATION pending tab
		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1)

		paginator=Paginator(purchase_orders_pending,no_of_entries)
		try:
			purchase_orders_pending=paginator.page(page)
		except PageNotAnInteger:
			purchase_orders_pending=paginator.page(1)
		except EmptyPage:
			purchase_orders_pending = paginator.page(paginator.num_pages)

		# Get the index of the current page
		index = purchase_orders_pending.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]

		entry_per_page=(purchase_orders_pending.end_index())-(purchase_orders_pending.start_index())+1

		#received tab pagination
		page2 = request.GET.get('page2',1)

		paginator2=Paginator(purchase_orders_received,no_of_entries)
		try:
			purchase_orders_received=paginator2.page(page2)
		except PageNotAnInteger:
			purchase_orders_received=paginator2.page(1)
		except EmptyPage:
			purchase_orders_received = paginator2.page(paginator2.num_pages)

		# Get the index of the current page
		index2 = purchase_orders_received.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index2 = len(paginator2.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index2 = index2 - 3 if index2 >= 3 else 0
		end_index2 = index2 + 3 if index2 <= max_index2 - 3 else max_index2
		# Get our new page range. In the latest versions of Django page_range returns
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range2 = list(paginator2.page_range)[start_index2:end_index2]

		entry_per_page2=(purchase_orders_received.end_index())-(purchase_orders_received.start_index())+1
		
		return render(request,'inventory/purchaseOrder.html',{"purchase_order_type":purchase_order_type,"purchase_orders_pending":purchase_orders_pending,"purchase_orders_received":purchase_orders_received,"page_range":page_range,"page_range2":page_range2,"entry_per_page":entry_per_page,"entry_per_page2":entry_per_page2,"no_of_entries":no_of_entries,"search_query":search})

	def post(self,request):
		action = request.POST.get('action')

		if action == 'delete_order':
			order_id = request.POST.get('order_id')
			PurchaseOrder.objects.get(id=int(order_id)).delete()
			messages.success(request,"Purchase Order Deleted successfully!")

		return redirect('bleach-inventory:inventory-purchaseorder')

class PurchaseOrderApproval(IsInventoryAdmin,View):
	def get(self,request,purchase_order_id):
		purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.all(),to_attr='purchase_order_items')).annotate(po_total=Sum('purchase_order_purchase_order_item__total_price')).get(id=int(purchase_order_id))
		shipment_status = request.GET.get('shipment_status')
		if shipment_status == 'approved':
			purchase_order.is_admin_approved = True
			purchase_order.is_rejected = False
			purchase_order.save()

			return redirect('bleach-inventory:inventory-purchaseorder')

		if shipment_status == 'rejected':
			purchase_order.is_admin_approved = False
			purchase_order.is_rejected = True
			purchase_order.save() 

			return redirect('bleach-inventory:inventory-purchaseorder') 

		return render(request,"inventory/po_admin_approval.html",{"purchase_order":purchase_order})

class PurchaseOrderItemsPage(IsInventoryAdminUser,View):
	def get(self,request,purchase_order_id):
		stores = Store.objects.filter(status=True)
		purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.select_related('product').all(),to_attr='purchase_order_items')).annotate(total_items_count=Sum('purchase_order_purchase_order_item__item_count'),total_added_items_count=Sum('purchase_order_purchase_order_item__added_item_count'),po_total=Sum('purchase_order_purchase_order_item__total_price'),total_qty_order_price=Sum(Case(When(purchase_order_purchase_order_item__product__item__item_add_type='quantity',then='purchase_order_purchase_order_item__total_price'),default=0,output_field=IntegerField())),total_unit_order_price=Sum(Case(When(purchase_order_purchase_order_item__product__item__item_add_type='unit',then='purchase_order_purchase_order_item__total_price'),default=0,output_field=IntegerField()))).get(id=int(purchase_order_id))
		shipment_status = request.GET.get('shipment_status')
		if shipment_status == 'complete':
			purchase_order.is_received = True
			purchase_order.save()

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
			store_id = request.POST.get('store_id')
			store = Store.objects.get(id=int(store_id))
			print(products,item_counts,"cts")

			loopcount = 0
			for product in products:
				item = InventoryItem.objects.get(id=int(product))
				purchase_order_item = PurchaseOrderItems.objects.get(purchase_order=purchase_order,product__item__id=int(product))
				print(item,item_counts[loopcount], "itm")
				
				
				try:
					quantitystore = QuantityStoreDetails.objects.get(item_store=store,quantity_item = item)
					quantitystore.quantity = float(quantitystore.quantity) + float(item_counts[loopcount])
					quantitystore.save()
				except:
					QuantityStoreDetails.objects.create(
					item_store = store,
					quantity_item = item,
					quantity = item_counts[loopcount]
					)

				item.total_quantity = float(item.total_quantity) + float(item_counts[loopcount])
				item.save()

				ItemHistory.objects.create(purchase_order=purchase_order,quantity_location=store,item=item,quantity=item_counts[loopcount],item_action='PURCHASE ORDER',item_remark=purchase_order.purchase_order_id,added_by=purchase_order_item.purchase_order.initiated_by)

				purchase_order_item.is_received = True
				purchase_order_item.added_item_count = float(item_counts[loopcount])
				purchase_order_item.save()
				loopcount += 1

			messages.success(request,"Quantity added to Inventory")

		if action == 'add_unit_to_inventory':
			item_id = request.POST.get('item_id')
			store_id = request.POST.get('store')
			serial_number = request.POST.get('serial_number')
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

			purchase_order_item = PurchaseOrderItems.objects.get(purchase_order=purchase_order,product__item__id=int(item_id))
			
			purchase_order_item.added_item_count = int(purchase_order_item.added_item_count) + 1
			purchase_order_item.save()

			print(purchase_order_item.added_item_count,purchase_order_item.item_count,"compr")
			if int(purchase_order_item.added_item_count) == int(purchase_order_item.item_count):
				print("reciv")
				purchase_order_item.is_received = True
				purchase_order_item.save()

			messages.success(request,"Unit added to Inventory")

		return redirect('bleach-inventory:inventory-purchaseorderitems', purchase_order_id)

class InventoryPurchaseOrderPage(View):
	def get(self,request,purchase_order_id):
		purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.select_related('product').all(),to_attr='purchase_order_items')).get(id=int(purchase_order_id))
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
		stores = Store.objects.filter(status=True)

		supplier_id = request.GET.get('supplier_id')
		if supplier_id :
			supplier = Supplier.objects.get(id=int(supplier_id))
			purchase_order.supplier = supplier
			purchase_order.save()

			items = SupplierItems.objects.filter(supplier__id=purchase_order.supplier.id)
		else:
			supplier = None
			items = SupplierItems.objects.all()

		print(items,"prin")

		store_id = request.GET.get('store_id')
		if store_id :
			store = Store.objects.get(id=int(store_id))
			purchase_order.store = store
			purchase_order.save()
		else:
			store = None

		purchase_order_items = PurchaseOrderItems.objects.select_related('product').filter(purchase_order=purchase_order,purchase_order__supplier=purchase_order.supplier)

		return render(request,'inventory/createpo.html',{"items":items,"suppliers":suppliers,"stores":stores,"supplier":supplier,"store":store,"purchase_order":purchase_order,"purchase_order_items":purchase_order_items})

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
			purchase_order_notes = request.POST.get('purchase_order_notes')

			purchase_order = PurchaseOrder.objects.get(id=int(purchase_order_id))
			purchase_order.discount = discount
			purchase_order.tax = tax
			purchase_order.shipping_charge = shipping_charges
			purchase_order.other_charge = other_charges
			purchase_order.currency = purchase_order.supplier.currency
			purchase_order.purchase_order_notes = purchase_order_notes

			purchase_order.is_order_completed = True
			purchase_order.save()
			messages.success(request,"Order Completed successfully!")
			return redirect('bleach-inventory:inventory-purchaseorderpage',purchase_order.id)

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


		return redirect('bleach-inventory:inventory-createpurchaseorder')


class InventoryEditPurchaseOrder(IsInventoryAdminUser,View):
	def get(self,request,purchase_order_id):

		purchase_order = PurchaseOrder.objects.prefetch_related(Prefetch('purchase_order_purchase_order_item',queryset=PurchaseOrderItems.objects.select_related('product').all(),to_attr='purchase_order_items')).annotate(total_order_price=Sum('purchase_order_purchase_order_item__total_price')).get(id=int(purchase_order_id))

		suppliers = Supplier.objects.filter(status=True)

		supplier_id = request.GET.get('supplier_id')
		if supplier_id :
			supplier = Supplier.objects.get(id=int(supplier_id))
			purchase_order.supplier = supplier
			purchase_order.save()
		else:
			supplier = None

		items = SupplierItems.objects.filter(supplier=purchase_order.supplier)

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
				purchase_order_notes = request.POST.get('purchase_order_notes')

				purchase_order = PurchaseOrder.objects.get(id=int(purchase_order_id))
				purchase_order.discount = discount
				purchase_order.tax = tax
				purchase_order.shipping_charge = shipping_charges
				purchase_order.other_charge = other_charges
				purchase_order.purchase_order_notes = purchase_order_notes

				purchase_order.is_order_completed = True
				purchase_order.save()
				messages.success(request,"Order Updated successfully!")
				return redirect('bleach-inventory:inventory-purchaseorder')

			return redirect('bleach-inventory:inventory-editpurchaseorder',purchase_order_id)

class InventoryViewPurchaseOrder(IsInventoryAdminUser,View):
	def get(self,request):
		return render(request,'inventory/viewpo.html',{})

class InventoryCheckedIn(IsInventoryAdminUser,View):
	def get(self,request):
		return render(request,'inventory/checkin.html',{})

class InventoryOrderDetails(IsInventoryAdminUser,View):
	def get(self,request):
		return render(request,'inventory/orderdetails.html',{})

class InventoryServices(IsInventoryAdminUser,View):
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

			ServiceRecipeIngredients.objects.create(service_or_person=recipe_type,service_type=get_servicetype,ingredient=ingredient,quantity=math.ceil(item_count),status=item_status)

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
			serviceingredient.quantity = math.ceil(item_count)
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

		return redirect('bleach-inventory:inventory-services')

class InventorySegment(IsInventoryAdminUser,View):
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
			
		return redirect('bleach-inventory:inventory-segment', category_id)

# def stockout(request,visit_id):
#     visit = OrderScheduler.objects.select_related('order_scheduler_book').prefetch_related(Prefetch('cleaning_team_order_scheduler',queryset=CleaningTeam.objects.filter(is_active=True).prefetch_related(Prefetch('cleaning_member_team',queryset=CleaningTeamMember.objects.filter(is_active=True),to_attr='team_members')),to_attr='cleaning_team')).get(id=int(visit_id))
#     check_out_items = CheckOutItems.objects.filter(visit=visit)
#     return render(request,"customer/downloads/stock-out-sheet.html",{"visit":visit,"check_out_items":check_out_items})


#Done By Ansab
class InventoryRequestOrder(IsInventoryAdminUser,View):
	def get(self,request):
		search = request.GET.get('search')

		request_order_type = request.GET.get('request_order_type',None)

		if search:
			request_orders_pending = RequestOrder.objects.filter(is_order_completed=True,is_received=False).filter(Q( Q(request_order_id__icontains = search) | Q(requested_by__name__icontains = search) )).annotate(total_added_units=Sum('items_request_order__item_count')).order_by('-id')
			request_orders_delivered = RequestOrder.objects.filter(is_order_completed=True,is_received=True).filter(Q( Q(request_order_id__icontains = search) | Q(requested_by__name__icontains = search) )).annotate(total_added_units=Sum('items_request_order__item_count')).order_by('-id')
		else:
			request_orders_pending = RequestOrder.objects.filter(is_order_completed=True,is_received=False).annotate(total_added_units=Sum('items_request_order__item_count')).order_by('-id')
			request_orders_delivered = RequestOrder.objects.filter(is_order_completed=True,is_received=True).annotate(total_added_units=Sum('items_request_order__item_count')).order_by('-id')
		
		#PAGINATION pending tab
		no_of_entries = request.GET.get('no_of_entries')
		if not no_of_entries:
			no_of_entries = 20

		page = request.GET.get('page',1)

		paginator=Paginator(request_orders_pending,no_of_entries)
		try:
			request_orders_pending=paginator.page(page)
		except PageNotAnInteger:
			request_orders_pending=paginator.page(1)
		except EmptyPage:
			request_orders_pending = paginator.page(paginator.num_pages)

		# Get the index of the current page
		index = request_orders_pending.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]

		entry_per_page=(request_orders_pending.end_index())-(request_orders_pending.start_index())+1

		#received tab pagination
		page2 = request.GET.get('page2',1)

		paginator2=Paginator(request_orders_delivered,no_of_entries)
		try:
			request_orders_delivered=paginator2.page(page2)
		except PageNotAnInteger:
			request_orders_delivered=paginator2.page(1)
		except EmptyPage:
			request_orders_delivered = paginator2.page(paginator2.num_pages)

		# Get the index of the current page
		index2 = request_orders_delivered.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index2 = len(paginator2.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index2 = index2 - 3 if index2 >= 3 else 0
		end_index2 = index2 + 3 if index2 <= max_index2 - 3 else max_index2
		# Get our new page range. In the latest versions of Django page_range returns
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range2 = list(paginator2.page_range)[start_index2:end_index2]

		entry_per_page2=(request_orders_delivered.end_index())-(request_orders_delivered.start_index())+1

		return render(request,'inventory/requestOrder.html',{"request_order_type":request_order_type,"request_orders_delivered":request_orders_delivered,"request_orders_pending":request_orders_pending,"search_query":search,"page_range":page_range,"page_range2":page_range2,"entry_per_page":entry_per_page,"entry_per_page2":entry_per_page2,"no_of_entries":no_of_entries})

	def post(self,request):
		action = request.POST.get('action')

		if action == 'delete_requestorder':
			order_id       = request.POST.get('request_order_id')
			RequestOrder.objects.get(id=order_id).delete()
			messages.success(request,"Inventory Request Order Deleted successfully!")

		return redirect('bleach-inventory:inventory-requestorder')

class InventoryCreateInventoryRequest(View):
	def get(self,request):

		request_order = RequestOrder.objects.filter(is_order_completed=False,created_by=request.user).last()

		if not request_order:
			
			todate = datetime.now()

			request_order_latest = RequestOrder.objects.all().last()
			if request_order_latest:
				code_number =  re.findall(r'(\d+)', request_order_latest.request_order_id)[0]
				code_number = int(code_number[-4:])+1
				new_item_code = 'BLIR'+str(todate.year)+''+str(todate.month)+''+ str(code_number)
			else:
				new_item_code = 'BLIR'+str(todate.year)+''+str(todate.month)+'1001'
			
			request_order = RequestOrder.objects.create(request_order_id=new_item_code,created_by=request.user)
		
		inventory_items     = InventoryItem.objects.filter(~Q(item_type='FINISHED GOODS'))
		request_order_items = RequestOrderItems.objects.filter(request_order=request_order)
		request_users       = UserProfile.objects.filter(Q(Q(is_active=True)&~Q(user_type='CUSTOMER')))

		return render(request,'inventory/createir.html',{'request_users':request_users,'request_order':request_order,'inventory_items':inventory_items,'request_order_items':request_order_items})

	def post(self,request):
		action = request.POST.get('action')

		if action == 'add_item':
			request_order_id = request.POST.get('request_order_id')
			inventory_item   = request.POST.get('item')
			add_type         = request.POST.get('add_type')

			if add_type == 'quantity':
				quantity             = float(request.POST.get('item_count'))
				request_order_item   = RequestOrderItems.objects.create(request_order_id=request_order_id,product_id=inventory_item,item_count=quantity)
			elif add_type == 'unit':
				quantity             = 1
				unit_id              = request.POST.get('unit_id')
				request_order_item   = RequestOrderItems.objects.create(request_order_id=request_order_id,product_id=inventory_item,product_unit_id=unit_id,item_count=quantity)

			#for asset add accessories
			if request_order_item.product.item_type == 'ASSETS':
				accessories = InventoryAccessory.objects.filter(inventory_item=request_order_item.product)
				for accessory in accessories:		
					accessory_quantity = quantity*accessory.count
					RequestOrderItems.objects.create(request_order_id=request_order_id,product=accessory.inventory_accessory,item_count=accessory_quantity)

			messages.success(request,"Item Added successfully!")

		if action == 'edit_item':
			request_item_id         = request.POST.get('request_item_id')			
			product                 = request.POST.get('item')	
			add_type                = request.POST.get('add_type')
			request_item            = RequestOrderItems.objects.get(id=request_item_id)

			if add_type == 'quantity':
				item_count                   = request.POST.get('item_count')
				request_item.product_id      = product
				request_item.item_count      = item_count
			elif add_type == 'unit':
				unit_id                      = request.POST.get('unit_id')
				request_item.product_id      = product
				request_item.product_unit_id = unit_id
				
			request_item.save()
			
			messages.success(request,"Item Updated successfully!")

		
		if action == 'delete_item':
			item_id                = int(request.POST.get('item_id'))
			RequestOrderItems.objects.get(id=item_id).delete()
			
			messages.success(request,"Item Deleted successfully!")

		if action == 'order_close':
			print(request.POST)
			request_order_id = request.POST.get('request_order_id')

			request_order    = RequestOrder.objects.get(id=request_order_id)

			requested_by     = request.POST.get('requested_by')	
			if requested_by:
				try:
					requester = ExternalCustomer.objects.get(name=requested_by)
				except:
					requester = ExternalCustomer.objects.create(name=requested_by)
				
				if requester:
					request_order.requested_by = requester

			purpose                    = request.POST.get('purpose')
			if purpose:
				request_order.purpose  = purpose

			request_order.is_order_completed = True
			if request.user.user_type == 'INVENTORYADMIN' or purpose == 'INVENTORY PREPARATION': 
				request_order.is_admin_approved = True
			request_order.save()
			
			messages.success(request,"Inventory Request Order Completed successfully!")

			return redirect('bleach-inventory:inventory-requestorderitems',request_order.id)

		return redirect('bleach-inventory:inventory-createinventoryrequest')


class InventoryEditRequestOrder(IsInventoryAdminUser,View):
	def get(self,request,request_order_id):
		
		request_order = RequestOrder.objects.get(id=request_order_id)

		if not request_order:
			
			todate = datetime.now()

			request_order_latest = RequestOrder.objects.all().last()
			if request_order_latest:
				code_number =  re.findall(r'(\d+)', request_order_latest.request_order_id)[0]
				code_number = int(code_number[-4:])+1
				new_item_code = 'BLIR'+str(todate.year)+''+str(todate.month)+''+ str(code_number)
			else:
				new_item_code = 'BLIR'+str(todate.year)+''+str(todate.month)+'1001'
			
			request_order = RequestOrder.objects.create(request_order_id=new_item_code,created_by=request.user)
		
		inventory_items     = InventoryItem.objects.filter(~Q(item_type='FINISHED GOODS'))
		request_order_items = RequestOrderItems.objects.filter(request_order=request_order)
		request_users       = UserProfile.objects.filter(Q(Q(is_active=True)&~Q(user_type='CUSTOMER')))

		return render(request,'inventory/editir.html',{'request_users':request_users,'request_order':request_order,'inventory_items':inventory_items,'request_order_items':request_order_items})

	def post(self,request,request_order_id):
			action        = request.POST.get('action')
			
			#Rejected Order Recover
			request_order = RequestOrder.objects.get(id=request_order_id)
			request_order.is_rejected   = False
			request_order.rejected_by   = None
			request_order.rejected_date = None
			request_order.save()

			if action == 'add_item':
				request_order_id = request.POST.get('request_order_id')
				inventory_item   = request.POST.get('item')
				add_type         = request.POST.get('add_type')

				if add_type == 'quantity':
					quantity             = float(request.POST.get('item_count'))
					request_order_item   = RequestOrderItems.objects.create(request_order_id=request_order_id,product_id=inventory_item,item_count=quantity)
				elif add_type == 'unit':
					quantity             = 1
					unit_id              = request.POST.get('unit_id')
					request_order_item   = RequestOrderItems.objects.create(request_order_id=request_order_id,product_id=inventory_item,product_unit_id=unit_id,item_count=quantity)

				messages.success(request,"Item Added successfully!")

			if action == 'edit_item':
				request_item_id         = request.POST.get('request_item_id')			
				product                 = request.POST.get('item')	
				add_type                = request.POST.get('add_type')
				request_item            = RequestOrderItems.objects.get(id=request_item_id)

				if add_type == 'quantity':
					item_count                   = request.POST.get('item_count')
					request_item.product_id      = product
					request_item.item_count      = item_count
				elif add_type == 'unit':
					unit_id                      = request.POST.get('unit_id')
					request_item.product_id      = product
					request_item.product_unit_id = unit_id
					
				request_item.save()
				
				messages.success(request,"Item Updated successfully!")
			
			if action == 'delete_item':
				item_id                = request.POST.get('item_id')
				RequestOrderItems.objects.get(id=item_id).delete()
			
				messages.success(request,"Item Deleted successfully!")

			if action == 'order_close':
				request_order_id = request.POST.get('request_order_id')

				request_order    = RequestOrder.objects.get(id=request_order_id)
				
				requester_id     = request.POST.get('requester_id')	
				if requester_id:
					try:
						requester = ExternalCustomer.objects.get(name=requester_id)
					except:
						requester = ExternalCustomer.objects.create(name=requester_id)
					
					if requester:
						request_order.requested_by = requester

				purpose                    = request.POST.get('purpose')
				if purpose:
					request_order.purpose  = purpose
				
				request_order.is_order_completed = True
				if request.user.user_type == 'INVENTORYADMIN': 
					request_order.is_admin_approved = True
				request_order.save()
				
				messages.success(request,"Inventory Request Order Completed successfully!")
				
				return redirect('bleach-inventory:inventory-requestorderitems',request_order.id)

			return redirect('bleach-inventory:inventory-requestorder')


class RequestOrderApproval(IsInventoryAdmin,View):
	def get(self,request,request_order_id):
		request_order       = RequestOrder.objects.get(id=request_order_id)
		request_order_items = RequestOrderItems.objects.select_related('product').filter(request_order=request_order)
		shipment_status = request.GET.get('shipment_status')
		if shipment_status == 'approved':
			request_order.is_admin_approved = True
			request_order.approved_by       = request.user
			request_order.approved_date     = timezone.now().date()
			request_order.save()
			messages.success(request,"Item Request Approved successfully!")
			return redirect('bleach-inventory:inventory-requestorder')

		if shipment_status == 'rejected':
			request_order.is_rejected = True
			request_order.rejected_by  = request.user
			request_order.rejected_date= timezone.now().date()
			request_order.save() 
			messages.success(request,"Item Request Rejected successfully!")
			return redirect('bleach-inventory:inventory-requestorder')

		if request_order_items:
			for request_order_item in request_order_items:
				if request_order_item.product.item_add_type == 'quantity':
					reminign_items = float(request_order_item.item_count)-float(request_order_item.product.total_quantity)
					if reminign_items < 0:
						request_order_item.status = 'Out Of Stock'
						is_all_items_available       = False
					elif reminign_items <= float(request_order_item.product.reserve_count) and reminign_items >= 0:
						request_order_item.status = 'About to Finish'
					else:
						request_order_item.status = 'Available'
				
				elif request_order_item.product.item_add_type == 'unit':
					print(request_order_item.item_count,request_order_item.product.total_quantity,"newmo")
					unitcount = ItemUnit.objects.filter(is_available=True,item=request_order_item.product).count()
					reminign_items = float(request_order_item.item_count)-float(unitcount)
					if	request_order_item.product_unit.is_available == True and reminign_items > 0:
						request_order_item.status = 'Available'
					else:
						request_order_item.status = 'Not Available'
						is_all_items_available       = False

		return render(request,"inventory/ro_admin_approval.html",{"request_order":request_order,"request_order_items":request_order_items})


class RequestOrderItemsPage(IsInventoryAdminUser,View):
	def get(self,request,request_order_id):
		request_order       = RequestOrder.objects.get(id=request_order_id)
		request_order_items = RequestOrderItems.objects.select_related('product').filter(request_order=request_order)
		
		try:
			store               = Store.objects.get(id=request.GET.get('store'))
		except:
			store               = Store.objects.first()

		#item availability check
		is_all_items_available = True
		if request_order_items:
			for request_order_item in request_order_items:
				if request_order_item.product.item_add_type == 'quantity':
					try:
						store_item     = QuantityStoreDetails.objects.get(item_store=store,quantity_item=request_order_item.product)
						reminign_items = float(store_item.quantity)-float(request_order_item.item_count)
					except:
						reminign_items = -1

					if reminign_items < 0:
						request_order_item.status = 'Out Of Stock'
						is_all_items_available       = False
					elif reminign_items <= float(request_order_item.product.reserve_count) and reminign_items >= 0:
						request_order_item.status = 'About to Finish'
					else:
						request_order_item.status = 'Available'
				
				elif request_order_item.product.item_add_type == 'unit':
					unitcount = ItemUnit.objects.filter(is_available=True,item=request_order_item.product,store=store).count()
					if	request_order_item.product_unit and request_order_item.product_unit.is_available == True and float(unitcount) >= float(request_order_item.item_count):
						request_order_item.status = 'Available'
					else:
						request_order_item.status = 'Not Available'
						is_all_items_available       = False
						
				
		return render(request,"inventory/requestorderitems.html",{"request_order":request_order,"request_order_items":request_order_items,"is_all_items_available":is_all_items_available,"store":store})

	def post(self,request,request_order_id):
		request_order       = RequestOrder.objects.get(id=request_order_id)
		request_order_items = RequestOrderItems.objects.select_related('product').filter(request_order=request_order)              

		try:
			store               = Store.objects.get(id=request.POST.get('store'))
		except:
			store               = Store.objects.first()

		action              = request.POST.get('action')

		if action == 'stock_out':
			#item availability check
			is_all_items_available = True
			if request_order_items:
				for request_order_item in request_order_items:
					if request_order_item.product.item_add_type == 'quantity':
						
						try:
							store_item     = QuantityStoreDetails.objects.get(item_store=store,quantity_item=request_order_item.product)
						except:
							store_item     = QuantityStoreDetails.objects.create(
									item_store = store,
									quantity_item = request_order_item.product,
									quantity = 0
									)
						
						if float(store_item.quantity) <= 0 or float(store_item.quantity) < float(request_order_item.item_count):
							request_order_item.status    = 'Out Of Stock'
							is_all_items_available       = False

							messages.error(request,"Some Items are not Available")
							return redirect('bleach-inventory:inventory-requestorderitems',request_order_id)
				
					elif request_order_item.product.item_add_type == 'unit':
						unitcount = ItemUnit.objects.filter(is_available=True,store=store,item=request_order_item.product).count()
						if not (request_order_item.product_unit.is_available == True and float(unitcount) >= float(request_order_item.item_count)):
							request_order_item.status    = 'Not Available'
							is_all_items_available       = False
						
							messages.error(request,"Some Items are not Available")
							return redirect('bleach-inventory:inventory-requestorderitems',request_order_id)
			
			#save delivery details
			if is_all_items_available == True:

				if request_order_items:
					for request_order_item in request_order_items:

						try:
							store_item     = QuantityStoreDetails.objects.get(item_store=store,quantity_item=request_order_item.product)
						except:
							store_item     = QuantityStoreDetails.objects.create(
									item_store = store,
									quantity_item = request_order_item.product,
									quantity = 0
									)
						
						if request_order_item.product.item_add_type == 'quantity':
							print(store_item.quantity,"storqty")
							if float(store_item.quantity) >= float(request_order_item.item_count):
								request_order_item.product.total_quantity = round(float(request_order_item.product.total_quantity)-float(request_order_item.item_count),2)
								store_item.quantity                       = round(float(store_item.quantity)-float(request_order_item.item_count),2)
							
								request_order_item.product.save()
								request_order_item.is_received             = True
								request_order_item.save()
								store_item.save()
																
								ItemHistory.objects.create(
								item = request_order_item.product,
								item_action = 'ITEM REQUEST',
								quantity_location=store,
								item_remark = request_order_item.request_order.request_order_id,
								quantity = request_order_item.item_count,
								external_user = request_order_item.request_order.requested_by.name
								)
						else:
							request_order_item.product.save()
							request_order_item.is_received             = True
							request_order_item.save()

							if request_order_item.product_unit:
								request_order_item.product_unit.status = 'working'
								request_order_item.product_unit.is_available=False
								request_order_item.product_unit.save()

				request_order.is_received  = True
				request_order.received_by  = request.user
				request_order.received_date= timezone.now().date()
				request_order.save()
				messages.success(request,"Items Delivered successfully!")

		return redirect('bleach-inventory:inventory-requestorder')


class InventoryRequestOrderPage(View):
	def get(self,request,request_order_id):
		request_order = RequestOrder.objects.prefetch_related(Prefetch('items_request_order',queryset=RequestOrderItems.objects.all(),to_attr='request_order_items')).get(id=request_order_id)
		return render(request,'inventory/requestorderpage.html',{"request_order":request_order})

class InventoryItemsListExport(View):
	def get(self,request):
		# Sheet header, first row
		row_num = 0

		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="Inventory_Items.xls"'

		wb = xlwt.Workbook(encoding='utf-8')

		#online
		ws = wb.add_sheet('ITEMS',cell_overwrite_ok = True)
	
		columns = ['Item Type','Item Name','Item Code','Supplier','Item Price','Category','Segment','Line','Available Qty','Reserve Qty']
		
		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		inventory_items = InventoryItem.objects.all().annotate(unit_count=Sum(Case(When(unit_item__is_available=True,then=1),default=0,output_field=IntegerField()))).values_list('item_type','name','item_code','id','id','item_category__name','item_segment__name','item_line__name','total_quantity','reserve_count','unit_count')


		rows = []

		for item in inventory_items:
			
			item_list = list(item)
			print(item_list[9],"uco")

			try:
				supplieritem = SupplierItems.objects.filter(item__id=int(item[3])).first()
				supplier_name = supplieritem.supplier.supplier_name
				item_price = supplieritem.item_price
				print(supplieritem,"splr")
			except:
				supplieritem = None
				supplier_name = '-'
				item_price = '-'

			if item_list[10] > 0 :
				item_list[8] = item_list[10]
			
			item_list[8] = math.ceil(float(item_list[8]))
			item_list[9] = math.ceil(float(item_list[9]))
			item_list[3] = supplier_name
			item_list[4] = item_price
			item_list[10] = '' #emptying unit count value row

			item = tuple(item_list)
			rows.append(item)

		rows = [[x.strftime("%d-%m-%Y") if isinstance(x, datetime) else x for x in row] for row in rows ]
	
		for row in rows:
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)

		wb.save(response)

		return response