from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe

#login_required
def recipes(request):
    context = {
        'recipes': Recipe.objects.all()
    }
    return render(request, 'recipes.html', context)

