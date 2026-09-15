# F07 — `best` and `worst` presuppose an ordering the metadata does not carry

**Status: new.** Found while mapping ORR on paper.

## Claim

`M.RecordSelection` can select the best record in a partition. Nothing anywhere says what
"best" means.

## Evidence

`M.RecordSelection` carries the configuration:

```json
{
  "name": "selection_rule",
  "dataType": "enum",
  "defaultValue": "last_non_missing",
  "enumValues": ["last_non_missing", "first_non_missing", "worst", "best",
                 "closest_to_target", "all_matching"],
  "description": "Rule for selecting record(s) within the partition"
}
```

`best` and `worst` are directional. Four of the six rules (`last_non_missing`,
`first_non_missing`, `all_matching`, and `closest_to_target` given its `target_value`) are
fully determined by the data and the configuration. Those two are not.

The method's single value input is:

```json
{ "name": "value", "dataType": "decimal", "required": true, "cardinality": "single" }
```

So "best" is undefined in two distinct ways:

1. **For a decimal**, best may be the maximum or the minimum. For a tumour shrinkage
   percentage it is the minimum; for a response rate the maximum. The method has no
   direction configuration and the formula —
   `<flag> := IF(<selection_rule>(<value>, <time_order>) OVER (<partition>+), 'Y', '')` —
   does not supply one.
2. **For an ordinal code** it is undefined entirely. RECIST 1.1 best overall response ranks
   CR ≺ PR ≺ SD ≺ PD ≺ NE. That ordering is clinical, standard, and wholly absent from the
   method, from `ACDC_Transformation_Library_v06.json`, and from
   `model/method/statistics_vocabulary.json`. The `value` role is typed `decimal`, so an
   ordinal code is not a valid input in the first place — yet `best` over response codes is
   the single most common use of best-record selection in oncology.

No derivation transformation upstream uses `selection_rule: best`, so the library provides no
worked example that would pin the semantics by demonstration.

## Why it matters

Step 2 of the ORR chain — best overall response across post-baseline assessments — composes
*syntactically*. `M.RecordSelection` with `selection_rule: best`, `scope: post_baseline`,
partitioned by Subject is the right shape, and it is satisfying to find that the primitive
exists. But two chains built that way, one ranking CR best and one ranking CR worst, are
identical in metadata and produce opposite results.

This is the same species as [F03](F03-chain-position-carries-meaning.md): the structure is
present, and the meaning that makes it correct is not. F03's distinguishing information at
least survived as prose in a `note` field. Here it is nowhere at all.

It also bears directly on the Part B signature design. A signature over
`usesMethod` + bindings + configurations captures `selection_rule: best` and stops there.
Two transformations with genuinely different clinical semantics hash identically.

## Suggestion

Either a `direction` configuration on `M.RecordSelection` for the numeric case, or — better,
since it generalises — an ordering declared on the concept or the parameter, so that
`best` resolves against a stated ranking rather than an assumed one. RECIST response ordering
is a property of the response scale, not of any one analysis, which argues for carrying it
with the concept.

Drafted as Issue 5 in [upstream-issues.md](upstream-issues.md), third in the suggested filing
order — real and demonstrable, but the fix involves a design choice, unlike
[F08](F08-no-risk-difference.md).
