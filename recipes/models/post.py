from django.db import models
from django.conf import settings
from .tag import Tag

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    caption = models.TextField(blank = True)
    #image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add= True)
    tags = models.ManyToManyField(Tag, blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        return self.comments.count()
    
    def __str__(self):
        return self.title