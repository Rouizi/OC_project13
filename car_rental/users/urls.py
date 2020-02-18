from django.conf.urls import url
from users import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^log_in/$', views.log_in, name='log_in'),
    url(r'^log_out/$', views.log_out, name="log_out"),
    url(r'^profile/(?P<username>.+)$', views.profile, name='profile'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),
]