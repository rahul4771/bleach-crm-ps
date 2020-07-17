from django.conf.urls import include, url
from order import views 

urlpatterns = [

	url(r'^quotation_data/$',views.quotation_data,name='quotation_data'),

	
]