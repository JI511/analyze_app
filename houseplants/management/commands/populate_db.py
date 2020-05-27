# Populates the db with names of pictures in a given directory

from django.core.management.base import BaseCommand
from houseplants.models import HouseplantItem
import os
from PIL import Image
import numpy as np


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

    def rename_all_in_dir(self, dir_path):
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if not os.path.isdir(file_path):
                if len(file) > 50:
                    extension = os.path.splitext(file_path)[1]
                    file_rename = os.path.join(dir_path, file[:50] + extension)
                    os.rename(file_path, file_rename)
                    print('%s renamed to %s' % (file_path, file_rename))

    def _create_items(self, directory):
        """
        Creates houseplant model objects in a given directory.
        :return:
        """
        if os.path.exists(directory) and os.path.isdir(directory):
            self.rename_all_in_dir(directory)
            for plant_image in os.listdir(directory):
                img = np.array(Image.open(os.path.join(directory, plant_image)))
                image_name = os.path.splitext(plant_image)[0]
                model_item = HouseplantItem(image_name=image_name,
                                            height=img.shape[0],
                                            width=img.shape[1])
                model_item.save()
                # Shape is H x W x D, but the convention is W x H
                print("'%s' has been added. Dimensions: %s" % (image_name, model_item.get_aspect_ratio()))

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
