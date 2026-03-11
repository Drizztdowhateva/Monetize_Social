# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | ✅ Yes     |
| 1.0.x   | ❌ No — upgrade to 1.1.x |

---

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email the maintainer directly or open a [GitHub Security Advisory](https://github.com/Drizztdowhateva/Monetize_Social/security/advisories/new).  
Expected response time: **72 hours**.

---

## Security Patch History

### v1.1.0 — 2026-03-11 (Critical — apply immediately if forking)

Three security vulnerabilities were identified and patched in the affiliate pipeline.  
**Forks and derivative works should apply these patches before processing  
untrusted CSV data.**

---

#### 1. SSRF — Server-Side Request Forgery in URL Validator

| Field | Detail |
|-------|--------|
| **File** | `src/monetize_social/affiliate_pipeline.py` |
| **Function** | `_is_safe_url()` (new), called in `run_live_link_checks()` |
| **Severity** | High |
| **CWE** | [CWE-918 — Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html) |
| **CVSS** | 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N) |

**Description:**  
The live-link checker passed affiliate URLs from the master CSV directly to
`urllib.request.urlopen` without validating the resolved IP address.  
An attacker who controls input data could supply a URL that resolves to an
internal RFC 1918 address (e.g. `http://192.168.1.1/admin`) and use the
pipeline to probe or exfiltrate data from private network services.

**Fix:**  
All URLs are now resolved via `socket.getaddrinfo` before any HTTP request.
The resolved IP is checked against private/loopback/reserved ranges. Requests
to private addresses are rejected with a logged warning.

**Blocked ranges:** `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`,
`127.0.0.0/8`, `169.254.0.0/16`, `100.64.0.0/10`, `::1`, `::ffff:0:0/96`,
`fc00::/7`, `fe80::/10`.

---

#### 2. CSV Injection (Formula Injection) in Export Writer

| Field | Detail |
|-------|--------|
| **File** | `src/monetize_social/affiliate_pipeline.py` |
| **Function** | `_sanitize_csv_cell()` (new), applied in all CSV/Excel write paths |
| **Severity** | Medium |
| **CWE** | [CWE-1236 — Improper Neutralization of Formula Elements in a CSV File](https://cwe.mitre.org/data/definitions/1236.html) |
| **CVSS** | 6.1 (AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N) |

**Description:**  
Output CSV and Excel files were written with raw cell values from the affiliate
master sheet. A malicious affiliate record containing a value starting with
`=`, `+`, `-`, `@`, `\t`, or `\r` would be interpreted as a formula by
spreadsheet applications (Excel, LibreOffice Calc, Google Sheets), potentially
executing arbitrary commands on the reviewer's machine.

**Fix:**  
`_sanitize_csv_cell()` prefixes any dangerous leading character with a single
quote (`'`), which causes spreadsheet apps to treat the value as a string
literal.

---

#### 3. Path Traversal in Onboarding Packet Generator

| Field | Detail |
|-------|--------|
| **File** | `src/monetize_social/affiliate_pipeline.py` |
| **Function** | `ensure_onboarding_packets()` |
| **Severity** | Medium |
| **CWE** | [CWE-22 — Improper Limitation of a Pathname ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html) |
| **CVSS** | 5.3 (AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N) |

**Description:**  
Onboarding packet filenames were constructed directly from affiliate platform
names in the master CSV without sanitizing path separators. A crafted value
such as `../../etc/cron.d/evil` could cause the pipeline to write files
outside the intended `docs/onboarding_packets/` directory.

**Fix:**  
Output paths are now resolved with `Path.resolve()` and validated with
`Path.is_relative_to(packets_dir)` before any file is written. Records that
fail validation are skipped and logged.

---

## Recommended Security Checklist for Forks

Before running the pipeline against untrusted / third-party CSV data:

- [ ] Confirm `_is_safe_url()` is present and called before every `urlopen`
- [ ] Confirm `_sanitize_csv_cell()` is applied to every export write path
- [ ] Confirm `is_relative_to` guard is present in `ensure_onboarding_packets()`
- [ ] Run `make test` — all tests should pass
- [ ] Review `CHANGELOG.md` for the version you are running

---

## General Security Notes

- The pipeline processes CSV data from disk. **Do not run against CSVs from
  untrusted sources** unless you have reviewed the content first.
- URL checking requires outbound HTTP. Use a sandboxed network if running in
  CI against external data.
- Preferences are stored in `~/.monetize_social_prefs.json` in plain text.
  Do not store secrets in preference fields.
