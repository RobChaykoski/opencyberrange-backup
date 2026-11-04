# Exercise 0.3 -- Name or Network?

!!! note "Lab"
    Launch **Name or Network? Troubleshooting a Broken Portal** in the platform
    before starting. Use the target address shown in the exercise.

## Background

"The portal is down" could mean three different things:

| Layer | Question | Tool |
|---|---|---|
| **Name** | Does the name resolve to the right address? | `dig`, `nslookup` |
| **Host** | Is the address reachable? | `ping` |
| **Service** | Is the application running on the expected port? | `curl`, browser |

A stale DNS record can make a healthy service look dead. A dead service can make
a healthy host look broken. This lab gives you a ticket with an old name and asks
you to find the current one.

## Tool Primer

### Checking a name

```bash
dig @<server> <name> A +short
```

### Reading an operational note

```bash
dig @<server> _note.range.local TXT +short
```

TXT records are often used for SPF, domain verification, and service notes.

### Confirming the host

```bash
ping -c 4 <address>
```

### Checking the service

```bash
curl http://<address>/
```

## Walkthrough

### Step 1: Check the name in the ticket

```bash
dig @<target> stale.range.local A +short
```

**Record:** what address does it return? Is that address on the lab network?

### Step 2: Read the note

```bash
dig @<target> _note.range.local TXT +short
```

**Record:** what does the note tell you to do?

### Step 3: Resolve the current name

```bash
dig @<target> portal.range.local A +short
```

**Record:** what address does the current name return?

### Step 4: Confirm the host

```bash
ping -c 4 <current-ip>
```

**Record:** did the host answer? What did that prove?

### Step 5: Check the service

```bash
curl http://<current-ip>/
```

**Record:** did the service answer? What did that prove that ping did not?

### Step 6: Capture the flag

```bash
curl -s http://<current-ip>/ | grep -o 'OCR{[^}]*}'
```

Submit the flag in the platform.

## Analysis Questions

**1. Why did `ping stale.range.local` fail?**

**2. What did the TXT record tell you that the A record did not?**

**3. If the new name resolved but ping failed, what would you check next?**

**4. If ping succeeded but `curl` failed, what would that tell you?**

**5. Why is it risky to "fix" a problem before identifying which layer is broken?**

**6. What would you tell the user in one sentence?**

## A Troubleshooting Checklist

Use this order every time:

1. **Name:** does it resolve, and to the right address?
2. **Host:** does the address answer?
3. **Service:** does the expected port answer?
4. **Evidence:** what does each answer prove, and what does it not prove?

## Key Takeaways

- Troubleshoot down the layers: name, host, service.
- A stale DNS record can make a healthy service unreachable.
- TXT records are often used for operational notes and policy.
- Each tool answers a different question; none of them answers all of them.

## Next Step

Continue to the **Chapter Review** to test your recall and collect the command
cheat sheet.
