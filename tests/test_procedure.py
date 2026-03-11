import unittest

from monetize_social.procedure import extract_checklist_items


class TestProcedureParsing(unittest.TestCase):
    def test_extracts_bullets_and_ordered_items(self):
        text = """
# Example

- first bullet
- second bullet
1. first ordered
2. second ordered
Not a list item
"""
        steps = extract_checklist_items(text)
        self.assertEqual(
            steps,
            ["first bullet", "second bullet", "first ordered", "second ordered"],
        )


if __name__ == "__main__":
    unittest.main()
