# Food Order Management App

## Stack
- Backend: Django + FastAPI (Django for admin/ORM, FastAPI for API endpoints)
- Database: SQLite
- Frontend: Tailwind CSS with Django templates
- Python: 3.11+

## Architecture
- Django manages models, migrations, admin, auth
- FastAPI handles REST API endpoints (mounted into Django via ASGI)
- Tailwind for all styling (no Bootstrap, no inline styles)
- SQLite for local dev

## Conventions
- All models in `core/models.py`
- API routes in `api/routers/`
- Templates in `templates/`
- Static files in `static/`
- Virtual env: `venv/` (never modify)
- Never hardcode secrets

## Setup

### Initial Setup
```bash
# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser
```

## Running the App

### Development Server (with ASGI for FastAPI)
```bash
pip install uvicorn
uvicorn food_order_project.asgi:application --reload
```
- Django admin: http://localhost:8000/admin
- API endpoints: http://localhost:8000/api/
- Frontend: http://localhost:8000/

**Note:** Must use ASGI (uvicorn) not WSGI (runserver) because the app uses FastAPI for API endpoints.

### Database

#### Run Migrations
```bash
python manage.py migrate
```

#### Create Fresh Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Populate Dummy Data
```bash
python manage.py populate_dummy_data
```
Creates sample customers, restaurants, menu items, and orders for testing.

## Admin Access

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Access admin panel at `http://localhost:8000/admin`

3. Log in with superuser credentials

## Agent Teams
- Use a backend agent for Django models, migrations, business logic
- Use an API agent for FastAPI routes and schemas
- Use a frontend agent for templates and Tailwind
- Orchestrate through main thread
