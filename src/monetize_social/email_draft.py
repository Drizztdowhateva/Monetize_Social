from __future__ import annotations

from pathlib import Path


def _read_template(root: Path) -> str:
    template_path = root / "docs/operations/brand_outreach_email_template.md"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return (
        "Subject: Partnership Inquiry – {platform}\n\n"
        "Hi {platform} Team,\n\n"
        "I'm interested in joining your affiliate program. "
        "Please find my details below.\n\n"
        "Program URL: {url}\n"
        "Category: {category}\n"
        "Notes: {notes}\n\n"
        "Best regards"
    )


def generate_email_draft(row: dict, root: Path) -> str:
    platform = row.get("Platform", "").strip() or "the program"
    url = row.get("Official Program URL", "").strip() or row.get("Apply/Signup URL", "").strip()
    category = row.get("Category", "").strip()
    benefits = row.get("Primary Benefits", "").strip()
    notes = row.get("Internal Notes", "").strip()
    niche = row.get("My Primary Niche", "").strip()
    channel = row.get("My Website/Channel", "").strip()

    template = _read_template(root)

    # Replace common placeholder patterns found in the template
    replacements = {
        "{platform}": platform,
        "[Brand Name]": platform,
        "[BRAND NAME]": platform,
        "{url}": url,
        "[Program URL]": url,
        "{category}": category,
        "{benefits}": benefits,
        "{notes}": notes,
        "{niche}": niche,
        "[Your Website/Channel]": channel,
        "[YOUR NICHE]": niche,
    }

    draft = template
    for placeholder, value in replacements.items():
        draft = draft.replace(placeholder, value)

    return draft


def write_email_drafts(rows: list[dict], root: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for row in rows:
        platform = row.get("Platform", "").strip()
        if not platform:
            continue
        safe_name = "".join(c if c.isalnum() or c in {"-", "_"} else "_" for c in platform).strip("_").lower()
        out_path = out_dir / f"{safe_name}_outreach.md"
        draft = generate_email_draft(row, root)
        out_path.write_text(draft, encoding="utf-8")
        written.append(out_path)

    return written
