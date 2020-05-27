import os
from django.db import models

media_dir = os.path.dirname(os.path.abspath(__file__))


# Create your models here.
class HouseplantItem(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=200)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    def get_media_url(self):
        return '/media/Houseplant_Images/' + str(self.image_name) + '.jpg'

    def get_aspect_ratio(self):
        return float(self.width / self.height)

    def __str__(self):
        return str(self.image_name)
