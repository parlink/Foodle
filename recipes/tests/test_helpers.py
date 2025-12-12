"""Tests for the helper functions in recipes/helpers.py."""
from django.test import TestCase
from recipes.helpers import (
    is_liked_util,
    is_saved_util,
    is_followed_util,
    get_rating_util,
)


class IsLikedUtilTestCase(TestCase):
    """Tests for the is_liked_util function."""

    def test_is_liked_util_returns_true_when_post_in_set(self):
        """is_liked_util should return True when post_id is in the set."""
        liked_posts_set = {1, 2, 3, 4, 5}
        result = is_liked_util(3, liked_posts_set)
        self.assertTrue(result)

    def test_is_liked_util_returns_false_when_post_not_in_set(self):
        """is_liked_util should return False when post_id is not in the set."""
        liked_posts_set = {1, 2, 3}
        result = is_liked_util(99, liked_posts_set)
        self.assertFalse(result)

    def test_is_liked_util_returns_false_for_empty_set(self):
        """is_liked_util should return False for empty set."""
        liked_posts_set = set()
        result = is_liked_util(1, liked_posts_set)
        self.assertFalse(result)


class IsSavedUtilTestCase(TestCase):
    """Tests for the is_saved_util function."""

    def test_is_saved_util_returns_true_when_post_in_set(self):
        """is_saved_util should return True when post_id is in the set."""
        saved_posts_set = {10, 20, 30}
        result = is_saved_util(20, saved_posts_set)
        self.assertTrue(result)

    def test_is_saved_util_returns_false_when_post_not_in_set(self):
        """is_saved_util should return False when post_id is not in the set."""
        saved_posts_set = {10, 20, 30}
        result = is_saved_util(50, saved_posts_set)
        self.assertFalse(result)

    def test_is_saved_util_returns_false_for_empty_set(self):
        """is_saved_util should return False for empty set."""
        saved_posts_set = set()
        result = is_saved_util(1, saved_posts_set)
        self.assertFalse(result)


class IsFollowedUtilTestCase(TestCase):
    """Tests for the is_followed_util function."""

    def test_is_followed_util_returns_true_when_author_in_map(self):
        """is_followed_util should return True when author_id is in the map with True."""
        is_following_map = {1: True, 2: True, 3: True}
        result = is_followed_util(2, is_following_map)
        self.assertTrue(result)

    def test_is_followed_util_returns_false_when_author_not_in_map(self):
        """is_followed_util should return False when author_id is not in the map."""
        is_following_map = {1: True, 2: True}
        result = is_followed_util(99, is_following_map)
        self.assertFalse(result)

    def test_is_followed_util_returns_false_for_empty_map(self):
        """is_followed_util should return False for empty map."""
        is_following_map = {}
        result = is_followed_util(1, is_following_map)
        self.assertFalse(result)

    def test_is_followed_util_returns_value_from_map(self):
        """is_followed_util should return the actual value from the map."""
        is_following_map = {1: True, 2: False}
        self.assertTrue(is_followed_util(1, is_following_map))
        self.assertFalse(is_followed_util(2, is_following_map))


class GetRatingUtilTestCase(TestCase):
    """Tests for the get_rating_util function."""

    def test_get_rating_util_returns_rating_when_post_in_dict(self):
        """get_rating_util should return rating when post_id is in the dict."""
        user_ratings_dict = {1: 5, 2: 4, 3: 3}
        result = get_rating_util(2, user_ratings_dict)
        self.assertEqual(result, 4)

    def test_get_rating_util_returns_zero_when_post_not_in_dict(self):
        """get_rating_util should return 0 when post_id is not in the dict."""
        user_ratings_dict = {1: 5, 2: 4}
        result = get_rating_util(99, user_ratings_dict)
        self.assertEqual(result, 0)

    def test_get_rating_util_returns_zero_for_empty_dict(self):
        """get_rating_util should return 0 for empty dict."""
        user_ratings_dict = {}
        result = get_rating_util(1, user_ratings_dict)
        self.assertEqual(result, 0)

    def test_get_rating_util_returns_various_ratings(self):
        """get_rating_util should return correct rating values."""
        user_ratings_dict = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
        for post_id in range(1, 6):
            self.assertEqual(get_rating_util(post_id, user_ratings_dict), post_id)
