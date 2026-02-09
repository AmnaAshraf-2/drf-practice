from django.db import models
from .manager import CarManager

# Create your models here.
class Car(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(default=2020)

    objects = models.Manager()
    car = CarManager()