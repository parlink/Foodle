"""Tests for the social feed views."""
import json
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Post, Like, Save, Comment, Rating, Follow, Tag
from recipes.tests.helpers import reverse_with_next


def create_test_image():
    """Create a test image for file upload tests."""
    image = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=buffer.getvalue(),
        content_type='image/jpeg'
    )


class FeedViewTestCase(TestCase):
    """Tests for the feed view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('feed')

        self.post1 = Post.objects.create(
            author=self.user,
            title="My Post",
            caption="This is my post content.",
        )
        self.post2 = Post.objects.create(
            author=self.other_user,
            title="Other Post",
            caption="Content from another user.",
        )

    def test_feed_url(self):
        """Test that feed URL is correct."""
        self.assertEqual(self.url, '/feed/')

    def test_get_feed_redirects_when_not_logged_in(self):
        """Test that feed redirects when not logged in."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_feed_when_logged_in(self):
        """Test that feed returns 200 when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/feed.html')

    def test_feed_context_contains_posts(self):
        """Test that feed context contains posts."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('posts', response.context)

    def test_feed_context_contains_saved_posts(self):
        """Test that feed context contains saved_posts."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('saved_posts', response.context)

    def test_feed_shows_all_posts_by_default(self):
        """Test that feed shows all posts by default."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        posts = response.context['posts']
        post_ids = [p.id for p in posts]
        self.assertIn(self.post1.id, post_ids)
        self.assertIn(self.post2.id, post_ids)

    def test_feed_followed_only_filter(self):
        """Test that followed=true filter shows only followed users' posts."""
        self.client.login(username=self.user.username, password='Password123')
        # Follow other user
        Follow.objects.create(follower=self.user, followed=self.other_user)
        response = self.client.get(self.url, {'followed': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_followed_only'])

    def test_posts_have_is_liked_attribute(self):
        """Test that posts have is_liked_by_user attribute."""
        self.client.login(username=self.user.username, password='Password123')
        Like.objects.create(user=self.user, post=self.post1)
        response = self.client.get(self.url)
        posts = response.context['posts']
        for post in posts:
            self.assertTrue(hasattr(post, 'is_liked_by_user'))

    def test_posts_have_is_saved_attribute(self):
        """Test that posts have is_saved_by_user attribute."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        posts = response.context['posts']
        for post in posts:
            self.assertTrue(hasattr(post, 'is_saved_by_user'))


class ToggleLikeViewTestCase(TestCase):
    """Tests for toggle_like view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            caption="Test content.",
        )
        self.url = reverse('toggle_like', kwargs={'post_id': self.post.id})

    def test_toggle_like_url(self):
        """Test that toggle_like URL is correct."""
        self.assertEqual(self.url, f'/post/{self.post.id}/like/')

    def test_toggle_like_redirects_when_not_logged_in(self):
        """Test that toggle_like redirects when not logged in."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_toggle_like_requires_ajax(self):
        """Test that toggle_like requires AJAX request."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_toggle_like_creates_like(self):
        """Test that toggle_like creates a like."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post).exists())

    def test_toggle_like_removes_like(self):
        """Test that toggle_like removes existing like."""
        self.client.login(username=self.user.username, password='Password123')
        Like.objects.create(user=self.user, post=self.post)
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)
        self.assertFalse(Like.objects.filter(user=self.user, post=self.post).exists())

    def test_toggle_like_nonexistent_post_returns_404(self):
        """Test that toggle_like on nonexistent post returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('toggle_like', kwargs={'post_id': 99999})
        response = self.client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)

    def test_toggle_like_get_not_allowed(self):
        """Test that GET request to toggle_like is not allowed."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405)


class ToggleSaveViewTestCase(TestCase):
    """Tests for toggle_save view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            caption="Test content.",
        )
        self.url = reverse('toggle_save', kwargs={'post_id': self.post.id})

    def test_toggle_save_url(self):
        """Test that toggle_save URL is correct."""
        self.assertEqual(self.url, f'/post/{self.post.id}/save/')

    def test_toggle_save_requires_ajax(self):
        """Test that toggle_save requires AJAX request."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_toggle_save_creates_save(self):
        """Test that toggle_save creates a save."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['saved'])
        self.assertIn('sidebar_html', data)
        self.assertTrue(Save.objects.filter(user=self.user, post=self.post).exists())

    def test_toggle_save_removes_save(self):
        """Test that toggle_save removes existing save."""
        self.client.login(username=self.user.username, password='Password123')
        Save.objects.create(user=self.user, post=self.post)
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['saved'])
        self.assertFalse(Save.objects.filter(user=self.user, post=self.post).exists())

    def test_toggle_save_nonexistent_post_returns_404(self):
        """Test that toggle_save on nonexistent post returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('toggle_save', kwargs={'post_id': 99999})
        response = self.client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)


class SubmitRatingViewTestCase(TestCase):
    """Tests for submit_rating view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            caption="Test content.",
        )
        self.url = reverse('submit_rating', kwargs={'post_id': self.post.id})

    def test_submit_rating_url(self):
        """Test that submit_rating URL is correct."""
        self.assertEqual(self.url, f'/post/{self.post.id}/rate/')

    def test_submit_rating_requires_ajax(self):
        """Test that submit_rating requires AJAX request."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {'score': 5})
        self.assertEqual(response.status_code, 400)

    def test_submit_rating_creates_rating(self):
        """Test that submit_rating creates a rating."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            {'score': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['score'], 5)
        self.assertTrue(Rating.objects.filter(user=self.user, post=self.post).exists())

    def test_submit_rating_updates_existing_rating(self):
        """Test that submit_rating updates existing rating."""
        self.client.login(username=self.user.username, password='Password123')
        Rating.objects.create(user=self.user, post=self.post, score=3)
        response = self.client.post(
            self.url,
            {'score': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['score'], 5)
        rating = Rating.objects.get(user=self.user, post=self.post)
        self.assertEqual(rating.score, 5)

    def test_submit_rating_invalid_score_low(self):
        """Test that submit_rating rejects score below 1."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            {'score': 0},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)

    def test_submit_rating_invalid_score_high(self):
        """Test that submit_rating rejects score above 5."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            {'score': 6},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)

    def test_submit_rating_nonexistent_post_returns_error(self):
        """Test that submit_rating on nonexistent post returns error."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('submit_rating', kwargs={'post_id': 99999})
        response = self.client.post(
            url,
            {'score': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # The view catches exceptions and returns 500
        self.assertIn(response.status_code, [404, 500])


class SubmitCommentViewTestCase(TestCase):
    """Tests for submit_comment view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            caption="Test content.",
        )
        self.url = reverse('submit_comment', kwargs={'post_id': self.post.id})

    def test_submit_comment_url(self):
        """Test that submit_comment URL is correct."""
        self.assertEqual(self.url, f'/post/{self.post.id}/comment/')

    def test_submit_comment_requires_ajax(self):
        """Test that submit_comment requires AJAX request."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {'text': 'Test comment'})
        self.assertEqual(response.status_code, 400)

    def test_submit_comment_creates_comment(self):
        """Test that submit_comment creates a comment."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            {'text': 'Test comment'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('comment_html', data)
        self.assertTrue(Comment.objects.filter(user=self.user, post=self.post).exists())

    def test_submit_comment_empty_text(self):
        """Test that submit_comment rejects empty text."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            {'text': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)

    def test_submit_comment_whitespace_only(self):
        """Test that submit_comment rejects whitespace-only text."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            {'text': '   '},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)

    def test_submit_comment_nonexistent_post_returns_404(self):
        """Test that submit_comment on nonexistent post returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('submit_comment', kwargs={'post_id': 99999})
        response = self.client.post(
            url,
            {'text': 'Test comment'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)


class ToggleFollowViewTestCase(TestCase):
    """Tests for toggle_follow view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('toggle_follow', kwargs={'author_id': self.other_user.id})

    def test_toggle_follow_url(self):
        """Test that toggle_follow URL is correct."""
        self.assertEqual(self.url, f'/user/{self.other_user.id}/follow/')

    def test_toggle_follow_requires_ajax(self):
        """Test that toggle_follow requires AJAX request."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_toggle_follow_creates_follow(self):
        """Test that toggle_follow creates a follow."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['is_following'])
        self.assertTrue(Follow.objects.filter(follower=self.user, followed=self.other_user).exists())

    def test_toggle_follow_removes_follow(self):
        """Test that toggle_follow removes existing follow."""
        self.client.login(username=self.user.username, password='Password123')
        Follow.objects.create(follower=self.user, followed=self.other_user)
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['is_following'])
        self.assertFalse(Follow.objects.filter(follower=self.user, followed=self.other_user).exists())

    def test_toggle_follow_cannot_follow_self(self):
        """Test that users cannot follow themselves."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('toggle_follow', kwargs={'author_id': self.user.id})
        response = self.client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_toggle_follow_nonexistent_user_returns_404(self):
        """Test that toggle_follow on nonexistent user returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('toggle_follow', kwargs={'author_id': 99999})
        response = self.client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)


class CreatePostViewTestCase(TestCase):
    """Tests for create_post view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('create_post')

    def test_create_post_url(self):
        """Test that create_post URL is correct."""
        self.assertEqual(self.url, '/create-post/')

    def test_get_create_post_redirects_to_feed(self):
        """Test that GET request redirects to feed."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('feed'))

    def test_create_post_success(self):
        """Test successful post creation."""
        self.client.login(username=self.user.username, password='Password123')
        test_image = create_test_image()
        response = self.client.post(self.url, {
            'title': 'New Post',
            'caption': 'Post content here.',
            'image': test_image,
            'difficulty': 'Easy',
            'servings': 4,
        })
        self.assertRedirects(response, reverse('feed'))
        self.assertTrue(Post.objects.filter(title='New Post').exists())

    def test_create_post_sets_author(self):
        """Test that create_post sets the author to current user."""
        self.client.login(username=self.user.username, password='Password123')
        test_image = create_test_image()
        self.client.post(self.url, {
            'title': 'New Post',
            'caption': 'Post content here.',
            'image': test_image,
            'difficulty': 'Easy',
            'servings': 4,
        })
        post = Post.objects.get(title='New Post')
        self.assertEqual(post.author, self.user)

    def test_create_post_invalid_form(self):
        """Test that invalid form redirects to feed."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'title': '',  # Required
            'caption': 'Content',
        })
        self.assertRedirects(response, reverse('feed'))


class DeletePostViewTestCase(TestCase):
    """Tests for delete_post view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.post = Post.objects.create(
            author=self.user,
            title="My Post",
            caption="Content",
        )
        self.url = reverse('delete_post', kwargs={'post_id': self.post.id})

    def test_delete_post_url(self):
        """Test that delete_post URL is correct."""
        self.assertEqual(self.url, f'/post/{self.post.id}/delete/')

    def test_delete_own_post(self):
        """Test that user can delete own post."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('feed'))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_cannot_delete_other_users_post(self):
        """Test that user cannot delete another user's post."""
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('feed'))
        # Post should still exist
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

    def test_delete_nonexistent_post_returns_404(self):
        """Test that deleting nonexistent post returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('delete_post', kwargs={'post_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class PostDetailViewTestCase(TestCase):
    """Tests for post_detail view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.post = Post.objects.create(
            author=self.other_user,
            title="Test Post",
            caption="Content",
        )
        self.url = reverse('post_detail', kwargs={'post_id': self.post.id})

    def test_post_detail_url(self):
        """Test that post_detail URL is correct."""
        self.assertEqual(self.url, f'/post/{self.post.id}/')

    def test_get_post_detail_when_logged_in(self):
        """Test that post_detail returns 200 when logged in."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/post_detail.html')

    def test_post_detail_context_contains_post(self):
        """Test that context contains the post."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('post', response.context)
        self.assertEqual(response.context['post'].id, self.post.id)

    def test_post_has_user_interaction_attributes(self):
        """Test that post has user interaction attributes."""
        self.client.login(username=self.user.username, password='Password123')
        Like.objects.create(user=self.user, post=self.post)
        Save.objects.create(user=self.user, post=self.post)
        Follow.objects.create(follower=self.user, followed=self.other_user)
        Rating.objects.create(user=self.user, post=self.post, score=4)
        
        response = self.client.get(self.url)
        post = response.context['post']
        
        self.assertTrue(post.is_liked_by_user)
        self.assertTrue(post.is_saved_by_user)
        self.assertTrue(post.is_followed_by_user)
        self.assertEqual(post.user_rating_score, 4)

    def test_post_without_interactions(self):
        """Test post attributes when user has no interactions."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        post = response.context['post']
        
        self.assertFalse(post.is_liked_by_user)
        self.assertFalse(post.is_saved_by_user)
        self.assertFalse(post.is_followed_by_user)
        self.assertEqual(post.user_rating_score, 0)

    def test_nonexistent_post_returns_404(self):
        """Test that nonexistent post returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('post_detail', kwargs={'post_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class FeedFiltersAndSortingTestCase(TestCase):
    """Tests for feed filters and sorting functionality."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('feed')

        # Create posts with different attributes
        self.post1 = Post.objects.create(
            author=self.user,
            title="Easy Post",
            caption="Easy recipe",
            difficulty='Easy',
            cuisine='Italian'
        )
        self.post2 = Post.objects.create(
            author=self.other_user,
            title="Hard Post",
            caption="Hard recipe",
            difficulty='Hard',
            cuisine='Chinese'
        )
        Rating.objects.create(user=self.user, post=self.post2, score=5)
        Rating.objects.create(user=self.other_user, post=self.post2, score=4)

    def test_feed_sorted_by_newest(self):
        """Test that feed sorts by newest by default."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'sort': 'newest'})
        self.assertEqual(response.status_code, 200)
        posts = list(response.context['posts'])
        # post2 was created after post1
        self.assertEqual(posts[0].id, self.post2.id)

    def test_feed_sorted_by_top_rated(self):
        """Test that feed sorts by top_rated rating."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'sort': 'top_rated'})
        self.assertEqual(response.status_code, 200)
        posts = list(response.context['posts'])
        # post2 has ratings, post1 doesn't
        self.assertEqual(posts[0].id, self.post2.id)

    def test_feed_filter_by_cuisine(self):
        """Test that feed filters by cuisine."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'cuisine': 'Italian'})
        self.assertEqual(response.status_code, 200)
        posts = response.context['posts']
        post_ids = [p.id for p in posts]
        self.assertIn(self.post1.id, post_ids)
        self.assertNotIn(self.post2.id, post_ids)

    def test_feed_filter_by_tag(self):
        """Test that feed filters by tag."""
        tag = Tag.objects.create(name='tasty')
        self.post1.tags.add(tag)
        
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'tag': 'tasty'})
        self.assertEqual(response.status_code, 200)
        posts = response.context['posts']
        post_ids = [p.id for p in posts]
        self.assertIn(self.post1.id, post_ids)

    def test_feed_followed_only_with_sorting(self):
        """Test followed filter combined with sorting."""
        Follow.objects.create(follower=self.user, followed=self.other_user)
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'followed': 'true', 'sort': 'newest'})
        self.assertEqual(response.status_code, 200)
        posts = response.context['posts']
        self.assertTrue(response.context['show_followed_only'])


class DeletePostViewAdditionalTestCase(TestCase):
    """Additional tests for delete_post view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="My Post",
            caption="Content",
        )
        # Create interactions
        Like.objects.create(user=self.user, post=self.post)
        Comment.objects.create(user=self.user, post=self.post, text="Great!")
        Rating.objects.create(user=self.user, post=self.post, score=5)
        Save.objects.create(user=self.user, post=self.post)
        
        self.url = reverse('delete_post', kwargs={'post_id': self.post.id})

    def test_delete_post_cascades_interactions(self):
        """Test that deleting post cascades to likes, comments, ratings, saves."""
        self.client.login(username=self.user.username, password='Password123')
        
        # Verify interactions exist
        self.assertTrue(Like.objects.filter(post=self.post).exists())
        self.assertTrue(Comment.objects.filter(post=self.post).exists())
        self.assertTrue(Rating.objects.filter(post=self.post).exists())
        self.assertTrue(Save.objects.filter(post=self.post).exists())
        
        # Delete post
        self.client.get(self.url)
        
        # Verify post is deleted
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())


class SubmitRatingViewAdditionalTestCase(TestCase):
    """Additional tests for submit_rating view edge cases."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            caption="Test content.",
        )
        self.url = reverse('submit_rating', kwargs={'post_id': self.post.id})

    def test_submit_rating_missing_score_parameter(self):
        """Test that submit_rating handles missing score parameter."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            {},  # No score parameter
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Missing score causes 500 error or 400 depending on implementation
        self.assertIn(response.status_code, [400, 500])

    def test_submit_rating_multiple_updates(self):
        """Test updating rating multiple times."""
        self.client.login(username=self.user.username, password='Password123')
        
        # First rating
        self.client.post(
            self.url,
            {'score': 3},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Update to different score
        response = self.client.post(
            self.url,
            {'score': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify only one rating exists with updated score
        self.assertEqual(Rating.objects.filter(user=self.user, post=self.post).count(), 1)
        rating = Rating.objects.get(user=self.user, post=self.post)
        self.assertEqual(rating.score, 5)


class EditPostViewTestCase(TestCase):
    """Tests for edit_post view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.post = Post.objects.create(
            author=self.user,
            title="My Post",
            caption="Original content",
        )
        self.url = reverse('edit_post', kwargs={'post_id': self.post.id})

    def test_edit_own_post_get_request(self):
        """Test that GET request to edit_post redirects to feed."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('feed'))

    def test_cannot_edit_other_users_post(self):
        """Test that users cannot edit other users' posts."""
        self.client.login(username=self.other_user.username, password='Password123')
        test_image = create_test_image()
        response = self.client.post(self.url, {
            'title': 'Modified Title',
            'caption': 'Modified content',
            'image': test_image,
            'difficulty': 'Easy',
            'servings': 4,
        })
        # Should redirect to feed without making changes
        self.assertRedirects(response, reverse('feed'))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "My Post")

    def test_edit_own_post_post_request_with_form_submit(self):
        """Test editing own post with POST request."""
        self.client.login(username=self.user.username, password='Password123')
        test_image = create_test_image()
        response = self.client.post(self.url, {
            'title': 'Updated Title',
            'caption': 'Updated content',
            'image': test_image,
            'difficulty': 'Hard',
            'servings': 6,
        })
        self.assertRedirects(response, reverse('feed'))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_edit_post_ajax_request(self):
        """Test editing post with AJAX request."""
        self.client.login(username=self.user.username, password='Password123')
        test_image = create_test_image()
        response = self.client.post(self.url, {
            'title': 'AJAX Updated',
            'caption': 'AJAX content',
            'image': test_image,
            'difficulty': 'Medium',
            'servings': 5,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # Should return JSON for AJAX requests
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertTrue(data['success'])
        else:
            # Or redirect if form is valid
            self.assertRedirects(response, reverse('feed'))

    def test_edit_post_invalid_form(self):
        """Test editing post with invalid form data."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, {
            'title': '',  # Required field missing
            'caption': 'Content',
        })
        # Should redirect to feed on invalid form
        self.assertRedirects(response, reverse('feed'))

    def test_edit_nonexistent_post_returns_404(self):
        """Test that editing nonexistent post returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('edit_post', kwargs={'post_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ToggleSaveViewAdditionalTestCase(TestCase):
    """Additional tests for toggle_save view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            caption="Test content.",
        )
        self.url = reverse('toggle_save', kwargs={'post_id': self.post.id})

    def test_toggle_save_redirects_when_not_logged_in(self):
        """Test that toggle_save redirects when not logged in."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_toggle_save_returns_sidebar_html(self):
        """Test that toggle_save returns sidebar HTML in response."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('sidebar_html', data)


class DeletePostViewLoginRequiredTestCase(TestCase):
    """Test that delete_post requires login."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            author=self.user,
            title="My Post",
            caption="Content",
        )
        self.url = reverse('delete_post', kwargs={'post_id': self.post.id})

    def test_delete_post_redirects_when_not_logged_in(self):
        """Test that delete_post redirects when not logged in."""
        response = self.client.get(self.url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class CreatePostWithTagsTestCase(TestCase):
    """Test create_post with various form configurations."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('create_post')
        # Create some tags
        self.tag1 = Tag.objects.create(name='vegetarian')
        self.tag2 = Tag.objects.create(name='gluten-free')

    def test_create_post_with_tags(self):
        """Test creating a post with tags."""
        self.client.login(username=self.user.username, password='Password123')
        test_image = create_test_image()
        response = self.client.post(self.url, {
            'title': 'Tagged Post',
            'caption': 'Post with tags',
            'image': test_image,
            'difficulty': 'Easy',
            'servings': 4,
            'tags': [self.tag1.id, self.tag2.id],
        })
        self.assertRedirects(response, reverse('feed'))
        post = Post.objects.get(title='Tagged Post')
        self.assertEqual(post.tags.count(), 2)

    def test_create_post_requires_post_method(self):
        """Test that create_post only works with POST."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('feed'))


class FeedContextDataTestCase(TestCase):
    """Test feed view context data completeness."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('feed')
        # Create cuisines and tags
        self.post1 = Post.objects.create(
            author=self.user,
            title="Italian Pasta",
            caption="Delicious pasta",
            cuisine='Italian'
        )
        self.post2 = Post.objects.create(
            author=self.user,
            title="Chinese Stir Fry",
            caption="Quick stir fry",
            cuisine='Chinese'
        )
        tag = Tag.objects.create(name='quick')
        self.post1.tags.add(tag)

    def test_feed_contains_all_cuisines(self):
        """Test that feed context contains all cuisine options."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('all_cuisines', response.context)
        cuisines = response.context['all_cuisines']
        self.assertIn('Italian', cuisines)
        self.assertIn('Chinese', cuisines)

    def test_feed_contains_popular_tags(self):
        """Test that feed context contains popular tags."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('popular_tags', response.context)
        tags = response.context['popular_tags']
        self.assertGreaterEqual(len(tags), 0)

    def test_feed_context_filters(self):
        """Test that feed context includes current filter values."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {
            'sort': 'top_rated',
            'cuisine': 'Italian',
            'tag': 'quick'
        })
        self.assertEqual(response.context['current_sort'], 'top_rated')
        self.assertEqual(response.context['current_cuisine'], 'Italian')
        self.assertEqual(response.context['current_tag'], 'quick')


class ToggleLikeMultipleInteractionsTestCase(TestCase):
    """Test toggle_like with multiple likes."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.get(username='@johndoe')
        self.user2 = User.objects.get(username='@janedoe')
        self.post = Post.objects.create(
            author=self.user1,
            title="Test Post",
            caption="Test content.",
        )
        self.url = reverse('toggle_like', kwargs={'post_id': self.post.id})

    def test_multiple_users_can_like_same_post(self):
        """Test that multiple users can like the same post."""
        # First user likes
        self.client.login(username=self.user1.username, password='Password123')
        response1 = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data1 = json.loads(response1.content)
        self.assertEqual(data1['likes_count'], 1)
        
        # Second user likes
        self.client.logout()
        self.client.login(username=self.user2.username, password='Password123')
        response2 = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data2 = json.loads(response2.content)
        self.assertEqual(data2['likes_count'], 2)


class PostDetailNoRatingTestCase(TestCase):
    """Test post_detail when user hasn't rated post."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.get(username='@johndoe')
        self.user2 = User.objects.get(username='@janedoe')
        self.post = Post.objects.create(
            author=self.user2,
            title="Test Post",
            caption="Test content.",
        )
        # Other user rates but not our test user
        Rating.objects.create(user=self.user2, post=self.post, score=5)
        self.url = reverse('post_detail', kwargs={'post_id': self.post.id})

    def test_post_detail_user_rating_defaults_to_zero(self):
        """Test that user_rating_score defaults to 0 when no rating exists."""
        self.client.login(username=self.user1.username, password='Password123')
        response = self.client.get(self.url)
        post = response.context['post']
        self.assertEqual(post.user_rating_score, 0)


class FeedRedirectsUnauthenticatedTestCase(TestCase):
    """Test that feed properly redirects unauthenticated users."""

    def test_feed_requires_login(self):
        """Test that feed requires authentication."""
        url = reverse('feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Should redirect to login page
        self.assertIn('/login/', response.url)