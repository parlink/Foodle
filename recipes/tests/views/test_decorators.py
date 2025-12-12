"""Tests of the view decorators."""
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from recipes.models import User
from recipes.views.decorators import login_prohibited, LoginProhibitedMixin


class LoginProhibitedDecoratorTestCase(TestCase):
    """Tests for the login_prohibited decorator."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(username='@johndoe')

    def test_unauthenticated_user_can_access_decorated_view(self):
        """Test that unauthenticated users can access the view."""
        @login_prohibited
        def sample_view(request):
            from django.http import HttpResponse
            return HttpResponse("Success")
        
        request = self.factory.get('/')
        request.user = AnonymousUser()
        response = sample_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Success")

    def test_authenticated_user_is_redirected_from_decorated_view(self):
        """Test that authenticated users are redirected away from the view."""
        @login_prohibited
        def sample_view(request):
            from django.http import HttpResponse
            return HttpResponse("Success")
        
        request = self.factory.get('/')
        request.user = self.user
        response = sample_view(request)
        self.assertEqual(response.status_code, 302)


class LoginProhibitedMixinTestCase(TestCase):
    """Tests for the LoginProhibitedMixin."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

    def test_login_prohibited_throws_exception_when_not_configured(self):
        """Test that mixin raises error when redirect URL not configured."""
        mixin = LoginProhibitedMixin()
        with self.assertRaises(ImproperlyConfigured):
            mixin.get_redirect_when_logged_in_url()

    def test_login_prohibited_returns_url_when_configured(self):
        """Test that mixin returns URL when redirect_when_logged_in_url is set."""
        mixin = LoginProhibitedMixin()
        mixin.redirect_when_logged_in_url = '/dashboard/'
        result = mixin.get_redirect_when_logged_in_url()
        self.assertEqual(result, '/dashboard/')
