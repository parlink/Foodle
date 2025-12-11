from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from recipes.models import Recipe, User

@login_required
def my_recipes(request):
    user = request.user
    
    # Get the sorting parameter and check if it's alphabetical
    sort_by = request.GET.get('sort_by', 'name')  # Default to alphabetical sorting by name
    letter_filter = request.GET.get('letter', '')  # Get the letter filter from the query params
    
    if sort_by == 'rating':
        recipes = Recipe.objects.filter(created_by=user).order_by('-average_rating')
    elif sort_by == 'difficulty':
        recipes = Recipe.objects.filter(created_by=user).order_by('difficulty')
    elif sort_by == 'time':
        recipes = Recipe.objects.filter(created_by=user).order_by('total_time')
    else:
        # If sorting by name, handle the letter filter
        if letter_filter:
            recipes = Recipe.objects.filter(created_by=user, name__istartswith=letter_filter).order_by('name')
        else:
            recipes = Recipe.objects.filter(created_by=user).order_by('name')
    
    paginator = Paginator(recipes, 12)  # Show 12 recipes per page
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    
    # Create a list of letters for the filter (A-Z)
    alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    return render(request, 'recipes/my_recipes.html', {
        'page': page,
        'alphabet': alphabet,
        'current_letter': letter_filter,  # To highlight the current letter in the banner
        'sort_by': sort_by,  # Pass the current sorting method to the template
    })


def recipe_detail(request, id):
    recipe = Recipe.objects.get(id=id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})
