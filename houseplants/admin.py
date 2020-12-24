from django.contrib import admin
from .models import HouseplantItem, Plant, PlantInstance, Watering, PropagationInstance

# Register your models here.
admin.site.register(HouseplantItem)
admin.site.register(Plant)
admin.site.register(PlantInstance)
admin.site.register(Watering)
admin.site.register(PropagationInstance)
