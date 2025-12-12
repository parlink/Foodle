from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
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
    
    # User Preferences / Settings
    THEME_CHOICES = [
        ('system', 'System Default'),
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    
    COLOR_BLIND_CHOICES = [
        ('none', 'None'),
        ('protanopia', 'Protanopia'),
        ('deuteranopia', 'Deuteranopia'),
        ('tritanopia', 'Tritanopia'),
        ('achromatopsia', 'Achromatopsia'),
    ]
    color_blind_mode = models.CharField(max_length=20, choices=COLOR_BLIND_CHOICES, default='none')
    
    font_scale = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.8), MaxValueValidator(1.5)]
    )
    
    # Units preference
    UNIT_CHOICES = [
        ('metric', 'Metric (kg, ml)'),
        ('imperial', 'Imperial (lbs, oz)'),
    ]
    units_preference = models.CharField(max_length=10, choices=UNIT_CHOICES, default='metric')
    
    # Privacy settings
    is_profile_public = models.BooleanField(default=True)
    show_stats_publicly = models.BooleanField(default=True)
    
    # Notification preferences
    email_weekly_summary = models.BooleanField(default=True)
    email_follower_notifications = models.BooleanField(default=False)
    reminder_log_meals = models.BooleanField(default=False)
    reminder_time = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
