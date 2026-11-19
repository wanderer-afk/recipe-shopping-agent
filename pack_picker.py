"""Step 4 of the Recipe-to-Shopping agent: pick the packs to buy.

For each item on the buy list, look at the store's pack sizes and prices in
store_prices.csv, then pick the cheapest total that covers the amount needed.
Leftover is counted, because a pack you cannot use is money spent.

If two choices cost the same, the item is marked ASK instead of guessed.

No AI here. The agent will call pick_packs() later as a tool.
"""

import csv
import math
import re
from fractions import Fraction
from pathlib import Path

PRICES_FILE = Path(__file__).parent / "store_prices.csv"

# Every unit converts to one base unit per family: grams, millilitres, or each.
UNITS = {
    "g": ("mass", 1.0), "gram": ("mass", 1.0), "grams": ("mass", 1.0),
    "kg": ("mass", 1000.0),
    "oz": ("mass", 28.3495), "ounce": ("mass", 28.3495), "ounces": ("mass", 28.3495),
    "lb": ("mass", 453.592), "lbs": ("mass", 453.592), "pound": ("mass", 453.592),
    "ml": ("volume", 1.0), "l": ("volume", 1000.0),
    "tsp": ("volume", 4.929), "tbsp": ("volume", 14.787),
    "cup": ("volume", 236.588), "cups": ("volume", 236.588),
    "fl oz": ("volume", 29.5735),
    "qt": ("volume", 946.353), "gal": ("volume", 3785.41),
    "each": ("count", 1.0), "clove": ("count", 1.0), "cloves": ("count", 1.0),
    "pod": ("count", 1.0), "slice": ("count", 1.0), "slices": ("count", 1.0),
    "egg": ("count", 1.0), "eggs": ("count", 1.0),
}

# Longest first, so "fl oz" is matched before "oz".
_UNIT_PATTERN = "|".join(sorted((re.escape(u) for u in UNITS), key=len, reverse=True))
_AMOUNT = re.compile(
    rf"^\s*(?P<qty>\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)\s*(?P<unit>{_UNIT_PATTERN})\b",
    re.IGNORECASE,
)


def parse_quantity(text: str) -> float | None:
    """Turn '2 1/4' or '2/3' or '1.5' into a number. Returns None if it is not a number."""
    text = text.strip()
    try:
        return float(sum(Fraction(part) for part in text.split()))
    except (ValueError, ZeroDivisionError):
        return None


def to_base(amount_text: str) -> tuple[str, float] | None:
    """Turn '3 tbsp' or '18 oz' into (family, base amount). Returns None if unclear."""
    match = _AMOUNT.match(amount_text)
    if not match:
        # A bare number such as "2" or "1/2" is a count of things, like eggs.
        qty = parse_quantity(amount_text)
        return ("count", qty) if qty is not None else None
    qty = parse_quantity(match.group("qty"))
    if qty is None:
        return None
    family, factor = UNITS[match.group("unit").lower()]
    return family, qty * factor


def load_prices(path: Path = PRICES_FILE) -> dict[str, list[dict]]:
    """Read store_prices.csv: one row per pack size, grouped by item name in lower case."""
    if not path.exists():
        return {}
    options: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            base = to_base(row["pack_size"])
            if base is None or not row["price"].strip():
                continue  # a pack with no readable size or no price is skipped, not guessed
            options.setdefault(row["item"].strip().lower(), []).append({
                "pack_size": row["pack_size"].strip(),
                "price": float(row["price"]),
                "family": base[0],
                "base": base[1],
            })
    return options


def pick_packs(item: str, need_text: str, options: dict[str, list[dict]]) -> dict:
    """Return the best pack choice for one item, or a reason it cannot be chosen."""
    need = to_base(need_text)
    if need is None:
        return {"item": item, "status": "CHECK", "reason": f"amount '{need_text}' is not in a unit this tool knows"}
    packs = options.get(item.lower())
    if not packs:
        return {"item": item, "status": "NO PRICE", "reason": "no pack sizes in store_prices.csv yet"}

    family, needed = need
    usable = [p for p in packs if p["family"] == family]
    if not usable:
        return {"item": item, "status": "CHECK", "reason": "pack units do not match the recipe amount (for example, weight vs volume)"}

    scored = []
    for p in usable:
        count = max(1, math.ceil(needed / p["base"]))
        leftover = count * p["base"] - needed
        total = count * p["price"]
        scored.append({"pack": p["pack_size"], "packs": count, "total": round(total, 2), "leftover": leftover})

    scored.sort(key=lambda s: (s["total"], s["packs"], s["leftover"]))
    best = scored[0]
    tied = [s for s in scored if s["total"] == best["total"] and s["packs"] == best["packs"]]
    if len(tied) > 1:
        return {"item": item, "status": "ASK", "reason": "two pack choices cost the same: " + ", ".join(s["pack"] for s in tied)}
    return {"item": item, "status": "OK", **best}


def main() -> None:
    from shopping_list import load_pantry
    from recipe_reader import RECIPE_FOLDER, read_grocery_lines

    recipe = RECIPE_FOLDER / "Sample Pancakes.md"
    pantry = load_pantry()
    options = load_prices()
    for row in read_grocery_lines(recipe):
        if row["flag"] != "no" or row["item"].lower() in pantry:
            continue
        result = pick_packs(row["item"], row["amount"], options)
        print(result)


if __name__ == "__main__":
    main()
