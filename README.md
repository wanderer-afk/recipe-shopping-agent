# Our Kitchen Grocery Book (Recipe Shopping Checker)

Paste a recipe, or take a photo of one. Tell the checker what you already have at home, and it gives you a
grocery list written in amounts stores actually sell, like "at least 2 tbsp" or "at least 6 oz".
It can also answer questions about a recipe with a small AI agent that runs on your own computer.

## What is in this repo
| File | What it does |
|---|---|
| `index.html` | The checker page. Open it in a browser. No install. Your recipes and answers stay on your device. |
| `recipe_reader.py` | Reads a recipe's `## Grocery lines` table (plain Python, no AI). |
| `shopping_list.py` | Splits items into "buy" and "check at home first" using a pantry list. |
| `pack_picker.py` | Picks the cheapest pack sizes that cover an amount, counting leftovers. |
| `staples_all_cultures.csv` / `.pdf` | 161 everyday staples used across many cuisines. Prices blank. |
| `estimated_prices_NOT_REAL.csv` / `.pdf` | Rough price guesses for those 161 items. **Not real.** |
| `average_prices_staples.csv` | The only checked price: eggs, from a US government average (see below). |
| `grocery_items_and_prices.pdf` | The checked-prices sheet as a PDF. |
| `showcase_prices_EXAMPLE_made_up.csv` / `.pdf` | Made-up example prices for demos. **Not real.** |
| `make_pdfs.py` | Rebuilds the two PDFs from their CSV files. |
| `agent.py` | The AI step: a small agent that calls the three tools, using a free model on your own computer (Ollama). |
| `sample_recipes/` | 11 made-up recipes for testing (table format: item, amount, aisle, pantry staple). |
| `sample_recipe_grocery_lists.pdf` | Buy and check-at-home lists for the sample recipes. |
| `sample_items.csv` | 12 rows from the staples list, as a small example. |
| `pantry.example.json` | A blank-style pantry list. Copy it to `pantry.json` to use it. |
| `requirements.txt` | Python packages needed to rebuild the PDFs. |
| `report.pdf` | The project report: the problem, how it works, the agent loop diagram, test results, and limits. |
| `make_report.py` | Rebuilds report.pdf. |
| `store_prices.example.csv` | Made-up prices showing the format for your own price file. Not real. |
| `LICENSE` | MIT license. |

## Prerequisites
- **Python 3.10 or newer** (for the three Python tools). Check with `python --version`.
- **A web browser** for `index.html` (Chrome, Edge, Firefox or Safari).
- **Packages:** the three tools use only the standard library, so nothing to install for them.
  Rebuilding the PDFs needs `reportlab` (listed in `requirements.txt`).
- **No API keys are needed.** The AI agent runs on your own computer through Ollama (free).

## Install (optional, only to rebuild the PDFs)
Windows (PowerShell, the default in Windows 11):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Windows (Command Prompt): run `.venv\Scripts\activate.bat` instead of `Activate.ps1`.
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
   python -m unittest discover -s tests    # the tests
   ```
   These read the made-up recipe in `sample_recipes/`.
3. **Your own recipes:** set a folder before running, so the tools read your files instead:
   - Windows PowerShell: `$env:RECIPE_FOLDER="C:\path\to\your\recipes"`
   - Windows Command Prompt: `set RECIPE_FOLDER=C:\path\to\your\recipes`
   - Mac / Linux: `export RECIPE_FOLDER=/path/to/your/recipes`
4. **Rebuild the PDFs:** `python make_pdfs.py`
5. **Prices (optional):** copy `store_prices.example.csv` to `store_prices.csv` and type in your own prices. The example prices are made up.

## About the price data (read this first)
- **Almost every price here is fake or a guess.** `estimated_prices_NOT_REAL.*` and
  `showcase_prices_EXAMPLE_made_up.*` are labelled as such in every file and on every page.
  Do not use them for shopping or budgeting.
- **One price is checked:** eggs, large Grade A, about $2.58 per dozen. This is the US Bureau of
  Labor Statistics national average for January 2026, so it is several months old and local prices differ.
- **The grocery amounts do not need prices.** The page shows the amount to buy. It also shows a made-up price guess beside each item, labelled NOT REAL, because you asked for one.
- **To use your own prices**, type them into a CSV with the columns `item,pack_size,price`, using the size
  printed on the package. Prices you type in stay in your own browser or your own files.
- **Store websites are not scraped.** Most stores forbid automated collection of their prices and catalogues
  in their terms. Prices here are typed in by hand, or come from public government data.

## Your own data and keys
- `pantry.json`, `store_prices.csv`, `.env` and `all_items.csv` are in `.gitignore`. Keep your personal lists
  and keys out of any public copy.

## What the class taught that shaped this project
Notes written in our own words from the class lessons. Teacher materials are not copied here.
- **Week 5 (agents):** an agent picks a tool by reading its description, so each tool's name and
  description must say exactly what it does. Our three tools are written that way.
- **Week 5 (safety):** a person should approve anything risky before it happens, and a loop needs a step
  limit. The checker never changes a shopping list or a store account on its own.
- **Week 6 (automation):** login details live in saved credentials, not in files. This is why `.env`
  is ignored by git.

## Photo of a recipe (on the live page)
1. Open the live page (below). Under "Add a recipe", press **Choose a recipe photo** (on a phone this opens the camera).
2. Wait for the reading to finish. The ingredient lines appear in the recipe box.
3. Check and fix any lines, then press **Check this recipe**.

The reading runs in your browser with the free Tesseract.js library. The library is downloaded from a public CDN (cdn.jsdelivr.net) only when you choose a photo, and it is checked against a fingerprint before it runs.
The photo is not uploaded to any server. Clear, straight, well-lit photos work best; a handwritten or curved recipe may need typing.
Tested on a made-up printed recipe: all five ingredient lines were read correctly.

## Live page
The checker also runs online with no install: https://wanderer-afk.github.io/recipe-shopping-agent/
(GitHub Pages serves `index.html` as a web page. Your answers stay in your own browser.)

## AI step (agent.py)
The agent reads your question, picks one of the three tools, runs it, and repeats for at most 6 steps.
It only reads recipes and prices; it never changes a list. It needs no API key.
1. Install Ollama (free) from https://ollama.com and run `ollama pull gemma3:12b`.
2. Run `python agent.py "What do I need to buy for Sample Pancakes.md?"`.
Tested once on the sample recipe: it used the shopping split tool and listed milk, large eggs, butter and maple syrup.
Other local models can be chosen with the `OLLAMA_MODEL` setting.

## Limits
- The AI step has been tested on one question only. Small local models can pick the wrong tool.
- Name matching is by plain text. "Milk" and "whole milk" match, but a different word for the same food may not.
- Bunches, cans, bags and rolls are counted as whole items (for example 'at least 1' bunch or 2 cans). Nothing is guessed about their weight.
- The page has been tested in a desktop browser. It has not been tested on a phone.

## Files and privacy
Your recipes, photos and answers are never uploaded. The page loads a free text reader and PDF reader from a public CDN (cdn.jsdelivr.net, cdnjs.cloudflare.com) when you choose a photo or PDF. Saved answers and your last recipe are kept in the browser on
your own computer.
