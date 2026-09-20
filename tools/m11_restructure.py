#!/usr/bin/env python3
"""
m11_restructure.py — move TORIVA's protocol synopsis into ICH M11 sections.

Phase 2, stage P1 (NORTH.md). The rule is the one the first three sections were
built under: MOVE, DO NOT WRITE. Every block of text in a generated section is
a verbatim line range of the source synopsis, and every M11 element the source
does not supply is recorded as absent rather than filled. The only prose this
script adds is the per-section header, the source citation on each block, and
the conformance notes at the foot of each section — all of which are ours and
say so.

Subsection numbers corrected 2026-09-20 (review-sheet item 2d): the labels had
been numbered from memory and eight were wrong against the M11 element pages
(e.g. Sample Size was 10.9, M11 says 10.11; Interim was 10.8, M11 10.9; Data
Protection was 11.4, M11 11.8; Concomitant Therapy was 6.8, M11 6.10). Blocks
that M11 places in a *different section* (randomisation and blinding 6.7,
dose modification 6.4, stopping rules 4.3, safety committee 11.4) are left
where they are and flagged in the notes, pending LG's 2b verdict.

Source: OpenTrialReporting/torivumab-nsclc-301, protocol/synopsis.md, commit
8534339d (study/source-refs.md). Referenced, never vendored: point --synopsis at
a local checkout. The generated sections are a CC BY 4.0 derived work and carry
the source's FICTIONAL banner, as the hand-made sections do.

Hand-made sections (stage 0b and endpoint 2) are NOT regenerated:
  section-00-title-page.md, section-03-objectives-endpoints.md,
  section-08-04-02-vital-signs.md, section-12-01-clinical-laboratory-tests.md
They are listed in coverage.json beside the generated ones.

Usage:
    python tools/m11_restructure.py --synopsis <path to synopsis.md>
    python tools/m11_restructure.py --synopsis <path> --check   # verify, no write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SOURCE_COMMIT = "8534339d"
BANNER = """# ⚠️ FICTIONAL EDUCATIONAL PROTOCOL — NOT FOR REGULATORY USE

**Derived excerpt of a fictional protocol, restructured for educational purposes only.**
Derived from **TORIVA-LUNG 301** (`OpenTrialReporting/torivumab-nsclc-301` at `8534339d`,
CC BY 4.0). See [`README.md`](README.md).

---
"""

# ---------------------------------------------------------------------------
# The map. Each M11 section: its file, the M11 title, the source blocks that
# move into it (1-based inclusive line ranges of synopsis.md at 8534339d, with
# the source heading they came from), and the conformance notes we add.
# ---------------------------------------------------------------------------
SECTIONS: list[dict] = [
    {
        "num": "1", "file": "section-01-protocol-summary.md",
        "title": "1 Protocol Summary",
        "elements": "1.1.1 Primary and Secondary Objectives and Estimands; 1.1.2 Overall Design; 1.2 Trial Schema; 1.3 Schedule of Activities",
        "blocks": [
            ("1.1.2 Overall Design ← SYNOPSIS TABLE", 113, 141),
            ("1.1.1 Primary and Secondary Objectives and Estimands ← §2.1–2.3 STUDY OBJECTIVES", 185, 205),
            ("1.2 Trial Schema ← §3.2 Design Schematic", 215, 268),
            ("1.3 Schedule of Activities — efficacy ← §6.1 Tumour Assessment Schedule", 444, 458),
            ("1.3 Schedule of Activities — safety ← §7.2 Safety Assessment Schedule", 498, 515),
        ],
        "notes": [
            "**Estimands** in 1.1: the synopsis table names endpoints, not estimands; the estimands are in §3 of this derived protocol, moved there from SAP §13 under stage 0b. 1.1 here carries the source's summary table and objectives as written.",
            "**Schedule of Activities** (1.3): M11 wants one table; the source has two — tumour assessments (§6.1) and safety assessments (§7.2) — and says of the latter *\"Full Schedule of Assessments (SoA) to be presented as a formal table in the final protocol body.\"* Both are moved; they are not merged, because merging would be writing. P2's USDM generator builds `scheduleTimelines` from both.",
            "**As-simulated deviation (D15).** The source's own header records that the synopsis states 2:1 randomisation (300:150) while the shipped data was generated 1:1 (225:225). The table above says 2:1, and **2:1 stands** (P6, 2026-09-20): the protocol is the specification, and §8.1's arithmetic was derived for it. The data's 1:1 is a divergence the alignment check reports, to be regenerated upstream.",
        ],
    },
    {
        "num": "2", "file": "section-02-introduction.md",
        "title": "2 Introduction",
        "elements": "2.1 Purpose of Trial; 2.2 Summary of Benefits and Risks (2.2.1 Risk Summary and Mitigation Strategy, 2.2.2 Benefit Summary, 2.2.3 Overall Risk-Benefit Assessment)",
        "blocks": [
            ("2.1 Purpose of Trial ← §1 BACKGROUND AND RATIONALE", 145, 182),
            ("2.2.3 Overall Risk-Benefit Assessment ← §9.5 Risk-Benefit Assessment", 779, 784),
        ],
        "notes": [
            "**Risk Summary and Mitigation Strategy** (2.2): the source carries the mitigation content under irAE management (§7.3, moved to section 9 here) rather than as a summary in the introduction. Not duplicated; recorded as located elsewhere.",
            "**D14** surfaces here: §1.4 says *\"first-line monotherapy\"*. **Corrected under P6 (2026-09-20)**: the trial is torivumab or placebo *plus* platinum-based chemotherapy (carboplatin/pemetrexed), as SAP §13.2 states and as the double-blind, matched-infusion design requires — a placebo-alone first-line control does not exist. The text is moved as written; the correction is stated in section 4 and the title page, and the USDM follows the corrected protocol.",
        ],
    },
    {
        "num": "4", "file": "section-04-trial-design.md",
        "title": "4 Trial Design",
        "elements": "4.1 Description of Trial Design; 4.2 Rationale for Trial Design; 4.3 Trial Stopping Rules; 4.4 Start of Trial and End of Trial; 4.5 Access to Trial Intervention After End of Trial",
        "blocks": [
            ("4.1 Description of Trial Design ← §3.1 Overview", 209, 213),
            ("4.1 Treatment Arms ← §3.5", 284, 291),
            ("4.3 Trial Stopping Rules ← §7.4, the myocarditis stopping rule", 599, 599),
            ("4.4 Start of Trial and End of Trial ← §3.6 Post-Treatment Follow-Up", 293, 297),
        ],
        "notes": [
            "**D14 — treatment arms, the protocol corrected to the SAP (P6, 2026-09-20).** The source's arms are torivumab 200 mg IV Q3W versus placebo, monotherapy. TORIVA's SAP §13.2 describes both arms on a carboplatin/pemetrexed backbone, and a placebo-alone control does not exist in first-line NSCLC: the protocol is the document in error. The moved text above is the source's; the arms this derived protocol *means* — *Torivumab + Chemotherapy* and *Placebo + Chemotherapy*, carried by the USDM's `arms` — are the combination. That the built data agrees is incidental. Disposition in `study/gap-register.md`: fix here. (Before P6 this note said the data was the ground truth; withdrawn by LG.)",
            "**D15 — randomisation ratio.** The source states 2:1 throughout (§3.1, §3.2, §8.1). Its own header records the shipped data as 1:1 (225:225). **2:1 stands** (P6): the USDM says 2:1 and the alignment check reports the data's 1:1 as a divergence.",
            "**4.2 Rationale for Trial Design**: the source gives a rationale for the dose (§1.4, PK/PD) and for the endpoints (§6.1 note on assessment frequency), not a rationale for the control type or for the design as a whole. Absent; not invented.",
            "**Moved 2026-09-20 (review-sheet item 2b, LG's verdict):** randomisation (§3.3) and blinding (§3.4) now sit at **6.7**, where M11 numbers them, not here; the myocarditis stopping rule (§7.4) comes here to **4.3**, from section 7. The one line at 4.3 is also part of the AESI text at 9.2.4 — the single duplicated line in this restructure, because the source states the rule inside the AESI paragraph.",
            "**4.3 Trial Stopping Rules**: the source has one — an enhanced monitoring and stopping rule for myocarditis, pre-specified in the SMC charter (§7.4). The SMC's own *\"stopping rules (safety)\"* are a charter item, not stated in the protocol.",
            "**4.5 Access to Trial Intervention After End of Trial**: absent from the source.",
            "**4.4 Start and End of Trial Definition**: the source gives the follow-up rule (§3.6) and the timeline (schematic: 18 months accrual, 24 months minimum follow-up), not a definition of trial start and end. Recorded as partial.",
        ],
    },
    {
        "num": "5", "file": "section-05-trial-population.md",
        "title": "5 Trial Population",
        "elements": "5.1 Description of Trial Population and Rationale; 5.2 Inclusion Criteria; 5.3 Exclusion Criteria; 5.4 Childbearing Potential and Contraception (5.4.1, 5.4.2); 5.5 Lifestyle Restrictions (5.5.1–5.5.4); 5.6 Screen Failure and Rescreening",
        "blocks": [
            ("5.2 Inclusion Criteria ← §4.1", 303, 335),
            ("5.3 Exclusion Criteria ← §4.2", 337, 369),
        ],
        "notes": [
            "**5.1 Description of Trial Population and Rationale** (Required, `C218739`): the source describes the population inside the objectives and the background (§1.2, §2.1) and not as a section of its own. Recorded as absent as an element; the content exists in section 2.",
            "**5.4 Contraception Requirements**: supplied inside inclusion criterion 11 rather than as a section; not duplicated.",
            "**5.5 Lifestyle Considerations** and **5.6 Screen Failures**: absent from the source.",
        ],
    },
    {
        "num": "6", "file": "section-06-trial-intervention.md",
        "title": "6 Trial Intervention And Concomitant Therapy",
        "elements": "6.1 Description of Investigational Trial Intervention; 6.2 Rationale for Investigational Trial Intervention Dose and Regimen; 6.3 Investigational Trial Intervention Administration; 6.4 Investigational Trial Intervention Dose Modification; 6.5 Management of Overdose; 6.6 Preparation, Storage and Handling, Accountability (6.6.1–6.6.3); 6.7 Participant Assignment, Randomisation, Blinding, Emergency Unblinding (6.7.1–6.7.4); 6.8 Adherence; 6.9 Noninvestigational Trial Intervention (6.9.1 Background, 6.9.2 Rescue, 6.9.3 Other); 6.10 Concomitant Therapy (6.10.1 Prohibited, 6.10.2 Permitted)",
        "blocks": [
            ("6.1 Description of Investigational Trial Intervention ← §5.1", 375, 382),
            ("6.3 Investigational Trial Intervention Administration ← §5.2", 384, 391),
            ("6.4 Investigational Trial Intervention Dose Modification ← §5.3 Dose Modifications, §5.3.1 Treatment Delays", 393, 405),
            ("6.7.2 Randomisation ← §3.3", 270, 274),
            ("6.7.3 Measures to Maintain Blinding ← §3.4", 276, 282),
            ("6.10 Concomitant Therapy ← §5.4", 422, 438),
        ],
        "notes": [
            "**D14** again: the intervention table lists torivumab and placebo only. Corrected under P6: both arms also receive platinum-based chemotherapy (carboplatin AUC5 + pemetrexed 500 mg/m² IV Q3W, up to 6 induction cycles, then pemetrexed maintenance — SAP §13.2). Moved as written; the USDM's `studyInterventions` carry the backbone as a background intervention, per the corrected protocol.",
            "**6.2 Rationale for Dose and Regimen**: in the source at §1.4 (PK/PD, receptor occupancy), moved to section 2 here; not duplicated.",
            "**Moved here 2026-09-20 (review-sheet item 2b, LG's verdict):** dose modifications and treatment delays (§5.3, §5.3.1) from section 7 to **6.4**; randomisation (§3.3) and blinding (§3.4) from section 4 to **6.7.2** and **6.7.3**. M11 numbers them here; the earlier placement followed the source's reading order.",
            "**6.5 Management of Overdose**: absent from the source.",
            "**6.6 Preparation, Storage and Handling, Accountability**: storage and dilution are in §5.1 (moved); accountability is absent.",
            "**6.7.1 Participant Assignment** is inside the randomisation text; **6.7.4 Emergency Unblinding at the Site**: absent from the source.",
            "**6.8 Adherence**: absent from the source.",
            "**6.9 Noninvestigational Trial Intervention**: the platinum-based chemotherapy both arms receive (D14, corrected under P6) is a **6.9.1 Background Trial Intervention**; the source protocol never described it, and the SAP §13.2 wording is carried in the D14 note above rather than invented as a section.",
        ],
    },
    {
        "num": "7", "file": "section-07-discontinuation.md",
        "title": "7 Discontinuation of Trial Intervention and Participant Withdrawal from Trial",
        "elements": "7.1 Discontinuation of Trial Intervention; 7.2 Participant Discontinuation or Withdrawal from the Trial; 7.3 Management of Loss to Follow-Up. (Trial Stopping Rules are M11 §4.3, not §7.)",
        "blocks": [
            ("7.1 Discontinuation of Trial Intervention — Permanent Discontinuation ← §5.3.2", 407, 420),
            ("7.2 Participant Discontinuation or Withdrawal from the Trial ← §3.6", 293, 297),
        ],
        "notes": [
            "**Moved out 2026-09-20 (review-sheet item 2b, LG's verdict):** temporary discontinuation and rechallenge (§5.3, §5.3.1) are dose-modification rules and now sit at **6.4**; the myocarditis stopping rule (§7.4) at **4.3**; the Safety Monitoring Committee (§7.5) at **11.4**. M11 has no 7.4.",
            "**7.1**: the source's temporary-discontinuation rules are its dose-modification table, now at 6.4; what remains here is permanent discontinuation (§5.3.2), which is what M11 7.1 asks for.",
            "**7.3 Management of Loss to Follow-Up**: absent from the source.",
            "**7.2**: the source gives what happens to assessments after discontinuation (§3.6) and no procedure for withdrawal of consent beyond naming it as a reason. Partial.",
        ],
    },
    {
        "num": "8", "file": "section-08-assessments-and-procedures.md",
        "title": "8 Trial Assessments and Procedures",
        "elements": "8.1 Trial Assessments and Procedures Considerations; 8.2 Screening/Baseline Assessments and Procedures; 8.3 Efficacy Assessments and Procedures; 8.4 Safety Assessments and Procedures (8.4.1 Physical Examination, 8.4.2 Vital Signs, 8.4.3 Electrocardiograms, 8.4.4 Clinical Laboratory Assessments, 8.4.5 Pregnancy Testing, 8.4.6 Suicidal Ideation and Behaviour Risk Monitoring); 8.5 Pharmacokinetics; 8.6 Genetics, Pharmacodynamic and Other Biomarkers (8.6.1–8.6.3); 8.7 Immunogenicity Assessments; 8.8 Medical Resource Utilisation and Health Economics",
        "blocks": [
            ("8.3 Efficacy Assessments and Procedures ← §6.1 Tumour Assessment Schedule", 444, 458),
            ("8.3 Response Evaluation — RECIST 1.1 ← §6.2", 460, 483),
            ("8.4 Safety Assessments and Procedures ← §7.2", 498, 515),
        ],
        "notes": [
            "**8.4.2 Vital Signs**: [`section-08-04-02-vital-signs.md`](section-08-04-02-vital-signs.md), hand-made for endpoint 2 — supplied in part.",
            "**8.4.4 Clinical Laboratory Assessments**: the schedule rows (haematology, chemistry, thyroid, cortisol, urinalysis) are in the moved §7.2 table; the analyte list is [`section-12-01-clinical-laboratory-tests.md`](section-12-01-clinical-laboratory-tests.md), backwards-sourced and marked (gap G4).",
            "**8.4.1, 8.4.3, 8.4.5**: physical examination, ECG and pregnancy testing appear as rows of the §7.2 table and nowhere else — timing only, no procedures.",
            "**8.4.6 Suicidal Ideation and Behaviour**: absent (and not applicable to the population; M11 marks it conditional).",
            "**8.5 PK, 8.6 Biomarkers, 8.7 Immunogenicity**: named as exploratory objectives (§2.3) and deferred by the source to separate plans; absent here.",
            "**8.1, 8.2, 8.8, 8.9**: absent from the source.",
        ],
    },
    {
        "num": "9", "file": "section-09-adverse-events.md",
        "title": "9 Adverse Events, Serious Adverse Events, Product Complaints, Pregnancy and Special Safety Situations",
        "elements": "9.1 Definitions (9.1.1 Adverse Events, 9.1.2 Serious Adverse Events, 9.1.3 Product Complaints); 9.2 Timing and Procedures for Collection and Reporting (9.2.1 Timing, 9.2.2 Collection Procedures, 9.2.3 Reporting, 9.2.4 Adverse Events of Special Interest, 9.2.5 Disease-Related Events); 9.3 Pregnancy (9.3.1, 9.3.2); 9.4 Special Safety Situations. (A safety monitoring committee is M11 §11.4 Committees.)",
        "blocks": [
            ("9.1 Definitions and 9.2 Timing and Procedures for Collection and Reporting ← §7.1 Adverse Event Monitoring", 489, 496),
            ("9.2.4 Adverse Events of Special Interest ← §7.4", 585, 599),
            ("9.4 Special Safety Situations — irAE management ← §7.3", 517, 583),
        ],
        "notes": [
            "**Moved out 2026-09-20 (review-sheet item 2b, LG's verdict):** the Safety Monitoring Committee (§7.5) now sits at **11.4 Committees**. M11 has no 9.6 or 9.7.",
            "**irAE management (§7.3)** is placed at 9.4 Special Safety Situations because M11 has no subsection for a toxicity-management algorithm; the nearest alternatives are 6.4 Dose Modification (it is partly that) and an appendix. Recorded, not resolved.",
            "**9.1.3 Product Complaints** definitions: absent (no device; M11 marks them conditional).",
            "**9.3 Follow-Up of AEs** and **9.4 Regulatory Reporting Requirements**: the source gives the AESI 24-hour reporting rule (§7.4) and nothing else on follow-up or expedited reporting. Partial.",
            "**9.5 Pregnancy**: a serum pregnancy test row in the schedule and a contraception criterion; no pregnancy-reporting procedure. Absent as an element.",
        ],
    },
    {
        "num": "10", "file": "section-10-statistical-considerations.md",
        "title": "10 Statistical Considerations",
        "elements": "10.1 General Considerations; 10.2 Analysis Sets; 10.3 Analyses of Demographics and Other Baseline Variables; 10.4 Analyses Associated with the Primary Objective(s); 10.5 Analyses Associated with the Secondary Objective(s); 10.6 Analyses Associated with the Exploratory Objective(s); 10.7 Safety Analyses; 10.8 Other Analyses; 10.9 Interim Analyses; 10.10 Multiplicity Adjustments; 10.11 Sample Size Determination",
        "blocks": [
            ("10.11 Sample Size Determination ← §8.1", 612, 685),
            ("10.2 Analysis Sets ← §8.2 Analysis Populations", 687, 694),
            ("10.4 Analyses Associated with the Primary Objective — Overall Survival ← §8.3", 696, 702),
            ("10.5 Analyses Associated with the Secondary Objectives ← §8.4", 704, 709),
            ("10.10 Multiplicity Adjustments ← §8.5", 711, 720),
            ("10.9 Interim Analyses ← §8.6", 722, 739),
            ("10.1 General Considerations ← §11 KEY INFORMATION FOR STATISTICAL ANALYSIS PLAN", 823, 844),
        ],
        "notes": [
            "**D15** lands hardest here: the sample-size arithmetic (§8.1) is for 2:1 and *\"was not re-derived for 1:1\"* (source header). Moved as written; 2:1 stands (P6). **D14 leaves a rationale gap here**: §8.1 benchmarks against monotherapy trials (KEYNOTE-024); with the design corrected to combination, the benchmark no longer matches the design. Noted, not re-derived — a sponsor's task.",
            "**D13**: §8.4 gives ORR a CMH test and Clopper–Pearson CI — no population-level summary is named here; SAP §5.3/§13.6 names a stratified MH risk difference and reaches for an odds-ratio estimator. The estimand in section 3.2.2 says risk difference. P3 checks that.",
            "**10.6 Exploratory** and **10.7 Safety**: one line each in §8.4 and the SAP-information table (§11); no methods beyond *\"descriptive\"*. Partial. **No laboratory or vital-signs analysis is specified anywhere** (D11, S1–S3): the analyses this project executed are its own and say so.",
            "**10.8 Other Analyses** (subgroups, sensitivity): listed as SAP requirements in §11 (moved into 10.1); not specified in the protocol body.",
            "**Analyses added by this project, not by the sponsor** (gap register S1–S3) — **demonstration analyses**, under P6. The two endpoints this project carried through the AC/DC framework use analyses the source never specified, and they are recorded here so the eSAP's analyses have a stated origin: **S1** laboratory change from baseline (ALT) by ANCOVA at C2D1, safety population, baseline as covariate; **S2** systolic blood pressure change from baseline by MMRM over the induction visits C1D15–C6D1 (unstructured covariance, REML, Kenward–Roger) and by ANCOVA at C2D1; **S3** the induction-visit window for that MMRM. These are this project's choices for exercising the framework, marked as such, and are not part of TORIVA's statistical plan.",
            "**10.7 Safety Analyses — laboratory and vital signs, specified under P6 (D11, G7; 2026-09-20).** Safety population, descriptive, no inferential testing. Laboratory: summary of values and change from baseline by parameter and analysis visit; shift from baseline to worst post-baseline reference-range category; worst post-baseline CTCAE v5.0 grade by parameter with a grade ≥3 listing. Vital signs: summary of values and change from baseline by parameter and visit. Stated in §3.2.5; this is what TORIVA's T-LB-01, T-LB-02 and L-LB-01 built without a specification.",
        ],
    },
    {
        "num": "11", "file": "section-11-general-considerations.md",
        "title": "11 General Considerations: Regulatory, Ethical, Trial Oversight and Data Handling",
        "elements": "11.1 Regulatory and Ethical Considerations; 11.2 Trial Oversight; 11.3 Informed Consent Process; 11.4 Committees; 11.5 Insurance and Indemnity; 11.6 Risk-Based Quality Management; 11.7 Data Governance; 11.8 Data Protection; 11.9 Source Records; 11.10 Protocol Deviations; 11.11 Early Site Closure; 11.12 Data Dissemination",
        "blocks": [
            ("11.1 Regulatory and Ethical Considerations — GCP compliance ← §9.1", 745, 754),
            ("11.1 Regulatory and Ethical Considerations — IRB/IEC ← §9.2", 756, 760),
            ("11.3 Informed Consent ← §9.3", 762, 773),
            ("11.8 Data Protection ← §9.4", 775, 777),
            ("11.4 Committees — Safety Monitoring Committee ← §7.5", 601, 607),
            ("11.7 Data Governance — CRF design ← §10 KEY INFORMATION FOR CRF DESIGN", 789, 817),
        ],
        "notes": [
            "**11.4 Committees**: the Safety Monitoring Committee (§7.5), moved here from section 9 on 2026-09-20 (review-sheet item 2b, LG's verdict), where M11 numbers it. **11.2 Trial Oversight**: absent from the source.",
            "**11.6–11.13**: source records, financial disclosure, insurance, publication policy, protocol deviations, early site closure, data dissemination, quality assurance — all absent from the source, which is a synopsis.",
        ],
    },
    {
        "num": "12", "file": "section-12-appendix-supporting-details.md",
        "title": "12 Appendix: Supporting Details",
        "elements": "12.1 Clinical Laboratory Tests; 12.2 Country/Region-Specific Differences; 12.3 Prior Protocol Amendment(s); 12.4 Additional Appendices",
        "blocks": [
            ("12.3 Prior Protocol Amendments ← DOCUMENT HISTORY", 946, 951),
        ],
        "notes": [
            "**12.1 Clinical Laboratory Tests**: [`section-12-01-clinical-laboratory-tests.md`](section-12-01-clinical-laboratory-tests.md), hand-made under stage 0b.",
            "**12.2 Country/Region-Specific Differences**: the source refers twice to a *\"country-specific protocol appendix\"* (§4.2 criterion 2) and a *\"country-specific consent addendum\"* (§9.3) that do not exist in the document set. Absent.",
            "**12.3 Prior Protocol Amendments**: the document history records v1.0 → v1.1 (identifier and legal-notice changes only). No substantive amendment; M11's amendment elements are correctly absent for an unamended protocol.",
        ],
    },
    {
        "num": "13", "file": "section-13-glossary.md",
        "title": "13 Appendix: Glossary of Terms and Abbreviations",
        "elements": "13 Glossary of Terms and Abbreviations",
        "blocks": [("13 ← APPENDIX A — ABBREVIATIONS", 850, 925)],
        "notes": ["Moved unchanged, including the source's broken table row at *DSMB* (lines 869–871), because fixing it would be editing."],
    },
    {
        "num": "14", "file": "section-14-references.md",
        "title": "14 Appendix: References",
        "elements": "14 References",
        "blocks": [("14 ← APPENDIX B — KEY REFERENCES", 931, 942)],
        "notes": [],
    },
]

HAND_MADE = [
    {"num": "0", "file": "section-00-title-page.md", "title": "Title Page", "status": "restructured by hand (stage 0b)", "gaps": "G2, G3"},
    {"num": "3", "file": "section-03-objectives-endpoints.md", "title": "3 Trial Objectives, Endpoints and Estimands", "status": "restructured by hand (stage 0b)", "gaps": "G1 resolved; G7"},
    {"num": "8.4.2", "file": "section-08-04-02-vital-signs.md", "title": "8.4.2 Vital Signs", "status": "restructured by hand (endpoint 2)", "gaps": "G6"},
    {"num": "12.1", "file": "section-12-01-clinical-laboratory-tests.md", "title": "12.1 Clinical Laboratory Tests", "status": "restructured by hand (stage 0b)", "gaps": "G4, G5"},
]


def render(sec: dict, src: list[str]) -> str:
    out = [BANNER, f"# {sec['title']}", "",
           f"*ICH M11 elements: {sec['elements']}.* Generated by `tools/m11_restructure.py` on the",
           f"source synopsis at `{SOURCE_COMMIT}`: every block below is a verbatim line range of it, cited. The notes",
           "at the foot are ours.", ""]
    for label, a, b in sec["blocks"]:
        out += [f"## {label}", "", f"*Source: `protocol/synopsis.md` lines {a}–{b}, moved unchanged.*", ""]
        out += [line.rstrip("\n") for line in src[a - 1:b]]
        out += [""]
    out += ["## M11 conformance of this section", ""]
    if sec["notes"]:
        out += [f"- {n}" for n in sec["notes"]]
    else:
        out += ["- Supplied in full by the source."]
    out += ["", f"*Dispositions for the gaps named here are in [`../../gap-register.md`](../../gap-register.md).*", ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synopsis", required=True, help="path to TORIVA protocol/synopsis.md at 8534339d")
    ap.add_argument("--root", default=".", help="repository root")
    ap.add_argument("--check", action="store_true", help="verify generated files match; write nothing")
    args = ap.parse_args()

    src_path = Path(args.synopsis)
    src = src_path.read_text(encoding="utf-8").splitlines(keepends=True)
    root = Path(args.root)
    out_dir = root / "study" / "m11" / "protocol"
    sha = hashlib.sha256(src_path.read_bytes()).hexdigest()[:12]

    problems = 0
    coverage = {"source": "OpenTrialReporting/torivumab-nsclc-301 protocol/synopsis.md",
                "source_commit": SOURCE_COMMIT, "source_sha256_12": sha,
                "generator": "tools/m11_restructure.py", "sections": []}
    for sec in SECTIONS:
        text = render(sec, src)
        target = out_dir / sec["file"]
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                print(f"  DIFFERS: {target}")
                problems += 1
        else:
            target.write_text(text, encoding="utf-8")
        n_lines = sum(b - a + 1 for _, a, b in sec["blocks"])
        coverage["sections"].append({
            "section": sec["num"], "title": sec["title"], "file": sec["file"],
            "status": "generated — moved from source" if sec["blocks"] else "absent from source",
            "moved_lines": n_lines, "blocks": [[lbl, a, b] for lbl, a, b in sec["blocks"]],
            "absent_elements": len(sec["notes"]),
        })
    for h in HAND_MADE:
        f = out_dir / h["file"]
        coverage["sections"].append({"section": h["num"], "title": h["title"], "file": h["file"],
                                     "status": h["status"] if f.is_file() else "MISSING", "gaps": h["gaps"]})
    coverage["sections"].sort(key=lambda s: [int(x) for x in s["section"].split(".")])
    cov_path = out_dir / "coverage.json"
    cov_text = json.dumps(coverage, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not cov_path.is_file() or cov_path.read_text(encoding="utf-8") != cov_text:
            print("  DIFFERS: coverage.json"); problems += 1
        print("check:", "OK" if problems == 0 else f"{problems} file(s) differ")
        return 1 if problems else 0
    cov_path.write_text(cov_text, encoding="utf-8")
    total = sum(s.get("moved_lines", 0) for s in coverage["sections"])
    print(f"wrote {len(SECTIONS)} sections + coverage.json; {total} source lines moved; "
          f"{len(coverage['sections'])} entries in coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
