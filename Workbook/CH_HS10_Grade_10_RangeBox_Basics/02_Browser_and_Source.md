# RangeBox Browser and Source

## Before You Begin

- [ ] Launched RangeBox and opened the browser
- [ ] You can reach `http://web.lab:8080/staff-notes.html`
- [ ] You know that the page is fictional and safe

## Scenario

A staff notes page looks almost empty. The visible page is not the whole
document, though: the browser also received HTML comments that are not shown on
screen.

You will open the page in RangeBox, view its source, and find the training token
in a comment.

## Walkthrough

### Step 1: Open the page

In the RangeBox browser, visit:

```text
http://web.lab:8080/staff-notes.html
```

The page looks almost empty. That is intentional.

### Step 2: View the page source

Right-click the page and choose **View Page Source**, or press `Ctrl+U`.

You will see the HTML that the browser received. Look for text between `<!--`
and `-->`. That is an HTML comment.

### Step 3: Find the token

The comment near the end of the document contains a line like:

```html
<!-- Training token: OCR{...} -->
```

Copy the `OCR{...}` value into the flag box.

### Step 4: Try the same thing with curl

In the RangeBox terminal, run:

```bash
curl http://web.lab:8080/staff-notes.html
```

You will see the same document. The browser and the terminal received the same
HTML; the browser simply chose not to display the comments.

## What Just Happened?

HTML comments are useful for developers, but they are not secret. Anyone who
views the source can read them. Comments can leak:

- internal notes;
- test data;
- file paths;
- tokens or passwords;
- information about unfinished features.

The defensive habit is simple: review the source before publishing a page, and
do not put sensitive information in comments.

## Optional: Check robots.txt

Visit:

```text
http://web.lab:8080/robots.txt
```

`robots.txt` is a request to well-behaved crawlers. It is not an access control
system. A page listed as disallowed can still be opened by a person.

## Analysis Questions

**1. What is the difference between what the browser displays and the HTML source?**

**2. Why are HTML comments easy to overlook?**

**3. What kinds of information should never appear in a comment?**

**4. Does `robots.txt` stop a person from opening a page? Why or why not?**

**5. How would you check a page before publishing it?**
