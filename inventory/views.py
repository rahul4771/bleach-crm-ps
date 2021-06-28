from django.shortcuts import render
from django.views import View

# Create your views here.
class InventoryHome(View):
    def get(self,request):
        return render(request,'inventory/home.html',{})

# Category.
class InventoryCategory(View):
    def get(self,request):
        return render(request,'inventory/category.html',{})
# Attribute.
class InventoryAttribute(View):
    def get(self,request):
        return render(request,'inventory/attribute.html',{})
# value.
class InventoryValue(View):
    def get(self,request):
        return render(request,'inventory/value.html',{})
# bundle.
class InventoryBundle(View):
    def get(self,request):
        return render(request,'inventory/bundle.html',{})
class InventoryItme(View):
    def get(self,request):
        return render(request,'inventory/item.html',{})