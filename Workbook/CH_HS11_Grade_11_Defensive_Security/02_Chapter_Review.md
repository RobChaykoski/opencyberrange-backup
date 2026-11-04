# Chapter Review -- Grade 11 Defensive Security

## What You Practised

- Reading a web server access log
- Comparing successful and failed requests
- Spotting repeated probing from one source address
- Explaining evidence without guessing beyond it

## Check Your Understanding

**1.** What does a `404` status code mean in an access log?

**2.** Why can repeated `404` requests from one address be suspicious?

**3.** What is the difference between finding a suspicious line and proving what
an attacker did?

**4.** Why should a defender avoid publishing a log that contains real IP
addresses, usernames, or personal information?

## Command Cheat Sheet

| Command | What it does |
|---|---|
| `curl http://logs.lab:8080/access.log` | Print the access log |
| `curl ... -o access.log` | Save the log to a file |
| `grep " 200 " access.log` | Show successful requests |
| `grep " 404 " access.log` | Show requests the server could not find |
| `grep "<address>" access.log` | Show activity from one source |
| `grep "OCR{" access.log` | Find training-token text |

## Key Takeaways

- Logs are evidence, not conclusions.
- Status codes and paths are a quick way to find the interesting lines.
- A pattern of failures followed by an unexpected success is more meaningful than
  any single request.
- Defensive security includes protecting the evidence itself and the people it
  describes.

## Where Next?

Grade 12 applies these investigation habits to a browser-only community event
challenge. You will inspect a fictional conference portal, check where a file came
from, and protect the people whose information appears in it.
