"""mutate_alignment.py — does check_alignment.py actually check what it says it checks?

Review-sheet phase 2, item 4a (2026-09-20). For each documents-layer PASS, copy study/ into a scratch
root, corrupt the one thing the check claims to verify, run the tool there, and record whether that
item FAILs. A check that still passes on the corrupted copy is vacuous. On its first run four of
sixteen mutations survived; two were weak mutations, two were weak checks (G4 matched the
three-letter code as a substring, G7 matched the word 'shift'), and the checks were tightened.

    python tools/mutate_alignment.py        # from the repository root; exits 1 if anything survives

For each documents-layer check, copy study/ into a scratch root, corrupt the one thing the check claims
to verify, run the tool there, and record whether that item FAILs. A check that still passes on the
corrupted copy is vacuous. Data layer is skipped in the scratch root (no TORIVA sibling), by design.
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = "study/m11/protocol/"
MUT = [
 # (item expected to FAIL, file, old, new)
 ("D13", P + "section-03-objectives-endpoints.md", "Stratified Mantel–Haenszel **risk difference** (torivumab − placebo)", "Stratified Mantel–Haenszel **odds ratio** (torivumab − placebo)"),
 ("G3",  P + "section-00-title-page.md", "| Optional elements deliberately left unmapped | 1 — EudraCT, see note 1 |", "| Optional elements deliberately left unmapped | 0 |"),
 ("G2",  P + "section-00-title-page.md", "Republic of Korea, ", ""),
 ("G2",  P + "section-00-title-page.md", "**Sponsor Approval Date** | 22 March 2026", "**Sponsor Approval Date** | not stated"),
 ("G5",  P + "section-12-01-clinical-laboratory-tests.md", "local results are not used for analysis", "local results are used for analysis"),
 ("G6",  P + "section-08-04-02-vital-signs.md", "rested for at least five minutes", "rested briefly"),
 ("G9",  P + "section-08-assessments-and-procedures.md", "28 days before Cycle 1 Day 1", "before Cycle 1 Day 1"),
 ("G7",  P + "section-03-objectives-endpoints.md", "(ii) shift from baseline", "(ii) change from baseline"),
 ("D11", P + "section-03-objectives-endpoints.md", "CTCAE v5.0 grade by parameter, with a listing of grade ≥3 abnormalities", "toxicity grade by parameter, with a listing"),
 ("S1",  P + "section-10-statistical-considerations.md", "**demonstration analyses**", "**analyses**"),
 ("D14", "study/usdm/toriva-lung-301.usdm.json", '"name": "Placebo + Chemotherapy"', '"name": "Placebo"'),
 ("D14", P + "section-00-title-page.md", "plus Platinum-Based Chemotherapy versus Placebo plus Platinum-Based Chemotherapy", "versus Placebo"),
 ("D15", "study/usdm/toriva-lung-301.usdm.json", "Randomisation 2:1 (D15, the protocol stands)", "Randomisation 1:1 (D15)"),
 ("G4",  P + "section-12-01-clinical-laboratory-tests.md", "Alkaline Phosphatase", "Alkaline Phos."),
 ("G1",  "study/usdm/toriva-lung-301.usdm.json", None, None),  # special: drop one estimand
 ("USDM↔protocol:END-OS", "study/usdm/toriva-lung-301.usdm.json", None, None),  # handled specially: append a word to END-OS text
 ("G8",  P + "coverage.json", None, None),  # handled specially: drop section 14
]
results = []
for item, f, old, new in MUT:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aln_"))
    shutil.copytree(ROOT / "study", tmp / "study")
    target = tmp / f
    txt = target.read_text(encoding="utf-8")
    if old is None:
        if f.endswith("usdm.json"):
            d = json.loads(txt)
            sdd = d["study"]["versions"][0]["studyDesigns"][0]
            if item == "G1":
                sdd["estimands"] = sdd["estimands"][:-1]
            for o in sdd["objectives"]:
                for e in o["endpoints"]:
                    if item != "G1" and e["name"] == "END-OS": e["text"] = e["text"] + " (investigator-assessed)"
            txt2 = json.dumps(d, ensure_ascii=False)
        else:
            d = json.loads(txt); secs = d.get("sections", d)
            secs = [s for s in secs if not str(s.get("section", s.get("num", ""))).startswith("14")]
            if isinstance(d, dict): d["sections"] = secs
            else: d = secs
            txt2 = json.dumps(d, ensure_ascii=False)
    else:
        assert txt.count(old) >= 1, (item, f, old[:50]); txt2 = txt.replace(old, new)
    target.write_text(txt2, encoding="utf-8")
    run = subprocess.run([sys.executable, str(ROOT / "tools/check_alignment.py"), "--root", str(tmp)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    failed_items = set(re.findall(r"^\s*FAIL\s+\S+\s+(\S+)", run.stdout, re.M))
    caught = item in failed_items
    results.append((item, f.split("/")[-1], (old or "special")[:45], caught, run.returncode, sorted(failed_items)))
    shutil.rmtree(tmp, ignore_errors=True)
print(f"{'item':24s} {'file':44s} {'mutation':47s} caught  exit  all FAILs")
for item, f, m, caught, rc, fails in results:
    print(f"{item:24s} {f:44s} {m:47s} {'YES' if caught else 'NO ':5s}   {rc}    {fails}")
print("\nvacuous (not caught):", [r[0] + ':' + r[2][:30] for r in results if not r[3]] or "none")
sys.exit(0 if all(r[3] for r in results) else 1)
