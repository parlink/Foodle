from django.db import models
from django.conf import settings
from .post import Post

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete= models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)