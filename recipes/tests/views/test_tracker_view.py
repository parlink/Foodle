"""Tests for the tracker view."""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from recipes.models import User, Profile, DailyLog, FastingSession, Meal
from recipes.tests.helpers import reverse_with_next


class TrackerViewTestCase(TestCase):
    """Tests for the main tracker view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('tracker')
        # Create profile
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                'calorie_goal': 2000,
                'protein_goal': 150,
                'carbs_goal': 250,
                'fat_goal': 70,
                'fasting_goal': 16
            }
        )

    def test_tracker_url(self):
        """Test that tracker URL resolves correctly."""
        self.assertEqual(self.url, '/tracker/')

    def test_get_tracker_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_tracker_when_logged_in(self):
        """Test GET request to tracker page when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/tracker.html')

    def test_tracker_creates_profile_if_not_exists(self):
        """Test that tracker creates profile if it doesn't exist."""
        # Delete existing profile
        Profile.objects.filter(user=self.user).delete()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_tracker_creates_daily_log_if_not_exists(self):
        """Test that tracker creates daily log if it doesn't exist."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(DailyLog.objects.filter(user=self.user).exists())

    def test_tracker_context_contains_required_data(self):
        """Test that tracker context contains all required data."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('daily_log', response.context)
        self.assertIn('daily_goals', response.context)
        self.assertIn('macros_consumed', response.context)
        self.assertIn('water_intake', response.context)
        self.assertIn('fasting_status', response.context)
        self.assertIn('meals', response.context)

    def test_update_water_positive(self):
        """Test adding water intake."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'action': 'update_water',
            'amount': 250
        })
        self.assertRedirects(response, self.url)
        daily_log = DailyLog.objects.get(user=self.user, date=date.today())
        self.assertEqual(daily_log.amount_ml, 250)

    def test_update_water_multiple_times(self):
        """Test adding water intake multiple times."""
        self.client.login(username=self.user.username, password='Password123')
        self.client.post(self.url, {'action': 'update_water', 'amount': 250})
        self.client.post(self.url, {'action': 'update_water', 'amount': 500})
        daily_log = DailyLog.objects.get(user=self.user, date=date.today())
        self.assertEqual(daily_log.amount_ml, 750)

    def test_update_water_negative_doesnt_go_below_zero(self):
        """Test that water intake doesn't go below zero."""
        self.client.login(username=self.user.username, password='Password123')
        # First add some water
        self.client.post(self.url, {'action': 'update_water', 'amount': 100})
        # Try to remove more than exists
        self.client.post(self.url, {'action': 'update_water', 'amount': -500})
        daily_log = DailyLog.objects.get(user=self.user, date=date.today())
        self.assertEqual(daily_log.amount_ml, 0)

    def test_update_goals(self):
        """Test updating daily goals."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'action': 'update_goals',
            'calorie_goal': 2500,
            'protein_goal': 180,
            'carbs_goal': 300,
            'fat_goal': 80,
            'water_goal': 3000
        })
        self.assertRedirects(response, self.url)
        daily_log = DailyLog.objects.get(user=self.user, date=date.today())
        self.assertEqual(daily_log.calorie_goal, 2500)
        self.assertEqual(daily_log.protein_goal, 180)
        self.assertEqual(daily_log.carbs_goal, 300)
        self.assertEqual(daily_log.fat_goal, 80)
        self.assertEqual(daily_log.water_goal, 3000)

    def test_start_fast(self):
        """Test starting a fasting session."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'action': 'start_fast',
            'target_duration': 18
        })
        self.assertRedirects(response, self.url)
        session = FastingSession.objects.filter(user=self.user, is_active=True).first()
        self.assertIsNotNone(session)
        self.assertEqual(session.target_duration, 18)

    def test_start_fast_ends_previous_active_session(self):
        """Test that starting a new fast ends any previous active session."""
        self.client.login(username=self.user.username, password='Password123')
        # Start first fast
        self.client.post(self.url, {'action': 'start_fast', 'target_duration': 16})
        first_session = FastingSession.objects.filter(user=self.user, is_active=True).first()
        self.assertIsNotNone(first_session)
        
        # Start second fast
        self.client.post(self.url, {'action': 'start_fast', 'target_duration': 18})
        first_session.refresh_from_db()
        self.assertFalse(first_session.is_active)
        
        active_sessions = FastingSession.objects.filter(user=self.user, is_active=True)
        self.assertEqual(active_sessions.count(), 1)
        self.assertEqual(active_sessions.first().target_duration, 18)

    def test_end_fast(self):
        """Test ending a fasting session."""
        self.client.login(username=self.user.username, password='Password123')
        # Start a fast first
        self.client.post(self.url, {'action': 'start_fast', 'target_duration': 16})
        session = FastingSession.objects.filter(user=self.user, is_active=True).first()
        self.assertIsNotNone(session)
        
        # End the fast
        response = self.client.post(self.url, {'action': 'end_fast'})
        self.assertRedirects(response, self.url)
        session.refresh_from_db()
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.end_date_time)

    def test_update_fasting_goal(self):
        """Test updating fasting goal without starting a fast."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'action': 'update_fasting_goal',
            'target_duration': 20
        })
        self.assertRedirects(response, self.url)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.fasting_goal, 20)

    def test_tracker_shows_meals(self):
        """Test that tracker shows today's meals."""
        self.client.login(username=self.user.username, password='Password123')
        # Create a meal
        Meal.objects.create(
            user=self.user,
            name='Test Breakfast',
            meal_type='Breakfast',
            date=date.today(),
            calories=400,
            protein_g=30,
            carbs_g=40,
            fat_g=15
        )
        response = self.client.get(self.url)
        meals = response.context['meals']
        self.assertEqual(len(meals['Breakfast']), 1)
        self.assertEqual(meals['Breakfast'][0]['title'], 'Test Breakfast')

    def test_tracker_calculates_macro_totals(self):
        """Test that tracker calculates macro totals correctly."""
        self.client.login(username=self.user.username, password='Password123')
        # Create two meals
        Meal.objects.create(
            user=self.user, name='Meal 1', meal_type='Breakfast',
            date=date.today(), calories=300, protein_g=20, carbs_g=30, fat_g=10
        )
        Meal.objects.create(
            user=self.user, name='Meal 2', meal_type='Lunch',
            date=date.today(), calories=500, protein_g=35, carbs_g=45, fat_g=20
        )
        response = self.client.get(self.url)
        macros = response.context['macros_consumed']
        self.assertEqual(macros['calories'], 800)
        self.assertEqual(macros['protein'], 55.0)
        self.assertEqual(macros['carbs'], 75.0)
        self.assertEqual(macros['fat'], 30.0)

    def test_tracker_shows_active_fasting_status(self):
        """Test that tracker shows active fasting status."""
        self.client.login(username=self.user.username, password='Password123')
        # Start a fast
        self.client.post(self.url, {'action': 'start_fast', 'target_duration': 16})
        response = self.client.get(self.url)
        fasting_status = response.context['fasting_status']
        self.assertTrue(fasting_status['is_active'])
        self.assertEqual(fasting_status['target_duration'], 16)
        self.assertIsNotNone(fasting_status['start_time'])

    def test_tracker_handles_snack_meal_type(self):
        """Test that tracker handles 'Snack' meal type in 'Snacks' category."""
        self.client.login(username=self.user.username, password='Password123')
        Meal.objects.create(
            user=self.user, name='Apple', meal_type='Snack',
            date=date.today(), calories=80, protein_g=0, carbs_g=20, fat_g=0
        )
        response = self.client.get(self.url)
        meals = response.context['meals']
        self.assertEqual(len(meals['Snacks']), 1)

    def test_tracker_handles_zero_carbs_goal(self):
        """Test that tracker handles zero carbs goal (no division by zero)."""
        self.client.login(username=self.user.username, password='Password123')
        # First get tracker to create the daily log
        self.client.get(self.url)
        # Update goals to have zero carbs goal
        DailyLog.objects.filter(user=self.user, date=date.today()).update(carbs_goal=0)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['carbs_pct'], 0)

    def test_tracker_handles_zero_fat_goal(self):
        """Test that tracker handles zero fat goal (no division by zero)."""
        self.client.login(username=self.user.username, password='Password123')
        # First get tracker to create the daily log
        self.client.get(self.url)
        # Update goals to have zero fat goal
        DailyLog.objects.filter(user=self.user, date=date.today()).update(fat_goal=0)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['fat_pct'], 0)

    def test_tracker_no_active_fasting_shows_default_status(self):
        """Test that tracker shows default fasting status when no active fast."""
        self.client.login(username=self.user.username, password='Password123')
        # Ensure no active fasting sessions
        FastingSession.objects.filter(user=self.user, is_active=True).delete()
        response = self.client.get(self.url)
        fasting_status = response.context['fasting_status']
        self.assertFalse(fasting_status['is_active'])
        self.assertEqual(fasting_status['time_elapsed'], '0h 00m 00s')

