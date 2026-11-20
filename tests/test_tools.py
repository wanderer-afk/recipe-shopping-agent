"""Small tests for the three tools and the agent's path check.

Run from the repo folder:  python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pack_picker import pick_packs, to_base  # noqa: E402
from recipe_reader import read_grocery_lines  # noqa: E402
from agent import safe_recipe_path  # noqa: E402

SAMPLE = Path(__file__).resolve().parent.parent / "sample_recipes" / "Sample Pancakes.md"


class RecipeReaderTests(unittest.TestCase):
    def test_reads_the_sample_recipe_rows(self):
        rows = read_grocery_lines(SAMPLE)
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0]["item"], "all-purpose flour")

    def test_header_row_is_not_an_ingredient(self):
        self.assertNotIn("item", [r["item"] for r in read_grocery_lines(SAMPLE)])


class AmountTests(unittest.TestCase):
    def test_cups_become_volume(self):
        family, base = to_base("1 1/2 cups")
        self.assertEqual(family, "volume")
        self.assertAlmostEqual(base, 1.5 * 236.588, places=2)

    def test_mixed_fraction_pounds(self):
        family, base = to_base("2 1/4 lb")
        self.assertEqual(family, "mass")
        self.assertAlmostEqual(base, 2.25 * 453.592, places=1)


class PackPickerTests(unittest.TestCase):
    def test_cheapest_pack_that_covers_the_amount(self):
        options = {"milk": [
            {"pack_size": "1 qt", "price": 1.40, "family": "volume", "base": 946.353},
            {"pack_size": "1 gal", "price": 4.00, "family": "volume", "base": 3785.41},
        ]}
        result = pick_packs("milk", "1 cup", options)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["pack"], "1 qt")

    def test_no_prices_says_so(self):
        self.assertEqual(pick_packs("milk", "1 cup", {})["status"], "NO PRICE")


class AgentPathTests(unittest.TestCase):
    def test_accepts_a_recipe_in_the_folder(self):
        self.assertIsNotNone(safe_recipe_path("Sample Pancakes.md"))

    def test_refuses_paths_outside_the_folder(self):
        for bad in ["../README.md", "sub/x.md", "", "Sample Pancakes.md/..", "notes.txt"]:
            self.assertIsNone(safe_recipe_path(bad), bad)


if __name__ == "__main__":
    unittest.main()
