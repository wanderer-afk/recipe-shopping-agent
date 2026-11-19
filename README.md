# Recipe-to-Shopping Agent (Codecademy bootcamp, Project 2)

A student project, in progress. It is part of the Codecademy course
"Building Agentic AI Applications". It is not affiliated with or endorsed by Codecademy.

The goal: give it a recipe, and it works out what to buy, what you probably already have at home,
and which pack sizes cover the amounts for the lowest total cost.

## What works now
- **recipe_reader.py**: reads a recipe's `## Grocery lines` table (no AI).
- **shopping_list.py**: splits the items into "buy" and "check at home first", using your pantry list.
- **pack_picker.py**: picks the cheapest pack sizes that cover each amount, and counts leftovers.
  It asks you when two choices cost the same.

## What does not work yet
- No real store prices. You type them yourself into `store_prices.csv`, which is not in this repo.
- No AI step yet. The three tools above will become the functions an AI agent calls.
- No pantry list is included. Copy `pantry.example.json` to `pantry.json` and fill it in.

## Try it
Requires Python 3.10 or newer. The scripts use only the standard library.

```bash
python recipe_reader.py
python shopping_list.py
python pack_picker.py
```

These read the made-up recipe in `sample_recipes/`. To use your own recipes, set the folder
first, for example `set RECIPE_FOLDER=C:\path\to\your\recipes` on Windows.

## Files
- `staples_all_cultures.pdf` and `.csv`: a general list of 161 staples used across many cuisines, with blank price columns. Prices are for you to type in by hand.
- `sample_items.csv`: 12 rows from that list, as a small example.
- `pantry.example.json`: a blank-style pantry file.

## Prices
Prices are typed in by hand from a store's shelves or website. This project does not collect
prices from any store's website, because store terms usually forbid automated collection.

## Secrets and personal data
Never commit a `.env` file or an API key. `.gitignore` blocks them and the other personal files.

## The checker page (index.html)
Open `index.html` in any web browser. Nothing is installed and nothing is sent anywhere.
1. Paste a recipe (or text copied from a PDF or list), one ingredient per line.
2. Tap "We have it", "Want more" or "We need it" for each one.
3. The grocery list shows what to buy, in amounts stores sell, like "at least 2 tbsp" or "at least 6 oz". No prices are needed.
4. Add anything else you want on the list, with no recipe.

The page only uses amounts; it does not know store prices. The one price shown is a national
government average for large eggs (January 2026, several months old), labelled on the page.
Answers and the last recipe are kept in your own browser, not in this repo.
Lines measured by spoon or cup but sold by weight need the grams in brackets, like `3/4 cup rice (150 g)`.
