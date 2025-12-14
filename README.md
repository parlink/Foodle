# Team Foodle (Pink-6) Small Group project

## Team members
The members of the team are:
- Daniel Darius Mani
- Hikmet Ozan Kaya
- Kasthury Aruleesan
- Mohammad Raza Khan
- Parlin Kaur


## Project structure
The project is called `Foodle`.

## Project overview
The Foodle system aims to provide users with a single, integrated platform to manage their food related activities, including discovering new recipes, creating and organising personal recipes, tracking meals/nutrition/water intake/ fasting, and engaging with a social food community. Its objective is to support healthier eating habits and meal planning by combining personal tracking tools with recipe management and social features in a user-friendly web application.

## Deployed version of the application
The deployed version of the application can be found at https://ozankaya4.pythonanywhere.com/.

### API-dependent features (deployed vs local)
The **Forgot Password** and **AI Recipes** features are available and useful in the deployed version because the required API keys are configured via environment variables on the server. These keys should **not** be submitted through the application submission on KEATS, and the features will not work on a local machine unless the grader provides their own API keys. To enable them locally, create a `.env` file from `.env.example` and set: `OPENAI_API_KEY`, `SENDGRID_API_KEY`, and `DEFAULT_FROM_EMAIL` (a verified sender email in SendGrid).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  The project source code has been developed using Python 3.12, so you are recommended to use the same version.  From the root of the project:

```
$ python3 -m venv venv
$ source .venv/bin/activate
```

If your system does not have `python3` installed and you are unable to install Python 3.12 as a version you can explicitly refer to from the CLI, then replace `python3` by `python3` or `python`, provide this employs a relatively recent version of Python.

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Generative AI Usage

This project utilized generative AI tools to assist in development:

- **Template Creation and Styling**: AI was used to some extent in creating templates and styling the pages throughout the application.

- **Debugging**: AI assistance was extensively used for debugging code issues, identifying errors, and resolving technical problems during development.

- **Test Case Development**: AI was utilized for finding missing test cases and ensuring comprehensive test coverage for the application's functionality.

## Sources
The packages used by this application are specified in `requirements.txt`
