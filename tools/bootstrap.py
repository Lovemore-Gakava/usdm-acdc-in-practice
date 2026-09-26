#!/usr/bin/env python3
"""
bootstrap.py — take a fresh clone to a green P3 on any machine.

Portability is a stage concern, not housekeeping: NORTH.md scores P3 from
tools/check_alignment.py exiting 0 *with the data layer run*, and the data layer
needs a TORIVA checkout at the pinned commit plus pyarrow. On a clone that has
neither, P3 is red. This script supplies both, and then proves it by running the
checker.

Idempotent: safe to re-run. Every step reports "ok" when it was already done.

  python tools/bootstrap.py                 # or python3 / py -3, whichever exists
  python tools/bootstrap.py --toriva PATH   # use an existing TORIVA checkout
  python tools/bootstrap.py --no-clone      # never fetch TORIVA; report and move on
  python tools/bootstrap.py --check         # report what is missing, change nothing

Run it with any Python 3.9+; it builds the virtual environment with the newest
3.10+ interpreter it can find, because pyreadstat (step 8 needs .xpt) requires
3.10 or newer. The repository's own tools run on 3.9 — the floor comes from the
dependencies, not the code.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv"
REQS = ROOT / "requirements.txt"
TORIVA_URL = "https://github.com/OpenTrialReporting/torivumab-nsclc-301.git"
TORIVA_DEFAULT = ROOT.parent / "torivumab-nsclc-301"

# Enough of TORIVA for the data layer and the document checks, and no more:
# the full checkout is ~81 MB, this is ~10 MB. datasets/adam is what
# find_toriva() looks for and what check_alignment's DATA checks read.
SPARSE = ["/datasets/adam/", "/protocol/", "/programming-specs/", "/sap/", "/define/"]

FAIL = []


def say(msg: str) -> None:
    print(msg, flush=True)


def step(n: str, msg: str) -> None:
    print(f"\n[{n}] {msg}", flush=True)


def run(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd) if cwd else None, check=check,
                          capture_output=True, text=True)


def git(*args: str, cwd: Path | None = None) -> str:
    return run("git", *args, cwd=cwd or ROOT).stdout.strip()


def venv_python(venv: Path = VENV) -> Path:
    return venv / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")


def pinned_commit() -> str | None:
    """The TORIVA commit study/source-refs.md pins. Single source of truth — same
    regex walkthrough.py's check_pin uses, so the two cannot disagree."""
    src = ROOT / "study" / "source-refs.md"
    if not src.is_file():
        return None
    m = re.search(r"\| Commit \| `([0-9a-f]{40})`", src.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def find_interpreter() -> str | None:
    """Newest Python >= 3.10 available. pyreadstat needs it; the tools do not."""
    if sys.version_info >= (3, 10):
        cands = [sys.executable]
    else:
        cands = []
    cands += [f"python3.{m}" for m in range(14, 9, -1)] + ["python3", "python"]
    for c in cands:
        exe = shutil.which(c) if not Path(c).is_absolute() else c
        if not exe:
            continue
        try:
            v = subprocess.run([exe, "-c", "import sys;print('%d.%d' % sys.version_info[:2])"],
                               capture_output=True, text=True, check=True).stdout.strip()
            if tuple(int(x) for x in v.split(".")) >= (3, 10):
                return exe
        except Exception:
            continue
    return None


# --------------------------------------------------------------------------- steps

def do_submodule(check_only: bool) -> None:
    step("1/5", "upstream submodule")
    sub = ROOT / "upstream" / "analysis-concepts"
    if (sub / "lib").is_dir():
        say(f"  ok — checked out at {git('rev-parse', '--short', 'HEAD', cwd=sub)}")
        return
    if check_only:
        say("  MISSING — run without --check to initialise")
        FAIL.append("submodule")
        return
    say("  initialising ...")
    run("git", "submodule", "update", "--init", "--recursive", cwd=ROOT)
    say(f"  done — at {git('rev-parse', '--short', 'HEAD', cwd=sub)}")


def do_hooks(check_only: bool) -> None:
    step("2/5", "pre-commit hook (runs check_consistency.py)")
    # `git config --get` exits 1 when the key is unset, which is not an error here
    cur = run("git", "config", "--get", "core.hooksPath", cwd=ROOT, check=False).stdout.strip()
    if cur == ".githooks":
        say("  ok — core.hooksPath is .githooks")
        return
    if check_only:
        say("  not set — run without --check to enable")
        return
    run("git", "config", "core.hooksPath", ".githooks", cwd=ROOT)
    say("  set core.hooksPath=.githooks")


def do_venv(check_only: bool) -> Path | None:
    step("3/5", "virtual environment and dependencies")
    py = venv_python()
    if py.is_file():
        try:
            run(str(py), "-c", "import pyarrow, pandas, pyreadstat")
            v = run(str(py), "-c", "import sys;print('%d.%d.%d' % sys.version_info[:3])").stdout.strip()
            say(f"  ok — .venv on Python {v} with pyarrow, pandas, pyreadstat")
            return py
        except subprocess.CalledProcessError:
            say("  .venv exists but a dependency is missing — reinstalling")
    if check_only:
        say("  MISSING — run without --check to create .venv")
        FAIL.append("venv")
        return None
    interp = find_interpreter()
    if not interp:
        say("  FAILED — no Python 3.10+ found. Install one (python.org, brew, apt) and re-run.")
        FAIL.append("venv")
        return None
    if not py.is_file():
        say(f"  creating .venv with {interp} ...")
        run(interp, "-m", "venv", str(VENV))
    py = venv_python()
    say("  installing dependencies ...")
    run(str(py), "-m", "pip", "install", "-q", "--upgrade", "pip")
    run(str(py), "-m", "pip", "install", "-q", "-r", str(REQS))
    v = run(str(py), "-c", "import sys;print('%d.%d.%d' % sys.version_info[:3])").stdout.strip()
    say(f"  done — .venv on Python {v}")
    return py


def do_toriva(arg: str | None, check_only: bool, no_clone: bool) -> Path | None:
    step("4/5", "TORIVA-LUNG 301 checkout")
    pin = pinned_commit()
    if not pin:
        say("  cannot read the pin from study/source-refs.md")
        FAIL.append("toriva")
        return None

    for cand in (arg, os.environ.get("TORIVA_DIR"), str(TORIVA_DEFAULT)):
        if cand and (Path(cand) / "datasets" / "adam" / "adsl.parquet").is_file():
            tor = Path(cand).resolve()
            head = git("rev-parse", "HEAD", cwd=tor)
            if head == pin:
                say(f"  ok — {tor} at {head[:8]}, as study/source-refs.md pins")
            else:
                say(f"  WARNING: {tor} is at {head[:8]} but the pin is {pin[:8]}")
                say("  the numbers in the walkthrough are for the pin; check it out or re-pin deliberately (CLAUDE.md)")
            return tor

    if check_only or no_clone:
        say(f"  MISSING — no checkout with datasets/adam/adsl.parquet at {TORIVA_DEFAULT}")
        say("  P3's data layer cannot run without it, so the row is red on this clone")
        FAIL.append("toriva")
        return None

    say(f"  cloning at the pin into {TORIVA_DEFAULT} (sparse, ~10 MB of 81) ...")
    run("git", "clone", "--filter=blob:none", "--no-checkout", "-q", TORIVA_URL, str(TORIVA_DEFAULT))
    run("git", "sparse-checkout", "init", "--no-cone", cwd=TORIVA_DEFAULT)
    # MSYS_NO_PATHCONV: on Git Bash for Windows, MSYS rewrites each leading-slash
    # pattern into a Windows path and the checkout silently yields an empty tree.
    env = dict(os.environ, MSYS_NO_PATHCONV="1")
    subprocess.run(["git", "sparse-checkout", "set", *SPARSE], cwd=str(TORIVA_DEFAULT),
                   check=True, capture_output=True, text=True, env=env)
    run("git", "checkout", "-q", pin, cwd=TORIVA_DEFAULT)
    say(f"  done — at {git('rev-parse', '--short', 'HEAD', cwd=TORIVA_DEFAULT)}")
    return TORIVA_DEFAULT


def do_verify(py: Path | None, tor: Path | None) -> None:
    step("5/5", "verify — tools/check_alignment.py, which is what P3 is scored on")
    if not py or not py.is_file():
        say("  skipped: no .venv")
        return
    cmd = [str(py), str(ROOT / "tools" / "check_alignment.py")]
    if tor:
        cmd += ["--toriva", str(tor)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    tail = [ln for ln in p.stdout.splitlines() if ln.strip()][-2:]
    for ln in tail:
        say("  " + ln)
    if p.returncode != 0:
        FAIL.append("alignment")
    elif "0 skip" not in p.stdout:
        say("  note: the data layer did not run — P3 stays red without TORIVA")


def main() -> int:
    ap = argparse.ArgumentParser(description="Take a fresh clone to a green P3.")
    ap.add_argument("--toriva", default=None, help="path to an existing TORIVA-LUNG 301 checkout")
    ap.add_argument("--no-clone", action="store_true", help="never fetch TORIVA; report and continue")
    ap.add_argument("--check", action="store_true", help="report what is missing, change nothing")
    args = ap.parse_args()

    say(f"bootstrap — {ROOT}")
    if args.check:
        say("(--check: reporting only, nothing will be changed)")

    do_submodule(args.check)
    do_hooks(args.check)
    py = do_venv(args.check)
    tor = do_toriva(args.toriva, args.check, args.no_clone)
    if not args.check:
        do_verify(py, tor)

    pyx = venv_python()
    rel = pyx.relative_to(ROOT) if pyx.is_file() else Path(".venv/bin/python")
    say("")
    if FAIL:
        say(f"incomplete: {', '.join(sorted(set(FAIL)))}")
        return 1
    say("ready. Use the virtual environment's interpreter for anything reading parquet:")
    say(f"  {rel} tools/walkthrough.py serve      # app + guide on :8080")
    say(f"  {rel} tools/check_alignment.py        # P3")
    say(f"  git commit{' ' * max(1, len(str(rel)) - 6)}                     # runs check_consistency.py via .githooks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
