"""
Management command to seed the database with lots of recipes and food images.

This command creates a comprehensive set of realistic recipes with ingredients,
methods, and food image URLs from Unsplash.
"""

from random import randint, choice
from django.core.management.base import BaseCommand
from recipes.models import Recipe


# Comprehensive list of realistic recipes with food image URLs
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
    Management command to seed the database with lots of recipes and food images.
    """
    help = 'Seeds the database with comprehensive recipes and food images'

    def handle(self, *args, **options):
        """Create all recipes from the RECIPES_DATA list."""
        created_count = 0
        skipped_count = 0
        
        self.stdout.write('Starting recipe seeding...')
        
        for recipe_data in RECIPES_DATA:
            try:
                # Check if recipe already exists
                if Recipe.objects.filter(name=recipe_data['name']).exists():
                    skipped_count += 1
                    continue
                
                Recipe.objects.create(**recipe_data)
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f'Created {created_count} recipes...', ending='\r')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create {recipe_data["name"]}: {str(e)}')
                )
                skipped_count += 1
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Recipe seeding complete! Created {created_count} recipes. '
                f'Skipped {skipped_count} duplicates or errors.'
            )
        )

