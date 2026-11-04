"""Privacy helpers for user-facing responses.

User-facing account exports and session views should not reveal private,
loopback, link-local, or otherwise non-global addresses. Administrators still
see the raw value in admin-only audit views.
"""
import ipaddress


REDACTED_IP = "redacted"


def redact_ip(value):
    """Return a global IP unchanged, or a redaction marker otherwise.

    Missing values stay missing. Malformed values are redacted rather than
    echoed, because the source is often a proxy header or an older row.
    """
    if value is None or value == "":
        return value
    try:
        address = ipaddress.ip_address(str(value).strip())
    except ValueError:
        return REDACTED_IP
    if not address.is_global:
        return REDACTED_IP
    return str(address)
