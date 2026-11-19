
"use strict";

// ---------- units: every amount becomes one base unit per family (grams, millilitres, or each) ----------
const UNITS = {
  "g": ["mass", 1], "gram": ["mass", 1], "grams": ["mass", 1], "kg": ["mass", 1000],
  "oz": ["mass", 28.3495], "ounce": ["mass", 28.3495], "ounces": ["mass", 28.3495],
  "lb": ["mass", 453.592], "lbs": ["mass", 453.592], "pound": ["mass", 453.592], "pounds": ["mass", 453.592],
  "ml": ["volume", 1], "l": ["volume", 1000], "liter": ["volume", 1000], "liters": ["volume", 1000],
  "tsp": ["volume", 4.929], "tbsp": ["volume", 14.787],
  "cup": ["volume", 236.588], "cups": ["volume", 236.588],
  "fl oz": ["volume", 29.5735], "pint": ["volume", 473.176], "pints": ["volume", 473.176],
  "qt": ["volume", 946.353], "quart": ["volume", 946.353],
  "gal": ["volume", 3785.41], "gallon": ["volume", 3785.41], "gallons": ["volume", 3785.41],
  "each": ["count", 1], "clove": ["count", 1], "cloves": ["count", 1], "egg": ["count", 1], "eggs": ["count", 1],
  "slice": ["count", 1], "slices": ["count", 1], "pod": ["count", 1], "pods": ["count", 1]
};
const UNIT_NAMES = Object.keys(UNITS).sort((a, b) => b.length - a.length);

// "2 1/4" -> 2.25 ; "1/3" -> 0.333 ; "2" -> 2. Returns null if not a number.
function parseNumber(text) {
  const t = text.trim();
  const m = t.match(/^(\d+)\s+(\d+)\/(\d+)$/);
  if (m) return Number(m[1]) + Number(m[2]) / Number(m[3]);
  const f = t.match(/^(\d+)\/(\d+)$/);
  if (f) return Number(f[1]) / Number(f[2]);
  if (/^\d+(\.\d+)?$/.test(t)) return Number(t);
  return null;
}

// Splits "1 1/2 cups milk" into {family, base, name}. A bare "2 eggs" counts as each.
// Returns null when no amount is found at the start of the line.
function parseAmount(line) {
  const s = line.trim().replace(/\s+/g, " ");
  const qty = s.match(/^(\d+\s+\d+\/\d+|\d+\/\d+|\d+(?:\.\d+)?)\s*(.*)$/);
  if (!qty) return null;
  const amount = parseNumber(qty[1]);
  if (amount === null) return null;
  const rest = qty[2];
  for (const unit of UNIT_NAMES) {
    if (rest.toLowerCase() === unit || rest.toLowerCase().startsWith(unit + " ")) {
      const [family, factor] = UNITS[unit];
      return { family, base: amount * factor, name: rest.slice(unit.length).trim() || rest, amountText: `${qty[1]} ${unit}` };
    }
  }
  return { family: "count", base: amount, name: rest, amountText: qty[1] };
}

// ---------- storage: one small saved value per key, with a fallback if the browser blocks storage ----------
function load(key, fallback) {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
}
function save(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* storage blocked: the page still works, nothing is remembered */ }
}

// ---------- price list ----------
function parsePriceLines(text) {
  const rows = [];
  const bad = [];
  text.split(/\r?\n/).forEach((raw, i) => {
    const line = raw.trim();
    if (!line || /^item,/i.test(line)) return;
    const parts = line.split(",").map(p => p.trim());
    if (parts.length !== 3) { bad.push(`line ${i + 1}: needs item,pack size,price`); return; }
    const [item, pack, priceText] = parts;
    const size = parseAmount(pack);
    const price = Number(priceText);
    if (!size || !Number.isFinite(price)) { bad.push(`line ${i + 1}: pack size or price not readable`); return; }
    rows.push({ item: item.toLowerCase(), pack, price, family: size.family, base: size.base });
  });
  return { rows, bad };
}

// The cheapest total that covers the amount; leftovers count. Ties become ASK.
function pickPacks(need, packs) {
  const usable = packs.filter(p => p.family === need.family);
  if (usable.length === 0) return { status: "CHECK", reason: "pack units do not match this amount" };
  const options = usable.map(p => {
    const count = Math.max(1, Math.ceil(need.base / p.base - 1e-9));
    return { pack: p.pack, count, total: Math.round(count * p.price * 100) / 100, leftover: count * p.base - need.base };
  }).sort((a, b) => a.total - b.total || a.count - b.count || a.leftover - b.leftover);
  const best = options[0];
  const tied = options.filter(o => o.total === best.total && o.count === best.count);
  if (tied.length > 1) return { status: "ASK", reason: "same cost: " + tied.map(t => t.pack).join(" or ") };
  return { status: "OK", ...best };
}


const t=[parseAmount('1 1/2 cups milk'),parseAmount('2 eggs'),parseAmount('1/8 tsp nutmeg')];
console.log(JSON.stringify(t));
const p=parsePriceLines('whole milk,1 gal,4.50
whole milk,1 qt,1.40
heavy cream,1 pint,3.25');
console.log(JSON.stringify(p.bad), JSON.stringify(pickPacks(parseAmount('1 1/2 cups milk'), p.rows.filter(r=>r.item==='whole milk'))));
console.log(JSON.stringify(pickPacks(parseAmount('2 cups heavy cream'), p.rows.filter(r=>r.item==='heavy cream'))));
