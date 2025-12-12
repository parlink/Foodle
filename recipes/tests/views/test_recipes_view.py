"""Tests for the recipes view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe
from recipes.views.recipes_view import parse_time_to_minutes


class ParseTimeToMinutesTestCase(TestCase):
    """Tests for parse_time_to_minutes utility function."""

    def test_parse_minutes_only(self):
        """Test parsing time with only minutes."""
        self.assertEqual(parse_time_to_minutes('25 minutes'), 25)
        self.assertEqual(parse_time_to_minutes('45 minutes'), 45)

    def test_parse_hours_only(self):
        """Test parsing time with only hours."""
        self.assertEqual(parse_time_to_minutes('1 hours'), 60)
        self.assertEqual(parse_time_to_minutes('2 hours'), 120)

    def test_parse_hours_and_minutes(self):
        """Test parsing time with hours and minutes."""
        self.assertEqual(parse_time_to_minutes('1 hours 30 minutes'), 90)
        self.assertEqual(parse_time_to_minutes('2 hours 15 minutes'), 135)

    def test_parse_with_uppercase(self):
        """Test parsing time with uppercase letters."""
        self.assertEqual(parse_time_to_minutes('25 MINUTES'), 25)
        self.assertEqual(parse_time_to_minutes('1 HOURS 30 MINUTES'), 90)

    def test_parse_with_extra_whitespace(self):
        """Test parsing time with extra whitespace."""
        self.assertEqual(parse_time_to_minutes('  25 minutes  '), 25)
        self.assertEqual(parse_time_to_minutes('  1 hours 30 minutes  '), 90)

    def test_parse_none_input(self):
        """Test parsing None returns None."""
        self.assertIsNone(parse_time_to_minutes(None))

    def test_parse_empty_string(self):
        """Test parsing empty string returns None."""
        self.assertIsNone(parse_time_to_minutes(''))

    def test_parse_invalid_format(self):
        """Test parsing invalid format returns None."""
        self.assertIsNone(parse_time_to_minutes('invalid'))
        self.assertIsNone(parse_time_to_minutes('25'))
        self.assertIsNone(parse_time_to_minutes('abc minutes'))

    def test_parse_malformed_hours_minutes(self):
        """Test parsing malformed hours and minutes returns None."""
        self.assertIsNone(parse_time_to_minutes('1 hours 30 seconds'))
        self.assertIsNone(parse_time_to_minutes('1 minute 30 minutes'))


class RecipesViewTestCase(TestCase):
    """Tests for the recipes view."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse('recipes')
        
        # Create test recipes
        self.recipe1 = Recipe.objects.create(
            name='Quick Pasta',
            total_time='20 minutes',
            servings=4,
            difficulty='Easy',
            ingredients='Pasta, sauce',
            method='Boil and mix'
        )
        
        self.recipe2 = Recipe.objects.create(
            name='Slow Roast',
            total_time='2 hours 30 minutes',
            servings=6,
            difficulty='Hard',
            ingredients='Beef, vegetables',
            method='Roast slowly'
        )
        
        self.recipe3 = Recipe.objects.create(
            name='Simple Salad',
            total_time='10 minutes',
            servings=2,
            difficulty='Easy',
            ingredients='Lettuce, tomato, dressing',
            method='Mix ingredients'
        )

    def test_recipes_url(self):
        """Test that recipes URL is accessible."""
        self.assertEqual(self.url, '/recipes/')

    def test_get_recipes_no_filter(self):
        """Test that recipes page loads with no filters."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')

    def test_recipes_context_contains_page_obj(self):
        """Test that context contains page_obj."""
        response = self.client.get(self.url)
        self.assertIn('page_obj', response.context)

    def test_recipes_context_contains_search_query(self):
        """Test that context contains search_query."""
        response = self.client.get(self.url)
        self.assertIn('search_query', response.context)
        self.assertEqual(response.context['search_query'], '')

    def test_recipes_context_contains_active_sort(self):
        """Test that context contains active_sort."""
        response = self.client.get(self.url)
        self.assertIn('active_sort', response.context)
        self.assertEqual(response.context['active_sort'], '')

    def test_recipes_search_by_name(self):
        """Test searching recipes by name."""
        response = self.client.get(self.url, {'q': 'Pasta'})
        recipes = list(response.context['page_obj'])
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, 'Quick Pasta')

    def test_recipes_search_by_ingredients(self):
        """Test searching recipes by ingredients."""
        response = self.client.get(self.url, {'q': 'Beef'})
        recipes = list(response.context['page_obj'])
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, 'Slow Roast')

    def test_recipes_search_by_method(self):
        """Test searching recipes by method."""
        response = self.client.get(self.url, {'q': 'Roast'})
        recipes = list(response.context['page_obj'])
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, 'Slow Roast')

    def test_recipes_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        response = self.client.get(self.url, {'q': 'pasta'})
        recipes = list(response.context['page_obj'])
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, 'Quick Pasta')

    def test_recipes_search_no_results(self):
        """Test searching with no results."""
        response = self.client.get(self.url, {'q': 'Nonexistent'})
        recipes = list(response.context['page_obj'])
        self.assertEqual(len(recipes), 0)

    def test_recipes_sort_by_quick_meals(self):
        """Test sorting recipes by quick meals (<=30 minutes)."""
        response = self.client.get(self.url, {'sort_by': 'quick-meals'})
        recipes = list(response.context['page_obj'])
        # Should contain only quick recipes
        for recipe in recipes:
            self.assertIn(recipe.id, [self.recipe1.id, self.recipe3.id])

    def test_recipes_sort_by_servings(self):
        """Test sorting recipes by servings (descending)."""
        response = self.client.get(self.url, {'sort_by': 'servings'})
        recipes = list(response.context['page_obj'])
        # First should be Slow Roast (6 servings)
        self.assertEqual(recipes[0].servings, 6)

    def test_recipes_sort_by_difficulty(self):
        """Test sorting recipes by difficulty (ascending)."""
        response = self.client.get(self.url, {'sort_by': 'difficulty'})
        recipes = list(response.context['page_obj'])
        # First should be Easy recipes
        self.assertEqual(recipes[0].difficulty, 'Easy')

    def test_recipes_sort_by_rating(self):
        """Test sorting recipes by rating."""
        response = self.client.get(self.url, {'sort_by': 'rating'})
        recipes = list(response.context['page_obj'])
        # Should not crash
        self.assertEqual(response.status_code, 200)

    def test_recipes_search_and_sort_combined(self):
        """Test combining search and sort."""
        response = self.client.get(self.url, {
            'q': 'Roast',
            'sort_by': 'difficulty'
        })
        recipes = list(response.context['page_obj'])
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, 'Slow Roast')

    def test_recipes_pagination_first_page(self):
        """Test pagination on first page."""
        response = self.client.get(self.url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)

    def test_recipes_pagination_invalid_page(self):
        """Test pagination with invalid page number."""
        response = self.client.get(self.url, {'page': 999})
        # Should return the last page instead of error
        self.assertEqual(response.status_code, 200)

    def test_recipes_active_sort_context(self):
        """Test that active_sort is set in context."""
        response = self.client.get(self.url, {'sort_by': 'quick-meals'})
        self.assertEqual(response.context['active_sort'], 'quick-meals')

    def test_recipes_search_query_context(self):
        """Test that search_query is set in context."""
        response = self.client.get(self.url, {'q': 'test query'})
        self.assertEqual(response.context['search_query'], 'test query')
