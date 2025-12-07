### Helper function and classes go here.

from django.db.models import QuerySet

def is_liked_util(post_id: int, liked_posts_set: set) -> bool:
    """Checks if the post ID is in the set of liked posts."""
    return post_id in liked_posts_set

def is_saved_util(post_id: int, saved_posts_set: set) -> bool:
    """Checks if the post ID is in the set of saved posts."""
    return post_id in saved_posts_set

def is_followed_util(author_id: int, is_following_map: dict) -> bool:
    """Checks if the author ID is in the following map."""
    return is_following_map.get(author_id, False)

def get_rating_util(post_id: int, user_ratings_dict: dict) -> int:
    """Returns the user's rating score for a given post ID."""
    return user_ratings_dict.get(post_id, 0)