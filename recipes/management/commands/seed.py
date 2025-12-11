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
from recipes.models import User, Recipe, Profile, Meal, DailyLog, FastingSession, Tag, Post, Like, Comment, Rating
from django.core.files import File


# User fixtures
user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'is_staff': True, 'is_superuser': True},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

# Comprehensive recipes with real data and Unsplash images
RECIPES_DATA = [
    {
        'name': 'Classic Margherita Pizza',
        'difficulty': 'Moderate',
        'total_time': '1 hour 30 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': 'Pizza dough, 400g canned tomatoes, 250g mozzarella cheese, fresh basil leaves, 2 cloves garlic, olive oil, salt, pepper',
        'method': '1) Preheat oven to 250°C. 2) Roll out pizza dough on a floured surface. 3) Spread crushed tomatoes over dough. 4) Add sliced mozzarella. 5) Drizzle with olive oil. 6) Bake for 10-12 minutes. 7) Top with fresh basil before serving.',
        'image_url': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800'
    },
    {
        'name': 'Grilled Salmon with Lemon',
        'difficulty': 'Easy',
        'total_time': '25 minutes',
        'servings': 2,
        'average_rating': 5,
        'ingredients': '2 salmon fillets, 1 lemon, 2 tbsp olive oil, fresh dill, salt, black pepper, garlic powder',
        'method': '1) Season salmon with salt, pepper, and garlic powder. 2) Heat grill to medium-high. 3) Brush salmon with olive oil. 4) Grill for 4-5 minutes per side. 5) Squeeze lemon over cooked salmon. 6) Garnish with fresh dill.',
        'image_url': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800'
    },
    {
        'name': 'Chocolate Chip Cookies',
        'difficulty': 'Easy',
        'total_time': '30 minutes',
        'servings': 24,
        'average_rating': 5,
        'ingredients': '225g butter, 150g brown sugar, 100g white sugar, 2 eggs, 1 tsp vanilla, 280g flour, 1 tsp baking soda, 300g chocolate chips',
        'method': '1) Cream butter and sugars. 2) Beat in eggs and vanilla. 3) Mix in flour and baking soda. 4) Fold in chocolate chips. 5) Drop spoonfuls onto baking sheet. 6) Bake at 180°C for 10-12 minutes.',
        'image_url': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800'
    },
    {
        'name': 'Caesar Salad',
        'difficulty': 'Easy',
        'total_time': '15 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '1 head romaine lettuce, 100g parmesan cheese, croutons, 2 anchovy fillets, 1 clove garlic, lemon juice, olive oil, Dijon mustard',
        'method': '1) Wash and chop lettuce. 2) Make dressing with anchovies, garlic, lemon, oil, and mustard. 3) Toss lettuce with dressing. 4) Add parmesan and croutons. 5) Serve immediately.',
        'image_url': 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=800'
    },
    {
        'name': 'Chicken Curry',
        'difficulty': 'Moderate',
        'total_time': '45 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '600g chicken thighs, 1 onion, 3 cloves garlic, 1 inch ginger, 2 tomatoes, curry powder, coconut milk, cilantro',
        'method': '1) Heat oil and sauté onions. 2) Add garlic and ginger. 3) Add chicken and brown. 4) Add curry powder and tomatoes. 5) Pour in coconut milk. 6) Simmer for 25 minutes. 7) Garnish with cilantro.',
        'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800'
    },
    {
        'name': 'Spaghetti Carbonara',
        'difficulty': 'Moderate',
        'total_time': '20 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '400g spaghetti, 200g pancetta, 4 eggs, 100g parmesan cheese, black pepper, garlic',
        'method': '1) Cook pasta until al dente. 2) Fry pancetta until crispy. 3) Whisk eggs with parmesan. 4) Toss hot pasta with pancetta. 5) Add egg mixture off heat. 6) Season with black pepper.',
        'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800'
    },
    {
        'name': 'Beef Burger',
        'difficulty': 'Easy',
        'total_time': '20 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '500g ground beef, 4 burger buns, lettuce, tomato, onion, pickles, cheese slices, ketchup, mustard',
        'method': '1) Form beef into 4 patties. 2) Season with salt and pepper. 3) Grill or pan-fry for 4-5 minutes per side. 4) Toast buns. 5) Assemble burgers with toppings. 6) Serve hot.',
        'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800'
    },
    {
        'name': 'Chocolate Brownies',
        'difficulty': 'Easy',
        'total_time': '45 minutes',
        'servings': 16,
        'average_rating': 5,
        'ingredients': '200g dark chocolate, 150g butter, 3 eggs, 200g sugar, 100g flour, 30g cocoa powder, vanilla extract',
        'method': '1) Melt chocolate and butter. 2) Beat eggs with sugar. 3) Mix in chocolate mixture. 4) Fold in flour and cocoa. 5) Bake at 180°C for 25 minutes. 6) Cool before cutting.',
        'image_url': 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800'
    },
    {
        'name': 'Chicken Stir Fry',
        'difficulty': 'Easy',
        'total_time': '20 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '500g chicken breast, bell peppers, broccoli, carrots, soy sauce, ginger, garlic, sesame oil',
        'method': '1) Cut chicken into strips. 2) Heat oil in wok. 3) Stir-fry chicken until cooked. 4) Add vegetables. 5) Add soy sauce and ginger. 6) Cook for 3-4 minutes. 7) Serve over rice.',
        'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800'
    },
    {
        'name': 'French Onion Soup',
        'difficulty': 'Moderate',
        'total_time': '1 hour',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '4 large onions, 50g butter, 1L beef stock, 200ml white wine, gruyère cheese, baguette, thyme',
        'method': '1) Slice onions thinly. 2) Caramelize in butter for 30 minutes. 3) Add wine and reduce. 4) Add stock and thyme. 5) Simmer for 20 minutes. 6) Top with bread and cheese. 7) Broil until golden.',
        'image_url': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800'
    },
    {
        'name': 'Pad Thai',
        'difficulty': 'Moderate',
        'total_time': '30 minutes',
        'servings': 2,
        'average_rating': 5,
        'ingredients': '200g rice noodles, 200g shrimp, bean sprouts, 2 eggs, tamarind paste, fish sauce, palm sugar, peanuts, lime',
        'method': '1) Soak noodles. 2) Heat oil and cook shrimp. 3) Push aside and scramble eggs. 4) Add noodles and sauce. 5) Toss everything together. 6) Add bean sprouts. 7) Serve with peanuts and lime.',
        'image_url': 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800'
    },
    {
        'name': 'Beef Steak',
        'difficulty': 'Moderate',
        'total_time': '20 minutes',
        'servings': 2,
        'average_rating': 5,
        'ingredients': '2 ribeye steaks, salt, black pepper, butter, garlic, rosemary, olive oil',
        'method': '1) Season steaks generously. 2) Heat pan until very hot. 3) Sear steaks 3-4 minutes per side. 4) Add butter, garlic, and rosemary. 5) Baste steaks. 6) Rest for 5 minutes. 7) Slice and serve.',
        'image_url': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800'
    },
    {
        'name': 'Chicken Wings',
        'difficulty': 'Easy',
        'total_time': '45 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '1kg chicken wings, hot sauce, butter, garlic powder, salt, blue cheese dip',
        'method': '1) Season wings with salt and garlic powder. 2) Bake at 200°C for 40 minutes. 3) Mix hot sauce with melted butter. 4) Toss wings in sauce. 5) Serve with blue cheese dip.',
        'image_url': 'https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=800'
    },
    {
        'name': 'Vegetable Lasagna',
        'difficulty': 'Moderate',
        'total_time': '1 hour 30 minutes',
        'servings': 6,
        'average_rating': 4,
        'ingredients': 'Lasagna sheets, ricotta cheese, mozzarella, spinach, mushrooms, marinara sauce, parmesan, basil',
        'method': '1) Cook lasagna sheets. 2) Sauté vegetables. 3) Layer sauce, pasta, ricotta, vegetables. 4) Repeat layers. 5) Top with mozzarella. 6) Bake at 180°C for 45 minutes. 7) Rest before serving.',
        'image_url': 'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=800'
    },
    {
        'name': 'Fish and Chips',
        'difficulty': 'Moderate',
        'total_time': '40 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '4 cod fillets, 4 large potatoes, flour, beer, baking powder, salt, vinegar, tartar sauce',
        'method': '1) Cut potatoes into chips. 2) Fry chips until golden. 3) Make batter with flour, beer, and baking powder. 4) Dip fish in batter. 5) Deep fry until crispy. 6) Serve with chips, vinegar, and tartar sauce.',
        'image_url': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800'
    },
    {
        'name': 'Chicken Noodle Soup',
        'difficulty': 'Easy',
        'total_time': '1 hour',
        'servings': 6,
        'average_rating': 4,
        'ingredients': '1 whole chicken, 200g egg noodles, carrots, celery, onion, chicken stock, herbs, salt, pepper',
        'method': '1) Simmer chicken in stock for 30 minutes. 2) Remove and shred chicken. 3) Add vegetables and cook. 4) Add noodles and cook. 5) Return chicken. 6) Season and serve hot.',
        'image_url': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800'
    },
    {
        'name': 'Beef Bolognese',
        'difficulty': 'Moderate',
        'total_time': '2 hours',
        'servings': 6,
        'average_rating': 5,
        'ingredients': '500g ground beef, 400g pasta, 1 onion, 2 carrots, celery, canned tomatoes, red wine, parmesan, basil',
        'method': '1) Sauté vegetables. 2) Add beef and brown. 3) Add wine and reduce. 4) Add tomatoes and simmer for 1.5 hours. 5) Cook pasta. 6) Toss pasta with sauce. 7) Top with parmesan and basil.',
        'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800'
    },
    {
        'name': 'Sushi Rolls',
        'difficulty': 'Hard',
        'total_time': '1 hour',
        'servings': 4,
        'average_rating': 5,
        'ingredients': 'Sushi rice, nori sheets, salmon, avocado, cucumber, rice vinegar, sugar, salt, soy sauce, wasabi',
        'method': '1) Cook and season rice. 2) Place nori on bamboo mat. 3) Spread rice. 4) Add fillings. 5) Roll tightly. 6) Slice into pieces. 7) Serve with soy sauce and wasabi.',
        'image_url': 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=800'
    },
    {
        'name': 'Apple Pie',
        'difficulty': 'Moderate',
        'total_time': '1 hour 30 minutes',
        'servings': 8,
        'average_rating': 5,
        'ingredients': 'Pie crust, 6 apples, sugar, cinnamon, butter, lemon juice, egg for egg wash',
        'method': '1) Peel and slice apples. 2) Mix with sugar, cinnamon, and lemon. 3) Fill pie crust. 4) Top with second crust. 5) Brush with egg wash. 6) Bake at 200°C for 45 minutes. 7) Cool before serving.',
        'image_url': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=800'
    },
    {
        'name': 'Ramen Noodles',
        'difficulty': 'Moderate',
        'total_time': '1 hour',
        'servings': 4,
        'average_rating': 5,
        'ingredients': 'Ramen noodles, pork belly, soft-boiled eggs, nori, green onions, miso paste, soy sauce, sesame oil',
        'method': '1) Simmer pork belly for 45 minutes. 2) Make broth with miso and soy. 3) Cook noodles. 4) Soft-boil eggs. 5) Assemble bowls with noodles, broth, pork, egg, nori, and green onions.',
        'image_url': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800'
    },
    {
        'name': 'BBQ Ribs',
        'difficulty': 'Moderate',
        'total_time': '3 hours',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '2 racks pork ribs, BBQ sauce, brown sugar, paprika, garlic powder, salt, pepper',
        'method': '1) Season ribs with spices. 2) Wrap in foil and bake at 150°C for 2.5 hours. 3) Brush with BBQ sauce. 4) Grill for 10 minutes. 5) Brush again with sauce. 6) Rest and serve.',
        'image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=800'
    },
    {
        'name': 'Chicken Tikka Masala',
        'difficulty': 'Moderate',
        'total_time': '1 hour',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '600g chicken, yogurt, garam masala, tomato sauce, cream, onions, garlic, ginger, cilantro',
        'method': '1) Marinate chicken in yogurt and spices. 2) Grill chicken pieces. 3) Sauté onions, garlic, and ginger. 4) Add tomato sauce and spices. 5) Add cream and chicken. 6) Simmer for 15 minutes. 7) Garnish with cilantro.',
        'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800'
    },
    {
        'name': 'Pancakes',
        'difficulty': 'Easy',
        'total_time': '20 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '200g flour, 2 eggs, 300ml milk, 2 tbsp sugar, 1 tsp baking powder, butter, maple syrup',
        'method': '1) Mix dry ingredients. 2) Whisk in wet ingredients. 3) Let rest 10 minutes. 4) Cook on griddle. 5) Flip when bubbles form. 6) Serve with butter and syrup.',
        'image_url': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800'
    },
    {
        'name': 'Tiramisu',
        'difficulty': 'Moderate',
        'total_time': '4 hours',
        'servings': 8,
        'average_rating': 5,
        'ingredients': 'Ladyfinger cookies, espresso, mascarpone cheese, eggs, sugar, cocoa powder, vanilla',
        'method': '1) Make coffee and cool. 2) Beat egg yolks with sugar. 3) Mix in mascarpone. 4) Dip cookies in coffee. 5) Layer cookies and cream. 6) Chill for 4 hours. 7) Dust with cocoa before serving.',
        'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800'
    },
    {
        'name': 'Beef Stroganoff',
        'difficulty': 'Moderate',
        'total_time': '45 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '600g beef sirloin, mushrooms, onions, sour cream, beef stock, flour, butter, egg noodles, paprika',
        'method': '1) Slice beef thinly. 2) Brown beef and set aside. 3) Sauté mushrooms and onions. 4) Add flour and stock. 5) Return beef and simmer. 6) Stir in sour cream. 7) Serve over noodles.',
        'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800'
    },
    {
        'name': 'Mushroom Risotto',
        'difficulty': 'Moderate',
        'total_time': '40 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': 'Arborio rice, mushrooms, onions, white wine, chicken stock, parmesan, butter, garlic, thyme',
        'method': '1) Sauté mushrooms and set aside. 2) Cook onions until soft. 3) Add rice and toast. 4) Add wine and reduce. 5) Add stock gradually, stirring. 6) Stir in mushrooms, parmesan, and butter. 7) Serve immediately.',
        'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800'
    },
    {
        'name': 'Greek Salad',
        'difficulty': 'Easy',
        'total_time': '15 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': 'Cucumber, tomatoes, red onion, feta cheese, kalamata olives, olive oil, lemon, oregano',
        'method': '1) Chop vegetables into chunks. 2) Mix olive oil, lemon, and oregano. 3) Toss vegetables with dressing. 4) Add feta and olives. 5) Season with salt and pepper. 6) Serve immediately.',
        'image_url': 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=800'
    },
    {
        'name': 'Chicken Teriyaki',
        'difficulty': 'Easy',
        'total_time': '30 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '600g chicken thighs, soy sauce, mirin, sugar, ginger, garlic, sesame seeds, rice',
        'method': '1) Make teriyaki sauce. 2) Marinate chicken. 3) Cook chicken until done. 4) Add sauce and reduce. 5) Glaze chicken. 6) Serve over rice. 7) Garnish with sesame seeds.',
        'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800'
    },
    {
        'name': 'Vegetable Curry',
        'difficulty': 'Easy',
        'total_time': '30 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': 'Mixed vegetables, curry powder, coconut milk, onions, garlic, ginger, cilantro, rice',
        'method': '1) Sauté onions, garlic, and ginger. 2) Add curry powder. 3) Add vegetables and cook. 4) Pour in coconut milk. 5) Simmer for 15 minutes. 6) Serve over rice with cilantro.',
        'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800'
    },
    {
        'name': 'Chicken Fried Rice',
        'difficulty': 'Easy',
        'total_time': '20 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': 'Cooked rice, chicken, eggs, peas, carrots, soy sauce, sesame oil, green onions, garlic',
        'method': '1) Scramble eggs and set aside. 2) Cook chicken. 3) Add vegetables. 4) Add rice and break up. 5) Stir in eggs and soy sauce. 6) Cook until heated through. 7) Garnish with green onions.',
        'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800'
    },
]


class Command(BaseCommand):
    """
    Management command to seed the database with sample data.
    
    Creates users, recipes, tracker data, social posts, and interactions.
    """

    USER_COUNT = 5
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data (users, recipes, tracker data, posts)'

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
    
    def create_recipes(self):
        """Create recipes from RECIPES_DATA."""
        self.stdout.write("Creating recipes...")
        created = 0
        
        for recipe_data in RECIPES_DATA:
            try:
                if not Recipe.objects.filter(name=recipe_data['name']).exists():
                    Recipe.objects.create(**recipe_data)
                    created += 1
            except:
                pass
        
        self.stdout.write(f"  Recipes: {Recipe.objects.count()} ({created} new)")

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
        self.stdout.write("Creating posts...")
        
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
        
        # Try to find seed images
        image_dir = os.path.join(os.path.dirname(__file__), '..', 'seed_images')
        image_files = []
        try:
            image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING("  seed_images folder not found. Posts created without images."))

        for i in range(len(FOOD_TITLES)):
            author = choice(users)
            
            post_data = {
                'author': author,
                'title': FOOD_TITLES[i],
                'caption': FOOD_CAPTIONS[i % len(FOOD_CAPTIONS)],
                'cuisine': choice(cuisine_choices),
                'difficulty': choice(['Easy', 'Moderate', 'Hard']),
                'prep_time': f"{randint(15, 90)} min",
                'servings': randint(2, 6),
            }

            image_file_handler = None
            if image_files:
                random_image_name = choice(image_files)
                image_path = os.path.join(image_dir, random_image_name)
                f = open(image_path, 'rb')
                image_file_handler = File(f, name=random_image_name)

            try:
                if image_file_handler:
                    post = Post.objects.create(image=image_file_handler, **post_data)
                    image_file_handler.close()
                else:
                    post = Post.objects.create(**post_data)
                
                if tags:
                    random_tags = sample(tags, k=randint(1, min(3, len(tags))))
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
