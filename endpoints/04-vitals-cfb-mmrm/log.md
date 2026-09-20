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
| V-D14 | Visit window for execution | Baseline + C1D15–C6D1, applied to the data before upload | an unstructured covariance over forty visits is not a fit; the cube's visit dimension holds one value, not a set |
| V-D15 | Execute MMRM with what? | **write an `M.MMRM` implementation** | upstream ships none (V4); WebR can install `mmrm` |
| V-D16 | Execution overrides | `advs`, `TRT01P`, `SAFFL = Y`, no treatment filter, covariate `BASE` | the lab tier's L7, applied up front |

Sixteen decisions, none of them statistical, and ten of them already made once on the lab
tier. The ones that are new — V-D5, V-D8, V-D14, V-D15 — are the ones the endpoint was chosen
for, and V-D15 is the one nobody planned.

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

### V4 — step 8 cannot run it: `M.MMRM` has no R implementation *(stage 6, 2026-09-19)*

With ADSL and ADVS loaded (450 and 52,920 rows), the dataset set to `advs`, `TRT01P`, `SAFFL = Y`,
no treatment filter and the covariate bound to `BASE`, Execute returned at once:
**`No R implementation available for M.MMRM`**. The registry confirms it:
`lib/method_implementations/r_implementations.json` at `739344c` carries 19 R implementations —
`M.ANCOVA`, `M.Subtraction`, `M.WindowedVisitAssignment`, the descriptive statistics and tests —
and no `M.MMRM`; the SAS registry (11) has none either. So the library ships the MMRM *template*
and the *method*, the builder authors the chain and generates the eSAP, and the execution layer
has nothing to run it with.

This blocks stage 6 for this endpoint, and therefore stage 7. It is the same shape as F13 one
layer down — method ≠ transformation ≠ builder, and now ≠ implementation — recorded here in the
log rather than as a fourteenth finding, because it blocked a stage being actively completed and
two paragraphs is what that gets. What happens next is a decision, not authoring.

### V5 — writing the implementation: three things `mmrm` needed that the engine did not give it *(stage 6, 2026-09-19)*

LG asked why an R implementation could not simply be written. It could. WebR reported `mmrm`,
`nlme`, `emmeans` and `lme4` installable, the registry format is a JSON entry with a
`callTemplate` of `<role>` placeholders and an `outputMapping` of R expressions per output class
(upstream's `M.ANCOVA` entry was the model), and the app reads the catalog from
`appState.methodImplementationCatalog` — so the entry was injected into the running page rather
than written into the pinned submodule. It is [`r_impl_mmrm.json`](r_impl_mmrm.json), ours, and
says so.

It took three iterations, each a fact about the seam between the framework's data layer and a
real mixed model:

1. **Duplicate time points at Baseline.** The endpoint slice has no visit filter, so the cube
   carried both Baseline-window rows for 340 subjects. `lm` had silently taken the first;
   `mmrm` refuses. The implementation now keeps one row per subject and visit (the engine's own
   `!duplicated` convention) and drops the visit at which every change is zero — the baseline
   visit by construction — because the slice cannot say "≠ Baseline".
2. **Non-syntactic names.** The engine's derived response is `__col_T_CFB_MMRM_Primary_Change_0`;
   `mmrm`'s formula parser cannot use it. Response and covariate are copied to syntactic names.
3. **Type-3 tests.** `car::Anova` fell to its default method on an `mmrm` object without `car`
   attached. `emmeans::joint_tests` supports `mmrm` directly and is used instead.

The run then completed in about a minute in WebR: six visits, 2,605 rows, 446 subjects, all six
output classes populated — and reproduced exactly by the same model in local R.

## What this endpoint cost, in one line

**Zero chain authoring and one method implementation, sixteen decisions of which ten were
repeats, two bindings resolved by hand because the app's own rule was not applied on the path
taken, an MMRM that upstream could not run and this project could — reproduced exactly — and the
same wrong baseline row as the lab tier, on 74% of subjects, at every visit.**

## P6 re-run, 2026-09-20

The fragment was regenerated under P6 (`NORTH.md`): arms per the protocol corrected to the SAP
(D14), randomisation 2:1 as the protocol states (D15), the "data is the ground truth" rule gone.
The chain was executed again on it, same data, same selection — MMRM identical at all six visits and in AIC (C2D1 −1.3753, SE 1.9333); ANCOVA companion −1.3862 (SE 1.9375, n 446), identical. Recorded as `p6_rerun` in
`results.json`, stamped with the new `usdm_sha256`, with the design note the app loaded
(*"Randomisation 2:1 (D15, the protocol stands)…"*) kept beside the run as evidence of which
fragment it was. The study description's corrections do not enter the execution, as P5 found.
