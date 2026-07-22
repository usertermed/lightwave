# Lightwave

Lightwave is a lightweight social feed app built with Django. It supports short posts, replies, likes/dislikes, follow relationships, profile display names, an About Me section, verified badges, and clickable @mentions.

## Features

- Home dashboard with `Following` and `Recommended` toggles
- Short text posts
- Like/dislike and reply support
- User profiles with customizable display name and About Me bio
- Profile verification badge toggleable in the Django admin
- @mentions that link to existing user profiles
- Simple profile browser and feed filtering

## Local setup

### Prerequisites

- Python 3.14
- `pip`
- Built-in `venv`

### Setup steps

1. Clone the project and open it in a terminal
   ```bash
   git clone http://github.com/usertermed/lightwave.git
   cd lightwave
   ```

2. Create and activate a virtual environment if you do not already have one:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser to access Django admin:
   ```bash
   python manage.py createsuperuser
   ( Follow the command's instructions )
   ```

6. Run the development server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

7. Open the app in your browser:
   - App: `http://127.0.0.1:8000/`
   - Admin: `http://127.0.0.1:8000/admin/`

## Developer notes

- The Django project is in `social/`
- The main application is `dwitter/`
- Templates are loaded from `social/templates/` and `dwitter/templates/`
- SQLite database file is `db.sqlite3`
- Custom template tags are located in `dwitter/templatetags/`

## Admin configuration

- User profiles are exposed via Django admin using `ProfileInline` on the `User` admin page
- The `is_verified` field can be toggled in admin to display a verified badge on the public profile and posts

## Useful commands

- Run tests:
  ```bash
  python manage.py test
  ```
- Create migrations:
  ```bash
  python manage.py makemigrations
  ```
- See available management commands:
  ```bash
  python manage.py help
  ```

## Notes

- This app is intended for local development and testing only. `DEBUG` is set to `True` in `social/settings.py`.
- If you add new models or fields, remember to run `python manage.py makemigrations` and `python manage.py migrate`.
