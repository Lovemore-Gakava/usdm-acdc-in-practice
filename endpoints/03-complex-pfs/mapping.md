# PFS — chain mapped on paper

Step 1 of the method: map the chain against the SAP text **before** opening the builder.
Nothing was authored before this document was written.

**Sources.** TORIVA-LUNG 301 at `8534339d`: SAP §4.2 (endpoint derivation), §13.5 (estimand E2),
`programming-specs/ADTTE-spec.md` v0.3. Upstream at `739344c`.

**Verdict: it does not compose.** Four blockers, three of them structural. Detail in
[F06](../../docs/findings/F06-no-general-predicate.md).

---

## What the SAP asks for

SAP §4.2, PFS (Secondary S1), estimand E2:

- **Start:** `RANDDT`
- **Event:** earliest of — BICR progression (`RS.RSSTRESC = "PD"` where `RSEVAL = "INDEPENDENT ASSESSOR"`), or death (`DTHDT`)
- **Censor,** per FDA 2018 guidance:
  1. No events → last adequate tumour assessment date, `max(RS.RSDTC)` with non-missing response
  2. New anti-cancer therapy before PD → last adequate assessment **before** therapy start
  3. ≥2 consecutive missed scheduled assessments before PD → last adequate assessment before the gap

Target: ADTTE `PARAMCD = "PFS"`, producing `AVAL` (days), `CNSR` (0/1), `ADT`, `EVNTDESC`, `STARTDT`.

## The chain as it would have to be built

| # | Step | Method | Composes? |
|---|---|---|---|
| 1 | Earliest BICR PD date | `M.RecordSelection` | **No** — B2, date-valued |
| 2 | Death date | `M.RecordSelection` | **No** — B2 |
| 3 | Last adequate assessment date | `M.Aggregation` (`agg_func: max`) | **No** — B2 |
| 4 | Therapy start before PD? | — | **No** — B1, two-variable predicate |
| 5 | ≥2 consecutive missed visits? | — | **No** — B4, no sequence operator |
| 6 | Resolve event vs censor | `M.ConditionalValue` ×4 nested | **No** — B1, predicate is `IS_NA` only |
| 7 | `ADT` ← resolved date | (from 6) | blocked by 6 |
| 8 | `AVAL` ← `ADT − STARTDT` | `M.DateDifference` (`unit: days`) | **Yes** |
| 9 | `CNSR` ← 0/1 | (from 6) | blocked by 6 |

One step of nine composes.

> **Corrected 2026-09-16 — none of nine is *authorable*.** Step 8's `M.DateDifference` has no
> transformation entry, so it cannot be selected in the builder. This mapping, like ORR's, was
> scored against the **method** library; the builder authors from the **transformation** library,
> where 65% of methods have no entry. See
> [F13](../../docs/findings/F13-authoring-surface-is-narrower-than-the-model.md). The verdict
> "does not compose" is unchanged and now understated.

## The blockers

**B1 — no multi-variable predicate.** Step 6 is the FDA hierarchy: a five-way resolution
branching on *relations between variables* (PD date ≤ DCO; therapy start < PD date; gap ≥ 2
visits). `M.ConditionalValue`'s predicate is hardwired to `IS_NA(value)`; `M.ThresholdCompare`
compares one input against a **constant**; `M.Categorization` takes conditions over a single
`value` input as free text. There is no method whose predicate can reference two variables.

Specification §5.3 assumed this composed as nested `M.ConditionalValue`. It does not.

**B2 — dates are not a value type for selection.** Steps 1–3 select and aggregate *dates*.
Every selection and aggregation method types `value` as `decimal`; the only `date` roles
upstream are `M.DateDifference.start_date` / `.end_date`. Workable by encoding dates as
numerics, at the cost of the type distinction.

**B3 — one decision, four columns.** Steps 7–9 plus `EVNTDESC` are four projections of the
single step-6 resolution. Each derivation transformation emits one output measure, so each
would re-run the hierarchy independently, with nothing requiring the four to agree.

**B4 — no sequence or gap operator.** Step 5 needs actual assessments compared against the
*planned* visit calendar. `M.WindowLookup` reaches neighbouring rows that exist; it cannot
detect an absent scheduled visit.

## Two discrepancies in the source study

Surfaced by the mapping, and to be resolved at comparison time against the built ADaM —
not here, since resolving them by inspection before authoring would contaminate step 3.

**D1 — time origin.** SAP §4.2 says `Start: RANDDT` (randomisation). `ADTTE-spec.md` says
`STARTDT` = `TRTSDT` (first dose) for OS/OSWOT/PFS/PFSINV/TTR, and `AVAL = ADT − STARTDT`.
These differ by the randomisation-to-first-dose interval. SAP §13.5 also states the variable
is *"Time (months) from randomisation"* while ADTTE stores days with `AVALU = "DAYS"`.

Relevant to the model: `M.RecordSelection.reference_event` defaults to `first_dose` and its
description names the randomisation date as the alternative — so the model represents this
choice explicitly, which is a point in its favour. The chain would have forced the question.

**D2 — estimator.** SAP §4.2 and §13.5 both specify `admiral::derive_param_tte()` with
`event = pd_event + death_event`, `censor_conditions = list(lasta_censor, rand_censor)`.
`ADTTE-spec.md` v0.3 (2026-07-24) records *"removed stale `derive_param_tte()` references
(code uses explicit logic)"*. The SAP was not updated to match.

D2 is the more interesting of the two for this project: the SAP delegates the censoring
hierarchy to a named library function, and the implementation then diverged from it silently.
That is exactly the opacity a declarative concept model is supposed to remove — and B1–B4 are
the reason it currently cannot.

## What this means for the tier

The complex tier finds the limit, as designed, but finds it **earlier than expected** — on
paper, before authoring. There is consequently no authoring-cost measurement for this tier,
because there is no authoring to do. The measurement that replaces it is the gap list above.

Steps 2 through 4 of the method (`chain.json`, `comparison.md`, `log.md`) are blocked for PFS
pending either an upstream change or a documented workaround. Proposed `T.` entries and the
methods they would need go in `transformations/proposed/`.

**This does not block the simple tier.** Lab change-from-baseline uses `T.BaselineSelection`
and `T.ChangeFromBaseline`, both of which exist.

> **Corrected after mapping ORR.** This section originally predicted that ORR would hit B1
> *"less severely."* It does not. ORR hits the same blocker on its primary derivation — the
> confirmation rule is a two-record predicate — and turns up two further gaps, F07 and F08.
> See [../02-moderate-orr/mapping.md](../02-moderate-orr/mapping.md). The prediction was
> speculation and is left visible rather than deleted.
