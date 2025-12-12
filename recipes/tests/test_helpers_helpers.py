"""Tests for test helpers."""
from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import User
from recipes.tests.helpers import reverse_with_next, LogInTester


class ReverseWithNextTestCase(TestCase):
    """Tests for reverse_with_next helper function."""

    def test_reverse_with_next_adds_next_parameter(self):
        """Test that reverse_with_next adds next parameter."""
        url = reverse_with_next('log_in', '/feed/')
        self.assertIn('?next=/feed/', url)

    def test_reverse_with_next_base_url_correct(self):
        """Test that base URL is correct."""
        url = reverse_with_next('log_in', '/feed/')
        self.assertTrue(url.startswith('/login/'))

    def test_reverse_with_next_with_empty_next(self):
        """Test reverse_with_next with empty next URL."""
        url = reverse_with_next('log_in', '')
        self.assertIn('?next=', url)

    def test_reverse_with_next_with_different_urls(self):
        """Test reverse_with_next with different URL names."""
        password_url = reverse_with_next('password', '/feed/')
        profile_url = reverse_with_next('profile', '/feed/')
        
        self.assertIn('?next=/feed/', password_url)
        self.assertIn('?next=/feed/', profile_url)
        self.assertNotEqual(password_url, profile_url)

    def test_reverse_with_next_with_long_path(self):
        """Test reverse_with_next with long next path."""
        long_path = '/recipes/123/edit/?sort=rating&filter=vegetarian'
        url = reverse_with_next('log_in', long_path)
        self.assertIn(long_path, url)


class LogInTesterTestCase(TestCase, LogInTester):
    """Tests for LogInTester helper class."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test client."""
        self.user = User.objects.get(username='@johndoe')

    def test_is_logged_in_returns_false_when_not_logged_in(self):
        """Test that _is_logged_in returns False when user is not logged in."""
        self.assertFalse(self._is_logged_in())

    def test_is_logged_in_returns_true_when_logged_in(self):
        """Test that _is_logged_in returns True when user is logged in."""
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())

    def test_is_logged_in_after_logout(self):
        """Test that _is_logged_in returns False after logout."""
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        
        self.client.logout()
        self.assertFalse(self._is_logged_in())

    def test_session_key_present_when_logged_in(self):
        """Test that session contains auth user ID when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        self.assertIn('_auth_user_id', self.client.session.keys())

    def test_session_key_absent_when_not_logged_in(self):
        """Test that session doesn't contain auth user ID when not logged in."""
        self.assertNotIn('_auth_user_id', self.client.session.keys())
