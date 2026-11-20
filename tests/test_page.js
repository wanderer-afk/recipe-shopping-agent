// Tests for the grocery page's recipe reader. Run from the repo folder:  node tests/test_page.js
// It loads the page's own script with a small stand-in for the browser, so no browser is needed.
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const js = html.match(/<script>([\s\S]*)<\/script>/)[1];
const store = {};
global.window = global;
const stub = () => ({ value: "", textContent: "", hidden: false, className: "", style: {}, cells: [],
  addEventListener() {}, append() {}, appendChild() {}, remove() {}, click() {}, focus() {},
  querySelectorAll: () => [], querySelector: () => null });
global.document = { getElementById: () => stub(), createElement: () => stub(), body: stub(), head: stub(), querySelectorAll: () => [] };
global.localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
global.Blob = class {};
global.URL = { createObjectURL: () => "x" };
global.fetch = () => Promise.reject(new Error("no network in tests"));
eval(js + ";globalThis.__P = parseRecipeText; globalThis.__S = storeAmount; globalThis.__K = categoryOf;");

const rows = text => __P(text, "test");
let passed = 0;
function check(name, fn) { fn(); passed++; console.log("ok  " + name); }

check("a table row reads as amount then item", () => {
  const r = rows("ground beef 85% lean | 1 1/2 lb | meat | no");
  assert.strictEqual(r[0].name, "ground beef 85% lean");
  assert.strictEqual(r[0].family, "mass");
});
check("website junk and method steps are not items", () => {
  const r = rows("Jump to Recipe\nServings: 6\n2 cups flour\nMarinate the chicken for 1 hour.\nBake at 350 F for 20 minutes\n4.9 from 312 reviews");
  assert.deepStrictEqual(r.map(x => x.name), ["flour"]);
});
check("headings and markdown fences are dropped", () => {
  const r = rows("# Marry Me Chicken Pasta\n```\n2 cups flour\n```");
  assert.deepStrictEqual(r.map(x => x.name), ["flour"]);
});
check("2 tbsp + 1/4 tsp adds together (about 31 ml)", () => {
  const r = rows("2 tbsp + 1/4 tsp kosher salt");
  assert.strictEqual(r[0].key, "salt");
  assert.ok(Math.abs(r[0].base - 30.8) < 1, "base " + r[0].base);
});
check("shredded cheese is bought by weight", () => {
  const r = rows("1 cup shredded cheddar");
  assert.strictEqual(r[0].family, "mass");
});
check("a bag of potatoes is an item, not a volume", () => {
  const r = rows("1 5-lb bag potatoes");
  assert.strictEqual(r[0].key, "potato");
  assert.strictEqual(r[0].family, "count");
});
check("freezer bags are counted, not dropped", () => {
  const r = rows("1 gallon freezer bags");
  assert.strictEqual(r.length, 1);
  assert.strictEqual(r[0].family, "count");
});
check("store amounts round up and are never zero", () => {
  assert.strictEqual(__S({ family: "volume", base: 946.353 }), "at least 1 qt");
  assert.strictEqual(__S({ family: "count", base: 0 }), null);
});
check("pepper alone is black pepper; bell pepper stays bell pepper", () => {
  assert.strictEqual(rows("1 tsp pepper")[0].key, "black pepper");
  assert.strictEqual(rows("1 red bell pepper")[0].key, "bell pepper");
});
check("canned goods keep 'canned'", () => {
  assert.strictEqual(__K(rows("2 cans diced tomatoes")[0].key), "Pantry & spices");
});
console.log("\n" + passed + " page tests passed");

// Labelled accuracy: each line has the answer we expect (item key and kind of amount).
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "accuracy_cases.json"), "utf8"));
let right = 0;
const wrong = [];
for (const c of cases) {
  const r = rows(c.line)[0];
  if (r && r.key === c.key && r.family === c.family) right++;
  else wrong.push(c.line + " -> " + (r ? r.key + " / " + r.family : "nothing"));
}
console.log("\naccuracy: " + right + " of " + cases.length + " labelled lines correct (" + Math.round(100 * right / cases.length) + "%)");
wrong.forEach(w => console.log("  miss: " + w));
// A wrong labelled line fails the run, so the score cannot quietly drop.
if (right < cases.length) { console.log("FAIL: accuracy below 100%"); process.exitCode = 1; }
