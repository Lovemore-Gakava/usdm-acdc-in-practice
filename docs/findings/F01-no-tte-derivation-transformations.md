# F01 — No time-to-event derivation transformations exist

**Status: confirmed in part; the output-cardinality argument is corrected.** The library gap
is real and unchanged. The claim that the *model* cannot admit a multi-output derivation is
**false**, and was corrected on 2026-09-16 while mapping the lab tier. See
*The output-shape argument was wrong*, below.

## Claim

The transformation library contains nothing that produces `AVAL` and `CNSR`.
`T.OS_LogRank` consumes time and event as though already derived.

## Evidence

The library holds 14 derivation transformations and 11 analysis transformations:

```
derivation: T.BaselineSelection, T.ChangeFromBaseline, T.LOCF_Imputation,
            T.PeakConcentration, T.ADAS_ItemMaxScore, T.ADAS_MissingContribution,
            T.ADAS_MissingScaleCapacity, T.ADAS_ScoreableFraction,
            T.ADAS_SumAvailableScores, T.ADAS_NonMissingCount,
            T.ADAS_ScoreableCheck, T.ADAS_Cog_11_TotalScore,
            T.UnitConversion, T.DeriveAnalysisVisit
analysis:   T.CFB_MMRM_Primary, T.CFB_ANCOVA, T.OS_LogRank, T.Count_Measure,
            T.Mean_Measure, T.SD_Measure, T.Median_Measure, T.Quartile_Measure,
            T.Min_Measure, T.Max_Measure, T.Responder_ChiSq
```

String frequency across the whole of `ACDC_Transformation_Library_v06.json`:

| Token | Occurrences |
|---|---|
| `CNSR` | 0 |
| `censor` / `Censor` | 0 |
| `AVAL` | 0 |
| `TimeToEvent` | 2 |

Both `TimeToEvent` occurrences are in `T.OS_LogRank`, as an **input** binding:

```json
"bindings": [
  { "methodRole": "time",  "concept": "TimeToEvent", "requiredValueType": "Quantity",        "direction": "input" },
  { "methodRole": "event", "concept": "Flag",        "requiredValueType": "CodeableConcept", "direction": "input" }
]
```

So the survival chain begins already derived. Nothing upstream produces either input.

## Where the gap is

Not at the method or schema layer. `M.DateDifference`, `M.RecordSelection`,
`M.ConditionalValue`, `M.ThresholdCompare`, `M.Aggregation` and `M.WindowLookup` all exist.

The original reading of this finding was that closing the gap means authoring three or four
new `T.` entries. **That reading is wrong**, for two reasons established while mapping PFS:

1. The available methods cannot express the censoring hierarchy at all — see
   [F06](F06-no-general-predicate.md).
2. The output shape is a narrower obstacle than this finding originally claimed — see below.

## The output-shape argument was wrong

This finding originally asserted:

> Every derivation method declares exactly one `computed_value` output class, and every one of
> the 14 derivation transformations emits exactly one output measure binding.

The first clause is false, and the second is contradicted by its own parenthetical (which said
`T.DeriveAnalysisVisit` emits zero and the other thirteen emit one — so "at most one", not
"exactly one").

Counting output classes across the 21 derivation methods at `739344c`:

| Output classes | Methods |
|---|---|
| 1 | 19 |
| 2 | `M.UnitConversion` → `result_value`, `result_unit` |
| 3 | `M.WindowedVisitAssignment` → `analysisVisit`, `analysisVisitNumber`, `analysisDay` |

**A derivation method can declare several coordinated outputs, and two do.** Both are bound
through to transformations. `T.DeriveAnalysisVisit` emits all three of its method's outputs —
two dimensions and an attribute — from one windowing decision. `T.UnitConversion` is closer
still to what a TTE derivation needs:

```json
{ "concept": "Measure", "qualifierType": "facet", "qualifierValue": "result.value",
  "direction": "output", "dataStructureRole": "measure",   "methodRole": "result_value" },
{ "concept": "Measure", "qualifierType": "facet", "qualifierValue": "result.unit",
  "direction": "output", "dataStructureRole": "attribute", "methodRole": "result_unit",
  "note": "Unit of the derived Measure … propagated so downstream derivations/analyses can
           read the Measure's unit without re-reading config." }
```

Two coordinated **facets of one `Measure` concept**, emitted together from a single method,
one as a measure and one as an attribute. That is a mechanism for exactly the problem the
original argument said the model lacked.

### What actually survives

The narrow count holds: **no derivation transformation emits more than one output binding whose
`dataStructureRole` is `measure`** — thirteen emit one, `T.DeriveAnalysisVisit` emits none.

So the accurate statement is not "the model cannot express a coordinated multi-output
derivation". It is: *the model expresses coordination through facets and non-measure outputs,
and there is no precedent for a derivation emitting several coordinated outputs that are each a
measure in their own right.*

Whether `AVAL`, `CNSR`, `ADT` and `EVNTDESC` need to be four measures, or are better modelled
as one `Measure` with `CNSR`/`ADT`/`EVNTDESC` as facets in the manner of `result.unit`, is a
**modelling question with a plausible upstream answer already in the library** — not a wall.

### Consequence

The gap is library content plus [F06](F06-no-general-predicate.md), and is narrower than this
finding claimed. `upstream-issues.md` Issue 3 was rewritten accordingly: it now cites
`T.UnitConversion`'s facet pattern and asks whether that is the intended shape for a TTE
derivation, instead of asserting that the model forbids one.

Had the original text been filed, it would have told the maintainers their model cannot do
something it demonstrably does, in a library entry the same finding already cites by name.
That is the third time verification has caught a wrong premise here, after F02 and F04.

## Reproduce

```
python3 tools/acdc_divergence.py --repo upstream/analysis-concepts
```
