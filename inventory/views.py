from django.shortcuts import render
from django.views import View

# Create your views here.
class InventoryHome(View):
    def get(self,request):
        return render(request,'inventory/home.html',{})