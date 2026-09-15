# The source study

**TORIVA-LUNG 301** — a simulated Phase 3 NSCLC trial with a fictional sponsor, public at
`OpenTrialReporting/torivumab-nsclc-301`.

## Why this study

Chosen over the CDISC Pilot and over real sponsor protocols because it is the only available
source where protocol, SAP, programming specs **and built ADaM** all exist, are internally
consistent, and carry no confidentiality constraint.

The built ADaM is the reason. Without ground truth the exercise demonstrates only that the
concept model is internally coherent. With it, each divergence is informative: either the
model cannot express something real, or it has exposed an ambiguity the SAP was carrying
silently. Both are worth knowing, and neither is available from a reference example.

## What is used

| Artefact | Size | Used for |
|---|---|---|
| SAP | 626 lines, nine estimands with an ICH E9(R1) table at §13 | Endpoint definitions and estimand attributes for all three tiers |
| Programming specs | Variable-level, per dataset | The derivation each tier has to reproduce |
| Built ADaM | Parquet, 450 subjects | Ground truth at step 3 of the method |
| Protocol synopsis | 959 lines | Endpoint text, objective hierarchy |
| TFL shells | Cross-referenced from the specs | Which analyses consume each parameter |

Exact sections and the pinned commit are in [source-refs.md](source-refs.md).

## What is not used

**Adverse events.** A different *shape* rather than a deeper one — event observations rather
than findings, counts rather than measures, OCCDS rather than BDS. Named as an untested
limitation; not worth the authoring cost in a snapshot.

**The other five ADTTE parameters.** ADTTE carries OS, OSWOT, PFS, PFSINV, DOR and TTR.
PFS alone is the tier.

OSWOT is worth a passing mention even so, because its own spec already records a data
limitation: no subsequent anti-cancer therapy is captured in CM, so the full SAP §13.4
censoring rule — `min(TRTEDT + 30d, subsequent therapy start)` — collapses to `TRTEDT + 30d`.
That is specification meeting data reality, and a flow snapshot should show it rather than
hide it.

The same limitation bears on PFS: SAP §4.2's second censoring branch, *new anti-cancer
therapy before PD*, is unreachable in this data for the same reason. It remains in the paper
mapping because the question is whether the **model** can express it, not whether this
particular dataset exercises it.

## The ADAS-Cog control

The CDISC Pilot's ADAS-Cog endpoint is retained as a control, since Scenario 2 is already
worked upstream. When something breaks, it distinguishes a broken flow from a broken endpoint.

## Note on authorship

The TORIVA programming specs carry the same author as this repository. That makes the study
convenient to work with and creates an obvious bias risk: a chain mapped against a spec one
wrote oneself is not an independent test of whether the SAP is expressible.

Two things limit it. The comparison at step 3 is against **built** ADaM — code that already
ran, not prose that can be reread charitably. And the discrepancies recorded in
`source-refs.md` (D1, D2) are discrepancies *in the source study*, found by the mapping and
recorded against it rather than quietly reconciled.
