from django import forms
from recipes.models import Post

class PostForm(forms.ModelForm):
    #Form for creating social feed posts.

    class Meta:
        model = Post
        fields = ['title', 'caption', 'tags']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Give your post a title'
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Share your thoughts...'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
        }