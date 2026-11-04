# VoIP Call Reconstruction

## Before You Begin

- [ ] Launched the exercise and can reach `http://voice.lab:8080`
- [ ] Downloaded `voip-call.pcap`
- [ ] You have Wireshark/tshark and Python 3, or RangeBox
- [ ] You know the call is fictional and safe to analyze
- [ ] If audio is unavailable, you know `transcript.txt` is the audio-free path

## Scenario

The help desk received a suspicious call. The network team captured the SIP
signalling and the RTP media stream before the caller hung up.

The packet list is mostly UDP. Your job is to separate the signalling from the
media, reconstruct the audio, listen to the message, and review the SIP headers
for the training token.

## Step 1: Download the capture

```bash
curl -O http://voice.lab:8080/voip-call.pcap
```

!!! note "Download the example capture"
    If you are reviewing this exercise without the lab, download the capture
    and reconstruction helper here:
    [voip-call.pcap](captures/voip-call.pcap) and
    [reconstruct.py](captures/reconstruct.py).

## Step 2: Find the signalling

Open the capture in Wireshark and filter for SIP:

```text
sip
```

You should see an `INVITE`, a `100 Trying`, a `200 OK`, an `ACK`, and a `BYE`.
Select the `INVITE` and expand the Session Description Protocol (SDP) body.

Look for:

```text
m=audio 40000 RTP/AVP 0
a=rtpmap:0 PCMU/8000
```

This says the caller offered audio on UDP port 40000 using payload type 0,
PCMU (G.711 u-law) at 8 kHz.

The `200 OK` chooses the server's RTP port, 40002.

## Step 3: Find the media

The audio is RTP on UDP port 40002. In Wireshark, you can use
**Telephony > VoIP Calls** or **Statistics > RTP** to see the stream.

With tshark, tell the RTP dissector which port to use:

```bash
tshark -r voip-call.pcap -d udp.port==40002,rtp -Y rtp \
  -T fields -e rtp.payload
```

Each line is a hex-encoded RTP payload. The payload is 160 bytes for a 20 ms
G.711 frame.

## Step 4: Rebuild the audio

### Option A: use the helper

The evidence package includes a small reconstruction script:

```bash
curl -O http://voice.lab:8080/reconstruct.py
python3 reconstruct.py voip-call.pcap call.wav
```

The script:

1. walks the pcap records;
2. keeps UDP packets sent to port 40002;
3. removes the 12-byte RTP header;
4. converts the G.711 u-law bytes to 16-bit PCM;
5. writes an 8 kHz mono WAV file.

### Option B: build it yourself

```bash
tshark -r voip-call.pcap -d udp.port==40002,rtp -Y rtp \
  -T fields -e rtp.payload \
  | tr -d '\n' \
  | xxd -r -p > call.ulaw

ffmpeg -f mulaw -ar 8000 -ac 1 -i call.ulaw call.wav
```

If you do not have ffmpeg, `sox` can also read raw u-law:

```bash
sox -t ul -r 8000 -c 1 call.ulaw call.wav
```

## Step 5: Listen and read the signalling

Play `call.wav`. The caller says where the training token is stored.

!!! note "Audio-free path"
    If you cannot play or hear the recording, download
    `http://voice.lab:8080/transcript.txt`. It contains the spoken message
    and points you at the same SIP evidence. The transcript does not contain
    the flag itself.

Then return to the SIP `INVITE` and read the headers. The `Subject` header
contains the `OCR{...}` token.

Copy it into the flag box.

## What Just Happened?

You separated signalling from media, identified the codec and port from SDP,
extracted the RTP payload, and rebuilt the audio. Then you used the signalling
metadata to finish the investigation.

Real VoIP investigations often combine:

- call detail records;
- SIP logs;
- RTP captures;
- voicemail and transcript stores;
- endpoint and network logs.

## Defensive Lessons

- Encrypt voice signalling and media where the platform supports it (for
  example, SIP over TLS and SRTP).
- Restrict capture access; a voice capture is personal information.
- Protect voicemail and call-recording stores like any other sensitive data.
- Log call metadata without logging content unless policy allows it.

## Analysis Questions

**1. What is the difference between SIP and RTP?**

**2. What does the SDP body tell you before you extract any audio?**

**3. Why is G.711 audio easy to reconstruct from RTP?**

**4. What could an investigator learn from the signalling even without the audio?**

**5. Which controls would make a real call harder to intercept?**
