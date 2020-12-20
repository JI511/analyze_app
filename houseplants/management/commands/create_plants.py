from django.core.management.base import BaseCommand
from houseplants.models import Plant


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Plant.objects.create(plant_name="Monstera Deliciosa").save()
        Plant.objects.create(plant_name="Neon Pothos").save()
        Plant.objects.create(plant_name="Silver Satin Pothos").save()
        Plant.objects.create(plant_name="Pilea Pepperomiodes").save()
        Plant.objects.create(plant_name="Sansivera").save()
        Plant.objects.create(plant_name="Aloe Vera").save()
        Plant.objects.create(plant_name="Prickly Pear").save()
        Plant.objects.create(plant_name="Golden Pothos").save()
        Plant.objects.create(plant_name="Chinese Evergreen").save()
        Plant.objects.create(plant_name="Calathea").save()
        for plant in Plant.objects.all():
            print("Plant '%s' created" % plant)
