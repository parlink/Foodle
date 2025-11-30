from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from recipes.models import Meal
from recipes.forms.meal_form import MealForm


@login_required
def add_meal(request):
    """View to add a new meal."""
    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            # Use today if no date provided
            if not meal.date:
                meal.date = date.today()
            meal.save()
            messages.success(request, 'Meal added successfully!')
            return redirect('tracker')
    else:

        form = MealForm(initial={'date': date.today()})
    
    return render(request, 'recipes/add_meal.html', {'form': form})


@login_required
def delete_meal(request, meal_id):
    """View to delete a meal. Only allows users to delete their own meals."""
    meal = get_object_or_404(Meal, id=meal_id)
    
    # Security check: ensure user owns this meal
    if meal.user != request.user:
        messages.error(request, 'You do not have permission to delete this meal.')
        return redirect('tracker')
    
    if request.method == 'POST':
        meal.delete()
        messages.success(request, 'Meal deleted successfully!')
        return redirect('tracker')
    
    # If GET request, redirect to tracker
    return redirect('tracker')

