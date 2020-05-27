# Populates the db with names of pictures in a given directory

from django.core.management.base import BaseCommand
from houseplants.models import HouseplantItem
import os


class Command(BaseCommand):
    """
    Base class for creating command.
    """
    def add_arguments(self, parser):
        parser.add_argument('image_dir', type=str)
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Delete model objects before creating/adding',
        )

    def _create_items(self, directory):
        """
        Creates houseplant model objects in a given directory.
        :return:
        """
        if os.path.exists(directory) and os.path.isdir(directory):
            for plant_image in os.listdir(directory):
                image_name = os.path.splitext(plant_image)[0]
                model_item = HouseplantItem(image_name=image_name)
                model_item.save()
                print("Item named '%s' has been added." % image_name)

    def _remove_items(self):
        """
        Removes all model objects.
        """
        for model_item in HouseplantItem.objects.all():
            model_item.delete()
            print("Removal of %s complete." % model_item)

    def handle(self, *args, **options):
        """
        Calls what is relevant
        """
        self._remove_items()
        self._create_items(options['image_dir'])
