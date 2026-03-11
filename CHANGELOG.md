# Changelog

All notable changes to **MonetizeSocial** are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [1.1.0] — 2026-03-11

### Security (Critical — recommended for all forks)

- **SSRF prevention in URL validator** (`affiliate_pipeline.py`)  
  All URLs submitted for live-link checking are now resolved to their IP address
  and rejected if they target private, loopback, or reserved ranges (RFC 1918 /
  RFC 3927 / RFC 5737 / RFC 6598 / ::1 / ::ffff:0:0/96).  
  *Affected function:* `_is_safe_url()` — called before every `urlopen`.  
  *Risk without patch:* Attacker-controlled CSV could pivot the pipeline to
  probe internal network services (SSRF).

- **CSV injection sanitization in export writer** (`affiliate_pipeline.py`)  
  All cell values written to CSV/Excel are now passed through
  `_sanitize_csv_cell()`, which prefixes `=`, `+`, `-`, `@`, `\t`, and `\r`
  with a single-quote (`'`) so spreadsheet applications do not interpret them
  as formulas or commands.  
  *Risk without patch:* Malicious affiliate names/URLs could inject formulas
  into output CSVs, executing arbitrary code when opened in Excel/LibreOffice.

- **Path traversal guard in onboarding packet generation** (`affiliate_pipeline.py`)  
  Output paths for generated onboarding packets are resolved with
  `Path.resolve()` and validated with `is_relative_to(packets_dir)` before any
  file is written.  
  *Risk without patch:* A crafted affiliate name such as `../../etc/cron.d/evil`
  could write files outside the intended output directory.

### Performance

- Parallel live-link checks via `ThreadPoolExecutor(max_workers=8)` —
  reduces full-build time proportionally with number of affiliate URLs.
- Column-width scanning in Excel workbook capped at 200 rows — prevents O(n)
  slowdown on large master sheets.
- `health_score` / `compliance_gaps` computed once per row; no duplicate work.
- Changelog file written in append mode (`open("a")`) — eliminates TOCTOU race.
- Snapshot uses `shutil.copy2` instead of manual read/write.

### Added

- Full 5-tab Tkinter desktop GUI (`gui.py`):
  Procedure, Pipeline, Hashtag Ads, Outputs, Email Drafts
- Hashtag seed collection from master CSV + ad caption generation (`campaigns.py`)
- Per-platform scheduler CSV export with hashtag-count limits (`scheduler_export.py`)
- Outreach email draft generator per affiliate platform (`email_draft.py`)
- Persistent user preferences — theme, tone, niche slider (`prefs.py`)
- 10 UX improvements: clipboard copy, niche-fit slider, auto-snapshot timer,
  dark/light theme, inline URL validator, caption template library,
  per-platform exports, compliance badges, email draft generator,
  prefs persistence
- PyInstaller packaging script → AppImage / EXE / DMG (`scripts/build_runtime.py`)

### Changed

- `.gitignore` — generated output data (`data/exports/`, `data/snapshots/`,
  `docs/email_drafts/`, `docs/onboarding_packets/`) excluded from version
  control; only source code and templates are tracked.

---

## [1.0.0] — 2026-03-11

### Added

- Initial release: affiliate pipeline, CSV templates, legal/ops docs,
  compliance checklist, onboarding playbook, tax tracker.

---

[Unreleased]: https://github.com/Drizztdowhateva/Monetize_Social/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Drizztdowhateva/Monetize_Social/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Drizztdowhateva/Monetize_Social/releases/tag/v1.0.0
