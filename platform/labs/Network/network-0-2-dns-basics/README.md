# The Internet's Phone Book: DNS Records

## Lab Overview

This lab introduces DNS: the system that turns names people can remember into
the IP addresses computers use. You will query an internal DNS server directly,
read several common record types, and find a flag hidden in a TXT record.

**Difficulty:** Beginner  
**Estimated Time:** 20–25 minutes  
**Focus:** Network fundamentals / DNS

## Prerequisites

- Completed **Can You Reach It? Ping Fundamentals**, or know how to open a
  terminal and read an IP address
- No previous DNS knowledge required

## Learning Objectives

By completing this lab, you will:

1. Explain the difference between a domain name and an IP address.
2. Query A, CNAME, MX, and TXT records.
3. Read TTL and explain caching at a high level.
4. Explain why DNS is a trust boundary and is not encrypted by default.

## Background

Computers route packets using IP addresses, not names. DNS is the distributed
database that maps names to addresses and publishes other information about a
domain.

A DNS query usually goes to a **resolver**. The resolver may answer from cache or
ask an **authoritative** server for the zone. In this lab, the target is the
authoritative server for `range.local`, so you will query it directly.

### Record types you will meet

| Record | Purpose | Example |
|---|---|---|
| **A** | Name to IPv4 address | `portal.range.local -> 10.100.13.10` |
| **AAAA** | Name to IPv6 address | `portal.range.local -> 2001:db8::10` |
| **CNAME** | Alias to another name | `alias.range.local -> portal.range.local` |
| **MX** | Mail server for a domain | `range.local -> mail.range.local` |
| **TXT** | Free-form text | `v=spf1 -all` |

> **Note:** The address above is from the reference `10.100.13.0/24` subnet.
> Your session may use a different `/24`; use the address shown in the
> **Active Lab View**. Static examples are not updated when the range changes.

### TTL and caching

Every record has a **TTL** (time to live). A resolver may cache the answer for
that many seconds. Caching makes DNS fast, but it also means a changed record can
take time to propagate.

## Step-by-Step Walkthrough

### Step 1: Query the portal address

Ask the lab server for the portal's A record:

```bash
dig @<target> portal.range.local A
```

Or with `nslookup`:

```bash
nslookup portal.range.local <target>
```

**What to record:**

- The IP address returned
- The TTL
- Whether the answer came from the authoritative server

### Step 2: Follow the alias

```bash
dig @<target> alias.range.local CNAME
```

A CNAME does not return an IP address. It returns another name. The resolver
then looks up that name. This is useful for service moves and for keeping one
canonical name.

### Step 3: Read the mail record

```bash
dig @<target> range.local MX
```

The MX record names the mail server and gives it a priority. Lower priority
values are preferred.

### Step 4: Read the TXT record

```bash
dig @<target> _note.range.local TXT
```

Add `+short` if you only want the value:

```bash
dig @<target> _note.range.local TXT +short
```

TXT records are often used for SPF, domain verification, and service notes. The
deployment note in this lab contains the flag.

### Step 5: Submit the flag

Copy the value inside the quotes and submit it in the platform.

## Analysis Questions

1. Why do people use names instead of remembering IP addresses?
2. What is the difference between an A record and a CNAME?
3. What does TTL control, and why can a change take time to appear?
4. Why is DNS a trust boundary?
5. DNS queries are usually unencrypted. What could an observer on the network
   learn from them?

## Common Mistakes

### Mistake 1: Querying the wrong resolver

If you run `dig portal.range.local` without `@<target>`, your machine asks its
normal resolver. That resolver does not know the lab zone. Always point the query
at the lab DNS server.

### Mistake 2: Expecting a CNAME to return an IP

A CNAME returns a name. You need a second lookup to get the address.

### Mistake 3: Ignoring the trailing dot

DNS names are fully qualified with a trailing dot: `portal.range.local.`. The
dot is easy to miss in output.

## Key Takeaways

- DNS maps names to addresses and publishes other records.
- A, CNAME, MX, and TXT are common record types with different jobs.
- TTL controls caching.
- DNS is not encrypted by default, so it reveals a lot about what a network is
  doing.

## Next Step

Continue to **Name or Network? Troubleshooting a Broken Portal** to use ping and
DNS together.
