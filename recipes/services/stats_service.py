from datetime import date, timedelta
from django.db.models import Sum
from django.utils import timezone


class UserStatsService:
    """Service class to compute user statistics for the profile page."""
    
    def __init__(self, user):
        self.user = user
        self._meals_count = None
        self._posts_count = None
        self._streak = None
    
    def get_stats(self):
        """Get all statistics for the user."""
        return {
            'total_meals_logged': self._count_meals(),
            'total_recipes_shared': self._count_posts(),
            'total_followers': self._count_followers(),
            'total_following': self._count_following(),
            'current_streak': self._calculate_streak(),
            'longest_streak': self._calculate_longest_streak(),
            'total_water_ml': self._sum_water(),
            'total_water_liters': round(self._sum_water() / 1000, 1),
            'total_fasting_hours': self._sum_fasting_hours(),
            'completed_fasts': self._count_completed_fasts(),
            'saved_recipes': self._count_saved_recipes(),
            'member_since': self.user.date_joined,
            'days_as_member': (timezone.now().date() - self.user.date_joined.date()).days,
        }
    
    def _count_meals(self):
        """Count total meals logged by the user."""
        if self._meals_count is None:
            from recipes.models import Meal
            self._meals_count = Meal.objects.filter(user=self.user).count()
        return self._meals_count
    
    def _count_posts(self):
        """Count total posts/recipes shared by the user."""
        if self._posts_count is None:
            from recipes.models import Post
            self._posts_count = Post.objects.filter(author=self.user).count()
        return self._posts_count
    
    def _count_followers(self):
        """Count followers."""
        from recipes.models import Follow
        return Follow.objects.filter(followed=self.user).count()
    
    def _count_following(self):
        """Count users being followed."""
        from recipes.models import Follow
        return Follow.objects.filter(follower=self.user).count()
    
    def _count_saved_recipes(self):
        """Count saved/bookmarked recipes."""
        from recipes.models import Save
        return Save.objects.filter(user=self.user).count()
    
    def _calculate_streak(self):
        """Calculate current consecutive days with meals logged."""
        if self._streak is not None:
            return self._streak
            
        from recipes.models import Meal
        
        # Get distinct dates with meals, ordered descending
        meal_dates = set(
            Meal.objects.filter(user=self.user)
            .values_list('date', flat=True)
            .distinct()
        )
        
        if not meal_dates:
            self._streak = 0
            return 0
        
        today = date.today()
        streak = 0
        current_date = today
        
        # Check if user logged today or yesterday (to allow for ongoing streak)
        if today not in meal_dates and (today - timedelta(days=1)) not in meal_dates:
            self._streak = 0
            return 0
        
        # If not logged today, start from yesterday
        if today not in meal_dates:
            current_date = today - timedelta(days=1)
        
        # Count consecutive days
        while current_date in meal_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        self._streak = streak
        return streak
    
    def _calculate_longest_streak(self):
        """Calculate the longest streak ever achieved."""
        from recipes.models import Meal
        
        meal_dates = sorted(
            Meal.objects.filter(user=self.user)
            .values_list('date', flat=True)
            .distinct()
        )
        
        if not meal_dates:
            return 0
        
        longest = 1
        current = 1
        
        for i in range(1, len(meal_dates)):
            if meal_dates[i] - meal_dates[i-1] == timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        
        return longest
    
    def _sum_water(self):
        """Sum total water intake in ml."""
        from recipes.models import DailyLog
        result = DailyLog.objects.filter(user=self.user).aggregate(
            total=Sum('amount_ml')
        )
        return result['total'] or 0
    
    def _sum_fasting_hours(self):
        """Sum total fasting hours from completed sessions."""
        from recipes.models import FastingSession
        
        completed_sessions = FastingSession.objects.filter(
            user=self.user,
            is_active=False,
            end_date_time__isnull=False
        )
        
        total_hours = 0
        for session in completed_sessions:
            if session.duration:
                total_hours += session.duration.total_seconds() / 3600
        
        return round(total_hours, 1)
    
    def _count_completed_fasts(self):
        """Count completed fasting sessions."""
        from recipes.models import FastingSession
        return FastingSession.objects.filter(
            user=self.user,
            is_active=False
        ).count()

