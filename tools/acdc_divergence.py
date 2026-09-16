#!/usr/bin/env python3
"""
acdc_divergence.py — signature computation and divergence detection for the
CDISC AC/DC framework (cdisc-org/analysis-concepts).

Implements sections 9.1-9.4 of the Concept Spine specification (docs/specification.md).

Reads methods and transformations from a checkout of the upstream repository,
computes signature hashes, and reports clusters of entries that are functionally
identical or near-identical. Read-only: never writes into the upstream tree.

Usage:
    python3 acdc_divergence.py --repo ./analysis-concepts
    python3 acdc_divergence.py --repo ./analysis-concepts --compare-naive
    python3 acdc_divergence.py --repo ./analysis-concepts --json report.json
    python3 acdc_divergence.py --repo ./analysis-concepts --overlay scopes.json

The optional overlay file maps oid to scope, so cross-catalogue clusters can be
distinguished from within-catalogue ones:

    {"M.Mean": {"scope_level": "ta", "scope_ref": "ONC"}, ...}

Entries absent from the overlay default to scope_level "org", which is correct
for anything coming straight from upstream.

Python 3.10+. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_NOTE = "acdc_methods.schema.json v0.8.0 / acdc_transformations.schema.json v0.1.0"


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"  ! skipping {path.name}: invalid JSON ({exc})", file=sys.stderr)
        return None


def load_methods(repo: Path) -> list[dict]:
    root = repo / "lib" / "methods"
    if not root.is_dir():
        sys.exit(f"error: {root} not found. Is --repo pointing at an analysis-concepts checkout?")
    out = []
    for path in sorted(root.rglob("*.json")):
        if path.name.startswith("_"):  # _index.json and friends
            continue
        doc = load_json(path)
        if isinstance(doc, dict) and doc.get("oid"):
            doc["_source"] = str(path.relative_to(repo))
            out.append(doc)
    return out


def load_transformations(repo: Path) -> list[dict]:
    root = repo / "lib" / "transformations"
    if not root.is_dir():
        return []
    out = []
    for path in sorted(root.glob("*.json")):
        doc = load_json(path)
        if not isinstance(doc, dict):
            continue
        for key in ("derivationTransformations", "analysisTransformations"):
            for entry in doc.get(key) or []:
                if entry.get("oid"):
                    entry["_source"] = f"{path.relative_to(repo)}::{key}"
                    out.append(entry)
    return out


# --------------------------------------------------------------------------
# signatures
# --------------------------------------------------------------------------


def _hash(payload: Any) -> str:
    return hashlib.sha1(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:12]


def _sorted(rows):
    """Sort rows that may contain None alongside strings. Optional fields are
    common in both schemas, so a plain sorted() raises on mixed types."""
    return sorted(rows, key=lambda row: [("" if v is None else str(v)) for v in row])


def method_roles(method: dict) -> list:
    return _sorted(
        [
            r.get("name"),
            r.get("statisticalRole"),
            r.get("dataType"),
            r.get("cardinality"),
            bool(r.get("required")),
        ]
        for r in (method.get("input_roles") or [])
    )


def method_outputs(method: dict) -> list:
    spec = method.get("output_specification") or {}
    return _sorted(
        [oc.get("class"), sorted(oc.get("statistics") or [])]
        for oc in (spec.get("output_classes") or [])
    )


def method_codings(method: dict) -> list:
    return sorted(str(c.get("code")) for c in (method.get("codings") or []) if c.get("code"))


def method_signature(method: dict, naive: bool = False) -> str:
    """Full signature per spec 4.1. naive=True reproduces the input-roles-only
    key, which is retained solely to demonstrate why it is insufficient."""
    roles = method_roles(method)
    configs = sorted(str(c.get("name")) for c in (method.get("configurations") or []))
    if naive:
        return _hash([method.get("type"), roles, configs])
    return _hash(
        [
            method.get("type"),
            roles,
            configs,
            method_outputs(method),
            method_codings(method),
        ]
    )


def transformation_bindings(tr: dict) -> list:
    return _sorted(
        [
            b.get("methodRole"),
            b.get("concept") or b.get("conceptCategory"),
            b.get("direction"),
            b.get("dataStructureRole"),
        ]
        for b in (tr.get("bindings") or [])
    )


def transformation_signature(tr: dict, ignore_config_values: bool = False) -> str:
    """Signature per spec 4.3. With ignore_config_values=True this becomes the
    loose key: transformations differing only in configuration values cluster
    together, which is the 'should this be one transformation with an option?'
    signal."""
    configs = tr.get("methodConfigurations") or []
    if ignore_config_values:
        cfg = sorted(str(c.get("configurationName")) for c in configs)
    else:
        cfg = _sorted([c.get("configurationName"), c.get("value")] for c in configs)
    return _hash(
        [
            tr.get("transformationType"),
            tr.get("usesMethod"),
            transformation_bindings(tr),
            cfg,
        ]
    )


# --------------------------------------------------------------------------
# clustering
# --------------------------------------------------------------------------


@dataclass
class Entry:
    oid: str
    name: str
    kind: str
    source: str
    scope_level: str = "org"
    scope_ref: str | None = None
    signatures: dict[str, str] = field(default_factory=dict)

    @property
    def scope(self) -> str:
        return f"{self.scope_level}:{self.scope_ref}" if self.scope_ref else self.scope_level


def build_entries(repo: Path, overlay: dict) -> list[Entry]:
    entries: list[Entry] = []

    for m in load_methods(repo):
        ov = overlay.get(m["oid"], {})
        entries.append(
            Entry(
                oid=m["oid"],
                name=m.get("name", ""),
                kind=f"method/{m.get('type', '?')}",
                source=m["_source"],
                scope_level=ov.get("scope_level", "org"),
                scope_ref=ov.get("scope_ref"),
                signatures={
                    "full": method_signature(m),
                    "naive": method_signature(m, naive=True),
                },
            )
        )

    for t in load_transformations(repo):
        ov = overlay.get(t["oid"], {})
        entries.append(
            Entry(
                oid=t["oid"],
                name=t.get("name", ""),
                kind=f"transformation/{t.get('transformationType', '?')}",
                source=t["_source"],
                scope_level=ov.get("scope_level", "org"),
                scope_ref=ov.get("scope_ref"),
                signatures={
                    "full": transformation_signature(t),
                    "loose": transformation_signature(t, ignore_config_values=True),
                },
            )
        )

    return entries


def cluster(entries: list[Entry], key: str) -> dict[str, list[Entry]]:
    buckets: dict[str, list[Entry]] = defaultdict(list)
    for e in entries:
        sig = e.signatures.get(key)
        if sig:
            buckets[sig].append(e)
    return {k: v for k, v in sorted(buckets.items()) if len(v) > 1}


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def print_clusters(title: str, clusters: dict[str, list[Entry]], total: int, note: str = "") -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if note:
        print(f"{note}\n")
    if not clusters:
        print("No clusters found. Every entry is functionally distinct on this key.")
        return
    flagged = sum(len(v) for v in clusters.values())
    print(f"{len(clusters)} cluster(s) covering {flagged} of {total} entries\n")
    for sig, members in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        scopes = {m.scope for m in members}
        marker = "  [CROSS-SCOPE]" if len(scopes) > 1 else ""
        print(f"  {sig}  ({len(members)} entries){marker}")
        for m in sorted(members, key=lambda e: e.oid):
            scope = f" <{m.scope}>" if m.scope != "org" else ""
            print(f"      {m.oid}{scope}")
        print()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default="./analysis-concepts", help="path to an analysis-concepts checkout")
    ap.add_argument("--overlay", help="optional JSON mapping oid to scope_level/scope_ref")
    ap.add_argument("--json", dest="json_out", help="write the full report as JSON")
    ap.add_argument("--compare-naive", action="store_true",
                    help="also run the input-roles-only key, to show why it is insufficient")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    overlay = {}
    if args.overlay:
        overlay = load_json(Path(args.overlay)) or {}

    entries = build_entries(repo, overlay)
    methods = [e for e in entries if e.kind.startswith("method")]
    transforms = [e for e in entries if e.kind.startswith("transformation")]

    print(f"AC/DC divergence report")
    print(f"repo:    {repo}")
    print(f"schemas: {SCHEMA_NOTE}")
    print(f"loaded:  {len(methods)} methods, {len(transforms)} transformations")
    if overlay:
        scopes = defaultdict(int)
        for e in entries:
            scopes[e.scope] += 1
        print("scopes:  " + ", ".join(f"{k}={v}" for k, v in sorted(scopes.items())))

    no_stato = sum(1 for m in load_methods(repo) if not m.get("codings"))
    if no_stato:
        print(f"note:    {no_stato}/{len(methods)} methods carry no STATO coding; "
              f"codings act as a tiebreaker only")

    method_clusters = cluster(methods, "full")
    print_clusters(
        "METHODS — full signature (roles + configs + outputs + codings)",
        method_clusters, len(methods),
        "Candidates for consolidation: same inputs, same outputs, same statistical meaning.",
    )

    if args.compare_naive:
        naive_clusters = cluster(methods, "naive")
        print_clusters(
            "METHODS — naive signature (input roles + config names only)",
            naive_clusters, len(methods),
            "Retained to demonstrate insufficiency. Univariate statistics are\n"
            "signature-identical on this key and legitimately distinct.",
        )

    tr_exact = cluster(transforms, "full")
    print_clusters(
        "TRANSFORMATIONS — full signature (method + bindings + config values)",
        tr_exact, len(transforms),
        "Functionally identical transformations.",
    )

    tr_loose = cluster(transforms, "loose")
    tr_loose_only = {k: v for k, v in tr_loose.items()
                     if {e.oid for e in v} not in [{e.oid for e in m} for m in tr_exact.values()]}
    print_clusters(
        "TRANSFORMATIONS — loose signature (configuration values ignored)",
        tr_loose_only, len(transforms),
        "Differ only in configuration values. Candidates for a single\n"
        "transformation with a configuration option.",
    )

    if args.json_out:
        report = {
            "repo": str(repo),
            "counts": {"methods": len(methods), "transformations": len(transforms)},
            "entries": [
                {"oid": e.oid, "name": e.name, "kind": e.kind, "source": e.source,
                 "scope_level": e.scope_level, "scope_ref": e.scope_ref,
                 "signatures": e.signatures}
                for e in entries
            ],
            "clusters": {
                "methods_full": {k: [e.oid for e in v] for k, v in method_clusters.items()},
                "transformations_full": {k: [e.oid for e in v] for k, v in tr_exact.items()},
                "transformations_loose": {k: [e.oid for e in v] for k, v in tr_loose_only.items()},
            },
        }
        Path(args.json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nJSON report written to {args.json_out}")

    total_flagged = len(method_clusters) + len(tr_exact) + len(tr_loose_only)
    print(f"\n{total_flagged} cluster(s) for review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
