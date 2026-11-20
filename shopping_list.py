"""Step 2 of the Recipe-to-Shopping agent: turn one recipe into a shopping list.

Rules (set by the project owner):
- flag "no"  = buy it for this recipe.
- flag "yes" = a pantry staple. Check the pantry file first. Only list it if it is NOT there.

Still no AI here. The agent will call build_shopping_list() later as a tool.
"""

import json
from pathlib import Path

from recipe_reader import RECIPE_FOLDER, read_grocery_lines

PANTRY_FILE = Path(__file__).parent / "pantry.json"


def load_pantry() -> set[str]:
    """Return the names of things already at home, in lower case."""
    if not PANTRY_FILE.exists():
        return set()
    data = json.loads(PANTRY_FILE.read_text(encoding="utf-8"))
    return {name.lower() for name in data.get("have", [])}


def build_shopping_list(recipe_file: Path, pantry: set[str]) -> dict:
    """Split a recipe's ingredients into 'buy' and 'check at home first'."""
    buy = []
    check_at_home = []

    for row in read_grocery_lines(recipe_file):
        if row["flag"] == "no":
            buy.append(row)
        elif row["item"].lower() in pantry:
            continue  # a staple we already have at home: skip it
        else:
            check_at_home.append(row)  # a staple, not in the pantry file: check, then buy

    return {"buy": buy, "check_at_home": check_at_home}


if __name__ == "__main__":
    recipe = RECIPE_FOLDER / "Sample Pancakes.md"
    result = build_shopping_list(recipe, load_pantry())

    print("BUY (not at home, buy for this recipe):")
    for row in result["buy"]:
        print(f"  - {row['item']}: {row['amount']}")

    print("CHECK AT HOME FIRST (staples, buy if you have none):")
    for row in result["check_at_home"]:
        print(f"  - {row['item']}: {row['amount']}")
