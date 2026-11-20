# Recipe Shopping Checker (Codecademy bootcamp, Project 2)

Paste a recipe, tell the checker what you already have at home, and get a grocery list written in
amounts stores actually sell, like "at least 2 tbsp" or "at least 6 oz".

Built by Bailey as a student project for the Codecademy course "Building Agentic AI Applications".
Claude (an AI assistant) helped with parts of the code, the page design and the write-up; Bailey set
the goals, made the decisions and tested the results. Not affiliated with or endorsed by Codecademy.

**Status:** the checker page and the three Python tools work. The AI-agent step (the part that
will let a model call these tools) is not built yet.

## What is in this repo
| File | What it does |
|---|---|
| `index.html` | The checker page. Open it in a browser. No install. Nothing is sent anywhere. |
| `recipe_reader.py` | Reads a recipe's `## Grocery lines` table (plain Python, no AI). |
| `shopping_list.py` | Splits items into "buy" and "check at home first" using a pantry list. |
| `pack_picker.py` | Picks the cheapest pack sizes that cover an amount, counting leftovers. |
| `staples_all_cultures.csv` / `.pdf` | 161 everyday staples used across many cuisines. Prices blank. |
| `estimated_prices_NOT_REAL.csv` / `.pdf` | Rough price guesses for those 161 items. **Not real.** |
| `average_prices_staples.csv` | The only checked price: eggs, from a US government average (see below). |
| `grocery_items_and_prices.pdf` | The checked-prices sheet as a PDF. |
| `showcase_prices_EXAMPLE_made_up.csv` / `.pdf` | Made-up example prices for demos. **Not real.** |
| `make_pdfs.py` | Rebuilds the two PDFs from their CSV files. |
| `sample_recipes/Sample Pancakes.md` | A made-up recipe for testing. |
| `sample_items.csv` | 12 rows from the staples list, as a small example. |
| `pantry.example.json` | A blank-style pantry list. Copy it to `pantry.json` to use it. |
| `requirements.txt` | Python packages needed to rebuild the PDFs. |
| `.env.example` | A template for future API keys. Copy it to `.env` and fill it in. Never commit `.env`. |

## Prerequisites
- **Python 3.10 or newer** (for the three Python tools). Check with `python --version`.
- **A web browser** for `index.html` (Chrome, Edge, Firefox or Safari).
- **Packages:** the three tools use only the standard library, so nothing to install for them.
  Rebuilding the PDFs needs `reportlab` (listed in `requirements.txt`).
- **No API keys are needed today.** A future AI step will need an API key from a model provider.
  You create that account and key yourself, and paste it into `.env`.

## Install (optional, only to rebuild the PDFs)
Windows (Command Prompt):
```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```
Mac / Linux:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run it
1. **The page:** double-click `index.html`, or open it from your browser's File menu.
   - Paste a recipe, one ingredient per line, amount first. Use the example button to try it.
   - Tap "We have it", "Want more" or "We need it" for each ingredient.
   - Add anything else you want on the list, with no recipe.
   - Lines measured by spoon or cup but sold by weight need the grams in brackets, like `3/4 cup rice (150 g)`.
2. **The Python tools** (from this folder):
   ```
   python recipe_reader.py
   python shopping_list.py
   python pack_picker.py
   ```
   These read the made-up recipe in `sample_recipes/`.
3. **Your own recipes:** set a folder before running, so the tools read your files instead:
   - Windows: `set RECIPE_FOLDER=C:\path\to\your\recipes`
   - Mac / Linux: `export RECIPE_FOLDER=/path/to/your/recipes`
4. **Rebuild the PDFs:** `python make_pdfs.py`

## About the price data (read this first)
- **Almost every price here is fake or a guess.** `estimated_prices_NOT_REAL.*` and
  `showcase_prices_EXAMPLE_made_up.*` are labelled as such in every file and on every page.
  Do not use them for shopping or budgeting.
- **One price is checked:** eggs, large Grade A, about $2.58 per dozen. This is the US Bureau of
  Labor Statistics national average for January 2026, so it is several months old and local prices differ.
- **The checker page does not need prices.** It tells you the amount to buy, not the cost.
- **To use your own prices**, type them into a CSV with the columns `item,pack_size,price`, using the size
  printed on the package. Prices you type in stay in your own browser or your own files.
- **Store websites are not scraped.** Most stores forbid automated collection of their prices and catalogues
  in their terms. Prices here are typed in by hand, or come from public government data.

## Your own data and keys
- `pantry.json`, `store_prices.csv`, `.env` and `all_items.csv` are in `.gitignore`. Keep your personal lists
  and keys out of any public copy.
- `.env.example` shows the shape of a key file. A real key goes only in `.env`, on your own computer.

## What the class taught that shaped this project
Notes written in our own words from the class lessons. Teacher materials are not copied here.
- **Week 5 (agents):** an agent picks a tool by reading its description, so each tool's name and
  description must say exactly what it does. Our three tools are written that way.
- **Week 5 (safety):** a person should approve anything risky before it happens, and a loop needs a step
  limit. The checker never changes a shopping list or a store account on its own.
- **Week 6 (automation):** login details live in saved credentials, not in files. This is why `.env`
  is ignored by git.

## Limits
- The AI step is not built, so nothing reads your recipe in natural language yet.
- Name matching is by plain text. "Milk" and "whole milk" match, but a different word for the same food may not.
- Packs counted in bunches, cans or dozens are flagged for you to check, except dozen eggs.
- The page has been tested in a desktop browser. It has not been tested on a phone.

## Files and privacy
Nothing on the page is sent over the internet. Saved answers and your last recipe are kept in the browser on
your own computer.
