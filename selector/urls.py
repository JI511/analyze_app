from django.urls import path
from . import views

app_name = 'selector'
urlpatterns = [
    path('', views.index, name='index'),
    path('redirect_to_app/', views.redirect_to_app, name='redirect_to_app'),
]