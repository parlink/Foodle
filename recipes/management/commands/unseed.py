"""
Management command to remove all seeded data from the database.

This command clears all user-generated content, tracker data, social interactions,
recipes, and non-staff users - essentially resetting the database to a clean state.
"""

from django.core.management.base import BaseCommand
from recipes.models import (
    User, FastingSession, Meal, DailyLog, Profile, 
    Post, Follow, Save, Like, Comment, Tag, Recipe, Rating
)


class Command(BaseCommand):
    """
    Management command to remove all seeded data from the database.
    
    Deletes all non-staff users and associated data, preserving 
    administrative accounts.
    """
    
    help = 'Removes all seeded data from the database (users, recipes, posts, tracker data)'

    def handle(self, *args, **options):
        """Execute the unseeding process."""
        self.stdout.write("Clearing all seeded data...")
        
        # Clear social interactions (order matters due to foreign keys)
        self.stdout.write("  Clearing social interactions...")
        Rating.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        Save.objects.all().delete()
        Follow.objects.all().delete()
        
        # Clear posts
        self.stdout.write("  Clearing posts...")
        Post.objects.all().delete()
        
        # Clear tracker data
        self.stdout.write("  Clearing tracker data...")
        FastingSession.objects.all().delete()
        Meal.objects.all().delete()
        DailyLog.objects.all().delete()
        
        # Clear recipes
        self.stdout.write("  Clearing recipes...")
        Recipe.objects.all().delete()
        
        # Clear profiles
        self.stdout.write("  Clearing profiles...")
        Profile.objects.all().delete()
        
        # Clear tags
        self.stdout.write("  Clearing tags...")
        Tag.objects.all().delete()

        # Delete non-staff users
        self.stdout.write("  Deleting non-staff users...")
        deleted_count, _ = User.objects.filter(is_staff=False).delete()
        
        self.stdout.write(self.style.SUCCESS(
            f"\nSuccessfully unseeded database!\n"
            f"  - Removed {deleted_count} users and all associated data.\n"
            f"  - Staff/admin accounts preserved."
        ))
