from django.shortcuts import render, get_object_or_404
from recipes.models import Recipe

def recipe_detail(request, id):
    # Retrieve the recipe by its id
    recipe = get_object_or_404(Recipe, id=id)
    
    # Split ingredients and method into separate lines for display
    ingredients = recipe.ingredients.split(', ')  # Assuming ingredients are stored as a comma-separated string
    method = recipe.method.split('\n')  # Assuming method steps are separated by new lines

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,
        'method': method,
    })
