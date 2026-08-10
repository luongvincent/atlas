"""Supabase client factories.

Two distinct factories, deliberately kept apart so it's obvious at every
call site which privilege level is in play:

- get_request_client(): anon key, optionally bound to a caller's own JWT.
  Every code path reachable from a client request must use this. RLS
  applies, so a caller can only ever touch its own rows.
- get_admin_client(): service role key, bypasses RLS entirely. Reserved for
  offline/admin scripts (migrations, seeding) that never run inside a
  request handler.
"""

from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from config import get_settings


@lru_cache
def _anon_base_client() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_request_client(access_token: str | None = None) -> Client:
    """Client for use inside API request handlers.

    Always uses the anon key. If ``access_token`` (the caller's Supabase
    JWT) is provided, PostgREST requests are made as that authenticated
    user so RLS policies keyed on auth.uid() apply; without a token, the
    client acts as the anonymous role.
    """
    settings = get_settings()
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    if access_token:
        client.postgrest.auth(access_token)
    return client


def get_admin_client() -> Client:
    """Service-role client. NEVER call this from an API request handler.

    Reserved for offline/admin scripts (see /migrations, /scripts) run
    manually server-side. Bypasses RLS.
    """
    settings = get_settings()
    if not settings.supabase_service_role_key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not set")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
