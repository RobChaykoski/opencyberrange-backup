import pytest

from app.services.lab_naming import parse_lab_slug


@pytest.mark.parametrize(
    "dirname,expected",
    [
        ("windows-1-1-basic-port-scan", ("windows", 1, 1)),
        (
            "high-school-10-1-rangebox-network-basics",
            ("high-school", 10, 1),
        ),
        (
            "software-security-2-1-diagnostics-command-injection",
            ("software-security", 2, 1),
        ),
        (
            "forensics-1-1-windows-memory-volatility",
            ("forensics", 1, 1),
        ),
        (
            "linux-midterm-3-blind-penetration-test",
            ("linux", None, 3),
        ),
        ("windows-D1-2-drill", ("windows", 901, 2)),
        ("not-a-lab", (None, None, None)),
    ],
)
def test_parse_lab_slug(dirname, expected):
    assert parse_lab_slug(dirname) == expected
