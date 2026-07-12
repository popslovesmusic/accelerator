import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import query_governance as qg


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "registry" / "db" / "acellorator_index.sqlite"
SCHEMA_PATH = ROOT / "schemas" / "governed_context_capsule_v1.schema.json"
TASK_NAME = "PATCH_ACCELERATOR_CANONICAL_CONTEXT_CAPSULE_050"


class GovernedContextCapsuleV1Tests(unittest.TestCase):
    def test_governed_context_capsule_schema_artifact(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        required_fields = {
            "schema_id",
            "schema_version",
            "capsule_id",
            "capsule_hash",
            "request_identity",
            "current_state",
            "freshness",
            "authority",
            "patch_chain",
            "open_debt",
            "relevant_artifacts",
            "runtime_trace",
            "candidate_actions",
            "exclusions",
            "provenance",
            "metrics",
        }

        self.assertEqual(schema["title"], "Governed Context Capsule Schema")
        self.assertTrue(required_fields.issubset(set(schema["required"])))
        self.assertEqual(schema["properties"]["schema_id"]["const"], qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION)
        self.assertEqual(schema["properties"]["schema_version"]["const"], qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE)

    def test_governed_context_capsule_contract_and_alias(self):
        capsule = qg.build_governed_context_capsule(
            str(DB_PATH),
            task=TASK_NAME,
            use_cache=False,
        )

        self.assertEqual(capsule["schema_id"], qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION)
        self.assertEqual(capsule["schema_version"], qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE)
        self.assertEqual(capsule["capsule_schema_version"], qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION)
        self.assertTrue(capsule["request_identity"]["request_id"])
        self.assertEqual(capsule["request_identity"]["request_scope"]["limit"], 20)
        self.assertEqual(capsule["freshness"]["status"], capsule["freshness"]["db_snapshot_status"])
        self.assertIsInstance(capsule["freshness"]["checked_sources"], list)
        self.assertIsInstance(capsule["freshness"]["stale_sources"], list)
        self.assertIn("authority_status", capsule["authority"])
        self.assertIn("allowed_actions", capsule["authority"])
        self.assertIn("forbidden_actions", capsule["authority"])
        self.assertIn("active_patch", capsule["patch_chain"])
        self.assertIn("predecessors", capsule["patch_chain"])
        self.assertIn("successors", capsule["patch_chain"])
        self.assertIn("chain_status", capsule["patch_chain"])
        self.assertIsInstance(capsule["open_debt"], list)
        self.assertEqual(capsule["provenance"]["producer"], "scripts.query_governance.build_governed_context_capsule_v1")
        self.assertEqual(capsule["provenance"]["producer_version"], qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE)
        self.assertTrue(capsule["provenance"]["source_records"])
        self.assertEqual(capsule["metrics"]["cache_status"], "MISS")
        self.assertEqual(capsule["metrics"]["estimated_tokens"], capsule["estimated_token_count"])
        self.assertEqual(qg.validate_governed_context_capsule_payload(capsule), [])

    def test_governed_context_capsule_cache_validation_rebuilds_invalid_payload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "capsules" / qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION
            with mock.patch.object(qg, "GOVERNED_CONTEXT_CAPSULE_CACHE_DIR", cache_dir):
                first = qg.build_governed_context_capsule_v1(
                    str(DB_PATH),
                    task=TASK_NAME,
                    use_cache=True,
                )
                self.assertEqual(first["cache_status"], "MISS")

                cache_path = cache_dir / f"{first['capsule_hash']}.json"
                self.assertTrue(cache_path.exists())
                cache_path.write_text(
                    json.dumps(
                        {
                            "capsule_id": first["capsule_id"],
                            "capsule_hash": first["capsule_hash"],
                        }
                    ),
                    encoding="utf-8",
                )

                second = qg.build_governed_context_capsule_v1(
                    str(DB_PATH),
                    task=TASK_NAME,
                    use_cache=True,
                )

                self.assertEqual(second["cache_status"], "MISS")
                self.assertEqual(second["metrics"]["cache_status"], "MISS")
                self.assertEqual(qg.validate_governed_context_capsule_payload(second), [])

    def test_governed_context_capsule_cache_hits_on_repeated_identical_inputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "capsules" / qg.GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION
            with mock.patch.object(qg, "GOVERNED_CONTEXT_CAPSULE_CACHE_DIR", cache_dir):
                first = qg.build_governed_context_capsule_v1(
                    str(DB_PATH),
                    task=TASK_NAME,
                    use_cache=True,
                )
                second = qg.build_governed_context_capsule_v1(
                    str(DB_PATH),
                    task=TASK_NAME,
                    use_cache=True,
                )

                self.assertEqual(first["capsule_hash"], second["capsule_hash"])
                self.assertEqual(first["cache_status"], "MISS")
                self.assertEqual(second["cache_status"], "HIT")
                self.assertEqual(second["metrics"]["cache_status"], "HIT")
                self.assertEqual(qg.validate_governed_context_capsule_payload(second), [])


if __name__ == "__main__":
    unittest.main()
