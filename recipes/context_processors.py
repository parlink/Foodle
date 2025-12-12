from django.core.exceptions import ObjectDoesNotExist
from recipes.models import Profile


def user_profile(request):
    """Context processor to safely provide user profile settings."""
    context = {}
    if request.user.is_authenticated:
        try:
            context['user_profile'] = request.user.profile
        except ObjectDoesNotExist:
            # Profile doesn't exist yet, create it with defaults
            context['user_profile'] = Profile.objects.create(user=request.user)
    return context


def user_theme_context(request):
    """
    Context processor to provide theme-related classes and styles for the body tag.
    
    Returns:
        dict: Contains 'body_classes' (space-separated CSS classes),
              'body_styles' (inline CSS styles string), and
              'user_theme' (the user's theme preference: 'system', 'light', or 'dark').
    """
    body_classes = []
    body_styles = ""
    user_theme = "light"  # Default for non-authenticated users
    
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except ObjectDoesNotExist:
            # Profile doesn't exist yet, create it with defaults
            profile = Profile.objects.create(user=request.user)
        
        user_theme = profile.theme
        
        # Build classes list - only add dark-mode if explicitly set (not system)
        if profile.theme == 'dark':
            body_classes.append('dark-mode')
        
        if profile.color_blind_mode != 'none':
            body_classes.append(f'cb-{profile.color_blind_mode}')
        
        # Build styles string
        if profile.font_scale != 1.0:
            body_styles = f"font-size: {profile.font_scale}rem;"
    
    return {
        'body_classes': ' '.join(body_classes),
        'body_styles': body_styles,
        'user_theme': user_theme,
    }
