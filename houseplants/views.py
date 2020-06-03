from django.shortcuts import render
from .models import HouseplantItem
import random

# Create your views here.


sorting_items = [
    'Aspect Ratio (High to Low)',
    'Aspect Ratio (Low to High)',
]


def index(request):
    return render(request, 'houseplants/index.html', {})


def reddit_images(request):
    image_row_display_count = 5
    page_image_limit = 20
    obj_list = list()
    page_list = list()
    sub_image_list = list()
    selected_sort = 'Aspect Ratio (High to Low)'
    houseplant_objs = sorted(HouseplantItem.objects.all(), key=lambda obj: obj.get_aspect_ratio(), reverse=True)

    if request.method == 'POST':
        print(request.POST)
        selected_sort = request.POST.get('sorting_method')
        if selected_sort == sorting_items[0]:
            houseplant_objs = sorted(HouseplantItem.objects.all(), key=lambda obj: obj.get_aspect_ratio(), reverse=True)
            print('High to Low')
        elif selected_sort == sorting_items[1]:
            houseplant_objs = sorted(HouseplantItem.objects.all(), key=lambda obj: obj.get_aspect_ratio())
            print('Low to High')

    # currently sorting by aspect ratio, maybe also some function of image area?
    for i, item in enumerate(houseplant_objs, start=1):
        sub_image_list.append(item)
        if i % image_row_display_count == 0:
            # reorder the sub list so everything doesnt look ordered as much
            random.shuffle(sub_image_list)
            obj_list.append(sub_image_list)
            sub_image_list = list()
    sub_page_list = list()
    for i, item in enumerate(obj_list, start=1):
        sub_page_list.append(item)
        if i % (page_image_limit / image_row_display_count) == 0:
            page_list.append(sub_page_list)
            sub_page_list = list()

    for a in page_list:
        print(a)

    if len(sub_image_list) != 0:
        obj_list.append(sub_image_list)

    template_dict = {
        'houseplant_images': page_list[0],
        'sorting_items': sorting_items,
        'selected_sort': selected_sort,
    }
    return render(request, 'houseplants/reddit_images.html', template_dict)
