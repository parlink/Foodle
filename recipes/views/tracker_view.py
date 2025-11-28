from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# @login_required
def tracker(request):
    daily_goals = {
        'calories': 2000,
        'protein': 150,
        'water': 2500, # Added water goal
    }
    macros_consumed = {
        'calories': 800,
        'protein': 60,
        'carbs': 63,
        'fat': 36,
    }

    # Calculate percentages for progress bars
    calories_pct = int((macros_consumed['calories'] / daily_goals['calories']) * 100)
    protein_pct = int((macros_consumed['protein'] / daily_goals['protein']) * 100)
    
    # Calculate water percentage
    water_intake = 1250
    water_pct = int((water_intake / daily_goals['water']) * 100)


    context = {
        'daily_goals': daily_goals,
        'macros_consumed': macros_consumed,
        'calories_pct': calories_pct,
        'protein_pct': protein_pct,
        'water_intake': water_intake,
        'water_pct': water_pct,
        'fasting_status': {
            'time_elapsed': '14h 20m',
            'goal_time': '18h 00m',
            'is_active': True,
        },
        'meals': {
            'Breakfast': [
                {'title': 'Oatmeal with Berries', 'calories': 350, 'protein': 12, 'carbs': 45, 'fat': 6},
                {'title': 'Boiled Eggs', 'calories': 140, 'protein': 12, 'carbs': 1, 'fat': 10},
            ],
            'Lunch': [
                {'title': 'Grilled Chicken Salad', 'calories': 450, 'protein': 40, 'carbs': 15, 'fat': 20},
            ],
            'Dinner': [],
            'Snacks': [
                {'title': 'Almonds', 'calories': 160, 'protein': 6, 'carbs': 6, 'fat': 14},
            ],
        }
    }
    return render(request, 'recipes/tracker.html', context)
