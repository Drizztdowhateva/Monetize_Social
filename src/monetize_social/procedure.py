from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
ORDERED_RE = re.compile(r"^\s*\d+\.\s+(.+?)\s*$")


@dataclass(frozen=True)
class ProcedureDocument:
    title: str
    path: str


PROCEDURE_DOCUMENTS = [
    ProcedureDocument("Easiest Onboarding Playbook", "docs/operations/easiest_onboarding_playbook.md"),
    ProcedureDocument("Affiliate Onboarding Checklist", "docs/operations/affiliate-onboarding-checklist.md"),
    ProcedureDocument("Tax and Payout Checklist", "docs/operations/tax_and_payout_checklist.md"),
]


def extract_checklist_items(markdown_text: str) -> list[str]:
    """Extract checklist-style steps from markdown bullet and numbered lists."""
    steps: list[str] = []

    for line in markdown_text.splitlines():
        bullet_match = BULLET_RE.match(line)
        ordered_match = ORDERED_RE.match(line)

        if bullet_match:
            steps.append(bullet_match.group(1).strip())
        elif ordered_match:
            steps.append(ordered_match.group(1).strip())

    return [s for s in steps if s]


def load_procedures(root: Path) -> dict[str, list[str]]:
    procedures: dict[str, list[str]] = {}

    for doc in PROCEDURE_DOCUMENTS:
        doc_path = root / doc.path
        if not doc_path.exists():
            procedures[doc.title] = [f"Missing file: {doc.path}"]
            continue

        text = doc_path.read_text(encoding="utf-8")
        steps = extract_checklist_items(text)
        procedures[doc.title] = steps or ["No checklist items found."]

    return procedures
