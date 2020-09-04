from django.shortcuts import render
from .models import HouseplantItem, PlantInstance
from django.contrib.auth.decorators import login_required
import random
import datetime

# Create your views here.


sorting_items = [
    'Aspect Ratio (High to Low)',
    'Aspect Ratio (Low to High)',
]


def index(request):
    return render(request, 'houseplants/index.html', {})


def reddit_images(request):
    image_row_display_count = 5
    page_image_count_limit = 20
    current_page = 1
    row_list = list()
    page_list = dict()
    sub_image_list = list()
    selected_sort = 'Aspect Ratio (High to Low)'
    houseplant_objs = sorted(HouseplantItem.objects.all(), key=lambda obj: obj.get_aspect_ratio(), reverse=True)

    if request.method == 'POST':
        # determines how many images are displayed per page
        page_image_count_limit = int(request.POST.get('display_count_text'))
        print(request.POST)
        # change sorting method if needed
        if 'sorting_method' in request.POST:
            selected_sort = request.POST.get('sorting_method')
            if selected_sort == sorting_items[0]:
                houseplant_objs = sorted(HouseplantItem.objects.all(), key=lambda obj: obj.get_aspect_ratio(),
                                         reverse=True)
                print('High to Low')
            elif selected_sort == sorting_items[1]:
                houseplant_objs = sorted(HouseplantItem.objects.all(), key=lambda obj: obj.get_aspect_ratio())
                print('Low to High')
        # Update page number
        if 'page_select' in request.POST:
            current_page = int(request.POST.get('page_select'))

    # create rows
    for i, item in enumerate(houseplant_objs, start=1):
        sub_image_list.append(item)
        if i % image_row_display_count == 0:
            # reorder the sub list so everything doesnt look ordered as much
            random.shuffle(sub_image_list)
            row_list.append(sub_image_list)
            sub_image_list = list()

    # create row from remaining items
    if len(sub_image_list) != 0:
        random.shuffle(sub_image_list)
        row_list.append(sub_image_list)

    # create pages
    sub_page_list = list()
    for i, item in enumerate(row_list, start=1):
        sub_page_list.append(item)
        if i % (page_image_count_limit / image_row_display_count) == 0:
            # add new dictionary item at +1 page number
            page_list[len(page_list) + 1] = sub_page_list
            sub_page_list = list()

    # create page from remaining rows
    if len(sub_page_list) != 0:
        page_list[len(page_list) + 1] = sub_page_list

    template_dict = {
        'houseplant_images': page_list,
        'sorting_items': sorting_items,
        'selected_sort': selected_sort,
        'current_page': current_page,
        'page_image_limit': page_image_count_limit,
    }

    return render(request, 'houseplants/reddit_images.html', template_dict)


@login_required(login_url='/accounts/login/')
def watering_schedule(request):
    weekly_dates = []
    # we want a weeks worth of days centered on the current day
    current = datetime.datetime.today() - datetime.timedelta(days=4)
    for i in range(1, 8):
        current += datetime.timedelta(days=1)
        # add tuple of format (Day of week, Month_Name Day)
        weekly_dates.append((current.strftime('%A'), current.strftime('%B %d')))

    user_plants = [''] if not request.user else PlantInstance.objects.filter(owner=request.user)
    template_dict = {
        'early_dates': weekly_dates[0:3],
        'current_date': [weekly_dates[3]],
        'later_dates': weekly_dates[4:],
        'user_plants': user_plants,
    }
    return render(request, 'houseplants/watering_schedule.html', template_dict)
