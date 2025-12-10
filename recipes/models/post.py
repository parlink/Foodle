from django.db import models
from django.conf import settings
from .tag import Tag

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    caption = models.TextField(blank = True)
    image = models.ImageField(upload_to='posts_images/', blank=True, null=True) 
    rating_total_score = models.PositiveIntegerField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    prep_time = models.CharField(max_length=50, blank=True, help_text="e.g. 25 min")
    servings = models.CharField(max_length=50, blank=True, help_text="e.g. 4 servings")
    created_at = models.DateTimeField(auto_now_add= True)
    tags = models.ManyToManyField(Tag, blank=True)
    prep_time = models.CharField(max_length=20, blank=True, help_text="e.g. 25 min")
    servings = models.PositiveIntegerField(default=1, blank=True)
    difficulty = models.CharField(max_length=20, choices=[("Easy", "Easy"), ("Moderate", "Moderate"), ("Hard", "Hard"),],default="Easy")
    CUISINE_CHOICES = [('Italian', 'Italian'), ('Mexican', 'Mexican'), ('Chinese', 'Chinese'), ('Indian', 'Indian'), ('Japanese', 'Japanese'), ('Thai', 'Thai'), ('French', 'French'), ('American', 'American'), ('Greek', 'Greek'), ('Spanish', 'Spanish'), ('Mediterranean', 'Mediterranean'), ('Korean', 'Korean'), ('Other', 'Other'),
    ]
    cuisine = models.CharField(max_length=50, choices=CUISINE_CHOICES, blank=True, null=True)

    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        return self.comments.count()
    
    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()

    def is_saved_by(self, user):
        return self.saves.filter(user=user).exists()
        
    @property
    def average_rating(self):
        if self.rating_count == 0:
            return 0.0
        return round(self.rating_total_score / self.rating_count, 1)
    
    def __str__(self):
        return self.title