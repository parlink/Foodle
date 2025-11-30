from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from recipes.models import WaterIntake
from django.db.models import Sum

@login_required
def water_history(request):
    """
    Display water intake history with weekly/monthly views and navigation.
    """
    view_type = request.GET.get('view_type', 'week')
    try:
        date_offset = int(request.GET.get('date_offset', 0))
    except ValueError:
        date_offset = 0

    today = timezone.localdate()
    
    #Calculate date range
    if view_type == 'month':
        #Align to start of month
        #Start from 1st of current month
        current_month_start = today.replace(day=1)
        
        #Adjust by offset (months)
        year = current_month_start.year
        month = current_month_start.month + date_offset
        
        #Adjust year/month overflow
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1
            
        start_date = current_month_start.replace(year=year, month=month)
        
        #End date is start of next month - 1 day
        if month == 12:
            end_date = start_date.replace(year=year+1, month=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=month+1) - timedelta(days=1)
            
        days_in_period = (end_date - start_date).days + 1
        
    else: #week default
        #Align to start of week, usually Monday
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week + timedelta(weeks=date_offset)
        end_date = start_date + timedelta(days=6)
        days_in_period = 7

    #Guard for future navigation
    #Check if end_date is in future relative to today
    is_current_period = start_date <= today <= end_date
    is_future_period = start_date > today
    
    #We allow navigation up to the current period. 
    show_next = end_date < today
    
    #Fetch data
    intake_records = WaterIntake.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )
    
    #Organize data by date for display
    intake_map = {record.date: record for record in intake_records}
    
    daily_data = []
    water_goal = 2500 #Default goal, could be fetched from user profile
    
    for i in range(days_in_period):
        current_day = start_date + timedelta(days=i)
        record = intake_map.get(current_day)
        amount = record.amount_ml if record else 0
        
        daily_data.append({
            'date': current_day,
            'amount': amount,
            'goal': water_goal,
            'percentage': min(100, int((amount / water_goal) * 100)),
            'met_goal': amount >= water_goal
        })

    #Handle Edit POST
    if request.method == 'POST':
        edit_date_str = request.POST.get('date')
        new_amount = request.POST.get('amount')
        
        if edit_date_str and new_amount is not None:
            try:
                #new_amount can be empty string if cleared? assume 0 if invalid
                amount_val = int(new_amount) if new_amount else 0
                amount_val = max(0, amount_val)
                
                WaterIntake.objects.update_or_create(
                    user=request.user,
                    date=edit_date_str,
                    defaults={'amount_ml': amount_val}
                )
            except ValueError:
                pass #Ignore invalid inputs
            
            return redirect(f"{request.path}?view_type={view_type}&date_offset={date_offset}")

    context = {
        'view_type': view_type,
        'date_offset': date_offset,
        'start_date': start_date,
        'end_date': end_date,
        'show_next': show_next,
        'daily_data': daily_data,
        'water_goal': water_goal,
    }
    
    return render(request, 'recipes/water_history.html', context)

