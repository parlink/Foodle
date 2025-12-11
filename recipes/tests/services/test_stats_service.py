"""Tests for the UserStatsService."""
from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from recipes.models import User, Profile, Meal, DailyLog, FastingSession, Post, Follow, Save
from recipes.services.stats_service import UserStatsService


class UserStatsServiceTestCase(TestCase):
    """Tests for the UserStatsService."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.service = UserStatsService(self.user)

    def test_get_stats_returns_all_expected_keys(self):
        """Test that get_stats returns all expected statistics keys."""
        stats = self.service.get_stats()
        expected_keys = [
            'total_meals_logged', 'total_recipes_shared', 'total_followers',
            'total_following', 'current_streak', 'longest_streak',
            'total_water_ml', 'total_water_liters', 'total_fasting_hours',
            'completed_fasts', 'saved_recipes', 'member_since', 'days_as_member'
        ]
        for key in expected_keys:
            self.assertIn(key, stats)

    def test_count_meals_with_no_meals(self):
        """Test meal count when user has no meals."""
        stats = self.service.get_stats()
        self.assertEqual(stats['total_meals_logged'], 0)

    def test_count_meals_with_meals(self):
        """Test meal count when user has meals."""
        # Create some meals
        for i in range(5):
            Meal.objects.create(
                user=self.user,
                name=f'Meal {i}',
                meal_type='Lunch',
                date=date.today(),
                calories=500,
                protein_g=30,
                carbs_g=50,
                fat_g=20
            )
        stats = self.service.get_stats()
        self.assertEqual(stats['total_meals_logged'], 5)

    def test_count_posts(self):
        """Test post/recipe count."""
        # Create some posts
        for i in range(3):
            Post.objects.create(
                author=self.user,
                title=f'Post {i}',
                caption='Test caption'
            )
        service = UserStatsService(self.user)
        stats = service.get_stats()
        self.assertEqual(stats['total_recipes_shared'], 3)

    def test_count_followers(self):
        """Test follower count."""
        # Create follow relationships
        Follow.objects.create(follower=self.other_user, followed=self.user)
        stats = self.service.get_stats()
        self.assertEqual(stats['total_followers'], 1)

    def test_count_following(self):
        """Test following count."""
        Follow.objects.create(follower=self.user, followed=self.other_user)
        stats = self.service.get_stats()
        self.assertEqual(stats['total_following'], 1)

    def test_count_saved_recipes(self):
        """Test saved recipes count."""
        # Create a post and save it
        post = Post.objects.create(
            author=self.other_user,
            title='Test Post',
            caption='Test'
        )
        Save.objects.create(user=self.user, post=post)
        stats = self.service.get_stats()
        self.assertEqual(stats['saved_recipes'], 1)

    def test_sum_water_with_no_logs(self):
        """Test water sum when no logs exist."""
        stats = self.service.get_stats()
        self.assertEqual(stats['total_water_ml'], 0)
        self.assertEqual(stats['total_water_liters'], 0.0)

    def test_sum_water_with_logs(self):
        """Test water sum with daily logs."""
        # Create daily logs with water
        DailyLog.objects.create(user=self.user, date=date.today(), amount_ml=2000)
        DailyLog.objects.create(user=self.user, date=date.today() - timedelta(days=1), amount_ml=1500)
        stats = self.service.get_stats()
        self.assertEqual(stats['total_water_ml'], 3500)
        self.assertEqual(stats['total_water_liters'], 3.5)

    def test_sum_fasting_hours_with_no_sessions(self):
        """Test fasting hours sum when no sessions exist."""
        stats = self.service.get_stats()
        self.assertEqual(stats['total_fasting_hours'], 0)

    def test_sum_fasting_hours_with_completed_sessions(self):
        """Test fasting hours sum with completed sessions."""
        now = timezone.now()
        # Create completed fasting sessions
        FastingSession.objects.create(
            user=self.user,
            start_date_time=now - timedelta(hours=20),
            end_date_time=now - timedelta(hours=4),
            target_duration=16,
            is_active=False
        )  # 16 hours
        FastingSession.objects.create(
            user=self.user,
            start_date_time=now - timedelta(days=1, hours=18),
            end_date_time=now - timedelta(days=1),
            target_duration=18,
            is_active=False
        )  # 18 hours
        stats = self.service.get_stats()
        self.assertGreater(stats['total_fasting_hours'], 30)

    def test_count_completed_fasts(self):
        """Test completed fasts count."""
        now = timezone.now()
        # Create completed and active sessions
        FastingSession.objects.create(
            user=self.user,
            start_date_time=now - timedelta(hours=20),
            end_date_time=now - timedelta(hours=4),
            target_duration=16,
            is_active=False
        )
        FastingSession.objects.create(
            user=self.user,
            start_date_time=now - timedelta(hours=5),
            target_duration=16,
            is_active=True
        )
        stats = self.service.get_stats()
        self.assertEqual(stats['completed_fasts'], 1)

    def test_current_streak_with_no_meals(self):
        """Test current streak when no meals exist."""
        stats = self.service.get_stats()
        self.assertEqual(stats['current_streak'], 0)

    def test_current_streak_with_consecutive_days(self):
        """Test current streak with consecutive days of meals."""
        today = date.today()
        for i in range(5):
            Meal.objects.create(
                user=self.user,
                name=f'Meal {i}',
                meal_type='Lunch',
                date=today - timedelta(days=i),
                calories=500,
                protein_g=30,
                carbs_g=50,
                fat_g=20
            )
        service = UserStatsService(self.user)
        stats = service.get_stats()
        self.assertEqual(stats['current_streak'], 5)

    def test_current_streak_breaks_on_gap(self):
        """Test that current streak is 0 when there's a gap."""
        today = date.today()
        # Create meals but not for today or yesterday
        Meal.objects.create(
            user=self.user,
            name='Old Meal',
            meal_type='Lunch',
            date=today - timedelta(days=3),
            calories=500,
            protein_g=30,
            carbs_g=50,
            fat_g=20
        )
        service = UserStatsService(self.user)
        stats = service.get_stats()
        self.assertEqual(stats['current_streak'], 0)

    def test_longest_streak(self):
        """Test longest streak calculation."""
        # Create consecutive meals in the past
        start_date = date.today() - timedelta(days=20)
        for i in range(7):  # 7-day streak
            Meal.objects.create(
                user=self.user,
                name=f'Meal {i}',
                meal_type='Lunch',
                date=start_date + timedelta(days=i),
                calories=500,
                protein_g=30,
                carbs_g=50,
                fat_g=20
            )
        service = UserStatsService(self.user)
        stats = service.get_stats()
        self.assertEqual(stats['longest_streak'], 7)

    def test_days_as_member(self):
        """Test days as member calculation."""
        stats = self.service.get_stats()
        self.assertIsInstance(stats['days_as_member'], int)
        self.assertGreaterEqual(stats['days_as_member'], 0)

    def test_member_since(self):
        """Test member since returns date_joined."""
        stats = self.service.get_stats()
        self.assertEqual(stats['member_since'], self.user.date_joined)

    def test_caching_meals_count(self):
        """Test that meals count is cached."""
        # First call
        stats1 = self.service.get_stats()
        meals1 = stats1['total_meals_logged']
        
        # Add a meal
        Meal.objects.create(
            user=self.user,
            name='New Meal',
            meal_type='Lunch',
            date=date.today(),
            calories=500,
            protein_g=30,
            carbs_g=50,
            fat_g=20
        )
        
        # Second call on same service instance should return cached value
        stats2 = self.service.get_stats()
        meals2 = stats2['total_meals_logged']
        self.assertEqual(meals1, meals2)
        
        # New service instance should get updated count
        new_service = UserStatsService(self.user)
        stats3 = new_service.get_stats()
        meals3 = stats3['total_meals_logged']
        self.assertEqual(meals3, meals1 + 1)

