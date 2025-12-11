"""
Management command to clear all recipes from the database.

This command deletes all Recipe records, allowing you to start fresh
with new recipes from seed_recipes or other sources.
"""

from django.core.management.base import BaseCommand
from recipes.models import Recipe


class Command(BaseCommand):
    """
    Management command to clear all recipes from the database.
    """
    help = 'Clears all recipes from the database'

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        """Delete all recipes from the database."""
        recipe_count = Recipe.objects.count()
        
        if recipe_count == 0:
            self.stdout.write(self.style.WARNING('No recipes found in the database.'))
            return
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    f'This will delete {recipe_count} recipe(s). '
                    'Are you sure? (yes/no): '
                )
            )
            confirmation = input().lower()
            if confirmation not in ['yes', 'y']:
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return
        
        deleted_count = Recipe.objects.all().delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} recipe(s).'
            )
        )

