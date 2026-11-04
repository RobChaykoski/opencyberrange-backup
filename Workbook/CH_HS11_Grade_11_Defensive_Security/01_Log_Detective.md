# Exercise 11.1 -- Log Detective

!!! note "Lab"
    Launch **RangeBox Log Detective** in the platform before starting. You can use
    the RangeBox desktop or the lab browser, with a terminal if you have one.

## Background

A web server access log records what the server received and how it responded.
Each line usually contains:

- the source address;
- the date and time;
- the requested path;
- the HTTP status code;
- the number of bytes returned;
- the user agent.

You do not need to memorise the whole line. Start with the status code and the
requested path, then look for repeats.

## Tool Primer

### `curl`

```bash
curl http://logs.lab:8080/access.log
```

Downloads the log and prints it in the terminal.

### `grep`

```bash
grep " 404 " access.log
```

Shows only lines containing the text `404`. Quoting the spaces makes the match
more specific so a number such as `14045` does not accidentally match.

```bash
grep "OCR{" access.log
```

Searches the log for text in the training-token format.

## Walkthrough

### Step 1: Launch the exercise

Open **RangeBox Log Detective** and wait for the lab to show **Running**. Start
RangeBox, or open the lab browser.

### Step 2: Download the log

In a terminal:

```bash
curl http://logs.lab:8080/access.log -o access.log
```

Or open `http://logs.lab:8080/access.log` in the lab browser and save the page.

### Step 3: Separate normal traffic from failures

Look at the status codes first:

```bash
grep " 200 " access.log
grep " 404 " access.log
```

Most normal page views return **200**. The failed requests return **404**.

**Record:**

| Question | Your answer |
|---|---|
| Which source address made the repeated failed requests? | |
| Which paths did that source try? | |
| What user agent did it use? | |

### Step 4: Find the request that succeeded

Filter the log for the source address you found in Step 3. One of its requests
returned **200** and includes an unusual query string.

```bash
grep "<source_address>" access.log
```

The successful request carries a training token in `OCR{...}` format.

**Record:** the path and query string from that request.

### Step 5: Capture the flag

Copy the full token, including `OCR{` and `}`, and submit it in the platform.

## Analysis Questions

**1. What makes the repeated 404 requests stand out from the normal traffic?**

**2. Why is a successful request from the same source more interesting than the failed requests alone?**

**3. What would you recommend the service owner check first after reading this log?**

**4. What can this log not tell you about the event?**

**5. Why is it important to quote the spaces in `grep " 404 "`?**

## Key Takeaways

- Access logs record requests, responses, and source addresses.
- Status codes help you separate normal responses from failed requests.
- Patterns across several lines are stronger evidence than a single line.
- A log is evidence, but it is not the whole investigation.
- Good defensive work ends with a clear explanation and a small next step.

## Next Step

Continue to **Grade 12 Applied Cybersecurity** to use browser-only investigation
skills in a community event scenario.
