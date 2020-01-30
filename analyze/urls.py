from django.urls import path
from . import views

app_name = 'analyze'
urlpatterns = [
    path('', views.index, name='index'),
    path('plot/', views.plot, name='plot'),
    path('download_plot_png/', views.download_plot_png, name='download_plot_png')
]
