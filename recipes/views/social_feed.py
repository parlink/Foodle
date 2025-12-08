from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F
from django.template.loader import render_to_string

from recipes.models import Post, Like, Comment, Save, Rating, Follow, User 
from recipes.forms.post_form import PostForm 
from recipes.helpers import is_liked_util, is_saved_util, is_followed_util, get_rating_util

@login_required
def feed(request):
    show_saved = request.GET.get('saved') == 'true'
    show_followed_only = request.GET.get('followed') == 'true'

    if show_saved:
        # Get posts saved by the current user
        posts = Post.objects.filter(saves__user=request.user)
    elif show_followed_only:
        # Get posts from followed users + own posts
        followed_ids = Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)
        posts = Post.objects.filter(author__in=followed_ids).union(
            Post.objects.filter(author=request.user)
        )
    else:
        # Get all posts
        posts = Post.objects.all()

    # Optimize queries
    posts = posts.select_related('author').prefetch_related('tags', 'comments__user').order_by('-created_at')

    # 2. Pre-calculate interactions for the UI
    # (We execute the queryset list to get IDs for the optimized lookups below)
    post_ids = [post.id for post in posts]
    
    liked_posts_set = set(Like.objects.filter(user=request.user, post_id__in=post_ids).values_list('post_id', flat=True))
    saved_posts_set = set(Save.objects.filter(user=request.user, post_id__in=post_ids).values_list('post_id', flat=True))
    user_ratings_dict = {r.post_id: r.score for r in Rating.objects.filter(user=request.user, post_id__in=post_ids)}
    
    author_ids = [post.author_id for post in posts]
    following_status = Follow.objects.filter(follower=request.user, followed_id__in=author_ids).values_list('followed_id', flat=True)
    is_following_map = {author_id: True for author_id in following_status}
    
    # Attach attributes to post objects for the template to use
    for post in posts:
        post.is_liked_by_user = is_liked_util(post.id, liked_posts_set)
        post.is_saved_by_user = is_saved_util(post.id, saved_posts_set)
        post.user_rating_score = get_rating_util(post.id, user_ratings_dict)
        post.is_followed_by_user = is_followed_util(post.author_id, is_following_map)

    form = PostForm()

    context = {
        'posts': posts,
        'show_followed_only': show_followed_only,
        'view_saved': show_saved, # Passed to template to highlight sidebar
        'form': form,
    }
    return render(request, 'recipes/feed.html', context)

@login_required
@require_POST
def toggle_like(request, post_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("Must be an AJAX request.")

    post = get_object_or_404(Post, id=post_id)
    liked = False

    try:
        with transaction.atomic():
            like_query = Like.objects.filter(user=request.user, post=post)
            if like_query.exists():
                like_query.delete()
                liked = False
            else:
                Like.objects.create(user=request.user, post=post)
                liked = True
            
            # Recalculate count dynamically to ensure accuracy
            current_count = post.likes.count()
            
            # If your Post model has a denormalized 'likes_count' field, update it:
            # post.likes_count = current_count
            # post.save(update_fields=['likes_count'])
            
            return JsonResponse({'liked': liked, 'likes_count': current_count})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def toggle_save(request, post_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("Must be an AJAX request.")
    
    post = get_object_or_404(Post, id=post_id)
    saved = False
    
    try:
        save_query = Save.objects.filter(user=request.user, post=post)
        if save_query.exists():
            save_query.delete()
            saved = False
        else:
            Save.objects.create(user=request.user, post=post)
            saved = True
        return JsonResponse({'saved': saved})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def delete_post(request, post_id):
    """
    Allows the author to delete their own post.
    """
    post = get_object_or_404(Post, pk=post_id)
    
    # Security check: ensure only the author can delete
    if request.user == post.author:
        post.delete()
        
    # Redirect back to feed (or wherever they were)
    return redirect('feed')

# ... (Keep submit_rating, submit_comment, toggle_follow, and create_post exactly as they were) ...
@login_required
@require_POST
def submit_rating(request, post_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("Must be an AJAX request.")
    
    try:
        score = int(request.POST.get('score')) 
        if not (1 <= score <= 5):
            return HttpResponseBadRequest("Score must be between 1 and 5.")
            
        post = get_object_or_404(Post, id=post_id)
        
        with transaction.atomic():
            rating_obj, created = Rating.objects.get_or_create(
                user=request.user, post=post, defaults={'score': score}
            )
            old_score = rating_obj.score
            
            if created:
                post.rating_total_score = F('rating_total_score') + score
                post.rating_count = F('rating_count') + 1
            else:
                post.rating_total_score = F('rating_total_score') - old_score + score
                rating_obj.score = score
                rating_obj.save()
            
            post.save()
            post.refresh_from_db() 
            
            return JsonResponse({
                'score': score,
                'average_rating': post.average_rating,
                'rating_count': post.rating_count
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def submit_comment(request, post_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("Must be an AJAX request.")
        
    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get('text', '').strip()

    if not text:
        return HttpResponseBadRequest("Comment cannot be empty.")
        
    try:
        new_comment = Comment.objects.create(user=request.user, post=post, text=text)
        html_comment = render_to_string('recipes/partials/comment_fragment.html', {'comment': new_comment})
        return JsonResponse({
            'success': True,
            'comment_html': html_comment,
            'comments_count': post.comments.count()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def toggle_follow(request, author_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("Must be an AJAX request.")

    target_user = get_object_or_404(User, id=author_id)
    if request.user == target_user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    is_following = False
    try:
        follow_query = Follow.objects.filter(follower=request.user, followed=target_user)
        if follow_query.exists():
            follow_query.delete()
            is_following = False
        else:
            Follow.objects.create(follower=request.user, followed=target_user)
            is_following = True
        return JsonResponse({'is_following': is_following})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('feed')
        else:
            print("Form Errors:", form.errors)
            
    return redirect('feed')