"""Tests for the auth forms in recipes/forms/auth_forms.py."""
from django.test import TestCase
from recipes.forms.auth_forms import UserRegisterForm, UserLoginForm
from recipes.models import User


class UserRegisterFormTestCase(TestCase):
    """Tests for the UserRegisterForm."""

    def setUp(self):
        """Set up test data."""
        self.form_input = {
            'username': '@newuser',  # Username must start with @
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        }

    def test_valid_user_register_form(self):
        """Test that valid data creates a valid form."""
        form = UserRegisterForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_user_register_form_has_email_field(self):
        """Test that the form has an email field."""
        form = UserRegisterForm()
        self.assertIn('email', form.fields)

    def test_email_is_required(self):
        """Test that email is required."""
        self.form_input['email'] = ''
        form = UserRegisterForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_email_is_invalid(self):
        """Test that duplicate email raises validation error."""
        User.objects.create_user(
            username='existinguser',
            email='newuser@example.com',
            password='TestPassword123!',
        )
        form = UserRegisterForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('A user with that email already exists.', form.errors['email'])

    def test_clean_email_returns_email_when_unique(self):
        """Test that clean_email returns email when unique."""
        form = UserRegisterForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'newuser@example.com')

    def test_form_saves_user_correctly(self):
        """Test that the form saves a new user correctly."""
        form = UserRegisterForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, '@newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')

    def test_password_mismatch_is_invalid(self):
        """Test that password mismatch makes form invalid."""
        self.form_input['password2'] = 'DifferentPassword123!'
        form = UserRegisterForm(data=self.form_input)
        self.assertFalse(form.is_valid())


class UserLoginFormTestCase(TestCase):
    """Tests for the UserLoginForm."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
        )
        self.form_input = {
            'username': 'testuser',
            'password': 'TestPassword123!',
        }

    def test_valid_login_form(self):
        """Test that valid credentials create a valid form."""
        form = UserLoginForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_login_form_has_username_field(self):
        """Test that the form has a username field."""
        form = UserLoginForm()
        self.assertIn('username', form.fields)

    def test_username_field_has_form_control_class(self):
        """Test that username field has form-control class."""
        form = UserLoginForm()
        self.assertIn('class', form.fields['username'].widget.attrs)
        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-control')

    def test_invalid_credentials(self):
        """Test that invalid credentials make form invalid."""
        self.form_input['password'] = 'WrongPassword!'
        form = UserLoginForm(data=self.form_input)
        self.assertFalse(form.is_valid())
