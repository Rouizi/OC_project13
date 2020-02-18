from django.conf.urls import url
from booking import views


urlpatterns = [
    url(r'^create_deal/$', views.create_deal, name='create_deal'),
]