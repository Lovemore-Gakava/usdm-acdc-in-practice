# Vital signs change from baseline (MMRM) — authoring log

Step 4 of the method: what the authoring cost, and every point where a decision was needed.

**Authored 2026-09-19** against `ac-dc-app` at upstream `739344c`, served locally, on the
TORIVA USDM fragment regenerated the same day to carry `END-S5-VS` and BC `C25298`. The chain
was authored with the lab tier's execution lessons applied up front, which is the point of a
second endpoint: to see what a second pass costs when the first one's decisions are known.

## Structural cost (stages 2–5)

| | |
|---|---|
| Analysis transformations selected | 1 (`T.CFB_MMRM_Primary`) |
| Derivation transformations selected | 1 (`T.ChangeFromBaseline`) — auto, one candidate |
| Derivation transformations authored | 0 |
| Method configurations changed | 0 (`UN` / `REML` / `KR` as shipped) |
| Terminals confirmed | 7 — three measure, four dimension |
| BCs linked | `BiomedicalConcept_SYSBP` on each of the three measure terminals |
| Unresolved slots at completion | 0 |
| Bindings resolved by hand outside the UI | **2** — see V1 |

## Decision points

| # | Decision | Chosen | Determined by |
|---|---|---|---|
| V-D1 | Endpoint | `END-S5-VS` | the second-endpoint decision |
| V-D2 | Concept category | `Change (Comparison)` | the analysis chosen |
| V-D3 | Parameter dimension form | `Parameter (DC)` | lab tier L7 / D18 |
| V-D4 | Parameter value | `Systolic Blood Pressure` (label) | lab tier D19 |
| V-D5 | Visit dimension form | `AnalysisVisit (DC)`, **no value** | MMRM takes every visit — replaces lab D21 |
| V-D6 | Population | `SAF` | protocol §8.2, safety endpoint |
| V-D7 | Treatment | `Torivumab vs Placebo` | the arms |
| V-D8 | Analysis template | `Change From Baseline MMRM Primary Analysis` | the second-endpoint decision |
| V-D9 | Resolve `minuend` | `(raw)` | lab tier D6 — still the tenth option, below nine wrong ones (L2) |
| V-D10 | Resolve `subtrahend` | `(raw)` | lab tier D7 |
| V-D11 | Resolve `covariate` | `(raw)` | lab tier D8 |
| V-D12 | Confirm `Treatment` terminal | confirmed | — |
| V-D13 | Link BC on three measure terminals | `SYSBP` | stage 2 |

Thirteen decisions, none of them statistical, and nine of them already made once on the lab
tier. The two that are new — V-D5 and V-D8 — are the ones the endpoint was chosen for.

## Where it strained

### V1 — two bindings the selection left unresolved, and a render that died on them

`T.CFB_MMRM_Primary` declares `repeated_factor` and `constraint` **by concept category**
(`VisitDimension`, `ParameterDimension`), not by concept. Selecting the template in step 4
copied both bindings into the endpoint's analysis with `concept` undefined. The next render
threw — `resolveRoleNames` in `transformation-linker.js:733`, `Cannot read properties of
undefined (reading 'includes')` — inside `rebuildSpec`, which runs on every render, so step 4
could not be used at all from that state.

The app has the rule for this: `buildPipelineGraph` resolves a category-declared binding from
the endpoint's `dimensionCategoryPicks` (the step 3 form picks) with the category's first
member as fallback. It is applied on the pipeline path and not on the selection path. Applying
it by hand — `repeated_factor ← AnalysisVisit`, `constraint ← Parameter`, both straight from the
picks — made step 4 render and everything downstream work. Recorded here as the only point where
the chain needed a hand outside the UI; not pursued further.

### V2 — the eSAP's estimand for an endpoint no estimand targets

No USDM `Estimand` points at `END-S5-VS` (the SAP has none for vitals). Step 7 still emitted an
estimand for it, assembled entirely from the chain: analysis population `SAF` and both arms from
the dimension values (L6), intercurrent events empty, and **population-level summary = `SAF`** —
the serializer's fallback is `dimValues.Population` when no USDM estimand supplies a summary.
That is a population name in a summary-measure slot. Left as emitted, because it is what the
tool does; noted so the eSAP is read with it in mind.

### V3 — the BC picker

The terminal picker listed all eight study BCs for every measure terminal, the new SYSBP entry
three times over. `Endpoint.biomedicalConceptIds` still is not consulted (lab tier L5): the
endpoint says SYSBP and the picker offers the seven lab tests beside it.

## What this endpoint cost, in one line (so far)

**Zero authoring, thirteen decisions of which nine were repeats, two bindings resolved by hand
because the app's own rule was not applied on the path taken, and a chain that reached the
eSAP with no single-visit choice.** Execution and comparison follow.
