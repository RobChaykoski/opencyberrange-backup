# High School Cybersecurity — Grade 10 RangeBox Basics

## Welcome

In Grade 9 you learned to move around the RangeBox desktop. This chapter adds
the network view: how a name becomes an address, how a browser asks a server for
a page, and how to read the response.

You still do not need to install anything. The activities work in RangeBox, and
the lab browser is available as a fallback.

## What You Need

- A browser
- The exercise panel open in OpenCyberRange
- A RangeBox desktop, or the lab browser as a fallback

## Three Ideas to Carry Forward

### 1. A hostname is a name

`network.lab` is a hostname. It is easier to remember than a number. The lab
network resolves that name to the target container for you.

### 2. A URL has parts

```text
http://network.lab:8080/status.json
```

- `http` is the scheme.
- `network.lab` is the host.
- `8080` is the port.
- `/status.json` is the path.

### 3. A response has more than a body

A web response includes:

- a status line, such as `HTTP/1.1 200 OK`;
- headers, such as `Content-Type` and `X-OCR-Token`;
- a blank line;
- the body.

The body is what the page shows. The headers are the part people often forget
to read.

## Activities

1. [RangeBox Network Basics](01_Network_Basics.md)
2. [RangeBox Browser and Source](02_Browser_and_Source.md)

## Safety Reminder

Every target in this chapter is fictional and isolated. You cannot affect
anything outside the lab. Using hints is allowed, and you can stop at any time.
