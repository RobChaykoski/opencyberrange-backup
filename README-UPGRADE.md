# OpenCyberRange

This is the canonical production and development tree for the
latest-supported-GA platform. The pre-cutover tree remains at
`RobChaykoski/opencyberrange-backup` as a read-only archive.

Start with:

- [Upgrade plan](docs/UPGRADE-TO-LATEST-GA-PLAN.md)
- [Supported versions](docs/SUPPORTED-VERSIONS.md)
- [Version inventory](scripts/report-versions.py)
- [Cutover checklist](docs/CUTOVER-TO-CANONICAL-REPO.md)

Wave 0 establishes the baseline and CI before any application dependency is
changed. Lab and RangeBox images are intentionally out of scope.

```bash
python scripts/report-versions.py --platform-only
```

Do not push a lab or RangeBox image upgrade into this tree without a separate
programme and per-lab solve tests.
