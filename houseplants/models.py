import os
from django.db import models

media_dir = os.path.dirname(os.path.abspath(__file__))


# Create your models here.
class HouseplantItem(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=200)

    def get_media_url(self):
        return os.path.join('Houseplant_Images', str(self.image_name) + '.jpg')

    def __str__(self):
        return str(self.image_name)
