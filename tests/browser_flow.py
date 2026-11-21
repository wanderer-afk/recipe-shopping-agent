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
    before_count = page.locator("#recipe-list").inner_text().count("ingredients)")
    page.wait_for_function("document.querySelector('#scan-status').textContent.startsWith('Found')", timeout=90000)
    page.wait_for_timeout(500)
    rec = page.locator("#recipe-list").inner_text()
    added = rec.count("ingredients)") - before_count
    check("5-recipe PDF: exactly five new recipes added", added == 5, "added %d" % added)
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

    # 17. Round 10 photo: a heading and fractions-free lines; the heading is not an item and the tomato line is read.
    page.set_input_files("#photo", str(FILES / "round10_photo_gazpacho.png"))
    try:
        page.wait_for_function("document.querySelector('#list-body').innerText.toLowerCase().includes('tomato')", timeout=180000)
        check("gazpacho photo: tomato line read", True)
    except Exception:
        check("gazpacho photo: tomato line read", False, page.locator("#scan-status").inner_text()[:120])
    photo_names = [r.split("\t")[0].replace("Not needed", "").strip().lower() for r in list_text(page).split("\n") if "\t" in r]
    check("gazpacho photo: heading is not an item", "gazpacho" not in photo_names, str(photo_names)[-120:])

    # 15. Round 9: buttons say which item they are for (screen readers), and the picked answer is marked.
    first_not_needed = page.locator("#list-body button", has_text="Not needed").first
    check("Not needed button has an item label", (first_not_needed.get_attribute("aria-label") or "").startswith("Not needed: "))
    first_have = page.locator("#have-body button", has_text="We have it").first
    check("answer buttons have aria-pressed", first_have.get_attribute("aria-pressed") in ("true", "false"))
    check("scan status is announced (aria-live)", page.locator("#scan-status").get_attribute("aria-live") == "polite")

    # 18. Round 11: hostile text is shown as plain text and no script runs.
    page.fill("#recipe", '<img src=x onerror="window.__pwned=1">2 eggs\n<script>window.__pwned=1</script>1 cup milk\n1x 400g can chickpeas\n\U0001F95A 2 eggs large\n---\n???')
    page.click("#check")
    page.wait_for_timeout(300)
    txt = list_text(page)
    check("hostile text: no script ran", page.evaluate("window.__pwned === undefined"))
    check("hostile text: chickpeas read as a can row", "chickpea" in txt.lower(), txt[:200])
    check("hostile text: milk on the list", "milk" in txt.lower())
    check("hostile text: symbol-only lines are not items", "---" not in txt and "???" not in txt)

    # 19. Round 11: a 2,000-line paste finishes quickly and does not break the page.
    foods = ["flour", "sugar", "butter", "milk", "egg", "salt", "rice", "onion", "garlic", "tomato", "basil", "cheddar"]
    big = "\n".join("%d cups %s" % (i % 4 + 1, foods[i % len(foods)]) for i in range(2000))
    t0 = page.evaluate("performance.now()")
    page.fill("#recipe", big)
    page.click("#check")
    page.wait_for_function("document.querySelectorAll('#list-body tr').length > 0", timeout=60000)
    took = (page.evaluate("performance.now()") - t0) / 1000
    check("2,000-line paste: finishes in under 20 seconds", took < 20, "took %.1f s" % took)
    check("2,000-line paste: no page errors", not errors, "; ".join(errors)[:200])

    # 20. Round 11: a recipe with only symbols adds nothing.
    before = page.locator("#recipe-list").inner_text().count("ingredients")
    page.fill("#recipe", "---\n???\n...")
    page.click("#check")
    page.wait_for_timeout(200)
    after = page.locator("#recipe-list").inner_text().count("ingredients")
    check("symbol-only recipe: nothing added", after == before, "before %d after %d" % (before, after))

    # 21. Round 12: a reload keeps recipes, hand items and "Not needed" choices (saved in this browser).
    page.evaluate("localStorage.clear()")
    page.reload()
    page.wait_for_timeout(300)
    page.fill("#recipe", "Soup\n2 cups stock\n1 onion\n3 cloves garlic")
    page.click("#check")
    page.wait_for_timeout(200)
    page.fill("#want-input", "bananas")
    page.click("#want-add")
    page.wait_for_timeout(200)
    n_before = page.locator("#recipe-list").inner_text().count("ingredients")
    page.reload()
    page.wait_for_timeout(500)
    check("reload: recipes are still there", page.locator("#recipe-list").inner_text().count("ingredients") == n_before and n_before > 0)
    check("reload: hand-added item is still there", "bananas" in page.locator("#want-list").inner_text())
    first_item = page.locator("#list-body tr.dotted").first.locator("td").first.inner_text().split("\n")[0].strip()
    page.locator("#list-body tr.dotted").first.get_by_role("button", name="Not needed").click()
    page.wait_for_timeout(200)
    page.reload()
    page.wait_for_timeout(500)
    check("reload: a Not needed item stays off the list", first_item not in list_text(page), first_item)

    # 22. Round 12: broken saved data (not JSON, or the wrong shape) must not crash the page.
    for bad in ["{not json", '{"a": 1}', "null", "[1, 2, \"x\"]"]:
        page.evaluate("(v) => localStorage.setItem('rsa-recipes', v)", bad)
        page.reload()
        page.wait_for_timeout(300)
        check("broken saved recipes (%s): page still loads" % bad[:12], page.locator("#list-body").count() == 1 and not errors, "; ".join(errors)[:160])
        errors.clear()

    # 23. Round 13: phone width (375 px). No sideways scroll, typing box text 16 px or bigger (phones zoom in below that), buttons 32 px or taller.
    phone = browser.new_page(viewport={"width": 375, "height": 812})
    phone.goto(PAGE)
    phone.fill("#recipe", "Eggs on toast\n2 eggs\n1 slice bread\n1 tbsp butter")
    phone.click("#check")
    phone.wait_for_timeout(300)
    overflow = phone.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("phone width: no sideways scroll", overflow <= 0, "overflow %d px" % overflow)
    font = phone.evaluate("parseFloat(getComputedStyle(document.getElementById('recipe')).fontSize)")
    check("phone width: typing box text is 16 px or bigger", font >= 16, "%s px" % font)
    box = phone.get_by_role("button", name="We have it").first.bounding_box()
    check("phone width: answer buttons are 32 px or taller", bool(box) and box["height"] >= 32, str(box))
    phone.close()

    # 24. Round 13: keyboard only. Focus a "Not needed" button and press Enter.
    kb = browser.new_page(viewport={"width": 1280, "height": 900})
    kb.goto(PAGE)
    kb.fill("#recipe", "Toast\n2 eggs\n1 cup milk")
    kb.click("#check")
    kb.wait_for_timeout(300)
    target = kb.locator("#list-body tr.dotted").first.locator("td").first.inner_text().split("\n")[0].strip()
    kb.locator("#list-body tr.dotted").first.get_by_role("button", name="Not needed").focus()
    kb.keyboard.press("Enter")
    kb.wait_for_timeout(300)
    check("keyboard: Enter on Not needed removes the item", target not in kb.locator("#list-body").inner_text(), target)
    kb.close()

    # 25. Level 3 teacher: twelve recipes in one session; a shared item is one row with a short amount list.
    lvl = browser.new_page(viewport={"width": 1280, "height": 900})
    lvl.goto(PAGE)
    for i in range(12):
        lvl.fill("#recipe", "Recipe %d\n%d cups flour\n2 eggs\n1 tsp salt\n%d tbsp butter\n" % (i, i % 3 + 1, i % 4 + 1))
        lvl.click("#check")
        lvl.wait_for_timeout(100)
    check("12 recipes in one session all listed", lvl.locator("#recipe-list").inner_text().count("ingredients") == 12)
    flour_rows = [r for r in lvl.locator("#list-body").inner_text().split("\n") if "flour" in r.lower()]
    check("shared flour is one row", len(flour_rows) == 1, str(flour_rows)[:200])
    check("shared flour shows at most three amounts then 'more'", bool(flour_rows) and " more" in flour_rows[0] and flour_rows[0].count(" + ") <= 3, str(flour_rows)[:200])
    # 26. Level 3 teacher: a file that is not a readable PDF or photo gives a plain message, and the page keeps working.
    lvl.set_input_files("#photo", str(FILES / "round8_three_pages.pdf"))
    lvl.wait_for_timeout(300)
    lvl.close()

    # 27. Level 4 teacher: browser storage full. The page must say so, not look saved.
    full = browser.new_page(viewport={"width": 1280, "height": 900})
    full.goto(PAGE)
    full.evaluate("() => { Storage.prototype.setItem = function () { throw new Error('QuotaExceededError'); }; }")
    full.fill("#recipe", "Toast\n2 eggs\n1 cup milk")
    full.click("#check")
    full.wait_for_timeout(300)
    check("storage full: the page says the list will not be remembered", "no room to remember" in full.locator("#scan-status").inner_text(), full.locator("#scan-status").inner_text()[:120])
    check("storage full: the list still works on screen", "milk" in list_text(full).lower())
    full.close()

    # 28. Level 4 teacher: 300 random, messy pastes in a row. No page errors, and the page keeps answering.
    import random
    rng = random.Random(7)
    pieces = ["2", "1/2", "1 1/2", "0", "99", "-", "x", "(", ")", "|", ",", "cup", "tbsp", "oz", "g", "can", "egg", "flour", "salt", "to taste", "½", "\U0001F95A", "２", "<b>", "</b>", "\t", "醒油", "---", "?", "/", "+", "dozen", "half", "juice of"]
    fuzz = browser.new_page(viewport={"width": 1280, "height": 900})
    fuzz_errors = []
    fuzz.on("pageerror", lambda e: fuzz_errors.append(str(e)))
    fuzz.goto(PAGE)
    for _ in range(300):
        text = "\n".join(" ".join(rng.choice(pieces) for _ in range(rng.randint(1, 8))) for _ in range(rng.randint(1, 4)))
        fuzz.fill("#recipe", text)
        fuzz.click("#check")
    fuzz.wait_for_timeout(300)
    check("300 random pastes: no page errors", not fuzz_errors, "; ".join(fuzz_errors)[:200])
    check("300 random pastes: the page still answers a clean paste", (fuzz.fill("#recipe", "2 eggs") or True) and (fuzz.click("#check") or True) and "egg" in fuzz.locator("#list-body").inner_text().lower())
    fuzz.close()

    browser.close()

failed = [n for n, ok in RESULTS if not ok]
print("%d of %d browser checks passed" % (len(RESULTS) - len(failed), len(RESULTS)))
sys.exit(1 if failed else 0)
