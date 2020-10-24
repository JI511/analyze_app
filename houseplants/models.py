import os
import uuid
from django.db import models
from django.contrib.auth.models import User

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


# When designing models it makes sense to have separate models for every "object". Plants,
# plant instances.

# There can be many instances of the same plant (monstera), but each plant type is unique
class PlantInstance(models.Model):
    """
    Model representing a specific plant instance (that a user owns).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this plant across all users')
    # Foreign key to plant model object
    plant = models.ForeignKey('Plant', on_delete=models.SET_NULL, null=True)
    # number of days between watering
    water_rate = models.IntegerField(default=7, help_text='Rate of watering in days')
    # The most recent water date
    last_watered = models.DateField(null=True, blank=True)
    # date the instance was created
    date_added = models.DateField(null=True, blank=True)
    # owner of the plant instance
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return '%s %s' % (self.plant.plant_name, self.owner)


class Plant(models.Model):
    plant_name = models.CharField(max_length=50)

    def __str__(self):
        return self.plant_name
