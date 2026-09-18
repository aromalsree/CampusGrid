# CampusGrid

CampusGrid is a Django-based campus marketplace for students. It lets users browse, sell, rent, and discover campus resources such as laptops, textbooks, notes, lab equipment, and room essentials.

The project is currently a server-rendered Django application with a responsive HTML/CSS interface and a small amount of vanilla JavaScript for navigation, marketplace interactions, and wishlist actions.

## Features

- Student registration and login with a custom `App_users` model.
- Public home, About, Contact, marketplace, categories, comparison, and need-board pages.
- Listings for sales, rentals, services, and digital assets.
- Category, type, condition, and text filtering in the marketplace.
- Authenticated listing creation.
- Wishlist save/remove behavior with per-user database records.
- Profile page with saved product previews.
- Admin dashboard and user-management views.
- Responsive navigation, product cards, forms, alerts, and dashboard templates.
- Local static product-image fallbacks and optional uploaded listing media.

## Technology

| Area | Technology |
| --- | --- |
| Backend | Django 6.1.1 |
| Language | Python |
| Database | SQLite for development |
| Image handling | Pillow 12.3.0 |
| Frontend | Django templates, CSS, SVG, vanilla JavaScript |
| Authentication | Django auth with `userops.App_users` |

## Project Structure

```text
CampusGrid/
├── README.md
├── plan/                 # Planning and contribution notes
└── server/
    ├── manage.py
    ├── requirements.txt
    ├── sample.json        # Demo categories, users, and listings
    ├── config/            # Django settings and root URL configuration
    ├── main/              # Home, About, Contact, and admin views
    ├── market/            # Categories, listings, need board, wishlist models/views
    ├── userops/           # Registration, login, user model, dashboard views
    ├── templates/         # Base layouts, components, pages, and dashboards
    ├── static/            # CSS, JavaScript, icons, and catalog images
    └── media/             # Runtime-uploaded listing images; ignored by Git
```

## Requirements

- Python 3.10 or newer
- Git
- A virtual environment is recommended

## Local Setup

From the repository root:

```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\venv\Scripts\Activate.ps1
```

Apply migrations and load the included demo data:

```bash
python manage.py migrate
python manage.py loaddata sample.json
```

Start the development server:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Database Reset

The development database is SQLite at `server/db.sqlite3`. To recreate it from the current migration files and fixture:

```bash
cd server
rm -f db.sqlite3
python manage.py migrate
python manage.py loaddata sample.json
```

Use the following only when intentionally rebuilding app migrations as well:

```bash
find market/migrations userops/migrations -type f \
  ! -name '__init__.py' -delete
rm -f db.sqlite3
python manage.py makemigrations userops market
python manage.py migrate
python manage.py loaddata sample.json
```

Do not use the migration-reset command against production data.

## Demo Data

`sample.json` currently contains:

- 6 categories
- 6 student users
- 6 marketplace listings

The fixture password values are placeholder hashes and should not be treated as known login credentials. Create a local administrator with:

```bash
python manage.py createsuperuser
```

The Django admin is available at `/admin/`.

## Main Routes

### Public pages

| URL | Purpose |
| --- | --- |
| `/` | Home page |
| `/about/` | About CampusGrid and FAQ |
| `/contact/` | Contact form |
| `/products/` | Marketplace catalogue and filters |
| `/categories/` | Category directory |
| `/compare/` | Product comparison page |
| `/requests/` | Need board |
| `/requests/board/` | Need board listing |

### Authentication and account pages

| URL | Purpose |
| --- | --- |
| `/register/` | Create an account |
| `/login/` | Sign in |
| `/logout/` | Sign out |
| `/dashboard/admin` | Admin dashboard |
| `/dashboard/user` | User dashboard |
| `/admin/` | Django admin site |

### Marketplace actions

| URL | Purpose |
| --- | --- |
| `/create/` | Create a listing; authentication required |
| `/seller/products/add/` | Alternate create-listing route |
| `/wishlist/<listing_id>/` | Toggle a listing in the current user's wishlist |
| `/requests/create/` | Create a need request; authentication required |
| `/requests/<pk>/` | View a need request |
| `/requests/<pk>/offer/` | Submit an offer on a need request |

## Static Files and Images

Development settings serve files from `server/static/` and uploaded media from `server/media/`.

Catalog images are tracked under:

```text
server/static/images/marketplace/products/
```

Uploaded `ListingImage` files are stored under:

```text
server/media/listings/images/
```

The media directory is ignored by Git. For production, configure a persistent media store and serve static/media files through the deployment platform or a web server.

## Testing and Checks

Run Django's system checks:

```bash
python manage.py check
```

Run the test suite:

```bash
python manage.py test
```

Run app-specific tests:

```bash
python manage.py test userops
python manage.py test market
```

Before relying on the marketplace tests, ensure the test database has the categories expected by the test fixtures, including the `laptops` and `notes` slugs.

## Configuration Notes

Development settings currently use:

- `DEBUG = True`
- `ALLOWED_HOSTS = ['*']`
- SQLite database
- Console email backend
- `AUTH_USER_MODEL = 'userops.App_users'`
- `LOGIN_URL = '/login/'`

These settings are suitable for local development only. Use environment-based secrets, restricted hosts, secure cookies, a production database, and a real email/media service before deployment.

## Contribution Workflow

1. Create a branch for your change.
2. Activate the virtual environment and install requirements.
3. Run `python manage.py check` before opening a pull request.
4. Run the focused tests for the area you changed.
5. Keep templates, CSS, JavaScript, migrations, and backend changes scoped to the feature.

## Current Limitations

- Password-reset URL patterns are currently commented out in `userops/urls.py`.
- The development project uses SQLite and local media storage.
- Some dashboard routes are still being consolidated between `main` and `userops`.
- Test fixtures and seeded categories should be kept aligned when adding new marketplace tests.
