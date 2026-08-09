import json
import tempfile
import unittest
from pathlib import Path

from crawl_engine.analyzers.core import cycles
from crawl_engine.engine import run

class RefinementTest(unittest.TestCase):
    def test_known_cycle_and_acyclic_fixture(self):
        cyclic = {"nodes":["a","b"],"edges":[{"from":"a","to":"b"},{"from":"b","to":"a"}]}
        acyclic = {"nodes":["a","b"],"edges":[{"from":"a","to":"b"}]}
        self.assertEqual(cycles(cyclic), [["a", "b", "a"]])
        self.assertEqual(cycles(acyclic), [])

    def test_engine_has_direct_and_propagated_blockers(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temp:
            report = run(root, Path(temp) / "result")
        kinds = {item["direct_or_propagated"] for item in report["blockers"]}
        self.assertEqual(kinds, {"DIRECT", "PROPAGATED"})
        self.assertEqual(len(report["object_inventory"]["analyzed"]), 6)

    def test_source_hashes_and_precedence_are_present(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temp:
            report = run(root, Path(temp) / "result")
        self.assertTrue(all(item["source_hash"] for item in report["object_inventory"]["analyzed"]))
        self.assertTrue(report["source_resolution"]["source_precedence_decisions"])

if __name__ == "__main__":
    unittest.main()
