"""bleach_crm_ps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf.urls.static import static  
from django.conf import settings
from user.views import Signin,logout,adddata,testcalendar

urlpatterns = [
    
    url(r'^admin/', admin.site.urls),
    url(r'^$',Signin.as_view(),name='login'),
    url(r'^logout/$',logout.as_view(),name='logout'),
    url(r'^add_data/$',adddata,name='add_data'),
    url(r'^test_data/$',testcalendar,name='test_data'),

    url(r'^bleach_admin/',include('bleachadmin.urls',namespace='bleach_admin')),
    url(r'^agent/',include('agent.urls',namespace='agent')),
    url(r'^evaluator/',include('evaluator.urls',namespace='evaluator')),
    url(r'^stl/',include('senior_team_leader.urls',namespace='stl')),
    url(r'^tl/',include('team_leader.urls',namespace='tl')),
    url(r'^accountant/',include('accountant.urls',namespace='accountant')),
    url(r'^customer/',include('customer.urls',namespace='customer')),
    url(r'^order-data/',include('order.urls',namespace='order_data')),

    url(r'^api/',include('Api.urls',namespace='api')),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
