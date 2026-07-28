import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def run_text(command, cwd):
    try:
        p = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, timeout=20)
        return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"returncode": None, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}


def checksum_exact(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(4096), b""):
            digest.update(block)
    return digest.hexdigest()


def access_test(path):
    try:
        with open(path, "rb") as handle:
            handle.read(1)
        return {"result": "PASS", "exception": None}
    except Exception as exc:
        return {"result": "FAIL", "exception": {"class": type(exc).__name__, "errno": getattr(exc, "errno", None), "text": str(exc)}}


def metadata(path, repo, relative, classification):
    item = {"absolute_path": str(path), "repository_relative_path": relative}
    item["exists"] = path.exists()
    item["lexists"] = os.path.lexists(path)
    item["is_file"] = path.is_file()
    item["is_directory"] = path.is_dir()
    item["is_symlink"] = path.is_symlink()
    item["symlink_target"] = os.readlink(path) if path.is_symlink() else None
    item["is_mount_point"] = path.is_mount()
    item["is_special_file"] = path.exists() and not (path.is_file() or path.is_dir())
    item["size_bytes"] = None
    item["stat_mode"] = None
    item["lstat_mode"] = None
    try:
        item["size_bytes"] = path.stat().st_size
        item["stat_mode"] = stat.filemode(path.stat().st_mode)
    except OSError as exc:
        item["stat_error"] = {"class": type(exc).__name__, "errno": getattr(exc, "errno", None), "text": str(exc)}
    try:
        item["lstat_mode"] = stat.filemode(path.lstat().st_mode)
    except OSError as exc:
        item["lstat_error"] = {"class": type(exc).__name__, "errno": getattr(exc, "errno", None), "text": str(exc)}
    item["owner_uid_or_platform_equivalent"] = None
    item["group_gid_or_platform_equivalent"] = None
    try:
        st = path.stat()
        item["owner_uid_or_platform_equivalent"] = getattr(st, "st_uid", None)
        item["group_gid_or_platform_equivalent"] = getattr(st, "st_gid", None)
    except OSError:
        pass
    item["read_access_test"] = access_test(path)
    parent = path.parent
    item["parent_directory_read_access"] = os.access(parent, os.R_OK)
    item["parent_directory_execute_or_traverse_access"] = os.access(parent, os.X_OK)
    item["git_status_entry"] = run_text(["git", "status", "--short", "--", relative], repo)
    ignored = run_text(["git", "check-ignore", "--no-index", "--", relative], repo)
    item["git_ignored_status"] = {"ignored": ignored["returncode"] == 0, "result": ignored}
    tracked = run_text(["git", "ls-files", "--error-unmatch", "--", relative], repo)
    item["git_tracked_status"] = {"tracked": tracked["returncode"] == 0, "result": tracked}
    item["file_extension"] = path.suffix.lower()
    item["candidate_indexer_classification"] = classification
    if os.name == "nt":
        item["windows_attributes"] = run_text(["attrib", str(path)], repo)
        item["windows_acl_read_only"] = run_text(["icacls", str(path)], repo)
    else:
        item["posix_ls_ld"] = run_text(["ls", "-ld", str(path)], repo)
        item["posix_namei"] = run_text(["namei", "-l", str(path)], repo)
        item["posix_getfacl"] = run_text(["getfacl", "-p", str(path)], repo)
    return item


def classify_failure(exc):
    if isinstance(exc, PermissionError): return "PermissionError"
    if isinstance(exc, IsADirectoryError): return "IsADirectoryError"
    if isinstance(exc, FileNotFoundError): return "FileNotFoundError"
    if isinstance(exc, UnicodeError): return "UnicodeError"
    if isinstance(exc, OSError): return "OSError"
    return type(exc).__name__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument("--log", required=True)
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()
    script_path = Path(__file__).resolve()
    repo = Path(args.root).resolve() if args.root else script_path.parents[3]
    log_path = Path(args.log).resolve()
    evidence_path = Path(args.evidence).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    candidates = 0
    hashed = 0
    failures = []
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        for root, dirs, files in os.walk(repo):
            if ".git" in dirs: dirs.remove(".git")
            if ".venv" in dirs: dirs.remove(".venv")
            if "__pycache__" in dirs: dirs.remove("__pycache__")
            for name in files + dirs:
                candidates += 1
                absolute = Path(root) / name
                relative = os.path.relpath(absolute, repo).replace("\\", "/")
                event = {"timestamp": utc_now(), "sequence": candidates, "repository_relative_path": relative, "absolute_path": str(absolute), "event": "CANDIDATE_BEFORE_CHECKSUM"}
                log.write(json.dumps(event, ensure_ascii=False) + "\n")
                log.flush()
                try:
                    if absolute.is_dir():
                        digest = None
                    else:
                        digest = checksum_exact(absolute)
                    hashed += 1
                    log.write(json.dumps({"timestamp": utc_now(), "sequence": candidates, "repository_relative_path": relative, "event": "CHECKSUM_SUCCESS", "sha256": digest}, ensure_ascii=False) + "\n")
                except Exception as exc:
                    failure_class = classify_failure(exc)
                    record = {"timestamp": utc_now(), "sequence": candidates, "repository_relative_path": relative, "absolute_path": str(absolute), "failure_class": failure_class, "exception": {"class": type(exc).__name__, "errno": getattr(exc, "errno", None), "text": str(exc)}, "traceback": traceback.format_exc(), "metadata": metadata(absolute, repo, relative, "INDEXER_SCOPE_SELECTED")}
                    failures.append(record)
                    log.write(json.dumps({"timestamp": utc_now(), "sequence": candidates, "repository_relative_path": relative, "event": "CHECKSUM_FAILURE", "failure": record}, ensure_ascii=False) + "\n")
                    log.flush()
    inaccessible = [x for x in failures if x["failure_class"] == "PermissionError"]
    evidence = {
        "packet_id": "D_VALID_REL_TOKEN_C_INDEXER_PERMISSION_DIAGNOSIS_20260727_001",
        "diagnostic_id": "DIAG_D_VALID_REL_TOKEN_C_INDEXER_PERMISSION_20260727_001",
        "execution_timestamp": utc_now(),
        "repository_head": run_text(["git", "rev-parse", "HEAD"], repo)["stdout"].strip(),
        "repository_status_before": "Recorded in diagnostic execution transcript; diagnostic writes only campaign evidence.",
        "canonical_indexer_path": "scripts/db/index_artifacts.py",
        "canonical_indexer_sha256": "35A7D6BA78F065DAC389E01B3AAE529105AA8AABBD4F4B7641CDB246705C3D74",
        "canonical_indexer_discovery_summary": {"root": str(repo), "method": "os.walk(root_dir)", "candidate_order": "files + dirs", "excluded_directories": [".git", ".venv", "__pycache__"], "followlinks": False},
        "canonical_indexer_checksum_summary": {"function": "get_checksum", "block_size": 4096, "directories_return_none": True, "hashing_before_database_mutation": True},
        "diagnostic_script_path": str(script_path.relative_to(repo)).replace("\\", "/"),
        "diagnostic_log_path": str(log_path.relative_to(repo)).replace("\\", "/"),
        "candidate_path_count": candidates,
        "successfully_hashed_path_count": hashed,
        "inaccessible_path_count": len(inaccessible),
        "inaccessible_paths": inaccessible,
        "first_permission_error_path": inaccessible[0]["absolute_path"] if inaccessible else None,
        "first_permission_error_exception": inaccessible[0]["exception"] if inaccessible else None,
        "all_failure_classes_observed": sorted(set(x["failure_class"] for x in failures)),
        "direct_read_test_results": [{"path": x["absolute_path"], "read_access_test": x["metadata"]["read_access_test"]} for x in inaccessible],
        "recommended_next_repair_class": "UNRESOLVED_REQUIRES_HUMAN_INSPECTION" if not inaccessible else "RESTORE_READ_PERMISSION_ON_TRACKED_REQUIRED_FILE",
        "recommended_next_repair_reason": "No inaccessible path was reproduced; human inspection is required." if not inaccessible else "The exact path is selected by the canonical indexer and fails only at read/checksum. Restore read access only after human review confirms it is a required tracked repository file; do not alter semantic artifacts or SQLite rows.",
        "protected_surface_diff_summary": "Diagnostic performs no writes to protected surfaces or SQLite.",
        "unexpected_mutations": [],
        "repository_status_after": "Diagnostic campaign artifacts only; no staging, commit, permission, file, registry, indexer, or database mutation.",
        "final_result": "PASS_MULTIPLE_DENIED_PATHS_IDENTIFIED" if len(inaccessible) > 1 else "PASS_DENIED_PATH_IDENTIFIED" if inaccessible else "FAIL_DENIED_PATH_NOT_REPRODUCED"
    }
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"candidate_path_count": candidates, "successfully_hashed_path_count": hashed, "inaccessible_path_count": len(inaccessible), "failure_classes": evidence["all_failure_classes_observed"], "final_result": evidence["final_result"], "elapsed_note": {"started": started, "ended": evidence["execution_timestamp"]}}, indent=2))


if __name__ == "__main__":
    main()
