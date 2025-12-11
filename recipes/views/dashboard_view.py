from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from recipes.models import Meal, DailyLog, Recipe, Post


@login_required
def dashboard(request):
    """
    Display the current user's dashboard.

    This view renders the dashboard page for the authenticated user.
    It ensures that only logged-in users can access the page. If a user
    is not authenticated, they are automatically redirected to the login
    page.
    """
    user = request.user
    today = timezone.now().date()
    
    # Calculate quick stats
    meals_today = Meal.objects.filter(user=user, date=today).count()
    
    # Get water intake for today
    try:
        daily_log = DailyLog.objects.get(user=user, date=today)
        water_today = daily_log.amount_ml
    except DailyLog.DoesNotExist:
        water_today = 0
    
    # Get user's recipe count
    recipes_count = Recipe.objects.filter(created_by=user).count()
    
    # Get user's posts count
    posts_count = Post.objects.filter(author=user).count()
    
    stats = {
        'meals_today': meals_today,
        'water_today': water_today,
        'recipes_count': recipes_count,
        'posts_count': posts_count,
    }
    
    return render(request, 'recipes/dashboard.html', {
        'user': user,
        'stats': stats,
    })
