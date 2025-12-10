from django.core.management.base import BaseCommand, CommandError
from recipes.models import (
    User, FastingSession, Meal, DailyLog, Profile, 
    Post, Follow, Save, Like, Comment, Tag, Recipe
)


class Command(BaseCommand):
    """
    Management command to remove (unseed) user data from the database.

    This command deletes all non-staff users and associated data from the database. 
    It is designed to complement the corresponding "seed" command, allowing developers 
    to reset the database to a clean state without removing administrative users.

    Attributes:
        help (str): Short description displayed when running
            `python manage.py help unseed`.
    """
    
    help = 'Removes seeded data from the database'

    def handle(self, *args, **options):
        """
        Execute the unseeding process.

        Deletes all tracker data, social data, and `User` records where `is_staff` 
        is False, preserving administrative accounts. Prints a confirmation message 
        upon completion.

        Args:
            *args: Positional arguments passed by Django (not used here).
            **options: Keyword arguments passed by Django (not used here).

        Returns:
            None
        """
        
        self.stdout.write("Clearing all seeded data...")
        
        # Clear social data (order matters due to foreign keys)
        self.stdout.write("  Clearing social data...")
        Comment.objects.all().delete()
        Like.objects.all().delete()
        Save.objects.all().delete()
        Follow.objects.all().delete()
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
        
        # Clear tags (optional - you might want to keep these)
        self.stdout.write("  Clearing tags...")
        Tag.objects.all().delete()

        # Delete non-staff users
        self.stdout.write("  Deleting non-staff users...")
        deleted_count, _ = User.objects.filter(is_staff=False).delete()
        
        self.stdout.write(self.style.SUCCESS(
            f"Successfully unseeded database: removed {deleted_count} users and all associated data."
        ))
