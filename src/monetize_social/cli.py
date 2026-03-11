from pathlib import Path

from monetize_social.affiliate_pipeline import run_pipeline


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    run_pipeline(root=root, live_link_check=False)


if __name__ == "__main__":
    main()
