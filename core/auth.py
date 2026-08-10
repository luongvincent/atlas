"""Auth dependencies backed by Supabase Auth.

We never verify JWTs ourselves - a bearer token, if present, is handed to
Supabase's own auth.get_user(), which validates it and returns the user.
Every downstream Supabase call for that request should reuse
core.supabase_client.get_request_client(access_token=...) with this same
token, so RLS policies keyed on auth.uid() apply - never the service role
key, per the project's security rules.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from core.supabase_client import get_request_client


@dataclass
class AuthContext:
    access_token: str
    user_id: str
    email: str | None


async def get_current_user_optional(
    authorization: str | None = Header(default=None),
) -> AuthContext | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return None

    client = get_request_client(access_token=token)
    try:
        response = client.auth.get_user(token)
    except Exception:
        # Expired/invalid/malformed token: treat as anonymous rather than
        # erroring, so callers can decide whether auth is required.
        return None

    user = getattr(response, "user", None)
    if user is None:
        return None
    return AuthContext(access_token=token, user_id=user.id, email=user.email)


async def get_current_user_required(
    user: AuthContext | None = Depends(get_current_user_optional),
) -> AuthContext:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
