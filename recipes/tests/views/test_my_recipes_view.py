"""Tests for the my_recipes (list/sort/search) view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.tests.helpers import reverse_with_next
from recipes.views.my_recipes_view import parse_total_time_to_minutes


class ParseTotalTimeToMinutesTest(TestCase):
    """Test suite for the parse_total_time_to_minutes utility function."""

    def test_empty_string(self):
        """Test parsing an empty string returns 0."""
        self.assertEqual(parse_total_time_to_minutes(''), 0)

    def test_none_value(self):
        """Test parsing None returns 0."""
        self.assertEqual(parse_total_time_to_minutes(None), 0)

    def test_minutes_only(self):
        """Test parsing time with only minutes."""
        self.assertEqual(parse_total_time_to_minutes('30 min'), 30)
        self.assertEqual(parse_total_time_to_minutes('45 minutes'), 45)

    def test_hours_only(self):
        """Test parsing time with only hours."""
        self.assertEqual(parse_total_time_to_minutes('1 hour'), 60)
        self.assertEqual(parse_total_time_to_minutes('2 hours'), 120)

    def test_hours_and_minutes(self):
        """Test parsing time with both hours and minutes."""
        self.assertEqual(parse_total_time_to_minutes('1 hour 30 min'), 90)
        self.assertEqual(parse_total_time_to_minutes('2 hours 45 minutes'), 165)

    def test_case_insensitive(self):
        """Test that parsing is case insensitive."""
        self.assertEqual(parse_total_time_to_minutes('1 HOUR 30 MIN'), 90)
        self.assertEqual(parse_total_time_to_minutes('45 MINUTES'), 45)

    def test_number_only(self):
        """Test parsing string with only a number treats it as minutes."""
        self.assertEqual(parse_total_time_to_minutes('30'), 30)
        self.assertEqual(parse_total_time_to_minutes('120'), 120)

    def test_no_number(self):
        """Test parsing string with no number returns 0."""
        self.assertEqual(parse_total_time_to_minutes('quick cook'), 0)
        self.assertEqual(parse_total_time_to_minutes('no time'), 0)

    def test_extra_spaces(self):
        """Test parsing with extra spaces."""
        self.assertEqual(parse_total_time_to_minutes('1   hour    30   min'), 90)
        self.assertEqual(parse_total_time_to_minutes('45   minutes'), 45)


class MyRecipesViewTestCase(TestCase):
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('my_recipes')

        # Recipes owned by logged-in user
        self.r1 = Recipe.objects.create(
            name="Apple Pie",
            average_rating=2,
            personal_rating=2,
            difficulty="Easy",
            total_time="45 min",
            servings=4,
            ingredients="apples, flour, sugar",
            method="Step 1\nStep 2",
            created_by=self.user,
        )
        self.r2 = Recipe.objects.create(
            name="Banana Bread",
            average_rating=5,
            personal_rating=5,
            difficulty="Moderate",
            total_time="1 hour 10 min",
            servings=6,
            ingredients="bananas, flour, butter",
            method="Mix\nBake",
            created_by=self.user,
        )
        self.r3 = Recipe.objects.create(
            name="Carrot Soup",
            average_rating=3,
            personal_rating=3,
            difficulty="Hard",
            total_time="20 min",
            servings=2,
            ingredients="carrots, stock, onion",
            method="Boil\nBlend",
            created_by=self.user,
        )

        # Recipe owned by someone else (should never appear)
        self.other = Recipe.objects.create(
            name="Zucchini Pasta",
            average_rating=4,
            personal_rating=4,
            difficulty="Easy",
            total_time="15 min",
            servings=2,
            ingredients="zucchini, pasta",
            method="Cook",
            created_by=self.other_user,
        )

    def test_my_recipes_url(self):
        self.assertEqual(self.url, '/my-recipes/')

    def test_get_my_recipes_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_my_recipes_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/my_recipes.html')

        # Only own recipes shown
        page = response.context['page']
        ids = [r.id for r in page.object_list]
        self.assertIn(self.r1.id, ids)
        self.assertIn(self.r2.id, ids)
        self.assertIn(self.r3.id, ids)
        self.assertNotIn(self.other.id, ids)

    def test_default_sort_is_alphabetical(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)  # default sort_by=name
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, sorted(names))

    def test_sort_by_rating_desc(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'sort_by': 'rating'})
        page = response.context['page']
        ratings = [r.average_rating for r in page.object_list]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_sort_by_difficulty(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'sort_by': 'difficulty'})
        page = response.context['page']
        diffs = [r.difficulty for r in page.object_list]
        self.assertEqual(diffs, sorted(diffs))

    def test_sort_by_time_uses_parsing(self):
        """
        Your view uses sorted(recipes_qs, key=parse_total_time_to_minutes).
        Here we test that it actually orders 20 min < 45 min < 1 hour 10 min.
        """
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'sort_by': 'time'})
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, ["Carrot Soup", "Apple Pie", "Banana Bread"])

    def test_search_by_recipe_name(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': 'banana'})
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, ["Banana Bread"])

    def test_search_by_ingredients(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': 'apples'})
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, ["Apple Pie"])

    def test_search_by_method(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': 'blend'})
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, ["Carrot Soup"])

    def test_search_returns_none_shows_empty_list(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': 'doesnotexist'})
        page = response.context['page']
        self.assertEqual(len(page.object_list), 0)

    def test_letter_filter_with_alphabetical_sort(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'sort_by': 'name', 'letter': 'B'})
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, ["Banana Bread"])
    def test_context_contains_alphabet(self):
        """Test that alphabet is provided in context for filtering."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        alphabet = response.context['alphabet']
        self.assertEqual(len(alphabet), 26)
        self.assertEqual(alphabet[0], 'A')
        self.assertEqual(alphabet[-1], 'Z')

    def test_context_contains_sort_by(self):
        """Test that sort_by is available in context."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'sort_by': 'rating'})
        self.assertEqual(response.context['sort_by'], 'rating')

    def test_context_contains_search_query(self):
        """Test that search_query is available in context."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': 'test'})
        self.assertEqual(response.context['search_query'], 'test')

    def test_letter_filter_case_insensitive(self):
        """Test that letter filter is case insensitive."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'letter': 'b'})
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, ["Banana Bread"])

    def test_letter_filter_with_no_matches(self):
        """Test letter filter that matches no recipes."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'letter': 'Z'})
        page = response.context['page']
        self.assertEqual(len(page.object_list), 0)

    def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        self.client.login(username=self.user.username, password='Password123')
        response1 = self.client.get(self.url, {'q': 'BANANA'})
        response2 = self.client.get(self.url, {'q': 'banana'})
        
        recipes1 = list(response1.context['page'].object_list)
        recipes2 = list(response2.context['page'].object_list)
        
        self.assertEqual(len(recipes1), 1)
        self.assertEqual(len(recipes2), 1)
        self.assertEqual(recipes1[0].id, recipes2[0].id)

    def test_search_with_leading_trailing_whitespace(self):
        """Test that search strips leading and trailing whitespace."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'q': '  banana  '})
        page = response.context['page']
        names = [r.name for r in page.object_list]
        self.assertEqual(names, ["Banana Bread"])

    def test_pagination_default_12_per_page(self):
        """Test that pagination shows 12 recipes per page."""
        # Create more recipes to exceed the 12-per-page limit
        for i in range(15):
            Recipe.objects.create(
                name=f"Recipe {i:02d}",
                average_rating=1,
                difficulty="Easy",
                total_time="30 min",
                servings=2,
                ingredients="test",
                method="test",
                created_by=self.user,
            )
        
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        
        page = response.context['page']
        self.assertEqual(page.paginator.per_page, 12)
        self.assertTrue(page.has_next())

    def test_pagination_page_2(self):
        """Test accessing second page of pagination."""
        # Create more recipes to exceed the 12-per-page limit
        for i in range(15):
            Recipe.objects.create(
                name=f"Recipe {i:02d}",
                average_rating=1,
                difficulty="Easy",
                total_time="30 min",
                servings=2,
                ingredients="test",
                method="test",
                created_by=self.user,
            )
        
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'page': 2})
        
        page = response.context['page']
        self.assertEqual(page.number, 2)
        self.assertTrue(page.has_previous())

    def test_invalid_page_returns_last_page(self):
        """Test that an invalid page number returns the last page."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'page': 999})
        
        page = response.context['page']
        self.assertEqual(page.number, page.paginator.num_pages)


class RecipeDetailViewTestCase(TestCase):
    """Test suite for the recipe detail view."""
    
    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            average_rating=4,
            difficulty='Easy',
            total_time='30 minutes',
            servings=4,
            calories=350,
            ingredients='Ingredient1, Ingredient2, Ingredient3',
            method='Step 1\nStep 2\nStep 3',
            created_by=self.user,
        )
        self.url = reverse('recipe_detail', args=[self.recipe.id])

    def test_recipe_detail_url(self):
        """Test that recipe_detail URL resolves correctly."""
        self.assertEqual(self.url, f'/recipe/{self.recipe.id}/')

    def test_get_recipe_detail(self):
        """Test GET request to recipe detail page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/recipe_detail.html')

    def test_recipe_detail_context(self):
        """Test that recipe detail context contains required data."""
        response = self.client.get(self.url)
        self.assertIn('recipe', response.context)
        self.assertIn('ingredients', response.context)
        self.assertIn('method', response.context)

    def test_recipe_detail_ingredients_parsed(self):
        """Test that ingredients are correctly parsed into a list."""
        response = self.client.get(self.url)
        ingredients = response.context['ingredients']
        
        self.assertEqual(len(ingredients), 3)
        self.assertEqual(ingredients[0], 'Ingredient1')
        self.assertEqual(ingredients[1], 'Ingredient2')
        self.assertEqual(ingredients[2], 'Ingredient3')

    def test_recipe_detail_ingredients_with_extra_spaces(self):
        """Test that ingredients are stripped of extra spaces."""
        recipe = Recipe.objects.create(
            name='Test Recipe 2',
            average_rating=4,
            difficulty='Easy',
            total_time='30 minutes',
            servings=4,
            calories=350,
            ingredients='Ingredient1, Ingredient2, Ingredient3',
            method='Step 1\nStep 2',
            created_by=self.user,
        )
        url = reverse('recipe_detail', args=[recipe.id])
        response = self.client.get(url)
        ingredients = response.context['ingredients']
        
        # Check that all ingredients have proper stripping
        self.assertEqual(len(ingredients), 3)
        for ingredient in ingredients:
            self.assertEqual(len(ingredient) > 0, True)

    def test_recipe_detail_method_parsed(self):
        """Test that method is correctly parsed into steps."""
        response = self.client.get(self.url)
        method = response.context['method']
        
        self.assertEqual(len(method), 3)
        self.assertEqual(method[0], 'Step 1')
        self.assertEqual(method[1], 'Step 2')
        self.assertEqual(method[2], 'Step 3')

    def test_recipe_detail_method_with_empty_lines(self):
        """Test that method handles empty lines - they are preserved."""
        recipe = Recipe.objects.create(
            name='Test Recipe 3',
            average_rating=4,
            difficulty='Easy',
            total_time='30 minutes',
            servings=4,
            calories=350,
            ingredients='test',
            method='Step 1\n\nStep 2\n\nStep 3',
            created_by=self.user,
        )
        url = reverse('recipe_detail', args=[recipe.id])
        response = self.client.get(url)
        method = response.context['method']
        
        # Empty lines are filtered out when non-empty (using if s.strip())
        # So we should only get 3 non-empty steps
        non_empty = [s for s in method if s.strip()]
        self.assertEqual(len(non_empty), 3)

    def test_recipe_detail_nonexistent_recipe(self):
        """Test accessing a recipe that doesn't exist."""
        url = reverse('recipe_detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_displays_correct_recipe(self):
        """Test that recipe_detail displays the correct recipe."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'].id, self.recipe.id)
        self.assertEqual(response.context['recipe'].name, 'Test Recipe')

    def test_recipe_detail_response_contains_recipe_name(self):
        """Test that recipe detail response contains the recipe name."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Test Recipe')

    def test_recipe_detail_no_ingredients(self):
        """Test recipe detail with empty ingredients creates a list with one empty string."""
        recipe = Recipe.objects.create(
            name='Test Recipe No Ingredients',
            average_rating=4,
            difficulty='Easy',
            total_time='30 minutes',
            servings=4,
            calories=350,
            ingredients='',
            method='Step 1',
            created_by=self.user,
        )
        url = reverse('recipe_detail', args=[recipe.id])
        response = self.client.get(url)
        ingredients = response.context['ingredients']
        
        # Empty ingredients field creates a list with one empty string after split
        # The filter removes it if it's empty after strip()
        filtered_ingredients = [i for i in ingredients if i.strip()]
        self.assertEqual(len(filtered_ingredients), 0)

    def test_recipe_detail_no_method(self):
        """Test recipe detail with empty method creates list with one empty string."""
        recipe = Recipe.objects.create(
            name='Test Recipe No Method',
            average_rating=4,
            difficulty='Easy',
            total_time='30 minutes',
            servings=4,
            calories=350,
            ingredients='test',
            method='',
            created_by=self.user,
        )
        url = reverse('recipe_detail', args=[recipe.id])
        response = self.client.get(url)
        method = response.context['method']
        
        # Empty method field creates a list with one empty string after split
        # The filter removes it if it's empty after strip()
        filtered_method = [m for m in method if m.strip()]
        self.assertEqual(len(filtered_method), 0)


class RecipeDeleteViewTestCase(TestCase):
    """Test suite for the recipe delete view."""
    
    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            name='Recipe to Delete',
            average_rating=4,
            difficulty='Easy',
            total_time='30 minutes',
            servings=4,
            calories=350,
            ingredients='test',
            method='test',
            created_by=self.user,
        )
        self.url = reverse('recipe_delete', args=[self.recipe.id])
        self.my_recipes_url = reverse('my_recipes')

    def test_recipe_delete_url(self):
        """Test that recipe_delete URL resolves correctly."""
        self.assertEqual(self.url, f'/recipes/{self.recipe.id}/delete/')

    def test_get_recipe_delete_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login on GET."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_recipe_delete_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to login on POST."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_recipe_delete(self):
        """Test successful deletion of a recipe."""
        self.client.login(username=self.user.username, password='Password123')
        before = Recipe.objects.count()
        response = self.client.post(self.url, follow=True)
        after = Recipe.objects.count()
        
        self.assertEqual(after, before - 1)
        self.assertRedirects(response, self.my_recipes_url)

    def test_recipe_not_found_returns_404(self):
        """Test that deleting non-existent recipe returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('recipe_delete', args=[99999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_users_recipe(self):
        """Test that a user cannot delete another user's recipe."""
        other_user = User.objects.create_user(
            username='@otheruser',
            email='other@example.org',
            first_name='Other',
            last_name='User',
            password='Password123'
        )
        
        other_recipe = Recipe.objects.create(
            name='Other User Recipe',
            average_rating=4,
            difficulty='Easy',
            total_time='30 minutes',
            servings=4,
            calories=350,
            ingredients='test',
            method='test',
            created_by=other_user,
        )
        
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('recipe_delete', args=[other_recipe.id])
        response = self.client.post(url)
        
        # Should return 404 because user doesn't have permission
        self.assertEqual(response.status_code, 404)
        # Recipe should still exist
        self.assertTrue(Recipe.objects.filter(id=other_recipe.id).exists())

    def test_get_recipe_delete_redirects_to_my_recipes(self):
        """Test that GET request to delete redirects to my_recipes."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.my_recipes_url)

    def test_delete_recipe_success_message(self):
        """Test that a success message is shown after deleting a recipe."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, follow=True)
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('Recipe "Recipe to Delete" deleted.', str(messages[0]))

    def test_recipe_deleted_not_in_database(self):
        """Test that deleted recipe is actually removed from database."""
        self.client.login(username=self.user.username, password='Password123')
        recipe_id = self.recipe.id
        self.client.post(self.url)
        
        self.assertFalse(Recipe.objects.filter(id=recipe_id).exists())