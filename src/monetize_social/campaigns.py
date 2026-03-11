from __future__ import annotations

import csv
import re
from pathlib import Path


TOKEN_SPLIT_RE = re.compile(r"[,;/|\\n]+")
NON_WORD_RE = re.compile(r"[^a-zA-Z0-9 ]+")


def _tokens_from_text(text: str) -> list[str]:
    cleaned = NON_WORD_RE.sub(" ", text or "")
    parts = [p.strip() for p in TOKEN_SPLIT_RE.split(cleaned)]
    return [p for p in parts if p]


def _to_hashtag(term: str) -> str:
    words = [w for w in re.split(r"\s+", term.strip()) if w]
    if not words:
        return ""
    merged = "".join(w.capitalize() for w in words)
    return f"#{merged}"


def collect_seed_terms(master_csv_path: Path) -> list[str]:
    if not master_csv_path.exists():
        return []

    fields = [
        "Category",
        "Platform",
        "Primary Benefits",
        "Best For",
        "Top Offers To Promote",
        "My Primary Niche",
    ]

    seeds: list[str] = []
    with master_csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        for field in fields:
            seeds.extend(_tokens_from_text(str(row.get(field, ""))))

    deduped: list[str] = []
    seen: set[str] = set()
    for seed in seeds:
        norm = seed.strip().lower()
        if norm and norm not in seen:
            deduped.append(seed)
            seen.add(norm)
    return deduped


def generate_hashtags(seed_terms: list[str], niche: str = "", limit: int = 30) -> list[str]:
    defaults = [
        "affiliate marketing",
        "creator economy",
        "online business",
        "content monetization",
        "passive income",
    ]
    terms = ([] if not niche else [niche]) + seed_terms + defaults

    out: list[str] = []
    seen: set[str] = set()
    for term in terms:
        tag = _to_hashtag(term)
        if not tag:
            continue
        norm = tag.lower()
        if norm in seen:
            continue
        out.append(tag)
        seen.add(norm)
        if len(out) >= limit:
            break
    return out


def generate_ad_captions(niche: str, offer: str, audience: str, tone: str, hashtags: list[str]) -> list[str]:
    niche_text = niche.strip() or "your niche"
    offer_text = offer.strip() or "a high-converting affiliate offer"
    audience_text = audience.strip() or "your audience"
    tag_line = " ".join(hashtags[:8])

    templates = {
        "Direct": [
            f"If you're in {niche_text}, this is the offer I'd launch first: {offer_text}. Built for {audience_text}. {tag_line}",
            f"Quick win for {audience_text}: plug {offer_text} into your next post and track clicks for 7 days. {tag_line}",
            f"Start simple: one funnel, one offer ({offer_text}), one audience ({audience_text}). {tag_line}",
        ],
        "Educational": [
            f"How to monetize {niche_text} content: pick one focused offer like {offer_text}, then match it to {audience_text}. {tag_line}",
            f"Affiliate framework: audience pain point -> relevant offer ({offer_text}) -> clear CTA. Great for {audience_text}. {tag_line}",
            f"Before posting, check fit: does {offer_text} solve a real problem for {audience_text}? If yes, publish. {tag_line}",
        ],
        "Story": [
            f"I tested dozens of links in {niche_text}. The one that kept converting was {offer_text} for {audience_text}. {tag_line}",
            f"Small tweak, big result: I positioned {offer_text} around one core pain point for {audience_text}. {tag_line}",
            f"What changed my affiliate results in {niche_text}: fewer links, better fit, and a clear offer ({offer_text}). {tag_line}",
        ],
    }

    return templates.get(tone, templates["Direct"])


def write_campaign_export(path: Path, captions: list[str], hashtags: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["caption", "hashtags"])
        writer.writeheader()
        joined_tags = " ".join(hashtags)
        for caption in captions:
            writer.writerow({"caption": caption, "hashtags": joined_tags})