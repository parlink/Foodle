"""Tests for the settings view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
import json
from recipes.models import User, Profile
from recipes.forms import SettingsForm
from recipes.tests.helpers import reverse_with_next


class SettingsViewTestCase(TestCase):
    """Tests for the settings view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('settings')
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.form_input = {
            'theme': 'dark',
            'color_blind_mode': 'none',
            'font_scale': 1.0,
        }

    def test_settings_url(self):
        """Test that settings URL resolves correctly."""
        self.assertEqual(self.url, '/settings/')

    def test_get_settings_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_settings_when_logged_in(self):
        """Test GET request to settings page when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/settings.html')
        self.assertIn('settings_form', response.context)
        self.assertTrue(isinstance(response.context['settings_form'], SettingsForm))

    def test_settings_creates_profile_if_not_exists(self):
        """Test that settings view creates profile if it doesn't exist."""
        Profile.objects.filter(user=self.user).delete()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_successful_settings_update(self):
        """Test successful settings update via POST."""
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['theme'] = 'dark'
        self.form_input['color_blind_mode'] = 'protanopia'
        self.form_input['font_scale'] = 1.2
        
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, 'dark')
        self.assertEqual(self.profile.color_blind_mode, 'protanopia')
        self.assertEqual(self.profile.font_scale, 1.2)

    def test_successful_settings_update_shows_success_message(self):
        """Test that successful update shows success message."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_unsuccessful_settings_update(self):
        """Test unsuccessful settings update with invalid data."""
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['font_scale'] = 2.5  # Invalid - too high
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_ajax_successful_settings_update(self):
        """Test successful AJAX settings update."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            self.form_input,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['theme'], 'dark')

    def test_ajax_unsuccessful_settings_update(self):
        """Test unsuccessful AJAX settings update."""
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['font_scale'] = 2.5  # Invalid
        response = self.client.post(
            self.url,
            self.form_input,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

    def test_settings_update_to_light_theme(self):
        """Test updating to light theme."""
        self.client.login(username=self.user.username, password='Password123')
        self.profile.theme = 'dark'
        self.profile.save()
        
        self.form_input['theme'] = 'light'
        self.client.post(self.url, self.form_input)
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, 'light')

    def test_settings_update_to_system_theme(self):
        """Test updating to system theme."""
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['theme'] = 'system'
        self.client.post(self.url, self.form_input)
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, 'system')

    def test_settings_update_color_blind_modes(self):
        """Test updating various color blind modes."""
        self.client.login(username=self.user.username, password='Password123')
        modes = ['protanopia', 'deuteranopia', 'tritanopia', 'achromatopsia', 'none']
        
        for mode in modes:
            self.form_input['color_blind_mode'] = mode
            self.client.post(self.url, self.form_input)
            self.profile.refresh_from_db()
            self.assertEqual(self.profile.color_blind_mode, mode)

    def test_settings_form_has_csrf_token(self):
        """Test that settings form includes CSRF protection."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_post_settings_redirects_when_not_logged_in(self):
        """Test that POST to settings redirects when not logged in."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

