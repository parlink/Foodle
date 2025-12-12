"""Tests for authentication forms."""
from django.test import TestCase
from django.core.exceptions import ValidationError
from recipes.forms.auth_forms import UserRegisterForm, UserLoginForm
from recipes.models import User


class UserRegisterFormTestCase(TestCase):
    """Tests for the UserRegisterForm."""

    def setUp(self):
        """Set up test data."""
        self.valid_form_data = {
            'username': '@newuser',
            'email': 'newuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
        }

    def test_form_valid_with_correct_data(self):
        """Test form is valid with correct data."""
        form = UserRegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_email(self):
        """Test form is invalid without email."""
        data = self.valid_form_data.copy()
        data['email'] = ''
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_with_duplicate_email(self):
        """Test form is invalid with duplicate email."""
        User.objects.create_user(
            username='@existing',
            email='existing@example.com',
            password='Password123'
        )
        
        data = self.valid_form_data.copy()
        data['email'] = 'existing@example.com'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_invalid_without_password(self):
        """Test form is invalid without password."""
        data = self.valid_form_data.copy()
        data['password1'] = ''
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_with_mismatched_passwords(self):
        """Test form is invalid with mismatched passwords."""
        data = self.valid_form_data.copy()
        data['password2'] = 'DifferentPassword123!'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_with_weak_password(self):
        """Test form is invalid with weak password."""
        data = self.valid_form_data.copy()
        data['password1'] = 'weak'
        data['password2'] = 'weak'
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_saves_user_correctly(self):
        """Test that form saves user correctly."""
        form = UserRegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, '@newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'Test')

    def test_form_has_email_field(self):
        """Test that form has email field."""
        form = UserRegisterForm()
        self.assertIn('email', form.fields)

    def test_email_field_required(self):
        """Test that email field is required."""
        form = UserRegisterForm()
        self.assertTrue(form.fields['email'].required)

    def test_clean_email_accepts_unique_email(self):
        """Test that clean_email accepts unique email."""
        form = UserRegisterForm(data=self.valid_form_data)
        form.is_valid()
        # Should not raise ValidationError
        self.assertIsNotNone(form.cleaned_data['email'])

    def test_form_invalid_without_username(self):
        """Test form is invalid without username."""
        data = self.valid_form_data.copy()
        data['username'] = ''
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())


class UserLoginFormTestCase(TestCase):
    """Tests for the UserLoginForm."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='@testuser',
            password='Password123!'
        )

    def test_form_has_username_field(self):
        """Test that form has username field."""
        form = UserLoginForm()
        self.assertIn('username', form.fields)

    def test_form_has_password_field(self):
        """Test that form has password field."""
        form = UserLoginForm()
        self.assertIn('password', form.fields)

    def test_form_valid_with_correct_credentials(self):
        """Test form is valid with correct credentials."""
        form = UserLoginForm(data={
            'username': '@testuser',
            'password': 'Password123!'
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_wrong_password(self):
        """Test form is invalid with wrong password."""
        form = UserLoginForm(data={
            'username': '@testuser',
            'password': 'WrongPassword'
        })
        self.assertFalse(form.is_valid())

    def test_form_invalid_with_nonexistent_user(self):
        """Test form is invalid with nonexistent user."""
        form = UserLoginForm(data={
            'username': '@nonexistent',
            'password': 'Password123!'
        })
        self.assertFalse(form.is_valid())

    def test_username_field_has_form_control_class(self):
        """Test that username field has form-control class."""
        form = UserLoginForm()
        widget_attrs = form.fields['username'].widget.attrs
        self.assertIn('class', widget_attrs)
        self.assertIn('form-control', widget_attrs['class'])

    def test_form_label_is_username(self):
        """Test that form label is 'Username'."""
        form = UserLoginForm()
        self.assertEqual(form.fields['username'].label, 'Username')

    def test_form_empty_fields_invalid(self):
        """Test form is invalid with empty fields."""
        form = UserLoginForm(data={
            'username': '',
            'password': ''
        })
        self.assertFalse(form.is_valid())
