from django.shortcuts import render
#from recipes.models import Post

def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'recipes/feed.html', {'posts': posts})

