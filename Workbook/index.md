# OpenCyberRange Workbook

Welcome to the OpenCyberRange student workbook. Each exercise walkthrough guides you step by step, explains the underlying concepts, and prompts you to record and interpret your findings.

!!! note "AI-assisted content"
    Parts of this workbook were drafted with AI assistance and reviewed by a
    human maintainer. Verify every command, target, and flag against the running
    lab before relying on it. See `BUILD_NOTICE.md` in the repository root for
    attribution and the full AI-assistance disclosure.

!!! note "Example IP addresses"
    The walkthrough examples use `10.100.13.0/24`, the subnet in the reference
    setup. The platform assigns each student session its own `/24` and shows it
    in the **Active Lab View**. If your session uses a different subnet,
    substitute your address in every command. Workbook examples are static and
    may not reflect later changes to the address range.

## Available Tracks

### Windows Penetration Testing

| Chapter | Focus | Exercises |
|---------|-------|------|
| CH01; Enumeration | Port scanning, service detection, OS fingerprinting | 5 exercises |
| CH02; SMB Reconnaissance | Anonymous shares, null sessions, user enumeration | 8 exercises |
| CH03; SMB Credential Attacks | Manual auth, brute force, credential chains | 5 exercises |
| CH04; RDP Exploitation | Service detection, enumeration, brute force, session access | 6 exercises |
| CH05; WinRM Exploitation | Service detection, authentication, command execution, file retrieval | 6 exercises |
| CH06; MSSQL Exploitation | Service detection, authentication, queries, file system access | 7 exercises |
| CH07; LDAP Enumeration | Service detection, anonymous bind, users, groups, full dump | 6 exercises |
| CH08; Credential Reuse | Cross-service credential discovery and lateral movement | 5 exercises |
| CH09; Complete Assessment | Multi-service exploitation and full penetration test | 3 exercises |
| CH10; Midterm Assessment | Network enumeration and midterm assessment | 2 exercises |

### Linux Penetration Testing

| Chapter | Focus | Exercises |
|---------|-------|------|
| CH L1; Linux Service Enumeration | SSH detection, multi-service discovery, NSE scripts, vulnerability ID | 6 exercises |
| CH L2; SSH Authentication | Basic login, user discovery, file discovery | 3 exercises |
| CH L3; SSH Post-Exploitation | Command execution, history analysis, privilege escalation | 3 exercises |

### Network Security

| Chapter | Focus | Exercises |
|---------|-------|------|
| CH N0; Network Foundations | IP addresses, ping, DNS, name-resolution troubleshooting | 3 exercises |
| CH N1; Log Analysis | Firewall logs, DNS logs, SSH auth logs, HTTP PCAP | 4 exercises |
| CH N2; PCAP Forensics | FTP, SMTP, HTTP sessions, DNS tunneling, attack chains | 5 exercises |

Start the Network Foundations chapter at
[CH N0 — Network Foundations](CH_N0_Network_Foundations/00_Introduction.md).

### Malware Analysis

| Chapter | Focus | Exercises |
|---------|-------|------|
| CH M1; Malware Fundamentals | Safe handling, strings triage, Ghidra reversing, C2 PCAP, live INetSim detection, email attachment and embedded-document analysis | 7 exercises |
| CH M2; Executable Analysis | PE headers, sections, imports, static triage of Windows binaries | 1 exercise |

### OT/ICS Security

| Chapter | Focus | Exercises |
|---------|-------|------|
| CH OT1; Modbus Fundamentals | Modbus TCP enumeration and register decoding | 1 exercise |

### AI Hacking

| Chapter | Focus | Exercises |
|---------|-------|------|
| CH AI1; AI Security Foundations | Prompt injection, jailbreak policy bypass, indirect prompt injection | 3 exercises |

Start the AI Hacking stream at
[CH AI1 — AI Security Foundations](CH_AI01_AI_Foundations/00_Introduction.md).

### OSINT

| Chapter | Focus | Exercises |
|---------|-------|-----------|
| CH OSINT1; Digital Footprint Foundations | Public profiles, `robots.txt`, source comments, image steganography | 2 exercises |
| CH OSINT2; Code and Sources | Static JavaScript, source-code comments, public metadata, public-repository leaks | 2 exercises |

Start the OSINT stream at
[CH OSINT1 — Digital Footprint Foundations](CH_OSINT01_OSINT_Foundations/00_Introduction.md).

### Software Security

| Chapter | Focus | Exercises |
|---------|-------|-----------|
| CH SWSEC; Software Security | Reading shipped code, hidden routes, client-side secrets, command injection, and remediation | 2 exercises |

Start the software-security stream at
[CH SWSEC — Software Security](CH_SWSEC_Software_Security/00_Introduction.md).

### Digital Forensics

| Chapter | Focus | Exercises |
|---------|-------|-----------|
| CH FOR01; Memory Forensics | Memory images, processes, registry data, and Volatility 3 | 1 exercise |
| CH FOR02; Network Forensics | Packet captures, SIP/RTP, and voice reconstruction | 1 exercise |

Start the forensics pathway at
[CH FOR01 - Memory Forensics](CH_FOR01_Memory_Forensics/00_Introduction.md).

### High School Cybersecurity

| Chapter | Focus | Exercises |
|---------|-------|-----------|
| CH HS09; Grade 9 RangeBox Basics | Launching RangeBox, terminal basics, file search | 2 exercises |
| CH HS10; Grade 10 RangeBox Basics | Hostnames, HTTP responses, browser source | 2 exercises |
| CH HS11; Grade 11 Defensive Security | Web server logs, suspicious requests, evidence and response | 1 exercise |
| CH HS12; Grade 12 Applied Cybersecurity | Browser-only OSINT, file metadata, privacy, and community event challenges | 1 exercise |

Start the high-school pathway at
[CH HS09 - Grade 9 RangeBox Basics](CH_HS09_Grade_9_RangeBox_Basics/00_Introduction.md).

## How to Use This Workbook

1. **Launch an exercise** in the OpenCyberRange platform
2. **Click the Workbook button** to open the walkthrough for that exercise
3. **Follow the steps** in the walkthrough while working in your terminal
4. **Record your findings** in the spaces provided
5. **Answer the analysis questions** to deepen your understanding

Each walkthrough includes background concepts, tool primers, guided steps, and analysis questions. The chapter reviews provide self-assessment quizzes and command cheat sheets.
