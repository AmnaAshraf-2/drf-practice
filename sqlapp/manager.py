from django.db import models


class CarManager(models.Manager):
    def by_make(self, make_name):
        return self.filter(make__iexact=make_name)

    def older_than(self, year):
        return self.filter(year__lt=year)
