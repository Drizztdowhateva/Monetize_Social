from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
import re
from urllib.parse import urlencode, urlparse, urlunparse


def normalize_sponsor_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9 ]+", " ", (name or "").lower()).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)

    aliases = {
        "snap on": "Snap-on",
        "snapon": "Snap-on",
        "jl audio": "JL Audio",
        "aws": "AWS",
        "ski doo": "Ski-Doo",
        "blue point": "Blue-Point",
    }
    if cleaned in aliases:
        return aliases[cleaned]

    if not cleaned:
        return ""

    words = [w.capitalize() for w in cleaned.split(" ")]
    return " ".join(words)


def _row_completeness(row: dict[str, str]) -> int:
    return sum(1 for value in row.values() if str(value).strip())


def dedupe_rows(rows: list[dict[str, str]], headers: list[str]) -> tuple[list[dict[str, str]], int]:
    merged: dict[str, dict[str, str]] = {}
    removed = 0

    for row in rows:
        normalized = normalize_sponsor_name(row.get("Sponsor", ""))
        key = normalized.lower().strip()
        if not key:
            continue

        candidate = {h: str(row.get(h, "")).strip() for h in headers}
        candidate["Sponsor"] = normalized

        existing = merged.get(key)
        if existing is None:
            merged[key] = candidate
            continue

        removed += 1
        if _row_completeness(candidate) > _row_completeness(existing):
            base = candidate
            fallback = existing
        else:
            base = existing
            fallback = candidate

        for header in headers:
            if not str(base.get(header, "")).strip() and str(fallback.get(header, "")).strip():
                base[header] = fallback[header]
        merged[key] = base

    out = sorted(merged.values(), key=lambda r: r.get("Sponsor", "").lower())
    return out, removed


def infer_program_urls(website: str) -> tuple[str, str, str]:
    if not website.strip():
        return "", "", "pending verification"

    base = website.strip().rstrip("/")
    confidence = "probable"
    program_page = f"{base}/partners"
    form_url = f"{base}/contact"

    lowered = base.lower()
    if "aws.amazon.com" in lowered:
        program_page = "https://aws.amazon.com/partners/"
        form_url = "https://aws.amazon.com/partners/"
        confidence = "public page"
    elif "amazon.com" in lowered:
        program_page = "https://affiliate-program.amazon.com/"
        form_url = "https://affiliate-program.amazon.com/"
        confidence = "public page"
    elif "google" in lowered:
        program_page = "https://about.google/intl/en/partner-programs/"
        form_url = "https://support.google.com/"
        confidence = "probable"

    return program_page, form_url, confidence


def _safe_float(raw: str) -> float | None:
    text = (raw or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _safe_int(raw: str, default: int = 0) -> int:
    text = (raw or "").strip()
    if not text:
        return default
    try:
        num = int(text)
    except ValueError:
        return default
    return max(0, min(num, 5))


def compute_total_score(
    row: dict[str, str],
    budget: float | None,
    weights: dict[str, int],
) -> tuple[int, str]:
    fit = _safe_int(row.get("Fit Score (1-5)", ""))
    readiness = _safe_int(row.get("Readiness Score (1-5)", ""))
    access = _safe_int(row.get("Access Score (1-5)", ""))

    investment = _safe_float(row.get("Estimated Investment Amount (USD)", ""))

    affordable_text = "Unknown"
    affordable_points = 0
    if budget is not None and investment is not None:
        is_affordable = investment <= budget
        affordable_text = "Yes" if is_affordable else "No"
        affordable_points = 1 if is_affordable else 0
    elif budget is not None and investment is None:
        affordable_text = "No"

    has_form = 1 if row.get("Application Form URL", "").strip() else 0

    total = (
        fit * max(1, weights.get("fit", 1))
        + readiness * max(1, weights.get("readiness", 1))
        + access * max(1, weights.get("access", 1))
        + has_form * max(1, weights.get("form", 1))
        + affordable_points * max(1, weights.get("budget", 1))
    )
    return total, affordable_text


def add_utm(url: str, sponsor: str, source: str = "sponsor_ops") -> str:
    raw = (url or "").strip()
    if not raw:
        return ""

    parsed = urlparse(raw)
    if not parsed.scheme:
        return raw

    sponsor_slug = re.sub(r"[^a-zA-Z0-9]+", "-", sponsor.strip().lower()).strip("-") or "sponsor"
    params = {
        "utm_source": source,
        "utm_medium": "sponsorship",
        "utm_campaign": sponsor_slug,
    }

    query = parsed.query
    if query:
        query = f"{query}&{urlencode(params)}"
    else:
        query = urlencode(params)

    updated = parsed._replace(query=query)
    return urlunparse(updated)


def build_followup_rows(rows: list[dict[str, str]], base_date: date) -> list[dict[str, str]]:
    cadence = [0, 3, 7, 14]
    output: list[dict[str, str]] = []

    for row in rows:
        sponsor = row.get("Sponsor", "").strip()
        status = row.get("Status", "").strip().lower()
        if not sponsor:
            continue
        if status in {"active", "paused"}:
            continue

        for day_offset in cadence:
            send_date = base_date + timedelta(days=day_offset)
            output.append(
                {
                    "Sponsor": sponsor,
                    "Current Status": row.get("Status", ""),
                    "Touchpoint": f"Day {day_offset}",
                    "Suggested Date": send_date.isoformat(),
                    "Message Prompt": f"Follow up with {sponsor} on sponsorship + affiliate terms and next step.",
                }
            )

    return output


def build_roi_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []

    for row in rows:
        sponsor = row.get("Sponsor", "").strip()
        if not sponsor:
            continue

        investment = _safe_float(row.get("Estimated Investment Amount (USD)", "")) or 0.0
        expected_conversions = 20
        commission_per_conversion = 45.0
        expected_revenue = expected_conversions * commission_per_conversion
        roi = expected_revenue - investment

        out.append(
            {
                "Sponsor": sponsor,
                "Estimated Investment (USD)": f"{investment:.2f}",
                "Expected Conversions": str(expected_conversions),
                "Commission per Conversion (USD)": f"{commission_per_conversion:.2f}",
                "Expected Revenue (USD)": f"{expected_revenue:.2f}",
                "Projected ROI (USD)": f"{roi:.2f}",
                "Break-even Conversions": f"{(investment / commission_per_conversion) if commission_per_conversion else 0:.2f}",
            }
        )

    return out


def build_dashboard_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_vertical: dict[str, dict[str, int]] = {}

    for row in rows:
        vertical = row.get("Vertical", "").strip() or "Other"
        status = row.get("Status", "").strip().lower() or "unknown"

        bucket = by_vertical.setdefault(
            vertical,
            {"total": 0, "active": 0, "negotiating": 0, "contacted": 0, "lead": 0},
        )
        bucket["total"] += 1
        if status in bucket:
            bucket[status] += 1

    out: list[dict[str, str]] = []
    for vertical, stats in sorted(by_vertical.items()):
        out.append(
            {
                "Vertical": vertical,
                "Total Sponsors": str(stats["total"]),
                "Lead": str(stats["lead"]),
                "Contacted": str(stats["contacted"]),
                "Negotiating": str(stats["negotiating"]),
                "Active": str(stats["active"]),
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_kanban_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    columns = ["Lead", "Researching", "Contacted", "Negotiating", "Active", "Paused"]
    grouped: dict[str, list[str]] = {c: [] for c in columns}

    for row in rows:
        status = row.get("Status", "").strip().title() or "Lead"
        sponsor = row.get("Sponsor", "").strip()
        if not sponsor:
            continue
        if status not in grouped:
            status = "Lead"
        grouped[status].append(sponsor)

    lines = ["# Sponsor Kanban Board", ""]
    for col in columns:
        lines.append(f"## {col}")
        items = sorted(grouped[col])
        if not items:
            lines.append("- (none)")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
