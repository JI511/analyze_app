import os
import uuid
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

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
    last_watered = models.DateField(default=now)
    # date the instance was created
    date_added = models.DateField(default=now)
    # owner of the plant instance
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '%s %s' % (self.plant.plant_name, self.owner)

    def due_for_watering(self, active_date=None):
        """
        Indicates if the last water date plus water rate has reached or passed the current day.

        :param datetime.date active_date: The date to compare against.
        """
        # TODO, while there isnt a lot of benefit to looking at watering in the past, the future needs to have the date change
        # TODO, The past could still show when something was last watered with a checkmark filled in?
        if active_date is None:
            active_date = datetime.date.today()
        is_due = False
        if active_date.toordinal() > self.last_watered.toordinal() + self.water_rate:
            is_due = True
        return is_due


class Plant(models.Model):
    plant_name = models.CharField(max_length=50)

    def __str__(self):
        return self.plant_name


class Watering(models.Model):
    watering_id = models.AutoField(primary_key=True)
    plant_instance = models.ForeignKey(PlantInstance, on_delete=models.SET_NULL, null=True)
    watering_date = models.DateField(default=now)
