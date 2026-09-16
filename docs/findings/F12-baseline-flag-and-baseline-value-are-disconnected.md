# F12 — The baseline flag and the baseline value are disconnected

**Status: new.** Found by running the builder on 2026-09-16, recorded as B11 in the lab tier's
mapping. Verified structurally against upstream `739344c`.

## Claim

`T.BaselineSelection` produces `ABLFL`. `T.ChangeFromBaseline` needs the baseline *value*.
Nothing connects them, and nothing can: the pipeline matches derivations to dependencies by
output concept, and a `Flag` is not a `Measure`. The baseline value is reached instead by
constraining `AnalysisVisit`, which makes it a **visit-based** definition where the SAP's is
**date-based**.

## How this was found

`ac-dc-app` was served and driven: CDISC Pilot study → endpoint **END5, *"Laboratory
evaluations (Change from Baseline)"*** → concept category `Change (Comparison)` → analysis
template *Change From Baseline ANCOVA* → derivation pipeline.

The pipeline asks the author to resolve `AVAL/AVALC/BASE (Measure)` for the `subtrahend` of
`T.ChangeFromBaseline` and offers **nine** templates:

```
LOCF Imputation · ADAS-Cog Item Max Score · ADAS-Cog Per-Item Missing-Capacity Contribution ·
ADAS-Cog Missing Scale Capacity · ADAS-Cog Scoreable Fraction · ADAS-Cog Sum of Available
Item Scores · ADAS-Cog Non-Missing Item Count · ADAS-Cog (11) Total Score · Unit Conversion
```

`T.BaselineSelection` is not among them. To resolve *the baseline value*, the builder offers
LOCF imputation, seven ADAS-Cog helpers and a unit conversion.

## Why — the mechanism, not the accident

`js/utils/transformation-linker.js`:

```js
export function findDerivationsForConcept(concept, library) {
  return (library.derivationTransformations || [])
    .filter(d => getOutputConcept(d) === concept);
}
```

Exact string equality on the output concept. Grouping the 14 derivation transformations by
what they output:

| Output concept | n | Transformations |
|---|---|---|
| `Measure` | 9 | `T.LOCF_Imputation`, the seven ADAS-Cog entries, `T.UnitConversion` |
| `Flag` | 2 | **`T.BaselineSelection`**, `T.ADAS_ScoreableCheck` |
| `Change` | 1 | `T.ChangeFromBaseline` |
| `AnalysisVisit` | 1 | `T.DeriveAnalysisVisit` |
| `PeakValue` | 1 | `T.PeakConcentration` |

The nine offered are exactly the nine that output `Measure`. `T.BaselineSelection` outputs
`Flag`, so it can never be a candidate for a `Measure` dependency. This is structural and
reproducible without the application.

## How the baseline value is actually reached

Through `T.ChangeFromBaseline`'s slice, which the builder renders as an inherited constraint on
the subtree:

```
inherited slice: parameter_baseline — scopes this subtree's inputs
  Parameter      {parameter}
  AnalysisVisit  Baseline
```

So `BASE` is *the value at the visit labelled Baseline*. `ABLFL` is *the flag on the last
non-missing pre-treatment record*. **Nothing in the metadata requires these to be the same
record.**

### And the two definitions are not the same definition

SAP §12.3 is explicit that TORIVA's baseline is not visit-based:

> The selection is **date-based, not visit-based**: the reference value is whichever assessment
> is last before treatment — a Screening draw *or* a Cycle 1 Day 1 pre-dose draw — regardless
> of the collected `VISIT`.

The concept model can express the visit-based form and not the date-based one. They coincide
only because `adlb.R` forces them to:

```r
# 6b. Baseline analysis visit — the ABLFL='Y' record is the baseline visit
# (AVISIT="Baseline", AVISITN=0) per CDISC ADaM convention, regardless of the
# window its ADY falls in (a C1D1 pre-dose draw windows to C1D1). SAP §12.3.
adlb <- apply_baseline_visit(adlb)
```

That one call is the entire bridge between the flag and the value. Its equivalent is what the
concept model does not carry — and the lab tier's mapping originally read the slice's use of
`AnalysisVisit` as an elegant joint, which is the opposite of what it is.

## The same shape in three places now

`AVAL`/`CNSR`/`ADT`/`EVNTDESC` ([F01](F01-no-tte-derivation-transformations.md)), `ANL01FL`
against `ABLFL` ([F11](F11-analysis-record-flag-has-no-transformation.md)), and now `ABLFL`
against `BASE`: several projections of one decision, with nothing in the metadata requiring
them to agree. F01 is a time-to-event problem and F11 an analysis-flag problem; this one is on
change from baseline, the simplest derivation in the library and the one the specification
expected to work with no new authoring.

## Incidental, and worse: every `Flag` is interchangeable

Since matching is by concept string, `T.BaselineSelection`'s `Flag` output **is** a valid
candidate for any dependency that needs a `Flag`. Three transformations do:

```
T.ADAS_Cog_11_TotalScore   (scoreable check)
T.OS_LogRank               (event indicator)
T.Responder_ChiSq          (responder flag)
```

So the builder will offer *baseline record flag* as a way to resolve **the event indicator of a
log-rank test** and **the responder flag of a chi-squared test**. Both are clinically absurd and
neither is prevented by anything in the model.

This is [F02](F02-time-event-role-collision.md) arriving operationally. F02 argued that
`time` and `event` are indistinguishable to any tooling reasoning over roles, and was written as
a signature-identity concern for Part B. Concept-level matching turns it into an authoring
hazard in the shipped builder: the concept vocabulary is too coarse to say what a flag *is*.

## Incidental: three demanded concepts have no producer

Counting measure-role input bindings across all 25 transformations against what the 14
derivations can output:

| Demanded concept | Needed by | Producible? |
|---|---|---|
| `Measure` | 21 | yes |
| `Flag` | 3 | yes |
| `Change` | 2 | yes |
| `Observation` | 1 | **no** |
| `Timing` | 1 | **no** |
| `TimeToEvent` | 1 | **no** |

`TimeToEvent` is demanded by `T.OS_LogRank` and produced by nothing — which is
[F01](F01-no-tte-derivation-transformations.md) restated structurally, and an independent
confirmation of its surviving core.

## Scope

Not a missing library entry. `T.BaselineSelection` is correct as written — `ABLFL` genuinely is
a flag. The gap is that the model has no way to say *"the value on the record this flag marks"*,
which is how ADaM defines `BASE` and how every SAP that defines a date-based baseline means it.

Fixing it needs either a reference from one derivation to another's selected records, or a
slice constraint expressible over a flag rather than only over a dimension. Both are larger than
a new `T.` entry, and the second looks closer to the existing design.

## Reproduce

```
python -c "
import json
from collections import defaultdict
lib=json.load(open('upstream/analysis-concepts/lib/transformations/ACDC_Transformation_Library_v06.json',encoding='utf-8'))
der=lib['derivationTransformations']
def out(t):
    b=next((b for b in t['bindings'] if b.get('direction')=='output'),None)
    return (b or {}).get('concept') or t.get('outputConcept')
by=defaultdict(list)
for t in der: by[out(t)].append(t['oid'])
for c,ts in sorted(by.items()): print(f'{c:<16}{len(ts):>3}  {ts}')
"
```

Expected at `739344c`: `Measure` 9, `Flag` 2 (including `T.BaselineSelection`), `Change` 1,
`AnalysisVisit` 1, `PeakValue` 1 — so the nine candidates the builder offers for a `Measure`
dependency are the nine `Measure` producers, and `T.BaselineSelection` is not one of them.

The matching rule itself is `findDerivationsForConcept` in
`ac-dc-app/js/utils/transformation-linker.js:134-137`.
