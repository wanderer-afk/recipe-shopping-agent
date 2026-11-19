"""Step 1 of the Recipe-to-Shopping agent: read the shopping list from one recipe.

No AI in this file yet. A function like this is what the agent will call later
as a "tool" (a function the AI is allowed to ask to run).
"""

import os
from pathlib import Path

# Where your recipes live. Set RECIPE_FOLDER in your environment to point at your own
# recipe folder; otherwise the made-up sample recipes in sample_recipes/ are used.
RECIPE_FOLDER = Path(os.environ.get("RECIPE_FOLDER", Path(__file__).parent / "sample_recipes"))
DEFAULT_RECIPE = "Sample Pancakes.md"


def read_grocery_lines(recipe_file: Path) -> list[dict]:
    """Return the rows from a recipe's '## Grocery lines' code block."""
    text = recipe_file.read_text(encoding="utf-8")
    rows = []
    found_heading = False
    inside_block = False

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if line.startswith("## Grocery lines"):
            found_heading = True
            continue

        if found_heading and line.startswith("```"):
            if inside_block:
                break  # second ``` is the closing fence, so we are done
            inside_block = True
            continue

        if inside_block and "|" in line:
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 4:
                continue  # skip any line that does not have 4 columns
            item, amount, aisle, flag = parts
            if item.lower() == "item":
                continue  # the header row (item | amount | aisle | flag) is not a grocery item
            rows.append({"item": item, "amount": amount, "aisle": aisle, "flag": flag})

    return rows


if __name__ == "__main__":
    # This block runs only when you start this file directly (python recipe_reader.py).
    recipe = RECIPE_FOLDER / "Sample Pancakes.md"
    for row in read_grocery_lines(recipe):
        print(row)
