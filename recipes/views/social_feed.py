from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from recipes.models import Post, Like
from recipes.forms import PostForm

def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'recipes/feed.html', {'posts': posts})

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if user already liked this post
    like_query = Like.objects.filter(user=request.user, post=post)
    
    if like_query.exists():
        # If liked, delete the like (Unlike)
        like_query.delete()
    else:
        # If not liked, create a like
        Like.objects.create(user=request.user, post=post)
        
    return redirect('feed')

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m() # Saves the tags
            return redirect('feed')
    else:
        form = PostForm()
    
    return render(request, 'recipes/create_post.html', {'form': form})