from __future__ import annotations

import json
from pathlib import Path

_PREFS_PATH = Path.home() / ".monetize_social_prefs.json"


def load_prefs() -> dict:
    if _PREFS_PATH.exists():
        try:
            return json.loads(_PREFS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_prefs(data: dict) -> None:
    try:
        existing = load_prefs()
        existing.update(data)
        _PREFS_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    except OSError:
        pass


def get_pref(key: str, default=None):
    return load_prefs().get(key, default)


def set_pref(key: str, value) -> None:
    save_prefs({key: value})
