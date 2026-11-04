# Glossary

This glossary defines the terms used across OpenCyberRange. Where a term has a
standard meaning in cyber threat intelligence, the definition follows the
[MISP data model](https://www.misp-project.org/datamodels/) and the
[MISP taxonomies](https://github.com/MISP/misp-taxonomies). The MISP machine tag
is shown so the same term can be used consistently in notes, reports, and
exports.

Two kinds of entry appear here:

- **Standard term** — follows MISP or another named standard.
- **Platform term** — specific to the OpenCyberRange training workflow. It is
  not a MISP concept and should not be tagged as one.

## How MISP machine tags work

MISP taxonomies use machine tags in the form `namespace:predicate="value"`.
Some taxonomies have a single level, such as `tlp:clear`; others have a
predicate and a value, such as `malware_classification:malware-category="Ransomware"`.
Use the exact namespace, predicate, and value from the taxonomy. Do not invent
local variants.

Examples:

```text
tlp:clear
PAP:GREEN
admiralty-scale:source-reliability="a"
estimative-language:likelihood-probability="likely"
kill-chain:Reconnaissance
malware_classification:malware-category="Ransomware"
workflow:state="complete"
```

## MISP core model

| Term | Definition | MISP reference |
|---|---|---|
| Event | A container for attributes, objects, and context about one incident, observation, report, collection, or analysis. | `misp:event-type="incident"` |
| Attribute | A single piece of information in an event, such as an IP address, domain, hash, filename, or email address. An attribute may or may not be used as an indicator. | Attribute type plus `misp:ids="true"` or `misp:ids="false"` |
| Object | A structured group of related attributes, such as a file object with a name, hash, size, and type. | MISP object template |
| Galaxy | A collection of related clusters, such as threat actors, malware families, tools, or ATT&CK techniques. | MISP galaxy |
| Cluster | One entry in a galaxy, such as a named threat actor or malware family. | Galaxy cluster |
| Taxonomy | A controlled vocabulary with a namespace, predicates, and values. | Taxonomy namespace |
| Tag | A label applied to an event, attribute, or object. A tag may come from a taxonomy or be free text. | `namespace:predicate="value"` |
| Sighting | Evidence that an attribute or object was observed, such as a matching file hash or network connection. | MISP sighting |
| Indicator | An attribute or object used to detect likely malicious activity. In MISP this is controlled with the IDS flag. | `misp:ids="true"` |
| Observable | An observed fact without a judgement about whether it is malicious. In MISP, model it as an attribute with the IDS flag disabled. | `misp:ids="false"` |
| Feed | An external source that supplies events or attributes to a MISP instance. | MISP feed |
| Sharing group | A defined group of organisations and instances that may receive an event. | MISP sharing group |
| MISP instance | A MISP server that stores, correlates, and shares events. | MISP instance |

## Cyber threat intelligence terms

| Term | Definition | MISP reference |
|---|---|---|
| Indicator of compromise (IOC) | An observable that is assessed as malicious or associated with malicious activity, such as a known C2 domain or malware hash. | `ioc:artifact-state="malicious"` |
| Indicator of attack (IOA) | Behaviour or telemetry that indicates an attack in progress, such as a suspicious process chain. It is behavioural rather than a single atomic value. | No single taxonomy; describe the behaviour with an ATT&CK technique or `common-taxonomy` value |
| TTP | Tactics, techniques, and procedures. The broad description of how an adversary operates. Do not use TTP as a synonym for one ATT&CK technique. | `kill-chain:*` for phase; `mitre-attack-pattern` galaxy for technique |
| Threat actor | The person, group, or organisation responsible for an attack. | MISP `threat-actor` galaxy |
| Campaign | A set of related malicious activities conducted over a period of time. | MISP `campaign` galaxy |
| Kill chain | The Lockheed Martin phase model: Reconnaissance, Weaponization, Delivery, Exploitation, Installation, Command and Control, and Actions on Objectives. | `kill-chain:Reconnaissance` (and the other phase names) |
| Diamond model | An intrusion analysis model built from four features: Adversary, Capability, Infrastructure, and Victim. | `diamond-model:Adversary` (and the other features) |
| Command and control (C2) | The infrastructure and channel an adversary uses to task and control an implant. | `common-taxonomy:malware="command-and-control"` |
| Exfiltration | Unauthorised transfer of data from a victim environment. | `pentest:post_exploitation="data_exfiltration"` |
| Lateral movement | Movement from one compromised host or account to another inside the same environment. | Use the ATT&CK technique; no single MISP taxonomy value |
| Persistence | A mechanism that lets an adversary keep access across reboots, logons, or service restarts. | `pentest:post_exploitation="persistence"` |
| Privilege escalation | Gaining a higher privilege level than the attacker was granted. | `pentest:post_exploitation="privilege_escalation"` |
| False positive | A finding that is not actually malicious. The alert fired, but the underlying behaviour is benign or expected. | `false-positive:risk="high"` for expected rate; `false-positive:confirmed="false"` for a specific alert |
| True positive | A finding that is correctly identified as malicious or unwanted. | No single taxonomy value; use `false-positive:confirmed="true"` only when the taxonomy semantics fit |
| Benign true positive | A detection that correctly fired on real behaviour, but the behaviour is authorised or harmless. It is not a false positive. | No single taxonomy value; explain in the event |
| Confidence | How strongly an analyst trusts a judgement. Keep analytic confidence separate from source reliability. | `misp:confidence-level="usually-confident"` or `estimative-language:confidence-in-analytic-judgment="high"` |
| Source reliability | How trustworthy the source of the information is, on the Admiralty A–F scale. | `admiralty-scale:source-reliability="a"` |
| Information credibility | How likely the information itself is true, on the Admiralty 1–6 scale. | `admiralty-scale:information-credibility="1"` |
| Likelihood | The probability that a stated event will occur. Use estimative-language terms instead of bare percentages. | `estimative-language:likelihood-probability="likely"` |
| TLP | Traffic Light Protocol 2.0 sharing label: CLEAR, GREEN, AMBER, AMBER+STRICT, or RED. | `tlp:clear`, `tlp:green`, `tlp:amber`, `tlp:amber+strict`, `tlp:red` |
| PAP | Permissible Actions Protocol: what a recipient may do with the information, from passive-only to unrestricted. | `PAP:RED`, `PAP:AMBER`, `PAP:GREEN`, `PAP:CLEAR` |
| Workflow state | The maturity of an analysis: incomplete, complete, draft, ongoing, rejected, or release. | `workflow:state="complete"` |
| Malware category | The broad class of malware, such as virus, worm, trojan, ransomware, rootkit, downloader, spyware, or botnet. | `malware_classification:malware-category="Ransomware"` |
| Ransomware type | The ransomware mechanism: scareware, locker ransomware, or crypto-ransomware. | `ransomware:type="crypto-ransomware"` |
| Vulnerability | A weakness that can be exploited. Record the identifier and exploit status separately. | `vulnerability:sighting="exploited"`; also CVE, CWE, CVSS |
| Event type | The purpose of an event: observation, incident, report, collection, analysis, or automatic-analysis. | `misp:event-type="incident"` |
| Threat level | The assessed risk level of the information: no-risk, low-risk, medium-risk, or high-risk. | `misp:threat-level="high-risk"` |

## Forensics terms

| Term | Definition | MISP reference |
|---|---|---|
| PCAP | A packet capture file containing network traffic. It is evidence, not an indicator by itself. | Share as an attribute or file object; do not tag the PCAP as an IOC without context |
| Packet | One unit of network data with headers and a payload. | No taxonomy value |
| Flow | A series of packets that share a source, destination, and protocol, often identified by a five-tuple. | No taxonomy value |
| Memory dump | A copy of the contents of volatile memory, also called a memory image. Treat it as sensitive evidence. | Share as a file object when needed; no single taxonomy value |
| Acquisition | The process of capturing volatile or non-volatile evidence before it changes. | No taxonomy value |
| Chain of custody | The documented history of who handled evidence, when, and how. | No taxonomy value |
| Artifact | Any object or trace with forensic value, such as a file, log entry, registry key, packet, or memory structure. | No single taxonomy value |
| Timeline | A chronological ordering of events from one or more evidence sources. | No taxonomy value |
| Hash | A fixed-length fingerprint of data, used to identify and verify evidence. Use the algorithm name in the attribute type. | MISP attribute types such as `md5`, `sha1`, `sha256` |
| Volatility | An open-source memory forensics framework used to inspect memory images. | Tool name; do not force it into `misp:tool` |
| Process list | The set of processes that were running when a memory image was captured. | No taxonomy value |
| Injected code | Code placed into another process's memory, often to hide execution or evade detection. | Describe with an ATT&CK technique; no single taxonomy value |

## OpenCyberRange platform terms

These are training-platform terms. They are deliberately not mapped to MISP
taxonomies because they do not describe threat intelligence.

| Term | Definition |
|---|---|
| Lab | A self-contained exercise environment with one or more target containers and a scoped objective. |
| Exercise | A single task inside a lab, usually with a flag and a set of hints. |
| Track | A themed collection of labs, such as Network Security or Malware Analysis. |
| Level | A difficulty grouping inside a track. |
| Course | An instructor-created collection of labs, students, assignments, and due dates. |
| Flag | The token a student submits to prove completion. It is a training marker, not an IOC. |
| Hint | A staged clue that unlocks after a configured time or condition. |
| RangeBox | The browser-based Kali, Ubuntu, or REMnux desktop used to work on a lab. |
| Session | One running instance of a lab assigned to one student. |
| Attempt | One submission of a flag or one launch of a lab, depending on the context. |
| Completion | The recorded state after a student submits the correct flag. |

## Preferred usage

Use the standard term in new text. Keep direct quotations as they are.

| Prefer | Avoid | Why |
|---|---|---|
| command and control (C2) | C&C, CNC | C2 is the term used by MISP and MITRE ATT&CK. |
| indicator of compromise (IOC) | IOC indicator | The expansion is already in the acronym. |
| observable | IOC, when no malicious judgement has been made | An observable is a fact; an indicator carries a judgement. |
| MITRE ATT&CK technique | TTP, when referring to one technique | TTP is the broader tactics, techniques, and procedures umbrella. |
| threat actor | hacker, bad guy | Neutral, standard attribution language. |
| malware family | virus, unless it is specifically a virus | Virus is one category in `malware_classification`. |
| ransomware | crypto locker, unless it is specifically a locker | Locker ransomware and crypto-ransomware are different types. |
| false positive | benign, when the alert was correct | A benign true positive is not a false positive. |
| TLP:CLEAR | TLP:WHITE in new text | TLP 2.0 uses CLEAR; WHITE is retained for backward compatibility. |
| PAP:CLEAR | PAP:WHITE in new text | CLEAR is the current unrestricted PAP label. |
| analytic confidence: high | probably | Use estimative-language terms and keep confidence separate from likelihood. |
| source reliability: A | trusted source | The Admiralty scale is explicit and repeatable. |

## Sources and review

- [MISP data models](https://www.misp-project.org/datamodels/)
- [MISP taxonomies](https://github.com/MISP/misp-taxonomies)
- [TLP 2.0](https://www.first.org/tlp/)
- [PAP taxonomy](https://www.misp-project.org/taxonomies.html#_pap)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [Lockheed Martin Cyber Kill Chain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)
- [Admiralty scale](https://www.misp-project.org/taxonomies.html#_admiralty_scale)
- [ICD 203 estimative language](https://www.dni.gov/files/documents/ICD/ICD-203.pdf)

Reviewed: 2026-11-02 against the MISP taxonomies repository. Recheck when a
taxonomy version changes or when a new term is added to this glossary.
