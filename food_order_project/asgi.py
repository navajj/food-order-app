import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_order_project.settings')

from django.core.asgi import get_asgi_application
django_app = get_asgi_application()

from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

from api.main import app as fastapi_app

# Wrap Django app with static files handler in DEBUG mode
if settings.DEBUG:
    django_static_app = ASGIStaticFilesHandler(django_app)
else:
    django_static_app = django_app


async def application(scope, receive, send):
    if scope["type"] == "http" and scope["path"].startswith("/api/"):
        await fastapi_app(scope, receive, send)
    else:
        await django_static_app(scope, receive, send)
