# Exercise 1.2: Badge Photo Intelligence

## Before You Begin

- [ ] Launched the exercise and opened the lab browser or a terminal
- [ ] You can reach `http://connect.lab:8080/people/dana.whitfield`
- [ ] You have a shell with `curl` and Python 3

## Scenario

People Security refreshed the Kestrel Ridge badge photos last week. Dana
Whitfield's profile still points at the old export, and the file is served
from the intranet with no access control.

A badge photo should contain a face and a name. This one also contains a
message that was never meant to be visible.

![Dana Whitfield badge photo](img/dana-badge.png)

## Your Objectives

- Download the image without altering its bytes
- Inspect the PNG metadata for context
- Recognise least-significant-bit steganography
- Extract the hidden payload and recover the flag

## Background: Metadata and Steganography

There are two different ways to hide data in an image:

**Metadata** lives beside the pixels. PNG text chunks and JPEG/TIFF EXIF
fields can carry camera model, software, comments, and GPS data. Metadata is
easy to inspect with `exiftool` and `strings`.

**Steganography** changes the pixels themselves. A common technique is
**least-significant-bit (LSB) embedding**: each pixel's lowest bit is replaced
with one bit of the secret. The colour change is usually invisible to the eye,
but the data survives lossless formats such as PNG.

A simple LSB payload often starts with a magic marker and a length, followed
by the secret. If you know the marker, you can scan the low bits of a colour
channel and rebuild the message.

## Walkthrough

### Step 1: Download the badge photo

```bash
curl -s http://connect.lab:8080/assets/badge.png -o badge.png
```

Do not re-save the image in a photo editor before analysis. Some editors
rewrite the pixel data and destroy the hidden payload.

### Step 2: Look at the file and its metadata

```bash
file badge.png
exiftool badge.png
strings badge.png | head -20
```

The metadata gives useful context: employee name, badge ID, and the photo
booth software. The flag is not stored in the metadata. This is a deliberate
distinction: metadata is the decoy, the pixels are the message.

### Step 3: Try the standard stego tools

If `zsteg` is available:

```bash
zsteg -a badge.png
```

`zsteg` tries several bit planes and channels. The payload is in the blue
channel's least significant bit, written from the top-left pixel onward.

If you do not have `zsteg`, the intranet serves a dependency-free extractor:

```bash
curl -s http://connect.lab:8080/tools/extract_lsb.py -o extract_lsb.py
python3 extract_lsb.py badge.png
```

The extractor reads the PNG chunk stream, decompresses the pixel data, reads
the blue-channel LSBs, and prints the payload. It uses only the Python
standard library.

**No terminal or low-bandwidth route:** open
`http://connect.lab:8080/tools/extract.html` in the lab browser, choose the
badge image, and read the result on the page. The extraction happens inside
the browser tab; the image is not uploaded to a third-party service. This is
the recommended route on a Chromebook, tablet, or shared computer without
local tools.

### Step 4: Submit the flag

Copy the `OCR{...}` value printed by the extractor into the exercise flag box.

## What Just Happened?

The image looked normal because the visible pixels barely changed. A single
bit per pixel is enough to store thousands of characters in a small badge
photo.

This is why "it is just an image" is not a safe assumption. Images can carry
metadata, appended archives, hidden bit planes, or a second file after the
end-of-image marker.

## Analysis Questions

**1. Why does re-saving a PNG in an image editor often destroy an LSB payload?**

**2. What is the difference between metadata and pixel data?**

**3. How could you detect that an image has been modified without knowing the payload?**

**4. Why is PNG a better container than JPEG for exact LSB embedding?**

**5. What would you do if a public image contained a real credential?**

## Defensive Takeaways

- Strip metadata before publishing images.
- Re-encode images through a trusted pipeline if they must be public.
- Do not treat an image as inert data; scan it like any other uploaded file.
- Store sensitive data in an access-controlled system, not in a public asset.
- Keep badge photos and other identity images out of unauthenticated paths.

## If You Get Stuck

- Check that you downloaded the file from `/assets/badge.png` and did not
  rename a screenshot.
- Run `file badge.png`; it should report a PNG image.
- If `zsteg` is missing, use the served `extract_lsb.py` or the browser
  extractor at `/tools/extract.html`.
- The payload starts at the top-left pixel and uses the blue channel.
