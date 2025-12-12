"""Tests for the my_recipes (list/sort/search) view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.tests.helpers import reverse_with_next


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
