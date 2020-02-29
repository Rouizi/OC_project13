from django.conf.urls import url
from booking import views


urlpatterns = [
    url(r'^create_deal/(?P<id>[0-9]+)/$', views.create_deal, name='create_deal'),
    url(r'^user_cars/$', views.user_cars, name='user_cars'),
    url(r'^delete_deal/(?P<id_deal>[0-9]+)$', views.delete_deal, name='delete_deal'),
    url(r'^confirmation_delete/(?P<id_deal>[0-9]+)/$', 
        views.confirmation_delete, name='confirmation_delete'),
    url(r'^update_deal/(?P<id_deal>[0-9]+)/$', views.update_deal, name='update_deal'),
    url(r'^detail_deal/$', views.detail_deal, name='detail_deal'),
    url(r'^reservations/(?P<id_deal>[0-9]+)/$', views.reservations, name='reservations'),
]