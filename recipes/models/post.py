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
    
    created_at = models.DateTimeField(auto_now_add= True)
    tags = models.ManyToManyField(Tag, blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        return self.comments.count()
        
    @property
    def average_rating(self):
        """Calculates the average rating."""
        if self.rating_count == 0:
            return 0.0
        return round(self.rating_total_score / self.rating_count, 1)
    
    def __str__(self):
        return self.title