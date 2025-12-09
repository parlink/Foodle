from django.views import generic
from django.urls import reverse_lazy
from recipes.views.decorators import LoginProhibitedMixin
from recipes.forms import SignUpForm

class SignUpView(LoginProhibitedMixin, generic.CreateView):
    """
    Handle new user registration.

    This class-based view displays a registration form for new users and handles
    the creation of their accounts. Authenticated users are automatically
    redirected away using `LoginProhibitedMixin`.
    """
    form_class = SignUpForm
    template_name = 'recipes/auth/signup.html'
    success_url = reverse_lazy('log_in')

    def get_redirect_when_logged_in_url(self):
        """
        Return the URL to redirect to if the user is already logged in.
        Required by LoginProhibitedMixin.
        """
        return reverse_lazy('dashboard')
