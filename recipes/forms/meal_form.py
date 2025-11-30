from django import forms
from recipes.models import Meal


class MealForm(forms.ModelForm):

    """Form for creating and editing meals."""
    
    class Meta:
        model = Meal
        fields = ['name', 'meal_type', 'date', 'calories', 'protein_g', 'carbs_g', 'fat_g']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'protein_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'carbs_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'fat_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
        exclude = ['user']

