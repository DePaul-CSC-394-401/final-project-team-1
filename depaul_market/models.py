from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return self.user.username
