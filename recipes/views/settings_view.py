from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from recipes.forms import SettingsForm
from recipes.models import Profile


class SettingsView(LoginRequiredMixin, TemplateView):
    """
    View for managing user settings (theme, accessibility, font scaling).
    
    This view allows authenticated users to update their display preferences
    including dark mode, color blind mode, and font scaling.
    Access is restricted to logged-in users via `LoginRequiredMixin`.
    """
    
    template_name = "recipes/settings.html"
    
    def get_context_data(self, **kwargs):
        """Add settings form to the context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create profile for the user
        profile, _ = Profile.objects.get_or_create(user=user)
        context['settings_form'] = SettingsForm(instance=profile)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission to update settings (supports AJAX)."""
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        settings_form = SettingsForm(request.POST, instance=profile)
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if settings_form.is_valid():
            settings_form.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Settings saved!',
                    'theme': profile.theme,
                    'color_blind_mode': profile.color_blind_mode,
                    'font_scale': float(profile.font_scale),
                })
            else:
                messages.success(request, "Settings updated successfully!")
                return self.get(request)
        else:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Error saving settings.',
                    'errors': settings_form.errors,
                }, status=400)
            else:
                messages.error(request, "There was an error with your submission.")
                context = self.get_context_data()
                context['settings_form'] = settings_form
                return self.render_to_response(context)

