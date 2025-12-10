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

    USER_COUNT = 100
    RECIPE_COUNT = 50 
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
            self.create_recipes()
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

    def create_recipes(self):
        """
        Create random recipes until the number of recipes = RECIPE_COUNT
        """
        recipe_count = Recipe.objects.count()
        while recipe_count < self.RECIPE_COUNT:
            self.generate_recipe()
            recipe_count = Recipe.objects.count()
        print("Recipe seeding complete")

    def generate_recipe(self):
        """Generate random recipes"""
        recipe_number = Recipe.objects.count() + 1
        name = f"Recipe_{recipe_number}"
        average_rating = randint(1,5)
        difficulty = self.faker.random_element(['Easy', 'Moderate', 'Hard'])
        total_time = f"{randint(1,5)} hours"
        servings = randint(2, 8)
        ingredients = self.generate_ingredients()
        method = self.generate_method()
        users = User.objects.all()
        random_user = choice(users)

        self.try_create_recipe({
            'name': name,
            'average_rating': average_rating,
            'difficulty': difficulty,
            'total_time': total_time,
            'servings': servings,
            'ingredients': ingredients,
            'method': method,
            'created_by': random_user,
        })

    def try_create_recipe(self, data):
        """Attempt to make a recipe & ignore errors"""
        try:
            self.create_recipe(data)
        except:
            pass

    def create_recipe(self, data):
        """Create recipe in database"""
        Recipe.objects.create(
            name = data['name'],
            average_rating = data['average_rating'],
            difficulty = data['difficulty'],
            total_time = data['total_time'],
            servings = data['servings'],
            ingredients = data['ingredients'],
            method = data['method'],
            created_by = data['created_by'],
        )

    def generate_ingredients(self):
        """Generate placeholder ingredients: e.g. Ingredient 1, Ingredient 2 ...
        Also generate optional spices in the form: Spice_1, Spice_2 ... --> could be 0 """
        ingredient_count = randint(3, 12)
        ingredients = [f"Ingredient_{i}" for i in range(1, ingredient_count + 1)]
        
        spice_count = randint(0, 5)
        spices = [f"Spice_{i}" for i in range(1, spice_count + 1)]

        lines = []
        lines.append("Ingredients: " + ", ".join(ingredients))

        if spices:
            lines.append("Spices: " + ", ".join(spices))

        return ', '.join(lines)

    def generate_method(self):
        """Generate random steps"""
        steps = randint(5, 10)
        return "\n".join([f"{i + 1}) Step_{i + 1}" for i in range(steps)])

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
                # Skew ratings towards positive (3, 4, or 5)
                score = randint(3, 5)
                Rating.objects.create(user=user, post=post, score=score)
                total_score += score
            
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