"""Tests for the Tag model."""
from django.test import TestCase
from recipes.models import Tag


class TagModelTestCase(TestCase):
    """Tests for the Tag model."""

    def test_tag_str_returns_name(self):
        """Test that Tag _str_ returns the tag name."""
        tag = Tag.objects.create(name='Vegan')
        self.assertEqual(str(tag), 'Vegan')

    def test_tag_can_be_created(self):
        """Test that a Tag can be created."""
        tag = Tag.objects.create(name='Gluten Free')
        self.assertTrue(Tag.objects.filter(name='Gluten Free').exists())
        self.assertEqual(tag.name, 'Gluten Free')

    def test_tag_name_max_length(self):
        """Test that tag name has correct max length."""
        tag = Tag.objects.create(name='a' * 50)
        self.assertEqual(len(tag.name), 50)