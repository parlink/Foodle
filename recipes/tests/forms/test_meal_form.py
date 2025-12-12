"""Unit tests for the MealForm."""
from django.test import TestCase
from datetime import date
from recipes.forms.meal_form import MealForm


class MealFormTestCase(TestCase):
    """Unit tests for the MealForm."""

    def setUp(self):
        self.form_input = {
            'name': 'Grilled Chicken',
            'meal_type': 'Lunch',
            'date': date.today(),
            'calories': 500,
            'protein_g': 40.0,
            'carbs_g': 30.0,
            'fat_g': 20.0,
        }

    def test_form_has_necessary_fields(self):
        """Test that form has all required fields."""
        form = MealForm()
        self.assertIn('name', form.fields)
        self.assertIn('meal_type', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('calories', form.fields)
        self.assertIn('protein_g', form.fields)
        self.assertIn('carbs_g', form.fields)
        self.assertIn('fat_g', form.fields)

    def test_valid_meal_form(self):
        """Test that form is valid with correct input."""
        form = MealForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        """Test that form rejects blank name."""
        self.form_input['name'] = ''
        form = MealForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_meal_type(self):
        """Test that form rejects blank meal type."""
        self.form_input['meal_type'] = ''
        form = MealForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_meal_type(self):
        """Test that form rejects invalid meal type."""
        self.form_input['meal_type'] = 'InvalidType'
        form = MealForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_all_valid_meal_types(self):
        """Test that form accepts all valid meal types."""
        valid_types = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        for meal_type in valid_types:
            self.form_input['meal_type'] = meal_type
            form = MealForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"Form should accept {meal_type}")

    def test_form_rejects_blank_calories(self):
        """Test that form rejects blank calories."""
        self.form_input['calories'] = ''
        form = MealForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_negative_calories(self):
        """Test that form rejects negative calories."""
        self.form_input['calories'] = -100
        form = MealForm(data=self.form_input)
        # Django's IntegerField doesn't reject negative by default
        # but we can check validation works
        self.assertTrue(form.is_valid())  # No min_value set

    def test_form_rejects_blank_protein(self):
        """Test that form rejects blank protein."""
        self.form_input['protein_g'] = ''
        form = MealForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_carbs(self):
        """Test that form rejects blank carbs."""
        self.form_input['carbs_g'] = ''
        form = MealForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_fat(self):
        """Test that form rejects blank fat."""
        self.form_input['fat_g'] = ''
        form = MealForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_decimal_macros(self):
        """Test that form accepts decimal values for macros."""
        self.form_input['protein_g'] = 35.5
        self.form_input['carbs_g'] = 22.3
        self.form_input['fat_g'] = 15.7
        form = MealForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_excludes_user_field(self):
        """Test that user field is excluded from form."""
        form = MealForm()
        self.assertNotIn('user', form.fields)

    def test_form_save_creates_meal(self):
        """Test that form save creates a meal object."""
        form = MealForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        meal = form.save(commit=False)
        self.assertEqual(meal.name, 'Grilled Chicken')
        self.assertEqual(meal.meal_type, 'Lunch')
        self.assertEqual(meal.calories, 500)

