from django.db import models
from django.conf import settings


class WaterIntake(models.Model):
    """Model to track daily water intake for users."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='water_intakes'
    )
    date = models.DateField()
    amount_ml = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.amount_ml}ml"

