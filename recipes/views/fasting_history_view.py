from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from recipes.models import FastingSession
from django.db.models import Avg
import calendar
from django.utils.dateparse import parse_datetime

@login_required
def fasting_history(request):
    """
    Display fasting history with weekly/monthly views, charts, and navigation.
    Sessions are attributed to the day they started.
    """
    view_type = request.GET.get('view_type', 'week')
    try:
        date_offset = int(request.GET.get('date_offset', 0))
    except ValueError:
        date_offset = 0

    #Handle Edit POST
    if request.method == 'POST' and request.POST.get('action') == 'edit_session':
        session_id = request.POST.get('session_id')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        
        session = get_object_or_404(FastingSession, id=session_id, user=request.user)
        
        if start_time_str:
            session.start_date_time = parse_datetime(start_time_str)
            
        if end_time_str:
            session.end_date_time = parse_datetime(end_time_str)
            session.is_active = False
        else:
            session.end_date_time = None
            session.is_active = True
            
        session.save()
        return redirect(f"{request.path}?view_type={view_type}&date_offset={date_offset}")

    today = timezone.localdate()
    #Get user's current goal to show as a baseline reference in charts
    user_goal = request.user.profile.fasting_goal
    
    chart_labels = []
    chart_data = [] #Actual duration
    chart_goal_data = [] #Goal duration for that session
    table_data = []

    if view_type == 'month':
        #Align to start of month
        #Start from 1st of current month
        current_month_start = today.replace(day=1)
        
        year = current_month_start.year
        month = current_month_start.month + date_offset
        
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1
            
        start_date = current_month_start.replace(year=year, month=month)
        _, last_day = calendar.monthrange(year, month)
        end_date = start_date.replace(day=last_day)
        
        show_next = end_date < today
        
        #Filter by start_date_time range
        sessions = FastingSession.objects.filter(
            user=request.user,
            start_date_time__date__range=[start_date, end_date],

            
        ).order_by('start_date_time')

        #Map sessions to weeks
        current_week_start = start_date
        
        while current_week_start <= end_date:
            days_until_sunday = 6 - current_week_start.weekday()

            current_week_end = min(current_week_start + timedelta(days=days_until_sunday), end_date)
            
            #Find sessions starting in this week
            last_session = sessions.last()
            week_sessions = [s for s in sessions if current_week_start <= timezone.localdate(s.start_date_time) <= current_week_end and (not s.is_active or s == last_session)]
            
            #Calculate average duration
            total_hours = 0
            count = 0
            for s in week_sessions:
                if s.duration:
                    total_hours += s.duration.total_seconds() / 3600
                    count += 1
            
            avg_hours = round(total_hours / count, 1) if count > 0 else 0
            
            label = f"{current_week_start.strftime('%b %d')} - {current_week_end.strftime('%d')}"
            chart_labels.append(label)
            chart_data.append(avg_hours)
            chart_goal_data.append(user_goal) 
            
            current_week_start = current_week_end + timedelta(days=1)

        #For the table, pass all sessions in reverse order
        for s in reversed(sessions):
             duration_hours = s.duration.total_seconds() / 3600 if s.duration else 0
             table_data.append({
                'id': s.id,
                'date': timezone.localdate(s.start_date_time),
                'start_time': s.start_date_time,
                'end_time': s.end_date_time,
                'duration_str': f"{int(duration_hours)}h {int((duration_hours % 1) * 60)}m",
                'goal': s.target_duration,
                'met_goal': duration_hours >= s.target_duration,
                'is_active': s.is_active
            })

    else:
        # --- Weekly Logic for daily data ---
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week + timedelta(weeks=date_offset)
        end_date = start_date + timedelta(days=6)
        
        show_next = end_date < today
        
        sessions = FastingSession.objects.filter(
            user=request.user,
            start_date_time__date__range=[start_date, end_date],
        ).order_by('start_date_time')
        
        session_map = {}
        for s in sessions:
            #Only chart completed sessions
            if not s.is_active:
                day = timezone.localdate(s.start_date_time)
                if day not in session_map:
                    session_map[day] = []
                session_map[day].append(s)
            
        for i in range(7):
            current_day = start_date + timedelta(days=i)
            day_sessions = session_map.get(current_day, [])
            
            #Chart Data: Max duration of the day
            max_duration = 0
            goal_for_max = user_goal
            
            if day_sessions:


                #Find longest fast
                longest_session = max(day_sessions, key=lambda x: x.duration.total_seconds() if x.duration else 0)
                if longest_session.duration:
                    max_duration = round(longest_session.duration.total_seconds() / 3600, 1)
                    goal_for_max = longest_session.target_duration
            
            chart_labels.append(current_day.strftime('%a %d'))
            chart_data.append(max_duration)
            chart_goal_data.append(goal_for_max)
        
        #Table Data (All sessions in this week)
        for s in reversed(sessions):
            duration_hours = s.duration.total_seconds() / 3600 if s.duration else 0
            table_data.append({
                'id': s.id,
                'date': timezone.localdate(s.start_date_time),
                'start_time': s.start_date_time,
                'end_time': s.end_date_time,
                'duration_str': f"{int(duration_hours)}h {int((duration_hours % 1) * 60)}m",
                'goal': s.target_duration,
                'met_goal': duration_hours >= s.target_duration,
                'is_active': s.is_active
            })

    context = {
        'view_type': view_type,
        'date_offset': date_offset,
        'start_date': start_date,
        'end_date': end_date,
        'show_next': show_next,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'chart_goal_data': chart_goal_data,
        'table_data': table_data,
    }
    
    return render(request, 'recipes/fasting_history.html', context)


