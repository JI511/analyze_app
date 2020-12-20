import random
import datetime
import pytz
from django.utils import timezone
from django.utils.timezone import now
from django.utils.timezone import activate
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from houseplants.models import Plant, PlantInstance


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int)
        parser.add_argument('--username', help='The name of the user.')

    def handle(self, *args, **options):
        activate(pytz.timezone('America/Chicago'))
        current_date = timezone.localtime(now(), timezone.get_current_timezone())
        for i in range(options['count']):
            PlantInstance(
                plant=Plant.objects.get(plant_name=Plant.objects.order_by("?").first()),
                water_rate=random.randrange(1, 5),
                date_added=current_date,
                owner=User.objects.get(username=options['username'])
            ).save()
        for plant_instance in PlantInstance.objects.filter(owner=User.objects.get(username=options['username'])):
            print("PlantInstance '%s' created with rate %s" % (plant_instance, plant_instance.water_rate))
