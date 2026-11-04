#!/usr/bin/env python3
"""Generate the VoIP call-reconstruction capture.

This file is kept for reproducibility. The committed capture is the artifact
students analyze; the generator is not shipped in the evidence container.
"""
import audioop
import os
import struct
import wave

from scapy.all import IP, UDP, Raw, wrpcap
from scapy.layers.rtp import RTP

FLAG = "OCR{v01c3_c4ll_r3c0n}"
CALLER = "10.10.30.15"
SERVER = "10.10.30.80"
CALLER_SIP_PORT = 5060
SERVER_SIP_PORT = 5060
CALLER_RTP_PORT = 40000
SERVER_RTP_PORT = 40002
SSRC = 0x1A2B3C4D
HERE = os.path.dirname(os.path.abspath(__file__))
WAV = os.path.join(HERE, "voice.wav")
OUT = os.path.join(HERE, "voip-call.pcap")


def load_ulaw(path):
    with wave.open(path, "rb") as wav:
        width = wav.getsampwidth()
        channels = wav.getnchannels()
        rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    if width != 2:
        raise SystemExit("expected 16-bit PCM")
    if channels > 1:
        frames = audioop.tomono(frames, 2, 0.5, 0.5)
    if rate != 8000:
        frames, _ = audioop.ratecv(frames, 2, 1, rate, 8000, None)
    return audioop.lin2ulaw(frames, 2)


def sip(payload, src, dst, sport, dport):
    return IP(src=src, dst=dst) / UDP(sport=sport, dport=dport) / Raw(load=payload)


def main():
    ulaw = load_ulaw(WAV)
    packets = []

    invite = (
        "INVITE sip:helpdesk@voice.lab SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP {CALLER}:{CALLER_SIP_PORT};branch=z9hG4bK-ocr-1\r\n"
        "Max-Forwards: 70\r\n"
        "From: <sip:caller@voice.lab>;tag=ocr-caller\r\n"
        "To: <sip:helpdesk@voice.lab>\r\n"
        "Call-ID: ocr-voice-2026@voice.lab\r\n"
        "CSeq: 1 INVITE\r\n"
        f"Contact: <sip:caller@{CALLER}:{CALLER_SIP_PORT}>\r\n"
        f"Subject: {FLAG}\r\n"
        "Content-Type: application/sdp\r\n"
        "Content-Length: 151\r\n"
        "\r\n"
        "v=0\r\n"
        f"o=caller 2026 2026 IN IP4 {CALLER}\r\n"
        "s=Training call\r\n"
        f"c=IN IP4 {CALLER}\r\n"
        "t=0 0\r\n"
        f"m=audio {CALLER_RTP_PORT} RTP/AVP 0\r\n"
        "a=rtpmap:0 PCMU/8000\r\n"
    )
    packets.append(sip(invite, CALLER, SERVER, CALLER_SIP_PORT, SERVER_SIP_PORT))

    trying = (
        "SIP/2.0 100 Trying\r\n"
        f"Via: SIP/2.0/UDP {CALLER}:{CALLER_SIP_PORT};branch=z9hG4bK-ocr-1\r\n"
        "From: <sip:caller@voice.lab>;tag=ocr-caller\r\n"
        "To: <sip:helpdesk@voice.lab>\r\n"
        "Call-ID: ocr-voice-2026@voice.lab\r\n"
        "CSeq: 1 INVITE\r\n"
        "Content-Length: 0\r\n\r\n"
    )
    packets.append(sip(trying, SERVER, CALLER, SERVER_SIP_PORT, CALLER_SIP_PORT))

    ok = (
        "SIP/2.0 200 OK\r\n"
        f"Via: SIP/2.0/UDP {CALLER}:{CALLER_SIP_PORT};branch=z9hG4bK-ocr-1\r\n"
        "From: <sip:caller@voice.lab>;tag=ocr-caller\r\n"
        "To: <sip:helpdesk@voice.lab>;tag=ocr-server\r\n"
        "Call-ID: ocr-voice-2026@voice.lab\r\n"
        "CSeq: 1 INVITE\r\n"
        f"Contact: <sip:helpdesk@{SERVER}:{SERVER_SIP_PORT}>\r\n"
        "Content-Type: application/sdp\r\n"
        "Content-Length: 150\r\n"
        "\r\n"
        "v=0\r\n"
        f"o=server 2026 2026 IN IP4 {SERVER}\r\n"
        "s=Training call\r\n"
        f"c=IN IP4 {SERVER}\r\n"
        "t=0 0\r\n"
        f"m=audio {SERVER_RTP_PORT} RTP/AVP 0\r\n"
        "a=rtpmap:0 PCMU/8000\r\n"
    )
    packets.append(sip(ok, SERVER, CALLER, SERVER_SIP_PORT, CALLER_SIP_PORT))

    ack = (
        "ACK sip:helpdesk@voice.lab SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP {CALLER}:{CALLER_SIP_PORT};branch=z9hG4bK-ocr-2\r\n"
        "From: <sip:caller@voice.lab>;tag=ocr-caller\r\n"
        "To: <sip:helpdesk@voice.lab>;tag=ocr-server\r\n"
        "Call-ID: ocr-voice-2026@voice.lab\r\n"
        "CSeq: 1 ACK\r\n"
        "Content-Length: 0\r\n\r\n"
    )
    packets.append(sip(ack, CALLER, SERVER, CALLER_SIP_PORT, SERVER_SIP_PORT))

    sequence = 1000
    timestamp = 0
    for offset in range(0, len(ulaw), 160):
        payload = ulaw[offset:offset + 160]
        packets.append(
            IP(src=CALLER, dst=SERVER)
            / UDP(sport=CALLER_RTP_PORT, dport=SERVER_RTP_PORT)
            / RTP(version=2, padding=0, extension=0, numsync=0, marker=0,
                  payload_type=0, sequence=sequence, timestamp=timestamp,
                  sourcesync=SSRC)
            / Raw(load=payload)
        )
        sequence += 1
        timestamp += 160

    bye = (
        "BYE sip:helpdesk@voice.lab SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP {CALLER}:{CALLER_SIP_PORT};branch=z9hG4bK-ocr-3\r\n"
        "From: <sip:caller@voice.lab>;tag=ocr-caller\r\n"
        "To: <sip:helpdesk@voice.lab>;tag=ocr-server\r\n"
        "Call-ID: ocr-voice-2026@voice.lab\r\n"
        "CSeq: 2 BYE\r\n"
        "Content-Length: 0\r\n\r\n"
    )
    packets.append(sip(bye, CALLER, SERVER, CALLER_SIP_PORT, SERVER_SIP_PORT))

    wrpcap(OUT, packets)
    print(f"wrote {OUT}: {len(packets)} packets, {len(ulaw)} bytes of u-law audio")


if __name__ == "__main__":
    main()
