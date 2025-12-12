from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe


def parse_time_to_minutes(time_string):
    """Parse time string like '25 minutes', '1 hour 30 minutes', '45 minutes' to total minutes.
    Returns None if parsing fails.
    """
    if not time_string:
        return None
    
    total_minutes = 0
    time_string = time_string.lower().strip()
    words = time_string.split()

    # either x minutes or x hours form
    if len(words) == 2:
        if words[1] == 'minutes':
            return int(words[0])
        elif words[1] == 'hours':
            return int(words[0]) * 60
    
    # x hours y minutes form
    if len(words) == 4: 
        if words[1] == 'hours' and words[3] == 'minutes':
            return int(words[0]) * 60 + int(words[2])

    return None

#login_required
def recipes(request):
    sort_by = request.GET.get('sort_by', '')
    recipe_list = Recipe.objects.all()

    if sort_by == 'quick-meals':
        quick_recipes = []
        for recipe in recipe_list:
            minutes = parse_time_to_minutes(recipe.total_time)
            if minutes and minutes <= 30:
                quick_recipes.append(recipe.id)
        recipe_list = Recipe.objects.filter(id__in=quick_recipes)
    
    elif sort_by == 'servings':
        recipe_list = Recipe.objects.all().order_by('-servings')
    elif sort_by == 'rating':
        recipe_list = Recipe.objects.all().order_by('-average_rating')
    else:
        recipe_list = Recipe.objects.all()

    paginator = Paginator(recipe_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'active_sort': sort_by
    }
    return render(request, 'recipes.html', context)

