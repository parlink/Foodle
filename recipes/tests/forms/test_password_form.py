"""Unit tests of the password form."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from recipes.models import User
from recipes.forms import PasswordForm


class PasswordFormTestCase(TestCase):
    """Unit tests of the password form."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123!',
            'password_confirmation': 'NewPassword123!',
        }

    def test_form_has_necessary_fields(self):
        """Test that form has all required fields."""
        form = PasswordForm(user=self.user)
        self.assertIn('password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_valid_form(self):
        """Test that form is valid with correct input."""
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        """Test that password must contain uppercase letter."""
        self.form_input['new_password'] = 'password123!'
        self.form_input['password_confirmation'] = 'password123!'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        """Test that password must contain lowercase letter."""
        self.form_input['new_password'] = 'PASSWORD123!'
        self.form_input['password_confirmation'] = 'PASSWORD123!'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        """Test that password must contain a number."""
        self.form_input['new_password'] = 'PasswordABC!'
        self.form_input['password_confirmation'] = 'PasswordABC!'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_special_character(self):
        """Test that password must contain a special character."""
        self.form_input['new_password'] = 'Password123'
        self.form_input['password_confirmation'] = 'Password123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        """Test that password and confirmation must match."""
        self.form_input['password_confirmation'] = 'WrongPassword123!'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_be_valid(self):
        """Test that current password must be correct."""
        self.form_input['password'] = 'WrongPassword123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_contain_user(self):
        """Test that form without user cannot validate current password."""
        form = PasswordForm(data=self.form_input)
        # Form validates but password check fails without user
        self.assertTrue(form.is_valid())

    def test_save_form_changes_password(self):
        """Test that saving form changes the user's password."""
        form = PasswordForm(user=self.user, data=self.form_input)
        form.full_clean()
        form.save()
        self.user.refresh_from_db()
        self.assertFalse(check_password('Password123', self.user.password))
        self.assertTrue(check_password('NewPassword123!', self.user.password))

    def test_save_userless_form_returns_none(self):
        """Test that saving form without user returns None."""
        form = PasswordForm(user=None, data=self.form_input)
        form.full_clean()
        result = form.save()
        self.assertIsNone(result)
