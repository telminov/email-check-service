from django.conf.urls import url

from core import views

urlpatterns = [
    url(r'^check_email/$', views.CheckEmail.as_view(), name='check_email'),
]
