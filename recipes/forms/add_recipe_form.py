from django import forms
from recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    """Form for creating and editing recipes."""
    
    class Meta:
        model = Recipe
        fields = [
            'name',
            'image',
            'personal_rating',
            'difficulty',
            'total_time',
            'servings',
            'calories',
            'ingredients',
            'method',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipe name'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'personal_rating': forms.HiddenInput(),
            'difficulty': forms.Select(attrs={
                'class': 'form-select'
            }),
            'total_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 min or 1 hour 15 min'
            }),
            'servings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'e.g., 350'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter ingredients, separated by commas\ne.g., 2 cups flour, 1 cup sugar, 3 eggs'
            }),
            'method': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter cooking instructions\nEach line will be a separate step'
            }),
        }
        labels = {
            'name': 'Recipe Name',
            'image': 'Photo',
            'personal_rating': 'Your Rating',
            'difficulty': 'Difficulty',
            'total_time': 'Duration',
            'servings': 'Servings',
            'calories': 'Calories (per serving)',
            'ingredients': 'Ingredients',
            'method': 'Instructions',
        }
        help_texts = {
            'image': 'Upload a photo of your recipe (optional)',
            'ingredients': 'Separate each ingredient with a comma',
            'method': 'Enter each step on a new line',
        }