"""
Management command to seed the database with demo data.

This command creates users, recipes, tracker data, social posts, and interactions.
"""

import os
from faker import Faker
from random import randint, random, choice, sample
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date, datetime
from django.conf import settings
from django.core.files import File
from recipes.models import User, Recipe, Profile, Meal, DailyLog, FastingSession, Tag, Post, Like, Comment, Rating


# User fixtures
user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'is_staff': True, 'is_superuser': True},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

# Comprehensive recipes with real data
RECIPES_DATA = [
    {
        'name': 'Classic Margherita Pizza',
        'difficulty': 'Moderate',
        'total_time': '1 hour 30 minutes',
        'servings': 4,
        'calories': 285,
        'average_rating': 5,
        'ingredients': 'Pizza dough, 400g canned tomatoes, 250g mozzarella cheese, fresh basil leaves, 2 cloves garlic, olive oil, salt, pepper',
        'method': '1) Preheat oven to 250°C. 2) Roll out pizza dough on a floured surface. 3) Spread crushed tomatoes over dough. 4) Add sliced mozzarella. 5) Drizzle with olive oil. 6) Bake for 10-12 minutes. 7) Top with fresh basil before serving.',
        'image': 'images/food1.jpg'
    },
    {
        'name': 'Grilled Salmon with Lemon',
        'difficulty': 'Easy',
        'total_time': '25 minutes',
        'servings': 2,
        'calories': 367,
        'average_rating': 5,
        'ingredients': '2 salmon fillets, 1 lemon, 2 tbsp olive oil, fresh dill, salt, black pepper, garlic powder',
        'method': '1) Season salmon with salt, pepper, and garlic powder. 2) Heat grill to medium-high. 3) Brush salmon with olive oil. 4) Grill for 4-5 minutes per side. 5) Squeeze lemon over cooked salmon. 6) Garnish with fresh dill.',
        'image': 'images/food2.jpg'
    },
    {
        'name': 'Chocolate Chip Cookies',
        'difficulty': 'Easy',
        'total_time': '30 minutes',
        'servings': 24,
        'calories': 148,
        'average_rating': 5,
        'ingredients': '225g butter, 150g brown sugar, 100g white sugar, 2 eggs, 1 tsp vanilla, 280g flour, 1 tsp baking soda, 300g chocolate chips',
        'method': '1) Cream butter and sugars. 2) Beat in eggs and vanilla. 3) Mix in flour and baking soda. 4) Fold in chocolate chips. 5) Drop spoonfuls onto baking sheet. 6) Bake at 180°C for 10-12 minutes.',
        'image': 'images/food3.jpg'
    },
    {
        'name': 'Caesar Salad',
        'difficulty': 'Easy',
        'total_time': '15 minutes',
        'servings': 4,
        'calories': 220,
        'average_rating': 4,
        'ingredients': '1 head romaine lettuce, 100g parmesan cheese, croutons, 2 anchovy fillets, 1 clove garlic, lemon juice, olive oil, Dijon mustard',
        'method': '1) Wash and chop lettuce. 2) Make dressing with anchovies, garlic, lemon, oil, and mustard. 3) Toss lettuce with dressing. 4) Add parmesan and croutons. 5) Serve immediately.',
        'image': 'images/food4.jpg'
    },
    {
        'name': 'Chicken Curry',
        'difficulty': 'Moderate',
        'total_time': '45 minutes',
        'servings': 4,
        'calories': 425,
        'average_rating': 5,
        'ingredients': '600g chicken thighs, 1 onion, 3 cloves garlic, 1 inch ginger, 2 tomatoes, curry powder, coconut milk, cilantro',
        'method': '1) Heat oil and sauté onions. 2) Add garlic and ginger. 3) Add chicken and brown. 4) Add curry powder and tomatoes. 5) Pour in coconut milk. 6) Simmer for 25 minutes. 7) Garnish with cilantro.',
        'image': 'images/food5.jpg'
    },
    {
        'name': 'Spaghetti Carbonara',
        'difficulty': 'Moderate',
        'total_time': '20 minutes',
        'servings': 4,
        'calories': 550,
        'average_rating': 5,
        'ingredients': '400g spaghetti, 200g pancetta, 4 eggs, 100g parmesan cheese, black pepper, garlic',
        'method': '1) Cook pasta until al dente. 2) Fry pancetta until crispy. 3) Whisk eggs with parmesan. 4) Toss hot pasta with pancetta. 5) Add egg mixture off heat. 6) Season with black pepper.',
        'image': 'images/food8.jpg'
    },
    {
        'name': 'Beef Burger',
        'difficulty': 'Easy',
        'total_time': '20 minutes',
        'servings': 4,
        'calories': 520,
        'average_rating': 4,
        'ingredients': '500g ground beef, 4 burger buns, lettuce, tomato, onion, pickles, cheese slices, ketchup, mustard',
        'method': '1) Form beef into 4 patties. 2) Season with salt and pepper. 3) Grill or pan-fry for 4-5 minutes per side. 4) Toast buns. 5) Assemble burgers with toppings. 6) Serve hot.',
        'image': 'images/food9.jpg'
    },
    {
        'name': 'Chocolate Brownies',
        'difficulty': 'Easy',
        'total_time': '45 minutes',
        'servings': 16,
        'calories': 195,
        'average_rating': 5,
        'ingredients': '200g dark chocolate, 150g butter, 3 eggs, 200g sugar, 100g flour, 30g cocoa powder, vanilla extract',
        'method': '1) Melt chocolate and butter. 2) Beat eggs with sugar. 3) Mix in chocolate mixture. 4) Fold in flour and cocoa. 5) Bake at 180°C for 25 minutes. 6) Cool before cutting.',
        'image': 'images/food10.jpg'
    },
    {
        'name': 'Chicken Stir Fry',
        'difficulty': 'Easy',
        'total_time': '20 minutes',
        'servings': 4,
        'calories': 310,
        'average_rating': 4,
        'ingredients': '500g chicken breast, bell peppers, broccoli, carrots, soy sauce, ginger, garlic, sesame oil',
        'method': '1) Cut chicken into strips. 2) Heat oil in wok. 3) Stir-fry chicken until cooked. 4) Add vegetables. 5) Add soy sauce and ginger. 6) Cook for 3-4 minutes. 7) Serve over rice.',
        'image': 'images/food11.jpg'
    },
    {
        'name': 'French Onion Soup',
        'difficulty': 'Moderate',
        'total_time': '1 hour',
        'servings': 4,
        'calories': 340,
        'average_rating': 4,
        'ingredients': '4 large onions, 50g butter, 1L beef stock, 200ml white wine, gruyère cheese, baguette, thyme',
        'method': '1) Slice onions thinly. 2) Caramelize in butter for 30 minutes. 3) Add wine and reduce. 4) Add stock and thyme. 5) Simmer for 20 minutes. 6) Top with bread and cheese. 7) Broil until golden.',
        'image': 'images/food12.jpg'
    },
    {
        'name': 'Pad Thai',
        'difficulty': 'Moderate',
        'total_time': '30 minutes',
        'servings': 2,
        'calories': 490,
        'average_rating': 5,
        'ingredients': '200g rice noodles, 200g shrimp, bean sprouts, 2 eggs, tamarind paste, fish sauce, palm sugar, peanuts, lime',
        'method': '1) Soak noodles. 2) Heat oil and cook shrimp. 3) Push aside and scramble eggs. 4) Add noodles and sauce. 5) Toss everything together. 6) Add bean sprouts. 7) Serve with peanuts and lime.',
        'image': 'images/food13.jpg'
    },
    {
        'name': 'Beef Steak',
        'difficulty': 'Moderate',
        'total_time': '20 minutes',
        'servings': 2,
        'calories': 680,
        'average_rating': 5,
        'ingredients': '2 ribeye steaks, salt, black pepper, butter, garlic, rosemary, olive oil',
        'method': '1) Season steaks generously. 2) Heat pan until very hot. 3) Sear steaks 3-4 minutes per side. 4) Add butter, garlic, and rosemary. 5) Baste steaks. 6) Rest for 5 minutes. 7) Slice and serve.',
        'image': 'images/food14.jpg'
    },
    {
        'name': 'Chicken Wings',
        'difficulty': 'Easy',
        'total_time': '45 minutes',
        'servings': 4,
        'calories': 430,
        'average_rating': 5,
        'ingredients': '1kg chicken wings, hot sauce, butter, garlic powder, salt, blue cheese dip',
        'method': '1) Season wings with salt and garlic powder. 2) Bake at 200°C for 40 minutes. 3) Mix hot sauce with melted butter. 4) Toss wings in sauce. 5) Serve with blue cheese dip.',
        'image': 'images/food15.jpg'
    },
    {
        'name': 'Vegetable Lasagna',
        'difficulty': 'Moderate',
        'total_time': '1 hour 30 minutes',
        'servings': 6,
        'calories': 385,
        'average_rating': 4,
        'ingredients': 'Lasagna sheets, ricotta cheese, mozzarella, spinach, mushrooms, marinara sauce, parmesan, basil',
        'method': '1) Cook lasagna sheets. 2) Sauté vegetables. 3) Layer sauce, pasta, ricotta, vegetables. 4) Repeat layers. 5) Top with mozzarella. 6) Bake at 180°C for 45 minutes. 7) Rest before serving.',
        'image': 'images/food16.jpg'
    },
]


class Command(BaseCommand):
    """
    Management command to seed the database with sample data.
    
    Creates users, recipes, tracker data, social posts, and interactions.
    """

    USER_COUNT = 50
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data (users, recipes, tracker data, posts)'
    
    # Local images for recipes (used by my_recipes template)
    RECIPE_IMAGES = [
        'images/food1.jpg', 'images/food2.jpg', 'images/food3.jpg', 
        'images/food4.jpg', 'images/food5.jpg', 'images/food8.jpg', 
        'images/food9.jpg', 'images/food10.jpg', 'images/food11.jpg', 
        'images/food12.jpg', 'images/food13.jpg', 'images/food14.jpg', 
        'images/food15.jpg', 'images/food16.jpg'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        """Execute the seeding process."""
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        self.create_users()
        self.create_recipes()
        self.create_tracker_data()
        self.create_tags()
        self.create_posts()
        self.create_post_interactions()
        
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    # ==================== USERS ====================

    def create_users(self):
        """Create fixture users and random users."""
        self.stdout.write("Creating users...")
        
        # Create fixture users
        for data in user_fixtures:
            self.try_create_user(data)

        # Create random users up to USER_COUNT
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            self.generate_random_user()
            user_count = User.objects.count()

        self.stdout.write(f"  Users: {User.objects.count()}")

    def generate_random_user(self):
        """Generate a single random user."""
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = f"{first_name}.{last_name}@example.org"
        username = f"@{first_name.lower()}{last_name.lower()}"
        self.try_create_user({
            'username': username, 
            'email': email, 
            'first_name': first_name, 
            'last_name': last_name
        })
       
    def try_create_user(self, data):
        """Attempt to create a user, ignoring errors."""
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=self.DEFAULT_PASSWORD,
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            user.is_staff = data.get('is_staff', False)
            user.is_superuser = data.get('is_superuser', False)
            user.save()
        except:
            pass

    # ==================== RECIPES ====================
    
    RECIPES_PER_USER_MIN = 2   # Minimum additional recipes per user
    RECIPES_PER_USER_MAX = 12  # Maximum additional recipes per user
    
    def create_recipes(self):
        """Create recipes from RECIPES_DATA and ensure each user has recipes."""
        self.stdout.write("Creating recipes...")
        
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING("  No users found. Skipping recipes."))
            return
        
        # First, create base recipes from RECIPES_DATA (shared pool)
        base_recipes_created = 0
        for recipe_data in RECIPES_DATA:
            try:
                if not Recipe.objects.filter(name=recipe_data['name']).exists():
                    recipe_data_copy = recipe_data.copy()
                    recipe_data_copy['created_by'] = choice(users)
                    recipe_data_copy['image'] = choice(self.RECIPE_IMAGES)
                    recipe_data_copy['method'] = self.convert_method_to_newlines(recipe_data['method'])
                    Recipe.objects.create(**recipe_data_copy)
                    base_recipes_created += 1
            except Exception as e:
                pass
        
        # Then, give each user additional random recipes for "My Recipes" page
        user_recipes_created = 0
        for user in users:
            # Each user gets a random number of ADDITIONAL recipes (on top of any base recipes)
            recipes_to_create = randint(self.RECIPES_PER_USER_MIN, self.RECIPES_PER_USER_MAX)
            
            for _ in range(recipes_to_create):
                recipe = self.create_random_recipe_for_user(user)
                if recipe:
                    user_recipes_created += 1
        
        self.stdout.write(f"  Base Recipes: {base_recipes_created}")
        self.stdout.write(f"  User Recipes: {user_recipes_created}")
        self.stdout.write(f"  Total Recipes: {Recipe.objects.count()}")
    
    def create_random_recipe_for_user(self, user):
        """Create a random recipe assigned to a specific user."""
        # Recipe name variations
        dishes = [
            "Pasta", "Salad", "Soup", "Stir Fry", "Curry", "Casserole", "Bowl",
            "Sandwich", "Wrap", "Tacos", "Pizza", "Risotto", "Noodles", "Rice",
            "Stew", "Pie", "Roast", "Bake", "Grill", "Skillet"
        ]
        proteins = [
            "Chicken", "Beef", "Pork", "Salmon", "Shrimp", "Tofu", "Turkey",
            "Lamb", "Tuna", "Cod", "Eggs", "Tempeh", "Chickpea", "Lentil"
        ]
        styles = [
            "Mediterranean", "Asian", "Mexican", "Italian", "Thai", "Indian",
            "Greek", "Japanese", "Korean", "American", "French", "Spanish",
            "Moroccan", "Vietnamese", "Hawaiian", "Cajun", "BBQ", "Teriyaki"
        ]
        adjectives = [
            "Creamy", "Spicy", "Crispy", "Savory", "Zesty", "Hearty", "Fresh",
            "Grilled", "Roasted", "Sautéed", "Baked", "Pan-Fried", "Slow-Cooked"
        ]
        
        # Generate unique recipe name
        name_style = randint(1, 4)
        if name_style == 1:
            name = f"{choice(adjectives)} {choice(proteins)} {choice(dishes)}"
        elif name_style == 2:
            name = f"{choice(styles)} {choice(proteins)} {choice(dishes)}"
        elif name_style == 3:
            name = f"{choice(proteins)} {choice(dishes)} {choice(styles)} Style"
        else:
            name = f"{choice(adjectives)} {choice(styles)} {choice(proteins)}"
        
        # Check if recipe with this name exists, add user suffix if needed
        base_name = name
        counter = 1
        while Recipe.objects.filter(name=name).exists():
            name = f"{base_name} #{counter}"
            counter += 1
            if counter > 10:
                return None  # Give up after 10 attempts
        
        # Generate random ingredients
        all_ingredients = [
            "olive oil", "garlic", "onion", "salt", "pepper", "butter",
            "chicken breast", "ground beef", "salmon fillet", "tofu",
            "rice", "pasta", "noodles", "bread", "tortillas",
            "tomatoes", "bell peppers", "broccoli", "spinach", "mushrooms",
            "carrots", "zucchini", "corn", "beans", "potatoes",
            "cheese", "cream", "milk", "eggs", "yogurt",
            "lemon", "lime", "ginger", "soy sauce", "honey",
            "paprika", "cumin", "oregano", "basil", "cilantro",
            "chicken broth", "coconut milk", "tomato sauce", "vinegar"
        ]
        num_ingredients = randint(5, 12)
        ingredients = ", ".join(sample(all_ingredients, min(num_ingredients, len(all_ingredients))))
        
        # Generate random method steps
        cooking_steps = [
            "Preheat the oven to 375°F (190°C)",
            "Heat oil in a large skillet over medium heat",
            "Season the protein with salt, pepper, and spices",
            "Cook until golden brown on both sides",
            "Add the vegetables and sauté for 5 minutes",
            "Pour in the sauce and bring to a simmer",
            "Reduce heat and let it cook for 15-20 minutes",
            "Stir occasionally to prevent sticking",
            "Add fresh herbs in the last few minutes",
            "Taste and adjust seasoning as needed",
            "Let rest for 5 minutes before serving",
            "Garnish with fresh herbs and serve hot",
            "Serve over rice or with crusty bread",
            "Top with cheese and let it melt",
            "Drizzle with olive oil before serving"
        ]
        num_steps = randint(4, 8)
        method = "\n".join(sample(cooking_steps, min(num_steps, len(cooking_steps))))
        
        difficulties = ["Very Easy", "Easy", "Moderate", "Hard", "Very Hard"]
        times = ["15 min", "20 min", "25 min", "30 min", "45 min", "1 hour", "1 hour 30 min"]
        
        try:
            recipe = Recipe.objects.create(
                name=name,
                created_by=user,
                ingredients=ingredients,
                method=method,
                difficulty=choice(difficulties),
                total_time=choice(times),
                servings=randint(2, 6),
                calories=randint(200, 800),
                average_rating=randint(1, 5),
                personal_rating=randint(1, 5),
                image=choice(self.RECIPE_IMAGES)
            )
            return recipe
        except Exception as e:
            return None
    
    def convert_method_to_newlines(self, method_string):
        """Convert '1) Step. 2) Step.' format to newline-separated steps."""
        import re
        # Split by pattern like "1) ", "2) ", etc.
        steps = re.split(r'\s*\d+\)\s*', method_string)
        # Filter out empty strings and strip whitespace
        steps = [step.strip().rstrip('.') for step in steps if step.strip()]
        return '\n'.join(steps)

    # ==================== TRACKER DATA ====================

    def create_tracker_data(self):
        """Create tracker data (profiles, meals, water, fasting) for all users."""
        self.stdout.write("Creating tracker data...")
        
        for user in User.objects.all():
            self.create_profile_for_user(user)
            self.generate_user_history(user, days=30)
        
        self.stdout.write(f"  Profiles: {Profile.objects.count()}")
        self.stdout.write(f"  Meals: {Meal.objects.count()}")
        self.stdout.write(f"  Daily Logs: {DailyLog.objects.count()}")
        self.stdout.write(f"  Fasting Sessions: {FastingSession.objects.count()}")

    def create_profile_for_user(self, user):
        """Create a Profile with random goals for a user."""
        try:
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'calorie_goal': randint(1500, 3000),
                    'protein_goal': randint(100, 200),
                    'carbs_goal': randint(150, 300),
                    'fat_goal': randint(50, 150),
                }
            )
        except:
            pass

    def generate_user_history(self, user, days=30):
        """Generate tracker history for the last N days for a user."""
        FastingSession.objects.filter(user=user).delete()
        
        today = date.today()
        start_date = today - timedelta(days=days - 1)
        last_end_datetime = None
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Generate meals (3-5 per day)
            for _ in range(randint(3, 5)):
                self.create_random_meal(user, current_date)
            
            # Generate daily log
            self.create_daily_log(user, current_date)
            
            # Generate fasting sessions (70% chance)
            if random() < 0.7:
                last_end_datetime = self.create_fasting_session(user, current_date, last_end_datetime)

    def create_random_meal(self, user, meal_date):
        """Create a random meal for a user on a given date."""
        meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        meal_type = choice(meal_types)
        
        calorie_ranges = {
            'Breakfast': (250, 600),
            'Lunch': (400, 800),
            'Dinner': (500, 1000),
            'Snack': (100, 300),
        }
        
        calories = randint(*calorie_ranges[meal_type])
        protein_g = round((calories * 0.25) / 4, 1)
        carbs_g = round((calories * 0.45) / 4, 1)
        fat_g = round((calories * 0.30) / 9, 1)
        
        meal_names = {
            'Breakfast': ['Oatmeal', 'Scrambled Eggs', 'Toast', 'Cereal', 'Yogurt Bowl'],
            'Lunch': ['Grilled Chicken Salad', 'Pasta', 'Sandwich', 'Soup', 'Rice Bowl'],
            'Dinner': ['Steak and Potatoes', 'Fish and Vegetables', 'Pasta Dish', 'Stir Fry', 'Pizza'],
            'Snack': ['Apple', 'Almonds', 'Protein Bar', 'Greek Yogurt', 'Banana'],
        }
        
        try:
            Meal.objects.create(
                user=user,
                name=choice(meal_names[meal_type]),
                meal_type=meal_type,
                date=meal_date,
                calories=calories,
                protein_g=protein_g,
                carbs_g=carbs_g,
                fat_g=fat_g,
            )
        except:
            pass

    def create_daily_log(self, user, intake_date):
        """Create a daily log entry."""
        is_weekend = intake_date.weekday() >= 5
        calorie_goal = randint(2500, 3000) if is_weekend else randint(1800, 2500)
        
        try:
            DailyLog.objects.update_or_create(
                user=user,
                date=intake_date,
                defaults={
                    'amount_ml': randint(1000, 3000),
                    'calorie_goal': calorie_goal,
                    'protein_goal': round((calorie_goal * 0.30) / 4),
                    'carbs_goal': round((calorie_goal * 0.40) / 4),
                    'fat_goal': round((calorie_goal * 0.30) / 9),
                    'water_goal': randint(2000, 3000),
                }
            )
        except:
            pass

    def create_fasting_session(self, user, session_date, last_end_datetime):
        """Create a fasting session for a user."""
        target_duration = choice([14, 16, 18])
        hour = randint(18, 22)
        minute = randint(0, 59)
        base_start_time = datetime.combine(session_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
        start_datetime = timezone.make_aware(base_start_time)
        
        if last_end_datetime and start_datetime < last_end_datetime:
            return last_end_datetime
            
        actual_duration_hours = target_duration + (random() * 2 - 1) 
        end_datetime = start_datetime + timedelta(hours=actual_duration_hours)
        
        now = timezone.now()
        is_active = False
        end_datetime_record = end_datetime
        
        if end_datetime > now:
            if start_datetime <= now:
                is_active = True
                end_datetime_record = None
            else:
                return last_end_datetime 

        try:
            FastingSession.objects.create(
                user=user,
                start_date_time=start_datetime,
                end_date_time=end_datetime_record,
                target_duration=target_duration,
                is_active=is_active,
            )
            return end_datetime 
        except:
            return last_end_datetime

    # ==================== TAGS ====================
    
    def create_tags(self):
        """Create standard tags for posts."""
        self.stdout.write("Creating tags...")
        
        tags = [
            "Breakfast", "Lunch", "Dinner", "Dessert", 
            "Snack", "Vegan", "Vegetarian", "Gluten-Free", 
            "Keto", "Paleo", "High Protein", "Low Carb", 
            "Spicy", "Quick & Easy", "Meal Prep", "Healthy"
        ]
        
        for tag_name in tags:
            Tag.objects.get_or_create(name=tag_name)
        
        self.stdout.write(f"  Tags: {Tag.objects.count()}")

    # ==================== POSTS ====================
    
    def create_posts(self):
        """Generate social posts with real food data and images."""
        self.stdout.write("Creating posts using local 'seed_images' folder...")
        
        users = list(User.objects.all())
        tags = list(Tag.objects.all())
        
        if not users:
            self.stdout.write("  No users found. Skipping posts.")
            return
        
        FOOD_TITLES = [
            "Homemade Margherita Pizza with Fresh Basil",
            "Creamy Roasted Tomato Soup & Grilled Cheese",
            "Baja-Style Spicy Chicken Tacos",
            "The Ultimate Classic Cheeseburger",
            "Fluffy Buttermilk Pancakes with Berries",
            "Fresh Mediterranean Greek Salad",
            "Garlic Herb Hummus with Veggie Sticks",
            "Chewy Salted Chocolate Chip Cookies",
            "Creamy Wild Mushroom Risotto",
            "Slow-Cooked BBQ Ribs with Slaw",
            "Authentic Chicken Pad Thai",
            "Rich & Creamy Chicken Tikka Masala",
            "Classic Spaghetti Carbonara",
            "Quick Veggie Stir-Fry with Tofu",
            "Avocado Toast with a Perfect Poached Egg",
            "Acai Berry Smoothie Bowl with Granola",
            "Crispy Fried Calamari with Marinara",
            "Decadent Lobster Mac and Cheese",
            "Baked French Onion Soup",
            "Steak Frites with Garlic Aioli"
        ]

        FOOD_CAPTIONS = [
            "Finally perfected my dough recipe! The crust was crunchy on the outside and soft inside.",
            "Perfect comfort food for this chilly weather. Highly recommend with sourdough grilled cheese.",
            "A little spicy, a little tangy, and totally delicious. Don't skimp on the lime juice!",
            "Sometimes you just need a classic. Juicy patty, melted cheddar, all the fixings.",
            "Weekend breakfast done right. These were so fluffy! Served with real maple syrup.",
            "Fresh, healthy, and packed with flavor. The homemade dressing ties it all together.",
            "The perfect snack for sharing. So much better than store-bought!",
            "Warm, gooey, and loaded with chocolate pools. A sprinkle of sea salt makes them addictive.",
            "A labor of love that requires constant stirring, but the creamy texture is so worth it.",
            "Fall-off-the-bone tender after cooking low and slow for 6 hours.",
            "Tastes just like takeout! It's all about balancing the sweet, sour, and savory flavors.",
            "Rich, aromatic, and full of spices. Best enjoyed with some warm garlic naan.",
            "A Roman classic made the right way—no cream, just eggs, Pecorino, and guanciale.",
            "A super fast and healthy weeknight dinner. Great way to use up fridge veggies.",
            "My go-to breakfast. Simple, nutritious, and delicious. The runny yolk is the best part.",
            "Packed with antioxidants and energy. Topped with homemade granola and coconut flakes.",
            "Crispy golden coating on the outside, tender on the inside. Fresh lemon is essential.",
            "Indulgent and cheesy with big chunks of lobster meat. A real treat!",
            "Rich beef broth, caramelized onions, and melted Gruyère cheese. So satisfying.",
            "Cooked medium-rare with a crispy sear. The garlic aioli for dipping the fries is incredible."
        ]

        cuisine_choices = ['Italian', 'Mexican', 'Chinese', 'Indian', 'Japanese', 'Thai', 
                           'French', 'American', 'Greek', 'Spanish', 'Mediterranean', 'Korean']
        
        # Try to find seed images using BASE_DIR for reliability
        image_folder = os.path.join(settings.BASE_DIR, 'recipes', 'management', 'seed_images')
        
        image_files = []
        try:
            image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f"  Could not find folder: {image_folder}"))
            self.stdout.write(self.style.WARNING("  Posts will be created without images."))

        # Loop 100 times to create volume
        for i in range(100):
            author = choice(users)
            
            post_data = {
                'author': author,
                'title': choice(FOOD_TITLES),
                'caption': choice(FOOD_CAPTIONS),
                'cuisine': choice(cuisine_choices),
                'difficulty': choice(['Easy', 'Moderate', 'Hard']),
                'prep_time': f"{randint(15, 90)} min",
                'servings': randint(2, 6),
            }

            image_file_handler = None
            if image_files:
                random_image_name = choice(image_files)
                image_path = os.path.join(image_folder, random_image_name)
                f = open(image_path, 'rb')
                image_file_handler = File(f, name=random_image_name)

            try:
                if image_file_handler:
                    post = Post.objects.create(image=image_file_handler, **post_data)
                    image_file_handler.close()
                else:
                    post = Post.objects.create(**post_data)
                
                if tags:
                    random_tags = sample(tags, k=randint(1, 3))
                    post.tags.set(random_tags)
            except:
                pass
        
        self.stdout.write(f"  Posts: {Post.objects.count()}")

    # ==================== INTERACTIONS ====================
    
    def create_post_interactions(self):
        """Generate Likes, Comments, and Ratings for posts."""
        self.stdout.write("Creating post interactions...")
        
        users = list(User.objects.all())
        posts = Post.objects.all()
        
        comments_list = [
            "This looks amazing!", "Can't wait to try this.", "Delicious!", 
            "Great recipe.", "My family loved it.", "Yum!", "So tasty.", 
            "Thanks for sharing!", "Added to my list.", "Wow!"
        ]

        if not users or not posts:
            return

        for post in posts:
            # Generate Likes
            num_likes = randint(0, 20)
            likers = sample(users, k=min(num_likes, len(users)))
            for user in likers:
                Like.objects.get_or_create(user=user, post=post)

            # Generate Comments
            num_comments = randint(0, 5)
            commenters = sample(users, k=min(num_comments, len(users)))
            for user in commenters:
                try:
                    Comment.objects.create(user=user, post=post, text=choice(comments_list))
                except:
                    pass

            # Generate Ratings
            num_ratings = randint(0, 15)
            raters = sample(users, k=min(num_ratings, len(users)))
            
            total_score = 0
            for user in raters:
                score = randint(3, 5)
                try:
                    Rating.objects.create(user=user, post=post, score=score)
                    total_score += score
                except:
                    pass
            
            if num_ratings > 0:
                post.rating_count = num_ratings
                post.rating_total_score = total_score
                post.save()

        self.stdout.write(f"  Likes: {Like.objects.count()}")
        self.stdout.write(f"  Comments: {Comment.objects.count()}")
        self.stdout.write(f"  Ratings: {Rating.objects.count()}")