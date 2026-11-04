#!/usr/bin/env python3
"""
Seed script to populate tracks and levels for the curriculum
Run inside the backend container or with proper database connection
"""

import os
import sys

# Add the app directory to path if running standalone
sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://labuser:labpass@db:5432/labdb')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Track definitions
TRACKS = [   {   'name': 'Windows Penetration Testing',
        'slug': 'windows',
        'description': 'Master Windows enumeration, authentication attacks, and service '
                       'exploitation.',
        'icon': 'windows',
        'color': '#0078D4',
        'sort_order': 1,
        'levels': [   {   'level_number': 1,
                          'name': 'Reconnaissance Fundamentals',
                          'description': 'Building enumeration skills through repetition'},
                      {   'level_number': 2,
                          'name': 'SMB Enumeration Part 1',
                          'description': 'Mastering SMB enumeration techniques'},
                      {   'level_number': 3,
                          'name': 'SMB Credential Attacks',
                          'description': 'Building credential attack skills'},
                      {   'level_number': 4,
                          'name': 'RDP Enumeration and Exploitation',
                          'description': 'Applying enumeration pattern to RDP'},
                      {   'level_number': 5,
                          'name': 'WinRM Enumeration and Exploitation',
                          'description': 'Applying pattern to WinRM service'},
                      {   'level_number': 6,
                          'name': 'MS-SQL Enumeration and Exploitation',
                          'description': 'Applying pattern to database services'},
                      {   'level_number': 7,
                          'name': 'LDAP Enumeration and Exploitation',
                          'description': 'Applying pattern to directory services'},
                      {   'level_number': 8,
                          'name': 'Credential Reuse and Lateral Movement',
                          'description': 'Combining previously learned skills, introducing '
                                         'automation with CrackMapExec'},
                      {   'level_number': 9,
                          'name': 'Comprehensive Windows Penetration Test',
                          'description': 'Final comprehensive testing using all skills, with '
                                         'CrackMapExec as primary automation tool'}]},
    {   'name': 'Linux Fundamentals',
        'slug': 'linux',
        'description': 'Learn Linux enumeration, privilege escalation, and system exploitation '
                       'techniques.',
        'icon': 'linux',
        'color': '#E95420',
        'sort_order': 2,
        'levels': [   {   'level_number': 1,
                          'name': 'Linux Reconnaissance',
                          'description': 'Basic Linux service enumeration'},
                      {   'level_number': 2,
                          'name': 'SSH Enumeration and Exploitation',
                          'description': 'SSH service attacks'},
                      {   'level_number': 3,
                          'name': 'Web Services on Linux',
                          'description': 'Apache, Nginx enumeration'},
                      {   'level_number': 4,
                          'name': 'Linux Privilege Escalation',
                          'description': 'SUID, sudo, cron exploitation'},
                      {   'level_number': 5,
                          'name': 'Comprehensive Linux Penetration Test',
                          'description': 'Full Linux attack chain'},
                      {   'level_number': 9,
                          'name': 'Capstone Assessments',
                          'description': 'End-to-end incident and recovery scenarios'}]},
    {   'name': 'Web Application Security',
        'slug': 'web',
        'description': 'Discover and exploit common web vulnerabilities including injection, XSS, '
                       'and authentication flaws.',
        'icon': 'web',
        'color': '#22C55E',
        'sort_order': 3,
        'levels': [   {   'level_number': 1,
                          'name': 'Web Reconnaissance',
                          'description': 'Directory enumeration, technology identification'},
                      {   'level_number': 2,
                          'name': 'Injection Vulnerabilities',
                          'description': 'SQL injection, command injection'},
                      {   'level_number': 3,
                          'name': 'Authentication Attacks',
                          'description': 'Brute force, session hijacking'},
                      {   'level_number': 4,
                          'name': 'Cross-Site Scripting (XSS)',
                          'description': 'Reflected, stored, DOM-based XSS'},
                      {   'level_number': 5,
                          'name': 'File Vulnerabilities',
                          'description': 'File upload, LFI, RFI'},
                      {   'level_number': 6,
                          'name': 'Advanced Web Exploitation',
                          'description': 'SSRF, XXE, deserialization'}]},
    {   'name': 'Network Security',
        'slug': 'network',
        'description': 'Learn network analysis, traffic capture, man-in-the-middle attacks, and '
                       'network protocol exploitation.',
        'icon': 'network',
        'color': '#8B5CF6',
        'sort_order': 4,
        'levels': [   {   'level_number': 0,
                          'name': 'Network Foundations',
                          'description': 'Ping, DNS, and name-resolution basics before the '
                                         'graded levels'},
                      {   'level_number': 1,
                          'name': 'Network Reconnaissance',
                          'description': 'Network scanning and mapping'},
                      {   'level_number': 2,
                          'name': 'Traffic Analysis',
                          'description': 'Wireshark, packet capture'},
                      {   'level_number': 3,
                          'name': 'Network Protocol Attacks',
                          'description': 'ARP, DNS, DHCP attacks'},
                      {   'level_number': 4,
                          'name': 'Man-in-the-Middle',
                          'description': 'MITM techniques and tools'},
                      {   'level_number': 5,
                          'name': 'Network Services Exploitation',
                          'description': 'FTP, Telnet, SNMP attacks'},
                      {   'level_number': 12,
                          'name': 'Firewalls and Filtering',
                          'description': 'Controlling inbound traffic and hardening firewall '
                                         'policy'}]},
    {   'name': 'Malware Analysis',
        'slug': 'malware',
        'description': 'Triage malicious samples safely: identify, hash, and reason about '
                       'what a file does before anything runs.',
        'icon': 'forensics',
        'color': '#F59E0B',
        'sort_order': 5,
        'levels': [   {   'level_number': 1,
                          'name': 'Malware Fundamentals',
                          'description': 'Safe handling, triage, and sample identification'},
                      {   'level_number': 2,
                          'name': 'Executable Analysis',
                          'description': 'PE headers, sections, imports, and static triage of '
                                         'Windows binaries'}]},
    {   'name': 'OT/ICS Security',
        'slug': 'ot',
        'description': 'Industrial control systems and operational technology: Modbus, '
                       'register maps, and protocol-aware triage.',
        'icon': 'network',
        'color': '#10B981',
        'sort_order': 6,
        'levels': [   {   'level_number': 1,
                          'name': 'Modbus Fundamentals',
                          'description': 'Modbus TCP enumeration and register decoding'}]},
    {   'name': 'AI Hacking',
        'slug': 'ai',
        'description': 'Attack and defend large language model applications: prompt '
                       'injection, jailbreaks, data exposure, and agent abuse.',
        'icon': 'aisec',
        'color': '#EC4899',
        'sort_order': 7,
        'levels': [   {   'level_number': 1,
                          'name': 'AI Security Foundations',
                          'description': 'Prompt injection, policy bypass, and indirect '
                                         'prompt injection against safe mock assistants'},
                      {   'level_number': 2,
                          'name': 'Instruction Hierarchy and Evasion',
                          'description': 'Encoded payloads, multi-turn attacks, and '
                                         'defences that separate data from instructions'},
                      {   'level_number': 3,
                          'name': 'LLM Data Exposure and RAG',
                          'description': 'System-prompt leakage, retrieval poisoning, and '
                                         'secret handling in AI applications'},
                      {   'level_number': 4,
                          'name': 'AI Agents and Tool Abuse',
                          'description': 'Function calling, excessive agency, and indirect '
                                         'injection that reaches an action'},
                      {   'level_number': 5,
                          'name': 'Model Supply Chain and Adversarial ML',
                          'description': 'Model provenance, malicious artifacts, and input '
                                         'manipulation risks'},
                      {   'level_number': 6,
                          'name': 'AI-Assisted Security and Capstone',
                          'description': 'Using AI responsibly in security operations and a '
                                         'full AI application assessment'}]},
    {   'name': 'OSINT',
        'slug': 'osint',
        'description': 'Collect and correlate public information from web pages, '
                       'images, metadata, and code. Follow a fictional organisation\'s '
                       'public footprint without touching a real target.',
        'icon': 'osint',
        'color': '#0EA5E9',
        'sort_order': 8,
        'levels': [   {   'level_number': 1,
                          'name': 'Digital Footprint Foundations',
                          'description': 'Public profiles, robots.txt, source comments, '
                                         'and image metadata'},
                      {   'level_number': 2,
                          'name': 'Code and Sources',
                          'description': 'Static assets, JavaScript comments, and leaked '
                                         'public repository material'}]},
    {   'name': 'High School Cybersecurity',
        'slug': 'high-school',
        'description': 'A browser-first pathway for grades 9-12. Start with RangeBox '
                       'basics, move into networks and browser source, practise '
                       'defensive log reading in Grade 11, then apply those skills in '
                       'Grade 12.',
        'icon': 'brain',
        'color': '#8B5CF6',
        'sort_order': 9,
        'levels': [   {   'level_number': 9,
                          'name': 'Grade 9 · RangeBox Basics',
                          'description': 'Launching the practice desktop, terminal basics, and file discovery'},
                      {   'level_number': 10,
                          'name': 'Grade 10 · Networks and the Web',
                          'description': 'Hostnames, HTTP responses, and browser source'},
                      {   'level_number': 11,
                          'name': 'Grade 11 · Defensive Security',
                          'description': 'Reading logs, spotting suspicious requests, and explaining evidence'},
                      {   'level_number': 12,
                          'name': 'Grade 12 · Applied Cybersecurity',
                          'description': 'Community event challenges, metadata, and '
                                         'browser-only investigations'}]},
    {   'name': 'Software Security',
        'slug': 'software-security',
        'description': 'Read code, find missing checks, and build safe exploits '
                       'against isolated training targets.',
        'icon': 'web',
        'color': '#0EA5E9',
        'sort_order': 10,
        'levels': [   {   'level_number': 1,
                          'name': 'Reading Code for Bugs',
                          'description': 'Source review, hidden routes, and '
                                         'client-side secrets'},
                      {   'level_number': 2,
                          'name': 'Injection and Exploitation',
                          'description': 'Command injection and the first exploit '
                                         'payload'},
                      {   'level_number': 3,
                          'name': 'Authentication and Authorization',
                          'description': 'IDOR, broken access control, and session '
                                         'checks'},
                      {   'level_number': 4,
                          'name': 'Memory Safety and Exploit Development',
                          'description': 'Crash triage, offsets, and a first exploit '
                                         'script'},
                      {   'level_number': 5,
                          'name': 'Capstone Exploit Development',
                          'description': 'End-to-end exploitation, mitigation, and '
                                         'disclosure'}]},
    {   'name': 'Digital Forensics',
        'slug': 'forensics',
        'description': 'Investigate memory and network evidence: reconstruct '
                       'activity from volatile data and captured traffic.',
        'icon': 'forensics',
        'color': '#14B8A6',
        'sort_order': 11,
        'levels': [   {   'level_number': 1,
                          'name': 'Memory Forensics',
                          'description': 'Memory images, processes, and volatile evidence'},
                      {   'level_number': 2,
                          'name': 'Network Forensics',
                          'description': 'Packet captures, voice traffic, and protocol reconstruction'}]}]

# Additional levels not part of the main track definitions
# (e.g., midterm/assessment levels inserted at non-sequential positions)
EXTRA_LEVELS = [
    {
        "track_slug": "windows",
        "level_number": 10,
        "name": "Midterm Assessment",
        "description": "Midterm assessment labs covering network enumeration and penetration testing techniques from previous levels.",
    },
]


def seed_curriculum():
    """Seed tracks and levels into database (supports incremental updates)"""
    db = SessionLocal()
    
    try:
        from sqlalchemy import text
        
        tracks_created = 0
        tracks_updated = 0
        levels_created = 0
        levels_updated = 0
        
        for track_data in TRACKS:
            levels = track_data.get('levels', [])
            track_slug = track_data['slug']
            track_payload = {k: v for k, v in track_data.items() if k != 'levels'}
            
            # Check if track exists
            existing_track = db.execute(
                text("SELECT id FROM tracks WHERE slug = :slug"),
                {"slug": track_slug}
            ).fetchone()
            
            if existing_track:
                # Update existing track
                track_id = existing_track[0]
                db.execute(
                    text("""
                        UPDATE tracks SET
                            name = :name,
                            description = :description,
                            icon = :icon,
                            color = :color,
                            sort_order = :sort_order,
                            is_active = TRUE
                        WHERE slug = :slug
                    """),
                    {**track_payload, "slug": track_slug}
                )
                print(f"✓ Updated track: {track_data['name']} (id={track_id})")
                tracks_updated += 1
            else:
                # Insert new track
                result = db.execute(
                    text("""
                        INSERT INTO tracks (name, slug, description, icon, color, sort_order, is_active)
                        VALUES (:name, :slug, :description, :icon, :color, :sort_order, TRUE)
                        RETURNING id
                    """),
                    {**track_payload, "slug": track_slug}
                )
                track_id = result.fetchone()[0]
                print(f"✓ Created track: {track_data['name']} (id={track_id})")
                tracks_created += 1
            
            # Process levels for this track
            for level_data in levels:
                # Check if level exists
                existing_level = db.execute(
                    text("""
                        SELECT id FROM levels 
                        WHERE track_id = :track_id AND level_number = :level_number
                    """),
                    {
                        "track_id": track_id,
                        "level_number": level_data["level_number"]
                    }
                ).fetchone()
                
                if existing_level:
                    # Update existing level
                    db.execute(
                        text("""
                            UPDATE levels SET
                                name = :name,
                                description = :description,
                                sort_order = :sort_order
                            WHERE track_id = :track_id AND level_number = :level_number
                        """),
                        {
                            "track_id": track_id,
                            "level_number": level_data["level_number"],
                            "name": level_data["name"],
                            "description": level_data["description"],
                            "sort_order": level_data["level_number"]
                        }
                    )
                    print(f"  ✓ Updated level {level_data['level_number']}: {level_data['name']}")
                    levels_updated += 1
                else:
                    # Insert new level
                    db.execute(
                        text("""
                            INSERT INTO levels (track_id, level_number, name, description, sort_order)
                            VALUES (:track_id, :level_number, :name, :description, :sort_order)
                        """),
                        {
                            "track_id": track_id,
                            "level_number": level_data["level_number"],
                            "name": level_data["name"],
                            "description": level_data["description"],
                            "sort_order": level_data["level_number"]
                        }
                    )
                    print(f"  ✓ Created level {level_data['level_number']}: {level_data['name']}")
                    levels_created += 1
        
        # Process extra levels (e.g., midterm assessments at non-sequential positions)
        for extra in EXTRA_LEVELS:
            track_id = db.execute(
                text("SELECT id FROM tracks WHERE slug = :slug"),
                {"slug": extra["track_slug"]}
            ).fetchone()
            if not track_id:
                print(f"  ⚠ Skipping extra level: track '{extra['track_slug']}' not found")
                continue
            track_id = track_id[0]

            existing = db.execute(
                text("SELECT id FROM levels WHERE track_id = :tid AND level_number = :ln"),
                {"tid": track_id, "ln": extra["level_number"]}
            ).fetchone()

            if existing:
                db.execute(
                    text("UPDATE levels SET name = :name, description = :desc, sort_order = :so WHERE id = :id"),
                    {"name": extra["name"], "desc": extra["description"], "so": 0, "id": existing[0]}
                )
                print(f"  ✓ Updated extra level {extra['track_slug']}/{extra['level_number']}: {extra['name']}")
                levels_updated += 1
            else:
                db.execute(
                    text("INSERT INTO levels (track_id, level_number, name, description, sort_order) VALUES (:tid, :ln, :name, :desc, :so)"),
                    {"tid": track_id, "ln": extra["level_number"], "name": extra["name"], "desc": extra["description"], "so": 0}
                )
                print(f"  ✓ Created extra level {extra['track_slug']}/{extra['level_number']}: {extra['name']}")
                levels_created += 1

        db.commit()
        print("\n✓ Curriculum seeding complete!")
        print(f"  Tracks: {tracks_created} created, {tracks_updated} updated")
        print(f"  Levels: {levels_created} created, {levels_updated} updated")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding curriculum: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_curriculum()
