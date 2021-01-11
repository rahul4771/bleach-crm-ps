from django.shortcuts import render,redirect
from django.views import View

# Create your views here.
def investigation(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "followup":
            return redirect('quality-control:follow-up')
        if action == "discount":
            return redirect('quality-control:cash-back')
        # if action == "gift":

        # if action == "internal":

    return render(request,"quality-control/investigation.html")

class Followup(View):
    def get(self,request):
        return render(request,"quality-control/follow-up.html")

class Cashback(View):
    def get(self,request):
        return render(request,"quality-control/cashback.html")