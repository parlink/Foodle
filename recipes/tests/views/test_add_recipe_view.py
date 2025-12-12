"""Tests for the add recipe view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.forms.add_recipe_form import RecipeForm
from recipes.tests.helpers import reverse_with_next


class AddRecipeViewTestCase(TestCase):
    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('recipe_create')

        self.form_input = {
            'name': 'Test Recipe',
            'personal_rating': 4,
            'difficulty': 'Easy',
            'total_time': '30 min',
            'servings': 2,
            # include calories only if your Recipe model has it
            'calories': 250,
            'ingredients': 'eggs, flour, milk',
            'method': 'Mix\nCook',
        }

    def test_add_recipe_url(self):
        self.assertEqual(self.url, '/add-recipe/')

    def test_get_add_recipe_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_recipe_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/add_recipe.html')
        self.assertTrue(isinstance(response.context['form'], RecipeForm))
        self.assertFalse(response.context['form'].is_bound)

    def test_successful_add_recipe(self):
        self.client.login(username=self.user.username, password='Password123')
        before = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after = Recipe.objects.count()
        self.assertEqual(after, before + 1)
        self.assertRedirects(response, reverse('my_recipes'))

        recipe = Recipe.objects.get(name='Test Recipe')
        self.assertEqual(recipe.created_by, self.user)
        # your create view syncs average_rating with personal_rating
        self.assertEqual(recipe.average_rating, 4)

    def test_unsuccessful_add_recipe_blank_name(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['name'] = ''
        before = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after = Recipe.objects.count()
        self.assertEqual(after, before)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/add_recipe.html')

    def test_post_add_recipe_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_add_recipe_form_has_csrf_token(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')
