import datetime

from django import forms
from .models import Plant
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class AddPlantForm(forms.Form):
    plant_name = forms.CharField(help_text="Enter the name of the plant.")
    water_rate = forms.IntegerField(help_text="How often does the plant need watering? (days)")
    last_watered = forms.DateField(help_text="What day did you last water this plant?")

    def clean_plant_name(self):
        name = self.cleaned_data['plant_name']
        if name not in [plant_obj_names.plant_name for plant_obj_names in Plant.objects.all()]:
            raise ValidationError(_('Invalid Plant - plant not in known object list!'))
        return name

    def clean_water_rate(self):
        rate = self.cleaned_data['water_rate']
        try:
            rate = round(rate)
            if rate < 0:
                raise ValueError
        except ValueError:
            raise ValidationError(_('Invalid watering rate - Please enter a valid number larger than 0'))

    def clean_last_watered(self):
        data = self.cleaned_data['last_watered']

        # Check if a date is not in the past.
        if data < (datetime.date.today() - datetime.timedelta(days=100)):
            raise ValidationError(_('Invalid date - too far in the past!'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today():
            raise ValidationError(_('Invalid date - you can\'t water the future!'))

        # Remember to always return the cleaned data.
        return data
