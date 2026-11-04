# Exercise 1.1: The Public Footprint

## Before You Begin

- [ ] Launched the exercise and opened the lab browser or a terminal
- [ ] `connect.lab` resolves to the target shown in the exercise panel
- [ ] You can reach `http://connect.lab:8080`

## Scenario

Kestrel Ridge's intranet, **Kestrel Connect**, is an ordinary staff site: a
dashboard, a people directory, a kudos wall, and company announcements.

One of the people-security review pages is still reachable. It is not linked
from the dashboard, and the site owner probably believes nobody will find it.
Your job is to prove otherwise.

## Your Objectives

- Map the visible pages of the intranet
- Read `robots.txt` for paths the site owner tried to hide
- Inspect the source of a profile and a review page
- Recover the flag from the restricted notes page

## Background: What Hides in Plain Sight

Three ordinary web conventions leak structure:

**`robots.txt`** tells search engines where not to crawl. It is not an access
control. A `Disallow` line is a hint that a path exists.

**HTML comments** survive in the page source. Developers use them for review
notes, build IDs, and reminders. They are visible to anyone who presses
**View Source**.

**Directory patterns** tend to repeat. If a profile lives at
`/people/first.last`, a related page often lives at a predictable child path.

## Walkthrough

### Step 1: Start at the dashboard

```text
http://connect.lab:8080
```

The dashboard shows the people directory, the kudos wall, and a few
announcements. Read the page as an outsider: what names, roles, and teams are
being published?

### Step 2: Read the robots file

```bash
curl -s http://connect.lab:8080/robots.txt
```

You should see `Disallow` entries. One of them points at a page under
`/people/dana.whitfield/`. Note the exact path.

### Step 3: Visit the profile

Open the people directory and find **Dana Whitfield**. The profile includes a
role, a team, a badge ID, recent kudos, and a badge photo. This is the normal,
intended surface of the site.

### Step 4: Open the restricted page

Use the path from `robots.txt`:

```text
http://connect.lab:8080/people/dana.whitfield/notes
```

The page renders a short review note. Now inspect the page source, not just
the rendered text. The flag is in an HTML comment near the bottom.

From the terminal:

```bash
curl -s http://connect.lab:8080/people/dana.whitfield/notes | grep -o 'OCR{[^}]*}'
```

### Step 5: Submit the flag

Copy the `OCR{...}` value into the exercise flag box. In a real assessment,
also record the URL, the exact command, and the time you collected it.

## What Just Happened?

The site did not have a vulnerability in the classic sense. It published a
path it did not want indexed and left a comment in the page source. Both are
ordinary developer habits, and both are visible to an outside researcher.

This is the core OSINT lesson: **the public surface is larger than the links
in the navigation bar**.

## Analysis Questions

**1. Why is `robots.txt` a hint rather than a security control?**

**2. What other files might reveal a site's structure before you browse it?**

**3. How would you record the notes page so another analyst can reproduce your finding?**

**4. What is the difference between hiding a page and protecting a page?**

**5. What would you remove from the review page before publishing the site?**

## Defensive Takeaways

- Treat `robots.txt` as public documentation, not as a secret.
- Never put credentials, tokens, or internal notes in HTML comments.
- Remove review pages from production, not just from navigation.
- Review the full rendered source and static assets before launch.
- Assume any file served by the web server can be fetched directly.

## If You Get Stuck

- Confirm the hostname and port from the exercise panel.
- Try the dashboard first, then the people directory.
- Run `curl -s http://connect.lab:8080/robots.txt` and read every line.
- The flag is in the source, not in the visible text of the notes page.
