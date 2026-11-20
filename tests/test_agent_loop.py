"""Tests for the agent loop in agent.py, using a fake model (no Ollama needed).

Run from the repo folder:  python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import agent  # noqa: E402


class FakeModel:
    """Returns a scripted list of replies, one per call."""
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def __call__(self, messages):
        self.calls += 1
        return self.replies.pop(0)


class AgentLoopTests(unittest.TestCase):
    def setUp(self):
        self._real = agent.ask_model

    def tearDown(self):
        agent.ask_model = self._real

    def test_uses_a_known_tool_then_answers(self):
        agent.ask_model = FakeModel([{"tool": "read_recipe", "args": {"name": "Sample Pancakes.md"}},
                                     {"final": "Milk, eggs and butter."}])
        self.assertEqual(agent.run("what is in the pancakes?"), "Milk, eggs and butter.")

    def test_unknown_tool_is_refused(self):
        agent.ask_model = FakeModel([{"tool": "delete_everything", "args": {}}])
        self.assertIn("unknown tool", agent.run("do it"))

    def test_reply_that_is_not_an_object_stops_the_run(self):
        agent.ask_model = FakeModel([["not", "an", "object"]])
        self.assertIn("not a JSON object", agent.run("hi"))

    def test_bad_arguments_are_reported_back_not_crashed(self):
        agent.ask_model = FakeModel([{"tool": "pick_pack", "args": {"wrong": 1}}, {"final": "ok"}])
        self.assertEqual(agent.run("price?"), "ok")

    def test_step_limit_stops_a_runaway_loop(self):
        fake = FakeModel([{"tool": "read_recipe", "args": {"name": "Sample Pancakes.md"}}] * (agent.MAX_STEPS + 2))
        agent.ask_model = fake
        self.assertIn("Stopped after", agent.run("loop forever"))
        self.assertEqual(fake.calls, agent.MAX_STEPS)

    def test_paths_outside_the_recipe_folder_are_refused(self):
        self.assertIsNone(agent.safe_recipe_path("../README.md"))


if __name__ == "__main__":
    unittest.main()
