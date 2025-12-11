from django.db import models
from django.conf import settings  


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    average_rating = models.IntegerField(default=0)

    difficulty = models.CharField(
        max_length=20,
        choices=[("Very Easy", "Very Easy"), ("Easy", "Easy"), ("Moderate", "Moderate"), ("Hard", "Hard"), ("Very Hard", "Very Hard")],
        default = "Easy",
    )

    total_time = models.CharField(max_length=50)

    servings = models.PositiveIntegerField(default=1)

    ingredients = models.TextField()

    method = models.TextField()

    # Image URL for the recipe
    image_url = models.URLField(blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  

    personal_rating = models.IntegerField(default=0, null=True, blank=True)

    image = models.ImageField(upload_to='images/', null=False, default='images/food1.jpg')

    def __str__(self):
        return self.name
