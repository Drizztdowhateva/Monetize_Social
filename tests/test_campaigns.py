from pathlib import Path
import tempfile
import unittest

from monetize_social.campaigns import collect_seed_terms, generate_ad_captions, generate_hashtags


class TestCampaigns(unittest.TestCase):
    def test_generate_hashtags(self):
        tags = generate_hashtags(["creator tools", "email marketing"], niche="ai automation", limit=8)
        self.assertGreaterEqual(len(tags), 3)
        self.assertTrue(all(tag.startswith("#") for tag in tags))

    def test_collect_seed_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "master.csv"
            path.write_text(
                "Category,Platform,Primary Benefits,Best For,Top Offers To Promote,My Primary Niche\n"
                "SaaS,PartnerStack,Recurring payouts,Creators,CRM Tool,B2B Growth\n",
                encoding="utf-8",
            )
            terms = collect_seed_terms(path)
            self.assertIn("SaaS", terms)
            self.assertIn("PartnerStack", terms)

    def test_generate_ad_captions(self):
        captions = generate_ad_captions(
            niche="productivity",
            offer="notion template bundle",
            audience="new creators",
            tone="Educational",
            hashtags=["#Productivity", "#CreatorEconomy"],
        )
        self.assertEqual(len(captions), 3)
        self.assertIn("notion template bundle", captions[0].lower())


if __name__ == "__main__":
    unittest.main()