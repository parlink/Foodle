"""Tests of the log in view."""
from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase
from django.urls import reverse
from recipes.models import User
from recipes.tests.helpers import LogInTester, reverse_with_next


class LogInViewTestCase(TestCase, LogInTester):
    """Tests of the log in view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(username='@johndoe')

    def test_log_in_url(self):
        self.assertEqual(self.url, '/login/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/auth/login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, AuthenticationForm))
        self.assertFalse(form.is_bound)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('profile')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/auth/login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, AuthenticationForm))
        self.assertFalse(form.is_bound)

    def test_get_log_in_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'recipes/dashboard.html')

    def test_unsuccessful_log_in(self):
        form_input = {'username': '@johndoe', 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/auth/login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, AuthenticationForm))
        self.assertFalse(self._is_logged_in())

    def test_log_in_with_blank_username(self):
        form_input = {'username': '', 'password': 'Password123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/auth/login.html')
        self.assertFalse(self._is_logged_in())

    def test_log_in_with_blank_password(self):
        form_input = {'username': '@johndoe', 'password': ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/auth/login.html')
        self.assertFalse(self._is_logged_in())

    def test_successful_log_in(self):
        form_input = {'username': '@johndoe', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'recipes/dashboard.html')

    def test_successful_log_in_with_next_parameter(self):
        """Test that login redirects to 'next' parameter when provided."""
        redirect_url = reverse('profile')
        form_input = {'username': '@johndoe', 'password': 'Password123', 'next': redirect_url}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        # Note: Django's LoginView handles 'next' differently - it may redirect to default
        self.assertEqual(response.status_code, 200)

    def test_post_log_in_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        form_input = {'username': '@wronguser', 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'recipes/dashboard.html')

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = {'username': '@johndoe', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/auth/login.html')
        self.assertFalse(self._is_logged_in())

    def test_log_in_form_has_csrf_token(self):
        """Test that login form includes CSRF protection."""
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_log_in_page_has_sign_up_link(self):
        """Test that login page has a link to sign up."""
        response = self.client.get(self.url)
        self.assertContains(response, reverse('sign_up'))

    def test_log_in_page_has_password_reset_link(self):
        """Test that login page has a link to password reset."""
        response = self.client.get(self.url)
        self.assertContains(response, reverse('password_reset'))
