# Hand-authored USDM v4 fragments

`NORTH.md` **stage 1**. Authored 2026-09-16, and loaded successfully in `ac-dc-app`.

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

## What is authored, and what is deliberately not

Authored from the **protocol synopsis** (endpoint definitions) and **SAP §2** (objectives),
quoted in each `description`:

| Objective | Endpoint | Source |
|---|---|---|
| OBJ1 primary | `END-OS` Overall Survival | SAP §2.1 |
| OBJ-S1 | `END-PFS` | SAP §2.2 S1 |
| OBJ-S2 | `END-ORR` | SAP §2.2 S2 |
| OBJ-S3 | `END-DOR` | SAP §2.2 S3 |
| OBJ-S4 | `END-DCR` | SAP §2.2 S4 |
| OBJ-S5 | `END-S5-LAB` Safety — laboratory evaluations | protocol §7.2 — **not the SAP**, see below |

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
