from django.db import models
from datetime import datetime


class Products(models.Model):
    image = models.ImageField(null=False, blank=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    made_avaliable = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['made_avaliable']