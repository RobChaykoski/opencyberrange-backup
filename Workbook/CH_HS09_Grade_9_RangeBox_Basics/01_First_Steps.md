# RangeBox First Steps

## Before You Begin

- [ ] Launched RangeBox and opened a terminal
- [ ] You know you can use hints at any time
- [ ] You have a place to write down the commands you try

!!! note "This is a safe place to start"
    You do not need any prior experience. The practice target is fictional, you
    cannot break it, and using hints is expected.

## Scenario

Your class is starting its first hands-on cybersecurity unit. Before you
investigate anything, you need to know how to move around the training desktop.

In this activity you will open RangeBox, start a terminal, run four basic
commands, and retrieve a welcome file from a practice server.

## Walkthrough

### Step 1: Start RangeBox

Launch the exercise and choose **Launch RangeBox**. Pick the **Kali** desktop.
When the desktop appears, open the terminal.

### Step 2: Find out where you are

Run:

```bash
pwd
```

You should see a path such as `/home/kali`. That is your current folder.

### Step 3: Find out who you are

Run:

```bash
whoami
```

You should see your RangeBox account name. This is the account you are using
inside the training desktop, not your OpenCyberRange login.

### Step 4: Look at the current folder

Run:

```bash
ls
```

You may see folders such as `Desktop`, `Documents`, and `Downloads`. `ls` lists
what is in the folder you are currently in.

### Step 5: Retrieve the welcome file

Run:

```bash
curl http://rangebox.lab:8080/welcome.txt
```

`curl` requests a URL and prints the response. The welcome file contains a line
that starts with `Training token:`. Copy the `OCR{...}` value into the flag box.

## If You Do Not Have RangeBox

Open the lab browser and visit:

```text
http://rangebox.lab:8080/welcome.txt
```

You will see the same file. The commands are worth learning, but the browser
path lets you finish the activity on a device without a terminal.

## What Just Happened?

- `pwd` told you your location in the file system.
- `whoami` told you which account you are using.
- `ls` listed the current folder.
- `curl` asked a web server for a file and printed the response.

These are the same basic steps you will use in later labs: find out where you
are, find out what you have, and ask a service for information.

## Analysis Questions

**1. What is the difference between the RangeBox account and your OpenCyberRange account?**

**2. Why is it useful to run `pwd` before opening a file?**

**3. What does `curl` do, in one sentence?**

**4. Which command would you use to list the files in a folder?**

**5. What would you try first if a command printed an error?**
