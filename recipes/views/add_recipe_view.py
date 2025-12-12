from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from recipes.forms.add_recipe_form import RecipeForm


@login_required
def recipe_create(request):
    """Handle recipe creation from the modal popup or standalone page."""
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            
            # Set average_rating from personal_rating if provided
            if recipe.personal_rating:
                recipe.average_rating = recipe.personal_rating
            
            recipe.save()
            
            # Check if AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Recipe added successfully!',
                    'recipe_id': recipe.id,
                })
            
            messages.success(request, f'Recipe "{recipe.name}" added successfully!')
            return redirect("my_recipes")
        else:
            # AJAX request with errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                }, status=400)
    else:
        form = RecipeForm()

    return render(request, "recipes/add_recipe.html", {"form": form})
