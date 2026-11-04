# Hidden Export Route

## Before You Begin

- [ ] Launched the **Hidden Export Route** exercise
- [ ] Opened the lab browser at `http://review.lab:8080`
- [ ] You know this portal is fictional and safe to explore
- [ ] You know you can pause, use a hint, or stop at any time

!!! note "Browser-only"
    You do not need a terminal, a VPN, or any installed tools. Viewing the page
    source is part of the exercise.

## Scenario

DevFest Windsor-Essex runs a small volunteer portal for speaker handoffs and
community-track exports. The organiser moved the speaker export to a new admin
console, but an old route was left in the JavaScript bundle.

Your job is to find the route, recover the flag, and explain why a secret
shipped to the browser is not a secret.

## Your Objectives

- Open the portal and find the JavaScript file
- Read the developer comment in the bundle
- Request the hidden export route with its token
- Recover the flag
- Explain the difference between client-side and server-side checks

## Background: The Browser Is Public

Anything the browser downloads can be read by the visitor. That includes HTML,
JavaScript, CSS, images, source maps, and API responses.

A hidden link, a disabled button, or a token in JavaScript is **not** access
control. The server must decide whether the request is allowed.

Common examples:

- an admin link hidden with CSS
- an API key embedded in a front-end bundle
- a `isAdmin` flag set in `localStorage`
- an export route left in a comment

## Walkthrough

### Step 1: Open the portal

```text
http://review.lab:8080
```

Read the page. The speaker export is described as "being moved" to a new admin
console.

### Step 2: Open the JavaScript

Choose **Open the portal JavaScript**, or view the page source and follow the
script link.

Look for a developer comment. It contains a temporary export route and token.

### Step 3: Request the route

Open the route in the browser. Use the route and token you found in the
JavaScript comment - do not guess them:

```text
http://review.lab:8080/admin/export?token=<token-from-the-bundle>
```

The export page returns the flag.

### Step 4: Submit the flag

Copy the `OCR{...}` value into the exercise flag box.

## What Just Happened?

The route was hidden, not protected. The token was shipped to every visitor in
the JavaScript bundle, so anyone who read the bundle could use it.

The fix is not to hide the route better. The fix is to enforce authorization on
the server and remove secrets from client-side code.

## Analysis Questions

**1. Why is a hidden route not the same as an authorized route?**

**2. What could an attacker do with the token if it were a real API key?**

**3. Why can a disabled button be bypassed?**

**4. Where should the authorization check live?**

**5. What would you search for in a front-end bundle during a code review?**

## Defensive Takeaways

- Treat everything sent to the browser as public.
- Enforce authorization on the server for every request.
- Do not put API keys, export tokens, or admin flags in front-end code.
- Remove temporary routes and comments before shipping.
- Add a test that requests the route without a valid session and expects 403.

## If You Get Stuck

- Re-read the page and follow the JavaScript link.
- Search the bundle for `admin`, `export`, or `token`.
- Copy the route exactly, including the query string.
- Ask a facilitator; using a hint is expected.

## Further Reading

- OWASP Top 10: Broken Access Control
- OWASP Cheat Sheet: Authorization
- MDN: View page source and the browser developer tools
