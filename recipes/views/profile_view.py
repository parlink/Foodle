from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView
from django.urls import reverse
from recipes.forms import AccountForm, ProfileForm, PasswordForm
from recipes.models import Post, Follow


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    """
    Allow authenticated users to view and update their profile information.

    This class-based view displays a user profile editing form with tabs for
    Public Profile, Account Settings, and Security. It handles updates to
    both profile information and password changes. Access is restricted to
    logged-in users via `LoginRequiredMixin`.
    """

    template_name = "recipes/profile.html"

    def get_context_data(self, **kwargs):
        """Add profile forms and stats to the context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Calculate stats
        context['posts_count'] = Post.objects.filter(author=user).count()
        context['followers_count'] = Follow.objects.filter(followed=user).count()
        context['following_count'] = Follow.objects.filter(follower=user).count()
        
        # Initialize forms
        context['profile_form'] = ProfileForm(instance=user)
        context['account_form'] = AccountForm(instance=user)
        context['password_form'] = PasswordForm(user=user)
        
        return context

    def post(self, request, *args, **kwargs):
        """Handle form submissions."""
        user = request.user
        action = request.POST.get('action')
        
        if action == 'update_profile':
            profile_form = ProfileForm(request.POST, request.FILES, instance=user)
            account_form = AccountForm(instance=user)
            password_form = PasswordForm(user=user)
            
            if profile_form.is_valid():
                profile_instance = profile_form.save(commit=False)
                # If profile_picture wasn't uploaded, preserve the existing one
                if 'profile_picture' not in request.FILES and not request.POST.get('profile_picture-clear'):
                    profile_instance.profile_picture = user.profile_picture
                profile_instance.save()
                messages.success(request, "Profile updated successfully!")
                return self.get(request)
            else:
                messages.error(request, "There was an error with your submission. Please correct the errors below.")
                # Recalculate stats for context
                context = self.get_context_data()
                context['profile_form'] = profile_form
                context['account_form'] = account_form
                context['password_form'] = password_form
                return self.render_to_response(context)
        
        elif action == 'update_account':
            account_form = AccountForm(request.POST, instance=user)
            profile_form = ProfileForm(instance=user)
            password_form = PasswordForm(user=user)
            
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "Account settings updated successfully!")
                return self.get(request)
            else:
                messages.error(request, "There was an error with your submission. Please correct the errors below.")
                # Recalculate stats for context
                context = self.get_context_data()
                context['profile_form'] = profile_form
                context['account_form'] = account_form
                context['password_form'] = password_form
                return self.render_to_response(context)
        
        elif action == 'change_password':
            password_form = PasswordForm(user=user, data=request.POST)
            profile_form = ProfileForm(instance=user)
            account_form = AccountForm(instance=user)
            
            if password_form.is_valid():
                password_form.save()
                # Update session auth hash so user isn't logged out
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully!")
                return self.get(request)
            else:
                messages.error(request, "There was an error with your submission. Please correct the errors below.")
                # Recalculate stats for context
                context = self.get_context_data()
                context['profile_form'] = profile_form
                context['account_form'] = account_form
                context['password_form'] = password_form
                return self.render_to_response(context)
        
        # Default: just render the page
        return self.get(request)