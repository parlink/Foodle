from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F, Q, Avg
from django.template.loader import render_to_string
from recipes.models import Post, Like, Comment, Save, Rating, Follow, User, Tag
from recipes.forms.post_form import PostForm 
from recipes.helpers import is_liked_util, is_saved_util, is_followed_util, get_rating_util

@login_required
def feed(request):
    show_followed_only = request.GET.get('followed') == 'true'
    sort_by = request.GET.get('sort', 'newest')  # NEW
    cuisine_filter = request.GET.get('cuisine', '')  # NEW
    tag_filter = request.GET.get('tag', '')  # NEW

    if show_followed_only:
        followed_ids = Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)
        posts_following = Post.objects.filter(author__in=followed_ids).select_related('author').prefetch_related('tags', 'comments__user')
        my_posts = Post.objects.filter(author=request.user).select_related('author').prefetch_related('tags', 'comments__user')
        posts = posts_following.union(my_posts)
    else:
        posts = Post.objects.all().select_related('author').prefetch_related('tags', 'comments__user')
    if cuisine_filter:
        posts = posts.filter(cuisine=cuisine_filter)
    if tag_filter:
        posts = posts.filter(tags__name=tag_filter)
    if sort_by == 'top_rated':
        posts = posts.annotate(calculated_average=Avg('ratings__score')).order_by('-calculated_average')
    else:
        posts = posts.order_by('-created_at')

    saved_posts = Post.objects.filter(saves__user=request.user).select_related('author').prefetch_related('tags', 'comments__user').order_by('-saves__created_at')

    main_posts_list = list(posts)
    saved_posts_list = list(saved_posts)
    all_posts_combined = main_posts_list + saved_posts_list
    
    post_ids = {p.id for p in all_posts_combined} 
    
    liked_posts_set = set(Like.objects.filter(user=request.user, post_id__in=post_ids).values_list('post_id', flat=True))
    saved_posts_set = set(Save.objects.filter(user=request.user, post_id__in=post_ids).values_list('post_id', flat=True))
    user_ratings_dict = {r.post_id: r.score for r in Rating.objects.filter(user=request.user, post_id__in=post_ids)}
    
    author_ids = {p.author_id for p in all_posts_combined}
    following_status = Follow.objects.filter(follower=request.user, followed_id__in=author_ids).values_list('followed_id', flat=True)
    is_following_map = {author_id: True for author_id in following_status}
    
    def attach_attrs(post_list):
        for post in post_list:
            post.is_liked_by_user = post.id in liked_posts_set
            post.is_saved_by_user = post.id in saved_posts_set
            post.user_rating_score = user_ratings_dict.get(post.id, 0)
            post.is_followed_by_user = is_following_map.get(post.author_id, False)

    attach_attrs(main_posts_list)
    attach_attrs(saved_posts_list)

    form = PostForm()

    all_cuisines = [c[0] for c in Post.CUISINE_CHOICES]
    popular_tags = Tag.objects.all()[:10]

    context = {
        'posts': main_posts_list,
        'saved_posts': saved_posts_list,
        'show_followed_only': show_followed_only,
        'form': form,
        'all_cuisines': all_cuisines,
        'popular_tags': popular_tags,
        'current_sort': sort_by,
        'current_cuisine': cuisine_filter,
        'current_tag': tag_filter,
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
            
            current_count = post.likes.count()
            
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

            return JsonResponse({'saved': saved})
        else:
            Save.objects.create(user=request.user, post=post)
            saved = True
            
            sidebar_html = render_to_string('recipes/partials/saved_card.html', {'post': post}, request=request)
            
            return JsonResponse({
                'saved': saved, 
                'sidebar_html': sidebar_html
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.user == post.author:
        post.delete()
        
    return redirect('feed')

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

@login_required
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
            # Form is invalid, redirect to feed
            pass
            
    return redirect('feed')

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    post.is_liked_by_user = Like.objects.filter(user=request.user, post=post).exists()
    post.is_saved_by_user = Save.objects.filter(user=request.user, post=post).exists()
    post.is_followed_by_user = Follow.objects.filter(follower=request.user, followed=post.author).exists()
    
    user_rating = Rating.objects.filter(user=request.user, post=post).first()
    post.user_rating_score = user_rating.score if user_rating else 0

    return render(request, 'recipes/post_detail.html', {'post': post})

def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    #Security check: Ensure only the author can edit
    if request.user != post.author:
        return redirect('feed')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            #If request is AJAX, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('feed')
    
    #If using a separate page (fallback)
    return redirect('feed')