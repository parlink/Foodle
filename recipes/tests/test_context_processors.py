"""Tests for context processors."""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from recipes.models import User, Profile
from recipes.context_processors import user_profile, user_theme_context


class UserProfileContextProcessorTestCase(TestCase):
    """Tests for the user_profile context processor."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(username='@johndoe')

    def test_returns_empty_context_for_unauthenticated_user(self):
        """Test that context is empty for unauthenticated users."""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        context = user_profile(request)
        self.assertEqual(context, {})

    def test_returns_profile_for_authenticated_user(self):
        """Test that context contains profile for authenticated users."""
        # Ensure profile exists
        Profile.objects.get_or_create(user=self.user)
        request = self.factory.get('/')
        request.user = self.user
        context = user_profile(request)
        self.assertIn('user_profile', context)
        self.assertEqual(context['user_profile'].user, self.user)

    def test_creates_profile_if_not_exists(self):
        """Test that profile is created if it doesn't exist."""
        Profile.objects.filter(user=self.user).delete()
        request = self.factory.get('/')
        request.user = self.user
        context = user_profile(request)
        self.assertIn('user_profile', context)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())


class UserThemeContextProcessorTestCase(TestCase):
    """Tests for the user_theme_context context processor."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(username='@johndoe')

    def test_returns_default_values_for_unauthenticated_user(self):
        """Test default values for unauthenticated users."""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        context = user_theme_context(request)
        self.assertEqual(context['body_classes'], '')
        self.assertEqual(context['body_styles'], '')
        self.assertEqual(context['user_theme'], 'system')

    def test_returns_dark_mode_class_for_dark_theme(self):
        """Test that dark-mode class is returned for dark theme."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.theme = 'dark'
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertIn('dark-mode', context['body_classes'])
        self.assertEqual(context['user_theme'], 'dark')

    def test_no_dark_mode_class_for_light_theme(self):
        """Test that dark-mode class is NOT returned for light theme."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.theme = 'light'
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertNotIn('dark-mode', context['body_classes'])
        self.assertEqual(context['user_theme'], 'light')

    def test_no_dark_mode_class_for_system_theme(self):
        """Test that dark-mode class is NOT added server-side for system theme."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.theme = 'system'
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertNotIn('dark-mode', context['body_classes'])
        self.assertEqual(context['user_theme'], 'system')

    def test_returns_color_blind_class(self):
        """Test that color blind mode class is returned."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.color_blind_mode = 'protanopia'
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertIn('cb-protanopia', context['body_classes'])

    def test_no_color_blind_class_when_none(self):
        """Test that no color blind class is added when mode is 'none'."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.color_blind_mode = 'none'
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertNotIn('cb-', context['body_classes'])

    def test_returns_font_scale_style(self):
        """Test that font scale style is returned."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.font_scale = 1.2
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertEqual(context['body_styles'], 'font-size: 1.2rem;')

    def test_no_font_scale_style_when_default(self):
        """Test that no font scale style is added when scale is 1.0."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.font_scale = 1.0
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertEqual(context['body_styles'], '')

    def test_creates_profile_if_not_exists(self):
        """Test that profile is created if it doesn't exist."""
        Profile.objects.filter(user=self.user).delete()
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(context['user_theme'], 'system')  # Default

    def test_multiple_classes_combined(self):
        """Test that multiple classes are combined properly."""
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.theme = 'dark'
        profile.color_blind_mode = 'deuteranopia'
        profile.save()
        
        request = self.factory.get('/')
        request.user = self.user
        context = user_theme_context(request)
        self.assertIn('dark-mode', context['body_classes'])
        self.assertIn('cb-deuteranopia', context['body_classes'])

