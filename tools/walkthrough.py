#!/usr/bin/env python
"""walkthrough.py — the set-up and tear-down half of docs/walkthrough.md, as one command.

    python tools/walkthrough.py stage     # check the pin, convert TORIVA's parquet to .xpt, stage the study,
                                          # chains and the M.MMRM implementation into the app
    python tools/walkthrough.py serve     # 'stage', then serve the app until Ctrl-C, then 'clean'
    python tools/walkthrough.py clean     # remove everything staged; the submodule is clean at its pin again

Option: --toriva <path> (default: a sibling checkout named torivumab-nsclc-301). The port is serve.py's, 8080.

What it does not do is the clicking: steps 1–8 of the walkthrough are yours. The Load button and
alert() freeze browser automation, so nothing here drives the page either.

The staged files live inside the pinned, read-only submodule (ac-dc-app/data/usdm/studies.json is
edited; new files are added under ac-dc-app/data/). 'clean' reverts the edit and deletes the files,
and refuses to finish while `git status` inside the submodule is not empty.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "upstream" / "analysis-concepts"
APP = SUB / "ac-dc-app"
STAGED = APP / "data" / "toriva"
USDM_SRC = ROOT / "study" / "usdm" / "toriva-lung-301.usdm.json"
USDM_DST = APP / "data" / "usdm" / "toriva-lung-301.usdm.json"
STUDIES = APP / "data" / "usdm" / "studies.json"
CHAINS = {
    "lab-chain.json": ROOT / "endpoints" / "01-simple-lab-cfb" / "chain.json",
    "chain-mmrm.json": ROOT / "endpoints" / "04-vitals-cfb-mmrm" / "chain-mmrm.json",
    "chain-ancova.json": ROOT / "endpoints" / "04-vitals-cfb-mmrm" / "chain.json",
    "r_impl_mmrm.json": ROOT / "endpoints" / "04-vitals-cfb-mmrm" / "r_impl_mmrm.json",
}
INDUCTION = ["Baseline", "C1D15", "C2D1", "C3D1", "C4D1", "C5D1", "C6D1"]


for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def say(msg: str) -> None:
    print(msg, flush=True)


OWN = ("ac-dc-app/data/usdm/studies.json", "ac-dc-app/data/usdm/toriva-lung-301.usdm.json", "ac-dc-app/data/toriva/")


def foreign_dirt() -> str:
    """Submodule status lines that are not this script's own staged files."""
    lines = [l for l in git("status", "--short").splitlines() if l.strip()]
    return "\n".join(l for l in lines if not any(l[3:].strip().startswith(o) for o in OWN))


def git(*args: str, cwd: Path = SUB) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True).stdout.strip()


def find_toriva(arg: str | None) -> Path:
    for cand in (arg, os.environ.get("TORIVA_DIR"), str(ROOT.parent / "torivumab-nsclc-301")):
        if cand and (Path(cand) / "datasets" / "adam" / "adsl.parquet").is_file():
            return Path(cand)
    sys.exit("TORIVA checkout not found: pass --toriva, set TORIVA_DIR, or clone it beside this repository")


def check_pin(tor: Path) -> None:
    pin = re.search(r"\| Commit \| `([0-9a-f]{40})`", (ROOT / "study" / "source-refs.md").read_text(encoding="utf-8"))
    head = git("rev-parse", "HEAD", cwd=tor)
    if pin and head == pin.group(1):
        say(f"pin OK: TORIVA checkout at {head[:8]}, as study/source-refs.md pins")
    else:
        say(f"WARNING: TORIVA checkout at {head[:8]} but study/source-refs.md pins {pin.group(1)[:8] if pin else '?'} — "
            "the numbers in the walkthrough are for the pin; re-pin deliberately (CLAUDE.md) or check out the pin")
    sub_head = git("rev-parse", "HEAD")
    dirt = git("status", "--short")
    state = "clean" if not dirt else ("only this script's staged files present" if not foreign_dirt() else "NOT CLEAN — foreign changes, fix by hand")
    say(f"submodule at {sub_head[:7]} ({state})")


def to_xpt(tor: Path) -> None:
    import pyarrow.parquet as pq  # noqa: WPS433 — optional dependency, only for stage
    import pyreadstat

    adam = tor / "datasets" / "adam"
    STAGED.mkdir(parents=True, exist_ok=True)

    def write(name: str, df, fname: str) -> None:
        for c in df.columns:
            if str(df[c].dtype) in ("object", "str", "string"):
                df[c] = df[c].astype(str).where(df[c].notna(), None)
        pyreadstat.write_xport(df, str(STAGED / fname), file_format_version=5, table_name=name.upper())
        say(f"  {fname}: {len(df)} rows")

    for name in ("adsl", "adlb"):
        write(name, pq.ParquetFile(adam / f"{name}.parquet").read().to_pandas(), f"{name}.xpt")
    advs = pq.ParquetFile(adam / "advs.parquet").read().to_pandas()
    present = [v for v in INDUCTION if v in set(advs["AVISIT"])]
    write("advs", advs[advs["AVISIT"].isin(present)].copy(), "advs_induction.xpt")
    say(f"  induction window: {', '.join(present)}")


def stage(args: argparse.Namespace) -> None:
    tor = find_toriva(args.toriva)
    check_pin(tor)
    if foreign_dirt():
        sys.exit("the submodule carries changes that are not this script's:\n" + foreign_dirt() + "\nit must be clean at its pin (CLAUDE.md) — fix by hand")
    say("converting TORIVA's ADaM to .xpt (adsl, adlb, advs induction window) — about a minute for adlb ...")
    to_xpt(tor)
    for dst, src in CHAINS.items():
        shutil.copy2(src, STAGED / dst)
    shutil.copy2(USDM_SRC, USDM_DST)
    manifest = json.loads(STUDIES.read_text(encoding="utf-8"))
    entries = manifest if isinstance(manifest, list) else manifest["studies"]
    if not any(e.get("file") == USDM_DST.name for e in entries):
        entries.append({"file": USDM_DST.name})
    STUDIES.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    say(f"staged: {USDM_DST.name} + manifest entry, {len(CHAINS)} chain/implementation files, 3 .xpt files under ac-dc-app/data/")
    say("""
In the app (http://localhost:8080/ac-dc-app/index.html) the study card is TORIVA-LUNG 301.
Load a saved chain from the browser console instead of the Load button (it opens a native picker):

  const ser = await import('/ac-dc-app/js/utils/instance-serializer.js');
  ser.deserializeStudyInstance(await (await fetch('/ac-dc-app/data/toriva/lab-chain.json')).json(), window.appState);

Step 8 data: upload from ac-dc-app/data/toriva/ (adsl.xpt, adlb.xpt; advs_induction.xpt for the vitals pass).
MMRM pass, once per page load, in the console on step 8:

  const impl = await (await fetch('/ac-dc-app/data/toriva/r_impl_mmrm.json')).json();
  window.appState.methodImplementationCatalog.implementations['M.MMRM'] = [impl];
  const eng = await import('/ac-dc-app/js/utils/webr-engine.js');
  await eng.executeR('webr::install("mmrm")');
""")


def clean(_: argparse.Namespace | None = None) -> None:
    subprocess.run(["git", "-C", str(SUB), "checkout", "--", "ac-dc-app/data/usdm/studies.json"], check=False)
    if USDM_DST.exists():
        USDM_DST.unlink()
    if STAGED.exists():
        import time
        for attempt in range(6):  # a serve or stage still writing an .xpt holds the file for a moment on Windows
            try:
                shutil.rmtree(STAGED); break
            except PermissionError as e:
                if attempt == 5:
                    sys.exit(f"cannot remove {STAGED}: {e}\nis a `walkthrough.py serve` or `stage` still running? stop it, then run clean again")
                say("  a staged file is still in use; waiting ..."); time.sleep(5)
    status = git("status", "--short")
    if status:
        sys.exit(f"the submodule is still not clean:\n{status}\nfix by hand — it must be clean at its pin")
    say(f"clean: submodule at {git('rev-parse', 'HEAD')[:7]}, nothing staged")


def serve(args: argparse.Namespace) -> None:
    stage(args)
    say("serving http://localhost:8080/ac-dc-app/index.html — Ctrl-C to stop and clean up")
    proc = subprocess.Popen([sys.executable, "ac-dc-app/serve.py"], cwd=str(SUB))
    try:
        proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM) if os.name != "nt" else proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        clean()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["stage", "serve", "clean"])
    ap.add_argument("--toriva", default=None, help="path to the TORIVA-LUNG 301 checkout")
    args = ap.parse_args()
    {"stage": stage, "serve": serve, "clean": clean}[args.command](args)


if __name__ == "__main__":
    main()
