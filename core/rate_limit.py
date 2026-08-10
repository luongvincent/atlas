"""Central slowapi Limiter instance.

Single limiter shared by the whole app (wired in main.py via
SlowAPIMiddleware + app.state.limiter), rather than separate per-endpoint
instances, since slowapi needs exactly one canonical limiter registered on
the app for header/Retry-After injection to work.

Key strategy - "per-IP and per-user" (per the brief) is implemented as one
identity per request, not two independently-enforced dimensions: an
authenticated caller is limited by their own account regardless of which
IP they're calling from (proxies, mobile networks, shared corporate NAT
would otherwise conflate unrelated users or unfairly throttle one), while
an anonymous caller - who has no other identity - is limited by IP.
"""

from __future__ import annotations

import hashlib

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def rate_limit_key(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1].strip()
        if token:
            # Hashed so the rate limiter's storage (in-memory or otherwise)
            # never holds a live bearer token.
            digest = hashlib.sha256(token.encode()).hexdigest()[:24]
            return f"user:{digest}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=["100/minute"],
    headers_enabled=True,
)
