from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    # 1–5 as used in your seeder
    average_rating = models.IntegerField(default=0)

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("Easy", "Easy"),
            ("Moderate", "Moderate"),
            ("Hard", "Hard"),
        ],
    )

    # Store value such as '3 hours'
    total_time = models.CharField(max_length=50)

    servings = models.PositiveIntegerField(default=1)

    # comma separated list: "Ingredient 1, Ingredient 2, ..."
    ingredients = models.TextField()

    # multiline method text
    method = models.TextField()

    def __str__(self):
        return self.name
