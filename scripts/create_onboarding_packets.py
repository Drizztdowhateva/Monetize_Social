from pathlib import Path
import csv

from monetize_social.affiliate_pipeline import PipelinePaths, ensure_onboarding_packets


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    paths = PipelinePaths(root=root)

    with paths.master.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    ensure_onboarding_packets(rows, root)
    print(f"Created onboarding packets under: {root / 'docs/onboarding_packets'}")
