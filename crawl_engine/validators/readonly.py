from crawl_engine.analyzers.core import snapshot

def check_mathematical_paths(root, relative_paths, before):
    after = snapshot(root, relative_paths)
    changed = [item["path"] for item in after["source_files"] if item not in before["source_files"]]
    return {"read_only": not changed, "changed_paths": changed, "before_hash": before["snapshot_hash"], "after_hash": after["snapshot_hash"], "checked": True}
