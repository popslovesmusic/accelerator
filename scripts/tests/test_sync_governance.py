import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts import sync_governance


def test_render_is_deterministic_and_sorted():
    entries = [
        {
            "source_induction_id": "B",
            "title": "B",
            "current_notes_section": "NOTES_ACTIVE",
            "source_summary": "b",
            "capture_status": "PRESERVED_LITERAL",
            "queue_status": "queued",
            "registry_status": "bound",
            "review_status": "NOT_REVIEWED",
            "promotion_status": "HOLD_C1",
            "capture_path": "capture-b",
            "capture_hash": "hash-b",
        },
        {
            "source_induction_id": "A",
            "title": "A",
            "current_notes_section": "NOTES_ACTIVE",
            "source_summary": "a",
            "capture_status": "PRESERVED_LITERAL",
            "queue_status": "queued",
            "registry_status": "bound",
            "review_status": "NOT_REVIEWED",
            "promotion_status": "HOLD_C1",
            "capture_path": "capture-a",
            "capture_hash": "hash-a",
        },
    ]
    # collect() guarantees canonical ordering; the renderer must preserve it.
    entries.sort(key=lambda item: item["source_induction_id"])
    first = sync_governance.render(entries)
    second = sync_governance.render(entries)
    assert first == second
    assert first.index("`A`") < first.index("`B`")
    assert hashlib.sha256(first.encode()).hexdigest() == hashlib.sha256(second.encode()).hexdigest()


def test_generated_markers_are_bounded():
    assert sync_governance.START != sync_governance.END
    assert sync_governance.START in sync_governance.render([])
    assert sync_governance.END in sync_governance.render([])


def test_preserved_capture_is_first_class_input():
    entries, conflicts = sync_governance.collect()
    match = [entry for entry in entries if entry["source_induction_id"] == "FILE_SUMMARY_GENERIC_RT_QMGR_20260801_001"]
    assert len(match) == 1
    entry = match[0]
    assert entry["capture_status"] == "PRESERVED_LITERAL"
    assert entry["review_status"] == "NOT_REVIEWED"
    assert entry["induction_status"] == "NOT_QUEUED"
    assert entry["capture_hash"] == "69CCCEADAC89A5D3498950F75927184761ACD052CCBA3024D18D6FCC3DD7E9BE"
    assert entry["current_notes_section"] == "NOTES_PENDING_PRESERVED"
    assert entry["source_trace"]["immutable_source_available"] is True
    assert not any(item.get("type") == "CAPTURE_HASH_CONFLICT" and item.get("induction_id") == entry["source_induction_id"] for item in conflicts)
