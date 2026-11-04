# Exercise 2.1: PE Header Analysis

## Before You Begin

Exercise 2.1 is the entry point to executable analysis. You will parse a
Windows PE32 sample by hand, using Python's `struct` module, so every offset is
visible rather than hidden behind a tool.

Make sure you have:

- [ ] Launched the exercise and opened the REMnux desktop
- [ ] A terminal open inside REMnux
- [ ] The **Evidence Server** address from the panel
- [ ] `python3`, `strings`, `file`, and `xxd` available
- [ ] Read the safety notes from Exercise 1.1

---

## Scenario

Halcyon Retail Group quarantined a workstation after EDR flagged a scheduled
task pointing at an unsigned executable in a user profile. The host is offline
and the file has been copied to the evidence server.

Level 2 begins with the format itself. Before you run a debugger or a sandbox, a
PE tells you a lot: what architecture it targets, when it was built, where
execution starts, which sections exist, and which Windows APIs it imports.
Those facts shape every later question.

The sample also carries an analyst marker. It is not plaintext: the readable
strings in `.rdata` explain how the `.data` section is encoded.

---

## Your Objectives

- Confirm the file is a Windows PE and identify its architecture
- Read the COFF timestamp and entry point
- Map the section table and explain what each section is for
- Inspect the import directory and identify network/file APIs
- Locate and decode the marker stored in `.data`

---

## Background: The PE Layout

A PE file is a sequence of headers followed by section data.

```text
+----------------------+  offset 0x00
| DOS header           |  "MZ", e_lfanew at 0x3C
+----------------------+
| DOS stub             |
+----------------------+  offset e_lfanew
| PE signature         |  "PE\0\0"
+----------------------+
| COFF header          |  machine, sections, timestamp
+----------------------+
| Optional header      |  entry point, image base, data directories
+----------------------+
| Section table        |  name, RVA, raw size, raw offset, flags
+----------------------+  offset SizeOfHeaders (usually 0x400)
| .text                |  executable code
| .rdata               |  read-only data, imports, strings
| .data                |  read/write data
+----------------------+
```

### The fields that matter first

| Field | Where | Why it matters |
|-------|-------|----------------|
| `e_lfanew` | DOS header `0x3C` | Offset of the PE signature |
| `Machine` | COFF `+4` | `0x14C` = i386, `0x8664` = x64 |
| `NumberOfSections` | COFF `+6` | How many section headers follow |
| `TimeDateStamp` | COFF `+8` | Build time (Unix epoch) |
| `SizeOfOptionalHeader` | COFF `+20` | Where the section table starts |
| `AddressOfEntryPoint` | Optional `+16` | RVA where execution begins |
| `ImageBase` | Optional `+28` | Preferred load address |
| `Subsystem` | Optional `+68` | GUI, console, driver |

### Reading RVAs

A **relative virtual address (RVA)** is an offset from `ImageBase`. To turn an
RVA into a file offset, find the section whose virtual range contains it and
subtract the section's `VirtualAddress`, then add its `PointerToRawData`.

The sample uses conventional alignment: sections start at RVA `0x1000`,
`0x2000`, and `0x3000`, and at file offsets `0x400`, `0x600`, and `0x800`.

---

## Tool Primer

| Tool | What it does |
|------|--------------|
| `file sample.exe` | Identifies the format from magic bytes |
| `strings sample.exe` | Prints printable runs |
| `xxd -l 256 sample.exe` | Hex dump of the headers |
| `objdump -x sample.exe` | Prints PE headers and imports |
| `python3 -c "import struct; ..."` | Parses exact offsets |

`pefile` is convenient if installed, but the lab deliberately uses `struct` so
you can see how the format is assembled.

---

## Walkthrough

### Step 1: Pull the Sample

!!! target "Download and fingerprint the evidence"
    ```bash
    curl -s http://<evidence>/halcyon_agent.exe -o agent.exe
    file agent.exe
    sha256sum agent.exe
    ```

`file` should report a PE32 executable for Intel 80386. Record the hash before
you analyse the copy.

### Step 2: Look at the First Bytes

!!! target "Inspect the DOS header"
    ```bash
    xxd -l 64 agent.exe
    ```

The first two bytes are `4D 5A` (`MZ`). At offset `0x3C`, the four-byte
`e_lfanew` field points at the PE signature. In this sample it is `0x80`.

```bash
python3 -c "import struct;d=open('agent.exe','rb').read();print(hex(struct.unpack_from('<I',d,0x3c)[0]))"
```

### Step 3: Parse the COFF Header

The PE signature is four bytes. The COFF header follows immediately.

!!! target "Read machine, sections, and timestamp"
    ```bash
    python3 - <<'PY'
    import struct

    d = open("agent.exe", "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    machine, nsections, timestamp = struct.unpack_from("<HHI", d, pe + 4)
    opt_size = struct.unpack_from("<H", d, pe + 20)[0]

    print("signature :", d[pe:pe+4])
    print("machine   :", hex(machine))
    print("sections  :", nsections)
    print("timestamp :", hex(timestamp))
    print("opt size  :", hex(opt_size))
    PY
    ```

`0x14C` confirms i386. Convert the timestamp to a date:

```bash
python3 -c "import datetime;print(datetime.datetime.fromtimestamp(0x6AD8827D, datetime.timezone.utc))"
```

### Step 4: Read the Optional Header

The optional header is not optional for executables. It carries the entry point
and the data directories.

!!! target "Entry point, image base, subsystem"
    ```bash
    python3 - <<'PY'
    import struct

    d = open("agent.exe", "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    opt = pe + 24

    entry, base_code, base_data = struct.unpack_from("<III", d, opt + 16)
    image_base = struct.unpack_from("<I", d, opt + 28)[0]
    subsystem = struct.unpack_from("<H", d, opt + 68)[0]

    print("entry RVA :", hex(entry))
    print("image base:", hex(image_base))
    print("subsystem :", subsystem, "(3 = console)")
    PY
    ```

The entry point is an RVA, not a file offset. It should fall inside `.text`.

### Step 5: Map the Section Table

The section table starts at `pe + 24 + SizeOfOptionalHeader`. Each entry is 40
bytes.

!!! target "List sections with RVA and raw offset"
    ```bash
    python3 - <<'PY'
    import struct

    d = open("agent.exe", "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    nsections = struct.unpack_from("<H", d, pe + 6)[0]
    opt_size = struct.unpack_from("<H", d, pe + 20)[0]
    table = pe + 24 + opt_size

    for i in range(nsections):
        off = table + i * 40
        name = d[off:off+8].split(bytes([0]))[0].decode()
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", d, off + 8)
        print(f"{name:8} RVA={vaddr:#06x} raw={rawptr:#06x} size={rawsize:#06x}")
    PY
    ```

You should see `.text`, `.rdata`, and `.data`. Note their RVAs and raw offsets;
you will need the `.data` entry in Step 7.

### Step 6: Inspect the Imports

The import directory is one of the optional header's data directories. The
sample imports from `KERNEL32.dll`.

!!! target "Read the DLL and imported names"
    ```bash
    strings agent.exe | grep -E 'KERNEL32|CreateFileA|InternetOpenA'
    ```

Or parse the import table directly:

```bash
python3 - <<'PY'
import struct

d = open("agent.exe", "rb").read()
pe = struct.unpack_from("<I", d, 0x3C)[0]
opt = pe + 24
import_rva = struct.unpack_from("<I", d, opt + 96 + 8)[0]

# The sample uses 1:1 RVA-to-file-offset for .rdata.
rdata = import_rva
dll_rva = struct.unpack_from("<I", d, rdata + 12)[0]
print("DLL:", d[dll_rva:dll_rva+13].split(bytes([0]))[0].decode())
PY
```

`CreateFileA` suggests file access. `InternetOpenA` suggests WinINet network
access. That combination is worth recording: the sample can read local files
and reach the network.

### Step 7: Decode the Marker in `.data`

The readable strings in `.rdata` say:

```text
Stage-2 marker: XOR 0x5A encoded in the .data section
```

Use the `.data` section's raw offset and size, then XOR each byte with `0x5A`.
The marker is terminated by the encoded NUL (`0x5A` in the encoded stream).

!!! target "Decode the .data marker"
    ```bash
    python3 - <<'PY'
    import struct

    d = open("agent.exe", "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    nsections = struct.unpack_from("<H", d, pe + 6)[0]
    opt_size = struct.unpack_from("<H", d, pe + 20)[0]
    table = pe + 24 + opt_size

    # .data is the third section.
    vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", d, table + 2 * 40 + 8)
    raw = d[rawptr:rawptr + rawsize]
    encoded = raw.split(bytes([0x5A]))[0]
    print(bytes(b ^ 0x5A for b in encoded).decode())
    PY
    ```

Submit the decoded marker as the flag.

---

## Defensive Takeaways

Static triage of the PE format is itself a control:

- **Block by hash and signature.** An unsigned executable in a user profile
  should not be allowed to run. Application control (WDAC/AppLocker) plus
  reputation services stop most of these before execution.
- **Inspect the timestamp.** A future or anomalous build time on an unsigned
  binary is a triage signal, not proof, but it narrows the candidate set.
- **Imports predict behaviour.** `InternetOpenA` plus `CreateFileA` in a
  consumer application is worth a closer look. Import hashing (imphash) lets
  you cluster variants that share a build.
- **Section anomalies.** A large `.data` section, an unusual entry point, or a
  section with execute permission and a generic name are all worth flagging.
- **Containment first.** The host was quarantined before anyone analysed the
  file. Analysis never happens on a live, connected endpoint.

## Analysis Questions

**1. Why does the PE signature sit at `e_lfanew` instead of at a fixed offset?**

**2. What does `Machine = 0x14C` tell you about the systems this sample can run on, and what would `0x8664` mean instead?**

**3. Why is the COFF timestamp useful even though an attacker can change it?**

**4. What is the difference between an RVA and a file offset, and why does the section table matter when converting one to the other?**

**5. What does the import of `InternetOpenA` suggest about the sample's intended behaviour, and what would you look for next?**

**6. Why is the marker XOR-encoded rather than stored as plaintext, and why does that not stop a determined analyst?**

---

## Indicators to Record

| Indicator | Value from this case |
|-----------|----------------------|
| File type | PE32 executable, i386 |
| Timestamp | `0x6AD8827D` (2026-10-21 09:14:37 UTC) |
| Entry point | RVA `0x1000` (`.text`) |
| Sections | `.text`, `.rdata`, `.data` |
| Imports | `KERNEL32.dll` / `CreateFileA`, `InternetOpenA` |
| Encoded marker | `.data`, XOR `0x5A` |

---

## If You Get Stuck

- **`e_lfanew` looks wrong:** read it as a little-endian 32-bit integer at
  offset `0x3C`, not `0x3E`.
- **The section table is empty:** `SizeOfOptionalHeader` is at COFF offset
  `+20`; add it to `pe + 24`.
- **The decoded text is gibberish:** confirm you are using the `.data` section
  (third entry) and XORing with `0x5A`.
- **`strings` finds the note but not the flag:** the flag is encoded; the note
  in `.rdata` tells you how.

---

## Next

Chapter M2 continues from this sample. Later exercises will use the section map
and imports you recorded here to move into code analysis and behaviour.
