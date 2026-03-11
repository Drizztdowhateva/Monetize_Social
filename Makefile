.PHONY: setup build validate packets report test gui package-native package-appimage package-exe package-dmg pre-release install-hooks all

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && pip install pyinstaller

build:
	. .venv/bin/activate && PYTHONPATH=src python scripts/build_all.py

validate:
	. .venv/bin/activate && PYTHONPATH=src python scripts/validate_affiliate_data.py

packets:
	. .venv/bin/activate && PYTHONPATH=src python scripts/create_onboarding_packets.py

report:
	. .venv/bin/activate && PYTHONPATH=src python scripts/build_affiliate_outputs.py

test:
	. .venv/bin/activate && PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'

gui:
	. .venv/bin/activate && PYTHONPATH=src python -m monetize_social.gui

package-native:
	. .venv/bin/activate && PYTHONPATH=src python scripts/build_runtime.py

package-appimage:
	. .venv/bin/activate && PYTHONPATH=src python scripts/build_runtime.py linux

package-exe:
	. .venv/bin/activate && PYTHONPATH=src python scripts/build_runtime.py win32

package-dmg:
	. .venv/bin/activate && PYTHONPATH=src python scripts/build_runtime.py darwin

all: build validate packets test

# ── Release / Security ───────────────────────────────────────────────────────

pre-release:
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  MonetizeSocial — Pre-Release Checklist Reminder"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  1. Run tests:         make test"
	@echo "  2. Run validation:    make validate"
	@echo "  3. Update CHANGELOG:  CHANGELOG.md  (required every release)"
	@echo "  4. Update SECURITY:   SECURITY.md   (if any security changes)"
	@echo "  5. Fill checklist:    docs/operations/release_checklist.md"
	@echo "  6. Update register:   docs/operations/paperwork_register.csv"
	@echo "  7. Tag the release:   git tag -a vX.Y.Z -m 'Release vX.Y.Z'"
	@echo ""
	@echo "  Pre-flight checks:"
	@git status --short || true
	@echo ""
	@if grep -q "## \[Unreleased\]" CHANGELOG.md && \
	    git diff --name-only HEAD 2>/dev/null | grep -q "CHANGELOG.md"; then \
	    echo "  ✓ CHANGELOG.md has staged changes — looks good."; \
	elif ! git diff --name-only HEAD 2>/dev/null | grep -q "CHANGELOG.md"; then \
	    echo "  ⚠  CHANGELOG.md has NOT been modified since last commit."; \
	    echo "     Please document this release before tagging."; \
	fi
	@echo ""

install-hooks:
	@cp scripts/hooks/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "  ✓ pre-commit hook installed at .git/hooks/pre-commit"
