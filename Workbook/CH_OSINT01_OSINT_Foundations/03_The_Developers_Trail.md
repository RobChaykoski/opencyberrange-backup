# Exercise 2.1: The Developer's Trail

## Before You Begin

- [ ] Launched the exercise and opened the lab browser or a terminal
- [ ] You can reach `http://connect.lab:8080`
- [ ] You have `curl` and `grep`

## Scenario

Kestrel Connect's dashboard is built from a handful of static files. The
visible pages are deliberately ordinary, but the front end shipped with a
developer note that was supposed to be removed before launch.

This is the bonus challenge in the OSINT track. Treat the public web surface
as a source: JavaScript, CSS, comments, source maps, and the public repository
are all fair game.

A second bonus flag has escaped into the public OpenCyberRange repository.
That one is not required to complete this exercise, but it is part of the
same lesson: public code leaks.

## Your Objectives

- Inspect a site's static assets instead of only its rendered pages
- Read JavaScript comments and build metadata
- Recover the staging token and submit it as the exercise flag
- Find the bonus flag in the public repository

## Background: Client-Side Code Is Public

Everything the browser downloads is public:

- HTML, CSS, and JavaScript
- source maps
- comments and build identifiers
- API paths and feature flags

A secret in client-side code is not a secret. Minification is not protection;
it only makes the code less readable. Source maps and lazy-loaded chunks often
put the original names back.

Developers leave useful traces in comments: `TODO`, `FIXME`, ticket numbers,
staging hostnames, and occasionally tokens.

## Walkthrough

### Step 1: View the page source

Open:

```text
http://connect.lab:8080
```

Use **View Page Source** or fetch it with `curl`:

```bash
curl -s http://connect.lab:8080/ | head -60
```

Look for the `<script src="/static/app.js">` tag. Static assets are part of
the public surface even when they are not linked from the navigation.

### Step 2: Fetch the JavaScript

```bash
curl -s http://connect.lab:8080/static/app.js
```

Search it for comments and staging strings:

```bash
curl -s http://connect.lab:8080/static/app.js | grep -n -i 'TODO\|token\|staging\|OCR'
```

The flag is in a block comment near the bottom of the file.

### Step 3: Submit the flag

Copy the `OCR{...}` value into the exercise flag box.

### Bonus: The public repository leak

A Kestrel Ridge staging note escaped into the public OpenCyberRange
repository. Find it using GitHub's code search or by browsing the repository:

- search for `Kestrel Ridge`
- search for the badge ID `KR-0421`
- search for `staging token`

The note contains a second `OCR{...}` value. That is the bonus flag. It is not
required for this exercise, but record where you found it and why it should
never have been committed.

## What Just Happened?

The flag was not in the rendered page. It was in a file the page loaded. The
browser needed that file, so the server served it to anyone who asked.

The same logic applies to the public repository. A commit is a publication.
Deleting a file in a later commit does not remove it from history, forks, or
search indexes.

## Analysis Questions

**1. Why is minification not a security control?**

**2. What kinds of comments should never reach production JavaScript?**

**3. How would you search a public repository without cloning it?**

**4. What should a team do if a real token was committed to a public repo?**

**5. How can source maps make a review easier?**

## Defensive Takeaways

- Never put credentials, tokens, or internal hostnames in client-side code.
- Treat every committed file as public, including deleted files in history.
- Scan build output for secret patterns before publishing.
- Use short-lived, least-privilege tokens even when a leak seems unlikely.
- Rotate a secret immediately if it reaches a public repository.

## If You Get Stuck

- Fetch `/static/app.js` directly; do not rely on the rendered dashboard.
- Search for `TODO`, `token`, `staging`, or `OCR`.
- For the bonus flag, search the public repository for `Kestrel Ridge` or
  `KR-0421`.
