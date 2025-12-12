"""Tests for the browse recipes view and parse_time_to_minutes function."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.views.recipes_view import parse_time_to_minutes


class ParseTimeToMinutesTestCase(TestCase):
    """Tests for the parse_time_to_minutes utility function."""

    def test_parse_time_returns_none_for_none_input(self):
        """parse_time_to_minutes should return None when given None."""
        result = parse_time_to_minutes(None)
        self.assertIsNone(result)

    def test_parse_time_returns_none_for_empty_string(self):
        """parse_time_to_minutes should return None when given empty string."""
        result = parse_time_to_minutes('')
        self.assertIsNone(result)

    def test_parse_time_returns_none_for_whitespace_only(self):
        """parse_time_to_minutes should return None for whitespace-only input."""
        result = parse_time_to_minutes('   ')
        self.assertIsNone(result)

    def test_parse_time_minutes_format(self):
        """parse_time_to_minutes should parse '25 minutes' correctly."""
        result = parse_time_to_minutes('25 minutes')
        self.assertEqual(result, 25)

    def test_parse_time_minutes_format_with_uppercase(self):
        """parse_time_to_minutes should handle uppercase input."""
        result = parse_time_to_minutes('30 MINUTES')
        self.assertEqual(result, 30)

    def test_parse_time_minutes_format_with_whitespace(self):
        """parse_time_to_minutes should handle leading/trailing whitespace."""
        result = parse_time_to_minutes('  15 minutes  ')
        self.assertEqual(result, 15)

    def test_parse_time_hours_format(self):
        """parse_time_to_minutes should parse '2 hours' correctly."""
        result = parse_time_to_minutes('2 hours')
        self.assertEqual(result, 120)

    def test_parse_time_one_hour_format(self):
        """parse_time_to_minutes should parse '1 hours' correctly."""
        result = parse_time_to_minutes('1 hours')
        self.assertEqual(result, 60)

    def test_parse_time_hours_and_minutes_format(self):
        """parse_time_to_minutes should parse '1 hours 30 minutes' correctly."""
        result = parse_time_to_minutes('1 hours 30 minutes')
        self.assertEqual(result, 90)

    def test_parse_time_hours_and_minutes_large_value(self):
        """parse_time_to_minutes should parse '2 hours 45 minutes' correctly."""
        result = parse_time_to_minutes('2 hours 45 minutes')
        self.assertEqual(result, 165)

    def test_parse_time_invalid_format_returns_none(self):
        """parse_time_to_minutes should return None for invalid format."""
        result = parse_time_to_minutes('about 30 mins')
        self.assertIsNone(result)

    def test_parse_time_single_word_returns_none(self):
        """parse_time_to_minutes should return None for single word input."""
        result = parse_time_to_minutes('quick')
        self.assertIsNone(result)

    def test_parse_time_three_words_returns_none(self):
        """parse_time_to_minutes should return None for three word input."""
        result = parse_time_to_minutes('30 min total')
        self.assertIsNone(result)

    def test_parse_time_wrong_unit_returns_none(self):
        """parse_time_to_minutes should return None for wrong unit."""
        result = parse_time_to_minutes('30 seconds')
        self.assertIsNone(result)

    def test_parse_time_mixed_case_hours_minutes(self):
        """parse_time_to_minutes should handle mixed case for hours and minutes."""
        result = parse_time_to_minutes('1 HOURS 30 MINUTES')
        self.assertEqual(result, 90)


class RecipesViewTestCase(TestCase):
    """Tests for the browse recipes view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('recipes')

        # Create test recipes with various attributes
        self.recipe1 = Recipe.objects.create(
            name="Quick Pasta",
            average_rating=4,
            difficulty="Easy",
            total_time="20 minutes",
            servings=2,
            ingredients="pasta, tomato sauce, basil",
            method="Boil pasta. Add sauce.",
            created_by=self.user,
        )
        self.recipe2 = Recipe.objects.create(
            name="Slow Roast Chicken",
            average_rating=5,
            difficulty="Hard",
            total_time="2 hours 30 minutes",
            servings=6,
            ingredients="chicken, herbs, butter, garlic",
            method="Season chicken. Roast for 2 hours.",
            created_by=self.user,
        )
        self.recipe3 = Recipe.objects.create(
            name="Vegetable Stir Fry",
            average_rating=3,
            difficulty="Moderate",
            total_time="15 minutes",
            servings=4,
            ingredients="broccoli, carrots, soy sauce, ginger",
            method="Chop vegetables. Stir fry in wok.",
            created_by=self.user,
        )
        self.recipe4 = Recipe.objects.create(
            name="Beef Stew",
            average_rating=4,
            difficulty="Moderate",
            total_time="1 hours 45 minutes",
            servings=8,
            ingredients="beef, potatoes, carrots, onion",
            method="Brown beef. Add vegetables. Simmer.",
            created_by=self.user,
        )
        self.recipe5 = Recipe.objects.create(
            name="Simple Salad",
            average_rating=2,
            difficulty="Very Easy",
            total_time="10 minutes",
            servings=1,
            ingredients="lettuce, tomatoes, cucumber, dressing",
            method="Chop vegetables. Add dressing.",
            created_by=self.user,
        )

    def test_recipes_url(self):
        """Test that the recipes URL is correct."""
        self.assertEqual(self.url, '/recipes/')

    def test_get_recipes_returns_200(self):
        """Test that GET request to recipes returns 200 status."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_recipes_uses_correct_template(self):
        """Test that recipes view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipes.html')

    def test_get_recipes_shows_all_recipes(self):
        """Test that all recipes are shown by default."""
        response = self.client.get(self.url)
        page_obj = response.context['page_obj']
        recipe_ids = [r.id for r in page_obj]
        self.assertIn(self.recipe1.id, recipe_ids)
        self.assertIn(self.recipe2.id, recipe_ids)
        self.assertIn(self.recipe3.id, recipe_ids)
        self.assertIn(self.recipe4.id, recipe_ids)
        self.assertIn(self.recipe5.id, recipe_ids)

    def test_context_contains_page_obj(self):
        """Test that context contains page_obj."""
        response = self.client.get(self.url)
        self.assertIn('page_obj', response.context)

    def test_context_contains_active_sort(self):
        """Test that context contains active_sort."""
        response = self.client.get(self.url)
        self.assertIn('active_sort', response.context)

    def test_context_contains_search_query(self):
        """Test that context contains search_query."""
        response = self.client.get(self.url)
        self.assertIn('search_query', response.context)

    def test_active_sort_is_empty_by_default(self):
        """Test that active_sort is empty string by default."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['active_sort'], '')

    def test_search_query_is_empty_by_default(self):
        """Test that search_query is empty string by default."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['search_query'], '')


class RecipesSearchTestCase(TestCase):
    """Tests for search functionality in browse recipes view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('recipes')

        self.recipe1 = Recipe.objects.create(
            name="Spicy Chicken Tikka",
            average_rating=4,
            difficulty="Moderate",
            total_time="45 minutes",
            servings=4,
            ingredients="chicken, curry powder, coconut milk",
            method="Fry chicken. Add curry and simmer.",
            created_by=self.user,
        )
        self.recipe2 = Recipe.objects.create(
            name="Vegetable Soup",
            average_rating=3,
            difficulty="Easy",
            total_time="30 minutes",
            servings=6,
            ingredients="carrots, celery, onion, stock",
            method="Chop vegetables. Boil in stock.",
            created_by=self.user,
        )
        self.recipe3 = Recipe.objects.create(
            name="Grilled Salmon",
            average_rating=5,
            difficulty="Moderate",
            total_time="25 minutes",
            servings=2,
            ingredients="salmon, lemon, dill, olive oil",
            method="Marinate salmon. Grill until cooked.",
            created_by=self.user,
        )

    def test_search_by_recipe_name(self):
        """Test search filters recipes by name."""
        response = self.client.get(self.url, {'q': 'tikka'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        self.assertEqual(names, ['Spicy Chicken Tikka'])

    def test_search_by_recipe_name_case_insensitive(self):
        """Test search is case insensitive for name."""
        response = self.client.get(self.url, {'q': 'TIKKA'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        self.assertEqual(names, ['Spicy Chicken Tikka'])

    def test_search_by_ingredients(self):
        """Test search filters recipes by ingredients."""
        response = self.client.get(self.url, {'q': 'salmon'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        self.assertEqual(names, ['Grilled Salmon'])

    def test_search_by_ingredients_partial_match(self):
        """Test search filters recipes by partial ingredient match."""
        response = self.client.get(self.url, {'q': 'carrot'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        self.assertIn('Vegetable Soup', names)

    def test_search_by_method(self):
        """Test search filters recipes by method."""
        response = self.client.get(self.url, {'q': 'grill'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        self.assertEqual(names, ['Grilled Salmon'])

    def test_search_with_no_results(self):
        """Test search with no matching results returns empty list."""
        response = self.client.get(self.url, {'q': 'xyz123notfound'})
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 0)

    def test_search_query_preserved_in_context(self):
        """Test that search query is preserved in context."""
        response = self.client.get(self.url, {'q': 'chicken'})
        self.assertEqual(response.context['search_query'], 'chicken')

    def test_search_multiple_results(self):
        """Test search can return multiple results."""
        # Both recipes have 'vegetables' related content
        response = self.client.get(self.url, {'q': 'vegetable'})
        page_obj = response.context['page_obj']
        self.assertGreaterEqual(len(list(page_obj)), 1)

    def test_search_with_empty_query_returns_all(self):
        """Test empty search query returns all recipes."""
        response = self.client.get(self.url, {'q': ''})
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 3)


class RecipesSortingTestCase(TestCase):
    """Tests for sorting functionality in browse recipes view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data with varying attributes for sorting tests."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('recipes')

        # Recipe with 10 minutes - should appear in quick meals
        self.quick_recipe = Recipe.objects.create(
            name="Quick Snack",
            average_rating=3,
            difficulty="Very Easy",
            total_time="10 minutes",
            servings=1,
            ingredients="crackers, cheese",
            method="Assemble.",
            created_by=self.user,
        )
        # Recipe with 25 minutes - should appear in quick meals
        self.medium_quick_recipe = Recipe.objects.create(
            name="Quick Salad",
            average_rating=4,
            difficulty="Easy",
            total_time="25 minutes",
            servings=2,
            ingredients="lettuce, tomato",
            method="Chop and mix.",
            created_by=self.user,
        )
        # Recipe with exactly 30 minutes - should appear in quick meals
        self.exactly_30_recipe = Recipe.objects.create(
            name="30 Min Pasta",
            average_rating=5,
            difficulty="Moderate",
            total_time="30 minutes",
            servings=4,
            ingredients="pasta, sauce",
            method="Cook pasta.",
            created_by=self.user,
        )
        # Recipe with 45 minutes - should NOT appear in quick meals
        self.slow_recipe = Recipe.objects.create(
            name="Slow Roast",
            average_rating=5,
            difficulty="Hard",
            total_time="45 minutes",
            servings=6,
            ingredients="beef, vegetables",
            method="Roast slowly.",
            created_by=self.user,
        )
        # Recipe with 2 hours - should NOT appear in quick meals
        self.very_slow_recipe = Recipe.objects.create(
            name="Braised Lamb",
            average_rating=2,
            difficulty="Very Hard",
            total_time="2 hours",
            servings=8,
            ingredients="lamb, wine",
            method="Braise for hours.",
            created_by=self.user,
        )

    def test_sort_by_quick_meals_filters_under_30_minutes(self):
        """Test that quick-meals filter shows only recipes under 30 minutes."""
        response = self.client.get(self.url, {'sort_by': 'quick-meals'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        self.assertIn('Quick Snack', names)
        self.assertIn('Quick Salad', names)
        self.assertIn('30 Min Pasta', names)
        self.assertNotIn('Slow Roast', names)
        self.assertNotIn('Braised Lamb', names)

    def test_sort_by_quick_meals_excludes_long_recipes(self):
        """Test that quick-meals excludes recipes over 30 minutes."""
        response = self.client.get(self.url, {'sort_by': 'quick-meals'})
        page_obj = response.context['page_obj']
        recipe_ids = [r.id for r in page_obj]
        self.assertNotIn(self.slow_recipe.id, recipe_ids)
        self.assertNotIn(self.very_slow_recipe.id, recipe_ids)

    def test_sort_by_quick_meals_sorted_fastest_first(self):
        """Test that quick-meals sorts from fastest to slowest."""
        response = self.client.get(self.url, {'sort_by': 'quick-meals'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        # Should be sorted by time: 10 min, 25 min, 30 min
        self.assertEqual(names[0], 'Quick Snack')  # 10 minutes
        self.assertEqual(names[1], 'Quick Salad')  # 25 minutes
        self.assertEqual(names[2], '30 Min Pasta')  # 30 minutes

    def test_sort_by_servings_descending(self):
        """Test sorting by servings is in descending order."""
        response = self.client.get(self.url, {'sort_by': 'servings'})
        page_obj = response.context['page_obj']
        servings_list = [r.servings for r in page_obj]
        self.assertEqual(servings_list, sorted(servings_list, reverse=True))

    def test_sort_by_servings_highest_first(self):
        """Test that highest servings recipe is first."""
        response = self.client.get(self.url, {'sort_by': 'servings'})
        page_obj = response.context['page_obj']
        first_recipe = list(page_obj)[0]
        self.assertEqual(first_recipe.name, 'Braised Lamb')  # 8 servings

    def test_sort_by_rating_descending(self):
        """Test sorting by rating is in descending order."""
        response = self.client.get(self.url, {'sort_by': 'rating'})
        page_obj = response.context['page_obj']
        ratings = [r.average_rating for r in page_obj]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_sort_by_rating_highest_first(self):
        """Test that highest rated recipes are first."""
        response = self.client.get(self.url, {'sort_by': 'rating'})
        page_obj = response.context['page_obj']
        first_recipe = list(page_obj)[0]
        self.assertEqual(first_recipe.average_rating, 5)

    def test_sort_by_difficulty_ascending(self):
        """Test sorting by difficulty is in ascending order."""
        response = self.client.get(self.url, {'sort_by': 'difficulty'})
        page_obj = response.context['page_obj']
        difficulties = [r.difficulty for r in page_obj]
        self.assertEqual(difficulties, sorted(difficulties))

    def test_active_sort_preserved_in_context(self):
        """Test that active_sort is preserved in context."""
        response = self.client.get(self.url, {'sort_by': 'rating'})
        self.assertEqual(response.context['active_sort'], 'rating')

    def test_sort_by_invalid_value_returns_all(self):
        """Test that invalid sort_by value returns all recipes."""
        response = self.client.get(self.url, {'sort_by': 'invalid'})
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 5)


class RecipesPaginationTestCase(TestCase):
    """Tests for pagination in browse recipes view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data with many recipes for pagination."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('recipes')

        # Create 25 recipes to test pagination (page size is 21)
        for i in range(25):
            Recipe.objects.create(
                name=f"Recipe {i+1:02d}",
                average_rating=(i % 5) + 1,
                difficulty="Easy",
                total_time="30 minutes",
                servings=4,
                ingredients=f"ingredient {i}",
                method=f"step {i}",
                created_by=self.user,
            )

    def test_first_page_has_21_recipes(self):
        """Test that first page contains 21 recipes."""
        response = self.client.get(self.url)
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 21)

    def test_second_page_has_remaining_recipes(self):
        """Test that second page contains remaining recipes."""
        response = self.client.get(self.url, {'page': 2})
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 4)

    def test_page_obj_has_correct_page_number(self):
        """Test that page_obj has correct page number."""
        response = self.client.get(self.url, {'page': 2})
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.number, 2)

    def test_page_obj_has_next_on_first_page(self):
        """Test that first page has next page."""
        response = self.client.get(self.url)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_next())

    def test_page_obj_no_next_on_last_page(self):
        """Test that last page has no next page."""
        response = self.client.get(self.url, {'page': 2})
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_next())

    def test_page_obj_has_previous_on_second_page(self):
        """Test that second page has previous page."""
        response = self.client.get(self.url, {'page': 2})
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())

    def test_page_obj_no_previous_on_first_page(self):
        """Test that first page has no previous page."""
        response = self.client.get(self.url)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())

    def test_invalid_page_returns_first_page(self):
        """Test that invalid page number returns first page."""
        response = self.client.get(self.url, {'page': 'invalid'})
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.number, 1)

    def test_out_of_range_page_returns_last_page(self):
        """Test that out of range page returns last page."""
        response = self.client.get(self.url, {'page': 999})
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.number, 2)  # Last page

    def test_paginator_count(self):
        """Test that paginator has correct total count."""
        response = self.client.get(self.url)
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.paginator.count, 25)

    def test_paginator_num_pages(self):
        """Test that paginator has correct number of pages."""
        response = self.client.get(self.url)
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.paginator.num_pages, 2)


class RecipesSearchAndSortCombinedTestCase(TestCase):
    """Tests for combined search and sort functionality."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('recipes')

        self.pasta1 = Recipe.objects.create(
            name="Pasta Carbonara",
            average_rating=5,
            difficulty="Moderate",
            total_time="25 minutes",
            servings=2,
            ingredients="pasta, eggs, bacon, parmesan",
            method="Cook pasta. Mix with sauce.",
            created_by=self.user,
        )
        self.pasta2 = Recipe.objects.create(
            name="Pasta Bolognese",
            average_rating=4,
            difficulty="Hard",
            total_time="1 hours 30 minutes",
            servings=6,
            ingredients="pasta, beef, tomatoes, onion",
            method="Simmer sauce. Cook pasta.",
            created_by=self.user,
        )
        self.pasta3 = Recipe.objects.create(
            name="Pasta Primavera",
            average_rating=3,
            difficulty="Easy",
            total_time="20 minutes",
            servings=4,
            ingredients="pasta, vegetables, olive oil",
            method="Saute vegetables. Toss with pasta.",
            created_by=self.user,
        )
        self.other_recipe = Recipe.objects.create(
            name="Grilled Steak",
            average_rating=5,
            difficulty="Moderate",
            total_time="15 minutes",
            servings=2,
            ingredients="steak, salt, pepper",
            method="Grill steak.",
            created_by=self.user,
        )

    def test_search_and_sort_by_rating(self):
        """Test search combined with sort by rating."""
        response = self.client.get(self.url, {'q': 'pasta', 'sort_by': 'rating'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        # Should only include pasta recipes, sorted by rating desc
        self.assertEqual(len(names), 3)
        self.assertNotIn('Grilled Steak', names)
        ratings = [r.average_rating for r in page_obj]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_search_and_sort_by_servings(self):
        """Test search combined with sort by servings."""
        response = self.client.get(self.url, {'q': 'pasta', 'sort_by': 'servings'})
        page_obj = response.context['page_obj']
        servings_list = [r.servings for r in page_obj]
        self.assertEqual(servings_list, sorted(servings_list, reverse=True))

    def test_search_and_sort_by_difficulty(self):
        """Test search combined with sort by difficulty."""
        response = self.client.get(self.url, {'q': 'pasta', 'sort_by': 'difficulty'})
        page_obj = response.context['page_obj']
        difficulties = [r.difficulty for r in page_obj]
        self.assertEqual(difficulties, sorted(difficulties))

    def test_search_and_sort_by_quick_meals(self):
        """Test search combined with quick-meals filter."""
        response = self.client.get(self.url, {'q': 'pasta', 'sort_by': 'quick-meals'})
        page_obj = response.context['page_obj']
        names = [r.name for r in page_obj]
        # Should only include quick pasta recipes (under 30 mins)
        self.assertIn('Pasta Carbonara', names)  # 25 min
        self.assertIn('Pasta Primavera', names)  # 20 min
        self.assertNotIn('Pasta Bolognese', names)  # 1h 30min

    def test_search_preserves_sort_in_context(self):
        """Test that both search and sort are preserved in context."""
        response = self.client.get(self.url, {'q': 'pasta', 'sort_by': 'rating'})
        self.assertEqual(response.context['search_query'], 'pasta')
        self.assertEqual(response.context['active_sort'], 'rating')


class RecipesViewNoRecipesTestCase(TestCase):
    """Tests for browse recipes view when no recipes exist."""

    def setUp(self):
        """Set up test without any recipes."""
        self.url = reverse('recipes')

    def test_empty_database_returns_200(self):
        """Test that empty database still returns 200."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_empty_database_returns_empty_page_obj(self):
        """Test that empty database returns empty page_obj."""
        response = self.client.get(self.url)
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 0)

    def test_empty_database_with_search_returns_empty(self):
        """Test that search on empty database returns empty result."""
        response = self.client.get(self.url, {'q': 'anything'})
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 0)

    def test_empty_database_with_sort_returns_empty(self):
        """Test that sort on empty database returns empty result."""
        response = self.client.get(self.url, {'sort_by': 'rating'})
        page_obj = response.context['page_obj']
        self.assertEqual(len(list(page_obj)), 0)


class RecipeModelTestCase(TestCase):
    """Tests for the Recipe model."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')

    def test_recipe_str_returns_name(self):
        """Test that Recipe __str__ returns the name."""
        recipe = Recipe.objects.create(
            name="Test Recipe",
            average_rating=3,
            difficulty="Easy",
            total_time="30 minutes",
            servings=4,
            ingredients="test ingredients",
            method="test method",
            created_by=self.user,
        )
        self.assertEqual(str(recipe), "Test Recipe")

    def test_recipe_default_values(self):
        """Test that Recipe has correct default values."""
        recipe = Recipe.objects.create(
            name="Minimal Recipe",
            total_time="30 minutes",
            ingredients="test",
            method="test",
            created_by=self.user,
        )
        self.assertEqual(recipe.average_rating, 0)
        self.assertEqual(recipe.difficulty, "Easy")
        self.assertEqual(recipe.servings, 1)
        self.assertEqual(recipe.calories, 0)
        self.assertEqual(recipe.personal_rating, 0)

    def test_recipe_difficulty_choices(self):
        """Test that Recipe accepts valid difficulty choices."""
        difficulties = ["Very Easy", "Easy", "Moderate", "Hard", "Very Hard"]
        for diff in difficulties:
            recipe = Recipe.objects.create(
                name=f"Recipe {diff}",
                difficulty=diff,
                total_time="30 minutes",
                ingredients="test",
                method="test",
                created_by=self.user,
            )
            self.assertEqual(recipe.difficulty, diff)

    def test_recipe_can_have_null_created_by(self):
        """Test that Recipe can have null created_by."""
        recipe = Recipe.objects.create(
            name="No Creator Recipe",
            total_time="30 minutes",
            ingredients="test",
            method="test",
            created_by=None,
        )
        self.assertIsNone(recipe.created_by)

    def test_recipe_image_url_can_be_blank(self):
        """Test that Recipe image_url can be blank."""
        recipe = Recipe.objects.create(
            name="No Image Recipe",
            total_time="30 minutes",
            ingredients="test",
            method="test",
            created_by=self.user,
            image_url="",
        )
        self.assertEqual(recipe.image_url, "")

    def test_recipe_image_url_can_be_null(self):
        """Test that Recipe image_url can be null."""
        recipe = Recipe.objects.create(
            name="Null Image Recipe",
            total_time="30 minutes",
            ingredients="test",
            method="test",
            created_by=self.user,
            image_url=None,
        )
        self.assertIsNone(recipe.image_url)
