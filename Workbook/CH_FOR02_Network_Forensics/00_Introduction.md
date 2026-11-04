# Digital Forensics — Network Forensics

## Welcome

Network forensics is the study of captured traffic: who talked to whom, when,
over which protocol, and what the conversation contained.

This chapter starts with voice over IP (VoIP). A VoIP call has two parts:

- **SIP** — the signalling. It sets up, changes, and ends the call.
- **RTP** — the media. It carries the audio in small packets.

Reconstructing a call means separating the two, rebuilding the audio, and then
reading the signalling for context.

## Why Voice Traffic Matters

Voice is data. A call can contain:

- personal information;
- financial details;
- credentials read aloud;
- instructions or threats;
- evidence of a scam or impersonation.

Voice traffic is also easy to overlook because it is UDP and often on unusual
ports. A packet capture preserves it for careful review.

## Evidence Handling

- Work from a copy of the capture.
- Record the filter or command that produced each finding.
- Do not upload the capture to a third-party service.
- The audio in this lab is synthesized and the people are fictional.
- Treat a real call recording as personal information.

## What You Need

- A browser and the exercise panel
- A RangeBox desktop, or a terminal with Wireshark/tshark and Python 3

## Activity

[VoIP Call Reconstruction](01_VoIP_Call_Reconstruction.md)
