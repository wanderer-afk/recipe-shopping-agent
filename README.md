# Our Kitchen Grocery Book (Recipe Shopping Checker)

Paste a recipe, or take a photo of one. Tell the checker what you already have at home, and it gives you a
grocery list with amounts rounded up to shop-friendly sizes, like "at least 2 tbsp" or "at least 6 oz". These are rounded amounts, not always real pack sizes.
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

## How the checker works (the short version)
1. **Input:** you paste a recipe, pick a photo, or pick a PDF. Each recipe heading becomes its own recipe.
2. **Reading:** each line is split into an amount and an item. "2 tbsp + 1/4 tsp" is added together, "1x 400g can chickpeas" is one can, and headings, website text and symbols are dropped.
3. **Naming:** item names are cleaned so "Sugr", "sugar" and "2 tsp sugar (packed)" become one item. Known typos and plurals are fixed.
4. **Merging:** the same item from several recipes is added up, then rounded up to a shop-friendly size ("at least 6 oz").
5. **Your answers:** "We have it", "Want more" and "Not needed" take items off the list. Your recipes and answers are saved in your own browser only.

**How well it works (last checked):**
| Check | Result |
|---|---|
| Labelled lines (`tests/accuracy_cases.json`) | 33 of 33 right |
| Page logic tests (`node tests/test_page.js`) | 15 pass |
| Python tests (`python -m unittest discover -s tests`) | 14 pass |
| Browser checks in Microsoft Edge (`python tests/browser_flow.py`) | 69 of 69 pass |

**What the browser checks cover:** a realistic recipe pasted from a website, tricky amounts (ranges, fraction sums, half a lemon, a dozen), twelve recipes in one session, a final boss that runs all of this in one session, a full browser storage message, 300 random messy pastes, typos and junk lines, two recipes at once, a 3-page PDF, a 4-page PDF with five recipes, a single-column and a two-column photo, adding and removing items, "We have it" and "Not needed", duplicate pastes, hostile text (`<script>` is shown as text and never runs), a 2,000-line paste, saved data that survives a reload, broken saved data that does not crash the page, a phone-width layout with no sideways scroll, and keyboard-only use.

**Still weak:** photo reading still makes mistakes on poor photos; a one-word typed title with no amount counts as an item; two items on one line joined with ";" are read as one; and the page is not yet tested on a real phone.

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
   - Tap "We have it", "Want more" or "We need it" for each ingredient. Tap "Not needed" to take an item off the list (Clear all answers puts it back).
   - Add anything else you want on the list, with no recipe.
   - Dry goods written in cups (flour, sugar, rice, cheese) are converted to weight automatically. For anything else, add the grams in brackets, like `3/4 cup rice (150 g)`.
2. **The Python tools** (from this folder):
   ```
   python recipe_reader.py
   python shopping_list.py
   python pack_picker.py
   node tests/test_page.js                  # the page logic and the labelled accuracy set (needs Node.js)
   python -m unittest discover -s tests    # the tests
   python tests/browser_flow.py            # the page in Microsoft Edge (needs: pip install playwright)
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
- **The grocery amounts do not need prices.** The page shows the amount to buy. It also shows a made-up price guess beside each item, labelled NOT REAL, for practice.
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
1. Open the live page (below). Under "Add a recipe", press **Choose a recipe photo or PDF** (on a phone this can open the camera).
2. Each recipe found is added to your list as its own recipe, one per heading, so you can press **Remove** on any one of them.
3. Check the list. If a reading is wrong, Remove that recipe and type it again.

The reading runs in your browser. Photos use the free Tesseract.js library and PDFs use PDF.js. Both are downloaded from public CDNs (cdn.jsdelivr.net and cdnjs.cloudflare.com) only when you choose a file.
The two main scripts are checked against a fingerprint before they run. The workers and language data that these libraries download after that are not fingerprint-checked.
The photo is not uploaded to any server. Clear, straight, well-lit photos work best; two columns are read column by column; a handwritten or curved recipe may need typing.
Tested in Microsoft Edge with `tests/browser_flow.py` on made-up files: a 3-page PDF, a 4-page PDF with five recipes, a single-column photo and a two-column photo. The photo results are checked against the made-up text, so OCR mistakes on other photos can still happen.

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
- The page has been tested in a desktop browser and in a phone-sized browser window (375 px wide) for layout. It has not been tested on a real phone.

## Files and privacy
Your recipes, photos and answers are never uploaded. The page loads its photo reader (from cdn.jsdelivr.net) and its PDF reader (from cdnjs.cloudflare.com) only when you choose a file.
Your recipes, your "We have it" and "Not needed" choices, and your hand-added items are saved in your browser's local storage on your own computer.
On GitHub Pages, every project page on the same account shares one local storage area, so other pages on that site could read these saved lists.
