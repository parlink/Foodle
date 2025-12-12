from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe
from django.db.models import Q


# Base recipe names to exclude from browse page (only show user-created recipes)
BASE_RECIPE_NAMES = [
    'Classic Margherita Pizza', 'Grilled Salmon with Lemon', 'Chocolate Chip Cookies',
    'Caesar Salad', 'Chicken Curry', 'Spaghetti Carbonara', 'Beef Burger',
    'Chocolate Brownies', 'Chicken Stir Fry', 'French Onion Soup', 'Pad Thai',
    'Beef Steak', 'Chicken Wings', 'Vegetable Lasagna',
]


def parse_time_to_minutes(time_string):
    """Parse time string like '25 minutes', '15 min', '1 hour 30 minutes', '1 hour 30 min' to total minutes.
    Returns None if parsing fails.
    """
    if not time_string:
        return None
    
    try:
        total_minutes = 0
        time_string = time_string.lower().strip()
        words = time_string.split()

        # either x minutes/min or x hours/hour form
        if len(words) == 2:
            if words[1] in ['minutes', 'min']:
                return int(words[0])
            elif words[1] in ['hours', 'hour']:
                return int(words[0]) * 60
        
        # x hours/hour y minutes/min form
        if len(words) == 4: 
            if words[1] in ['hours', 'hour'] and words[3] in ['minutes', 'min']:
                return int(words[0]) * 60 + int(words[2])

        return None
    except (ValueError, IndexError):
        return None

#login_required
def recipes(request):
    sort_by = request.GET.get('sort_by', '')
    # Exclude base recipes - only show user-created recipes
    recipe_list = Recipe.objects.exclude(name__in=BASE_RECIPE_NAMES)
    search_query = request.GET.get('q', '')

    if search_query:
        recipe_list = recipe_list.filter(
            Q(name__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(method__icontains=search_query)
        ).distinct()

    if sort_by == 'quick-meals':
        # Filter recipes under 30 minutes and sort by time (fastest first)
        # Convert queryset to list to iterate and filter
        all_recipes = list(recipe_list)
        quick_recipes_with_time = []
        for recipe in all_recipes:
            minutes = parse_time_to_minutes(recipe.total_time)
            if minutes is not None and minutes <= 30:
                quick_recipes_with_time.append((recipe, minutes))
        # Sort by time (fastest to slowest)
        quick_recipes_with_time.sort(key=lambda x: x[1])
        # Extract just the recipes in sorted order
        recipe_list = [r[0] for r in quick_recipes_with_time]
    
    elif sort_by == 'servings':
        recipe_list = recipe_list.order_by('-servings')
    elif sort_by == 'rating':
        recipe_list = recipe_list.order_by('-average_rating')
    elif sort_by == 'difficulty':
        recipe_list = recipe_list.order_by('difficulty')
    else:
        # Default ordering to ensure consistent pagination
        recipe_list = recipe_list.order_by('-id')


    paginator = Paginator(recipe_list, 21)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'active_sort': sort_by,
        'search_query': search_query
    }
    return render(request, 'recipes.html', context)

