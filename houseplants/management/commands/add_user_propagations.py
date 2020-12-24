import os
import pytz
from django.utils import timezone
from django.utils.timezone import now
from django.utils.timezone import activate
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from houseplants.models import Plant, PropagationInstance


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--count', type=int)
        parser.add_argument('--username', help='The name of the user.')

    def handle(self, *args, **options):
        activate(pytz.timezone('America/Chicago'))
        current_date = timezone.localtime(now(), timezone.get_current_timezone())
        for i in range(options['count']):
            PropagationInstance(
                plant=Plant.objects.get(plant_name=Plant.objects.order_by("?").first()),
                listed_date=current_date,
                image=os.path.join(os.getcwd(), 'houseplants/static/houseplants.jpg'),
                type="Cutting" if i % 2 == 0 else "Rooted Cutting",
                description="This was an auto generated cutting.",
                amount=i % 5,
                owner=User.objects.get(username=options['username'])
            ).save()
        for propagation_instance in PropagationInstance.objects.filter(
                owner=User.objects.get(username=options['username'])):
            print("PropagationInstance '%s' created" % (propagation_instance,))
