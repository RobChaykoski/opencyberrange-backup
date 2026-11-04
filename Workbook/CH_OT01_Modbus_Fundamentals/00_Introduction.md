# Chapter OT1: Modbus Fundamentals

## Industrial Protocols and the Analyst

Operational technology (OT) networks run the physical world: water, power,
manufacturing. They use protocols designed decades ago for reliability, not
security. Modbus TCP is the most common: no authentication, no encryption,
and a 16-bit register model that anyone on the network can read or write.

This chapter starts with the protocol itself. You will enumerate a simulated
process controller, read its holding registers, and decode the analyst marker
stored in the first block.

---\n
## What You Will Learn

- Discover a Modbus TCP service and identify the device
- Read holding registers and coils with mbpoll and raw Python
- Decode ASCII stored in consecutive registers
- Record the device identity and register layout

---\n
## Connection Details

| Exercise | Evidence | What you pull |
|----------|----------|---------------|
| 1.1 | PLC (offset 60) | Modbus TCP on port 502 |

---\n
## Safety Note

Modbus has no authentication. Treat every register read as potentially
sensitive and every write as potentially dangerous. In this lab you only
read; never write to a real controller.
