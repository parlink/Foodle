import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from recipes.models import Recipe, User
from django.db.models import Q, F
from django.contrib import messages


def parse_total_time_to_minutes(total_time_str: str) -> int:
    if not total_time_str:
        return 0

    s = total_time_str.lower()

    hours = 0
    minutes = 0

    # Look for hours
    match_hours = re.search(r'(\d+)\s*hour', s)
    if match_hours:
        hours = int(match_hours.group(1))

    # Look for minutes
    match_minutes = re.search(r'(\d+)\s*min', s)
    if match_minutes:
        minutes = int(match_minutes.group(1))

    # If we didn't find explicit 'hour' or 'min', just grab the first number as minutes
    if hours == 0 and minutes == 0:
        match_any = re.search(r'(\d+)', s)
        if match_any:
            minutes = int(match_any.group(1))

    return hours * 60 + minutes


@login_required
def my_recipes(request):
    user = request.user
    
    # Get the sorting parameter and check if it's alphabetical
    sort_by = request.GET.get('sort_by', 'name')  # Default to alphabetical sorting by name
    letter_filter = request.GET.get('letter', '')  # Get the letter filter from the query params
    search_query = request.GET.get('q', '').strip()

    recipes_qs = Recipe.objects.filter(created_by=user)

    if search_query:
        recipes_qs = recipes_qs.filter(
            Q(name__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(method__icontains=search_query)
        ).distinct()

    if sort_by == 'time':
        # Apply the complex sorting using your custom function
        recipes = sorted(
            recipes_qs, # Apply sorted() to the filtered queryset!
            key=lambda r: parse_total_time_to_minutes(r.total_time)
        )
    elif sort_by == 'rating':
        recipes = recipes_qs.order_by('-average_rating')
    elif sort_by == 'difficulty':
        recipes = recipes_qs.order_by('difficulty')
    else:

        if letter_filter:
            recipes_qs = recipes_qs.filter(name__istartswith=letter_filter)
        recipes = recipes_qs.order_by('name')
    
    paginator = Paginator(recipes, 12)  # Show 12 recipes per page
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    
    # Create a list of letters for the filter (A-Z)
    alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    return render(request, 'recipes/my_recipes.html', {
        'page': page,
        'alphabet': alphabet,
        'current_letter': letter_filter,  
        'sort_by': sort_by,  
        'search_query': search_query,
    },)


def recipe_detail(request, id):
    recipe = Recipe.objects.get(id=id)
    
    ingredients = [i.strip() for i in recipe.ingredients.split(',') if i.strip()]
    method = [s.strip() for s in recipe.method.split('\n') if s.strip()]
    
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,
        'method': method,
    })

@login_required
def recipe_delete(request, id):
    recipe = get_object_or_404(Recipe, id=id, created_by=request.user)

    if request.method == "POST":
        recipe_name = recipe.name
        recipe.delete()
        messages.success(request, f'Recipe "{recipe_name}" deleted.')

    return redirect("my_recipes")

