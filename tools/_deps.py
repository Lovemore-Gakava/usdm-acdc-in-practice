"""
_deps.py — one message for the mistake every parquet-reading tool invites.

The data dependencies live in .venv (tools/bootstrap.py puts them there), so
running one of these tools with the system interpreter fails. On macOS that is
the *likely* thing to type, because `python3` is on PATH and `python` is not.

A bare ModuleNotFoundError does not mention .venv, so the reader has no way to
know the machine is already set up correctly and only the interpreter is wrong.
This says which interpreter would have worked, and reconstructs the command
from sys.argv so it can be pasted.

Behaviour is the caller's: walkthrough.py cannot continue and exits,
check_alignment.py records a SKIP because P3 is scored from whether the data
layer ran, check_baseline_ambiguity.py exits 2. Only the wording is shared.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def venv_python() -> Path:
    """The interpreter tools/bootstrap.py creates."""
    if os.name == "nt":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def _invocation() -> str:
    """The command that was run, relative to the repository root where possible."""
    try:
        script = Path(sys.argv[0]).resolve().relative_to(ROOT)
    except (ValueError, OSError):
        script = Path(sys.argv[0])
    return " ".join([script.as_posix(), *sys.argv[1:]])


def venv_cmd() -> str:
    """The current invocation, re-pointed at .venv's interpreter. Paths relative
    to the repository root where possible, so the line can be pasted."""
    py = venv_python()
    try:
        shown = py.relative_to(ROOT).as_posix()
    except ValueError:
        shown = str(py)
    return f"{shown} {_invocation()}"


def hint(package: str) -> str:
    """Why `import <package>` failed, and the command that would have worked."""
    if venv_python().is_file():
        return (
            f"{package} is not installed for this interpreter ({sys.executable}).\n"
            f"It is in .venv. Run:\n"
            f"    {venv_cmd()}"
        )
    cmd = _invocation()
    return (
        f"{package} is not installed, and there is no .venv yet.\n"
        f"Set the repository up first, with whatever Python this machine has:\n"
        f"    python tools/bootstrap.py        # python3 on macOS and Linux\n"
        f"then re-run:\n"
        f"    .venv/bin/python {cmd}"
    )
