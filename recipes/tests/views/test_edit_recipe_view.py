"""Tests for the edit recipe view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.forms.add_recipe_form import RecipeForm
from recipes.tests.helpers import reverse_with_next


class EditRecipeViewTestCase(TestCase):
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')

        self.recipe = Recipe.objects.create(
            name="Edit Me",
            average_rating=2,
            personal_rating=2,
            difficulty="Easy",
            total_time="45 min",
            servings=4,
            ingredients="a, b, c",
            method="Step 1\nStep 2",
            created_by=self.user,
        )
        self.url = reverse('recipe_edit', kwargs={'id': self.recipe.id})

        self.form_input = {
            'name': 'Edited Name',
            'personal_rating': 5,
            'difficulty': 'Hard',
            'total_time': '1 hour',
            'servings': 3,
            'calories': 123,
            'ingredients': 'x, y, z',
            'method': 'New step 1\nNew step 2',
        }

    def test_edit_recipe_url(self):
        self.assertEqual(self.url, f'/recipes/{self.recipe.id}/edit/')

    def test_get_edit_recipe_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_edit_recipe_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/edit_recipe.html')
        self.assertTrue(isinstance(response.context['form'], RecipeForm))

    def test_successful_edit_recipe(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, reverse('my_recipes'))

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.name, 'Edited Name')
        self.assertEqual(self.recipe.personal_rating, 5)
        self.assertEqual(self.recipe.average_rating, 5)  # sync logic
        self.assertEqual(self.recipe.difficulty, 'Hard')

    def test_cannot_edit_other_users_recipe(self):
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_edit_nonexistent_recipe_returns_404(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('recipe_edit', kwargs={'id': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_recipe_with_invalid_form(self):
        self.client.login(username=self.user.username, password='Password123')
        invalid_form_input = {'name': ''}  # Missing required fields
        response = self.client.post(self.url, invalid_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/edit_recipe.html')

    def test_edit_recipe_preserves_created_by(self):
        self.client.login(username=self.user.username, password='Password123')
        self.client.post(self.url, self.form_input, follow=True)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.created_by, self.user)

    def test_edit_recipe_updates_average_rating(self):
        self.client.login(username=self.user.username, password='Password123')
        self.client.post(self.url, self.form_input)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.average_rating, self.recipe.personal_rating)

    def test_edit_recipe_context_contains_form(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    def test_edit_recipe_context_contains_recipe(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('recipe', response.context)
        self.assertEqual(response.context['recipe'].id, self.recipe.id)

    def test_edit_recipe_success_message(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('updated', str(messages[0]).lower())
