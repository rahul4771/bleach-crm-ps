from django.shortcuts import render,redirect
from django.views import View
from bleach_crm_ps.permissions import IsInventoryAdmin,IsInventoryAdminUser
from inventory.models import Category,Segment,Line,Attribute
from django.contrib import messages
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q,Sum,When,Case,Value,F,Func,Count,Avg,Max,ExpressionWrapper,DateTimeField,DurationField,BigIntegerField,BooleanField,IntegerField,FloatField,CharField,Prefetch
# Create your views here.

class InventoryHome(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/home.html',{})

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
        category_name   = request.POST.get('category_name')
        category_status = request.POST.get('category_status')

        category_latest = Category.objects.all().last()
        if category_latest:
            code_number  =  int(re.findall(r'(\d+)', category_latest.category_code)[0]) + 1
            category_code = 'CAT'+str(code_number)
        else:
            category_code = 'CAT9001'

        Category.objects.create(name=category_name,category_code=category_code,status=category_status)

        messages.success(request,"Category Added Successfully !")
        return redirect('inventory:inventory-category')

# Attribute.
class InventoryAttribute(IsInventoryAdmin,View):
    def get(self,request):
        search = request.GET.get('search')

        if search:
            attributes = Attribute.objects.filter(name__icontains=search).annotate(value_count=Count('value_attribute'))
        else:
            attributes = Attribute.objects.all().annotate(value_count=Count('value_attribute'))

        return render(request,'inventory/attribute.html',{"attributes":attributes,"search_query":search})

    def post(self,request):
        return redirect('inventory:inventory-attribute')
# value.
class InventoryValue(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/value.html',{})

# bundle.
class InventoryBundle(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/bundle.html',{})

class InventoryItem(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/item.html',{})

class InventorySupplier(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/supplier.html',{})

class InventoryStore(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/store.html',{})

class InventoryInv(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/inventory.html',{})

class InventoryOrder(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/order.html',{})

class InventoryUsers(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/users.html',{})

class InventoryCheckout(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/checkout.html',{})

class InventoryCreateCheckout(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/createCheckout.html',{})

class InventoryPurchaseOrder(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/purchaseOrder.html',{})
class InventoryPurchaseOrderPage(View):
    def get(self,request):
        return render(request,'inventory/purchaseorderpage.html',{})        
class InventoryCreatePurchaseOrder(View):
    def get(self,request):
        return render(request,'inventory/createpo.html',{})

class InventoryEditPurchaseOrder(IsInventoryAdmin,View):
    def get(self,request):
        return render(request,'inventory/editpo.html',{})

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
        return render(request,'inventory/services.html',{})

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

            Segment.objects.create(category=category,name=name,status=status)
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
            segment_id = request.POST.get('segment_id')
            Segment.objects.get(id=int(segment_id)).delete()
            messages.success(request,"Segment Deleted Successfully !")
            
        return redirect('inventory:inventory-segment', category_id)
