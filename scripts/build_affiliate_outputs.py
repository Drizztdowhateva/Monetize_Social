from pathlib import Path

from monetize_social.affiliate_pipeline import run_pipeline


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    summary = run_pipeline(root=root, live_link_check=False)
    print("Created outputs:")
    for key, value in summary.items():
        print(f"- {key}: {value}")
