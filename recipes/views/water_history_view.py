from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from recipes.models import WaterIntake
from django.db.models import Sum, Avg
import calendar

@login_required
def water_history(request):
    """
    Display water intake history with weekly/monthly views, charts, and navigation.
    """
    view_type = request.GET.get('view_type', 'week')
    try:
        date_offset = int(request.GET.get('date_offset', 0))
    except ValueError:
        date_offset = 0

    today = timezone.localdate()
    water_goal = 2500  #Default goal

    chart_labels = []
    chart_data = []
    table_data = []

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
        
        # End date is last day of month
        _, last_day = calendar.monthrange(year, month)
        end_date = start_date.replace(day=last_day)
        
        # Guard for future navigation
        show_next = end_date < today
        
        # Fetch all records for the month
        intake_records = WaterIntake.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )
        intake_map = {record.date: record.amount_ml for record in intake_records}
        
        # Aggregate by Week
        # We iterate through the month week by week
        current_week_start = start_date
        
        while current_week_start <= end_date:
            # End of this partial week is either Sunday or Month End
            days_until_sunday = 6 - current_week_start.weekday()
            current_week_end = min(current_week_start + timedelta(days=days_until_sunday), end_date)
            
            # Calculate average for this specific week slice
            total_ml = 0
            days_count = 0
            
            iter_date = current_week_start
            while iter_date <= current_week_end:
                total_ml += intake_map.get(iter_date, 0)
                days_count += 1
                iter_date += timedelta(days=1)
            
            avg_intake = int(total_ml / days_count) if days_count > 0 else 0
            
            # Label
            label = f"{current_week_start.strftime('%b %d')} - {current_week_end.strftime('%d')}"
            
            # Add to chart data
            chart_labels.append(label)
            chart_data.append(avg_intake)
            
            # Add to table data
            table_data.append({
                'range': label,
                'avg_intake': avg_intake,
                'total_intake': total_ml, # Optional extras
                'days_count': days_count
            })
            
            # Move to next week
            current_week_start = current_week_end + timedelta(days=1)
            
    else:
        # --- Weekly Logic (Daily Data) ---
        
        # Align to start of week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week + timedelta(weeks=date_offset)
        end_date = start_date + timedelta(days=6)
        
        # Guard for future navigation
        show_next = end_date < today
        
        # Fetch data
        intake_records = WaterIntake.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )
        intake_map = {record.date: record.amount_ml for record in intake_records}
        
        # Build 7 days of data
        for i in range(7):
            current_day = start_date + timedelta(days=i)
            amount = intake_map.get(current_day, 0)
            
            # Chart Data
            chart_labels.append(current_day.strftime('%a %d'))
            chart_data.append(amount)
            
            # Table Data
            table_data.append({
                'date': current_day,
                'amount': amount,
                'goal': water_goal,
                'met_goal': amount >= water_goal
            })

    #Handle Edit POST
    if request.method == 'POST':
        edit_date_str = request.POST.get('date')
        new_amount = request.POST.get('amount')
        
        if edit_date_str and new_amount is not None:
            try:
                amount_val = max(0, int(new_amount))
                WaterIntake.objects.update_or_create(
                    user=request.user,
                    date=edit_date_str,
                    defaults={'amount_ml': amount_val}
                )
            except ValueError:
                pass
            return redirect(f"{request.path}?view_type={view_type}&date_offset={date_offset}")

    context = {
        'view_type': view_type,
        'date_offset': date_offset,
        'start_date': start_date,
        'end_date': end_date,
        'show_next': show_next,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'table_data': table_data,
        'water_goal': water_goal,
    }
    
    return render(request, 'recipes/water_history.html', context)
