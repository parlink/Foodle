"""Unit tests of the account form."""
from django import forms
from django.test import TestCase
from recipes.forms import AccountForm
from recipes.models import User


class AccountFormTestCase(TestCase):
    """Unit tests of the account form."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
        }

    def test_form_has_necessary_fields(self):
        """Test that form has all required fields."""
        form = AccountForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

    def test_valid_account_form(self):
        """Test that form is valid with correct input."""
        form = AccountForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        """Test that form validates username format."""
        self.form_input['username'] = 'badusername'
        form = AccountForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        """Test that form saves correctly when updating a user."""
        user = User.objects.get(username='@johndoe')
        form = AccountForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        user.refresh_from_db()
        self.assertEqual(user.username, '@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')

    def test_form_rejects_blank_username(self):
        """Test that form rejects blank username."""
        self.form_input['username'] = ''
        form = AccountForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_email(self):
        """Test that form rejects blank email."""
        self.form_input['email'] = ''
        form = AccountForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_email(self):
        """Test that form rejects invalid email format."""
        self.form_input['email'] = 'notanemail'
        form = AccountForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_duplicate_username(self):
        """Test that form rejects duplicate username."""
        # Create another user first
        User.objects.create_user(
            username='@janedoe',
            email='existing@example.org',
            password='Password123!'
        )
        user = User.objects.get(username='@johndoe')
        form = AccountForm(instance=user, data=self.form_input)
        self.assertFalse(form.is_valid())
