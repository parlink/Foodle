from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from recipes.models import Meal, Profile, DailyLog, FastingSession

def get_accounting_date():
    """
    Returns the date for accounting purposes based on the 6 AM rule.
    If current time is before 6 AM, returns yesterday's date.
    Otherwise, returns today's date.
    This exists so that if the user drinks water at night, it doesn't count for the day after.
    """
    now = timezone.localtime(timezone.now())
    if now.hour < 6:
        return now.date() - timedelta(days=1)
    return now.date()

@login_required
def tracker(request):
    today = get_accounting_date()
    
    #Get or create user profile, default is 2000 calories per day
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'calorie_goal': 2000,
            'protein_goal': 150,
            'carbs_goal': 250,
            'fat_goal': 70,
            'fasting_goal': 16
        }
    )

    #Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        #Handle water intake actions
        if action == 'update_water':
            amount = int(request.POST.get('amount', 0))
            daily_log = DailyLog.objects.filter(user=request.user, date=today).first()
            if not daily_log:
                daily_log = DailyLog.objects.create(
                    user=request.user,
                    date=today,
                    calorie_goal=profile.calorie_goal,
                    protein_goal=profile.protein_goal,
                    carbs_goal=profile.carbs_goal,
                    fat_goal=profile.fat_goal,
                    water_goal=2500,
                    amount_ml=0
                )
            #Update amount, ensuring it doesn't go below 0
            new_amount = daily_log.amount_ml + amount
            daily_log.amount_ml = max(0, new_amount)
            daily_log.save()
            return redirect('tracker')
        
        #Handle goal updates
        elif action == 'update_goals':
            calorie_goal = int(request.POST.get('calorie_goal', 2500))
            protein_goal = int(request.POST.get('protein_goal', 187))
            carbs_goal = int(request.POST.get('carbs_goal', 250))
            fat_goal = int(request.POST.get('fat_goal', 83))
            water_goal = int(request.POST.get('water_goal', 2500))
            
            # Get or create DailyLog for today
            daily_log, _ = DailyLog.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={
                    'calorie_goal': profile.calorie_goal,
                    'protein_goal': profile.protein_goal,
                    'carbs_goal': profile.carbs_goal,
                    'fat_goal': profile.fat_goal,
                    'water_goal': 2500,
                }
            )
            
            # Update DailyLog goals
            daily_log.calorie_goal = calorie_goal
            daily_log.protein_goal = protein_goal
            daily_log.carbs_goal = carbs_goal
            daily_log.fat_goal = fat_goal
            daily_log.water_goal = water_goal
            daily_log.save()
            
            # Update Profile defaults (so tomorrow uses these as defaults)
            profile.calorie_goal = calorie_goal
            profile.protein_goal = protein_goal
            profile.carbs_goal = carbs_goal
            profile.fat_goal = fat_goal
            profile.save()
            
            return redirect('tracker')
        
        #Handle fasting actions
        elif action == 'start_fast':
            target_duration = int(request.POST.get('target_duration', 16))
            
            #Save user preference
            profile.fasting_goal = target_duration
            profile.save()

            #Deactivate any existing active sessions
            #Using update() is efficient but we want to ensure we don't leave zombie active sessions.
            #Update sets end_date_time to now, effectively closing them.
            FastingSession.objects.filter(user=request.user, is_active=True).update(
                is_active=False,
                end_date_time=timezone.now()
            )

            #Create new active session
            FastingSession.objects.create(
                user=request.user,
                start_date_time=timezone.now(),
                target_duration=target_duration,
                is_active=True
            )
            return redirect('tracker')
        
        elif action == 'update_fasting_goal':
            target_duration = int(request.POST.get('target_duration', 16))
            profile.fasting_goal = target_duration
            profile.save()
            return redirect('tracker')
        
        elif action == 'end_fast':
            #Deactivate active fasting session
            FastingSession.objects.filter(user=request.user, is_active=True).update(
                is_active=False,
                end_date_time=timezone.now()
            )
            return redirect('tracker')
    
    
    #Get or create DailyLog for today, copying defaults from Profile
    daily_log, _ = DailyLog.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={
            'calorie_goal': profile.calorie_goal,
            'protein_goal': profile.protein_goal,
            'carbs_goal': profile.carbs_goal,
            'fat_goal': profile.fat_goal,
            'water_goal': 2500,
            'amount_ml': 0
        }
    )
    water_intake = daily_log.amount_ml
    
    #Get active fasting session
    active_fasting = FastingSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-start_date_time').first()
    
    fasting_status = {
        'time_elapsed': '0h 00m 00s',
        'goal_time': f"{profile.fasting_goal}h 00m",
        'is_active': False,
        'target_duration': profile.fasting_goal,
        'start_time': None,
        'start_timestamp': None
    }
    
    if active_fasting:
        now = timezone.now()
        elapsed = now - active_fasting.start_date_time
        hours_elapsed = int(elapsed.total_seconds() // 3600)
        minutes_elapsed = int((elapsed.total_seconds() % 3600) // 60)
        seconds_elapsed = int(elapsed.total_seconds() % 60)
        fasting_status['time_elapsed'] = f"{hours_elapsed}h {minutes_elapsed:02d}m {seconds_elapsed:02d}s"
        fasting_status['goal_time'] = f"{active_fasting.target_duration}h 00m"
        fasting_status['is_active'] = True
        fasting_status['target_duration'] = active_fasting.target_duration
        fasting_status['start_time'] = active_fasting.start_date_time.isoformat()
        fasting_status['start_timestamp'] = active_fasting.start_date_time.timestamp() * 1000
    
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
    

    daily_goals = {
        'calories': int(daily_log.calorie_goal or 2000),
        'protein': int(daily_log.protein_goal or 0),
        'carbs': int(daily_log.carbs_goal or 0),
        'fat': int(daily_log.fat_goal or 0),
        'water': int(daily_log.water_goal or 2500),
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
    
    water_pct = min(100, max(0, int((water_intake / daily_goals['water']) * 100))) if daily_goals['water'] > 0 else 0
    
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
        'daily_log': daily_log,
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
