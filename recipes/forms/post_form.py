from django import forms
from recipes.models import Post, Tag

class PostForm(forms.ModelForm):
    image = forms.ImageField(
        required=True, 
        label='Recipe Image', 
        widget=forms.FileInput(attrs={'class': 'file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100'})
    )

    class Meta:
        model = Post
        fields = ['title', 'caption', 'image', 'tags', 'prep_time', 'servings', 'difficulty', 'cuisine']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500', 
                'placeholder': 'Give your post a title'
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-control rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500', 
                'rows': 3, 
                'placeholder': 'Share your thoughts...'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500'
            }),
            'prep_time': forms.TextInput(attrs={
                 'class': 'form-control rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500',
                 'placeholder': '25 min'
            }),
            'servings': forms.TextInput(attrs={
                 'class': 'form-control rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500',
                 'placeholder': '4 servings'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500'
            }),
            'cuisine': forms.Select(attrs={
                'class': 'form-control rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500'
            }),
        }