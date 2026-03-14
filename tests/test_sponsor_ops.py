import unittest

from monetize_social.sponsor_ops import (
    add_utm,
    compute_total_score,
    dedupe_rows,
    infer_program_urls,
    normalize_sponsor_name,
)


class TestSponsorOps(unittest.TestCase):
    def test_normalize_sponsor_name_aliases(self):
        self.assertEqual(normalize_sponsor_name("snap on"), "Snap-on")
        self.assertEqual(normalize_sponsor_name("  jl audio "), "JL Audio")

    def test_dedupe_rows_merges_variants(self):
        headers = ["Sponsor", "Website", "Status"]
        rows = [
            {"Sponsor": "Snap on", "Website": "", "Status": "Lead"},
            {"Sponsor": "Snap-on", "Website": "https://www.snapon.com/", "Status": ""},
        ]
        deduped, removed = dedupe_rows(rows, headers)
        self.assertEqual(removed, 1)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["Sponsor"], "Snap-on")
        self.assertEqual(deduped[0]["Website"], "https://www.snapon.com/")

    def test_compute_total_score_uses_weights(self):
        row = {
            "Fit Score (1-5)": "4",
            "Readiness Score (1-5)": "3",
            "Access Score (1-5)": "2",
            "Application Form URL": "https://example.com/form",
            "Estimated Investment Amount (USD)": "500",
        }
        score, affordable = compute_total_score(
            row,
            budget=600,
            weights={"fit": 2, "readiness": 1, "access": 1, "form": 1, "budget": 2},
        )
        self.assertEqual(affordable, "Yes")
        self.assertEqual(score, 16)

    def test_infer_program_urls(self):
        page, form, confidence = infer_program_urls("https://aws.amazon.com/")
        self.assertIn("partners", page)
        self.assertIn("partners", form)
        self.assertEqual(confidence, "public page")

    def test_add_utm(self):
        out = add_utm("https://example.com/offer", sponsor="Sony")
        self.assertIn("utm_source=sponsor_ops", out)
        self.assertIn("utm_campaign=sony", out)


if __name__ == "__main__":
    unittest.main()
