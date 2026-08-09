from __future__ import annotations

import json
from pathlib import Path

from tools.governance_inventory import write_q0_authority_scope_partition_artifacts
from tools.runtime_authority import build_live_authority_access_inventory


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    bundle = write_q0_authority_scope_partition_artifacts(
        core_rule_path=ROOT / "governance" / "core_rules" / "GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json",
        partition_path=ROOT / "governance" / "authority_partitions" / "Q0_AUTHORITY_SCOPE_PARTITION_001.json",
        before_state_path=ROOT / "outputs" / "governance_inventory" / "q0_scope_partition_before.json",
        after_state_path=ROOT / "outputs" / "governance_inventory" / "q0_scope_partition_after.json",
        diff_path=ROOT / "outputs" / "governance_inventory" / "q0_scope_partition_diff.json",
        write_owners_path=ROOT / "outputs" / "governance_inventory" / "q0_exclusive_write_owners.json",
        validation_path=ROOT / "outputs" / "governance_inventory" / "q0_validator_authority_partition.json",
        instruction_path=ROOT / "outputs" / "governance_inventory" / "q0_instruction_authority_partition.json",
        queue_path=ROOT / "outputs" / "governance_inventory" / "q0_scope_partition_queue.json",
        review_path=ROOT / "docs" / "governance" / "q0_authority_scope_partition.md",
    )
    inventory_path = ROOT / "outputs" / "governance_inventory" / "q0_live_authority_access_inventory.json"
    inventory_path.write_text(
        json.dumps(build_live_authority_access_inventory(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    summary = {
        "patch_id": bundle["partition"]["patch_id"],
        "partition_id": bundle["partition"]["partition_id"],
        "cluster_id": bundle["partition"]["cluster_id"],
        "resolved_record_count": bundle["partition"]["resolved_ambiguity_count"],
        "resolved_question_count": bundle["partition"]["resolved_question_count"],
        "remaining_blocking_ambiguities": bundle["partition"]["remaining_blocking_ambiguities"],
        "artifacts": bundle["artifacts"],
        "live_authority_access_inventory": str(inventory_path.relative_to(ROOT)).replace("\\", "/"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
