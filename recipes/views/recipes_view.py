from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe


#login_required
def recipes(request):
    
    recipe_list = Recipe.objects.all()
    paginator = Paginator(recipe_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj 
    }
    return render(request, 'recipes.html', context)

