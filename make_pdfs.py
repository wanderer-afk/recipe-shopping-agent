"""Rebuild the two price PDFs from their CSV files.

Usage:  python make_pdfs.py [output_folder]

Reads average_prices_staples.csv (checked prices) and estimated_prices_NOT_REAL.csv
(rough guesses, NOT real), and writes grocery_items_and_prices.pdf and
estimated_prices_NOT_REAL.pdf. Needs reportlab (see requirements.txt).
"""

import csv
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE


def make_table(header, body, widths, header_color, row_color):
    styles = getSampleStyleSheet()
    cell = styles["BodyText"].clone("cell")
    cell.fontSize, cell.leading = 8, 10
    head = styles["BodyText"].clone("head")
    head.fontSize, head.textColor = 8.5, colors.white
    data = [[Paragraph(h, head) for h in header]]
    data += [[Paragraph(x, cell) for x in row] for row in body]
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(row_color)]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c9b89a")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def read_csv(name):
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    return rows


def build_checked():
    rows = read_csv("average_prices_staples.csv")
    header, body = rows[0], rows[1:]
    keep = [header.index(c) for c in ("item", "category", "typical_price", "source")]
    body = [[r[i] if i < len(r) else "" for i in keep] for r in body]
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(OUT / "grocery_items_and_prices.pdf"), pagesize=landscape(letter),
                            leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36,
                            title="Grocery items and prices (only checked prices filled in)")
    table = make_table(["Item", "Category", "Typical price", "Source"], body,
                       [190, 150, 130, 300], "#6f8f5e", "#f4f1e6")
    doc.build([
        Paragraph("Grocery items and prices (only checked prices filled in)", styles["Heading2"]),
        Paragraph("Only eggs has a checked public price: the US Bureau of Labor Statistics national average, "
                  "January 2026 (several months old). Every other price is blank because it has not been checked. "
                  "Local prices differ.", styles["BodyText"]),
        Spacer(1, 8), table])


def build_estimates():
    rows = read_csv("estimated_prices_NOT_REAL.csv")
    banner, header, body = rows[0], rows[1], rows[2:]
    styles = getSampleStyleSheet()
    warn = styles["BodyText"].clone("warn")
    warn.fontSize, warn.textColor = 10, colors.HexColor("#8b1e1e")
    doc = SimpleDocTemplate(str(OUT / "estimated_prices_NOT_REAL.pdf"), pagesize=landscape(letter),
                            leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36,
                            title="Estimated prices (NOT REAL)")
    table = make_table(header, body, [190, 140, 140, 110, 240], "#8b1e1e", "#f7eeee")
    disclaimer = ("<b>THESE PRICES ARE NOT REAL AND NOT ACCURATE.</b> They are rough guesses from general knowledge, "
                  "not checked against any store, and not averages from any survey. The only checked price is eggs at "
                  "$2.58 per dozen (US Bureau of Labor Statistics national average, January 2026), on the checked sheet. "
                  "Do not use these for shopping or budgeting.")
    doc.build([Paragraph("Estimated prices (NOT REAL, NOT ACCURATE)", styles["Heading2"]), Spacer(1, 6),
               table, Spacer(1, 10), Paragraph(disclaimer, warn)])


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    build_checked()
    build_estimates()
    print(f"wrote PDFs to {OUT}")
