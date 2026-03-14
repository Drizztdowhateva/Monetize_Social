# Reset and Resume

Created: 2026-03-14

## Saved Checkpoint

- Backup archive: backups/MonetizeSocial_checkpoint_20260314_075905.tar.gz
- Workspace root: /home/blackmox/code/MonetizeSocial

## Current Project Status

- Pipeline and automation are implemented.
- Build, validation, onboarding packet generation, and tests passed in the latest run.
- Generated outputs are in data/exports and snapshots in data/snapshots.

## Fast Reset (Non-Destructive)

1. Close active terminals.
2. Open a new terminal in project root.
3. Recreate runtime outputs if desired:
   - rm -rf data/exports data/snapshots docs/onboarding_packets
4. Recreate environment if desired:
   - rm -rf .venv
   - python3 -m venv .venv || virtualenv .venv
   - . .venv/bin/activate
   - pip install -r requirements.txt

## Resume Commands

1. Activate env:
   - . .venv/bin/activate
2. Rebuild all:
   - PYTHONPATH=src python scripts/build_all.py
3. Validate data:
   - PYTHONPATH=src python scripts/validate_affiliate_data.py
4. Regenerate onboarding packets:
   - PYTHONPATH=src python scripts/create_onboarding_packets.py
5. Run tests:
   - PYTHONPATH=src python -m unittest discover -s tests -p test_*.py

## One Command Option

- make all

## Restore from Backup

- tar -xzf backups/MonetizeSocial_checkpoint_20260314_075905.tar.gz -C /home/blackmox/code/MonetizeSocial
