from django.db import models


class Owner(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Car(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(default=2020)

    owner = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        related_name='car',
    )