from pathlib import Path

from monetize_social.affiliate_pipeline import PipelinePaths, validate_rows
import csv


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    paths = PipelinePaths(root=root)

    with paths.master.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    issues = validate_rows(rows, check_live_links=False)
    paths.exports.mkdir(parents=True, exist_ok=True)

    out = paths.validation_csv
    with out.open("w", newline="", encoding="utf-8") as f:
        if issues:
            import csv as _csv

            writer = _csv.DictWriter(f, fieldnames=["row", "platform", "issue_type", "detail"])
            writer.writeheader()
            writer.writerows(issues)
        else:
            f.write("row,platform,issue_type,detail\n")

    print(f"Validation issues: {len(issues)}")
    print(f"Output: {out}")
