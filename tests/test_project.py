from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectContractTests(unittest.TestCase):
    def test_agent_source_is_valid_python(self) -> None:
        source = (ROOT / "agent" / "my_agent.py").read_text()
        tree = ast.parse(source)
        names = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
        self.assertIn("MyAgent", names)

    def test_notebook_builder_is_valid_python(self) -> None:
        ast.parse((ROOT / "scripts" / "build_notebook.py").read_text())

    def test_metadata_respects_competition_constraints(self) -> None:
        meta = json.loads((ROOT / "notebooks" / "kernel-metadata.json").read_text())
        self.assertFalse(meta["enable_internet"])
        self.assertFalse(meta["enable_tpu"])
        self.assertEqual(meta["competition_sources"], ["arc-prize-2026-arc-agi-3"])


if __name__ == "__main__":
    unittest.main()
