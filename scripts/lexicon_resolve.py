from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|ε|ρ|R|CSI", re.UNICODE)


def repo_root_from(start: Path) -> Path:
    p = start.resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "GEMINI.md").exists():
            return candidate
    raise SystemExit(f"Could not locate repo root from {start}")


def load_alias_map(repo_root: Path) -> dict[str, str]:
    alias_path = repo_root / "registry" / "lexicon_alias_map.json"
    payload = json.loads(alias_path.read_text(encoding="utf-8"))
    aliases: dict[str, str] = payload.get("aliases", {})
    # Make lookup case-insensitive by adding lowered keys when absent.
    out: dict[str, str] = {}
    for k, v in aliases.items():
        out[str(k)] = str(v)
        lk = str(k).lower()
        if lk not in out:
            out[lk] = str(v)
    return out


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def normalize_tokens(tokens: Iterable[str], alias_map: dict[str, str]) -> list[str]:
    normalized: list[str] = []
    for t in tokens:
        key = t if t in alias_map else t.lower()
        normalized.append(alias_map.get(key, t))
    return normalized


@dataclass(frozen=True)
class PrimitiveSpec:
    name: str
    keywords: set[str]


def primitive_specs() -> list[PrimitiveSpec]:
    # These keyword sets intentionally mix canonical lexicon entries and frequent surface forms.
    # The alias map normalizes many of them (e.g. "csi" -> "csi").
    return [
        PrimitiveSpec(
            name="epsilon",
            keywords={
                "epsilon",
                "ε",
                "mismatch",
                "deviation",
                "difference",
                "asymmetry",
                "NOT_axiom",
                "signal",
                "pressure",
                "gradient",
            },
        ),
        PrimitiveSpec(
            name="residue",
            keywords={
                "residue",
                "R",
                "memory",
                "constraint",
                "trace",
                "inscription",
                "accumulation",
                "accumulated",
            },
        ),
        PrimitiveSpec(
            name="coupling",
            keywords={
                "coupling",
                "csi",
                "CSI",
                "interaction",
                "reach",
                "relation",
                "connections",
                "adjacency",
                "domain",
                "graph",
                "diffusion",
            },
        ),
    ]


def score_primitives(normalized_tokens: list[str]) -> dict[str, float]:
    counts = Counter(normalized_tokens)
    specs = primitive_specs()
    scores: dict[str, float] = {}
    for spec in specs:
        score = 0.0
        for kw in spec.keywords:
            score += float(counts.get(kw, 0))
        scores[spec.name] = score
    return scores


def mapping_from_scores(scores: dict[str, float], top_terms: list[str]) -> dict[str, str]:
    # Emit a simple stable mapping string; users can edit in paper.
    # When no evidence, default to the repo's canonical primitive descriptions (AGENTS.md).
    def pick(primitive: str, default: str) -> str:
        if scores.get(primitive, 0.0) <= 0.0:
            return default
        # choose a short phrase using top terms
        related = [t for t in top_terms if t]
        snippet = ", ".join(related[:4])
        return f"{default} (evidence: {snippet})" if snippet else default

    return {
        "epsilon": pick("epsilon", "Signal / pressure (mismatch)"),
        "residue": pick("residue", "Memory / constraint (accumulated trace)"),
        "coupling": pick("coupling", "Coupling / reach (interaction domain / CSI)"),
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Resolve free-text excerpts into canonical epsilon/residue/coupling mappings using theory/lexicon."
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Excerpt text to analyze.")
    src.add_argument("--file", help="Path to a text/markdown file to analyze.")
    p.add_argument("--top", type=int, default=25, help="Top normalized terms to report (default: 25).")
    p.add_argument("--out", default=None, help="Optional output JSON path.")
    return p.parse_args(argv)


def main() -> None:
    args = parse_args()
    start = Path.cwd()
    repo_root = repo_root_from(start)
    alias_map = load_alias_map(repo_root)

    if args.text:
        text = args.text
        source = {"kind": "text", "value": "<arg --text>"}
    else:
        path = Path(args.file).resolve()
        text = path.read_text(encoding="utf-8", errors="replace")
        source = {"kind": "file", "value": str(path)}

    raw_tokens = tokenize(text)
    normalized = normalize_tokens(raw_tokens, alias_map)
    counts = Counter(normalized)

    top_terms = [t for t, _c in counts.most_common(args.top)]
    scores = score_primitives(normalized)
    mapping = mapping_from_scores(scores, top_terms=top_terms)

    out: dict[str, Any] = {
        "source": source,
        "lexicon": {
            "alias_map": str(repo_root / "registry" / "lexicon_alias_map.json"),
        },
        "stats": {
            "raw_token_count": len(raw_tokens),
            "unique_normalized_terms": len(counts),
        },
        "top_terms": [{"term": t, "count": int(counts[t])} for t, _ in counts.most_common(args.top)],
        "primitive_scores": scores,
        "mapping": mapping,
        "notes": [
            "This resolver is heuristic: it normalizes tokens via the alias map and scores primitives via keyword matches.",
            "For governed papers, treat the output as a draft mapping to be checked against the excerpt and model observables.",
        ],
    }

    payload = json.dumps(out, indent=2, ensure_ascii=False)
    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()

