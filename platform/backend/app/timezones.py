"""Timezone helpers for user-facing timestamps and reports.

Users may have a null timezone (legacy accounts) or an IANA name that this
host does not have tzdata for. Both cases fall back to UTC rather than raising
during a report download.
"""
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = ZoneInfo("UTC")


def resolve_timezone(name: str | None) -> ZoneInfo:
    """Return a usable ZoneInfo for an IANA name, or UTC."""
    if not name:
        return UTC
    try:
        return ZoneInfo(str(name))
    except (ZoneInfoNotFoundError, ValueError):
        return UTC
