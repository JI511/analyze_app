from django.db import models


class ScatterKeysXAxis(models.Model):
    name = models.CharField(max_length=35, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['name']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name


class ScatterKeysYAxis(models.Model):
    name = models.CharField(max_length=35, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['name']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name


class BasketballTeamNames(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    # Metadata
    class Meta:
        ordering = ['name']

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name
