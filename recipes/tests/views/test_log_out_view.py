"""Tests of the log out view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User
from recipes.tests.helpers import LogInTester


class LogOutViewTestCase(TestCase, LogInTester):
    """Tests of the log out view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.get(username='@johndoe')

    def test_log_out_url(self):
        """Test that log out URL resolves correctly."""
        self.assertEqual(self.url, '/logout/')

    def test_get_log_out(self):
        """Test that logged in user can log out and is redirected to home."""
        self.client.login(username='@johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'welcome.html')
        self.assertFalse(self._is_logged_in())

    def test_get_log_out_without_being_logged_in(self):
        """Test that unauthenticated user accessing logout is redirected to home."""
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'welcome.html')
        self.assertFalse(self._is_logged_in())

    def test_log_out_clears_session(self):
        """Test that logout properly clears the user session."""
        self.client.login(username='@johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())
        self.client.get(self.url)
        self.assertFalse(self._is_logged_in())
