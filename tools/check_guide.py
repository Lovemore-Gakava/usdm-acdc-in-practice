#!/usr/bin/env python3
"""
check_guide.py — the guide may not state a number it did not get from the repository.

NORTH.md stage G0, and the mechanism the rest of phase 3 rests on. Written before
the prose, deliberately: a guide that says "torivumab - placebo = -1.276" is wrong
the next time TORIVA is re-pinned, and TORIVA was re-pinned twice in one day on
2026-09-20, moving every figure in both endpoints. Retro-fitting a checker to
prose already written is how F02 came to assert a premise that had never been true.

Three checks:

  facts    every {{fact:...}} reference resolves to a value that is actually in
           endpoints/*/results.json right now. The number is never typed, so it
           cannot be stale - it is substituted at build time by --render.

  literals a bare decimal or percentage in prose is a number somebody typed.
           Each must be in docs/guide/literals.yml with a reason, which makes
           "I will just write the figure here" a deliberate, reviewable act.
           Integers are ignored: years, section numbers and counts are not the
           risk, and flagging them would train the reader to ignore this tool.

  terms    the audience is anyone in pharma, with or without CDISC background
           (LG, 2026-09-26), so the vocabulary cannot be assumed. Any high-risk
           term used in the guide must carry a one-line gloss or a link in
           docs/guide/terms.yml. A glossary chapter was considered and rejected
           as too heavy; this is the cheap enforcement of the same intent.

Usage:
    python tools/check_guide.py                # check
    python tools/check_guide.py --render DIR   # write the guide with facts substituted
    python tools/check_guide.py --list-facts   # every addressable fact, for authoring

Exit 0 only when the guide exists and every check passes. A repository with no
guide exits 1, so NORTH's G5 cannot read green on an empty docs/guide/.

Python 3.9+. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Terms a reader without CDISC background cannot be expected to know. Using one in
# the guide without a gloss or a link is the failure this list exists to catch.
HIGH_RISK_TERMS = [
    "USDM", "M11", "eSAP", "ADaM", "SDTM", "BDS", "OCCDS", "WebR", "RECIST",
    "ADLB", "ADVS", "ADSL", "ADRS", "ADTTE", "AVISIT", "ABLFL", "PARAMCD",
    "ANCOVA", "MMRM", "ITT", "CDISC", "estimand", "intercurrent event",
    "biomedical concept", "derivation concept", "analysis concept",
]

FACT_RE = re.compile(r"\{\{fact:([^}]+)\}\}")
# A number somebody typed: a decimal, or a percentage. Integers are not flagged.
LITERAL_RE = re.compile(r"(?<![\w.])[-−+]?\d+\.\d+%?|(?<![\w.])\d+%")
FENCE_RE = re.compile(r"^\s*(```|:::)")


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, status: str, check: str, detail: str) -> None:
        self.rows.append((status, check, detail))

    @property
    def failed(self) -> int:
        return sum(1 for s, _, _ in self.rows if s == "FAIL")

    def print(self) -> None:
        for status, check, detail in self.rows:
            print(f"  {status:<4} {check:<28} {detail}")
        p = sum(1 for s, _, _ in self.rows if s == "PASS")
        print(f"\nguide: {p} pass, {self.failed} fail → {'OK' if not self.failed else 'FAIL'}")


# ---------------------------------------------------------------- minimal parsers

def read_simple_yaml(path: Path) -> dict[str, str]:
    """`key: value` per line, plus `#` comments. A dependency-free subset, which is
    all these two files need; adding PyYAML to install a glossary would be absurd."""
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        # Only a whitespace-preceded '#' starts a comment. A bare split on '#' would
        # truncate every fact address, which are of the form file.json#dotted.path —
        # and it did, silently, until the first alias failed to resolve.
        if line.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", line).rstrip()
        if not line.strip() or ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip().strip('"\'')] = v.strip().strip('"\'')
    return out


def load_facts(root: Path) -> dict[str, object]:
    """Every value in every results.json, addressed as file#dotted.path."""
    facts: dict[str, object] = {}
    for f in sorted((root / "endpoints").glob("*/results.json")):
        rel = f.relative_to(root).as_posix()
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        def walk(node: object, path: str) -> None:
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, f"{path}.{k}" if path else str(k))
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{path}[{i}]")
            else:
                facts[f"{rel}#{path}"] = node

        walk(data, "")
    return facts


def resolve(ref: str, facts: dict[str, object], aliases: dict[str, str]) -> object | None:
    ref = ref.strip()
    return facts.get(aliases.get(ref, ref), None if aliases.get(ref, ref) not in facts else facts[aliases.get(ref, ref)])


# ---------------------------------------------------------------- the checks

def prose_lines(text: str) -> list[tuple[int, str]]:
    """Lines outside fenced code blocks. Code is quoted from the repository and is
    not the guide asserting a figure."""
    out, fenced = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            fenced = not fenced if line.strip().startswith("```") else fenced
            continue
        if not fenced:
            out.append((i, line))
    return out


def check_facts(chapters: list[Path], facts: dict[str, object], aliases: dict[str, str], R: Report, root: Path) -> None:
    refs = 0
    bad: list[str] = []
    for ch in chapters:
        text = ch.read_text(encoding="utf-8")
        for m in FACT_RE.finditer(text):
            refs += 1
            key = aliases.get(m.group(1).strip(), m.group(1).strip())
            if key not in facts:
                bad.append(f"{ch.relative_to(root).as_posix()}: {m.group(1).strip()}")
    for b in bad:
        R.add("FAIL", "facts", f"unresolved reference — {b}")
    if not bad:
        R.add("PASS", "facts", f"{refs} fact reference(s), all resolve to a value in endpoints/*/results.json")


def check_literals(chapters: list[Path], allowed: dict[str, str], R: Report, root: Path) -> None:
    offenders: list[str] = []
    for ch in chapters:
        text = FACT_RE.sub("", ch.read_text(encoding="utf-8"))  # substituted values are not typed
        for lineno, line in prose_lines(text):
            for m in LITERAL_RE.finditer(line):
                lit = m.group(0)
                if lit in allowed or lit.lstrip("+-−") in allowed:
                    continue
                # A section reference is not a figure. "M11 §3.1.1" and "v0.3" are
                # structure, not results, and flagging them would teach the reader to
                # ignore this check — which is the only way a check like this fails.
                before, after = line[:m.start()], line[m.end():]
                if before.rstrip().endswith(("§", "section", "Section")) or before.endswith(("v", "V")):
                    continue
                if re.match(r"\.\d", after) or re.search(r"\d\.$", before):
                    continue
                offenders.append(f"{ch.relative_to(root).as_posix()}:{lineno}: {lit}")
    for o in offenders[:20]:
        R.add("FAIL", "literals", f"figure typed in prose — {o}")
    if len(offenders) > 20:
        R.add("FAIL", "literals", f"... and {len(offenders) - 20} more")
    if not offenders:
        R.add("PASS", "literals", "no decimal or percentage typed in prose that is not allow-listed with a reason")


def check_terms(chapters: list[Path], terms: dict[str, str], R: Report) -> None:
    joined = "\n".join(ch.read_text(encoding="utf-8") for ch in chapters)
    missing = [t for t in HIGH_RISK_TERMS
               if re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", joined) and t not in terms]
    empty = [t for t, v in terms.items() if not v.strip()]
    dead = [t for t in terms if not re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", joined)]
    for t in missing:
        R.add("FAIL", "terms", f"{t!r} is used but has no gloss or link in docs/guide/terms.yml")
    for t in empty:
        R.add("FAIL", "terms", f"{t!r} is in terms.yml with an empty gloss")
    if dead:
        R.add("FAIL", "terms", f"defined but never used, so the definition is untested: {', '.join(sorted(dead)[:8])}")
    if not (missing or empty or dead):
        R.add("PASS", "terms", f"{len(terms)} term(s) glossed or linked; every high-risk term used is covered")


# ---------------------------------------------------------------- render

def render(chapters: list[Path], facts: dict[str, object], aliases: dict[str, str], out_dir: Path) -> int:
    """Write the chapters with every {{fact:}} substituted, plus the support files a
    renderer needs. The build directory, not docs/guide/, is what Quarto is pointed
    at — rendering the source directly would publish the placeholders."""
    out_dir.mkdir(parents=True, exist_ok=True)
    src = chapters[0].parent
    for extra in ("_quarto.yml", "index.qmd", "styles.css", "cover.png"):
        if (src / extra).is_file():
            shutil.copy2(src / extra, out_dir / extra)
    for ch in chapters:
        def sub(m: re.Match) -> str:
            key = aliases.get(m.group(1).strip(), m.group(1).strip())
            return str(facts.get(key, m.group(0)))
        (out_dir / ch.name).write_text(FACT_RE.sub(sub, ch.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"rendered {len(chapters)} chapter(s) into {out_dir}")
    return 0


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Check the guide states no figure it did not get from the repository.")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--render", default=None, metavar="DIR", help="write chapters with facts substituted")
    ap.add_argument("--list-facts", action="store_true", help="print every addressable fact and exit")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    guide = root / "docs" / "guide"
    facts = load_facts(root)

    if args.list_facts:
        for k in sorted(facts):
            print(f"{k} = {facts[k]}")
        print(f"\n{len(facts)} addressable fact(s)")
        return 0

    chapters = sorted(guide.glob("*.qmd")) if guide.is_dir() else []
    if not chapters:
        print(f"no guide yet: {guide.relative_to(root).as_posix()}/*.qmd is empty.")
        print("NORTH.md phase 3 G1-G7 stay red until it exists. This is not an error in the tool.")
        return 1

    aliases = read_simple_yaml(guide / "facts.yml")
    terms = read_simple_yaml(guide / "terms.yml")
    allowed = read_simple_yaml(guide / "literals.yml")

    if args.render:
        return render(chapters, facts, aliases, Path(args.render))

    print(f"guide check — {len(chapters)} chapter(s), {len(facts)} addressable fact(s)\n")
    R = Report()
    check_facts(chapters, facts, aliases, R, root)
    check_literals(chapters, allowed, R, root)
    check_terms(chapters, terms, R)
    R.print()
    return 1 if R.failed else 0


if __name__ == "__main__":
    sys.exit(main())
