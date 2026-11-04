"""Shared rate-limiter construction.

Each router keeps its own ``Limiter`` so its decorators are self-contained, but
they must all point at the same counter store. With the default ``memory://``
store every uvicorn worker keeps a private counter and the effective limit is
multiplied by the worker count. Setting ``RATELIMIT_STORAGE_URI`` (for example
``redis://redis:6379/0``) makes the limits global.
"""
import os

from slowapi import Limiter
from slowapi.util import get_remote_address


def rate_limit_storage_uri() -> str:
    """Return the configured counter backend, defaulting to per-process memory."""
    return os.environ.get("RATELIMIT_STORAGE_URI", "memory://") or "memory://"


def create_limiter(**kwargs) -> Limiter:
    """Build a Limiter that honours RATELIMIT_STORAGE_URI."""
    kwargs.setdefault("key_func", get_remote_address)
    kwargs.setdefault("storage_uri", rate_limit_storage_uri())
    return Limiter(**kwargs)
