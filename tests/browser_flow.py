"""Browser tests for the page (index.html): real clicks, uploads and typing in Microsoft Edge.

Usage:  python tests/browser_flow.py  [path_to_test_files]
Needs:  pip install playwright   (uses the Edge already on this PC; no browser download)
Test files (PDF, photo, messy paste) are passed in as a folder; see the README.
Exit code 0 means every check passed.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = (Path(__file__).resolve().parent.parent / "index.html").as_uri()
FILES = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "fixtures"
RESULTS = []

def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (("  -- " + detail) if detail and not ok else ""))

def list_text(page):
    return page.locator("#list-body").inner_text()

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(PAGE)

    # 1. Typed recipe with typos and junk lines: the list shows merged, spelled-right items.
    page.fill("#recipe", "Chicken Katsu\nServes 4\n2 eggs, beaten\n1 tbsp sugr\n2 garlc cloves\n3 cloves garlic\nAdvertisement")
    page.click("#check")
    page.wait_for_timeout(300)
    txt = list_text(page)
    check("typed recipe: sugar spelled right", "sugar" in txt and "sugr" not in txt, txt[:200])
    check("typed recipe: junk lines dropped", "Advertisement" not in txt and "Serves" not in txt)
    check("typed recipe: garlic merged (2 + 3 cloves = at least 5)", "at least 5 cloves" in txt, txt[:300])

    # 2. A second recipe is added alongside the first (multiple recipes).
    page.fill("#recipe", "Aloo Gobi\n600 g cauliflower florets\n1 tsp ground turmeric\n1/2 tsp tumeric")
    page.click("#check")
    page.wait_for_timeout(300)
    txt = list_text(page)
    check("second recipe: cauliflower on the list", "cauliflower" in txt)
    check("second recipe: turmeric merged (1 tsp + 1/2 tsp)", txt.count("turmeric") == 1, "turmeric appears %d times" % txt.count("turmeric"))
    recipes_box = page.locator("#recipe-list").inner_text()
    check("two recipes listed", recipes_box.count("ingredients") >= 2, recipes_box[:200])

    # 3. Three-page PDF with different recipes: every recipe's items are read.
    pdf = FILES / "round8_three_pages.pdf"
    page.set_input_files("#photo", str(pdf))
    page.wait_for_function("document.querySelector('#scan-status') && document.querySelector('#scan-status').textContent.length > 0", timeout=60000)
    page.wait_for_timeout(1500)
    txt = list_text(page)
    check("3-page PDF: pad see ew noodles read (page 1)", "noodle" in txt.lower(), txt[:200])
    check("3-page PDF: black beans read (page 2)", "black bean" in txt.lower())
    check("3-page PDF: panko read (page 3, second recipe on that page)", "panko" in txt.lower())

    # 4. Photo with printed text: OCR reads it (needs the Tesseract library from the internet).
    page.set_input_files("#photo", str(FILES / "round8_photo_aloo.png"))
    try:
        page.wait_for_function("document.querySelector('#list-body') && document.querySelector('#list-body').innerText.toLowerCase().includes('garam')", timeout=180000)
        check("photo: garam masala from the photo is on the list", True)
    except Exception as e:
        check("photo: garam masala from the photo is on the list", False, page.locator("#scan-status").inner_text()[:120])

    # 5. Add items by hand and remove them again.
    page.fill("#want-input", "dish soap")
    page.click("#want-add")
    page.wait_for_timeout(200)
    check("hand-added item appears", "dish soap" in page.locator("#want-list").inner_text())
    page.locator("#want-list li", has_text="dish soap").get_by_role("button", name="Remove").click()
    page.wait_for_timeout(200)
    check("hand-added item removed", "dish soap" not in page.locator("#want-list").inner_text())

    # 6. Take one recipe off the list.
    before = page.locator("#recipe-list").inner_text().count("ingredients")
    page.locator("#recipe-list button", has_text="Remove").first.click()
    page.wait_for_timeout(300)
    after = page.locator("#recipe-list").inner_text().count("ingredients")
    check("remove a recipe: count goes down", after == before - 1, "before %d after %d" % (before, after))

    # 7. Mark an item "We have it" and it leaves the shopping list.
    page.wait_for_timeout(200)
    txt_before = list_text(page)
    row = page.locator("#have-body tr").nth(1)
    item = row.locator("td").first.inner_text().strip()
    row.get_by_role("button", name="We have it").click()
    page.wait_for_timeout(300)
    check("We have it: item leaves the shopping list", item and item not in list_text(page), "item %r still listed" % item)

    # 8. Empty recipe does not break the page.
    page.fill("#recipe", "")
    page.click("#check")
    page.wait_for_timeout(200)
    check("empty recipe: no crash", not errors, "; ".join(errors)[:200])

    # 9. Clear the whole list.
    page.click("#clear-pantry")
    page.wait_for_timeout(300)
    check("clear answers: answers are really gone", "Not answered yet" in page.locator("#have-body").inner_text(), page.locator("#have-body").inner_text()[:200])

    # 10. Paste the whole messy fixture (titles, junk, typos) in one go.
    page.fill("#recipe", (FILES / "messy_r8.txt").read_text(encoding="utf-8"))
    page.click("#check")
    page.wait_for_timeout(300)
    txt = list_text(page)
    check("messy fixture: no title 'Minestrone' as an item", "minestrone" not in txt.lower(), txt[:200])
    check("messy fixture: junk 'Calories' not an item", "calories" not in txt.lower())
    check("messy fixture: 'soy sauce' spelled right", "soy saus" not in txt.lower() and "dark soy sauce" in txt.lower())

    # 11. The same recipe pasted again (extra spaces, lines reordered) is not added twice.
    page.fill("#recipe", "Chicken Katsu\nServes 4\n2 eggs, beaten\n1 tbsp sugr\n2 garlc cloves\n3 cloves garlic\nAdvertisement")
    page.click("#check")
    page.wait_for_timeout(200)
    before = page.locator("#recipe-list").inner_text().count("ingredients")
    page.fill("#recipe", "  3 cloves garlic  \n1 tbsp sugr\n2 garlc cloves\nAdvertisement\n2 eggs, beaten\nServes 4\nChicken Katsu")
    page.click("#check")
    page.wait_for_timeout(200)
    after = page.locator("#recipe-list").inner_text().count("ingredients")
    check("duplicate paste with extra spaces and lines reordered is not added again", after == before, "before %d after %d" % (before, after))

    # 12. "Not needed" takes one item off the shopping list; "Clear all answers" puts it back.
    first_item = page.locator("#list-body tr.dotted").first.locator("td").first.inner_text().split("\n")[0].strip()
    page.locator("#list-body tr.dotted").first.get_by_role("button", name="Not needed").click()
    page.wait_for_timeout(300)
    check("not needed: item leaves the list", first_item not in list_text(page), first_item)
    page.click("#clear-pantry")
    page.wait_for_timeout(300)
    check("not needed: clear answers puts it back", first_item in list_text(page), first_item)

    # 13. Round 9: a 4-page PDF with five recipes (one page has two). Each heading becomes its own recipe, not an item.
    page.set_input_files("#photo", str(FILES / "round9_four_pages.pdf"))
    page.wait_for_function("document.querySelector('#scan-status').textContent.startsWith('Found')", timeout=90000)
    page.wait_for_timeout(500)
    rec = page.locator("#recipe-list").inner_text()
    check("5-recipe PDF: five recipes on the list", "Recipes on your list" in rec and rec.count("ingredients)") >= 5, rec[:200])
    item_names = [r.split("\t")[0].replace("Not needed", "").strip().lower() for r in list_text(page).split("\n") if "\t" in r]
    check("5-recipe PDF: headings are not items", not any(h in item_names for h in ["japchae", "spanakopita", "chilaquiles rojos", "tom yum goong", "chicken tikka masala"]), str(item_names)[:200])

    # 14. Round 9: a two-column photo is read column by column.
    page.set_input_files("#photo", str(FILES / "round9_photo_two_columns.png"))
    try:
        page.wait_for_function("document.querySelector('#list-body').innerText.toLowerCase().includes('sesame oil')", timeout=180000)
        check("two-column photo: sesame oil read from the left column", True)
    except Exception:
        check("two-column photo: sesame oil read from the left column", False, page.locator("#scan-status").inner_text()[:120])
    check("two-column photo: fish sauce is its own row", "fish sauce" in list_text(page).lower())

    # 16. Round 10: a 3-page PDF where Carbonara continues onto page 2 with no heading, and Gazpacho starts page 3.
    page.set_input_files("#photo", str(FILES / "round10_three_pages.pdf"))
    page.wait_for_timeout(7000)
    rec10 = page.locator("#recipe-list").inner_text()
    check("3-page PDF: Carbonara and Gazpacho are two recipes", "Carbonara (6 ingredients)" in rec10 and "Gazpacho (4 ingredients)" in rec10, rec10[:200])
    names10 = [r.split("\t")[0].replace("Not needed", "").strip().lower() for r in list_text(page).split("\n") if "\t" in r]
    check("3-page PDF: no recipe title is an item", "carbonara" not in names10 and "gazpacho" not in names10, str(names10)[:200])
    check("3-page PDF: page-2 ingredients joined to Carbonara (pecorino on the list)", any("pecorino" in n for n in names10))

    # 15. Round 9: buttons say which item they are for (screen readers), and the picked answer is marked.
    first_not_needed = page.locator("#list-body button", has_text="Not needed").first
    check("Not needed button has an item label", (first_not_needed.get_attribute("aria-label") or "").startswith("Not needed: "))
    first_have = page.locator("#have-body button", has_text="We have it").first
    check("answer buttons have aria-pressed", first_have.get_attribute("aria-pressed") in ("true", "false"))
    check("scan status is announced (aria-live)", page.locator("#scan-status").get_attribute("aria-live") == "polite")

    browser.close()

failed = [n for n, ok in RESULTS if not ok]
print("%d of %d browser checks passed" % (len(RESULTS) - len(failed), len(RESULTS)))
sys.exit(1 if failed else 0)
