from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


class FastingSession(models.Model):
    """Model to track intermittent fasting sessions for users."""

    TARGET_DURATION_CHOICES = [
        (14, '14 hours'),
        (16, '16 hours'),
        (18, '18 hours'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fasting_sessions'
    )
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField(null=True, blank=True)
    target_duration = models.IntegerField(choices=TARGET_DURATION_CHOICES, default=16)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date_time']
        
    @property
    def duration(self):
        if self.end_date_time and self.start_date_time:
            return self.end_date_time - self.start_date_time
        if self.is_active:
             return timezone.now() - self.start_date_time
        return timedelta(0)

    def end_time(self):
        """Calculate when the fast should finish."""
        return self.start_date_time + timedelta(hours=self.target_duration)

    def __str__(self):
        status = "Active" if self.is_active else "Completed"
        return f"{self.user.username}'s {self.target_duration}h fast - {status}"

