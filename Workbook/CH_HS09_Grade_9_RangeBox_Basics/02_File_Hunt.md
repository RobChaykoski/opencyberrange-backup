# RangeBox File Hunt

## Before You Begin

- [ ] Completed RangeBox First Steps, or know how to open a terminal
- [ ] You can reach `http://files.lab:8080`
- [ ] You have not downloaded any real personal files

## Scenario

A class shared folder was exported before a cleanup. The archive is full of
ordinary notes, a few decoys, and one file that contains the training token.

Your job is to find the real token without opening every file by hand. This is
the same pattern investigators use when they triage a folder of evidence:
narrow the list first, then read the file that matters.

## Walkthrough

### Step 1: Download the archive

In the RangeBox terminal, run:

```bash
curl -O http://files.lab:8080/evidence.zip
```

`-O` tells curl to save the file with the same name as the remote file.

### Step 2: Unpack the archive

```bash
unzip evidence.zip
ls evidence
```

You should see a folder named `evidence` with several subfolders.

### Step 3: Read the archive README

```bash
cat evidence/README.txt
```

The README explains which subfolder holds the real token. Read it before opening
random files.

### Step 4: List the files

```bash
find evidence -type f
```

`find` lists files by walking the folder tree. `-type f` means "files only".

### Step 5: Search for the token

```bash
grep -R "OCR{" evidence
```

`grep` searches file contents. `-R` means "recurse into subfolders". You will see
a decoy token and the real token.

### Step 6: Read the real file

The README says the real token is in `archive/old/flag.txt`:

```bash
cat evidence/archive/old/flag.txt
```

Copy the `OCR{...}` value into the flag box.

## What Just Happened?

- `curl -O` downloaded a file.
- `unzip` expanded a ZIP archive.
- `find` narrowed a large folder to a list of files.
- `grep` searched the contents of those files.

Filenames alone are not evidence. A file named `notes.txt` can contain anything,
and a decoy can be named to look important. Read the content and check the
context.

## Analysis Questions

**1. Why did the README matter before running `grep`?**

**2. What is the difference between `find` and `grep`?**

**3. Why might an investigator list files before opening them?**

**4. What could happen if you trusted a filename without reading the file?**

**5. How would you remove the decoy from your results?**
