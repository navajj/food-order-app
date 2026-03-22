from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from fastapi import HTTPException, Request

from core.models import Customer


async def get_current_user(request: Request) -> User:
    scope = request.scope
    django_request = scope.get("django_request")
    user = None

    if django_request:
        user = await sync_to_async(lambda: django_request.user if django_request.user.is_authenticated else None)()

    if user is None:
        # Fallback: try session from ASGI scope
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.auth import get_user

        cookies = request.cookies
        session_key = cookies.get("sessionid")
        if not session_key:
            raise HTTPException(status_code=401, detail="Not authenticated")

        session = SessionStore(session_key=session_key)

        user_id = await sync_to_async(lambda: session.get("_auth_user_id"))()
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        user = await sync_to_async(User.objects.get)(pk=user_id)

    return user


async def get_current_customer(request: Request) -> Customer:
    user = await get_current_user(request)
    try:
        customer = await sync_to_async(Customer.objects.get)(user=user)
    except Customer.DoesNotExist:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    return customer
