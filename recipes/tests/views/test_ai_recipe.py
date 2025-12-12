"""Tests for the AI recipe chatbot view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages


class ChatbotViewTestCase(TestCase):
    """Tests for the chatbot/AI recipe view."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse('ai_recipes')

    def test_chatbot_url(self):
        """Test that chatbot URL is correct."""
        self.assertEqual(self.url, '/ai-recipes/')

    def test_get_chatbot_page(self):
        """Test that chatbot page loads via GET."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AI_Recipe.html')

    def test_chatbot_context_contains_recipes(self):
        """Test that context contains recipes list."""
        response = self.client.get(self.url)
        self.assertIn('recipes', response.context)
        self.assertEqual(response.context['recipes'], [])

    def test_chatbot_session_recipes_empty_initially(self):
        """Test that session recipes is empty initially."""
        response = self.client.get(self.url)
        recipes = response.context['recipes']
        self.assertEqual(len(recipes), 0)

    def test_chatbot_clear_history_post(self):
        """Test clearing recipe history via POST."""
        # Set some recipes in session
        session = self.client.session
        session['recipes'] = [['Recipe 1', 'Step 1'], ['Recipe 2', 'Step 2']]
        session.save()

        # Clear history
        response = self.client.post(self.url, {'clear_history': 'true'})
        self.assertEqual(response.status_code, 200)
        recipes = response.context['recipes']
        self.assertEqual(len(recipes), 0)

    def test_chatbot_clear_history_clears_session(self):
        """Test that clear_history clears session data."""
        session = self.client.session
        session['recipes'] = [['Recipe'], ['Recipe2']]
        session.save()

        response = self.client.post(self.url, {'clear_history': 'true'})
        self.assertEqual(len(self.client.session.get('recipes', [])), 0)

    def test_chatbot_no_api_key_handling(self):
        """Test chatbot response when API key is missing."""
        # The view checks for OPENAI_API_KEY in settings
        # This test verifies the error handling path
        response = self.client.post(
            self.url,
            {'submit': 'true', 'user_input': 'test ingredients'},
        )
        # Should either show error or redirect
        self.assertIn(response.status_code, [200, 302])

    def test_chatbot_post_with_submit_button(self):
        """Test POST request with submit button (would need API)."""
        response = self.client.post(
            self.url,
            {'submit': 'true', 'user_input': 'test ingredients'},
            follow=True
        )
        # Without API key, should handle gracefully
        self.assertEqual(response.status_code, 200)

    def test_chatbot_session_preserves_recipes(self):
        """Test that session preserves recipes across requests."""
        session = self.client.session
        session['recipes'] = [['Test Recipe', 'Step 1', 'Step 2']]
        session.save()

        response = self.client.get(self.url)
        recipes = response.context['recipes']
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0], ['Test Recipe', 'Step 1', 'Step 2'])

    def test_chatbot_multiple_recipes_in_session(self):
        """Test handling multiple recipes in session."""
        session = self.client.session
        recipes_list = [
            ['Pasta', 'Boil water', 'Add pasta'],
            ['Salad', 'Chop vegetables', 'Mix dressing']
        ]
        session['recipes'] = recipes_list
        session.save()

        response = self.client.get(self.url)
        recipes = response.context['recipes']
        self.assertEqual(len(recipes), 2)

    def test_chatbot_context_accessible(self):
        """Test that chatbot context is always accessible."""
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context.get('recipes'))

    def test_chatbot_empty_user_input(self):
        """Test POST with empty user input."""
        response = self.client.post(
            self.url,
            {'submit': 'true', 'user_input': ''},
            follow=True
        )
        # Should handle gracefully
        self.assertEqual(response.status_code, 200)

    def test_chatbot_post_without_session_key(self):
        """Test that POST works even without pre-existing session."""
        # Delete session if it exists
        if 'recipes' in self.client.session:
            del self.client.session['recipes']
            self.client.session.save()

        response = self.client.post(
            self.url,
            {'clear_history': 'true'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipes'], [])
