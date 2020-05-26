# Populates the db with names of pictures in a given directory

from django.core.management.base import BaseCommand
from houseplants.models import HouseplantItem
import os


class Command(BaseCommand):
    """
    Base class for creating command.
    """
    def _create_items(self):
        """
        Creates houseplant model objects in a given directory.
        :return:
        """
        directory = r'C:\Users\ingwe\Desktop\Programs\analyze_django\mysite\analyze_app\media\Houseplant_Images'
        for plant_image in os.listdir(directory):
            image_name = os.path.splitext(plant_image)[0]
            model_item = HouseplantItem(image_name=image_name)
            model_item.save()
            print("Item named '%s' has been added." % image_name)

    def handle(self, *args, **options):
        """
        Calls what is relevant
        """
        self._create_items()
