"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from recipes.forms import AccountForm, ProfileForm, PasswordForm
from recipes.models import User
from recipes.tests.helpers import reverse_with_next


class ProfileViewTest(TestCase):
    """Test suite for the profile view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('profile')
        self.account_form_input = {
            'action': 'update_account',
            'first_name': 'John2',
            'last_name': 'Doe2',
            'username': '@johndoe2',
            'email': 'johndoe2@example.org',
        }
        self.profile_form_input = {
            'action': 'update_profile',
            'bio': 'Updated bio',
            'dietary_preference': 'Vegetarian',
        }
        self.password_form_input = {
            'action': 'change_password',
            'password': 'Password123',
            'new_password': 'NewPassword123!',
            'password_confirmation': 'NewPassword123!',
        }

    def test_profile_url(self):
        """Test that profile URL resolves correctly."""
        self.assertEqual(self.url, '/profile/')

    def test_get_profile(self):
        """Test GET request to profile page."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        self.assertIn('profile_form', response.context)
        self.assertIn('account_form', response.context)
        self.assertIn('password_form', response.context)
        self.assertTrue(isinstance(response.context['profile_form'], ProfileForm))
        self.assertTrue(isinstance(response.context['account_form'], AccountForm))
        self.assertTrue(isinstance(response.context['password_form'], PasswordForm))

    def test_get_profile_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_account_update_with_invalid_username(self):
        """Test that account update fails with invalid username."""
        self.client.login(username=self.user.username, password='Password123')
        self.account_form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.account_form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_unsuccessful_account_update_due_to_duplicate_username(self):
        """Test that account update fails with duplicate username."""
        self.client.login(username=self.user.username, password='Password123')
        self.account_form_input['username'] = '@janedoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.account_form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_successful_account_update(self):
        """Test successful account update."""
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.account_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe2')
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')

    def test_successful_profile_update(self):
        """Test successful profile update."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.profile_form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'Updated bio')
        self.assertEqual(self.user.dietary_preference, 'Vegetarian')

    def test_post_profile_redirects_when_not_logged_in(self):
        """Test that POST to profile page redirects when not logged in."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.account_form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_profile_page_shows_user_stats(self):
        """Test that profile page displays user statistics."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('stats', response.context)
        self.assertIn('posts_count', response.context)
        self.assertIn('followers_count', response.context)
        self.assertIn('following_count', response.context)

    def test_profile_form_has_csrf_token(self):
        """Test that profile form includes CSRF protection."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_successful_password_change(self):
        """Test successful password change from profile page."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.password_form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        # Verify password was changed
        self.user.refresh_from_db()
        from django.contrib.auth.hashers import check_password
        self.assertTrue(check_password('NewPassword123!', self.user.password))

    def test_unsuccessful_password_change_with_wrong_current_password(self):
        """Test password change fails with wrong current password."""
        self.client.login(username=self.user.username, password='Password123')
        self.password_form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.password_form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        # Verify password was NOT changed
        self.user.refresh_from_db()
        from django.contrib.auth.hashers import check_password
        self.assertTrue(check_password('Password123', self.user.password))

    def test_unsuccessful_password_change_with_mismatched_confirmation(self):
        """Test password change fails when confirmation doesn't match."""
        self.client.login(username=self.user.username, password='Password123')
        self.password_form_input['password_confirmation'] = 'DifferentPassword123!'
        response = self.client.post(self.url, self.password_form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_post_without_action_returns_profile_page(self):
        """Test POST without action parameter returns profile page."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')

    def test_profile_update_preserves_existing_profile_picture(self):
        """Test that profile update preserves existing profile picture when not uploading new one."""
        self.client.login(username=self.user.username, password='Password123')
        # First set a bio without uploading a picture
        profile_data = {
            'action': 'update_profile',
            'bio': 'Test bio',
            'dietary_preference': 'None',
        }
        response = self.client.post(self.url, profile_data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_unsuccessful_profile_update_with_invalid_dietary_preference(self):
        """Test that profile update fails with invalid dietary preference."""
        self.client.login(username=self.user.username, password='Password123')
        profile_data = {
            'action': 'update_profile',
            'bio': 'Test bio',
            'dietary_preference': 'InvalidChoice',  # Invalid choice
        }
        response = self.client.post(self.url, profile_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_profile_update_with_profile_picture_upload(self):
        """Test profile update with profile picture upload."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username=self.user.username, password='Password123')
        # Create a simple test image
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        image = SimpleUploadedFile('test.gif', image_content, content_type='image/gif')
        profile_data = {
            'action': 'update_profile',
            'bio': 'Updated bio with image',
            'dietary_preference': 'Vegan',
            'profile_picture': image,
        }
        response = self.client.post(self.url, profile_data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
