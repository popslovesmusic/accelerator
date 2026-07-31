import json
import tempfile
import unittest
from pathlib import Path

from crawl_engine.engine import run

class EngineTest(unittest.TestCase):
    def test_focused_run_is_deterministically_structured(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temp:
            first_path = Path(temp) / "first"
            second_path = Path(temp) / "second"
            first = run(root, first_path)
            second = run(root, second_path)
            self.assertEqual(first_path.with_suffix(".json").read_bytes(), second_path.with_suffix(".json").read_bytes())
        self.assertEqual(first, second)
        self.assertTrue(first["validation"]["schema_validation"]["passed"])
        self.assertTrue(first["validation"]["readonly_validation"]["read_only"])

if __name__ == "__main__":
    unittest.main()
