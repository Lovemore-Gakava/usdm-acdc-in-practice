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
