from django.conf.urls import include, url
from customer import views 

#all users urls

urlpatterns = [

		url(r'^quatation/(?P<evaluation_id>[-\w]+)$',views.Quatation.as_view(),name='quatation'),

	]