# F03 — Chain position carries meaning that individual entries do not

**Status: confirmed, and stronger than originally stated.**

## Claim

`T.ADAS_SumAvailableScores` and `T.ADAS_MissingScaleCapacity` are structurally identical.
What separates them is what feeds them.

## Evidence

Comparing the two entries key by key, ignoring `oid`, `name`, `description`,
`composedPhrase` and `exampleInstance`, exactly one key differs: `bindings`.

Identical across both:

| Key | Value |
|---|---|
| `usesMethod` | `M.Aggregation` |
| `methodConfigurations` | `[{ "configurationName": "agg_func", "value": "sum" }]` |
| `methodOutputSlotMapping` | `null` |
| `sliceKeys` | `null` |
| `transformationType` | `derivation` |

And within `bindings`, all seven binding objects match on every machine-readable field —
`concept`, `methodRole`, `direction`, `dataStructureRole`, `conceptCategory`, `_layerNote`.

The **only** difference in the entire pair is the free-text `note` on the input binding:

```
A: "note": "11 ADAS-Cog item scores (from BCs)"
B: "note": "Per-row missing-capacity contribution from T.ADAS_MissingContribution
            (item_max_score when item is missing, else 0)"
```

## Why this is stronger than stated

The original finding said a signature computed over a transformation in isolation cannot
distinguish the two. That is true, but understates it: the distinguishing information is
**not structured at all**. It exists only as English prose in a `note` field. No signature
over any subset of the structured fields can separate them, because the structured fields
are byte-identical.

The repository's own tool reproduces this, and flags the pair as a false positive:

```
TRANSFORMATIONS — full signature (method + bindings + config values)
1 cluster(s) covering 2 of 25 entries
  152b97e6efa9  (2 entries)
      T.ADAS_MissingScaleCapacity
      T.ADAS_SumAvailableScores
```

The loose signature additionally pulls in `T.ADAS_NonMissingCount`, a third genuinely
distinct transformation.

## Consequence

Two, one immediate and one for Part B:

1. `tools/acdc_divergence.py` is trustworthy for methods (see §9.2 of the specification,
   verified: 2 clusters across 60 methods) and **not** trustworthy for transformations.
   It reports a 2-entry cluster that is a false positive.
2. A transformation signature must incorporate the provenance of its inputs — the
   derivation chain position — or divergence detection produces false positives on exactly
   the cases where the model is doing the most work. This corrects §9.3 of the specification,
   which originally proposed `usesMethod` + bindings + configurations.

## Reproduce

```
python3 tools/acdc_divergence.py --repo upstream/analysis-concepts --compare-naive
```
