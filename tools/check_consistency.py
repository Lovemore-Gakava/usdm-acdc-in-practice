#!/usr/bin/env python3
"""
check_consistency.py — assert the repository's documents agree with the repository.

This repository's method (docs/method.md) requires that a claim about upstream be
backed by a command. The same rule is applied here to claims the repository makes
about *itself*: counts of findings, drafted issues, discrepancies and mapped
endpoints are all derivable from the filesystem, so they are derived and checked
rather than maintained by hand.

Ground truth is the filesystem. Documents are wrong, never the other way round.

It also prints NORTH.md's finish line on every run, so the project's actual
progress is visible at every commit rather than only when someone looks.

Checks:
  1. findings      F01-F0N ranges match the files in docs/findings/
  2. findings-index every finding file appears in docs/findings/README.md, and the
                   top-level README links to that index
  3. issues        stated counts of drafted issues match '## Issue' headings
  4. discrepancies stated counts of D-items match the source-refs table, and the
                   D-ids are contiguous from D1
  5. endpoints     stated counts of mapped endpoints match endpoints/*/mapping.md
  6. coverage      every tracked .md and .py is named somewhere in PROVENANCE.md
  7. links         every relative markdown link resolves to a file that exists
  8. submodule     upstream is checked out, and at the commit the documents pin
  9. north         NORTH.md's nine-stage status table matches the filesystem, so
                   the compass cannot claim a stage that has not happened

Two kinds of line are exempt, because they are correct records of what was once
believed rather than claims about the present:

  - anything under a 'Change log' heading, automatically
  - any line carrying the marker '<!-- consistency:ignore -->'

What this CANNOT check is the harder half: whether a claim is still *true*.
Nothing here would have caught 'ORR will hit F06 less severely' being disproved,
or F02's premise being wrong. Those need the verification pass, not a script.

Usage:
    python tools/check_consistency.py
    python tools/check_consistency.py --verbose     show every matched claim
    python tools/check_consistency.py --root .      run against another checkout

Exit code 0 if consistent, 1 if not. Python 3.10+. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

NUMBER_WORDS = {
    "no": 0, "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
}

# Lines carrying this marker are exempt. Use it for deliberately historical
# statements whose numbers are a record of what was once believed.
IGNORE = "<!-- consistency:ignore -->"


def historical_lines(lines: list[str]) -> set[int]:
    """1-based line numbers under a 'Change log' heading.

    A change log records what was true at each version, so its numbers are
    deliberately stale and must not be checked against the present.
    """
    out: set[int] = set()
    depth = 0
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(#+)\s+(.*)", line)
        if m:
            level = len(m.group(1))
            if re.search(r"change\s*log|revision history", m.group(2), re.I):
                depth = level
                out.add(i)
                continue
            if depth and level <= depth:
                depth = 0
        if depth:
            out.add(i)
    return out


def exempt(path: str, i: int, line: str, hist: dict[str, set[int]]) -> bool:
    return IGNORE in line or i in hist.get(path, set())


def to_int(token: str) -> int | None:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


@dataclass
class Problem:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"  {self.path}:{self.line}\n      {self.message}"


@dataclass
class Claim:
    path: str
    line: int
    text: str
    value: int


# --------------------------------------------------------------------------
# sentinel patterns
# --------------------------------------------------------------------------
# Explicit and tight, by design. A naive scan for number-words near "issues"
# flags historical statements such as upstream-issues.md's "Originally two
# issues were planned", which is a correct record of what was once true.
# Adding a phrasing here is a deliberate act; that is the point.

ISSUE_PATTERNS = [
    r"There are now (?P<n>[A-Za-z0-9]+)\b",
    r"(?P<n>[A-Za-z0-9]+) of which are drafted as\b",
    r"(?P<n>[A-Za-z0-9]+) (?:issues?|findings?) are drafted\b",
    r"(?P<n>[A-Za-z0-9]+) are drafted as public issues\b",
    r"\|\s*Upstream issues\s*\|\s*(?P<n>[A-Za-z0-9]+) drafted\b",
]

DISCREPANCY_PATTERNS = [
    r"(?P<n>[A-Za-z0-9]+) discrepancies inside TORIVA\b",
    r"the (?P<n>[A-Za-z0-9]+) discrepancies found inside TORIVA\b",
    # "Discrepancies D1 and D2 in study/source-refs.md ..." — prose enumeration
    # that silently stops being the whole list when a new one is recorded.
    r"[Dd]iscrepancies D1 and D(?P<n>\d+)\b",
]

ENDPOINT_PATTERNS = [
    r"\*\*7\.7 (?P<n>[A-Za-z0-9]+) of the three endpoints have been mapped\b",
]


def scan(files: dict[str, list[str]], patterns: list[str],
         hist: dict[str, set[int]]) -> list[Claim]:
    claims: list[Claim] = []
    for path, lines in files.items():
        for i, line in enumerate(lines, 1):
            if exempt(path, i, line, hist):
                continue
            for pat in patterns:
                for m in re.finditer(pat, line):
                    value = to_int(m.group("n"))
                    if value is not None:
                        claims.append(Claim(path, i, m.group(0).strip(), value))
    return claims


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def check_findings(root: Path, files: dict[str, list[str]],
                   hist: dict[str, set[int]]) -> tuple[list[Problem], int]:
    found = sorted(p.name for p in (root / "docs" / "findings").glob("F*.md"))
    numbers = sorted(int(n) for n in (re.match(r"F(\d+)", f).group(1) for f in found))
    problems: list[Problem] = []

    if numbers != list(range(1, len(numbers) + 1)):
        problems.append(Problem("docs/findings/", 0,
                                f"finding files are not contiguous from F01: {numbers}"))
    top = max(numbers)

    # F01-F08, F01–F08, "F01 … F08"
    pattern = re.compile(r"F01\s*(?:[-–—]|\.\.\.|…)\s*F(\d{2})")
    for path, lines in files.items():
        for i, line in enumerate(lines, 1):
            if exempt(path, i, line, hist):
                continue
            for m in pattern.finditer(line):
                stated = int(m.group(1))
                if stated != top:
                    problems.append(Problem(
                        path, i,
                        f"states range {m.group(0)!r} but docs/findings/ holds "
                        f"F01-F{top:02d} ({len(numbers)} files)"))
    return problems, top


def check_findings_index(root: Path, files: dict[str, list[str]]) -> list[Problem]:
    """Every finding is indexed, in exactly one place.

    This once required the full F01-FNN table in the top-level README too. That
    rule encoded the structure of the drifted era, in which findings were the
    product: it made the README's second heading a thirteen-row table and kept
    it there. Findings are a by-product (NORTH.md), so the index owns the list
    and the README owns a link to it.
    """
    found = sorted(p.name for p in (root / "docs" / "findings").glob("F*.md"))
    problems: list[Problem] = []

    index = "docs/findings/README.md"
    body = "\n".join(files.get(index, []))
    for name in found:
        stem = name[:3]  # F01
        if name not in body and f"[{stem}]" not in body:
            problems.append(Problem(index, 0,
                                    f"{name} is not listed in the findings index"))

    # The README need not enumerate them, but it must lead a reader to them.
    if index not in "\n".join(files.get("README.md", [])):
        problems.append(Problem("README.md", 0,
                                f"does not link to {index}, so the findings are "
                                f"unreachable from the top level"))
    return problems


def check_counted(files: dict[str, list[str]], patterns: list[str], truth: int,
                  noun: str, source: str,
                  hist: dict[str, set[int]]) -> tuple[list[Problem], list[Claim]]:
    claims = scan(files, patterns, hist)
    problems = [
        Problem(c.path, c.line,
                f"claims {c.value} {noun} ({c.text!r}) but {source} holds {truth}")
        for c in claims if c.value != truth
    ]
    return problems, claims


def check_coverage(root: Path, tracked: list[str], files: dict[str, list[str]]) -> list[Problem]:
    body = "\n".join(files.get("PROVENANCE.md", []))
    problems: list[Problem] = []

    # A basename shared by several files (endpoints/*/mapping.md) proves nothing:
    # naming one satisfies all of them. Those must appear by full path.
    counts: dict[str, int] = {}
    for rel in tracked:
        counts[Path(rel).name] = counts.get(Path(rel).name, 0) + 1

    for rel in tracked:
        if not rel.endswith((".md", ".py")):
            continue
        if rel in ("PROVENANCE.md",):
            continue
        name = Path(rel).name
        if counts[name] > 1:
            if rel not in body:
                problems.append(Problem("PROVENANCE.md", 0,
                                        f"{rel} is tracked but named nowhere in the "
                                        f"provenance record (its basename is shared "
                                        f"with {counts[name] - 1} other file(s), so it "
                                        f"must be named in full)"))
            continue
        aliases = [rel, name, Path(rel).stem]
        m = re.match(r"(F\d{2})-", name)
        if m:
            # findings are named collectively, e.g. "docs/findings/`F01`-`F08`"
            aliases.append(m.group(1))
        if not any(a in body for a in aliases):
            problems.append(Problem("PROVENANCE.md", 0,
                                    f"{rel} is tracked but named nowhere in the "
                                    f"provenance record"))
    return problems


def check_links(root: Path, files: dict[str, list[str]]) -> list[Problem]:
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    problems: list[Problem] = []
    for path, lines in files.items():
        base = (root / path).parent
        for i, line in enumerate(lines, 1):
            for m in pattern.finditer(line):
                target = m.group(1).split("#")[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                if not (base / target).exists():
                    problems.append(Problem(path, i,
                                            f"link target does not exist: {target}"))
    return problems


def check_submodule(root: Path, files: dict[str, list[str]],
                    hist: dict[str, set[int]]) -> tuple[list[Problem], list[Problem]]:
    """Returns (problems, warnings).

    A submodule that is not checked out is a state of this working copy, not a
    defect in the documents, so it warns rather than fails — otherwise a
    collaborator who has not run 'git submodule update --init' could not commit
    a typo fix. A documented sha that disagrees with the checkout is a content
    defect and does fail.
    """
    sub = root / "upstream" / "analysis-concepts"
    if not (sub / "lib").is_dir():
        return [], [Problem(".gitmodules", 0,
                            "upstream/analysis-concepts is not checked out - "
                            "docs/method.md's reproduce block will not run here. "
                            "Fix with: git submodule update --init")]

    def git(*args: str) -> str | None:
        try:
            return subprocess.run(args, capture_output=True, text=True,
                                  check=True).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    head = git("git", "-C", str(sub), "rev-parse", "HEAD")
    if head is None:
        return [], [Problem("upstream/analysis-concepts", 0,
                            "cannot read the submodule's HEAD")]

    problems: list[Problem] = []

    tree = git("git", "-C", str(root), "ls-tree", "HEAD", "upstream/analysis-concepts")
    gitlink = tree.split()[2] if tree and len(tree.split()) > 2 else None
    if gitlink and gitlink != head:
        problems.append(Problem("upstream/analysis-concepts", 0,
                                f"checked out at {head[:12]} but the parent repo "
                                f"records {gitlink[:12]}"))

    # Only hex tokens that are a near-miss of the pinned sha are treated as a
    # stale upstream pin: same first four characters, diverging after. Tokens
    # belonging to other repositories share no such prefix and are left alone.
    token = re.compile(r"([0-9a-f]{7,40})")
    seen: set[tuple[str, int, str]] = set()
    for path, lines in files.items():
        for i, line in enumerate(lines, 1):
            if exempt(path, i, line, hist):
                continue
            for m in token.finditer(line):
                sha = m.group(1)
                if head.startswith(sha):
                    continue
                if sha[:4] == head[:4]:
                    key = (path, i, sha)
                    if key not in seen:
                        seen.add(key)
                        problems.append(Problem(
                            path, i,
                            f"pins upstream at {sha} but the submodule is at "
                            f"{head[:12]}"))
    return problems, []


# --------------------------------------------------------------------------
# NORTH.md — the finish line
# --------------------------------------------------------------------------
# The compass is only useful if it cannot lie. Each stage is computed from the
# filesystem and compared against the status table in NORTH.md, so the table
# cannot quietly claim a stage that has not happened.


def _chains(root: Path) -> list[dict]:
    out = []
    for f in sorted((root / "endpoints").glob("*/chain.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    return out


def _specs(chains: list[dict]) -> list[dict]:
    return [sp for c in chains for sp in (c.get("endpointSpecs") or {}).values()]


# Per-endpoint definitions of the finish line. NORTH.md's unnamed status block
# is the first endpoint, whose stages 0, 0b and 1 were defined study-wide before
# a second endpoint existed. A named block (<!-- north:status:NAME -->) is scoped
# to its own endpoint directory, M11 section, restructured protocol file and BC
# code, so a second endpoint cannot inherit the first one's green rows.
ENDPOINTS: dict[str, dict] = {
    "": {"dir": None, "m11_mark": None, "protocol_file": None, "bc_code": None},
    "vitals": {
        "dir": "04-vitals-cfb-mmrm",
        "m11_mark": "8.4.2",
        "protocol_file": "section-08-04-02-vital-signs.md",
        "bc_code": "C25298",
    },
}


def _sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase2_stages(root: Path) -> list[tuple[str, str, bool]]:
    """Phase 2 — fix the study's gaps, digitise the protocol, verify alignment.

    Decided 2026-09-19 (NORTH.md). Each stage is computed from files, as the
    endpoint stages are, so the block cannot claim what has not happened:

      P0  study/gap-register.md exists and names every discrepancy D1..Dn from
          study/source-refs.md, each with a disposition.
      P1  study/m11/protocol/coverage.json lists the 14 M11 sections, each with
          a status that is not "not started".
      P2  the USDM fragment carries activities and scheduleTimelines AND names
          the generator that produced it (tools/m11_to_usdm.py), which exists.
      P3  tools/check_alignment.py exists and exits 0.
      P4  docs/walkthrough.md exists.
      P5  every endpoints/*/results.json carries usdm_sha256 equal to the
          current fragment's hash — i.e. the runs are against the aligned study.
    """
    import subprocess as _sp
    src = root / "study" / "source-refs.md"
    d_ids = sorted(set(re.findall(r"\bD(\d+)\b", src.read_text(encoding="utf-8", errors="replace")))) if src.is_file() else []
    reg = root / "study" / "gap-register.md"
    p0 = reg.is_file() and bool(d_ids) and all(re.search(rf"\bD{n}\b", reg.read_text(encoding="utf-8", errors="replace")) for n in d_ids) \
        and "disposition" in reg.read_text(encoding="utf-8", errors="replace").lower()

    cov = root / "study" / "m11" / "protocol" / "coverage.json"
    p1 = False
    if cov.is_file():
        try:
            c = json.loads(cov.read_text(encoding="utf-8"))
            secs = c.get("sections") if isinstance(c, dict) else c
            p1 = isinstance(secs, list) and len(secs) >= 14 and all(
                str(s.get("status", "not started")).lower() != "not started" for s in secs)
        except (OSError, json.JSONDecodeError, AttributeError):
            p1 = False

    usdm_files = [f for f in (root / "study" / "usdm").glob("*.usdm.json")] if (root / "study" / "usdm").is_dir() else []
    p2 = False
    gen = root / "tools" / "m11_to_usdm.py"
    for f in usdm_files:
        try:
            u = json.loads(f.read_text(encoding="utf-8"))
            sd = u["study"]["versions"][0]["studyDesigns"][0]
            txt = f.read_text(encoding="utf-8")
            if sd.get("activities") and sd.get("scheduleTimelines") and "tools/m11_to_usdm.py" in txt and gen.is_file():
                p2 = True
        except (OSError, json.JSONDecodeError, KeyError, IndexError, TypeError):
            pass

    aln = root / "tools" / "check_alignment.py"
    p3 = False
    if aln.is_file():
        try:
            p3 = _sp.run([sys.executable, str(aln), "--root", str(root)], capture_output=True, timeout=120).returncode == 0
        except (OSError, _sp.SubprocessError):
            p3 = False

    p4 = (root / "docs" / "walkthrough.md").is_file()

    p5 = False
    if usdm_files:
        sha = _sha256(usdm_files[0])
        results = list((root / "endpoints").glob("*/results.json"))
        p5 = bool(results) and all(
            (lambda r: r.get("usdm_sha256") == sha)(_load_json(f) or {}) for f in results)

    return [
        ("P0", "Gap register — every discrepancy with a disposition", p0),
        ("P1", "Protocol fully M11 — all 14 sections covered", p1),
        ("P2", "USDM generated from it, with the schedule of activities", p2),
        ("P3", "Alignment verified by a tool", p3),
        ("P4", "Hands-on walkthrough written", p4),
        ("P5", "Both endpoints re-run on the aligned study", p5),
    ]


PHASES: dict[str, object] = {"phase2": phase2_stages}


def north_stages(root: Path, name: str = "") -> list[tuple[str, str, bool]]:
    """The stages of NORTH.md's finish line, each computed from the repository.

    `name` selects the endpoint (see ENDPOINTS). The unnamed endpoint keeps the
    original study-wide definitions; a named one is scoped to its own files.
    """
    ep = ENDPOINTS[name]
    ep_glob = f"{ep['dir']}/" if ep["dir"] else "*/"
    chains = [c for f in sorted((root / "endpoints").glob(ep_glob + "chain.json"))
              for c in [_load_json(f)] if c is not None]
    specs = _specs(chains)

    m11 = root / "study" / "m11"
    usdm_text = "".join(
        f.read_text(encoding="utf-8", errors="replace")
        for f in (root / "study" / "usdm").iterdir() if f.is_file()
    ) if (root / "study" / "usdm").is_dir() else ""
    if ep["m11_mark"]:
        mapping = m11 / "protocol-to-m11.md"
        stage0 = mapping.is_file() and ep["m11_mark"] in mapping.read_text(encoding="utf-8", errors="replace")
        prot_file = m11 / "protocol" / ep["protocol_file"]
        stage0b = prot_file.is_file() and ep["protocol_file"] in usdm_text
        stage1 = ep["bc_code"] in usdm_text
        return _north_rows(root, ep_glob, specs, stage0, stage0b, stage1)

    stage0 = m11.is_dir() and any(m11.iterdir())

    # 0b: the protocol restructured to M11, AND the USDM regenerated from it.
    # Both halves are required: a restructured section that nothing downstream
    # consumes leaves stage 1's fragment still transcribed from prose, which is
    # the thing 0b exists to fix.
    prot = m11 / "protocol"
    restructured = prot.is_dir() and any(prot.iterdir())
    usdm_dir = root / "study" / "usdm"
    regenerated = usdm_dir.is_dir() and any(
        "study/m11/protocol" in f.read_text(encoding="utf-8", errors="replace")
        for f in usdm_dir.iterdir() if f.is_file()
    )
    stage0b = restructured and regenerated

    usdm = root / "study" / "usdm"
    stage1 = usdm.is_dir() and any(usdm.iterdir())
    return _north_rows(root, ep_glob, specs, stage0, stage0b, stage1)


def _load_json(f: Path):
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _north_rows(root: Path, ep_glob: str, specs: list[dict],
                stage0: bool, stage0b: bool, stage1: bool) -> list[tuple[str, str, bool]]:
    def linked(sp: dict) -> bool:
        if sp.get("linkedBCIds"):
            return True
        return any(t.get("linkedBCIds") for t in (sp.get("confirmedTerminals") or []))

    stage2 = any(linked(sp) for sp in specs)
    stage3 = any(sp.get("derivationChain") or sp.get("selectedDerivations") for sp in specs)
    stage4 = any(sp.get("selectedTransformationOid") for sp in specs)
    stage5 = any((root / "endpoints").glob(ep_glob + "esap*"))
    stage6 = any((root / "endpoints").glob(ep_glob + "results*"))

    # Stage 7 is "compared against built ADaM", inside a finish line whose stage 6
    # is "executed, a real result produced". So what is compared is the RESULT.
    # A comparison.md with no execution behind it compares *definitions* — useful,
    # and not what the row claims. This was green from 2026-09-16 to 2026-09-17 on
    # the weaker test, while the stronger one had never been attempted, which is
    # precisely the quiet lie the scoreboard exists to prevent.
    stage7 = any((root / "endpoints").glob(ep_glob + "comparison.md")) and stage6

    return [
        ("0",  "Protocol mapped to ICH M11 elements", stage0),
        ("0b", "Protocol restructured to M11, USDM regenerated from it", stage0b),
        ("1",  "USDM fragments hand-authored", stage1),
        ("2",  "BC linked on the chain's terminals", stage2),
        ("3",  "DC — derivation authored", stage3),
        ("4",  "AC — analysis bound", stage4),
        ("5",  "eSAP generated", stage5),
        ("6",  "Executed, a real result produced", stage6),
        ("7",  "Compared against built ADaM", stage7),
    ]


TRUE_MARKS = {"✓", "✔", "yes", "y", "done"}
FALSE_MARKS = {"✗", "✘", "no", "n", "x", ""}


def check_north(root: Path, files: dict[str, list[str]]) -> list[Problem]:
    """NORTH.md's status table must match what the filesystem says."""
    lines = files.get("NORTH.md")
    if lines is None:
        return [Problem("NORTH.md", 0,
                        "NORTH.md is missing — it is the project's destination and the "
                        "only statement of what 'done' means")]

    # Rows count only inside a marker block: <!-- north:status --> for the first
    # endpoint, <!-- north:status:NAME --> for a named one. Two tables with the
    # same stage numbers would otherwise overwrite each other.
    stated: dict[str, dict[str, tuple[int, bool]]] = {}
    row = re.compile(r"^\|\s*([0-9P][0-9a-z]?)\s*\|([^|]*)\|\s*(\S*)\s*\|\s*$")
    open_mark = re.compile(r"<!--\s*north:status(?::([A-Za-z0-9_-]+))?\s*-->")
    close_mark = re.compile(r"<!--\s*/north:status")
    block: str | None = None
    problems: list[Problem] = []
    for i, line in enumerate(lines, 1):
        m = open_mark.search(line)
        if m:
            block = m.group(1) or ""
            if block not in ENDPOINTS and block not in PHASES:
                problems.append(Problem("NORTH.md", i,
                                        f"status block {block!r} is not a known endpoint "
                                        f"(tools/check_consistency.py ENDPOINTS)"))
            stated.setdefault(block, {})
            continue
        if close_mark.search(line):
            block = None
            continue
        if block is None or (block not in ENDPOINTS and block not in PHASES):
            continue
        m = row.match(line)
        if not m:
            continue
        num, mark = m.group(1), m.group(3).strip().lower()
        if mark in TRUE_MARKS:
            stated[block][num] = (i, True)
        elif mark in FALSE_MARKS:
            stated[block][num] = (i, False)

    if "" not in stated:
        problems.append(Problem("NORTH.md", 0, "no <!-- north:status --> block found"))
    for name, rows in stated.items():
        if name not in ENDPOINTS and name not in PHASES:
            continue
        tag = f" [{name}]" if name else ""
        computed = north_stages(root, name) if name in ENDPOINTS else PHASES[name](root)
        for num, label, actual in computed:
            if num not in rows:
                problems.append(Problem("NORTH.md", 0,
                                        f"stage {num}{tag} ({label}) has no row in its status table"))
                continue
            line_no, claimed = rows[num]
            if claimed != actual:
                problems.append(Problem(
                    "NORTH.md", line_no,
                    f"stage {num}{tag} ({label}) is marked "
                    f"{'done' if claimed else 'not done'} but the filesystem says "
                    f"{'done' if actual else 'not done'}"))
    return problems


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repository root (default: .)")
    ap.add_argument("--verbose", action="store_true",
                    help="list every claim that was matched and checked")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    root = Path(args.root).resolve()
    try:
        tracked = subprocess.run(["git", "-C", str(root), "ls-files"],
                                 capture_output=True, text=True,
                                 check=True).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"error: {root} is not a git checkout", file=sys.stderr)
        return 2

    files: dict[str, list[str]] = {}
    for rel in tracked:
        if rel.endswith(".md"):
            p = root / rel
            if p.is_file():
                files[rel] = p.read_text(encoding="utf-8").splitlines()

    hist = {path: historical_lines(lines) for path, lines in files.items()}

    print("Repository consistency report")
    print(f"root:    {root}")
    print(f"scanned: {len(files)} markdown files, {len(tracked)} tracked paths")

    problems: list[Problem] = []
    all_claims: list[Claim] = []

    finding_problems, n_findings = check_findings(root, files, hist)
    problems += finding_problems
    problems += check_findings_index(root, files)

    n_issues = sum(
        1 for line in files.get("docs/findings/upstream-issues.md", [])
        if re.match(r"^## Issue \d", line)
    )
    p, c = check_counted(files, ISSUE_PATTERNS, n_issues,
                         "drafted issues", "upstream-issues.md", hist)
    problems += p
    all_claims += c

    d_ids = sorted({
        int(m.group(1))
        for line in files.get("study/source-refs.md", [])
        for m in [re.match(r"\|\s*\*\*D(\d+)\*\*", line)] if m
    })
    if d_ids and d_ids != list(range(1, len(d_ids) + 1)):
        problems.append(Problem("study/source-refs.md", 0,
                                f"D-ids are not contiguous from D1: {d_ids}"))
    n_disc = len(d_ids)
    p, c = check_counted(files, DISCREPANCY_PATTERNS, n_disc,
                         "discrepancies", "the source-refs table", hist)
    problems += p
    all_claims += c

    for path, lines in files.items():
        for i, line in enumerate(lines, 1):
            if exempt(path, i, line, hist):
                continue
            for m in re.finditer(r"\bD1\s*[-–—]\s*D(\d+)\b", line):
                if int(m.group(1)) != n_disc:
                    problems.append(Problem(
                        path, i,
                        f"states range {m.group(0)!r} but the source-refs table "
                        f"holds D1-D{n_disc}"))

    tiers = sorted(p.name for p in (root / "endpoints").iterdir() if p.is_dir())
    mapped = sorted(p.parent.name for p in (root / "endpoints").glob("*/mapping.md"))
    p, c = check_counted(files, ENDPOINT_PATTERNS, len(mapped),
                         "mapped endpoints", "endpoints/*/mapping.md", hist)
    problems += p
    all_claims += c

    problems += check_coverage(root, tracked, files)
    problems += check_links(root, files)
    sub_problems, warnings = check_submodule(root, files, hist)
    problems += sub_problems
    problems += check_north(root, files)

    north_text = "\n".join(files.get("NORTH.md", []))
    for name in list(ENDPOINTS) + list(PHASES):
        marker = "<!-- north:status" + (f":{name}" if name else "") + " -->"
        if marker not in north_text:
            continue
        stages = north_stages(root, name) if name in ENDPOINTS else PHASES[name](root)
        done = sum(1 for _, _, ok in stages if ok)
        print()
        print(f"NORTH — finish line{' [' + name + ']' if name else ''}: {done} of {len(stages)} stages")
        for num, label, ok in stages:
            print(f"  [{'x' if ok else ' '}] {num}. {label}")
        if done < len(stages):
            print("  → the test: which numbered stage does the next piece of work advance?")
    print()

    print(f"truth:   {n_findings} findings, {n_issues} drafted issues, "
          f"{n_disc} discrepancies, {len(mapped)}/{len(tiers)} endpoints mapped")

    if args.verbose and all_claims:
        print("\nClaims checked")
        print("--------------")
        for c in sorted(all_claims, key=lambda x: (x.path, x.line)):
            print(f"  {c.path}:{c.line}  {c.value}  {c.text!r}")

    print()
    if warnings:
        for warn in warnings:
            print(f"warning: {warn.message}")
        print()

    if problems:
        print(f"{len(problems)} inconsistenc{'y' if len(problems) == 1 else 'ies'}:")
        print()
        for prob in problems:
            print(prob)
        print()
        print("Ground truth is the filesystem. Update the documents.")
        return 1

    print("Consistent. Every counted claim matches the filesystem.")
    print()
    print("Note: this checks counts and cross-references, not whether a claim is")
    print("still true. Semantic drift needs the verification pass (docs/method.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
