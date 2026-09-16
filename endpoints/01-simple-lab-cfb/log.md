# Lab change from baseline — authoring log

Step 4 of the method: what the authoring actually cost, and every point where a decision was
needed.

**Authored 2026-09-16** against `ac-dc-app` at upstream `739344c`, served locally
(`python ac-dc-app/serve.py`). Endpoint: CDISC Pilot **END5, *"Laboratory evaluations (Change
from Baseline)"***. Result: [`chain.json`](chain.json).

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

### L1 — the study is not the study

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

### L5 — no BC linking was required to finish

`endpointSpecs.Endpoint_5.linkedBCIds` is `[]` in the serialised instance, and the pipeline still
reported complete. F04 established that BC linkage lives at terminal level and is populated in
the shipped worked scenario; here it simply was not demanded to reach a finished state. Not
pursued further — it would need a second pass with the BC picker, and it does not bear on the
step-3 comparison.

---

## What this tier cost, in one line

**Zero authoring, eleven decisions, four of them unguided by the SAP, and a chain that
completes while being wrong by a median 21% on the value it subtracts.**

## What it says about scale

Specification §6.1 asks whether ten to fifty endpoints can go through this. On the evidence of
the shallowest tier: the *mechanical* cost is genuinely low — no new transformations, no
configuration, eleven clicks. The cost that would not scale is **L4**. If a chain can validate
while under-determined, then every endpoint needs the step-3 check that caught it, and that
check is bespoke per endpoint and needs the built data.

The measurement worth carrying forward is therefore not "eleven decisions per endpoint" but
"one dataset-level correctness check per endpoint, none of which the framework provides."
