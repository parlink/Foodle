from django import forms
from recipes.models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'name',
            'difficulty',
            'total_time',
            'servings',
            'ingredients',
            'method',
            'image',
            'image_url',
        ]
        widgets = {
            'ingredients': forms.Textarea(attrs={'rows': 4}),
            'method': forms.Textarea(attrs={'rows': 6}),
        }