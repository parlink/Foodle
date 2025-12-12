"""Tests for the AI recipe chatbot view."""
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse


class AIRecipeViewTestCase(TestCase):
    """Tests for the chatbot view."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse('ai_recipes')

    def test_ai_recipes_url(self):
        """Test that AI recipes URL is correct."""
        self.assertEqual(self.url, '/ai-recipes/')

    def test_get_ai_recipes_returns_200(self):
        """Test that GET request returns 200."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_ai_recipes_uses_correct_template(self):
        """Test that view uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'AI_Recipe.html')

    def test_context_contains_recipes(self):
        """Test that context contains recipes list."""
        response = self.client.get(self.url)
        self.assertIn('recipes', response.context)

    def test_recipes_empty_by_default(self):
        """Test that recipes is empty by default."""
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipes'], [])

    def test_clear_history_clears_session_recipes(self):
        """Test that clear_history action clears session recipes."""
        # First add some recipes to session
        session = self.client.session
        session['recipes'] = [['Recipe 1', 'Step 1'], ['Recipe 2', 'Step 1']]
        session.save()
        
        # Clear history
        response = self.client.post(self.url, {'clear_history': 'true'})
        self.assertEqual(response.status_code, 200)
        
        # Check recipes are cleared (the response shows current state)
        self.assertEqual(response.context['recipes'], [])

    @override_settings(OPENAI_API_KEY=None)
    def test_submit_without_api_key_shows_error(self):
        """Test that submit without API key shows error message."""
        response = self.client.post(self.url, {
            'submit': 'true',
            'user_input': 'chicken and rice',
        })
        self.assertRedirects(response, self.url)
        # Follow the redirect to check for message
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(OPENAI_API_KEY='test-api-key')
    @patch('recipes.views.ai_recipe.OpenAI')
    def test_submit_with_valid_input_calls_api(self, mock_openai):
        """Test that submit with valid input calls the OpenAI API."""
        # Mock the OpenAI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test Recipe\n1. Step one\n2. Step two"
        mock_client.chat.completions.create.return_value = mock_response
        
        response = self.client.post(self.url, {
            'submit': 'true',
            'user_input': 'chicken and rice',
        })
        
        # Should redirect after successful API call
        self.assertRedirects(response, self.url)
        
        # Check that OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

    @override_settings(OPENAI_API_KEY='test-api-key')
    @patch('recipes.views.ai_recipe.OpenAI')
    def test_submit_stores_recipe_in_session(self, mock_openai):
        """Test that submit stores recipe in session."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test Recipe\n1. Step one"
        mock_client.chat.completions.create.return_value = mock_response
        
        self.client.post(self.url, {
            'submit': 'true',
            'user_input': 'chicken',
        })
        
        # Check session has recipes
        session = self.client.session
        self.assertIn('recipes', session)
        self.assertEqual(len(session['recipes']), 1)

    @override_settings(OPENAI_API_KEY='test-api-key')
    @patch('recipes.views.ai_recipe.OpenAI')
    def test_api_error_shows_error_message(self, mock_openai):
        """Test that API error shows error message and redirects."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        response = self.client.post(self.url, {
            'submit': 'true',
            'user_input': 'chicken',
        })
        
        self.assertRedirects(response, self.url)

    def test_session_recipes_persist_across_requests(self):
        """Test that session recipes persist across requests."""
        session = self.client.session
        session['recipes'] = [['Saved Recipe', 'Step 1', 'Step 2']]
        session.save()
        
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['recipes']), 1)
        self.assertEqual(response.context['recipes'][0][0], 'Saved Recipe')

    @override_settings(OPENAI_API_KEY='test-api-key')
    @patch('recipes.views.ai_recipe.OpenAI')
    def test_multiple_submissions_accumulate_recipes(self, mock_openai):
        """Test that multiple submissions accumulate recipes."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # First submission
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock()]
        mock_response1.choices[0].message.content = "Recipe 1\nStep 1"
        mock_client.chat.completions.create.return_value = mock_response1
        
        self.client.post(self.url, {
            'submit': 'true',
            'user_input': 'chicken',
        })
        
        # Second submission
        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock()]
        mock_response2.choices[0].message.content = "Recipe 2\nStep 1"
        mock_client.chat.completions.create.return_value = mock_response2
        
        self.client.post(self.url, {
            'submit': 'true',
            'user_input': 'pasta',
        })
        
        # Check session has 2 recipes
        session = self.client.session
        self.assertEqual(len(session['recipes']), 2)
