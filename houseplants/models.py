import os
import uuid
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
        if active_date is None:
            active_date = timezone.localtime(now(), timezone.get_current_timezone()).toordinal()
        else:
            active_date = active_date.toordinal()
        is_due = False
        last_watered = self.get_last_watered()
        if last_watered is None or active_date > last_watered.toordinal() + self.water_rate:
            is_due = True
        return is_due

    def get_last_watered(self):
        """
        Gets the most recent watering date for the plant instance.

        :rtype Datetime.date object
        """
        watering = Watering.objects.filter(plant_instance=self)
        last_watered_date = None
        if watering:
            last_watered_date = datetime.date.fromordinal(max(
                [water.watering_date.astimezone(timezone.get_current_timezone()).toordinal() for water in watering]
            ))
        return last_watered_date

    def water_plant(self, date_watered):
        """
        Creates a watering for the plant instance on the specified day.
        """
        Watering.objects.create(plant_instance=self, watering_date=date_watered)


class Plant(models.Model):
    plant_name = models.CharField(max_length=50)

    def __str__(self):
        return self.plant_name


class Watering(models.Model):
    watering_id = models.AutoField(primary_key=True)

    plant_instance = models.ForeignKey(PlantInstance, on_delete=models.SET_NULL, null=True)
    watering_date = models.DateTimeField(default=now)

    def __str__(self):
        return '%s: %s on %s' % (self.plant_instance.owner.username, self.plant_instance.plant.plant_name,
                                 self.watering_date.strftime('%A %B %d, %Y'))

    def get_plant_name(self):
        return self.plant_instance.plant.plant_name
