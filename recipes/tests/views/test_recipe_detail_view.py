"""Tests for the recipe_detail view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe


class RecipeDetailViewTestCase(TestCase):
    """Tests for the recipe_detail view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            average_rating=4,
            difficulty="Moderate",
            total_time="30 minutes",
            servings=4,
            ingredients="flour, sugar, eggs, butter",
            method="Step 1: Mix ingredients\nStep 2: Bake for 30 minutes\nStep 3: Let cool",
            created_by=self.user,
        )
        self.url = reverse('recipe_detail', kwargs={'id': self.recipe.id})

    def test_recipe_detail_url(self):
        """Test that the recipe detail URL is correct."""
        self.assertEqual(self.url, f'/recipe/{self.recipe.id}/')

    def test_get_recipe_detail_returns_200(self):
        """Test that GET request returns 200 status."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_recipe_detail_uses_correct_template(self):
        """Test that recipe detail view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipes/recipe_detail.html')

    def test_context_contains_recipe(self):
        """Test that context contains the recipe."""
        response = self.client.get(self.url)
        self.assertIn('recipe', response.context)
        self.assertEqual(response.context['recipe'].id, self.recipe.id)

    def test_context_contains_ingredients_list(self):
        """Test that context contains ingredients as a list."""
        response = self.client.get(self.url)
        self.assertIn('ingredients', response.context)
        self.assertIsInstance(response.context['ingredients'], list)

    def test_ingredients_are_split_correctly(self):
        """Test that ingredients are split by comma and space."""
        response = self.client.get(self.url)
        ingredients = response.context['ingredients']
        self.assertEqual(ingredients, ['flour', 'sugar', 'eggs', 'butter'])

    def test_context_contains_method_list(self):
        """Test that context contains method as a list."""
        response = self.client.get(self.url)
        self.assertIn('method', response.context)
        self.assertIsInstance(response.context['method'], list)

    def test_method_is_split_correctly(self):
        """Test that method is split by newlines."""
        response = self.client.get(self.url)
        method = response.context['method']
        self.assertEqual(len(method), 3)
        self.assertIn('Step 1: Mix ingredients', method)
        self.assertIn('Step 2: Bake for 30 minutes', method)
        self.assertIn('Step 3: Let cool', method)

    def test_nonexistent_recipe_returns_404(self):
        """Test that nonexistent recipe returns 404."""
        url = reverse('recipe_detail', kwargs={'id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_recipe_with_single_ingredient(self):
        """Test recipe with single ingredient."""
        recipe = Recipe.objects.create(
            name="Simple Recipe",
            total_time="10 minutes",
            ingredients="water",
            method="Boil",
            created_by=self.user,
        )
        url = reverse('recipe_detail', kwargs={'id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.context['ingredients'], ['water'])

    def test_recipe_with_single_step(self):
        """Test recipe with single step method."""
        recipe = Recipe.objects.create(
            name="Simple Recipe",
            total_time="10 minutes",
            ingredients="water",
            method="Boil",
            created_by=self.user,
        )
        url = reverse('recipe_detail', kwargs={'id': recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.context['method'], ['Boil'])
