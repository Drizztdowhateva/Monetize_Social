# Release Checklist

> Fill out **one copy of this file per release** before running `make build` or tagging a version.  
> Copy it to `release_checklist_vX.Y.Z.md`, fill in each item, and commit it with your release commit.

---

## Release Metadata

| Field | Value |
|-------|-------|
| Version | vX.Y.Z |
| Release date | YYYY-MM-DD |
| Branch | master / release/vX.Y.Z |
| Release author | |
| Reviewer | |

---

## 1. Code Quality

- [ ] `make test` passes with zero failures
- [ ] `make validate` runs without errors on a sample CSV
- [ ] No new `TODO` / `FIXME` items left unresolved

---

## 2. Security — Required Every Build

- [ ] Any new URL-fetching code calls `_is_safe_url()` before `urlopen`
- [ ] Any new CSV/Excel write path wraps values with `_sanitize_csv_cell()`
- [ ] Any new file-write path using user-supplied names uses `Path.resolve()` + `is_relative_to()` guard
- [ ] Dependencies scanned for known CVEs:
  ```
  pip-audit  -or-  safety check
  ```
- [ ] No secrets or credentials committed (check with `git diff HEAD~1 -- .`)
- [ ] `SECURITY.md` updated if a new vulnerability was found or patched

---

## 3. Changelog

- [ ] `CHANGELOG.md` has an entry for this version
- [ ] Entry includes all **Added**, **Changed**, **Fixed**, **Security**, and **Removed** sections
- [ ] Comparison URL at the bottom of `CHANGELOG.md` points to the correct tags

---

## 4. Packaging / Distribution

- [ ] `make package-native` builds without error on the release platform
- [ ] Packaged binary launches and GUI opens (`make gui` smoke test)
- [ ] `dist_runtime/` output **not** committed (it is `.gitignore`d)

---

## 5. Legal / Compliance

- [ ] `docs/operations/paperwork_register.csv` — `Last Updated` column refreshed if any doc changed
- [ ] No new affiliate data or PII accidentally committed (check `git status`)
- [ ] License headers present in any new source files

---

## 6. Git Hygiene

- [ ] Working tree is clean (`git status`)
- [ ] Commit message follows conventional format (`feat:` / `fix:` / `security:` / `chore:`)
- [ ] Tag created: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push tag: `git push origin vX.Y.Z`

---

## 7. Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | | | |
| Reviewer | | | |

---

*Template location: `docs/operations/release_checklist.md`*  
*Registered in: `docs/operations/paperwork_register.csv`*
