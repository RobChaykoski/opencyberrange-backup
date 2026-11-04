# Windows Memory Analysis with Volatility

## Before You Begin

- [ ] Launched the exercise and opened RangeBox or a terminal
- [ ] You have the analyst workstation credentials
- [ ] You know the image is read-only evidence
- [ ] You have a place to record commands and output

!!! note "This image is safe to explore"
    The memory image is a training sample. It contains a fictional Windows
    Server 2008 system and test accounts. Do not copy credentials or personal
    data out of the lab.

## Scenario

A Windows Server 2008 training VM was captured before the machine was rebuilt.
The memory image and a matching Volatility symbol file are on the analyst
workstation.

Your job is to answer three questions from the image:

1. What operating system and build was running?
2. Which processes were alive?
3. What local account hashes were present in memory?

The final token is built from the first 8 characters of the `student` account's
NTLM hash.

## Connect to the Analyst Workstation

From the RangeBox terminal:

```bash
ssh analyst@memory.lab
```

Use the password from the lab credentials panel. Then read the case brief:

```bash
cat ~/evidence/case_brief.txt
```

## Step 1: Identify the image

```bash
vol -s ~/symbols -f ~/evidence/memdump.mem windows.info
```

`windows.info` prints the kernel base, build lab, architecture, and system time.
The `-s ~/symbols` option points Volatility at the symbol file supplied with the
image.

**What you should see:** a `NTBuildLab` value that starts with `6001.18000`,
which identifies Windows Server 2008 SP1 x86.

## Step 2: List the processes

```bash
vol -s ~/symbols -f ~/evidence/memdump.mem windows.pslist
```

Look at the `PID`, `PPID`, and `ImageFileName` columns. A process list can show
you:

- which services were running;
- which user applications were open;
- whether a process has an unusual parent;
- whether a known tool or malware name appears.

You can also look at command lines:

```bash
vol -s ~/symbols -f ~/evidence/memdump.mem windows.cmdline
```

## Step 3: Extract local account hashes

Volatility can read the SAM and SYSTEM registry hives from memory:

```bash
vol -s ~/symbols -f ~/evidence/memdump.mem windows.hashdump
```

The output has four tab-separated columns:

```text
User    rid    lmhash    nthash
```

Find the `student` row. The fourth field is the NTLM hash. Take its first 8
characters and place them inside `OCR{...}`.

For example, if the hash began with `abcd1234`, the flag would be
`OCR{abcd1234}`. Use the value from your own output, not the example.

## What Just Happened?

Volatility parsed the Windows kernel structures in the image, located the
registry hives, and read the local account database. The NTLM hash was in memory
because the system had loaded the registry data.

This is why memory acquisition is time-sensitive: the evidence is volatile, and
a reboot can remove it.

## Defensive Lessons

- Credential material can live in memory even when it is not on disk.
- Limit who can acquire memory and where images are stored.
- Treat memory images as sensitive evidence.
- Clear secrets from memory where the application supports it.
- Use disk encryption and strong account passwords, but do not assume either
  protects a running system.

## Analysis Questions

**1. What is the difference between disk evidence and memory evidence?**

**2. Why does Volatility need a symbol file?**

**3. What can a process list tell an investigator that a file listing cannot?**

**4. Why is a memory image sensitive even if the disk is encrypted?**

**5. What would you document before and after acquiring memory?**
