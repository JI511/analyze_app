from django.urls import path
from . import views

app_name = 'houseplants'
urlpatterns = [
    path('', views.index, name='index'),
]
