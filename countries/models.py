from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capital = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    population = models.IntegerField()
    currency_code = models.CharField(max_length=10, blank=True, null=True)
    exchange_rate = models.FloatField(blank=True, null=True)
    estimated_gdp = models.FloatField(blank=True, null=True)
    flag_url = models.URLField(blank=True, null=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

