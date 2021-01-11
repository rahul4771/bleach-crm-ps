from django.shortcuts import render

# Create your views here.

def investigation(request):
    return render(request,"quality-control/investigation.html")
