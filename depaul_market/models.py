from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

'''
class Products(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    made_available = models.DateTimeField(auto_now=True)
    on_hold = models.BooleanField(default=False)

    available_until = models.DateTimeField(null=True, blank=True)  # This field can be null if no duration is provided


    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['made_available']
'''
class Products(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    made_available = models.DateTimeField(auto_now=True)

    available_until = models.DateTimeField(null=True, blank=True)  # This field can be null if no duration is provided
    is_sold = models.BooleanField(default=False)  # New field to track sold status
    on_hold = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['made_available']


class UserCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ForeignKey(Products, on_delete=models.CASCADE)

# Profile model to store additional student info
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    year = models.CharField(max_length=20, choices=[
        ('freshman', 'Freshman'),
        ('sophomore', 'Sophomore'),
        ('junior', 'Junior'),
        ('senior', 'Senior'),
        ('graduate', 'Graduate')
    ])
    campus = models.CharField(max_length=50, choices=[
        ('lincoln_park', 'Lincoln Park'),
        ('loop', 'Loop')
    ])
    graduating = models.BooleanField(default=False)
    
    # Add this field to store the user's self-written introduction
    introduction = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    
    def __str__(self):
        return self.balance