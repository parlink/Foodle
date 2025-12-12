"""Tests for the delete recipe view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.tests.helpers import reverse_with_next


class DeleteRecipeViewTestCase(TestCase):
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')

        self.recipe = Recipe.objects.create(
            name="Delete Me",
            average_rating=3,
            personal_rating=3,
            difficulty="Easy",
            total_time="30 min",
            servings=2,
            ingredients="a, b",
            method="Do thing",
            created_by=self.user,
        )
        self.url = reverse('recipe_delete', kwargs={'id': self.recipe.id})

    def test_delete_recipe_url(self):
        self.assertEqual(self.url, f'/recipes/{self.recipe.id}/delete/')

    def test_delete_recipe_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_delete_recipe(self):
        self.client.login(username=self.user.username, password='Password123')
        before = Recipe.objects.count()
        response = self.client.post(self.url, follow=True)
        after = Recipe.objects.count()
        self.assertEqual(after, before - 1)
        self.assertRedirects(response, reverse('my_recipes'))
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_cannot_delete_other_users_recipe(self):
        self.client.login(username=self.other_user.username, password='Password123')
        before = Recipe.objects.count()
        response = self.client.post(self.url, follow=True)
        after = Recipe.objects.count()
        self.assertEqual(after, before)
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_delete_nonexistent_recipe_returns_404(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('recipe_delete', kwargs={'id': 999999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
