import os
from django.db import models


# Create your models here.
class Graph(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=200)

    def get_media_url(self):
        return os.path.join('Media', 'Houseplant_Images', str(self.image_name))
