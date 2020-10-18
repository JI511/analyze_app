from django.urls import path
from . import views

app_name = 'houseplants'

urlpatterns = [
    path('', views.index, name='index'),
    path('reddit_images/', views.reddit_images, name='reddit_images'),
    path('watering_schedule/', views.watering_schedule, name='watering_schedule'),
    path('add_plants/', views.add_plants, name='add_plants'),
]
