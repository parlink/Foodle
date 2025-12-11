"""Tests for the fasting history view."""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from recipes.models import User, Profile, FastingSession
from recipes.tests.helpers import reverse_with_next


class FastingHistoryViewTestCase(TestCase):
    """Tests for the fasting history view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('fasting_history')
        # Create profile with fasting goal
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={'fasting_goal': 16}
        )
        # Create some fasting sessions
        now = timezone.now()
        for i in range(3):
            start = now - timedelta(days=i, hours=20)
            end = start + timedelta(hours=16)
            FastingSession.objects.create(
                user=self.user,
                start_date_time=start,
                end_date_time=end,
                target_duration=16,
                is_active=False
            )

    def test_fasting_history_url(self):
        """Test that fasting history URL resolves correctly."""
        self.assertEqual(self.url, '/fasting-history/')

    def test_get_fasting_history_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_fasting_history_when_logged_in(self):
        """Test GET request to fasting history page when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/fasting_history.html')

    def test_fasting_history_context_contains_required_data(self):
        """Test that fasting history context contains all required data."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('view_type', response.context)
        self.assertIn('date_offset', response.context)
        self.assertIn('start_date', response.context)
        self.assertIn('end_date', response.context)
        self.assertIn('chart_labels', response.context)
        self.assertIn('chart_data', response.context)
        self.assertIn('chart_goal_data', response.context)
        self.assertIn('table_data', response.context)

    def test_fasting_history_default_view_type_is_week(self):
        """Test that default view type is week."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['view_type'], 'week')

    def test_fasting_history_week_view(self):
        """Test fasting history weekly view."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=week')
        self.assertEqual(response.context['view_type'], 'week')
        # Weekly view should have 7 data points
        self.assertEqual(len(response.context['chart_labels']), 7)
        self.assertEqual(len(response.context['chart_data']), 7)

    def test_fasting_history_month_view(self):
        """Test fasting history monthly view."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=month')
        self.assertEqual(response.context['view_type'], 'month')
        self.assertGreater(len(response.context['chart_labels']), 0)

    def test_fasting_history_date_offset_navigation(self):
        """Test date offset navigation."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=week&date_offset=-1')
        self.assertEqual(response.context['date_offset'], -1)

    def test_fasting_history_invalid_date_offset_defaults_to_zero(self):
        """Test that invalid date offset defaults to 0."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?date_offset=invalid')
        self.assertEqual(response.context['date_offset'], 0)

    def test_fasting_history_edit_session(self):
        """Test editing a fasting session via POST."""
        self.client.login(username=self.user.username, password='Password123')
        session = FastingSession.objects.filter(user=self.user).first()
        new_start = timezone.now() - timedelta(hours=20)
        new_end = new_start + timedelta(hours=18)
        
        response = self.client.post(self.url + '?view_type=week&date_offset=0', {
            'action': 'edit_session',
            'session_id': session.id,
            'start_time': new_start.isoformat(),
            'end_time': new_end.isoformat()
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        session.refresh_from_db()
        self.assertFalse(session.is_active)

    def test_fasting_history_edit_session_makes_active_when_no_end_time(self):
        """Test editing session without end time makes it active."""
        self.client.login(username=self.user.username, password='Password123')
        session = FastingSession.objects.filter(user=self.user, is_active=False).first()
        new_start = timezone.now() - timedelta(hours=5)
        
        response = self.client.post(self.url + '?view_type=week&date_offset=0', {
            'action': 'edit_session',
            'session_id': session.id,
            'start_time': new_start.isoformat(),
            'end_time': ''  # No end time
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        session.refresh_from_db()
        self.assertTrue(session.is_active)
        self.assertIsNone(session.end_date_time)

    def test_fasting_history_edit_nonexistent_session_returns_404(self):
        """Test editing non-existent session returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url + '?view_type=week&date_offset=0', {
            'action': 'edit_session',
            'session_id': 99999,
            'start_time': timezone.now().isoformat()
        })
        self.assertEqual(response.status_code, 404)

    def test_fasting_history_table_shows_sessions(self):
        """Test that table data contains fasting sessions."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        table_data = response.context['table_data']
        self.assertGreater(len(table_data), 0)
        # Check structure of table data
        if table_data:
            session_data = table_data[0]
            self.assertIn('id', session_data)
            self.assertIn('date', session_data)
            self.assertIn('start_time', session_data)
            self.assertIn('duration_str', session_data)
            self.assertIn('goal', session_data)
            self.assertIn('met_goal', session_data)

    def test_fasting_history_show_next_is_false_for_current_period(self):
        """Test that show_next is False when viewing current period."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=week&date_offset=0')
        self.assertFalse(response.context['show_next'])

    def test_fasting_history_show_next_is_true_for_past_period(self):
        """Test that show_next is True when viewing past period."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url + '?view_type=week&date_offset=-2')
        self.assertTrue(response.context['show_next'])

    def test_fasting_history_calculates_duration_correctly(self):
        """Test that duration is calculated correctly for completed sessions."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        table_data = response.context['table_data']
        # Find a completed session in table data
        for session_data in table_data:
            if not session_data.get('is_active'):
                # Should have a duration string like "16h 0m"
                self.assertIn('h', session_data['duration_str'])
                break

    def test_fasting_history_month_view_year_overflow(self):
        """Test month view handles year overflow."""
        self.client.login(username=self.user.username, password='Password123')
        # Go 12 months back
        response = self.client.get(self.url + '?view_type=month&date_offset=-12')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['view_type'], 'month')

    def test_fasting_history_month_view_year_underflow(self):
        """Test month view handles year underflow when going back many months."""
        self.client.login(username=self.user.username, password='Password123')
        # Go 15 months back (more than a year)
        response = self.client.get(self.url + '?view_type=month&date_offset=-15')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['view_type'], 'month')

    def test_fasting_history_week_view_with_active_session(self):
        """Test week view handles active sessions."""
        self.client.login(username=self.user.username, password='Password123')
        # Create an active session
        FastingSession.objects.create(
            user=self.user,
            start_date_time=timezone.now() - timedelta(hours=5),
            target_duration=16,
            is_active=True
        )
        response = self.client.get(self.url + '?view_type=week')
        self.assertEqual(response.status_code, 200)
        # Active sessions should be in table data
        table_data = response.context['table_data']
        active_sessions = [s for s in table_data if s.get('is_active')]
        self.assertGreaterEqual(len(active_sessions), 1)

