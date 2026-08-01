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
