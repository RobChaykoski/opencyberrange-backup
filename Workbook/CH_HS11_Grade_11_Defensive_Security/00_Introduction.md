# High School Cybersecurity — Grade 11 Defensive Security

## Welcome

In Grade 9 you learned to move around the RangeBox desktop and find files. In
Grade 10 you looked at how names, addresses, and web responses fit together. In
Grade 11 you switch to the defender's side: reading the records a service leaves
behind and explaining what happened.

You do not need to install anything. The activity works in RangeBox or the lab
browser, and hints are always allowed.

## What You Need

- A browser
- The exercise panel open in OpenCyberRange
- A RangeBox desktop, or the lab browser as a fallback

## Three Ideas to Carry Forward

### 1. A log is evidence

Servers write down what they saw: who connected, what they asked for, and how the
server answered. A log is not the whole story, but it is often the first useful
record.

### 2. Status codes tell you what happened

A **200** response means the request succeeded. A **404** means the server could
not find the requested page. Repeated 404s from one address can be a sign that
someone is guessing at paths.

### 3. Patterns matter more than single lines

One failed request is usually noise. A burst of failures from one source,
followed by a successful request that should not exist, is a pattern worth
explaining.

## Your Activity

[Log Detective](01_Log_Detective.md) — read a short access log, separate normal
traffic from probing, and recover the training token.

## How to Work Safely

- The service and the log are fictional.
- You are reading evidence, not attacking a real system.
- Do not paste real names, real addresses, or personal information into your
  answers.
- If something looks like a real secret outside this exercise, stop and tell your
  teacher.

## The Defensive Loop

1. **Read** the record carefully.
2. **Separate** normal activity from unusual activity.
3. **Explain** what the evidence supports and what it does not.
4. **Recommend** a small, responsible next step.
