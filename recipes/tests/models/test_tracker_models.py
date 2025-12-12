"""Unit tests for tracker-related models: Meal, DailyLog, FastingSession."""
from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from recipes.models import User, Meal, DailyLog, FastingSession


class MealModelTestCase(TestCase):
    """Unit tests for the Meal model."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.meal_data = {
            'user': self.user,
            'name': 'Chicken Salad',
            'meal_type': 'Lunch',
            'date': date.today(),
            'calories': 450,
            'protein_g': 35.0,
            'carbs_g': 20.0,
            'fat_g': 25.0,
        }

    def test_create_meal(self):
        """Test creating a meal with valid data."""
        meal = Meal.objects.create(**self.meal_data)
        self.assertEqual(meal.name, 'Chicken Salad')
        self.assertEqual(meal.meal_type, 'Lunch')
        self.assertEqual(meal.calories, 450)
        self.assertEqual(meal.protein_g, 35.0)
        self.assertEqual(meal.carbs_g, 20.0)
        self.assertEqual(meal.fat_g, 25.0)

    def test_meal_str_representation(self):
        """Test meal string representation."""
        meal = Meal.objects.create(**self.meal_data)
        expected_str = f"{self.user.username} - Lunch: Chicken Salad ({date.today()})"
        self.assertEqual(str(meal), expected_str)

    def test_meal_type_choices(self):
        """Test all valid meal type choices."""
        for meal_type, _ in Meal.MEAL_TYPE_CHOICES:
            self.meal_data['meal_type'] = meal_type
            meal = Meal.objects.create(**self.meal_data)
            self.assertEqual(meal.meal_type, meal_type)
            meal.delete()

    def test_meal_ordering(self):
        """Test meal ordering (by date descending, then meal_type)."""
        yesterday = date.today() - timedelta(days=1)
        meal1 = Meal.objects.create(
            user=self.user, name='Yesterday Dinner', meal_type='Dinner',
            date=yesterday, calories=600, protein_g=40, carbs_g=50, fat_g=30
        )
        meal2 = Meal.objects.create(
            user=self.user, name='Today Breakfast', meal_type='Breakfast',
            date=date.today(), calories=400, protein_g=30, carbs_g=40, fat_g=20
        )
        meals = list(Meal.objects.filter(user=self.user))
        self.assertEqual(meals[0], meal2)  # Today first (more recent)


class DailyLogModelTestCase(TestCase):
    """Unit tests for the DailyLog model."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.daily_log_data = {
            'user': self.user,
            'date': date.today(),
            'amount_ml': 1500,
            'calorie_goal': 2000,
            'protein_goal': 150,
            'carbs_goal': 200,
            'fat_goal': 70,
            'water_goal': 2500,
        }

    def test_create_daily_log(self):
        """Test creating a daily log with valid data."""
        daily_log = DailyLog.objects.create(**self.daily_log_data)
        self.assertEqual(daily_log.amount_ml, 1500)
        self.assertEqual(daily_log.calorie_goal, 2000)
        self.assertEqual(daily_log.water_goal, 2500)

    def test_daily_log_str_representation(self):
        """Test daily log string representation."""
        daily_log = DailyLog.objects.create(**self.daily_log_data)
        expected_str = f"{self.user.username} - {date.today()}: 1500ml water, 2000 cal goal"
        self.assertEqual(str(daily_log), expected_str)

    def test_daily_log_unique_together(self):
        """Test that user and date combination is unique."""
        DailyLog.objects.create(**self.daily_log_data)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            DailyLog.objects.create(**self.daily_log_data)

    def test_daily_log_default_values(self):
        """Test default values for daily log."""
        daily_log = DailyLog.objects.create(user=self.user, date=date.today())
        self.assertEqual(daily_log.amount_ml, 0)
        self.assertEqual(daily_log.calorie_goal, 2500)
        self.assertEqual(daily_log.protein_goal, 187)
        self.assertEqual(daily_log.carbs_goal, 250)
        self.assertEqual(daily_log.fat_goal, 83)
        self.assertEqual(daily_log.water_goal, 2500)


class FastingSessionModelTestCase(TestCase):
    """Unit tests for the FastingSession model."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.now = timezone.now()
        self.fasting_data = {
            'user': self.user,
            'start_date_time': self.now,
            'target_duration': 16,
            'is_active': True,
        }

    def test_create_fasting_session(self):
        """Test creating a fasting session with valid data."""
        session = FastingSession.objects.create(**self.fasting_data)
        self.assertEqual(session.target_duration, 16)
        self.assertTrue(session.is_active)
        self.assertIsNone(session.end_date_time)

    def test_fasting_session_str_representation_active(self):
        """Test fasting session string representation when active."""
        session = FastingSession.objects.create(**self.fasting_data)
        expected_str = f"{self.user.username}'s 16h fast - Active"
        self.assertEqual(str(session), expected_str)

    def test_fasting_session_str_representation_completed(self):
        """Test fasting session string representation when completed."""
        self.fasting_data['is_active'] = False
        self.fasting_data['end_date_time'] = self.now + timedelta(hours=16)
        session = FastingSession.objects.create(**self.fasting_data)
        expected_str = f"{self.user.username}'s 16h fast - Completed"
        self.assertEqual(str(session), expected_str)

    def test_duration_property_completed_session(self):
        """Test duration property for completed session."""
        start = self.now - timedelta(hours=18)
        end = self.now
        session = FastingSession.objects.create(
            user=self.user,
            start_date_time=start,
            end_date_time=end,
            target_duration=16,
            is_active=False
        )
        duration = session.duration
        self.assertAlmostEqual(duration.total_seconds(), 18 * 3600, delta=1)

    def test_duration_property_active_session(self):
        """Test duration property for active session."""
        start = self.now - timedelta(hours=5)
        session = FastingSession.objects.create(
            user=self.user,
            start_date_time=start,
            target_duration=16,
            is_active=True
        )
        duration = session.duration
        # Should be approximately 5 hours
        self.assertGreaterEqual(duration.total_seconds(), 5 * 3600 - 10)

    def test_duration_property_no_end_not_active(self):
        """Test duration property returns zero when not active and no end time."""
        session = FastingSession.objects.create(
            user=self.user,
            start_date_time=self.now,
            target_duration=16,
            is_active=False,
            end_date_time=None
        )
        duration = session.duration
        self.assertEqual(duration, timedelta(0))

    def test_end_time_method(self):
        """Test end_time method calculates correct target end time."""
        session = FastingSession.objects.create(**self.fasting_data)
        expected_end = self.now + timedelta(hours=16)
        self.assertEqual(session.end_time(), expected_end)

    def test_target_duration_choices(self):
        """Test all valid target duration choices."""
        for duration, _ in FastingSession.TARGET_DURATION_CHOICES:
            self.fasting_data['target_duration'] = duration
            session = FastingSession.objects.create(**self.fasting_data)
            self.assertEqual(session.target_duration, duration)
            session.delete()

