"""Unit tests for the SettingsForm."""
from django.test import TestCase
from recipes.forms import SettingsForm
from recipes.models import User, Profile


class SettingsFormTestCase(TestCase):
    """Unit tests for the SettingsForm."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.form_input = {
            'theme': 'dark',
            'color_blind_mode': 'none',
            'font_scale': 1.0,
        }

    def test_form_has_necessary_fields(self):
        """Test that form has all required fields."""
        form = SettingsForm()
        self.assertIn('theme', form.fields)
        self.assertIn('color_blind_mode', form.fields)
        self.assertIn('font_scale', form.fields)

    def test_valid_settings_form(self):
        """Test that form is valid with correct input."""
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_form_accepts_light_theme(self):
        """Test that form accepts light theme."""
        self.form_input['theme'] = 'light'
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_form_accepts_dark_theme(self):
        """Test that form accepts dark theme."""
        self.form_input['theme'] = 'dark'
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_form_accepts_system_theme(self):
        """Test that form accepts system theme."""
        self.form_input['theme'] = 'system'
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_form_rejects_invalid_theme(self):
        """Test that form rejects invalid theme."""
        self.form_input['theme'] = 'invalid_theme'
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertFalse(form.is_valid())

    def test_form_accepts_all_color_blind_modes(self):
        """Test that form accepts all color blind mode options."""
        valid_modes = ['none', 'protanopia', 'deuteranopia', 'tritanopia', 'achromatopsia']
        for mode in valid_modes:
            self.form_input['color_blind_mode'] = mode
            form = SettingsForm(data=self.form_input, instance=self.profile)
            self.assertTrue(form.is_valid(), f"Form should accept color blind mode: {mode}")

    def test_form_rejects_invalid_color_blind_mode(self):
        """Test that form rejects invalid color blind mode."""
        self.form_input['color_blind_mode'] = 'invalid_mode'
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertFalse(form.is_valid())

    def test_form_accepts_valid_font_scales(self):
        """Test that form accepts valid font scale values."""
        valid_scales = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
        for scale in valid_scales:
            self.form_input['font_scale'] = scale
            form = SettingsForm(data=self.form_input, instance=self.profile)
            self.assertTrue(form.is_valid(), f"Form should accept font scale: {scale}")

    def test_form_rejects_font_scale_below_minimum(self):
        """Test that form rejects font scale below 0.8."""
        self.form_input['font_scale'] = 0.5
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertFalse(form.is_valid())

    def test_form_rejects_font_scale_above_maximum(self):
        """Test that form rejects font scale above 1.5."""
        self.form_input['font_scale'] = 2.0
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertFalse(form.is_valid())

    def test_form_save_updates_profile(self):
        """Test that form save updates the profile."""
        self.form_input['theme'] = 'dark'
        self.form_input['color_blind_mode'] = 'protanopia'
        self.form_input['font_scale'] = 1.2
        
        form = SettingsForm(data=self.form_input, instance=self.profile)
        self.assertTrue(form.is_valid())
        form.save()
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, 'dark')
        self.assertEqual(self.profile.color_blind_mode, 'protanopia')
        self.assertEqual(self.profile.font_scale, 1.2)

    def test_form_has_correct_widgets(self):
        """Test that form fields have correct widget types."""
        form = SettingsForm()
        from django import forms
        self.assertIsInstance(form.fields['theme'].widget, forms.Select)
        self.assertIsInstance(form.fields['color_blind_mode'].widget, forms.Select)
        self.assertIsInstance(form.fields['font_scale'].widget, forms.NumberInput)

    def test_form_excludes_other_profile_fields(self):
        """Test that form only includes settings fields."""
        form = SettingsForm()
        # These fields should NOT be in the form
        self.assertNotIn('calorie_goal', form.fields)
        self.assertNotIn('protein_goal', form.fields)
        self.assertNotIn('fasting_goal', form.fields)
        self.assertNotIn('bio', form.fields)

