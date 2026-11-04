# Digital Forensics — Memory Forensics

## Welcome

Memory forensics is the study of a computer's volatile memory: the running
processes, network connections, loaded modules, and sometimes credentials that
exist only while a system is powered on.

This chapter uses a Windows Server 2008 training image and Volatility 3, an
open-source memory-analysis framework. You will work on an isolated analyst
workstation, so the evidence stays inside the lab.

## Why Memory Matters

Disk evidence shows what was stored. Memory evidence can show what was running:

- which processes were active;
- which accounts were logged in;
- which network connections were open;
- which commands had been typed;
- which credentials or tokens were in use.

Memory is fragile. It changes constantly and disappears when the machine loses
power. Investigators capture it early and preserve the image exactly as it was
acquired.

## Evidence Handling

- Treat the memory image as read-only evidence.
- Do not edit, rename, or overwrite the image.
- Record the commands you run and the output you rely on.
- Do not copy real credentials or personal data out of the lab.
- This image is a training sample; the accounts are not real production
  credentials.

## What You Need

- A browser and the exercise panel
- A RangeBox desktop, or a terminal with SSH
- The analyst workstation credentials from the lab page

## Activity

[Windows Memory Analysis with Volatility](01_Windows_Memory_Volatility.md)

## Attribution

The training memory image comes from Sam Bowne's Windows Server 2008 memory
analysis exercise at [samsclass.info](https://samsclass.info/121/proj/p5-Vol.htm).
It is used here for isolated classroom training.
