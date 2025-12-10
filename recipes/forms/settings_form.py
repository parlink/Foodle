from django import forms
from recipes.models import Profile


class SettingsForm(forms.ModelForm):
    """Form for updating user settings (theme, accessibility, font scaling)."""
    
    class Meta:
        model = Profile
        fields = ['theme', 'color_blind_mode', 'font_scale']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'color_blind_mode': forms.Select(attrs={'class': 'form-select'}),
            'font_scale': forms.NumberInput(attrs={
                'class': 'form-range',
                'type': 'range',
                'min': '0.8',
                'max': '1.5',
                'step': '0.1',
            }),
        }
        labels = {
            'theme': 'Theme',
            'color_blind_mode': 'Color Blind Mode',
            'font_scale': 'Font Scale',
        }
        help_texts = {
            'theme': 'Choose between light and dark theme.',
            'color_blind_mode': 'Apply color filters for color vision deficiencies.',
            'font_scale': 'Adjust font size (0.8x to 1.5x).',
        }

