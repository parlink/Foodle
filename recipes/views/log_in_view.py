from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from recipes.views.decorators import LoginProhibitedMixin
from recipes.forms import UserLoginForm

class LogInView(LoginProhibitedMixin, auth_views.LoginView):
    """
    Handle user login requests.

    This class-based view displays a login form for unauthenticated users
    and processes login submissions. Authenticated users are redirected
    away automatically via `LoginProhibitedMixin`.
    """
    form_class = UserLoginForm
    template_name = 'recipes/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

    def get_redirect_when_logged_in_url(self):
        """
        Return the URL to redirect to if the user is already logged in.
        Required by LoginProhibitedMixin.
        """
        return self.get_success_url()
