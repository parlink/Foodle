"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""



from faker import Faker
from random import randint, random
from django.core.management.base import BaseCommand, CommandError
from recipes.models import User, Recipe


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'is_staff': True},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
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

    def handle(self, *args, **options):
        """
        Django entrypoint for the command.

        Runs the full seeding workflow and stores ``self.users`` for any
        post-processing or debugging (not required for operation).
        """
        self.create_users()
        self.create_recipes()
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
        """
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

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

        self.try_create_recipe({
            'name': name,
            'average_rating': average_rating,
            'difficulty': difficulty,
            'total_time': total_time,
            'servings': servings,
            'ingredients': ingredients,
            'method': method,
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
