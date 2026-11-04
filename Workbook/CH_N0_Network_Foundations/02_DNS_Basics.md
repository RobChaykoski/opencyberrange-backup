# Exercise 0.2 -- DNS Basics

!!! note "Lab"
    Launch **The Internet's Phone Book: DNS Records** in the platform before
    starting. Use the DNS server address shown in the exercise.

!!! note "Example IP addresses"
    The record examples use `10.100.13.10` from the reference lab subnet. The
    platform assigns each student session its own `/24` and shows it in the
    **Active Lab View**. If your session uses a different subnet, substitute
    your address. Static examples are not updated when the range changes.

## Background

DNS is the distributed database that maps names to addresses and publishes other
information about a domain. People use names; computers route packets using IP
addresses.

A DNS query usually goes to a **resolver**, which may answer from cache or ask an
**authoritative** server for the zone. In this lab, the target is the
authoritative server for `range.local`, so you will query it directly.

## Record Types

| Record | Purpose | Example |
|---|---|---|
| **A** | Name to IPv4 address | `portal.range.local -> 10.100.13.10` |
| **AAAA** | Name to IPv6 address | `portal.range.local -> 2001:db8::10` |
| **CNAME** | Alias to another name | `alias.range.local -> portal.range.local` |
| **MX** | Mail server for a domain | `range.local -> mail.range.local` |
| **TXT** | Free-form text | `v=spf1 -all` |

## Tool Primer

### `dig`

```bash
dig @<server> <name> <type>
```

- `@<server>` asks a specific DNS server instead of your normal resolver.
- `<type>` is `A`, `AAAA`, `CNAME`, `MX`, `TXT`, or another record type.
- `+short` trims the output to the answer.

### `nslookup`

```bash
nslookup <name> <server>
```

This is useful on systems where `dig` is not installed.

### `host`

```bash
host <name> <server>
```

A compact alternative that shows the record type and value.

## Walkthrough

### Step 1: Query the portal A record

```bash
dig @<target> portal.range.local A
```

**Record:**

| Field | Your value |
|---|---|
| IP address | |
| TTL | |
| Server that answered | |

### Step 2: Follow the alias

```bash
dig @<target> alias.range.local CNAME
```

**Record:** what name does the alias point to? Why does a CNAME not return an IP
address directly?

### Step 3: Read the mail record

```bash
dig @<target> range.local MX
```

**Record:** which host handles mail, and what is its priority?

### Step 4: Read the TXT note

```bash
dig @<target> _note.range.local TXT
```

Add `+short` for a compact answer:

```bash
dig @<target> _note.range.local TXT +short
```

**Record:** what is inside the quotes?

### Step 5: Capture the flag

The TXT value is the flag. Submit it in the platform.

## Analysis Questions

**1. Why do people use names instead of remembering IP addresses?**

**2. What is the difference between an A record and a CNAME?**

**3. What does TTL control, and why can a change take time to appear?**

**4. Why is DNS a trust boundary?**

**5. DNS queries are usually unencrypted. What could an observer learn from them?**

**6. What happens if you query the name without `@<target>`?**

## Key Takeaways

- DNS maps names to addresses and publishes other records.
- A, CNAME, MX, and TXT are common record types with different jobs.
- TTL controls caching.
- DNS is not encrypted by default.
- The authoritative server for a zone is the source of truth for that zone.

## Next Step

Continue to **Exercise 0.3 -- Name or Network?** to combine ping and DNS in a
troubleshooting scenario.
