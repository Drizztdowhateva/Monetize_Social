from __future__ import annotations

import csv
from pathlib import Path


# Platform-specific hashtag count norms
PLATFORM_LIMITS = {
    "instagram": 30,
    "tiktok": 10,
    "linkedin": 5,
    "twitter": 3,
    "facebook": 5,
}

PLATFORM_CAPTIONS = {
    "instagram": "Instagram post (up to 2,200 chars, 30 hashtags)",
    "tiktok": "TikTok caption (up to 300 chars, ~10 hashtags)",
    "linkedin": "LinkedIn post (professional tone, 5 hashtags)",
    "twitter": "X/Twitter post (up to 280 chars, 3 hashtags)",
    "facebook": "Facebook post (conversational, 5 hashtags)",
}


def export_platform_schedules(
    exports_dir: Path,
    captions: list[str],
    hashtags: list[str],
    platforms: list[str] | None = None,
) -> list[Path]:
    if platforms is None:
        platforms = list(PLATFORM_LIMITS.keys())

    exports_dir.mkdir(parents=True, exist_ok=True)
    out_files: list[Path] = []

    for platform in platforms:
        limit = PLATFORM_LIMITS.get(platform, 10)
        tags = hashtags[:limit]
        tag_str = " ".join(tags)
        path = exports_dir / f"campaign_{platform}.csv"

        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["platform", "description", "caption", "hashtags", "char_count"])
            writer.writeheader()
            desc = PLATFORM_CAPTIONS.get(platform, platform)
            for caption in captions:
                full_text = f"{caption} {tag_str}"
                writer.writerow({
                    "platform": platform,
                    "description": desc,
                    "caption": caption,
                    "hashtags": tag_str,
                    "char_count": len(full_text),
                })

        out_files.append(path)

    return out_files
