from django.db import models
from django.conf import settings


class DailyLog(models.Model):
    """Model to track daily nutrition goals and water intake for users."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_logs'
    )
    date = models.DateField()
    
    #Water intake tracking
    amount_ml = models.IntegerField(default=0)
    
    #Daily goals for this specific date
    calorie_goal = models.IntegerField(default=2500)
    protein_goal = models.IntegerField(default=187)  #30% of 2500 cal / 4
    carbs_goal = models.IntegerField(default=250)    #40% of 2500 cal / 4
    fat_goal = models.IntegerField(default=83)       #30% of 2500 cal / 9
    water_goal = models.IntegerField(default=2500)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.amount_ml}ml water, {self.calorie_goal} cal goal"

