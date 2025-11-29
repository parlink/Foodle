from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import date
from recipes.models import Meal, Profile, WaterIntake, FastingSession

@login_required
def tracker(request):
    today = date.today()
    
    #Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        #Handle water intake actions
        if action == 'add_water':
            water_intake_record, _ = WaterIntake.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={'amount_ml': 0}
            )
            water_intake_record.amount_ml += 250
            water_intake_record.save()
            return redirect('tracker')
        
        elif action == 'remove_water':
            water_intake_record, _ = WaterIntake.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={'amount_ml': 0}
            )
            water_intake_record.amount_ml = max(0, water_intake_record.amount_ml - 250)
            water_intake_record.save()
            return redirect('tracker')
        
        #Handle fasting actions
        elif action == 'start_fast':
            target_duration = int(request.POST.get('target_duration', 16))
            #Deactivate any existing active sessions
            FastingSession.objects.filter(user=request.user, is_active=True).update(is_active=False)

            #Create new active session
            FastingSession.objects.create(
                user=request.user,
                start_date_time=timezone.now(),
                target_duration=target_duration,
                is_active=True
            )
            return redirect('tracker')
        
        elif action == 'end_fast':
            #Deactivate active fasting session
            FastingSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
            return redirect('tracker')
    
    #Get or create user profile, default is 2000 calories per day
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'calorie_goal': 2000,
            'protein_goal': 150,
        }
    )
    
    #Set default water goal if not in profile, default is 2500ml per day
    water_goal = 2500  # Default water goal in ml
    
    #Get or create water intake for today
    water_intake_record, _ = WaterIntake.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'amount_ml': 0}
    )
    water_intake = water_intake_record.amount_ml
    
    #Get active fasting session
    active_fasting = FastingSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-start_date_time').first()
    
    fasting_status = {
        'time_elapsed': '0h 0m',
        'goal_time': '0h 0m',
        'is_active': False,
        'target_duration': 18,
    }
    
    if active_fasting:
        now = timezone.now()
        elapsed = now - active_fasting.start_date_time
        hours_elapsed = int(elapsed.total_seconds() // 3600)
        minutes_elapsed = int((elapsed.total_seconds() % 3600) // 60)
        fasting_status['time_elapsed'] = f"{hours_elapsed}h {minutes_elapsed:02d}m"
        fasting_status['goal_time'] = f"{active_fasting.target_duration}h 00m"
        fasting_status['is_active'] = True
        fasting_status['target_duration'] = active_fasting.target_duration
    
    #Get today's meals
    today_meals = Meal.objects.filter(
        user=request.user,
        date=today
    )
    
    #Calculate totals from meals
    totals = today_meals.aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein_g'),
        total_carbs=Sum('carbs_g'),
        total_fat=Sum('fat_g')
    )
    
    macros_consumed = {
        'calories': int(totals['total_calories'] or 0),
        'protein': float(totals['total_protein'] or 0),
        'carbs': float(totals['total_carbs'] or 0) if totals['total_carbs'] is not None else 0.0,
        'fat': float(totals['total_fat'] or 0) if totals['total_fat'] is not None else 0.0,
    }
    
    #Get daily goals from profile
    daily_goals = {
        'calories': int(profile.calorie_goal or 2000),
        'protein': int(profile.protein_goal or 0),
        'carbs': int(profile.carbs_goal or 0),
        'fat': int(profile.fat_goal or 0),
        'water': water_goal,
    }

    #Calculate percentages for progress bars
    calories_pct = min(100, max(0, int((macros_consumed['calories'] / daily_goals['calories']) * 100))) if daily_goals['calories'] > 0 else 0
    protein_pct = min(100, max(0, int((macros_consumed['protein'] / daily_goals['protein']) * 100))) if daily_goals['protein'] > 0 else 0
    
    #Calculate carbs percentage
    carbs_consumed = macros_consumed['carbs']
    carbs_goal = daily_goals['carbs']
    if carbs_goal > 0:
        carbs_pct = min(100, max(0, int((carbs_consumed / carbs_goal) * 100)))
    else:
        carbs_pct = 0
    
    #Calculate fat percentage
    fat_consumed = macros_consumed['fat']
    fat_goal = daily_goals['fat']
    if fat_goal > 0:
        fat_pct = min(100, max(0, int((fat_consumed / fat_goal) * 100)))
    else:
        fat_pct = 0
    
    water_pct = min(100, max(0, int((water_intake / water_goal) * 100))) if water_goal > 0 else 0
    
    #Organize meals by type
    meals_dict = {
        'Breakfast': [],
        'Lunch': [],
        'Dinner': [],
        'Snacks': [], 
    }
    
    for meal in today_meals:
        meal_data = {
            'id': meal.id,
            'title': meal.name,
            'calories': meal.calories,
            'protein': meal.protein_g,
            'carbs': meal.carbs_g,
            'fat': meal.fat_g,
        }

        meal_type = 'Snacks' if meal.meal_type == 'Snack' else meal.meal_type
        if meal_type in meals_dict:
            meals_dict[meal_type].append(meal_data)
    
    context = {
        'daily_goals': daily_goals,
        'macros_consumed': macros_consumed,
        'calories_pct': calories_pct,
        'protein_pct': protein_pct,
        'carbs_pct': carbs_pct,
        'fat_pct': fat_pct,
        'water_intake': water_intake,
        'water_pct': water_pct,
        'fasting_status': fasting_status,
        'meals': meals_dict,
    }
    return render(request, 'recipes/tracker.html', context)
