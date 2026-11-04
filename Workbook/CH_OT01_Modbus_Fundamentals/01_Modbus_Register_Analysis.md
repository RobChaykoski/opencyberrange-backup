# Exercise 1.1: Modbus Register Analysis

## Before You Begin

- [ ] Launched the exercise and opened the REMnux/RangeBox desktop
- [ ] A terminal open
- [ ] The **PLC** address from the panel
- [ ] `python3`, `nmap`, `mbpoll` available

## Scenario

Halcyon Industrial Controls operates a small process line. An analyst captured
a Modbus TCP conversation and noticed the controller's holding registers contain
more than setpoints. The controller is online in the lab.

Modbus has no authentication and no encryption. Your job is to enumerate the
device, read the holding registers, and recover the analyst marker.

## Your Objectives

- Discover the Modbus TCP service
- Read the holding register map
- Decode the ASCII marker stored in consecutive registers

## Background: Modbus TCP

Modbus is a request/response protocol. A master sends a function code and
address; the slave responds with data. Common function codes:

| Code | Name |
|------|------|
| 0x01 | Read Coils |
| 0x02 | Read Discrete Inputs |
| 0x03 | Read Holding Registers |
| 0x04 | Read Input Registers |
| 0x05 | Write Single Coil |
| 0x06 | Write Single Register |

The Modbus TCP frame (MBAP + PDU):

```
Transaction ID (2) | Protocol ID (2) | Length (2) | Unit ID (1) | Function (1) | ...
```

Protocol ID is 0 for Modbus TCP. Each register is 16 bits.

## Walkthrough

### Step 1: Discover the Service

```bash
nmap -sV -p 502 <plc_ip>
```

### Step 2: Read Holding Registers with mbpoll

```bash
mbpoll -m tcp -p 502 -t 4 -r 0 -c 40 <plc_ip>
```

### Step 3: Decode the Marker

```bash
python3 - <<'PY'
import socket, struct
ip = "<plc_ip>"
s = socket.create_connection((ip, 502), 5)
req = struct.pack(">HHHBBHH", 1, 0, 6, 1, 3, 0, 40)
s.sendall(req)
r = s.recv(256)
bc = r[8]
vals = struct.unpack(">%dH" % (bc // 2), r[9:9+bc])
out = "".join(chr(v) for v in vals if 32 <= v < 127)
print(out.split(chr(0))[0])
PY
```

Submit the decoded marker as the flag.

## Analysis Questions

**1. Why is Modbus risky when exposed to untrusted networks?**

**2. What does function code 0x03 return, and how is it different from 0x04?**

**3. How is ASCII text commonly stored across Modbus registers?**

**4. What defensive controls would you recommend for an OT network?**

## Defensive Takeaways

- Segment OT networks from IT and the internet.
- Use read-only gateways and unidirectional diodes where possible.
- Monitor Modbus traffic for anomalous read/write patterns.
- Never expose port 502 to untrusted networks.

## If You Get Stuck

- **Connection refused:** confirm the PLC IP and that port 502 is open.
- **Gibberish output:** check the byte-count parsing; the flag is one char per register.
- **mbpoll not found:** use the raw Python socket method.
