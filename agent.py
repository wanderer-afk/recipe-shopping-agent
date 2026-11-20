"""The AI step: a small agent that calls the three tools to answer a grocery question.

How it works (the "agent loop"):
  1. You ask a question in plain words.
  2. The model (running on your own computer through Ollama) picks ONE tool and its inputs,
     as JSON, or says it is finished.
  3. This program runs that tool and sends the result back to the model.
  4. Repeat, but never more than MAX_STEPS times (a safety stop).

Guardrails:
  - The tools only READ recipes and prices. Nothing changes your lists or accounts.
  - Unknown tool names are refused. Bad JSON is reported, not run.
  - No API key is needed. The model runs locally through Ollama (free).

Setup: install Ollama (https://ollama.com), then run `ollama pull gemma3:12b`.
Run:   python agent.py "What do I need to buy for the sample pancakes?"
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

from pack_picker import load_prices, pick_packs
from recipe_reader import RECIPE_FOLDER, read_grocery_lines
from shopping_list import build_shopping_list, load_pantry

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:12b")
MAX_STEPS = 6


def safe_recipe_path(name: str) -> Path | None:
    """Return the path only if it is a .md file directly inside the recipe folder. Otherwise None."""
    if not name or "/" in name or "\\" in name or ".." in name or not name.lower().endswith(".md"):
        return None
    folder = RECIPE_FOLDER.resolve()
    path = (folder / name).resolve()
    if path.parent != folder or not path.is_file():
        return None
    return path


def tool_read_recipe(name: str) -> str:
    """Return the grocery lines of one recipe file in the recipe folder."""
    path = safe_recipe_path(name)
    if path is None:
        return f"No recipe named {name!r} in the recipe folder."
    return json.dumps(read_grocery_lines(path))


def tool_shopping_split(name: str) -> str:
    """Split one recipe into 'buy' and 'check at home' using the pantry list."""
    path = safe_recipe_path(name)
    if path is None:
        return f"No recipe named {name!r} in the recipe folder."
    return json.dumps(build_shopping_list(path, load_pantry()), default=str)


def tool_pick_pack(item: str, amount: str) -> str:
    """Pick the cheapest pack for an item and amount, using store_prices.csv."""
    result = pick_packs(item, amount, load_prices())
    return json.dumps(result, default=str)


TOOLS = {
    "read_recipe": (tool_read_recipe, "name: recipe file name, e.g. 'Sample Pancakes.md'"),
    "shopping_split": (tool_shopping_split, "name: recipe file name, e.g. 'Sample Pancakes.md'"),
    "pick_pack": (tool_pick_pack, "item: ingredient name; amount: e.g. '1 cup' or '18 oz'"),
}

SYSTEM = (
    "You help with a grocery list. You can use these tools, one at a time:\n"
    + "\n".join(f"- {name}({desc})" for name, (_, desc) in TOOLS.items())
    + "\nReply with JSON only. To use a tool: {\"tool\": \"<name>\", \"args\": {...}}. "
    "When you can answer: {\"final\": \"<answer in plain words>\"}. "
    "You only read data. You never change lists. Answer every part of the question; if a tool says NO PRICE, say so."
)


def ask_model(messages: list[dict]) -> dict:
    body = json.dumps({"model": MODEL, "messages": messages, "stream": False,
                       "format": "json", "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        text = json.loads(resp.read())["message"]["content"]
    return json.loads(text)


def run(question: str) -> str:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for step in range(1, MAX_STEPS + 1):
        try:
            choice = ask_model(messages)
        except (OSError, ValueError, KeyError) as err:
            return f"The model did not answer ({err}). Is Ollama running and is {MODEL} pulled?"
        if not isinstance(choice, dict):
            return "Stopped: the model's reply was not a JSON object. Nothing was changed."
        if "final" in choice:
            return str(choice["final"])
        name = choice.get("tool")
        if name not in TOOLS:
            return f"Stopped: the model asked for an unknown tool ({name!r}). Nothing was changed."
        args = choice.get("args") or {}
        if not isinstance(args, dict):
            args = {}
        print(f"  step {step}: {name} {args}")
        try:
            result = TOOLS[name][0](**args)
        except Exception as err:  # a bad tool call is reported to the model, never crashes the agent
            result = f"Tool {name} could not run: {type(err).__name__}: {err}"
        messages.append({"role": "assistant", "content": json.dumps(choice)})
        messages.append({"role": "user", "content": f"Tool result: {result}"})
    return f"Stopped after {MAX_STEPS} steps to stay safe. Ask a smaller question."


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What do I need to buy for Sample Pancakes.md? Use the pantry list."
    print(run(q))
