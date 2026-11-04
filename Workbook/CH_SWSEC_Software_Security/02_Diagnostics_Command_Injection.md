# Diagnostics Command Injection

## Before You Begin

- [ ] Launched the **Diagnostics Command Injection** exercise
- [ ] Opened the lab browser at `http://diag.lab:8080`
- [ ] You know the target is fictional and isolated
- [ ] You know you can pause, use a hint, or stop at any time

!!! warning "Safe target only"
    This exercise intentionally runs a shell inside its own isolated container.
    Never use these techniques against a system you do not own or have written
    permission to test.

## Scenario

The DevFest volunteer team added a small diagnostics page to check that
conference network names resolve. It accepts a hostname and prints the lookup
result.

The page was written quickly. The developer passed the visitor's input to a
shell command, so a separator can turn one lookup into two commands.

Your job is to find the injection point, read the flag, and explain how to fix
the bug.

## Your Objectives

- Run a normal lookup and observe the output
- Identify that the input reaches a shell
- Use a shell separator to run a second command
- Read the flag from `/tmp/flag`
- Explain the fix: argument arrays, allowlisting, and least privilege

## Background: Input Becomes Code

A shell treats characters such as `;`, `|`, `&`, `$()`, and backticks as
control characters. If an application builds a command by joining a string,
the user's input can become part of the command language.

Vulnerable pattern:

```python
subprocess.run(f"getent hosts {host}", shell=True)
```

If `host` is `127.0.0.1; cat /tmp/flag`, the shell runs two commands.

Safer pattern:

```python
subprocess.run(["getent", "hosts", host], shell=False)
```

The argument array still passes the value to `getent`, but the shell never
parses it as a second command.

## Walkthrough

### Step 1: Run a normal lookup

Open:

```text
http://diag.lab:8080
```

Leave the default `127.0.0.1` and submit. The page shows the lookup output.

### Step 2: Add a second command

In the host field, try:

```text
127.0.0.1; cat /tmp/flag
```

Submit the form. The result should include the training flag.

### Step 3: Submit the flag

Copy the `OCR{...}` value into the exercise flag box.

## What Just Happened?

The application trusted the host field and passed it to `sh -c`. The semicolon
ended the first command and started a second one. The second command read the
flag file.

The bug is not "the flag file exists." The bug is that untrusted input reached a
shell.

## Analysis Questions

**1. Which character changed the meaning of the command?**

**2. Why does `shell=False` with an argument array prevent this?**

**3. What other characters can separate commands in a shell?**

**4. Why is an allowlist safer than a blocklist for hostnames?**

**5. What privilege should the diagnostics service run with, and why?**

## Defensive Takeaways

- Avoid `shell=True` and string-built commands.
- Pass arguments as a list and validate them.
- Allowlist expected hostnames or IP formats.
- Run the service as an unprivileged user with no capabilities.
- Keep secrets out of files reachable by the service unless the exercise needs
  them.
- Add a test with `;`, `|`, `$()`, and backticks and expect a safe rejection.

## If You Get Stuck

- Start with a normal lookup and confirm the output.
- Try adding `;` and a harmless second command such as `id`.
- The flag is in `/tmp/flag` inside the training container.
- Ask a facilitator; using a hint is expected.

## Further Reading

- OWASP Top 10: Injection
- OWASP Command Injection Prevention Cheat Sheet
- Python `subprocess` documentation: shell=False and argument lists
