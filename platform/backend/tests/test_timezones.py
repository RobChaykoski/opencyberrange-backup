"""Timezone resolution falls back safely instead of failing a report."""
from app.timezones import UTC, resolve_timezone


def test_resolve_known_zone():
    assert resolve_timezone("America/Chicago").key == "America/Chicago"


def test_null_zone_falls_back_to_utc():
    assert resolve_timezone(None) is UTC
    assert resolve_timezone("") is UTC


def test_unknown_zone_falls_back_to_utc():
    assert resolve_timezone("Not/A_Real_Zone") is UTC
