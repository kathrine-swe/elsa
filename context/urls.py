from django.conf.urls import url
from . import views



app_name='context'
urlpatterns = [
    url(r'^$', views.context, name='context'),

]
