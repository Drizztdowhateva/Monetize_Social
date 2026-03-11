# MonetizeSocial

Affiliate operations workspace for researching programs, tracking approvals/tokens, and managing compliance paperwork.

## Quick Start

1. Create and activate virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Build all outputs:
   - `make build`
4. Start tracking:
   - Fill `data/templates/affiliate_blank_template_fillable.csv`
   - Use `data/templates/affiliate_master_fillable.csv` for prefilled reference rows

## One-Command Operations

- `make setup`: create `.venv` and install dependencies
- `make build`: generate CSV views, dashboard, workbook tabs, snapshots, changelog, onboarding packets
- `make validate`: run duplicate + URL format validation and export issues
- `make packets`: generate per-platform onboarding packet folders
- `make test`: run unit tests
- `make gui`: launch desktop GUI for guided affiliate procedures and pipeline controls
- `make all`: build + validate + packets + tests

## GUI Workflow

Run the desktop app:

- `make gui`
- or `monetize-social-gui`

The GUI includes:

- `Procedure` tab: guided checklists from onboarding and tax playbooks
- `Pipeline` tab: run full build and generate onboarding packets
- `Hashtag Ads` tab: collect hashtag seeds from affiliate master data and generate ad captions
- `Outputs` tab: see which required output files are present or missing

## Hashtag Advertising Flow

Use the `Hashtag Ads` tab for a zero-switch workflow:

1. Enter `Niche`, `Offer`, and `Audience`.
2. Click `Collect from Master CSV` to pull terms from your affiliate data.
3. Click `Generate Hashtag Ads` to create post-ready captions + hashtag sets.
4. Click `Export Campaign CSV` to write `data/exports/hashtag_campaign_plan.csv`.

This is designed for quick content batching without command-line arguments.

## Runtime Packaging (AppImage / EXE / DMG)

One-command packaging targets:

- Linux AppImage: `make package-appimage`
- Windows EXE (run on Windows): `make package-exe`
- macOS DMG (run on macOS): `make package-dmg`
- Native platform auto-detect: `make package-native`

Output folder: `dist_runtime/`

Notes:

- AppImage requires `appimagetool` installed on Linux.
- DMG requires `create-dmg` installed on macOS.
- EXE and DMG should be built on their native OS.

## Key Outputs

- `data/exports/affiliate_priority_apply_list.csv`
- `data/exports/affiliate_high_payout_potential.csv`
- `data/exports/monthly_dashboard_summary.csv`
- `data/exports/validation_issues.csv`
- `data/exports/hashtag_campaign_plan.csv`
- `data/exports/affiliate_tracker_workbook.xlsx`
- `data/snapshots/affiliate_master_snapshot_*.csv`
- `data/snapshots/changelog.md`

## Easiest Onboarding

- Playbook: `docs/operations/easiest_onboarding_playbook.md`
- Auto-generated packets: `docs/onboarding_packets/<platform>/`
- Outreach tracker: `data/templates/outreach_crm_lite.csv`

## Taxes (LLC Sole Proprietor, 1099)

- Tracker template: `data/templates/taxes_tracker_llc_1099_sole_prop.csv`
- Workflow checklist: `docs/operations/tax_and_payout_checklist.md`
- Intended for single-member LLC taxed as sole proprietor receiving 1099 income.

## Project Structure

- `docs/legal/` legal and policy templates
- `docs/operations/` business and workflow checklists
- `data/templates/` affiliate tracking templates
- `data/exports/` generated reports and workbook
- `data/snapshots/` historical snapshots and changelog
- `src/monetize_social/` python package
- `scripts/` utility scripts for export and reporting
- `LICENSES/` additional common open-source license texts

## Legal Note

Templates in this repository are for operational drafting only and are not legal advice. Have final policies reviewed by a qualified attorney for your jurisdiction.
