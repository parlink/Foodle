from django.db import models
from django.conf import settings
from datetime import date


class Meal(models.Model):
    """Model to track meals and their nutritional information."""

    MEAL_TYPE_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Snack', 'Snack'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meals'
    )
    name = models.CharField(max_length=200)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    date = models.DateField(default=date.today)
    
    # Nutrition Fields
    calories = models.IntegerField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()

    class Meta:
        ordering = ['-date', 'meal_type']

    def __str__(self):
        return f"{self.user.username} - {self.meal_type}: {self.name} ({self.date})"

