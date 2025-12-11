from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from recipes.forms.add_recipe_form import RecipeForm

@login_required
def recipe_create(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            return redirect("my_recipes")
    else:
        form = RecipeForm()

    return render(request, "recipes/recipe_create.html", {"form": form})
