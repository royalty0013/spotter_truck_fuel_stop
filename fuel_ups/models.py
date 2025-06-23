from django.contrib.gis.db import models


class FuelStop(models.Model):
    opis_truckstop = models.IntegerField()
    truckstop_name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    rack_id = models.IntegerField()
    retail_price = models.DecimalField(max_digits=10, decimal_places=3)
    point = models.PointField(geography=True)

    def __str__(self):
        return self.truckstop_name
