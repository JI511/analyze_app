from django.contrib import admin
from .models import ScatterXKey, ScatterYKey, BasketballTeamName, TrendLineChoice, GridChoice, Graph

# Register your models here.
admin.site.register(ScatterXKey)
admin.site.register(ScatterYKey)
admin.site.register(BasketballTeamName)
admin.site.register(TrendLineChoice)
admin.site.register(GridChoice)
admin.site.register(Graph)
