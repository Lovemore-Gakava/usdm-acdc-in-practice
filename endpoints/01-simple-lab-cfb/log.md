# Lab change from baseline — authoring log

Step 4 of the method: what the authoring actually cost, and every point where a decision was
needed.

**Authored 2026-09-16** against `ac-dc-app` at upstream `739344c`, served locally
(`python ac-dc-app/serve.py`).

**Re-authored the same day against TORIVA.** The first pass used CDISC Pilot END5 because no
TORIVA USDM existed (L1). Once stages 1 and 0b supplied one, the chain was rebuilt on
**TORIVA `Endpoint_SAFETY_LAB`** and BCs were linked (stage 2). [`chain.json`](chain.json) is
the TORIVA chain; the decision counts below are from the first pass and are marked where the
re-authoring changed them.

---

## What is being measured, and what is not

**No elapsed time is reported here.** PROVENANCE §7.9 gives the reason: this chain was authored
by an AI model driving the browser, and its wall-clock is not a statistician's, not a wizard
session's, and does not scale like either. Reporting it as the specification §6.1 figure would
produce a number that looks like evidence and is not.

What is reported instead is **decision points** and **structural cost** — both properties of the
chain rather than of whoever authored it, and therefore comparable across tiers, which is the
comparison §6.1 actually wants. Neither answers *"how many hours"*. That still needs a
statistician in the builder with a stopwatch.

---

## Structural cost

| | |
|---|---|
| Analysis transformations selected | 1 (`T.CFB_ANCOVA`) |
| Derivation transformations selected | 1 (`T.ChangeFromBaseline`) — **auto**, see D3 below |
| Derivation transformations authored from scratch | 0 |
| Method configurations set | 0 |
| Terminals confirmed | 7 |
| Bindings resolved | 6 |
| Unresolved slots at completion | 0 |
| Serialised instance | 4,225 bytes compact / 6,640 pretty |

Nothing was authored. Everything was **selected or confirmed** — which is exactly what the
specification predicted for this tier (*"expected to work with no new authoring"*), and it held.

---

## Decision points

Eleven, in order. The column that matters is the last one.

| # | Decision | Options | Chosen | Determined by the SAP? |
|---|---|---|---|---|
| D1 | Study | 2 shown, 1 selectable | CDISC Pilot | **n/a** — TORIVA is not loadable, see L1 |
| D2 | Endpoint | 11 | END5 | yes |
| D3 | Concept category | **29** | `Change (Comparison)` | **no** |
| D4 | Data type | 6 | `Quantity` (default) | implicitly |
| D5 | Analysis template | 2 | `Change From Baseline ANCOVA` | **no** — TORIVA specifies no lab analysis at all |
| D6 | Resolve `minuend` | 9 templates + `(raw)` | `(raw)` | yes |
| D7 | Resolve `subtrahend` | 9 templates + `(raw)` | `(raw)` | **no** — see L2 |
| D8 | Resolve `covariate` | 9 templates + `(raw)` | `(raw)` | yes |
| D9 | Confirm `Treatment` terminal | confirm | confirmed | yes |
| D10 | Confirm `Observation.Identification.Topic` terminal | confirm | confirmed | yes |
| D11 | Confirm `Visit` terminal | confirm | confirmed | yes |

`Subject` was auto-confirmed by the application (`autoConfirm` on shared dimensions), so it is
not counted.

**Four of eleven decisions are not determined by the source SAP** — D1, D3, D5, D7. Three of
those four are not judgement calls a statistician would recognise as theirs to make.

---

## Where it strained

### L1 — the study is not the study *(retired 2026-09-16)*

> **No longer true.** The chain was re-authored against **TORIVA** once `study/usdm/` existed
> (stages 1 and 0b). `chain.json` now carries `"studyName": "TORIVA-LUNG 301"` and endpoint
> `Endpoint_SAFETY_LAB`. The original text follows, because the decision counts recorded in
> this log were taken under it.

### L1 — the study is not the study *(as originally recorded)*

The builder carries one selectable study, the CDISC Pilot. TORIVA cannot be loaded, because
its USDM fragments do not exist (specification §15.3, still open). END5 is the right *shape* —
laboratory change from baseline — so the chain and its cost are representative, but every
endpoint identifier in `chain.json` is a Pilot identifier.

This is the single largest caveat on this tier and it propagates into step 3: the comparison in
[`comparison.md`](comparison.md) is of *definitions*, not of output numbers.

### L2 — the correct answer was the tenth option, below nine wrong ones

D6, D7 and D8 each offered nine derivation templates: LOCF imputation, seven ADAS-Cog helpers,
and a unit conversion. For a laboratory change from baseline against collected values, all nine
are wrong. The correct answer — `AVAL/AVALC/BASE (Measure) (raw) — Use source data directly
without derivation` — is rendered **after** all nine, at the bottom of the library panel.

The panel text reads *"Select a derivation template from the library panel that produces …"*
and *"9 templates available →"*. Nothing indicates that using source data is the expected
answer for most slots, or that it is available at all without scrolling.

For D7 specifically this is worse than a UI nuisance. The slot being resolved is the
**baseline value**, and the obviously-named candidate for it — `T.BaselineSelection` — is not in
the list and cannot be, because it outputs a `Flag`
([F12](../../docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md)). An author
looking for baseline selection will not find it, will find LOCF imputation instead, and has no
signal that `(raw)` plus an invisible visit constraint is what the model intends.

### L3 — one derivation was chosen for me

`T.ChangeFromBaseline` was selected automatically, with no prompt, because
`findDerivationsForConcept('Change', library)` returns exactly one candidate and
`transformation-linker.js:189` auto-selects when `candidates.length === 1`.

That is reasonable behaviour and it is worth recording that it happened, because the resulting
`chain.json` does not distinguish an auto-selection from a deliberate one. `selectedDerivations`
carries `{"T.CFB_ANCOVA/Change/0": "T.ChangeFromBaseline"}` either way. For a governance overlay
that wants to know what an author *decided*, that distinction is lost.

### L4 — the chain validates while under-determined

The pipeline reported no unresolved slots and the instance serialised cleanly. Step 3 then
showed that the baseline the chain will subtract is ambiguous for 71% of subject × parameter
groups in the target data, with a median 21% error if the wrong candidate is taken.

**Nothing in the builder or the artefact records that.** A complete-looking chain and a correct
chain are indistinguishable here, which is the strongest single observation the lab tier
produced.

### L5 — no BC linking was required to finish *(still true, and now demonstrated)*

The pipeline reported complete with **no BCs linked at all**. That was the first pass, and it
stands as an observation: BC linkage is not demanded to reach a finished-looking chain.

Stage 2 then linked them deliberately — seven TORIVA laboratory BCs on each of the three
measure terminals — and the chain was no more "complete" afterwards than before. Nothing in the
builder distinguishes the two states.

**And the USDM join is not consumed.** `Endpoint.biomedicalConceptIds` was authored in stages 1
and 0b, linking all seven BCs to the laboratory endpoint. The terminal picker ignores it:
injecting a study BC deliberately *not* linked to the endpoint, it was still offered. So a study
can state its endpoint→BC relationship in USDM and the chain will neither use nor check it —
terminal `linkedBCIds` is a second, independent join that the author must supply again by hand.

---

### L6 — two dimension values the eSAP needs that the chain did not have *(stage 5, 2026-09-17)*

Found by generating the eSAP. Step 7 reads the estimand's population-level summary and
intercurrent events from the USDM `Estimand` (matched on `variableOfInterestId`), and reads the
analysis population and treatment from the chain's `dimensionValues.Population` and
`.Treatment` (`instance-serializer.js`, `resolveAnalysisPopulation` / `resolveInterventions`).

The chain reached stage 4 with `dimensionValues: {}` — no dimension had been required to get
there, as L5 records for BCs — so the first eSAP carried `AnalysisPopulation_unknown` and
`Intervention_unspecified`. Adding the Population and Treatment dimensions in step 3 and setting
them to `SAF` and `Torivumab vs Placebo` resolved both.

**Two decisions, D12 and D13.** Neither is stated in the SAP for this endpoint; both are stated
in the USDM (`E6.analysisPopulationId`, the two arms), which is not where step 7 reads them
from. So the chain has to carry them itself. Same shape as L5.

### L7 — execution took eleven more decisions, none of them statistical *(stage 6, 2026-09-17)*

Step 8 needs `.xpt` files; TORIVA ships parquet (converted with `pyreadstat`, 44.8 MB for ADLB).
The engine's R source parsed with an error on first execute — `unexpected invalid token` — because
`core.autocrlf=true` had checked it out with CRLF; `git config core.autocrlf false` in the
submodule and a re-checkout fixed it, without changing the pinned commit.

Then the chain as authored through stage 4 did not describe TORIVA's data. In order:

| # | Decision | Chosen | Why |
|---|---|---|---|
| D14 | Source dataset | `adlb` | the builder defaulted to `adsl` |
| D15 | Treatment variable | `TRT01P` | the mapping says `TRTP`; ADLB carries `TRT01P` |
| D16 | Population slice | `SAFFL == "Y"` | the estimand's `SAF` became `ITTFL == "SAF"` |
| D17 | Treatment slice | *no filter* | the step 3 value `Torivumab vs Placebo` is a contrast label, and the data reads `Torivumab + Chemotherapy` — D14 in `source-refs.md`, in the data |
| D18 | Parameter dimension form | `Parameter (DC)` | the OC form `Observation.Identification.Topic` has no column in ADaM; the builder's own tooltip says to switch |
| D19 | Parameter value | `Alanine Aminotransferase` | the DC form is label-valued, so `ALT` matched nothing |
| D20 | Visit dimension form | `AnalysisVisit (DC)` | the OC form is collected `VISIT`, which has no `Baseline` |
| D21 | Visit | `C2D1` | one visit, or the cube pools every post-baseline row |
| D22 | Covariate variable | `BASE` | the default `AVAL` is the C2D1 value — run 3's covariate was the response's own minuend |
| D23 | Which baseline row | *not offered* | the engine takes the first; TORIVA takes `ABLFL` — see `comparison.md` |
| D24 | `ANL01FL` | *not offered* | F11 |

**Nine decisions the builder offered, two it could not.** Of the nine, none is a statistical
judgement; all are about which column and which label. Four (D15–D17, D19) exist because the
USDM and the chain name things differently from the data, which is L6 again at execution.

**Three runs are kept** in `results.json`, because each is a different authoring state and each
was reproduced exactly: run 1 with constraints skipped, run 3 after D18–D21, run 4 after D22.

## What this tier cost, in one line

**Zero authoring, eleven decisions to specify and eleven more to execute, and a chain that
completes while being wrong by a median 21% on the value it subtracts — a gap that, executed,
is 0.86 on a treatment difference with SE 1.4, on 70% of subjects.**

## What it says about scale

Specification §6.1 asks whether ten to fifty endpoints can go through this. On the evidence of
the shallowest tier: the *mechanical* cost is genuinely low — no new transformations, no
configuration, eleven clicks. The cost that would not scale is **L4**. If a chain can validate
while under-determined, then every endpoint needs the step-3 check that caught it, and that
check is bespoke per endpoint and needs the built data.

The measurement worth carrying forward is therefore not "eleven decisions per endpoint" but
"one dataset-level correctness check per endpoint, none of which the framework provides."

## P6 re-run, 2026-09-20

The fragment was regenerated under P6 (`NORTH.md`): arms per the protocol corrected to the SAP
(D14), randomisation 2:1 as the protocol states (D15), the "data is the ground truth" rule gone.
The chain was executed again on it, same data, same selection — lab ANCOVA: 1.8301 (SE 1.7678, n 435, Placebo − Torivumab), identical to run 4. Recorded as `p6_rerun` in
`results.json`, stamped with the new `usdm_sha256`, with the design note the app loaded
(*"Randomisation 2:1 (D15, the protocol stands)…"*) kept beside the run as evidence of which
fragment it was. The study description's corrections do not enter the execution, as P5 found.

## P7 re-run on the regenerated data, `a806630` (2026-09-20)

TORIVA issue #27 regenerated the data (2:1, origin at randomisation, no C1D15, the ADLB flags), and the
source was re-pinned. Executed again, same chain, same overrides — lab ANCOVA 1.2757 (SE 2.2149, n 429), reproduced by the Python replica of the engine's selection; reference A on TORIVA's CHG/BASE/ANL01FL 1.305 (SE 1.607). Recorded as
`p7_rerun_a806630` in `results.json`, stamped with the TORIVA commit and the fragment's hash. The
comparison against the built ADaM is in `comparison.md`, section *At `a806630`*.
