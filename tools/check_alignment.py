#!/usr/bin/env python3
"""
check_alignment.py — do the protocol, the USDM, the SAP excerpt and the built ADaM agree?

Phase 2, stage P3 (NORTH.md). The checklist is study/gap-register.md: every row
whose disposition is "fix here" must be verifiable in the files its Action
column names, and every "upstream only" row is reported as a known divergence
between the documents and the built data rather than silently passing. A
fix-here row without a check here is itself a failure, so the register cannot
grow a promise this tool does not test.

Two layers:
  DOCUMENTS — always run: the M11 sections, the USDM fragment, coverage.json.
  DATA      — run when TORIVA's ADaM parquet files are found (--toriva, the
              TORIVA_DIR environment variable, or a sibling checkout named
              torivumab-nsclc-301). Skipped, and said so, otherwise.

Verdicts: PASS, FAIL (a fix-here promise not kept), WARN (a known upstream-only
divergence, confirmed), INFO (something worth knowing), SKIP (data not present).
Exit 0 unless any FAIL. Writes study/alignment-report.md.

Usage:
    python tools/check_alignment.py [--root .] [--toriva <path>]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

LAB_BC_CODES = {"Alanine Aminotransferase": "ALT", "Aspartate Aminotransferase": "AST", "Alkaline Phosphatase": "ALP",
                "Bilirubin": "BILI", "Creatinine": "CREAT", "Haemoglobin": "HGB", "Neutrophils": "NEUT",
                "Systolic Blood Pressure": "SYSBP"}


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str, str]] = []   # (verdict, id, layer, detail)

    def add(self, verdict: str, id_: str, layer: str, detail: str) -> None:
        self.rows.append((verdict, id_, layer, detail))

    @property
    def failed(self) -> bool:
        return any(v == "FAIL" for v, *_ in self.rows)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def parse_register(text: str) -> dict[str, str]:
    """{ID: disposition-cell} for every table row whose first cell is an ID."""
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*([DGSX]\d+)\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        # disposition is the cell that carries a bold disposition word
        disp = next((c for c in cells if re.search(r"\*\*(fix here|sponsor decision|upstream only|resolved|not a study gap)", c)), "")
        out[m.group(1)] = disp
    return out


def find_toriva(arg: str | None, root: Path) -> Path | None:
    cands = [arg, os.environ.get("TORIVA_DIR"), str(root.resolve().parent / "torivumab-nsclc-301")]
    for c in cands:
        if c and (Path(c) / "datasets" / "adam" / "adsl.parquet").is_file():
            return Path(c)
    return None


def main() -> int:
    # The report carries arrows and section signs; a cp1252 console must not turn that into an exit 1.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--toriva", default=None)
    args = ap.parse_args()
    root = Path(args.root)
    R = Report()

    prot = root / "study" / "m11" / "protocol"
    sec = {n: read(prot / f) for n, f in {
        "00": "section-00-title-page.md", "01": "section-01-protocol-summary.md", "03": "section-03-objectives-endpoints.md",
        "04": "section-04-trial-design.md", "06": "section-06-trial-intervention.md", "08.4.2": "section-08-04-02-vital-signs.md",
        "10": "section-10-statistical-considerations.md", "12.1": "section-12-01-clinical-laboratory-tests.md"}.items()}
    reg_text = read(root / "study" / "gap-register.md")
    reg = parse_register(reg_text)
    usdm_path = root / "study" / "usdm" / "toriva-lung-301.usdm.json"
    usdm = json.loads(read(usdm_path)) if usdm_path.is_file() else {}
    ver = usdm.get("study", {}).get("versions", [{}])[0]
    sd = (ver.get("studyDesigns") or [{}])[0]
    arms = [a.get("name") for a in sd.get("arms", [])]
    endpoints = [e for o in sd.get("objectives", []) for e in o.get("endpoints", [])]
    bcs = {b.get("name"): b for b in ver.get("biomedicalConcepts", [])}

    # ---------------- DOCUMENTS ----------------
    if not reg:
        R.add("FAIL", "register", "documents", "study/gap-register.md has no parsable rows")
    fix_here = sorted(i for i, d in reg.items() if "fix here" in d)
    implemented = {"D11", "D13", "D14", "D15", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "S1", "S2", "S3"}
    for i in fix_here:
        if i not in implemented:
            R.add("FAIL", i, "documents", "register says 'fix here' and this tool has no check for it")

    # D13 — risk difference stated for ORR's estimand
    blk = sec["03"][sec["03"].find("3.2.2"):sec["03"].find("3.2.3")] if "3.2.2" in sec["03"] else ""
    R.add("PASS" if re.search(r"risk difference", blk, re.I) else "FAIL", "D13", "documents",
          "§3.2.2 Population-level Summary names a risk difference" if re.search(r"risk difference", blk, re.I) else "§3.2.2 does not say 'risk difference'")

    # ---- P6 (2026-09-20): the documents made correct. Six decisions, each a PASS/FAIL on the documents. ----
    p6: dict[str, bool] = {}
    usdm_text = json.dumps(usdm, ensure_ascii=False)

    # D14 — the protocol corrected to the SAP: title, §3.0, section 04; USDM arms follow the corrected protocol,
    # backbone intervention present, and the withdrawn "data is the ground truth" rule gone from the fragment
    want = {"Torivumab + Chemotherapy", "Placebo + Chemotherapy"}
    blk30 = sec["03"][sec["03"].find("## 3.0"):sec["03"].find("## 3.1")]
    ok = set(arms) == want and "plus Platinum-Based Chemotherapy" in sec["00"] and "Corrected under P6" in blk30 \
        and all(n in blk30 for n in want) and "D14" in sec["04"] and "P6" in sec["04"] \
        and any("D14" in n for a in sd.get("arms", []) for n in a.get("notes", [])) \
        and any("backbone" in (i.get("name", "") + i.get("label", "")).lower() for i in ver.get("studyInterventions", [])) \
        and "ground truth" not in usdm_text
    p6["D14"] = ok
    R.add("PASS" if ok else "FAIL", "D14", "documents", f"title, §3.0 and section 04 corrected to the combination; USDM arms {arms} per the corrected protocol; backbone intervention present; no 'ground truth' rule in the fragment" if ok else f"D14 correction incomplete: arms {arms}; title corrected: {'plus Platinum-Based Chemotherapy' in sec['00']}; §3.0 corrected: {'Corrected under P6' in blk30}; ground-truth rule gone: {'ground truth' not in usdm_text}")

    # D15 — 2:1 as the protocol states, in the USDM and noted in sections 01, 04, 10
    ok = any("2:1" in str(n) for n in sd.get("notes", [])) and not any("1:1 (D15)" in str(n) for n in sd.get("notes", [])) \
        and all("D15" in sec[k] for k in ("01", "04", "10"))
    p6["D15"] = ok
    R.add("PASS" if ok else "FAIL", "D15", "documents", "USDM design notes say 2:1, the protocol's ratio; sections 01, 04, 10 carry the D15 note" if ok else "D15: USDM does not say 2:1, or a section lacks the note")

    # D11 / G7 — the laboratory (and vital-signs) analysis specified in §3.2.5, descriptive; section 10 restates it
    blk325 = sec["03"][sec["03"].find("3.2.5"):sec["03"].find("## 3.3")] if "3.2.5" in sec["03"] else ""
    ok = all(re.search(p, blk325, re.I) for p in (r"Filled under P6", r"shift", r"CTCAE", r"descriptive", r"demonstration analyses")) \
        and "specified under P6" in sec["10"]
    p6["D11/G7"] = ok
    for i in ("D11", "G7"):
        R.add("PASS" if ok else "FAIL", i, "documents", "§3.2.5 specifies the descriptive laboratory summary (values by visit, reference-range shift, worst CTCAE grade) and section 10 restates it" if ok else "§3.2.5 or section 10 lacks the P6 laboratory analysis specification")

    # S1–S3 — this project's analyses stated in section 10, now as demonstration analyses
    ok = all(f"**{s}**" in sec["10"] for s in ("S1", "S2", "S3")) and "not part of TORIVA's statistical plan" in sec["10"] \
        and "demonstration analyses" in sec["10"]
    for i in ("S1", "S2", "S3"):
        R.add("PASS" if ok else "FAIL", i, "documents", "section 10 states the analyses added by this project (S1–S3) as demonstration analyses, not the sponsor's" if ok else "section 10 lacks the S1–S3 demonstration statement")

    # G2 — title page: countries and site count from the trial's records, approval date = version date, all marked
    ok = all(c in sec["00"] for c in ("Republic of Korea", "United States of America", "Poland")) and "15 sites" in sec["00"] \
        and "**Sponsor Approval Date** | 22 March 2026" in sec["00"] and "Supplied under P6" in sec["00"]
    p6["G2"] = ok
    R.add("PASS" if ok else "FAIL", "G2", "documents", "title page supplies 13 countries, 15 sites and the approval date, marked as supplied under P6" if ok else "title page G2 content missing or unmarked")

    # G6 — vital-signs procedure supplied in §8.4.2, marked
    ok = "Supplied under P6" in sec["08.4.2"] and re.search(r"five minutes", sec["08.4.2"]) and "60 minutes before" in sec["08.4.2"]
    p6["G6"] = bool(ok)
    R.add("PASS" if ok else "FAIL", "G6", "documents", "§8.4.2 supplies the collection procedure, marked as supplied under P6" if ok else "§8.4.2 G6 procedure missing or unmarked")

    # G5 — central laboratory stated in §12.1, marked
    ok = "Supplied under P6" in sec["12.1"] and re.search(r"central laboratory", sec["12.1"], re.I) and "not used for analysis" in sec["12.1"]
    p6["G5"] = bool(ok)
    R.add("PASS" if ok else "FAIL", "G5", "documents", "§12.1 states a central laboratory with central reference ranges, marked as supplied under P6" if ok else "§12.1 G5 content missing or unmarked")

    # G1 — resolved: six estimands in the USDM, six population-level summaries in §3
    n_est = len(sd.get("estimands", [])); n_pls = len(re.findall(r"Population-level Summary", sec["03"]))
    R.add("PASS" if n_est == 6 and n_pls >= 6 else "FAIL", "G1", "documents", f"USDM estimands {n_est}; §3 population-level summaries {n_pls}")

    # G3 — EU CT correction on the title page
    R.add("PASS" if "EU CT" in sec["00"] else "FAIL", "G3", "documents", "title page carries the EU CT number correction" if "EU CT" in sec["00"] else "no 'EU CT' on the title page")

    # G4 — the seven lab BCs appear in §12.1
    missing = [n for n, c in LAB_BC_CODES.items() if c != "SYSBP" and n in bcs and (c not in sec["12.1"] and n not in sec["12.1"])]
    R.add("PASS" if not missing else "FAIL", "G4", "documents", "all lab BCs named in §12.1" if not missing else f"BCs not in §12.1: {missing}")

    # G8 — coverage of all 14 M11 sections
    cov = json.loads(read(prot / "coverage.json") or "{}")
    tops = {s.get("section", "").split(".")[0] for s in cov.get("sections", [])}
    ok = all(str(n) in tops for n in range(1, 15))
    R.add("PASS" if ok else "FAIL", "G8", "documents", f"coverage.json covers sections {sorted(tops, key=lambda x: int(x) if x.isdigit() else 0)}")

    # USDM ↔ protocol: every endpoint's TEXT appears in §3 or §8.4.2 (the protocol names endpoints by
    # their definition, the USDM by this project's labels, so labels are not what to compare)
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[*`_]", "", s)).strip().lower()
    S3, S8 = norm(sec["03"]), norm(sec["08.4.2"])
    for e in endpoints:
        nm = e.get("name", ""); probe = norm(e.get("text", ""))[:70]
        ok = bool(probe) and (probe in S3 or probe in S8)
        R.add("PASS" if ok else "FAIL", f"USDM↔protocol:{nm}", "documents", "endpoint text present in the M11 protocol" if ok else f"endpoint text not found in §3 / §8.4.2: {probe[:50]!r}")
    ok = any("section-08-04-02-vital-signs.md" in json.dumps(e) for e in endpoints if e.get("name") == "END-S5-VS")
    R.add("PASS" if ok else "FAIL", "USDM↔protocol:END-S5-VS cites §8.4.2", "documents", "yes" if ok else "no")
    ok = "tools/m11_to_usdm.py" in json.dumps(usdm) and sd.get("scheduleTimelines")
    R.add("PASS" if ok else "FAIL", "USDM generated", "documents", "fragment names its generator and carries a schedule" if ok else "fragment is not the generated one")

    # ---------------- DATA ----------------
    tor = find_toriva(args.toriva, root)
    if tor is None:
        R.add("SKIP", "data", "data", "TORIVA ADaM not found (--toriva, TORIVA_DIR, or a sibling torivumab-nsclc-301 checkout)")
    else:
        try:
            import pyarrow.parquet as pq
        except ImportError:
            pq = None
            R.add("SKIP", "data", "data", "pyarrow not installed")
        if pq:
            adam = tor / "datasets" / "adam"
            def cols(n):
                return pq.ParquetFile(adam / f"{n}.parquet").schema.names
            def col(n, c):
                return pq.ParquetFile(adam / f"{n}.parquet").read(columns=[c]).column(c).to_pylist()
            # D14 — the data's arm names against the corrected protocol's; a mismatch is the data's to fix (WARN), P6
            trt = collections.Counter(col("adsl", "TRT01P"))
            ok = set(trt) == set(arms)
            R.add("PASS" if ok else "WARN", "D14", "data", f"ADSL TRT01P values {sorted(trt)} {'==' if ok else '!='} the corrected protocol's arms {sorted(arms)}" + ("" if ok else " — the data diverges from the documents; regenerate upstream"))
            # D15 — the protocol says 2:1; the shipped data is 1:1 — a divergence of the data (WARN), P6
            vals = sorted(trt.values())
            two_to_one = len(vals) == 2 and vals[0] > 0 and abs(vals[1] / vals[0] - 2) < 0.1
            R.add("PASS" if two_to_one else "WARN", "D15", "data", f"ADSL arm counts {dict(trt)} — {'2:1, as the protocol states' if two_to_one else '1:1; the protocol says 2:1 — the data diverges from the documents, to be regenerated upstream'}")
            # BCs ↔ data
            lb = set(col("adlb", "PARAMCD")); vs = set(col("advs", "PARAMCD"))
            lab_codes = {c for n, c in LAB_BC_CODES.items() if n in bcs and c != "SYSBP"}
            miss = lab_codes - lb
            R.add("PASS" if not miss else "FAIL", "BC↔ADLB", "data", f"lab BC codes in ADLB PARAMCD: {sorted(lab_codes & lb)}" + (f"; missing {sorted(miss)}" if miss else ""))
            R.add("PASS" if "SYSBP" in vs else "FAIL", "BC↔ADVS", "data", "SYSBP in ADVS PARAMCD" if "SYSBP" in vs else "SYSBP not in ADVS")
            R.add("INFO", "ADLB parameters without a BC", "data", f"{sorted(lb - lab_codes)} — collected and analysed by TORIVA, not carried by this project's USDM")
            # SoA ↔ data: encounter names vs AVISIT
            enc = {e.get("name") for e in sd.get("encounters", [])}
            av = set(col("advs", "AVISIT")) | set(col("adlb", "AVISIT"))
            av = {a for a in av if a}
            not_in_soa = sorted(av - enc)
            R.add("INFO", "SoA↔AVISIT", "data", f"analysis visits not named as protocol encounters: {not_in_soa[:6]}{'…' if len(not_in_soa) > 6 else ''} — the SAP's windowed labels (Baseline, MAINT_CnD1, UNSCHEDULED) versus the protocol's cycle visits (Cycle 7+ are 'maintenance' in the SAP, 'Day 1 each subsequent cycle' in the protocol)")
            # upstream-only known divergences, confirmed against the data
            adrs = cols("adrs"); adlb_c = cols("adlb"); adtte_u = set(col("adtte", "AVALU"))
            R.add("WARN" if "EFFFL" not in adrs else "PASS", "D7", "data", "EFFFL absent from ADRS, as recorded" if "EFFFL" not in adrs else "EFFFL now present in ADRS — register row D7 is stale")
            R.add("WARN" if ("ANRIND" not in adlb_c and "NRIND" in adlb_c) else "PASS", "D8", "data", "ADLB carries NRIND, not ANRIND/BNRIND, as recorded")
            R.add("WARN" if "BTOXGR" not in adlb_c else "PASS", "D9", "data", "BTOXGR absent from ADLB, as recorded")
            R.add("WARN" if adtte_u == {"DAYS"} else "INFO", "D1", "data", f"ADTTE AVALU = {sorted(adtte_u)}; SAP says months")
            R.add("WARN" if "RSEVAL" not in adrs else "INFO", "D3", "data", "ADRS carries no RSEVAL column — reader cannot be told from the data; the SAP's BICR reader stands as recorded" if "RSEVAL" not in adrs else "RSEVAL present")

    # ---------------- report ----------------
    p6_pass = sum(1 for v in p6.values() if v)
    p6_line = f"P6 decisions: {p6_pass}/{len(p6)} pass — " + ", ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in p6.items())
    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "SKIP": 3, "PASS": 4}
    rows = sorted(R.rows, key=lambda r: (order[r[0]], r[2], r[1]))
    counts = collections.Counter(v for v, *_ in R.rows)
    lines = ["# Alignment report — protocol ↔ USDM ↔ SAP excerpt ↔ built ADaM", "",
             "Written by `tools/check_alignment.py` (phase 2, stage P3), which takes [`gap-register.md`](gap-register.md)",
             "as its checklist. Re-run it to regenerate this file. `PASS` — a fix-here promise kept; `FAIL` — one not",
             "kept; `WARN` — the data diverging from the corrected documents, or an upstream-only divergence, confirmed against the data; `INFO` — worth knowing; `SKIP` —",
             "data not present.", "",
             f"**{counts.get('PASS', 0)} pass, {counts.get('FAIL', 0)} fail, {counts.get('WARN', 0)} warn, {counts.get('INFO', 0)} info, {counts.get('SKIP', 0)} skip.** {p6_line}."
             + (" Data layer: TORIVA ADaM checked." if tor else " Data layer skipped."), "",
             "| Verdict | Item | Layer | Detail |", "|---|---|---|---|"]
    for v, i, l, d in rows:
        lines.append(f"| {v} | {i} | {l} | {d.replace('|', '/')} |")
    (root / "study" / "alignment-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for v, i, l, d in rows:
        print(f"  {v:4s} {l:9s} {i:34s} {d[:110]}")
    print(p6_line)
    print(f"\nalignment: {counts.get('PASS', 0)} pass, {counts.get('FAIL', 0)} fail, {counts.get('WARN', 0)} warn, "
          f"{counts.get('INFO', 0)} info, {counts.get('SKIP', 0)} skip → {'FAIL' if R.failed else 'OK'}")
    return 1 if R.failed else 0


if __name__ == "__main__":
    sys.exit(main())
