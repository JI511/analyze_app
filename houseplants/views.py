import random
import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import now

from .models import HouseplantItem, PlantInstance, Plant, Watering
from .forms import AddPlantForm


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
    # TODO Notes
    # Dates in the past should gather any Watering objects from that day and display them
    print(request.POST)
    current_date = datetime.date.today()
    if request.method == 'POST':
        if 'calendar_select' in request.POST:
            temp_date = request.POST.get('calendar_select')
            current_date = datetime.datetime.strptime(temp_date, '%m-%d-%Y').date()
        elif 'jump_to_date' in request.POST:
            temp_date = request.POST.get('jump_to_date')
            current_date = datetime.datetime.strptime(temp_date, '%Y-%m-%d').date()
        elif 'plant_water_update' in request.POST:
            # iterate over user's plants and match with which IDs were in POST
            for plant in PlantInstance.objects.filter(owner=request.user):
                if str(plant.id) in request.POST:
                    plant.water_plant(now())

    current_ord = current_date.toordinal()
    weekly_dates = []
    for i in range(current_ord - 3, current_ord + 4):
        td = datetime.date.fromordinal(i)
        if i == current_ord:
            # create tuple of: full datetime.date object, day of week, day of month, is middle date
            weekly_dates.append((td, td.strftime('%A'), td.strftime('%B'), True))
        else:
            weekly_dates.append((td, td.strftime('%A'), td.strftime('%B'), False))

    user_plant_instances = []
    watering = []
    if current_ord < datetime.datetime.today().toordinal():
        watering = Watering.objects.filter(watering_date=current_date)
    else:
        for pi in PlantInstance.objects.filter(owner=request.user):
            if pi.due_for_watering(active_date=current_date):
                user_plant_instances.append(pi)

    template_dict = {
        'weekly_dates': weekly_dates,
        'user_plant_instances': user_plant_instances,
        'watering': watering,
    }

    return render(request, 'houseplants/watering_schedule.html', template_dict)


@login_required(login_url='/accounts/login/')
def my_plants(request):
    """

    :param request:
    :return:
    """
    user_plants = PlantInstance.objects.filter(owner=request.user)
    template_dict = {
        'user_plants': user_plants
    }
    return render(request, 'houseplants/my_plants.html', template_dict)


@login_required(login_url='/accounts/login/')
def add_plants(request):
    status_message = 'Add a new plant!'
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = AddPlantForm(request.POST)

        if form.is_valid() and request.user.is_authenticated:
            plant_instance = PlantInstance(
                plant=Plant.objects.get(plant_name=form.cleaned_data['plant_name']),
                water_rate=form.cleaned_data['water_rate'],
                date_added=datetime.datetime.today(),
                owner=User.objects.get(username=request.user.username)
            )
            plant_instance.save()
            # Create an initial watering instance from the created plant instance
            watering = Watering(plant_instance=PlantInstance.objects.get(id=plant_instance.id),
                                watering_date=form.cleaned_data['watering'])
            watering.save()

            status_message = 'Plant added successfully: %s' % plant_instance.plant.plant_name
    else:
        form = AddPlantForm(initial={'water_rate': 7})
    template_dict = {
        'form': form,
        'status_message': status_message,
        'plants': Plant.objects.all(),
    }

    return render(request, 'houseplants/add_plants.html', template_dict)


@login_required(login_url='/accounts/login/')
def remove_plants(request):
    """

    :param request:
    :return:
    """
    # TODO add logic for removal
    user_plants = PlantInstance.objects.filter(owner=request.user)
    template_dict = {
        'user_plants': user_plants
    }
    return render(request, 'houseplants/remove_plants.html', template_dict)
