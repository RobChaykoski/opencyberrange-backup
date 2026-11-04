"""lab.yaml hostnames become Docker network aliases."""
from app.services.docker_manager import _lab_hostnames_by_offset


def test_groups_hostnames_by_ip_offset():
    entries = [
        {"ip_offset": "96", "hostname": "voice.lab"},
        {"ip_offset": "96", "hostname": "voice.internal"},
        {"ip_offset": 82, "hostname": "connect.lab"},
    ]
    assert _lab_hostnames_by_offset(entries) == {
        "96": ["voice.lab", "voice.internal"],
        "82": ["connect.lab"],
    }


def test_deduplicates_and_ignores_incomplete_entries():
    entries = [
        {"ip_offset": "17", "hostname": "recon.lab"},
        {"ip_offset": "17", "hostname": "recon.lab"},
        {"ip_offset": "", "hostname": "missing-offset.lab"},
        {"ip_offset": "18", "hostname": ""},
        "not-a-dict",
        None,
    ]
    assert _lab_hostnames_by_offset(entries) == {"17": ["recon.lab"]}


def test_none_is_empty():
    assert _lab_hostnames_by_offset(None) == {}
