"""Unit tests for the Profile model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipes.models import User, Profile


class ProfileModelTestCase(TestCase):
    """Unit tests for the Profile model."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        # Delete any existing profile to test creation
        Profile.objects.filter(user=self.user).delete()

    def test_create_profile(self):
        """Test creating a profile with default values."""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.theme, 'light')
        self.assertEqual(profile.color_blind_mode, 'none')
        self.assertEqual(profile.font_scale, 1.0)

    def test_profile_str_representation(self):
        """Test profile string representation."""
        profile = Profile.objects.create(user=self.user)
        expected_str = f"{self.user.username}'s profile"
        self.assertEqual(str(profile), expected_str)

    def test_profile_default_nutritional_goals(self):
        """Test default nutritional goal values."""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.calorie_goal, 2000)
        self.assertEqual(profile.protein_goal, 150)
        self.assertEqual(profile.carbs_goal, 250)
        self.assertEqual(profile.fat_goal, 70)

    def test_profile_default_fasting_goal(self):
        """Test default fasting goal."""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.fasting_goal, 16)

    def test_profile_theme_choices(self):
        """Test all valid theme choices."""
        profile = Profile.objects.create(user=self.user)
        for theme, _ in Profile.THEME_CHOICES:
            profile.theme = theme
            profile.save()
            profile.refresh_from_db()
            self.assertEqual(profile.theme, theme)

    def test_profile_color_blind_mode_choices(self):
        """Test all valid color blind mode choices."""
        profile = Profile.objects.create(user=self.user)
        for mode, _ in Profile.COLOR_BLIND_CHOICES:
            profile.color_blind_mode = mode
            profile.save()
            profile.refresh_from_db()
            self.assertEqual(profile.color_blind_mode, mode)

    def test_profile_fasting_goal_choices(self):
        """Test all valid fasting goal choices."""
        profile = Profile.objects.create(user=self.user)
        for hours, _ in Profile.FASTING_CHOICES:
            profile.fasting_goal = hours
            profile.save()
            profile.refresh_from_db()
            self.assertEqual(profile.fasting_goal, hours)

    def test_font_scale_minimum_validation(self):
        """Test that font_scale cannot be below minimum."""
        profile = Profile.objects.create(user=self.user, font_scale=0.5)
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_font_scale_maximum_validation(self):
        """Test that font_scale cannot be above maximum."""
        profile = Profile.objects.create(user=self.user, font_scale=2.0)
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_font_scale_valid_range(self):
        """Test that font_scale accepts valid values."""
        profile = Profile.objects.create(user=self.user)
        valid_scales = [0.8, 1.0, 1.2, 1.5]
        for scale in valid_scales:
            profile.font_scale = scale
            profile.full_clean()  # Should not raise

    def test_profile_units_preference_choices(self):
        """Test all valid units preference choices."""
        profile = Profile.objects.create(user=self.user)
        for units, _ in Profile.UNIT_CHOICES:
            profile.units_preference = units
            profile.save()
            profile.refresh_from_db()
            self.assertEqual(profile.units_preference, units)

    def test_profile_privacy_defaults(self):
        """Test default privacy settings."""
        profile = Profile.objects.create(user=self.user)
        self.assertTrue(profile.is_profile_public)
        self.assertTrue(profile.show_stats_publicly)

    def test_profile_notification_defaults(self):
        """Test default notification settings."""
        profile = Profile.objects.create(user=self.user)
        self.assertTrue(profile.email_weekly_summary)
        self.assertFalse(profile.email_follower_notifications)
        self.assertFalse(profile.reminder_log_meals)
        self.assertIsNone(profile.reminder_time)

    def test_profile_bio_blank_by_default(self):
        """Test that bio is blank by default."""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.bio, '')

    def test_profile_one_to_one_with_user(self):
        """Test that profile has one-to-one relationship with user."""
        profile = Profile.objects.create(user=self.user)
        # Try to create another profile for the same user
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user)

