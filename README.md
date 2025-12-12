# Team Foodle Small Group project

## Team members
The members of the team are:
- Daniel Darius Mani
- Hikmet Ozan Kaya
- Kasthury Aruleesan
- Mohammad Raza Khan
- Parlin Kaur


## Project structure
The project is called `Foodle`.

## Deployed version of the application
The deployed version of the application can be found at [*enter url here*](*enter_url_here*).

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

### Environment Variables Setup

Create a `.env` file in the project root directory (copy from `.env.example`):

On Windows:
copy .env.example .env


On Linux/Mac:
cp .env.example .env

**Important:** After setting environment variables, make sure to reload your web app from the Web tab for the changes to take effect.

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

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

When deployed:
Edit the `.env` file and fill in the required values:

- OPENAI_API_KEY: Required for AI recipe generation. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
  - For team members: Ask your team lead or check the shared password manager/documentation for the shared API key
  - For deployment: Set this as an environment variable in your hosting platform.

Note: The `.env` file is in `.gitignore` and should never be committed to version control. The `.env.example` file shows what variables are needed without exposing sensitive values.

PythonAnywhere Deployment

For PythonAnywhere, you can set environment variables using one of these methods:

Create a `.env` file on PythonAnywhere
1. Go to the Files tab in your PythonAnywhere dashboard
2. Navigate to your project directory
3. Create a new file named `.env`
4. Add your environment variables:
   
   OPENAI_API_KEY=sk-your-api-key-here

5. Save the file. The application will automatically load these variables when it starts.

## Sources
The packages used by this application are specified in `requirements.txt`
