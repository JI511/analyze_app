from django.shortcuts import render

# Create your views here.


def index(request):
    temp_dict = {
        'app_names': ['analyze', 'houseplants']
    }
    return render(request, 'selector/index.html', temp_dict)
