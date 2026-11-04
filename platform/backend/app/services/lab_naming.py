"""Shared parsing for discovery-compatible lab directory names."""

import re


def parse_lab_slug(dirname: str):
    """Extract track, level, and lab number from a lab directory name.

    Examples:
        web-1-1-basic-directory-enumeration -> (web, 1, 1)
        high-school-10-1-rangebox-network-basics -> (high-school, 10, 1)
        software-security-2-1-diagnostics-command-injection
            -> (software-security, 2, 1)
        linux-midterm-3-blind-penetration-test -> (linux, None, 3)

    Supports compound track slugs: walks parts left-to-right, concatenating
    non-numeric parts as the track slug until the first numeric part (level).
    """
    parts = dirname.split("-")
    if len(parts) < 3:
        return None, None, None

    track_parts = []
    i = 0
    while i < len(parts):
        try:
            int(parts[i])
            break
        except ValueError:
            pass
        drill_match = re.match(r"^[Dd](\d+)$", parts[i])
        if drill_match:
            break
        track_parts.append(parts[i].lower())
        i += 1

    if not track_parts or i + 1 >= len(parts):
        return None, None, None

    if track_parts[-1] in ("midterm", "final"):
        base_track = "-".join(track_parts[:-1])
        if not base_track:
            return None, None, None
        try:
            special_num = int(parts[i])
            if track_parts[-1] == "final":
                special_num = 500 + special_num
            return base_track, None, special_num
        except (ValueError, IndexError):
            return None, None, None

    track_slug = "-".join(track_parts)
    try:
        drill_match = re.match(r"^[Dd](\d+)$", parts[i])
        if drill_match:
            level_num = 900 + int(drill_match.group(1))
        else:
            level_num = int(parts[i])
        lab_num = int(parts[i + 1])
        return track_slug, level_num, lab_num
    except (ValueError, IndexError):
        return None, None, None
