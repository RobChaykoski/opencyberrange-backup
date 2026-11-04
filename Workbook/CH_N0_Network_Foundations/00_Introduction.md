# CH N0 -- Network Foundations

!!! note "AI-assisted content"
    This chapter was drafted with AI assistance and reviewed by a human
    maintainer. Verify every command and flag against the running lab. See
    `BUILD_NOTICE.md` in the repository root for the full disclosure.

!!! note "Example IP addresses"
    The examples in this chapter use `10.100.13.0/24`, the subnet in the
    reference setup. The platform assigns each student session its own `/24`
    and displays it in the **Active Lab View**. If your session uses a
    different subnet, substitute your address in every command. These static
    examples are not updated automatically when the range changes.

## Why Start Here?

Most cybersecurity courses begin with a tool. This one begins with a question:

> **What is actually happening when my computer talks to another computer?**

Before port scans, packet captures, or exploitation, you need a mental model of
three simple things:

1. **Addresses** -- every host on a network has an IP address.
2. **Names** -- people use names such as `portal.range.local`; DNS turns them
   into addresses.
3. **Reachability** -- a host can be up even when a particular service is down.

The three labs in this chapter teach those ideas in order. Each one gives you a
small, safe target and asks you to explain what your evidence does and does not
prove.

## The Three Labs

| Lab | Question it answers | Main tools |
|---|---|---|
| **0.1 Ping Basics** | Can I reach the host at all? | `ping` |
| **0.2 DNS Basics** | What address does this name point to? | `dig`, `nslookup` |
| **0.3 Name or Network?** | Is the problem the name, the host, or the service? | `dig`, `ping`, `curl` |

## A Model You Can Reuse

Think of a request in layers:

```text
Name  ──DNS──>  Address  ──network──>  Host  ──port──>  Service
```

A failure at any layer can look like "the site is down." The skill is figuring
out **which layer** failed before you change anything.

- If the name resolves to the wrong address, the host may be perfectly healthy.
- If the host is unreachable, the service may still be running on a different path.
- If the host is reachable but the service is down, ping will still succeed.

## Safety and Ethics

These labs use an isolated range network and documentation addresses. Do not
run scans, pings, or DNS queries against systems you do not own or have explicit
permission to test.

The habit to build is:

> **Know what you are testing, why you are testing it, and what the result proves.**

## How to Work Through the Chapter

For each lab:

1. Read the background and tool primer.
2. Run the commands in your own terminal.
3. Record the actual output, not what you expected.
4. Answer the analysis questions in your own words.
5. Capture the flag only after you can explain the result.

## What You Need

- A terminal in the OpenCyberRange lab network
- The target address shown in each exercise
- No previous networking knowledge

Let's start with the simplest possible question: can you reach the host?
