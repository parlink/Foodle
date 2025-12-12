"""Tests for the recipe detail view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe


class RecipeDetailViewTestCase(TestCase):
    """Tests for the recipe detail view."""

    def setUp(self):
        """Set up test data."""
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            total_time='30 minutes',
            servings=4,
            difficulty='Easy',
            ingredients='Flour, sugar, eggs, butter',
            method='Mix ingredients\nBake at 350\nCool down'
        )
        self.url = reverse('recipe_detail', kwargs={'id': self.recipe.id})

    def test_recipe_detail_url(self):
        """Test that recipe_detail URL is correct."""
        self.assertEqual(self.url, f'/recipe/{self.recipe.id}/')

    def test_get_recipe_detail(self):
        """Test that recipe detail page loads."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/recipe_detail.html')

    def test_recipe_detail_context_contains_recipe(self):
        """Test that context contains the recipe."""
        response = self.client.get(self.url)
        self.assertIn('recipe', response.context)
        self.assertEqual(response.context['recipe'].id, self.recipe.id)

    def test_recipe_detail_context_contains_ingredients(self):
        """Test that context contains ingredients list."""
        response = self.client.get(self.url)
        self.assertIn('ingredients', response.context)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 4)
        self.assertEqual(ingredients[0], 'Flour')

    def test_recipe_detail_ingredients_split_correctly(self):
        """Test that ingredients are split correctly."""
        response = self.client.get(self.url)
        ingredients = response.context['ingredients']
        self.assertIn('sugar', ingredients)
        self.assertIn('eggs', ingredients)
        self.assertIn('butter', ingredients)

    def test_recipe_detail_context_contains_method(self):
        """Test that context contains method steps."""
        response = self.client.get(self.url)
        self.assertIn('method', response.context)
        method = response.context['method']
        self.assertEqual(len(method), 3)

    def test_recipe_detail_method_split_correctly(self):
        """Test that method is split correctly by newlines."""
        response = self.client.get(self.url)
        method = response.context['method']
        self.assertEqual(method[0], 'Mix ingredients')
        self.assertEqual(method[1], 'Bake at 350')
        self.assertEqual(method[2], 'Cool down')

    def test_nonexistent_recipe_returns_404(self):
        """Test that nonexistent recipe returns 404."""
        url = reverse('recipe_detail', kwargs={'id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_with_single_ingredient(self):
        """Test recipe detail with single ingredient."""
        recipe = Recipe.objects.create(
            name='Simple Recipe',
            total_time='10 minutes',
            servings=1,
            difficulty='Easy',
            ingredients='Salt',
            method='Add salt'
        )
        url = reverse('recipe_detail', kwargs={'id': recipe.id})
        response = self.client.get(url)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0], 'Salt')

    def test_recipe_detail_with_single_step(self):
        """Test recipe detail with single method step."""
        recipe = Recipe.objects.create(
            name='One Step Recipe',
            total_time='5 minutes',
            servings=1,
            difficulty='Easy',
            ingredients='Water',
            method='Drink'
        )
        url = reverse('recipe_detail', kwargs={'id': recipe.id})
        response = self.client.get(url)
        method = response.context['method']
        self.assertEqual(len(method), 1)
        self.assertEqual(method[0], 'Drink')

    def test_recipe_detail_all_fields_present(self):
        """Test that all recipe fields are present in context."""
        response = self.client.get(self.url)
        recipe = response.context['recipe']
        self.assertEqual(recipe.name, 'Test Recipe')
        self.assertEqual(recipe.servings, 4)
        self.assertEqual(recipe.difficulty, 'Easy')
