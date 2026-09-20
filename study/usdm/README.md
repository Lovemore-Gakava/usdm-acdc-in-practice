# Hand-authored USDM v4 fragments

`NORTH.md` **stage 1**, then **regenerated under stage 0b**. Authored 2026-09-16 from prose,
regenerated the same day from the ICH M11-restructured protocol in `study/m11/protocol/`.
Loaded successfully in `ac-dc-app` both times.

**The regeneration took the fragment from one `Estimand` to six**, and added two
`AnalysisPopulation` objects, because M11 §3 puts the estimand attributes in the protocol where
USDM can source them. See [`../m11/protocol/README.md`](../m11/protocol/README.md).

`toriva-lung-301.usdm.json` — TORIVA-LUNG 301's objective and endpoint hierarchy, arms,
population, one estimand, and the seven laboratory biomedical concepts.

## What was learned about USDM v4

The shape the application requires, established by reading `ac-dc-app/js/utils/usdm-parser.js`
rather than guessing, and confirmed against the shipped CDISC Pilot study:

```
study
└── versions[0]                       ← everything hangs off the first version
    ├── studyIdentifiers[]
    ├── businessTherapeuticAreas[]
    ├── biomedicalConcepts[]          ← BCs live at VERSION level, not on the design
    │   └── properties[]              ← each with datatype and responseCodes
    └── studyDesigns[0]
        ├── studyType / studyPhase / therapeuticAreas    ← Code or AliasCode objects
        ├── arms[]
        ├── population
        ├── objectives[]
        │   └── endpoints[]
        │       └── biomedicalConceptIds[]   ← the endpoint → BC join
        ├── estimands[]               ← variableOfInterestId points at an Endpoint id
        ├── analysisPopulations[]
        └── activities / encounters / scheduleTimelines
```

Three things that were not obvious beforehand:

1. **`biomedicalConcepts` sit on the study *version*, not the study design.** The Pilot's design
   carries `0` and its version carries `182`.
2. **Endpoints carry `biomedicalConceptIds` directly.** So the BC join exists in USDM before any
   AC/DC chain is authored — the framework's `linkedBCIds` at terminal level is a *second*,
   separate join. Two places to say the same thing, which is worth keeping in mind for stage 2.
3. **`Estimand.variableOfInterestId` references an `Endpoint` id.** That is the hook the
   specification claims connects protocol metadata to the eSAP, and it is real.

Codes (`C15602` Phase III, `C85826`/`C85827` objective levels, `C94496`/`C139173` endpoint
levels, `C174266`/`C174268` arm types) were taken from the shipped Pilot study rather than from
memory.

## Does USDM need the SAP? Almost never — and that is the point

Asked after the fragment was first authored, and it found a mistake in it: objectives were
cited to **SAP §2** when the protocol carries all six in full at **§2 STUDY OBJECTIVES**.
Corrected — every objective's `text` is now the protocol's wording.

The layering, once you look:

```
protocol  +  CDISC Library   →   USDM   (objectives, endpoints, BCs, arms, population)
SAP                          →   DC (derivations)  and  AC (analyses)
```

**USDM is a study-definition model, so the protocol is its source.** Objectives §2, endpoint
definitions §6, arms, population, phase, therapeutic area, and the schedule of activities that
BCs attach to — all protocol.

**BC needs nothing from the SAP at all.** Biomedical Concepts are CDISC Library entries — the
shipped Pilot's carry `reference: /mdr/bc/packages/2025-04-01/biomedicalconcepts/C28421` — and
they attach to *activities* in the protocol's SoA. The SAP has no role.

**One exception: estimand content.** TORIVA's protocol defers it. Synopsis line 834 lists
*"Define estimands per ICH E9(R1) … for OS, PFS, ORR separately"* as an **SAP deliverable**, and
the estimands themselves exist only in SAP §13. So the six `Estimand` objects here are what the
protocol could not supply, and each says so on the object.

> **Corrected 2026-09-17.** This said *"one exception: the `Estimand` class"* and *"`Estimand_E1`
> is the single object the protocol could not supply"*. That was too narrow on both counts. It is
> **estimand content** that is displaced, not one class, and it surfaces in USDM as two: the
> `Estimand` objects, and two of the four `AnalysisPopulation` objects. `RESPEVAL` and
> `RESPONDER` cite SAP §13.6 and §13.7, because they arrive through M11's **Population** element
> `C70833` — itself an ICH E9(R1) estimand attribute — rather than from any population section of
> the protocol. `ITT` and `SAF` are the protocol-native pair. The layering below is unchanged;
> the exception is one category wider than stated.
>
> **Corrected again 2026-09-18, on review (review-sheet item 3a).** The paragraph above is itself
> too wide. TORIVA's protocol defines the Response Evaluable population at **§8.2**, alongside
> ITT, Safety and Per-Protocol, and names the responder set in its analysis table. The fragment's
> `RESPEVAL` and `RESPONDER` objects cited SAP §13.6/§13.7 because *I* took them from there — a
> citation error in the fragment, not a property of the study. Corrected in the fragment and in
> `study/m11/protocol/section-03-objectives-endpoints.md`. So three of the four populations are
> protocol-native and the fourth is protocol-named; the exception is the estimand attributes and
> nothing else. The layering holds as first written.

That is worth noticing rather than shrugging at. ICH E9(R1) intends estimands to be
pre-specified in the protocol, and USDM models `Estimand` as study-definition content. A study
that puts its estimands in the SAP puts a USDM class out of reach of its natural source — and
if the protocol were digitised as USDM first, as USDM is meant to be used, those estimands would
have nowhere to come from.

It also explains the lab tier cleanly. USDM is fine for it: the protocol names Safety and
schedules laboratory assessments. It is the **DC/AC end** that is empty, because the SAP is
silent on laboratory analysis. The gap is downstream of USDM, not in it.

## What is authored, and what is deliberately not

Authored from the **protocol synopsis** — objectives §2, endpoint definitions §6 — with SAP
cross-references in each `description` where the SAP adds a hypothesis or a threshold:

| Objective | Endpoint | Objective text from | SAP adds |
|---|---|---|---|
| OBJ1 primary | `END-OS` Overall Survival | protocol §2.1 | §2.1 — null hypothesis OS HR = 1 |
| OBJ-S1 | `END-PFS` | protocol §2.2 (1) | §2.2 S1 — PFS HR = 1 |
| OBJ-S2 | `END-ORR` | protocol §2.2 (2) | §2.2 S2 — ORR difference = 0 |
| OBJ-S3 | `END-DOR` | protocol §2.2 (3) | §2.2 S3 — no formal test |
| OBJ-S4 | `END-DCR` | protocol §2.2 (4) | §2.2 S4 — DCR difference = 0, SD ≥ 8 weeks |
| OBJ-S5 | `END-S5-LAB` Safety — laboratory evaluations | protocol §2.2 (5), §7.2 | **nothing** — see below |

Endpoint text is from protocol §6 throughout. The SAP contributes hypotheses and thresholds,
which are analysis content — it supplies no objective or endpoint *definition*.

**Not authored:** schedule of activities, encounters, eligibility criteria, study interventions,
the other eight estimands. Not needed for the traverse and not worth inventing.

## The one honest compromise

`END-S5-LAB` is authored **from the protocol, not the SAP.** The protocol names Safety as a key
secondary endpoint and §7.2 schedules laboratory assessments, so the endpoint is real. But the
SAP defines no laboratory analysis: `ADLB` appears only in data-handling conventions (§12.2,
§12.3, §7), and all three safety estimands in §13.7 are adverse-event based — TEAE incidence,
exposure-adjusted TEAE rate, irAE incidence. **There is no laboratory estimand.**

That is discrepancy **D11**, and it is visible in this fragment: `END-S5-LAB` is the only
endpoint here with no `Estimand` pointing at it. It was not smoothed over, because the endpoint
the project takes all the way through the framework being one the SAP never analyses is a
result, not an inconvenience.

## Verified how

Copied into `ac-dc-app/data/usdm/` with a `studies.json` entry as a **throwaway local edit**,
served, and loaded. The app listed *"TORIVA-LUNG 301 | SIMULATED-TORIVUMAB-2026 | Phase III
Trial | Lung Non-Small Cell Carcinoma"* and rendered all six endpoints under their objectives
with correct Primary/Secondary levels. The submodule was then reverted —
`git -C upstream/analysis-concepts checkout ac-dc-app/data/usdm/studies.json` — and is clean at
`739344c`.

## Known limitation, carried into stage 2

This fragment has **no `activities` and no `scheduleTimelines`**, so the Schedule of Activities
tab is empty. Whether the derivation pipeline's terminal BC picker can offer these BCs without
an activity to hang them on is **not yet known**, and is the first thing to find out in stage 2.

## Second endpoint, 2026-09-19

`END-S5-VS` — vital signs, under OBJ-S5 beside `END-S5-LAB` — and the BC `Systolic Blood Pressure` (`C25298`, shape copied from the shipped Pilot's SYSBP BC) were added, sourced from the restructured M11 §8.4.2 (`../m11/protocol/section-08-04-02-vital-signs.md`). No estimand targets it: the SAP specifies no vital-signs analysis, the laboratory situation (D11) again. The fragment now carries eight BCs and seven endpoints.

## Phase 2, stage P2 — generated, 2026-09-19

The fragment is now **generated** by [`../../tools/m11_to_usdm.py`](../../tools/m11_to_usdm.py) from the
M11 sections in `../m11/protocol/`, and re-runnable (`--check` verifies). What changed from the
hand-written fragment:

- **A schedule of activities exists.** 3 epochs, 39 encounters (screening, Cycle 1–35 Day 1, EOT,
  30- and 90-day follow-up), 13 activities parsed from the source's §7.2 safety table plus tumour
  imaging from §6.1, and one timeline of 39 instances with 334 activity-visits. The lab BCs hang on
  the Haematology and Chemistry activities, SYSBP on Vital signs. The app's Schedule of Activities
  tab, empty since stage 1, renders it.
- **Arms and interventions are corrected and marked** — *(as first generated; revised under P6, below)* D14 (both arms on the chemotherapy backbone,
  named as `TRT01P` names them; a third `StudyIntervention` for the backbone cites SAP §13.2) and
  D15 (1:1). The source's monotherapy and 2:1 wording is kept in `notes` on each object.
- Objectives, endpoints, estimands, populations and BCs are carried over unchanged from stage 0b.

The "known limitation carried into stage 2" below no longer holds; it is kept as the record.

**Endpoint texts, 2026-09-19 (P3 found this).** The alignment tool's first run failed five of
seven endpoints: the fragment's endpoint texts had been *written* at stage 1 — "subjects" where
the protocol says "patients", the lab and vitals endpoints composed rather than moved — so the
USDM disagreed with the M11 protocol on wording. The generator now lifts each endpoint's text
verbatim from the `Endpoint` row of its §3 block, and the vitals endpoint's text is the source's
own measurement list from §8.4.2. Each endpoint carries a note saying so.

## Phase 2, stage P7 — regenerated from the re-pinned source (`a806630`), 2026-09-20

TORIVA issue #27 closed and the source was re-pinned. The generator now runs on the synopsis at
`a806630`, which states the combination design itself; the D14 and D15 notes on the arms say
*resolved upstream*, the backbone intervention cites the source's §3.5/§5.1, and the hand-carried
design description no longer says the data is 1:1. Endpoint texts are unchanged. Hash
`0fa49253…`; both endpoints re-run on it and on the regenerated data (`p7_rerun_a806630`).

## Phase 2, stage P6 — regenerated on the corrected documents, 2026-09-20

The rule the P2 generation ran on — *the built data is the ground truth* — was withdrawn by LG
(review-sheet item 3a; `NORTH.md` P6). The fragment now follows the corrected protocol:

- **D14** — the arms are still *Torivumab + Chemotherapy* and *Placebo + Chemotherapy*, but
  because the protocol was corrected to the SAP (a placebo-alone first-line control does not
  exist), not because the data names them so. The notes on each arm and on the backbone
  intervention say this; the phrase *ground truth* no longer appears in the fragment, and the
  alignment tool checks that it does not.
- **D15** — the design's randomisation is **2:1**, as the protocol states. The data's 1:1 is
  reported by `tools/check_alignment.py` as a WARN: the data diverging from the documents, to be
  regenerated upstream.
- Nothing else in the fragment changed. The hash did, so both endpoints were re-run on it the same
  day (P5): identical at every number. Each `results.json` carries a `p6_rerun` block stamped with
  the new hash and the design note the app loaded.
