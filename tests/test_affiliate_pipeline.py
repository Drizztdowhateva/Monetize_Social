import unittest

from monetize_social.affiliate_pipeline import (
    compliance_gaps,
    health_score,
    score_payout,
    score_priority,
    valid_url_format,
    validate_rows,
)


class TestAffiliatePipeline(unittest.TestCase):
    def test_valid_url_format(self):
        self.assertTrue(valid_url_format("https://example.com"))
        self.assertTrue(valid_url_format("http://example.org/path"))
        self.assertFalse(valid_url_format("example.com"))
        self.assertFalse(valid_url_format(""))

    def test_scores(self):
        row = {
            "Platform": "PartnerStack",
            "Approval Difficulty": "Medium",
            "Program Status": "Active",
            "Commission Model": "Recurring rev share",
            "Niche Fit Score (1-10)": "8",
            "Approval Status (Pending/Approved/Rejected)": "Approved",
            "Application Submitted (Y/N)": "Y",
            "Tax Form Submitted (Y/N)": "Y",
            "Payment Profile Completed (Y/N)": "Y",
            "Promo Assets Access (Y/N)": "Y",
            "2FA Enabled (Y/N)": "Y",
            "Compliance Notes": "ok",
        }
        self.assertGreaterEqual(score_priority(row), 0)
        self.assertGreaterEqual(score_payout(row), 0)
        self.assertGreaterEqual(health_score(row), 70)

    def test_compliance_gaps(self):
        row = {
            "Tax Form Submitted (Y/N)": "N",
            "Payment Profile Completed (Y/N)": "N",
            "Promo Assets Access (Y/N)": "N",
            "2FA Enabled (Y/N)": "N",
            "Compliance Notes": "",
        }
        gaps = compliance_gaps(row)
        self.assertIn("tax_form", gaps)
        self.assertIn("2fa", gaps)

    def test_validate_rows_duplicate(self):
        rows = [
            {
                "Platform": "Amazon Associates",
                "Official Program URL": "https://affiliate-program.amazon.com/",
                "Apply/Signup URL": "https://affiliate-program.amazon.com/",
                "Support/Docs URL": "https://affiliate-program.amazon.com/help",
            },
            {
                "Platform": "Amazon Associates",
                "Official Program URL": "https://affiliate-program.amazon.com/",
                "Apply/Signup URL": "bad-url",
                "Support/Docs URL": "https://affiliate-program.amazon.com/help",
            },
        ]
        issues = validate_rows(rows, check_live_links=False)
        kinds = {i["issue_type"] for i in issues}
        self.assertIn("duplicate_platform", kinds)
        self.assertIn("invalid_url_format", kinds)


if __name__ == "__main__":
    unittest.main()
