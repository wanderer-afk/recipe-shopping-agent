"""Builds report.pdf: the project report for Our Kitchen Grocery Book (Recipe Shopping Checker).

Usage:  python make_report.py [output_folder]
Needs reportlab (see requirements.txt).
"""

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
st = getSampleStyleSheet()
body = st["BodyText"]
small = body.clone("small")
small.fontSize = 9
cell = body.clone("cell")
cell.fontSize = 9
cell.leading = 11

story = [
    Paragraph("Our Kitchen Grocery Book: project report", st["Title"]),
    Paragraph("Recipe Shopping Checker, a student project in Codecademy's Building Agentic AI Applications course. "
              "Live page: https://wanderer-afk.github.io/recipe-shopping-agent/ . Code: https://github.com/wanderer-afk/recipe-shopping-agent", small),
    Spacer(1, 10),

    Paragraph("1. The problem", st["Heading2"]),
    Paragraph("People plan a meal, then shop from a list that is in the wrong units, or repeats an ingredient, or forgets what they already have. "
              "This tool takes a recipe (typed, pasted, a photo, or a PDF), asks what is already at home, and gives one grocery list, "
              "grouped by aisle, in amounts a shop actually sells (for example 'at least 2 tbsp' or 'at least 6 oz').", body),
    Spacer(1, 6),

    Paragraph("2. How it works", st["Heading2"]),
    Paragraph("<b>The page</b> (index.html) reads each line into an amount and an item, merges items that share a name, "
              "converts dry goods to weight (1 cup of flour is about 120 g), and rounds up to a shop size. "
              "Photos and PDFs are read in the browser: text PDFs by their text layer, photos and scanned pages by Tesseract.js (OCR). "
              "Nothing you type or photograph is uploaded.", body),
    Paragraph("<b>The Python tools</b> read the same recipe tables from a folder: recipe_reader.py (the table), shopping_list.py "
              "(buy versus check at home), pack_picker.py (the cheapest pack that covers an amount).", body),
    Paragraph("<b>The agent</b> (agent.py) is a small tool loop. A local model (Ollama, gemma3:12b) reads a question and picks one tool "
              "(read_recipe, shopping_split, pick_pack), the program runs it, sends the result back, and repeats. "
              "Guards: the model may only call the three named tools; a reply that is not a JSON object stops the run; "
              "a bad call is reported back to the model; the loop stops after 6 steps; recipe paths must be a .md file directly inside the recipe folder. "
              "The agent only reads data and never changes a list.", body),
    Spacer(1, 6),

    Paragraph("3. Diagram: the agent loop", st["Heading2"]),
]

loop = Table(
    [["1. Your question"], ["2. Model picks ONE tool and inputs (JSON)"], ["3. Guard: known tool? valid inputs? inside the recipe folder?"],
     ["4. Tool runs (read_recipe / shopping_split / pick_pack)"], ["5. Result sent back to the model"], ["6. Model answers, or step 2 again (max 6 steps)"]],
    colWidths=[400],
)
loop.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#6f8f5e")),
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f1e6")),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
]))
story += [loop, Spacer(1, 8)]

story += [
    Paragraph("4. Tests and real runs", st["Heading2"]),
]
results = [
    ["Check", "Result"],
    ["Python unit tests (python -m unittest discover -s tests)", "8 of 8 pass: recipe reading, amounts, pack picking, path guard"],
    ["Sample recipes (10 table recipes) through the page's parser", "All 10 read; every row has an amount and an aisle"],
    ["Long recipe (75 lines, 25 unique items)", "75 rows in, 75 rows out; items grouped to the right aisle"],
    ["Pasted website text (headings, servings, method steps)", "Headings and method lines are dropped; amounts like '2 tbsp + 1/4 tsp' keep the first part"],
    ["Photo of a plain grocery list, and a PDF recipe, in the live page", "Both added to the same list in a browser test"],
    ["Agent on a sample question (gemma3:12b, local)", "Answered the 'what to buy' question from the shopping-split tool"],
    ["Agent asked about a price with no price file", "Said no price was available; did not invent one"],
]
t = Table([[Paragraph(a, cell), Paragraph(b, cell)] for a, b in results], colWidths=[230, 270])
t.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c9b89a")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9e2cc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
story += [t, Spacer(1, 8)]

story += [
    Paragraph("5. What is not done (honest limits)", st["Heading2"]),
    Paragraph("The AI agent is command-line only and needs Ollama and a model on your own computer; the live page does not use the agent. "
              "Prices are made up for practice and labelled that way; the only checked price is eggs (US government average, January 2026). "
              "Recipes are marked untested. The page is tested in a desktop browser, not on a phone. Name matching is by text, so an unusual "
              "spelling can stay as a separate row. Two-column PDFs can merge columns. Printing is a list-only print view.", body),
    Spacer(1, 6),

    Paragraph("6. What I would do next", st["Heading2"]),
    Paragraph("Teach the page to use the same tables as the Python tools; add a tick-off mode for shopping; add per-recipe servings; "
              "test on a phone; and cook two sample recipes to replace the untested amounts with measured ones.", body),
]

doc = SimpleDocTemplate(str(OUT / "report.pdf"), pagesize=letter, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50,
                        title="Our Kitchen Grocery Book: project report", author="Bailey")
doc.build(story)
print("wrote", OUT / "report.pdf")
