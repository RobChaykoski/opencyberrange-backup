# Third-Party Notices

This file is a starting inventory of third-party software used by
OpenCyberRange. It is **not legal advice**. Confirm the exact licence for the
versions you distribute and include the full licence text and copyright notice
for each component.

This updated build is based on the upstream OpenCyberRange/OCR-Lite build by
Lewis Heuermann. Keep the upstream `LICENSE`, `NOTICE`, and
[`BUILD_NOTICE.md`](BUILD_NOTICE.md) with any distribution.

## Attribution checklist

Before publishing a source archive, container image, or hosted deployment:

1. Keep the project `LICENSE`, `NOTICE`, `LICENSING.md`, and `BUILD_NOTICE.md`.
2. Keep the licence text for every third-party component you distribute.
3. Preserve copyright lines and any `NOTICE` files required by Apache-2.0
   components.
4. Include the licence text for MPL-2.0 and LGPL components listed below.
5. Audit the packages installed inside each lab container, not only the
   backend and frontend.
6. Generate an SBOM for each release and store it with the build artifacts.

Possible SBOM commands:

```bash
cd platform/backend
pip-audit -r requirements.txt
# or generate a CycloneDX SBOM with your preferred tool

cd ../frontend
npm sbom --sbom-format=cyclonedx > ../../sbom-frontend.cdx.json
```

## Backend runtime dependencies

These are the direct production dependencies from
`platform/backend/requirements.txt`. Transitive dependencies add more MIT, BSD,
Apache-2.0, ISC, PSF, and MPL-2.0 components; an SBOM is the reliable inventory.

| Package | Licence family | Notes |
|---------|----------------|-------|
| fastapi | MIT | Include copyright notice |
| uvicorn | BSD-3-Clause | Include copyright notice |
| sqlalchemy | MIT | Include copyright notice |
| psycopg (v3) | LGPL with exceptions | Notice-sensitive; include licence and exception text |
| PyJWT | MIT | Include copyright notice |
| pwdlib | MIT | Include copyright notice |
| argon2-cffi | MIT | Include copyright notice |
| bcrypt | Apache-2.0 | Include licence and any NOTICE |
| python-multipart | Apache-2.0 | Include licence |
| pydantic | MIT | Include copyright notice |
| pydantic-settings | MIT | Include copyright notice |
| email-validator | CC0-1.0 | Public-domain dedication |
| PyYAML | MIT | Include copyright notice |
| docker (Python SDK) | Apache-2.0 | Include licence and any NOTICE |
| APScheduler | MIT | Include copyright notice |
| cryptography | Apache-2.0 OR BSD-3-Clause | Include the chosen licence text |
| requests | Apache-2.0 | Include licence |
| slowapi | MIT | Include copyright notice |
| fpdf2 | LGPL-3.0-or-later | Notice-sensitive; include licence and relinking/source information |
| matplotlib | PSF-based | Include licence |
| aiohttp | Apache-2.0 | Include licence |
| pywinrm | MIT | Include copyright notice |
| alembic | MIT | Include copyright notice |
| pyotp | MIT | Include copyright notice |
| qrcode | BSD | Include copyright notice |
| Pillow | HPND | Include copyright and licence notice |

Notable transitive components include `certifi` (MPL-2.0), `pathspec`
(MPL-2.0), `python-dateutil` (dual BSD/Apache-2.0), `pywin32` (PSF), `numpy`
(BSD), and `starlette` (BSD).

## Frontend runtime dependencies

From `platform/frontend/package.json`. The generated `dist/` bundles these into
the frontend image.

| Package | Licence family | Notes |
|---------|----------------|-------|
| vue | MIT | Include copyright notice |
| vue-router | MIT | Include copyright notice |
| axios | MIT | Include copyright notice |
| chart.js | MIT | Include copyright notice |
| vue-chartjs | MIT | Include copyright notice |
| marked | MIT | Include copyright notice |
| dompurify | MPL-2.0 OR Apache-2.0 | Include the chosen licence text |
| sortablejs | MIT | Include copyright notice |
| @novnc/novnc | MPL-2.0 | Include licence; disclose modifications to MPL files |

Development-only packages (Vite, ESLint, plugins) are not part of the shipped
runtime, but their licences should still be retained if you distribute the build
toolchain or source archive.

## Documentation and workbook tooling

The workbook is built with MkDocs and shipped as static HTML under
`platform/frontend/wiki/`.

| Component | Licence family | Notes |
|-----------|----------------|-------|
| MkDocs | BSD | Include copyright notice |
| MkDocs Material | MIT | Include copyright notice |
| PyMdown Extensions | MIT | Include copyright notice |
| mkdocs-material-extensions | MIT | Include copyright notice |
| Lunr | MIT | Bundled in the search index assets |
| Mermaid | MIT | If diagrams are rendered with Mermaid |
| html2pdf.js | MIT | Bundled for workbook PDF export |
| Pygments | BSD-2-Clause | Syntax highlighting |

## Fonts and icons

- **Inter**, **JetBrains Mono**, **Fira Code**, and **Fira Sans** are licensed
  under the SIL Open Font License 1.1. Keep the OFL notice with any self-hosted
  font files. Do not sell the fonts on their own.
- The application uses inline SVG icons in
  `platform/frontend/src/components/icons/`. No third-party icon package is
  declared. If any icon path was adapted from Lucide, Feather, Heroicons, or
  another set, add that project's MIT notice.

## Container base images

Container images include their own licences and package notices. At minimum,
review and retain notices for:

| Image | Typical licence family |
|-------|------------------------|
| `python:3.11-slim` | Python Software Foundation licence plus Debian packages |
| `node:18-alpine` | Node.js MIT plus Alpine package licences |
| `nginx:alpine` | BSD-2-Clause plus Alpine package licences |
| `postgres:15-alpine` | PostgreSQL Licence plus Alpine package licences |
| `ubuntu:22.04` | Ubuntu/Debian package licences |
| Kali / REMnux / RangeBox images | Kali, REMnux, Debian, and bundled tool licences |

If you distribute built images, include the licences for the installed packages
or provide a clear source/notice path. Do not assume the base image's licence
covers every package inside it.

## Lab container dependencies

Each lab may install its own packages. Examples in this repository include:

| Component | Licence family | Where |
|-----------|----------------|-------|
| Apache HTTP Server | Apache-2.0 | Web lab containers |
| pymodbus | BSD-3-Clause (verify pinned version) | OT Modbus lab |
| Python standard library | PSF | AI mock assistant and tooling |
| qrcode / Pillow | BSD / HPND | Certificate QR generation |

Run a package inventory inside each built lab image before distributing it. A
lab image that installs a GPL, AGPL, or other notice-sensitive package inherits
that package's obligations.

## Lab evidence and reference data

Some exercises depend on third-party evidence files or reference data. These
are not covered by the project licence and need their own provenance review.

| Component | Source | Obligation / note |
|-----------|--------|-------------------|
| `memdump.7z` / `memdump.mem` | Sam Bowne, [samsclass.info](https://samsclass.info/121/proj/) | Windows Server 2008 memory-analysis training image. No explicit open-source licence was found at the source. It is downloaded at image-build time for isolated classroom use, not vendored in this repository. Treat it as all-rights-reserved third-party material and obtain permission before redistributing the image outside your course. |
| Volatility 3 (`volatility3==2.28.2`) | [Volatility Foundation](https://github.com/volatilityfoundation/volatility3) | Volatility Software License 1.0 (VSL-1.0), which includes notice and source-availability obligations. Keep the licence text or the link <https://www.volatilityfoundation.org/license/vsl-v1.0> with any image that installs it. Review the copyleft clause before publishing wrappers or derived training material. |
| `pycryptodome` | [PyCryptodome](https://www.pycryptodome.org/) | Public domain for most files, BSD-2-Clause for some. Keep the package's `LICENSE.rst`. |
| `ntkrpamp.pdb/*.json.xz` | Microsoft public symbol server, converted to Volatility 3 JSON | Microsoft symbol data remains subject to Microsoft's terms. The file is included to make the memory lab reproducible; verify redistribution rights before publishing built images or the symbol artifact itself. |
| VoIP lab capture and audio | Generated by `platform/labs/Forensics/forensics-2-1-voip-call-reconstruction/containers/evidence/generate_pcap.py` | Original synthetic training data created for this project. The transcript is an original accessibility aid for that audio. |

The memory lab's `case_brief.txt` and the workbook page repeat the Samsclass
attribution so learners can see where the evidence came from.

## Notice-sensitive components

Pay particular attention to these, because a permissive-licence checklist alone
will miss them:

- `fpdf2` — LGPL-3.0-or-later. Include the licence and enough information to
  replace/relink the library. If you distribute a container, keep the package
  source path and licence notice available.
- `psycopg` (v3) — LGPL with exceptions. Include the licence and exception.
- `@novnc/novnc` — MPL-2.0. Include the licence; if you modify MPL-covered
  files, make those files available under MPL-2.0.
- `dompurify` — MPL-2.0 OR Apache-2.0. Choose one and include its terms.
- `certifi` and `pathspec` — MPL-2.0. Include the licence notice.

## Suggested repository layout

The notice-sensitive licence texts are included here:

```text
LICENSE
NOTICE
LICENSING.md
BUILD_NOTICE.md
THIRD_PARTY_NOTICES.md
THIRD_PARTY_LICENSES/
  fpdf2-LGPL-3.0.txt
  psycopg-LGPL-with-exceptions.txt
  novnc-MPL-2.0.txt
  dompurify-MPL-2.0-OR-Apache-2.0.txt
  certifi-MPL-2.0.txt
  pathspec-MPL-2.0.txt
```

Add the full licence text for any additional component you distribute. A
source-only archive has a smaller obligation than a built container image that
bundles every dependency.

---

_This inventory was prepared with AI assistance and reviewed as part of the
updated build. Verify it against the exact versions you ship._
