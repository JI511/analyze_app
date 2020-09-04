from django.contrib import admin
from .models import HouseplantItem, Plant, PlantInstance

# Register your models here.
admin.site.register(HouseplantItem)
admin.site.register(Plant)
admin.site.register(PlantInstance)
