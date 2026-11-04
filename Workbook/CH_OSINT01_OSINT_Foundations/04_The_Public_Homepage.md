# Exercise 2.2: The Public Homepage

## Before You Begin

- [ ] You can reach `https://www.swocts.com` from your browser or terminal
- [ ] If you are working offline, you can reach the mirror at
      `http://connect.lab:8080`
- [ ] You have `curl` and `grep`

## Scenario

SWOCTS Hub is the public home of the Southwestern Ontario Cybersecurity
community. Like any modern site, it ships metadata and source code to every
visitor.

A flag has been placed in the site's source for this exercise. The rendered
page looks ordinary; the flag is in the document metadata.

The live target is **https://www.swocts.com**. A local mirror is available at
`http://connect.lab:8080` for offline practice and validation. Use the live
site when you can, then confirm the same technique against the mirror.

## Your Objectives

- Treat a public homepage as an OSINT source
- Fetch the page source instead of only reading the rendered page
- Search metadata and comments for a hidden marker
- Record the exact URL and source location of the finding

## Background: The Head Is Part of the Page

A modern homepage is more than its visible text. The document `<head>` can
contain:

- `<title>` and description metadata
- social-sharing cards (`og:` and `twitter:` tags)
- framework build identifiers
- custom `meta` tags used by internal tools
- analytics and verification tokens

Most visitors never see the head. An OSINT researcher reads it.

## Walkthrough

### Step 1: Open the live site

Browse to:

```text
https://www.swocts.com
```

Use **View Page Source** (not the browser's rendered text view). If you are
working offline, open the mirror:

```text
http://connect.lab:8080
```

### Step 2: Fetch the source

```bash
curl -s https://www.swocts.com/ -o swocts.html
```

If the live site is unavailable, use the mirror:

```bash
curl -s http://connect.lab:8080/ -o swocts.html
```

### Step 3: Search the head

```bash
grep -i 'OCR{\|osint\|meta name' swocts.html
```

The flag is in a custom `meta` tag in the document head. It is not visible in
the rendered page.

### Step 4: Submit the flag

Copy the `OCR{...}` value into the exercise flag box. Record the URL and the
exact tag you found so another analyst can reproduce the finding.

## What Just Happened?

The site owner left a marker in the public source. This is not a
vulnerability; it is a deliberate OSINT breadcrumb. The lesson is that the
public surface includes metadata, comments, and build artifacts that never
appear in the visible page.

The same technique applies to any public site: fetch the source, read the
head, and search for identifiers that should not be there.

## Analysis Questions

**1. Why is a `meta` tag a good place for a deliberate OSINT clue?**

**2. What kinds of real secrets are sometimes leaked in page metadata?**

**3. How would you archive the page so the finding is reproducible after the site changes?**

**4. What is the difference between viewing the rendered page and viewing the source?**

**5. How would you report a real metadata leak without publishing the secret?**

## Defensive Takeaways

- Treat metadata as public content and review it before launch.
- Strip internal build identifiers and staging markers from production.
- Do not put secrets in `meta` tags, comments, or source maps.
- Include the document head in launch checklists and security reviews.
- Monitor public source changes if your site is a high-value target.

## If You Get Stuck

- Make sure you are looking at the source, not the rendered text.
- Search for `OCR{`, `osint`, or `meta name`.
- If the live site is blocked, use the mirror at `http://connect.lab:8080`.
- The flag is in a custom `meta` tag in the head.
