from django.shortcuts import render
from .models import HouseplantItem

# Create your views here.


def index(request):
    return render(request, 'houseplants/index.html', {})


def reddit_images(request):
    image_display_count = 3
    obj_list = list()
    sub_list = list()
    for i, item in enumerate(HouseplantItem.objects.all(), start=1):
        sub_list.append(item)
        if i % image_display_count == 0:
            obj_list.append(sub_list)
            sub_list = list()

    if len(sub_list) != 0:
        obj_list.append(sub_list)

    print(obj_list)
    template_dict = {
        'houseplant_images': obj_list
    }
    return render(request, 'houseplants/reddit_images.html', template_dict)
