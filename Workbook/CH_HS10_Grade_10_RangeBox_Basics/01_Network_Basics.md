# RangeBox Network Basics

## Before You Begin

- [ ] Launched RangeBox and opened a terminal
- [ ] You can reach `http://network.lab:8080/status.json`
- [ ] You know how to copy the `OCR{...}` token into the flag box

## Scenario

A small classroom service reports whether it is healthy. The page says very
little, but the response headers carry a training token for this exercise.

You will use RangeBox to ask the service for its status and then read the whole
response, not just the body.

## Walkthrough

### Step 1: Ask for the status page

In the RangeBox terminal, run:

```bash
curl -i http://network.lab:8080/status.json
```

The `-i` option tells curl to show the response headers as well as the body.

### Step 2: Read the response from top to bottom

You should see something like:

```text
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 120
X-OCR-Token: OCR{...}

{"service": "rangebox-basics", "status": "ok"}
```

Read it in this order:

1. **Status line** — did the request succeed?
2. **Headers** — what did the server send with the body?
3. **Blank line** — the headers are finished.
4. **Body** — the content itself.

### Step 3: Filter for the token header

If the output is hard to read, ask for only the headers and filter them:

```bash
curl -s -D - -o /dev/null http://network.lab:8080/status.json | grep -i x-ocr-token
```

`-D -` writes the headers to standard output. `-o /dev/null` discards the body.
`grep -i` ignores case.

Copy the value after `X-OCR-Token:` into the flag box.

## What Just Happened?

The token was never in the page body. It was in a response header, which the
browser normally hides in its developer tools.

Response headers can reveal:

- the server and framework;
- caching behaviour;
- security settings;
- custom metadata or tokens.

This is why analysts read the whole response during troubleshooting and
incident triage.

## Analysis Questions

**1. What is the difference between a status line, a header, and a body?**

**2. Why might a browser hide response headers from a normal user?**

**3. What does `curl -i` add to the output?**

**4. What does `-o /dev/null` do in the filtering command?**

**5. Why is a custom header a poor place to store a real secret?**
