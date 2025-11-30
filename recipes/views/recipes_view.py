from django.shortcuts import render
from django.contrib.auth.decorators import login_required

#@login_required
def recipes(request):
    context = {
        'recipes': []  
    }
    return render(request, 'recipes.html', context)

