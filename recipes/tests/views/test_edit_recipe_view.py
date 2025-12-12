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

    def test_edit_recipe_without_personal_rating(self):
        """Test editing recipe without personal_rating doesn't update average_rating."""
        self.client.login(username=self.user.username, password='Password123')
        form_input = {
            'name': 'Edited Without Rating',
            'personal_rating': 0,  # No rating
            'difficulty': 'Easy',
            'total_time': '30 min',
            'servings': 2,
            'calories': 100,
            'ingredients': 'test',
            'method': 'test method',
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertRedirects(response, reverse('my_recipes'))

    def test_context_contains_recipe(self):
        """Test that the context contains the recipe object."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertIn('recipe', response.context)
        self.assertEqual(response.context['recipe'].id, self.recipe.id)

    def test_invalid_form_stays_on_page(self):
        """Test that invalid form data re-renders the edit page."""
        self.client.login(username=self.user.username, password='Password123')
        invalid_input = {
            'name': '',  # Name is required
            'personal_rating': 5,
            'difficulty': 'Hard',
            'total_time': '1 hour',
            'servings': 3,
            'calories': 123,
            'ingredients': 'x, y, z',
            'method': 'New step 1',
        }
        response = self.client.post(self.url, invalid_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/edit_recipe.html')

    def test_post_edit_recipe_redirects_when_not_logged_in(self):
        """Test that POST request redirects when not logged in."""
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_updates_created_by_to_current_user(self):
        """Test that editing updates created_by to current user."""
        self.client.login(username=self.user.username, password='Password123')
        self.client.post(self.url, self.form_input)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.created_by, self.user)
