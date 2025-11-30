from django.db import models
from django.conf import settings
from .user import User

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default='')
    
    # Nutritional Goals
    calorie_goal = models.IntegerField(default=2000)
    protein_goal = models.IntegerField(default=150)
    carbs_goal = models.IntegerField(default=250)
    fat_goal = models.IntegerField(default=70)
    
    # Fasting Goal
    FASTING_CHOICES = [
        (12, '12 hours'),
        (14, '14 hours'),
        (16, '16 hours'),
        (18, '18 hours'),
    ]
    fasting_goal = models.IntegerField(choices=FASTING_CHOICES, default=16)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
