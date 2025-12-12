"""Tests for the Post model."""
from django.test import TestCase
from recipes.models import User, Post, Like, Save, Comment


class PostModelTestCase(TestCase):
    """Tests for the Post model."""

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
            title="Test Post",
            caption="Test caption",
        )

    def test_post_str_returns_title(self):
        """Test that Post _str_ returns the title."""
        self.assertEqual(str(self.post), "Test Post")

    def test_total_likes_returns_zero_when_no_likes(self):
        """Test that total_likes returns 0 when no likes exist."""
        self.assertEqual(self.post.total_likes(), 0)

    def test_total_likes_returns_correct_count(self):
        """Test that total_likes returns correct count."""
        Like.objects.create(user=self.user, post=self.post)
        Like.objects.create(user=self.other_user, post=self.post)
        self.assertEqual(self.post.total_likes(), 2)

    def test_total_comments_returns_zero_when_no_comments(self):
        """Test that total_comments returns 0 when no comments exist."""
        self.assertEqual(self.post.total_comments(), 0)

    def test_total_comments_returns_correct_count(self):
        """Test that total_comments returns correct count."""
        Comment.objects.create(user=self.user, post=self.post, text="Comment 1")
        Comment.objects.create(user=self.other_user, post=self.post, text="Comment 2")
        self.assertEqual(self.post.total_comments(), 2)

    def test_is_liked_by_returns_true_when_liked(self):
        """Test that is_liked_by returns True when user has liked."""
        Like.objects.create(user=self.user, post=self.post)
        self.assertTrue(self.post.is_liked_by(self.user))

    def test_is_liked_by_returns_false_when_not_liked(self):
        """Test that is_liked_by returns False when user hasn't liked."""
        self.assertFalse(self.post.is_liked_by(self.user))

    def test_is_saved_by_returns_true_when_saved(self):
        """Test that is_saved_by returns True when user has saved."""
        Save.objects.create(user=self.user, post=self.post)
        self.assertTrue(self.post.is_saved_by(self.user))

    def test_is_saved_by_returns_false_when_not_saved(self):
        """Test that is_saved_by returns False when user hasn't saved."""
        self.assertFalse(self.post.is_saved_by(self.user))

    def test_average_rating_returns_zero_when_no_ratings(self):
        """Test that average_rating returns 0 when no ratings exist."""
        self.assertEqual(self.post.average_rating, 0.0)

    def test_average_rating_returns_correct_value(self):
        """Test that average_rating returns correct calculated value."""
        self.post.rating_total_score = 15
        self.post.rating_count = 3
        self.post.save()
        self.assertEqual(self.post.average_rating, 5.0)

    def test_average_rating_rounds_correctly(self):
        """Test that average_rating rounds to one decimal place."""
        self.post.rating_total_score = 10
        self.post.rating_count = 3
        self.post.save()
        self.assertEqual(self.post.average_rating, 3.3)

    def test_default_difficulty_is_easy(self):
        """Test that default difficulty is Easy."""
        post = Post.objects.create(
            author=self.user,
            title="New Post",
        )
        self.assertEqual(post.difficulty, "Easy")

    def test_default_servings_is_one(self):
        """Test that default servings is 1."""
        post = Post.objects.create(
            author=self.user,
            title="New Post",
        )
        self.assertEqual(post.servings, 1)