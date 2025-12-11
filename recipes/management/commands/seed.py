"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""


import os
from faker import Faker
from random import randint, random, choice, sample
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta, date, datetime
from recipes.models import User, Recipe, Profile, Meal, DailyLog, FastingSession, Tag, Post, Like, Comment, Rating
from django.core.files import File


user_fixtures = [
    {'name': 'John','surname': 'Doe', 'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'is_staff': True, 'is_superuser': True},
    {'name': 'Jane','surname': 'Doe', 'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'name': 'Charlie','surname': 'Johnson', 'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

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
        'name': 'Cauliflower Fried Rice',
        'difficulty': 'Easy',
        'total_time': '20 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '1 head cauliflower, eggs, peas, carrots, soy sauce, sesame oil, green onions, garlic, ginger',
        'method': '1) Grate cauliflower into rice-like pieces. 2) Scramble eggs and set aside. 3) Sauté vegetables. 4) Add cauliflower rice. 5) Stir in eggs and soy sauce. 6) Cook until tender. 7) Serve hot.',
        'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800'
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
        'name': 'Lobster Roll',
        'difficulty': 'Moderate',
        'total_time': '30 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '4 lobster tails, hot dog buns, mayonnaise, lemon, celery, chives, butter, salt, pepper',
        'method': '1) Boil lobster tails. 2) Remove meat and chop. 3) Mix with mayo, lemon, celery, and chives. 4) Butter and toast buns. 5) Fill buns with lobster mixture. 6) Serve immediately.',
        'image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=800'
    },
    {
        'name': 'Vegetable Stir Fry',
        'difficulty': 'Easy',
        'total_time': '15 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': 'Broccoli, bell peppers, carrots, snow peas, mushrooms, soy sauce, ginger, garlic, sesame oil',
        'method': '1) Cut vegetables into uniform pieces. 2) Heat oil in wok. 3) Stir-fry vegetables. 4) Add garlic and ginger. 5) Add soy sauce. 6) Cook until crisp-tender. 7) Serve over rice.',
        'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800'
    },
    {
        'name': 'Tiramisu',
        'difficulty': 'Moderate',
        'total_time': '4 hours (including chilling)',
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
        'name': 'Chocolate Lava Cake',
        'difficulty': 'Moderate',
        'total_time': '25 minutes',
        'servings': 4,
        'average_rating': 5,
        'ingredients': 'Dark chocolate, butter, eggs, sugar, flour, vanilla ice cream',
        'method': '1) Melt chocolate and butter. 2) Beat eggs and sugar. 3) Mix in chocolate. 4) Fold in flour. 5) Bake in ramekins at 200°C for 12 minutes. 6) Serve immediately with ice cream.',
        'image_url': 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800'
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
        'name': 'Pulled Pork Sandwich',
        'difficulty': 'Moderate',
        'total_time': '4 hours',
        'servings': 8,
        'average_rating': 5,
        'ingredients': '2kg pork shoulder, BBQ sauce, buns, coleslaw, spices, brown sugar, apple cider vinegar',
        'method': '1) Rub pork with spices. 2) Slow cook at 150°C for 3.5 hours. 3) Shred pork. 4) Mix with BBQ sauce. 5) Toast buns. 6) Fill with pork and coleslaw. 7) Serve hot.',
        'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800'
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
        'name': 'Beef Pho',
        'difficulty': 'Moderate',
        'total_time': '2 hours',
        'servings': 4,
        'average_rating': 5,
        'ingredients': 'Beef bones, rice noodles, beef slices, onions, ginger, star anise, cinnamon, basil, lime, bean sprouts',
        'method': '1) Simmer bones for 2 hours. 2) Strain broth. 3) Cook noodles. 4) Heat broth. 5) Assemble bowls with noodles, beef, and herbs. 6) Pour hot broth over. 7) Serve with lime and sprouts.',
        'image_url': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800'
    },
    {
        'name': 'Chicken Satay',
        'difficulty': 'Moderate',
        'total_time': '1 hour',
        'servings': 4,
        'average_rating': 5,
        'ingredients': '600g chicken, coconut milk, curry paste, peanut sauce, skewers, cucumber, rice',
        'method': '1) Marinate chicken in coconut milk and curry. 2) Thread onto skewers. 3) Grill until cooked. 4) Make peanut sauce. 5) Serve with rice, cucumber, and sauce.',
        'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800'
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
    {
        'name': 'Beef Kebabs',
        'difficulty': 'Easy',
        'total_time': '30 minutes',
        'servings': 4,
        'average_rating': 4,
        'ingredients': '600g beef, bell peppers, onions, mushrooms, olive oil, spices, skewers, rice',
        'method': '1) Marinate beef in spices and oil. 2) Cut vegetables. 3) Thread onto skewers. 4) Grill until done. 5) Serve over rice.',
        'image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=800'
    },
    {
        'name': 'Chicken Pot Pie',
        'difficulty': 'Moderate',
        'total_time': '1 hour 30 minutes',
        'servings': 6,
        'average_rating': 5,
        'ingredients': 'Chicken, pie crust, vegetables, chicken stock, cream, flour, butter, herbs',
        'method': '1) Cook chicken and vegetables. 2) Make creamy sauce. 3) Combine filling. 4) Top with pie crust. 5) Bake at 200°C for 45 minutes. 6) Rest before serving.',
        'image_url': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=800'
    },
]


class Command(BaseCommand):
    """
    Build automation command to seed the database with data.

    This command inserts a small set of known users (``user_fixtures``) and then
    repeatedly generates additional random users until ``USER_COUNT`` total users
    exist in the database. Each generated user receives the same default password.

    Attributes:
        USER_COUNT (int): Target total number of users in the database.
        DEFAULT_PASSWORD (str): Default password assigned to all created users.
        help (str): Short description shown in ``manage.py help``.
        faker (Faker): Locale-specific Faker instance used for random data.
    """

    USER_COUNT = 5
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'


    def __init__(self, *args, **kwargs):
        """Initialize the command with a locale-specific Faker instance."""
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--with-recipes',
            action='store_true',
            help='Also create generic recipes (use seed_recipes for recipes with images)',
        )

    def handle(self, *args, **options):
        """
        Django entrypoint for the command.

        Runs the full seeding workflow and stores ``self.users`` for any
        post-processing or debugging (not required for operation).
        """
        self.create_users()
        # Recipes are now seeded separately with seed_recipes command
        # Use --with-recipes flag to create generic recipes
        if options.get('with_recipes'):
            self.create_recipes_from_data()
        self.create_tracker_data()
        self.create_tags()
        self.create_posts()
        self.create_post_interactions()
        self.users = User.objects.all()
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    def create_users(self):
        """
        Create fixture users and then generate random users up to USER_COUNT.

        The process is idempotent in spirit: attempts that fail (e.g., due to
        uniqueness constraints on username/email) are ignored and generation continues.
        """
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        """Attempt to create each predefined fixture user."""
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        """
        Generate random users until the database contains USER_COUNT users.

        Prints a simple progress indicator to stdout during generation.
        """
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        """
        Generate a single random user and attempt to insert it.

        Uses Faker for first/last names, then derives a simple username/email.
        """
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def try_create_user(self, data):
        """
        Attempt to create a user and ignore any errors.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        """
        Create a user with the default password.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``. 
                May also include ``is_staff`` and ``is_superuser`` for admin users.
        """
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        # Set admin status explicitly before saving
        user.is_staff = data.get('is_staff', False)
        user.is_superuser = data.get('is_superuser', False)
        user.save()

    def create_recipes_from_data(self):
        """
        Create recipes using the static RECIPES_DATA list.

        - Skips recipes whose name already exists (idempotent).
        - Assigns a random existing user as created_by (if any).
        - Relies on the default `image` field value (e.g. images/food1.jpg).
        """
        users = list(User.objects.all())
        created_count = 0
        skipped_count = 0

        self.stdout.write("Starting recipe seeding from RECIPES_DATA...")

        for recipe_data in RECIPES_DATA:
            try:
                if Recipe.objects.filter(name=recipe_data["name"]).exists():
                    skipped_count += 1
                    continue

                created_by = choice(users) if users else None

                Recipe.objects.create(
                    name=recipe_data["name"],
                    difficulty=recipe_data["difficulty"],
                    total_time=recipe_data["total_time"],
                    servings=recipe_data["servings"],
                    average_rating=recipe_data["average_rating"],
                    ingredients=recipe_data["ingredients"],
                    method=recipe_data["method"],
                    image_url=recipe_data["image_url"],
                    created_by=created_by,
                    # `image` field uses its default (e.g. images/food1.jpg)
                )
                created_count += 1

                if created_count % 10 == 0:
                    self.stdout.write(
                        f"Created {created_count} recipes...", ending="\r"
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Failed to create {recipe_data["name"]}: {str(e)}'
                    )
                )
                skipped_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Recipe seeding complete! Created {created_count} recipes. "
                f"Skipped {skipped_count} duplicates or errors."
            )
        )


    def create_tracker_data(self):
        """Create tracker data (profiles, meals, water, fasting) for all users."""
        all_users = User.objects.all()
        total_users = all_users.count()
        
        self.stdout.write(f"Creating tracker data for {total_users} users...")
        
        for idx, user in enumerate(all_users, 1):
            if idx % 10 == 0:
                self.stdout.write(f"  Processing user {idx}/{total_users}", ending='\r')
            
            # Create profile for user
            self.create_profile_for_user(user)
            
            # Generate 30 days of history
            self.generate_user_history(user, days=30)
        
        self.stdout.write(f"Tracker data creation complete.     ")

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
                    # 'current_weight' and 'height' removed in recent migrations
                }
            )
        except:
            pass

    def generate_user_history(self, user, days=30):
        """Generate tracker history for the last N days for a user."""
        #Make the seeder idempotent for fasting data: clear old data first
        FastingSession.objects.filter(user=user).delete()
        
        today = date.today()
        start_date = today - timedelta(days=days - 1)
        
        last_end_datetime = None
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            #Generate meals (3-5 per day)
            meal_count = randint(3, 5)
            for _ in range(meal_count):
                self.create_random_meal(user, current_date)
            
            #Generate daily log
            self.create_daily_log(user, current_date)
            
            #Generate fasting sessions sequentially
            #70% chance to fast on any given day
            if random() < 0.7:
                last_end_datetime = self.create_sequential_fasting_session(user, current_date, last_end_datetime)

    def create_random_meal(self, user, meal_date):
        """Create a random meal for a user on a given date."""
        meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        meal_type = choice(meal_types)
        
        # Realistic calorie ranges based on meal type
        calorie_ranges = {
            'Breakfast': (250, 600),
            'Lunch': (400, 800),
            'Dinner': (500, 1000),
            'Snack': (100, 300),
        }
        
        calories = randint(*calorie_ranges[meal_type])
        
        # Calculate macros with realistic proportions
        # Generate percentages that sum to 100%
        protein_percent = random() * 0.15 + 0.15  # 15-30%
        carbs_percent = random() * 0.30 + 0.30    # 30-60%
        remaining = 1.0 - protein_percent - carbs_percent
        # Ensure fat is at least 10% and adjust if needed
        fat_percent = max(0.10, remaining)
        # Normalize to ensure they sum to 100%
        total = protein_percent + carbs_percent + fat_percent
        protein_percent = protein_percent / total
        carbs_percent = carbs_percent / total
        fat_percent = fat_percent / total
        
        protein_g = round((calories * protein_percent) / 4, 1)
        carbs_g = round((calories * carbs_percent) / 4, 1)
        fat_g = round((calories * fat_percent) / 9, 1)
        
        meal_names = {
            'Breakfast': ['Oatmeal', 'Scrambled Eggs', 'Toast with Butter', 'Cereal', 'Yogurt Bowl'],
            'Lunch': ['Grilled Chicken Salad', 'Pasta', 'Sandwich', 'Soup', 'Rice Bowl'],
            'Dinner': ['Steak and Potatoes', 'Fish and Vegetables', 'Pasta Dish', 'Stir Fry', 'Pizza'],
            'Snack': ['Apple', 'Almonds', 'Protein Bar', 'Greek Yogurt', 'Banana'],
        }
        
        name = choice(meal_names[meal_type])
        
        try:
            Meal.objects.create(
                user=user,
                name=name,
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
        amount_ml = randint(1000, 3000)
        
        #Randomize calorie goal - higher on weekends (Saturday=5, Sunday=6) but within realistic range
        weekday = intake_date.weekday()
        is_weekend = weekday >= 5
        
        if is_weekend:
            #Higher goals on weekends (within 1800-3000 range)
            calorie_goal = randint(2500, 3000)
        else:
            #Normal goals on weekdays (within 1800-3000 range)
            calorie_goal = randint(1800, 2500)
        
        #Calculate macros based on calorie goal (40% carbs, 30% protein, 30% fat)
        #Protein: 30% of calories / 4 cal per gram
        protein_goal = round((calorie_goal * 0.30) / 4)
        #Carbs: 40% of calories / 4 cal per gram
        carbs_goal = round((calorie_goal * 0.40) / 4)
        #Fat: 30% of calories / 9 cal per gram
        fat_goal = round((calorie_goal * 0.30) / 9)
        #Water goal
        water_goal = randint(2000, 3000)
        
        try:
            #Use update_or_create to ensure goals are always set, even if record exists
            DailyLog.objects.update_or_create(
                user=user,
                date=intake_date,
                defaults={
                    'amount_ml': amount_ml,
                    'calorie_goal': calorie_goal,
                    'protein_goal': protein_goal,
                    'carbs_goal': carbs_goal,
                    'fat_goal': fat_goal,
                    'water_goal': water_goal,
                }
            )
        except:
            pass

    def create_sequential_fasting_session(self, user, session_date, last_end_datetime):
        """
        Create a fasting session for a user starting on a given date, 
        ensuring it doesn't overlap with the previous one.
        Returns the end_datetime of the created session (or None if failed).
        """
        target_durations = [14, 16, 18]
        target_duration = choice(target_durations)
        
        #Proposed start: Evening time (18:00 - 22:00)
        hour = randint(18, 22)
        minute = randint(0, 59)
        base_start_time = datetime.combine(session_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
        start_datetime = timezone.make_aware(base_start_time)
        
        #Adjust start time if it overlaps with last_end_datetime
        #Ensure we don't start before the previous fast ended
        if last_end_datetime and start_datetime < last_end_datetime:
            # If the calculated evening time is BEFORE the last fast ended (e.g. last fast ended tomorrow morning),
            # we simply skip fasting today.
            return last_end_datetime
            
        #Determine duration
        actual_duration_hours = target_duration + (random() * 2 - 1) 
        duration = timedelta(hours=actual_duration_hours)
        
        end_datetime = start_datetime + duration
        
        #Check if this session is the "current/active" one
        now = timezone.now()
        is_active = False
        end_datetime_record = end_datetime
        
        if end_datetime > now:
            #Only make it active if it started in the past
            if start_datetime <= now:
                is_active = True
                end_datetime_record = None
            else:
                #Started in future? Don't create it yet
                return last_end_datetime 
        else:
            is_active = False

        try:
            FastingSession.objects.create(
                user=user,
                start_date_time=start_datetime,
                end_date_time=end_datetime_record,
                target_duration=target_duration,
                is_active=is_active,
            )
            #Return the calculated end time (even if active, conceptually it occupies time)
            return end_datetime 
        except:
            return last_end_datetime
        
    def create_tags(self):
        """Create standard tags for posts."""
        tags = [
            "Breakfast", "Lunch", "Dinner", "Dessert", 
            "Snack", "Vegan", "Vegetarian", "Gluten-Free", 
            "Keto", "Paleo", "High Protein", "Low Carb", 
            "Spicy", "Quick & Easy", "Meal Prep", "Healthy"
        ]
        
        for tag_name in tags:
            # get_or_create prevents duplicates if you run seed multiple times
            Tag.objects.get_or_create(name=tag_name)
            
        self.stdout.write("Tags seeding complete.")

    def create_posts(self):
        """Generate social posts using real food titles, captions, and images."""
        users = list(User.objects.all())
        tags = list(Tag.objects.all())
        
        # Real Food Data
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
            "Finally perfected my dough recipe! The crust was crunchy on the outside and soft inside. Fresh basil is a must.",
            "Perfect comfort food for this chilly weather. Highly recommend pairing it with a sourdough grilled cheese.",
            "A little spicy, a little tangy, and totally delicious. Don't skimp on the lime juice!",
            "Sometimes you just need a classic. Juicy patty, melted cheddar, and all the fixings on a brioche bun.",
            "Weekend breakfast done right. These were so fluffy! Served with real maple syrup and fresh strawberries.",
            "Fresh, healthy, and packed with flavor. The homemade lemon-oregano dressing ties it all together.",
            "The perfect snack for sharing. So much better than store-bought! Super creamy and garlicky.",
            "Warm, gooey, and loaded with chocolate pools. A sprinkle of sea salt on top makes them addictive.",
            "A labor of love that requires constant stirring, but the creamy texture is so worth it.",
            "Fall-off-the-bone tender after cooking low and slow for 6 hours. The homemade BBQ sauce is a game changer.",
            "Tastes just like takeout! It's all about balancing the sweet, sour, and savory flavors.",
            "Rich, aromatic, and full of spices. Best enjoyed with some warm garlic naan to scoop up the sauce.",
            "A Roman classic made the right way—no cream, just eggs, Pecorino Romano, guanciale, and lots of black pepper.",
            "A super fast and healthy weeknight dinner. A great way to use up whatever veggies are in the fridge.",
            "My go-to breakfast. Simple, nutritious, and delicious. The runny yolk is the best part.",
            "Packed with antioxidants and energy. Topped with homemade granola, banana, and coconut flakes.",
            "Crispy golden coating on the outside, tender on the inside. A squeeze of fresh lemon is essential.",
            "Indulgent and cheesy with big chunks of lobster meat. A real treat for a special occasion.",
            "Rich beef broth, caramelized onions, and a thick layer of melted Gruyère cheese on toast. So satisfying.",
            "Cooked medium-rare with a crispy sear. The garlic aioli for dipping the fries is incredible."
        ]

        cuisine_choices = [
            'Italian', 'Mexican', 'Chinese', 'Indian', 'Japanese', 
            'Thai', 'French', 'American', 'Greek', 'Spanish', 
            'Mediterranean', 'Korean', 'Other'
        ]
        
        # Locate the image directory relative to this script file
        image_dir = os.path.join(os.path.dirname(__file__), '..', 'seed_images')
        image_files = []
        try:
            # Create a list of all files in the directory
            image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f"Warning: Image directory '{image_dir}' not found. Posts will be created without images."))

        if not users:
            self.stdout.write("No users found. Skipping post generation.")
            return

        num_posts = len(FOOD_TITLES)
        self.stdout.write(f"Seeding {num_posts} social posts with real data...")
        
        for i in range(num_posts):
            author = choice(users)
            
            # Use titles sequentially from the list
            title = FOOD_TITLES[i]
            # Cycle through captions if we have more titles than captions
            caption = FOOD_CAPTIONS[i % len(FOOD_CAPTIONS)]
            
            # Prepare post data
            post_data = {
                'author': author,
                'title': title,
                'caption': caption,
                'cuisine': choice(cuisine_choices),
                'difficulty': choice(['Easy', 'Moderate', 'Hard']),
                'prep_time': f"{randint(15, 90)} min",
                'servings': randint(2, 6),
            }

            # Pick a random image file if any exist
            image_file_handler = None
            if image_files:
                random_image_name = choice(image_files)
                image_path = os.path.join(image_dir, random_image_name)
                # Open the file in binary mode so Django can read it
                f = open(image_path, 'rb')
                image_file_handler = File(f, name=random_image_name)

            # Create the post, passing the image file handler if it exists
            if image_file_handler:
                post = Post.objects.create(image=image_file_handler, **post_data)
                image_file_handler.close()
            else:
                post = Post.objects.create(**post_data)
            
            # Add random tags
            if tags:
                random_tags = sample(tags, k=randint(1, min(3, len(tags))))
                post.tags.set(random_tags)
                
        self.stdout.write("Social posts seeded successfully.")

    def create_post_interactions(self):
        """Generate Likes, Comments, and Ratings for posts."""
        users = list(User.objects.all())
        posts = Post.objects.all()
        
        comments_list = [
            "This looks amazing!", "Can't wait to try this.", "Delicious!", 
            "Great recipe.", "My family loved it.", "Yum!", "So tasty.", 
            "Thanks for sharing!", "Added to my list.", "Wow!"
        ]

        if not users or not posts:
            return

        self.stdout.write("Seeding likes, comments, and ratings...")

        for post in posts:
            # 1. Generate Likes
            # Randomly select 0 to 20 unique users to like this post
            num_likes = randint(0, 20)
            likers = sample(users, k=min(num_likes, len(users)))
            for user in likers:
                Like.objects.get_or_create(user=user, post=post)

            # 2. Generate Comments
            # Randomly select 0 to 5 users to comment
            num_comments = randint(0, 5)
            commenters = sample(users, k=min(num_comments, len(users)))
            for user in commenters:
                Comment.objects.create(user=user, post=post, text=choice(comments_list))

            # 3. Generate Ratings
            # Randomly select 0 to 15 unique users to rate
            num_ratings = randint(0, 15)
            raters = sample(users, k=min(num_ratings, len(users)))
            
            total_score = 0
            for user in raters:
                score = randint(3, 5)
                try:
                    Rating.objects.create(user=user, post=post, score=score)
                    total_score += score
                except:
                    # Ignore duplicates
                    pass

            
            # Update Post aggregates to match the created ratings
            if num_ratings > 0:
                post.rating_count = num_ratings
                post.rating_total_score = total_score
                # Note: average_rating is a @property, so we don't set it directly.
                # It will calculate automatically from total_score / rating_count
                post.save()

        self.stdout.write("Interactions seeded.")

def create_username(first_name, last_name):
    """
    Construct a simple username from first and last names.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: A username in the form ``@{firstname}{lastname}`` (lowercased).
    """
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    """
    Construct a simple example email address.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: An email in the form ``{firstname}.{lastname}@example.org``.
    """
    return first_name + '.' + last_name + '@example.org'