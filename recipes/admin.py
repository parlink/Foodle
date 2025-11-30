from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from recipes.models import User, Recipe, Profile, FastingSession, WaterIntake, Meal


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the custom User model."""
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin configuration for Recipe model."""
    list_display = ['name', 'difficulty', 'average_rating', 'servings', 'total_time']
    list_filter = ['difficulty', 'average_rating']
    search_fields = ['name', 'ingredients']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Profile model."""
    list_display = ['user', 'calorie_goal', 'protein_goal', 'current_weight', 'height']
    list_filter = ['calorie_goal']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']


@admin.register(FastingSession)
class FastingSessionAdmin(admin.ModelAdmin):
    """Admin configuration for FastingSession model."""
    list_display = ['user', 'start_date_time', 'target_duration', 'end_time', 'is_active']
    list_filter = ['is_active', 'target_duration', 'start_date_time']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'start_date_time'


@admin.register(WaterIntake)
class WaterIntakeAdmin(admin.ModelAdmin):
    """Admin configuration for WaterIntake model."""
    list_display = ['user', 'date', 'amount_ml']
    list_filter = ['date']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'date'


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    """Admin configuration for Meal model."""
    list_display = ['user', 'name', 'meal_type', 'date', 'calories', 'protein_g', 'carbs_g', 'fat_g']
    list_filter = ['meal_type', 'date']
    search_fields = ['user__username', 'name', 'user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'date'
