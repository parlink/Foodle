"""Tests of the welcome/home view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User


class WelcomeViewTestCase(TestCase):
    """Tests of the welcome/home view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(username='@johndoe')

    def test_home_url(self):
        """Test that home URL resolves to '/'."""
        self.assertEqual(self.url, '/')

    def test_get_welcome_page(self):
        """Test that unauthenticated users see the welcome page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'welcome.html')

    def test_get_welcome_redirects_when_logged_in(self):
        """Test that authenticated users are redirected to dashboard."""
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'recipes/dashboard.html')

    def test_welcome_page_contains_login_link(self):
        """Test that welcome page has a link to login."""
        response = self.client.get(self.url)
        self.assertContains(response, reverse('log_in'))

    def test_welcome_page_contains_signup_link(self):
        """Test that welcome page has a link to sign up."""
        response = self.client.get(self.url)
        self.assertContains(response, reverse('sign_up'))

    def test_welcome_page_contains_branding(self):
        """Test that welcome page displays Foodle branding."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Foodle')

    def test_welcome_page_contains_features_section(self):
        """Test that welcome page displays features information."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Features')

    def test_welcome_page_contains_socials_section(self):
        """Test that welcome page displays socials information."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Socials')

    def test_welcome_page_contains_get_started_button(self):
        """Test that welcome page has a Get Started button."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Get Started')

    def test_welcome_page_extends_base_template(self):
        """Test that welcome page extends base.html."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'base.html')
