from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROFILE_RE = re.compile(r"^profile_.*\.csv$", re.IGNORECASE)


@dataclass(frozen=True)
class CsvGroupKey:
    csv_type: str
    schema_hash: str


@dataclass
class CsvFileInfo:
    path: Path
    root: Path
    rel_path: Path
    csv_type: str
    headers: list[str]
    schema_hash: str
    row_count: int


def detect_csv_type(path: Path) -> str:
    if PROFILE_RE.match(path.name):
        return "profiles"
    return path.name.removesuffix(".csv")


def schema_hash(headers: Iterable[str]) -> str:
    digest = hashlib.sha1("\x1f".join(headers).encode("utf-8")).hexdigest()
    return digest[:10]


def count_data_rows(path: Path) -> int:
    newline_count = 0
    file_size = path.stat().st_size
    if file_size == 0:
        return 0

    last_byte = b""
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            newline_count += chunk.count(b"\n")
            last_byte = chunk[-1:]

    with path.open("rb") as handle:
        header_line = handle.readline()
        if not header_line:
            return 0
        has_data_without_trailing_newline = last_byte not in {b"\n", b"\r"}
        total_lines = newline_count + (1 if has_data_without_trailing_newline else 0)
        return max(total_lines - 1, 0)


def inspect_csv(path: Path, root: Path) -> CsvFileInfo:
    rel_path = path.relative_to(root)
    csv_type = detect_csv_type(path)
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        headers = next(reader, [])
    return CsvFileInfo(
        path=path,
        root=root,
        rel_path=rel_path,
        csv_type=csv_type,
        headers=headers,
        schema_hash=schema_hash(headers),
        row_count=count_data_rows(path),
    )


def collect_csv_files(roots: list[Path], exclude_types: set[str] | None = None) -> list[CsvFileInfo]:
    files: list[CsvFileInfo] = []
    exclude_types = exclude_types or set()
    for root in roots:
        for path in sorted(root.rglob("*.csv")):
            info = inspect_csv(path, root)
            if info.csv_type in exclude_types:
                continue
            files.append(info)
    return files


def build_master_name(group_key: CsvGroupKey, multiple_schemas: bool) -> str:
    suffix = f"__{group_key.schema_hash}" if multiple_schemas else ""
    return f"master_{group_key.csv_type}{suffix}.csv"


def write_master_csv(
    output_path: Path,
    members: list[CsvFileInfo],
) -> None:
    with output_path.open("wb") as out_handle:
        first = True
        for info in members:
            with info.path.open("rb") as in_handle:
                header = in_handle.readline()
                if first:
                    out_handle.write(header)
                    first = False
                while True:
                    chunk = in_handle.read(1024 * 1024)
                    if not chunk:
                        break
                    out_handle.write(chunk)


def write_summary_csv(output_dir: Path, files: list[CsvFileInfo], groups: dict[CsvGroupKey, list[CsvFileInfo]]) -> None:
    file_summary = output_dir / "master_file_inventory.csv"
    with file_summary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "csv_type",
                "schema_hash",
                "source_root",
                "source_relpath",
                "source_filename",
                "row_count",
                "column_count",
                "columns",
            ],
        )
        writer.writeheader()
        for info in sorted(files, key=lambda item: (item.csv_type, str(item.rel_path))):
            writer.writerow(
                {
                    "csv_type": info.csv_type,
                    "schema_hash": info.schema_hash,
                    "source_root": str(info.root),
                    "source_relpath": str(info.rel_path),
                    "source_filename": info.path.name,
                    "row_count": info.row_count,
                    "column_count": len(info.headers),
                    "columns": "|".join(info.headers),
                }
            )

    type_summary = output_dir / "master_type_summary.csv"
    schema_counts = defaultdict(int)
    for group_key in groups:
        schema_counts[group_key.csv_type] += 1

    with type_summary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "csv_type",
                "schema_hash",
                "source_file_count",
                "total_row_count",
                "column_count",
                "columns",
                "master_csv",
            ],
        )
        writer.writeheader()
        for group_key, members in sorted(groups.items(), key=lambda item: (item[0].csv_type, item[0].schema_hash)):
            writer.writerow(
                {
                    "csv_type": group_key.csv_type,
                    "schema_hash": group_key.schema_hash,
                    "source_file_count": len(members),
                    "total_row_count": sum(item.row_count for item in members),
                    "column_count": len(members[0].headers),
                    "columns": "|".join(members[0].headers),
                    "master_csv": build_master_name(group_key, schema_counts[group_key.csv_type] > 1),
                }
            )


def consolidate(roots: list[Path], output_dir: Path, exclude_types: set[str] | None = None) -> None:
    files = collect_csv_files(roots, exclude_types=exclude_types)
    groups: dict[CsvGroupKey, list[CsvFileInfo]] = defaultdict(list)
    for info in files:
        groups[CsvGroupKey(info.csv_type, info.schema_hash)].append(info)

    output_dir.mkdir(parents=True, exist_ok=True)
    schema_counts = defaultdict(int)
    for group_key in groups:
        schema_counts[group_key.csv_type] += 1

    for group_key, members in sorted(groups.items(), key=lambda item: (item[0].csv_type, item[0].schema_hash)):
        master_name = build_master_name(group_key, schema_counts[group_key.csv_type] > 1)
        write_master_csv(output_dir / master_name, sorted(members, key=lambda item: str(item.rel_path)))

    write_summary_csv(output_dir, files, groups)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consolidate CSV outputs into master CSVs by type.")
    parser.add_argument(
        "--roots",
        nargs="+",
        default=["outputs", "outputs_batches"],
        help="Root directories to scan recursively for CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs_consolidated",
        help="Directory where master CSVs and summary manifests will be written.",
    )
    parser.add_argument(
        "--exclude-type",
        action="append",
        default=[],
        help="CSV type to exclude from consolidation. Can be provided multiple times.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    roots = [Path(root).resolve() for root in args.roots]
    output_dir = Path(args.output_dir).resolve()
    consolidate(roots, output_dir, exclude_types=set(args.exclude_type))


if __name__ == "__main__":
    main()
