# Can You Reach It? Ping Fundamentals

## Lab Overview

This is the first lab in the Network Foundations level. It teaches the simplest
question in network troubleshooting: **can this host be reached at all?**

You will use `ping` to send ICMP echo requests, read the reply, and then compare
host reachability with service availability.

**Difficulty:** Beginner  
**Estimated Time:** 15–20 minutes  
**Focus:** Network fundamentals / help-desk troubleshooting

## Prerequisites

- A terminal in the OpenCyberRange lab network
- No previous networking knowledge required

## Learning Objectives

By completing this lab, you will:

1. Explain what an ICMP echo request and echo reply are.
2. Use `ping` to test whether a host is reachable.
3. Read round-trip time, TTL, and packet loss.
4. Explain why a successful ping does not prove a service is working.

## Background

**ICMP** (Internet Control Message Protocol) is a helper protocol used for
network diagnostics. `ping` sends an **echo request** and waits for an **echo
reply**.

Ping answers one question: *did a packet make it to the host and back?* It does
not answer:

- Is the web server running?
- Is the database accepting connections?
- Is the application healthy?
- Is the firewall allowing HTTP?

Those are different layers of the problem.

## Step-by-Step Walkthrough

### Step 1: Ping the host

On Linux or macOS:

```bash
ping -c 4 <target>
```

On Windows:

```cmd
ping -n 4 <target>
```

Replace `<target>` with the portal address shown in the exercise.

> **Note:** The output below uses `10.100.13.10` from the reference lab
> subnet. Your session may use a different `/24`; use the target address shown
> in the **Active Lab View**. Static examples are not updated when the range
> changes.

**Expected output (Linux):**

```
PING 10.100.13.10 (10.100.13.10) 56(84) bytes of data.
64 bytes from 10.100.13.10: icmp_seq=1 ttl=64 time=0.42 ms
64 bytes from 10.100.13.10: icmp_seq=2 ttl=64 time=0.38 ms
64 bytes from 10.100.13.10: icmp_seq=3 ttl=64 time=0.40 ms
64 bytes from 10.100.13.10: icmp_seq=4 ttl=64 time=0.41 ms

--- 10.100.13.10 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 0.380/0.402/0.420/0.015 ms
```

### Step 2: Read the summary

Record:

| Measurement | Your value | What it means |
|---|---|---|
| Packets transmitted | | How many requests you sent |
| Packets received | | How many replies came back |
| Packet loss | | Missing replies |
| Round-trip time | | How long the trip took |

On a local lab network, the round-trip time should be small. High latency or
packet loss would point to a path or congestion problem rather than a dead host.

### Step 3: Check the service

Ping only tests the host. Now open the portal:

```bash
curl http://<target>/
```

or open `http://<target>/` in a browser.

The maintenance page contains the flag. It also explains the difference between
host reachability and service availability.

### Step 4: Record the flag

```bash
curl -s http://<target>/ | grep -o 'OCR{[^}]*}'
```

Submit the flag in the platform.

## Analysis Questions

1. What did the ping reply prove?
2. What did the ping reply **not** prove?
3. If ping succeeded but the web page failed, what would you check next?
4. If ping failed but the web page loaded, what could explain that?
5. Why might a firewall block ping but still allow HTTP?

## Common Mistakes

### Mistake 1: Treating ping as a service check

A reply means the host's network stack is alive. It says nothing about the
application listening on port 80 or 443.

### Mistake 2: Assuming 100% packet loss means the host is off

The host could be running while a firewall, routing rule, or network path drops
ICMP. Try another check before declaring the host dead.

### Mistake 3: Ignoring the summary line

The individual replies are useful, but the summary gives you packet loss and
round-trip statistics at a glance.

## Key Takeaways

- `ping` uses ICMP echo requests and replies.
- A reply proves **host reachability**, not **service availability**.
- Packet loss and latency are separate signals from "up" or "down."
- Good troubleshooting separates the network path, the host, and the service.

## Next Step

Continue to **The Internet's Phone Book: DNS Records** to learn how names become
IP addresses.
