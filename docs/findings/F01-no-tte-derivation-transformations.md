# F01 — No time-to-event derivation transformations exist

**Status: confirmed** at upstream `739344c`.

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
2. Even given the predicates, the output shape does not fit. Every derivation method declares
   exactly one `computed_value` output class, and every one of the 14 derivation
   transformations emits exactly one output measure binding (verified by counting
   `direction == "output" && dataStructureRole == "measure"` per entry; `T.DeriveAnalysisVisit`
   emits zero, the other thirteen emit one).

   `AVAL`, `CNSR`, `ADT` and `EVNTDESC` are four projections of a **single** censoring
   resolution. Under a one-output-per-transformation model they must be derived by four
   independent passes, with nothing in the metadata constraining them to agree — an `AVAL`
   taken from the PD date and a `CNSR` of 1 are individually well-formed and jointly wrong.

The gap is therefore wider than missing library content. A TTE derivation is not expressible
as a transformation of the shape the model currently defines.

## Reproduce

```
python3 tools/acdc_divergence.py --repo upstream/analysis-concepts
```
