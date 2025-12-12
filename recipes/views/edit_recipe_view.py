from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from recipes.models import Recipe
from recipes.forms.add_recipe_form import RecipeForm


@login_required
def recipe_edit(request, id):
    recipe = get_object_or_404(Recipe, id=id, created_by=request.user)

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            updated = form.save(commit=False)

            updated.created_by = request.user
            
            if updated.personal_rating:
                updated.average_rating = updated.personal_rating

            updated.save()
            messages.success(request, f'Recipe "{updated.name}" updated!')
            return redirect("my_recipes")
    else:
        form = RecipeForm(instance=recipe)

    return render(request, "recipes/edit_recipe.html", {"form": form, "recipe": recipe})
