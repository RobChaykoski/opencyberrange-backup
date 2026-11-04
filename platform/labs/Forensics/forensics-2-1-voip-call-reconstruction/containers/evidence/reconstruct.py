#!/usr/bin/env python3
"""Reconstruct the G.711 u-law audio from the VoIP capture.

Usage:
    python3 reconstruct.py voip-call.pcap call.wav

The script walks the pcap records, finds UDP packets sent to the server's RTP
port (40002), strips the 12-byte RTP header, and writes the payload as a mono
8 kHz WAV file.
"""
import audioop
import struct
import sys
import wave

RTP_PORT = 40002


def packets(path):
    with open(path, "rb") as handle:
        header = handle.read(24)
        if len(header) < 24:
            raise SystemExit("not a pcap file")
        magic = header[:4]
        if magic == b"\xd4\xc3\xb2\xa1":
            endian = "<"
        elif magic == b"\xa1\xb2\xc3\xd4":
            endian = ">"
        else:
            raise SystemExit("only classic pcap files are supported")
        while True:
            record = handle.read(16)
            if len(record) < 16:
                break
            seconds, fraction, incl_len, _orig_len = struct.unpack(endian + "IIII", record)
            data = handle.read(incl_len)
            if len(data) < incl_len:
                break
            yield seconds + fraction / 1_000_000, data


def udp_payload(data):
    if len(data) < 20 + 8:
        return None
    # The capture is raw IPv4 (pcap linktype 228), but accept Ethernet too so
    # the same helper works with a re-exported capture.
    if len(data) >= 14 and data[12:14] in (b"\x08\x00", b"\x81\x00"):
        offset = 14
        if data[12:14] == b"\x81\x00":
            offset += 4
    elif data[0] >> 4 == 4:
        offset = 0
    else:
        return None
    ip = data[offset:]
    ihl = (ip[0] & 0x0F) * 4
    if len(ip) < ihl + 8 or ip[9] != 17:
        return None
    udp = ip[ihl:]
    src_port, dst_port, length = struct.unpack("!HHH", udp[:6])
    if dst_port != RTP_PORT:
        return None
    payload = udp[8:length]
    if len(payload) <= 12:
        return None
    return src_port, payload[12:]


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python3 reconstruct.py voip-call.pcap call.wav")
    source, output = sys.argv[1], sys.argv[2]
    audio = bytearray()
    count = 0
    for _when, data in packets(source):
        result = udp_payload(data)
        if result:
            _src_port, payload = result
            audio.extend(payload)
            count += 1
    if not audio:
        raise SystemExit("no RTP payload found on UDP port 40002")
    pcm = audioop.ulaw2lin(bytes(audio), 2)
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(pcm)
    print(f"wrote {output}: {count} RTP packets, {len(audio)} bytes u-law, {len(audio)/8000:.1f}s")


if __name__ == "__main__":
    main()
