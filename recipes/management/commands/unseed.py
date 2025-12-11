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

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        """Execute the unseeding process."""
        
        # Count records before deletion
        counts = {
            'users': User.objects.filter(is_staff=False).count(),
            'recipes': Recipe.objects.count(),
            'posts': Post.objects.count(),
            'meals': Meal.objects.count(),
            'profiles': Profile.objects.count(),
        }
        
        total = sum(counts.values())
        
        if total == 0:
            self.stdout.write(self.style.WARNING('Database is already empty. Nothing to unseed.'))
            return
        
        # Confirmation prompt
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                f"\nThis will delete:\n"
                f"  - {counts['users']} non-staff users\n"
                f"  - {counts['recipes']} recipes\n"
                f"  - {counts['posts']} posts\n"
                f"  - {counts['meals']} meals\n"
                f"  - {counts['profiles']} profiles\n"
                f"  - All related data (likes, comments, follows, etc.)\n\n"
                f"Are you sure? (yes/no): "
            ))
            confirmation = input().lower()
            if confirmation not in ['yes', 'y']:
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return
        
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
