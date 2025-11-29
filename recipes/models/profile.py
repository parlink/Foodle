from django.db import models
from django.conf import settings


class Profile(models.Model):
    """Model to store user profile information including daily goals and current status."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Daily Goals
    calorie_goal = models.IntegerField(default=2000)
    protein_goal = models.IntegerField(null=True, blank=True)
    carbs_goal = models.IntegerField(null=True, blank=True)
    fat_goal = models.IntegerField(null=True, blank=True)
    
    # Current Status
    current_weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")

    def __str__(self):
        return f"{self.user.username}'s Profile"

