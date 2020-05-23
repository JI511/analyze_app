from django.shortcuts import render
from .models import HouseplantItem

# Create your views here.


def index(request):
    return render(request, 'houseplants/index.html', {})


def reddit_images(request):
    template_dict = {
        'houseplant_images': HouseplantItem.objects.all()
    }
    return render(request, 'houseplants/reddit_images.html', template_dict)
