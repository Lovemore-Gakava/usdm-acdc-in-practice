#!/usr/bin/env python3
"""
m11_to_usdm.py — generate the TORIVA USDM v4 fragment from the M11-restructured protocol.

Phase 2, stage P2 (NORTH.md). The first phase's fragment was transcribed by hand
from three restructured sections. This generator produces the fragment from the
sections in study/m11/protocol/ — the whole protocol as restructured under P1 —
and adds what the hand-written fragment never had: epochs, encounters,
activities and a schedule of activities, parsed from the two assessment tables
the source protocol carries (§6.1 tumour assessments, §7.2 safety assessments,
both moved verbatim into section-01-protocol-summary.md).

What it keeps from the existing fragment, unchanged: objectives, endpoints,
estimands, analysis populations and biomedical concepts — the §3 content that
stage 0b regenerated from the M11 estimand elements. Those are read from the
current fragment and carried over, so this generator is idempotent on them.

What it corrects, and marks (study/gap-register.md):
  D14  arms and interventions are the combination the SAP and the built data
       describe (torivumab or placebo + carboplatin/pemetrexed), named to match
       TRT01P; the source protocol's "monotherapy" wording is kept in notes.
  D15  the design's randomisation is 1:1, as the shipped data was generated;
       the source's 2:1 is kept in notes.

Everything the source does not say is left out, not invented: no eligibility
criteria objects, no timing durations beyond the cycle length the source states,
no visit windows beyond the ±7 days the source gives for imaging.

Usage:
    python tools/m11_to_usdm.py            # regenerate study/usdm/toriva-lung-301.usdm.json
    python tools/m11_to_usdm.py --check    # verify the file matches; write nothing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

GENERATOR = "tools/m11_to_usdm.py"
SOURCE_COMMIT = "8534339d"
CS = "http://www.cdisc.org"
CSV = "2024-09-27"
N_CYCLES = 35  # "Up to 35 cycles (~2 years)" — source §3.5


def code(id_, c, decode):
    return {"id": id_, "code": c, "codeSystem": CS, "codeSystemVersion": CSV, "decode": decode, "instanceType": "Code"}


# ---------------------------------------------------------------------------
# Parsing the moved tables out of the M11 sections
# ---------------------------------------------------------------------------
def read_section(root: Path, name: str) -> str:
    return (root / "study" / "m11" / "protocol" / name).read_text(encoding="utf-8")


def parse_safety_table(text: str) -> list[dict]:
    """§7.2 Safety Assessment Schedule → rows of {assessment, cells{col: text}}."""
    hdr = "| Assessment | Screening | Cycle 1 Day 1 | Day 1 Each Subsequent Cycle | EOT | 30-day Safety | 90-day Safety |"
    i = text.index(hdr)
    lines = text[i:].split("\n")
    cols = [c.strip() for c in hdr.strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != len(cols):
            break
        rows.append({"assessment": cells[0], "cells": dict(zip(cols[1:], cells[1:]))})
    return rows


def parse_endpoint_texts(sec03: str) -> list[str]:
    """§3: one '| **Endpoint** …' or '| **Secondary Endpoint** …' row per objective block, in
    document order. The trailing citation '*(protocol §6…)*' is the section's own note and is
    dropped; the rest is the protocol's wording as moved under stage 0b."""
    out = []
    for line in sec03.splitlines():
        m = re.match(r"^\|\s*\*\*(?:Secondary |Primary )?Endpoint\*\*\s*`C25212`\s*\|\s*(.*?)\s*\|\s*$", line)
        if m:
            txt = re.sub(r"\s*\*\([^)]*\)\*\s*$", "", m.group(1)).strip()
            out.append(txt)
    return out


def parse_tumour_table(text: str) -> list[tuple[str, str]]:
    """§6.1 Tumour Assessment Schedule → [(timepoint, assessment)]."""
    hdr = "| Timepoint | Assessment |"
    i = text.index(hdr)
    out = []
    for line in text[i:].split("\n")[2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2:
            out.append((cells[0], cells[1]))
    return out


# ---------------------------------------------------------------------------
# Schedule rules. The source's cells are either ✓ or a short rule. Each rule
# the source uses is handled explicitly; anything else is recorded, not guessed.
# ---------------------------------------------------------------------------
def cycles_for_rule(rule: str) -> tuple[set[int], str | None]:
    """Cycle-visit numbers (Day 1 of cycle n, n >= 2) at which a 'Day 1 Each
    Subsequent Cycle' cell applies. Returns (cycles, unparsed_note)."""
    r = rule.strip()
    if r == "✓":
        return set(range(2, N_CYCLES + 1)), None
    if r == "—" or r == "":
        return set(), None
    if r.startswith("Pre/post-infusion"):
        return set(range(2, N_CYCLES + 1)), "pre- and post-infusion on the day"
    m = re.match(r"C3, C5, then Q(\d+) cycles", r)
    if m:
        q = int(m.group(1))
        return {3, 5} | set(range(5 + q, N_CYCLES + 1, q)), None
    if r.startswith("C3, C5, then Q12 weeks"):
        # 12 weeks = 4 cycles of 21 days
        return {3, 5} | set(range(9, N_CYCLES + 1, 4)), None
    if r.startswith("If clinically indicated"):
        return set(), "if clinically indicated — not scheduled"
    if r.startswith("Q6 weeks"):
        # every 2 cycles, from cycle 3 (6 weeks after C1D1); FOCBP only
        return set(range(3, N_CYCLES + 1, 2)), "FOCBP only"
    return set(), f"unparsed rule kept verbatim: {r!r}"


def tumour_cycles() -> set[int]:
    """§6.1: C3D1, C5D1, then Q6W (every 2 cycles) for 12 months, then Q12W (every 4).
    Month 12 ≈ cycle 18 (17 cycles × 21 days = 357 days)."""
    s = {3, 5}
    s |= set(range(7, 19, 2))          # Q6W through month 12
    s |= set(range(21, N_CYCLES + 1, 4))  # Q12W thereafter
    return s


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(root: Path) -> dict:
    base = json.loads((root / "study" / "usdm" / "toriva-lung-301.usdm.json").read_text(encoding="utf-8"))
    v = base["study"]["versions"][0]
    sd = v["studyDesigns"][0]

    sec01 = read_section(root, "section-01-protocol-summary.md")
    safety_rows = parse_safety_table(sec01)
    tumour_rows = parse_tumour_table(sec01)

    # ---- endpoint texts: from the M11 protocol, not from the previous fragment ----
    # §3 carries one endpoint row per objective in the order 3.1.1, 3.2.1 … 3.2.5; the USDM's
    # objectives hold their endpoints in the same order. The vitals endpoint has no §3 row (the
    # safety objective's row is the AE/laboratory one); its text is the measurement list the
    # source gives at the data-domain row moved into §8.4.2, verbatim.
    ep_texts = parse_endpoint_texts(read_section(root, "section-03-objectives-endpoints.md"))
    assert len(ep_texts) == 6, f"expected 6 endpoint rows in section 03, found {len(ep_texts)}"
    sec0842 = read_section(root, "section-08-04-02-vital-signs.md")
    vs_text = "BP, HR, temperature, weight, height"
    assert vs_text in sec0842
    ordered = [e for o in sd["objectives"] for e in o.get("endpoints", [])]
    non_vs = [e for e in ordered if e["id"] != "Endpoint_SAFETY_VS"]
    assert len(non_vs) == 6, [e["id"] for e in non_vs]
    for e, txt in zip(non_vs, ep_texts):
        e["text"] = txt
        e["notes"] = [n for n in e.get("notes", []) if "lifted verbatim" not in n] + [
            "text lifted verbatim from study/m11/protocol/section-03-objectives-endpoints.md by tools/m11_to_usdm.py"]
    for e in ordered:
        if e["id"] == "Endpoint_SAFETY_VS":
            e["text"] = vs_text   # verbatim: the source's own list of what "Vital Signs" collects
            e["description"] = ("The source protocol names the vital-signs measurements only as a data-domain row — "
                                "'BP, HR, temperature, weight, height' — and schedules them in §7.2; both are moved into "
                                "section-08-04-02-vital-signs.md, from which this text is lifted verbatim. Collected per the §7.2 "
                                "schedule; analysed as change from baseline by this project (gap register S2), not by the sponsor. "
                                "No estimand targets this endpoint.")
            e["notes"] = [n for n in e.get("notes", []) if "lifted verbatim" not in n] + [
                "measurement list lifted verbatim from study/m11/protocol/section-08-04-02-vital-signs.md by tools/m11_to_usdm.py"]

    # ---- arms and interventions: D14 / D15 corrected, source wording kept ----
    note14 = ("D14: the source protocol describes torivumab monotherapy versus placebo (title, §1.4, §3.5, §5.1). "
              "SAP §13.2 and the built data (TRT01P) describe both arms on a carboplatin/pemetrexed backbone; "
              "the data is the ground truth, so the arm is named as the data names it. See study/gap-register.md.")
    note15 = ("D15: the source protocol states 2:1 randomisation (300:150). Its own header records the shipped "
              "data as generated 1:1 (225:225). The design here is 1:1. See study/gap-register.md.")
    sd["arms"] = [
        {"id": "StudyArm_1", "name": "Torivumab + Chemotherapy", "label": "Torivumab 200 mg IV Q3W + carboplatin/pemetrexed",
         "description": "Arm A (Active). Source §3.5: torivumab 200 mg IV infusion over 30 min, Q3W (Day 1 of each 21-day cycle), up to 35 cycles.",
         "type": code("Code_ArmA", "C174266", "Investigational Arm"),
         "dataOriginDescription": "Data collected from subjects", "dataOriginType": code("Code_DO1", "C188866", "Data Generated Within Study"),
         "populationIds": [], "notes": [note14, note15], "instanceType": "StudyArm"},
        {"id": "StudyArm_2", "name": "Placebo + Chemotherapy", "label": "Placebo IV Q3W + carboplatin/pemetrexed",
         "description": "Arm B (Control). Source §3.5: matching placebo IV infusion over 30 min, Q3W (Day 1 of each 21-day cycle), up to 35 cycles.",
         "type": code("Code_ArmB", "C174268", "Placebo Control Arm"),
         "dataOriginDescription": "Data collected from subjects", "dataOriginType": code("Code_DO2", "C188866", "Data Generated Within Study"),
         "populationIds": [], "notes": [note14, note15], "instanceType": "StudyArm"},
    ]
    v["studyInterventions"] = [
        {"id": "StudyIntervention_1", "name": "Torivumab", "label": "Torivumab 200 mg/10 mL concentrate for solution for infusion",
         "description": "Source §5.1: anti-PD-L1 humanised IgG1 mAb, 200 mg/10 mL (20 mg/mL) concentrate for IV infusion; §5.2: 200 mg IV over 30 minutes on Day 1 of each 21-day cycle.",
         "role": code("Code_IR1", "C41161", "Experimental Intervention"), "type": code("Code_IT1", "C1909", "Pharmacologic Substance"),
         "notes": [], "instanceType": "StudyIntervention"},
        {"id": "StudyIntervention_2", "name": "Placebo", "label": "Matching placebo",
         "description": "Source §5.1: matching placebo, matching volume, identical appearance; §5.2: IV over 30 minutes on Day 1 of each 21-day cycle.",
         "role": code("Code_IR2", "C41180", "Placebo Comparator"), "type": code("Code_IT2", "C1909", "Pharmacologic Substance"),
         "notes": [], "instanceType": "StudyIntervention"},
        {"id": "StudyIntervention_3", "name": "Chemotherapy backbone", "label": "Carboplatin / pemetrexed",
         "description": "Not in the source protocol. SAP §13.2 and the built data (TRT01P) place both arms on a carboplatin/pemetrexed backbone. Recorded from the SAP with that citation, because the data is the ground truth (D14).",
         "role": code("Code_IR3", "C41182", "Background Intervention"), "type": code("Code_IT3", "C1909", "Pharmacologic Substance"),
         "notes": [note14], "instanceType": "StudyIntervention"},
    ]
    sd["studyInterventionIds"] = [i["id"] for i in v["studyInterventions"]]

    # ---- epochs ----
    sd["epochs"] = [
        {"id": "StudyEpoch_1", "name": "Screening", "label": "Screening", "description": "Source §3.2: up to 28 days.", "type": code("Code_E1", "C202487", "Screening Epoch"), "previousId": None, "nextId": "StudyEpoch_2", "notes": [], "instanceType": "StudyEpoch"},
        {"id": "StudyEpoch_2", "name": "Treatment", "label": "Treatment Period", "description": "Source §3.2: up to 35 cycles / ~2 years.", "type": code("Code_E2", "C101526", "Treatment Epoch"), "previousId": "StudyEpoch_1", "nextId": "StudyEpoch_3", "notes": [], "instanceType": "StudyEpoch"},
        {"id": "StudyEpoch_3", "name": "Follow-up", "label": "Post-Treatment Follow-Up", "description": "Source §3.6: tumour assessments until progression; survival follow-up every 12 weeks.", "type": code("Code_E3", "C99158", "Follow-Up Epoch"), "previousId": "StudyEpoch_2", "nextId": None, "notes": [], "instanceType": "StudyEpoch"},
    ]

    # ---- encounters ----
    enc = []
    def add_enc(id_, name, label, epoch, desc):
        enc.append({"id": id_, "name": name, "label": label, "description": desc, "type": code(f"Code_{id_}", "C25716", "Visit"),
                    "previousId": None, "nextId": None, "scheduledAtId": None, "epochId": epoch, "notes": [], "instanceType": "Encounter"})
    add_enc("Encounter_SCR", "SCREENING", "Screening", "StudyEpoch_1", "Source §3.2: within 28 days before Cycle 1 Day 1.")
    for n in range(1, N_CYCLES + 1):
        add_enc(f"Encounter_C{n}D1", f"C{n}D1", f"Cycle {n} Day 1", "StudyEpoch_2", "Source §3.5: Day 1 of each 21-day cycle.")
    add_enc("Encounter_EOT", "EOT", "End of Treatment", "StudyEpoch_3", "Source §7.2 column EOT.")
    add_enc("Encounter_FU30", "FU30", "30-day Safety Follow-up", "StudyEpoch_3", "Source §7.2 column 30-day Safety.")
    add_enc("Encounter_FU90", "FU90", "90-day Safety Follow-up", "StudyEpoch_3", "Source §7.2 column 90-day Safety.")
    for i, e in enumerate(enc):
        e["previousId"] = enc[i - 1]["id"] if i else None
        e["nextId"] = enc[i + 1]["id"] if i + 1 < len(enc) else None
    sd["encounters"] = enc

    # ---- activities: one per safety row, plus tumour imaging; BCs attached ----
    bc_by_name = {b["name"]: b["id"] for b in v.get("biomedicalConcepts", [])}
    bc_links = {
        "Haematology": [bc_by_name.get("Haemoglobin"), bc_by_name.get("Neutrophils")],
        "Chemistry (LFTs, creatinine)": [bc_by_name.get(n) for n in ("Alanine Aminotransferase", "Aspartate Aminotransferase", "Alkaline Phosphatase", "Bilirubin", "Creatinine")],
        "Vital signs": [bc_by_name.get("Systolic Blood Pressure")],
    }
    acts = []
    schedule: dict[str, list[str]] = {e["id"]: [] for e in enc}   # encounterId -> activityIds
    notes_unparsed = []
    for k, row in enumerate(safety_rows, 1):
        aid = f"Activity_{k}"
        links = [x for x in bc_links.get(row["assessment"], []) if x]
        acts.append({"id": aid, "name": row["assessment"], "label": row["assessment"],
                     "description": f"Source §7.2 Safety Assessment Schedule, row '{row['assessment']}'.",
                     "previousId": None, "nextId": None, "childIds": [], "definedProcedures": [],
                     "biomedicalConceptIds": links, "bcCategoryIds": [], "bcSurrogateIds": [], "timelineId": None,
                     "notes": [], "instanceType": "Activity"})
        c = row["cells"]
        if c["Screening"] == "✓" or c["Screening"].startswith("✓"):
            schedule["Encounter_SCR"].append(aid)
        if c["Cycle 1 Day 1"] != "—" and c["Cycle 1 Day 1"] != "":
            schedule["Encounter_C1D1"].append(aid)
        cyc, note = cycles_for_rule(c["Day 1 Each Subsequent Cycle"])
        for n in sorted(cyc):
            schedule[f"Encounter_C{n}D1"].append(aid)
        if note:
            acts[-1]["notes"].append(f"§7.2 rule for subsequent cycles: {c['Day 1 Each Subsequent Cycle']!r} — {note}")
            if note.startswith("unparsed"):
                notes_unparsed.append((row["assessment"], c["Day 1 Each Subsequent Cycle"]))
        for col, eid in (("EOT", "Encounter_EOT"), ("30-day Safety", "Encounter_FU30"), ("90-day Safety", "Encounter_FU90")):
            if c[col] == "✓":
                schedule[eid].append(aid)
    # tumour imaging
    aid = f"Activity_{len(acts) + 1}"
    acts.append({"id": aid, "name": "Tumour imaging (RECIST 1.1)", "label": "Tumour assessment",
                 "description": "Source §6.1: CT with contrast (or MRI) of chest, abdomen and pelvis; screening within 28 days before C1D1; C3D1 (week 6), C5D1 (week 12), Q6W for 12 months, Q12W thereafter, EOT; ±7 days. BICR per RECIST 1.1 (§6.2).",
                 "previousId": None, "nextId": None, "childIds": [], "definedProcedures": [], "biomedicalConceptIds": [],
                 "bcCategoryIds": [], "bcSurrogateIds": [], "timelineId": None,
                 "notes": ["Timepoints as the source's table gives them: " + "; ".join(f"{t} — {a}" for t, a in tumour_rows)],
                 "instanceType": "Activity"})
    schedule["Encounter_SCR"].append(aid)
    for n in sorted(tumour_cycles()):
        schedule[f"Encounter_C{n}D1"].append(aid)
    schedule["Encounter_EOT"].append(aid)
    for i, a in enumerate(acts):
        a["previousId"] = acts[i - 1]["id"] if i else None
        a["nextId"] = acts[i + 1]["id"] if i + 1 < len(acts) else None
    sd["activities"] = acts

    # ---- the timeline ----
    instances = []
    for k, e in enumerate(enc, 1):
        instances.append({"id": f"ScheduledActivityInstance_{k}", "name": e["name"], "label": e["label"], "description": "-",
                          "defaultConditionId": None, "epochId": e["epochId"], "instanceType": "ScheduledActivityInstance",
                          "timelineId": None, "timelineExitId": None, "activityIds": schedule[e["id"]], "encounterId": e["id"]})
    for k, inst in enumerate(instances):
        inst["defaultConditionId"] = instances[k + 1]["id"] if k + 1 < len(instances) else None
    sd["scheduleTimelines"] = [{
        "id": "ScheduleTimeline_1", "name": "Main Timeline", "label": "Main Timeline",
        "description": "Generated from the source's §6.1 and §7.2 assessment tables as moved into section-01-protocol-summary.md. Cycle length 21 days (§3.5). No timing objects: the source gives ±7 days for imaging only, and that is recorded on the activity, not invented as windows.",
        "mainTimeline": True, "entryCondition": "Informed consent (source §4.1 criterion 12)", "entryId": instances[0]["id"],
        "exits": [], "timings": [], "instances": instances, "plannedDuration": None, "instanceType": "ScheduleTimeline"}]

    # ---- provenance of the generation ----
    v["rationale"] = (
        f"USDM v4 fragment GENERATED by {GENERATOR} on the ICH M11-restructured protocol in study/m11/protocol/ "
        f"(source TORIVA-LUNG 301 synopsis at {SOURCE_COMMIT}, restructured by tools/m11_restructure.py). "
        "Objectives, endpoints, estimands, analysis populations and biomedical concepts are carried over from the stage 0b "
        "regeneration (section-03, section-12-01, section-08-04-02). Arms, interventions, epochs, encounters, activities and the "
        "schedule of activities are generated from sections 01, 04 and 06, with D14 and D15 corrected and marked. "
        "Not in the source, therefore not here: eligibility criteria objects, visit-window timings, planned enrollment beyond the arm split.")
    sd["notes"] = [n for n in sd.get("notes", []) if GENERATOR not in str(n)] + [
        f"Generated by {GENERATOR}. Randomisation 1:1 (D15). Arms named as the built data names them (D14)."]
    if notes_unparsed:
        sd["notes"].append("Schedule rules kept verbatim, not scheduled: " + "; ".join(f"{a}: {r!r}" for a, r in notes_unparsed))
    return base


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = Path(args.root)
    out = root / "study" / "usdm" / "toriva-lung-301.usdm.json"
    text = json.dumps(build(root), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        ok = out.is_file() and out.read_text(encoding="utf-8") == text
        print("check:", "OK" if ok else "DIFFERS")
        return 0 if ok else 1
    out.write_text(text, encoding="utf-8")
    d = json.loads(text); sd = d["study"]["versions"][0]["studyDesigns"][0]
    tl = sd["scheduleTimelines"][0]
    print(f"wrote {out}: arms {len(sd['arms'])}, interventions {len(d['study']['versions'][0]['studyInterventions'])}, "
          f"epochs {len(sd['epochs'])}, encounters {len(sd['encounters'])}, activities {len(sd['activities'])}, "
          f"timeline instances {len(tl['instances'])}, scheduled activity-visits {sum(len(i['activityIds']) for i in tl['instances'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
