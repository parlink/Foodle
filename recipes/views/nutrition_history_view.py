from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta, date
from recipes.models import DailyLog, Meal


@login_required
def nutrition_history(request):
    """
    Display nutrition history with charts showing calories and macros vs goals.
    """
    try:
        days = int(request.GET.get('days', 30))
    except ValueError:
        days = 30
    
    #Limit to reasonable range
    days = max(7, min(days, 90))
    
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)
    
    #Fetch DailyLog records for the period
    daily_logs = DailyLog.objects.filter(
        user=request.user,
        date__range=[start_date, today]
    ).order_by('date')
    
    #Fetch meals for the period
    meals = Meal.objects.filter(
        user=request.user,
        date__range=[start_date, today]
    )
    
    #Create a map of date -> daily log for quick lookup
    log_map = {log.date: log for log in daily_logs}
    
    meals_by_date = {}
    for meal in meals:
        if meal.date not in meals_by_date:
            meals_by_date[meal.date] = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
            }
        meals_by_date[meal.date]['calories'] += meal.calories
        meals_by_date[meal.date]['protein'] += meal.protein_g
        meals_by_date[meal.date]['carbs'] += meal.carbs_g
        meals_by_date[meal.date]['fat'] += meal.fat_g
    
    #Build chart data
    chart_labels = []
    calories_actual = []
    calories_goal = []
    protein_actual = []
    protein_goal = []
    carbs_actual = []
    carbs_goal = []
    fat_actual = []
    fat_goal = []
    
    current_date = start_date
    while current_date <= today:
        log = log_map.get(current_date)
        consumed = meals_by_date.get(current_date, {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
        })
        
        #Format label (show day/month for readability)
        if days <= 14:
            label = current_date.strftime('%b %d')
        else:
            label = current_date.strftime('%m/%d')
        
        chart_labels.append(label)
        
        if log:
            calories_actual.append(consumed['calories'])
            calories_goal.append(log.calorie_goal)
            protein_actual.append(round(consumed['protein'], 1))
            protein_goal.append(log.protein_goal)
            carbs_actual.append(round(consumed['carbs'], 1))
            carbs_goal.append(log.carbs_goal)
            fat_actual.append(round(consumed['fat'], 1))
            fat_goal.append(log.fat_goal)
        else:
            #No log for this date - use zeros or skip
            calories_actual.append(consumed['calories'])
            calories_goal.append(0)
            protein_actual.append(round(consumed['protein'], 1))
            protein_goal.append(0)
            carbs_actual.append(round(consumed['carbs'], 1))
            carbs_goal.append(0)
            fat_actual.append(round(consumed['fat'], 1))
            fat_goal.append(0)
        
        current_date += timedelta(days=1)
    
    context = {
        'days': days,
        'start_date': start_date,
        'end_date': today,
        'chart_labels': chart_labels,
        'calories_actual': calories_actual,
        'calories_goal': calories_goal,
        'protein_actual': protein_actual,
        'protein_goal': protein_goal,
        'carbs_actual': carbs_actual,
        'carbs_goal': carbs_goal,
        'fat_actual': fat_actual,
        'fat_goal': fat_goal,
    }
    
    return render(request, 'recipes/nutrition_history.html', context)

