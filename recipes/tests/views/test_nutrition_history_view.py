"""Tests for the nutrition history view."""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from recipes.models import User, DailyLog, Meal
from recipes.tests.helpers import reverse_with_next


class NutritionHistoryViewTestCase(TestCase):
    """Tests for the nutrition history view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('nutrition_history')
        # Create some daily logs and meals for testing
        today = timezone.localdate()
        for i in range(14):
            date = today - timedelta(days=i)
            DailyLog.objects.create(
                user=self.user,
                date=date,
                calorie_goal=2000,
                protein_goal=150,
                carbs_goal=200,
                fat_goal=70,
                amount_ml=2000
            )
            Meal.objects.create(
                user=self.user,
                name=f'Meal {i}',
                meal_type='Lunch',
                date=date,
                calories=1500 + (i * 50),
                protein_g=100 + (i * 5),
                carbs_g=150 + (i * 3),
                fat_g=50 + (i * 2)
            )

    def test_nutrition_history_url(self):
        """Test that nutrition history URL resolves correctly."""
        self.assertEqual(self.url, '/nutrition-history/')

    def test_get_nutrition_history_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_nutrition_history_when_logged_in(self):
        """Test GET request to nutrition history page when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/nutrition_history.html')

    def test_nutrition_history_context_contains_required_data(self):
        """Test that nutrition history context contains all required data."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('days', response.context)
        self.assertIn('start_date', response.context)
        self.assertIn('end_date', response.context)
        self.assertIn('chart_labels', response.context)
        self.assertIn('calories_actual', response.context)
        self.assertIn('calories_goal', response.context)
        self.assertIn('protein_actual', response.context)
        self.assertIn('protein_goal', response.context)
        self.assertIn('carbs_actual', response.context)
        self.assertIn('carbs_goal', response.context)
        self.assertIn('fat_actual', response.context)
        self.assertIn('fat_goal', response.context)

    def test_nutrition_history_default_days_is_30(self):
        """Test that default days is 30."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['days'], 30)

    def test_nutrition_history_custom_days(self):
        """Test custom days parameter."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=14')
        self.assertEqual(response.context['days'], 14)
        # Should have 14 data points
        self.assertEqual(len(response.context['chart_labels']), 14)

    def test_nutrition_history_days_minimum_is_7(self):
        """Test that days is limited to minimum of 7."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=3')
        self.assertEqual(response.context['days'], 7)

    def test_nutrition_history_days_maximum_is_90(self):
        """Test that days is limited to maximum of 90."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=120')
        self.assertEqual(response.context['days'], 90)

    def test_nutrition_history_invalid_days_defaults_to_30(self):
        """Test that invalid days parameter defaults to 30."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=invalid')
        self.assertEqual(response.context['days'], 30)

    def test_nutrition_history_shows_actual_calories(self):
        """Test that actual calories are calculated from meals."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=7')
        calories_actual = response.context['calories_actual']
        # Should have data for days with meals
        self.assertGreater(sum(calories_actual), 0)

    def test_nutrition_history_shows_goal_calories(self):
        """Test that goal calories are fetched from daily logs."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=7')
        calories_goal = response.context['calories_goal']
        # Should have goal data from daily logs
        self.assertGreater(sum(calories_goal), 0)

    def test_nutrition_history_date_range(self):
        """Test that date range is calculated correctly."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=14')
        today = timezone.localdate()
        expected_start = today - timedelta(days=13)
        self.assertEqual(response.context['start_date'], expected_start)
        self.assertEqual(response.context['end_date'], today)

    def test_nutrition_history_labels_format_for_short_period(self):
        """Test that labels use 'Mon DD' format for periods <= 14 days."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=14')
        labels = response.context['chart_labels']
        # Short period labels should be like "Jan 01"
        self.assertTrue(any(' ' in label for label in labels))

    def test_nutrition_history_labels_format_for_long_period(self):
        """Test that labels use 'MM/DD' format for periods > 14 days."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?days=30')
        labels = response.context['chart_labels']
        # Long period labels should be like "01/15"
        self.assertTrue(any('/' in label for label in labels))

    def test_nutrition_history_handles_days_without_logs(self):
        """Test that days without logs show zero goals."""
        self.client.login(username=self.user.username, password='Password123')
        # Request data for a period that includes days without logs
        response = self.client.get(self.url + '?days=90')
        calories_goal = response.context['calories_goal']
        # Some days should have 0 goals (no daily log)
        self.assertIn(0, calories_goal)

    def test_nutrition_history_aggregates_multiple_meals_per_day(self):
        """Test that multiple meals per day are aggregated."""
        self.client.login(username=self.user.username, password='Password123')
        today = timezone.localdate()
        # Add another meal for today
        Meal.objects.create(
            user=self.user,
            name='Extra Meal',
            meal_type='Dinner',
            date=today,
            calories=500,
            protein_g=30,
            carbs_g=40,
            fat_g=20
        )
        response = self.client.get(self.url + '?days=7')
        calories_actual = response.context['calories_actual']
        # Today's calories should be sum of both meals
        # Today is the last day in the list
        self.assertGreater(calories_actual[-1], 1500)

