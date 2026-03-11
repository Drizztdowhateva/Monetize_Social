.PHONY: setup build validate packets report test gui package-native package-appimage package-exe package-dmg all

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
