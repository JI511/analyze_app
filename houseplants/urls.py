from django.urls import path
from . import views

app_name = 'houseplants'

urlpatterns = [
    path('', views.index, name='index'),
    path('reddit_images/', views.reddit_images, name='reddit_images'),
    path('watering_schedule/', views.watering_schedule, name='watering_schedule'),
    path('add_plants/', views.add_plants, name='add_plants'),
    path('my_plants/', views.my_plants, name='my_plants'),
    path('remove_plants/', views.remove_plants, name='remove_plants'),
    path('propagation_board/', views.propagation_board, name='propagation_board'),
    path('propagation_board/<int:propagation_instance_id>', views.propagation_detail, name='propagation_detail'),
]
