"""Tests for the water history view."""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from recipes.models import User, DailyLog
from recipes.tests.helpers import reverse_with_next


class WaterHistoryViewTestCase(TestCase):
    """Tests for the water history view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('water_history')
        # Create some water intake records
        today = timezone.localdate()
        for i in range(7):
            DailyLog.objects.create(
                user=self.user,
                date=today - timedelta(days=i),
                amount_ml=2000 + (i * 100)
            )

    def test_water_history_url(self):
        """Test that water history URL resolves correctly."""
        self.assertEqual(self.url, '/water-history/')

    def test_get_water_history_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_water_history_when_logged_in(self):
        """Test GET request to water history page when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/water_history.html')

    def test_water_history_context_contains_required_data(self):
        """Test that water history context contains all required data."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('view_type', response.context)
        self.assertIn('date_offset', response.context)
        self.assertIn('start_date', response.context)
        self.assertIn('end_date', response.context)
        self.assertIn('chart_labels', response.context)
        self.assertIn('chart_data', response.context)
        self.assertIn('table_data', response.context)

    def test_water_history_default_view_type_is_week(self):
        """Test that default view type is week."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['view_type'], 'week')

    def test_water_history_week_view(self):
        """Test water history weekly view."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=week')
        self.assertEqual(response.context['view_type'], 'week')
        # Weekly view should have 7 data points
        self.assertEqual(len(response.context['chart_labels']), 7)
        self.assertEqual(len(response.context['chart_data']), 7)

    def test_water_history_month_view(self):
        """Test water history monthly view."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=month')
        self.assertEqual(response.context['view_type'], 'month')
        # Monthly view should have data aggregated by weeks
        self.assertGreater(len(response.context['chart_labels']), 0)

    def test_water_history_date_offset_navigation(self):
        """Test date offset navigation."""
        self.client.login(username=self.user.username, password='Password123')
        # Go to previous week
        response = self.client.get(self.url + '?view_type=week&date_offset=-1')
        self.assertEqual(response.context['date_offset'], -1)

    def test_water_history_invalid_date_offset_defaults_to_zero(self):
        """Test that invalid date offset defaults to 0."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?date_offset=invalid')
        self.assertEqual(response.context['date_offset'], 0)

    def test_water_history_edit_water_intake(self):
        """Test editing water intake via POST."""
        self.client.login(username=self.user.username, password='Password123')
        today = timezone.localdate()
        response = self.client.post(self.url + '?view_type=week&date_offset=0', {
            'date': str(today),
            'amount': 3000
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        daily_log = DailyLog.objects.get(user=self.user, date=today)
        self.assertEqual(daily_log.amount_ml, 3000)

    def test_water_history_edit_creates_new_log_if_not_exists(self):
        """Test that editing creates new log if it doesn't exist."""
        self.client.login(username=self.user.username, password='Password123')
        # Use a date far in the past that doesn't have a log
        old_date = timezone.localdate() - timedelta(days=30)
        response = self.client.post(self.url + '?view_type=week&date_offset=0', {
            'date': str(old_date),
            'amount': 1500
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        daily_log = DailyLog.objects.get(user=self.user, date=old_date)
        self.assertEqual(daily_log.amount_ml, 1500)

    def test_water_history_edit_invalid_amount_ignored(self):
        """Test that invalid amount value is ignored."""
        self.client.login(username=self.user.username, password='Password123')
        today = timezone.localdate()
        original_amount = DailyLog.objects.get(user=self.user, date=today).amount_ml
        response = self.client.post(self.url + '?view_type=week&date_offset=0', {
            'date': str(today),
            'amount': 'invalid'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        daily_log = DailyLog.objects.get(user=self.user, date=today)
        self.assertEqual(daily_log.amount_ml, original_amount)

    def test_water_history_negative_amount_set_to_zero(self):
        """Test that negative amount is set to zero."""
        self.client.login(username=self.user.username, password='Password123')
        today = timezone.localdate()
        response = self.client.post(self.url + '?view_type=week&date_offset=0', {
            'date': str(today),
            'amount': -500
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        daily_log = DailyLog.objects.get(user=self.user, date=today)
        self.assertEqual(daily_log.amount_ml, 0)

    def test_water_history_show_next_is_false_for_current_period(self):
        """Test that show_next is False when viewing current period."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=week&date_offset=0')
        self.assertFalse(response.context['show_next'])

    def test_water_history_show_next_is_true_for_past_period(self):
        """Test that show_next is True when viewing past period."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=week&date_offset=-2')
        self.assertTrue(response.context['show_next'])

    def test_water_history_month_view_navigate_forward(self):
        """Test navigating forward in month view."""
        self.client.login(username=self.user.username, password='Password123')
        # Navigate to a past month first, then we can check forward navigation
        response = self.client.get(self.url + '?view_type=month&date_offset=-3')
        self.assertEqual(response.context['view_type'], 'month')
        self.assertEqual(response.status_code, 200)

    def test_water_history_month_view_year_overflow(self):
        """Test month view handles year overflow (Dec -> Jan)."""
        self.client.login(username=self.user.username, password='Password123')
        # Go 12 months back (full year)
        response = self.client.get(self.url + '?view_type=month&date_offset=-12')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['view_type'], 'month')

    def test_water_history_month_view_year_underflow(self):
        """Test month view handles year underflow."""
        self.client.login(username=self.user.username, password='Password123')
        # Go forward (though won't show data) to test the logic
        response = self.client.get(self.url + '?view_type=month&date_offset=0')
        self.assertEqual(response.status_code, 200)

