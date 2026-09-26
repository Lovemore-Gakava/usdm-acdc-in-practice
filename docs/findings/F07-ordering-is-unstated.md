# F07 — `best` and `worst` presuppose an ordering the metadata does not carry

**Status: new, and amended.** Found while mapping ORR on paper. **Amended 2026-09-16 after
the lab tier**, which supplies a counter-example to this finding's own proposed fix — see
*The ordering is not always a property of the concept*, below.

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
worked example that would pin the semantics by demonstration. The position is in fact weaker
than that: `T.BaselineSelection` is the **only** transformation in the library that uses
`M.RecordSelection` at all, and it configures `last_non_missing`. Five of the six selection
rules are exercised by nothing — see [F11](F11-analysis-record-flag-has-no-transformation.md).

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

## The ordering is not always a property of the concept

Mapping the lab tier turned up a case that **breaks the suggestion this finding originally
made**, and it is recorded here rather than quietly dropped.

TORIVA's shift table (`programs/tfl/t_lb_01_shift.R`) selects the worst post-baseline
reference-range indicator per subject per parameter, and supplies its own ranking:

```r
nrind_order <- c("LOW" = 1, "HIGH" = 1, "NORMAL" = 0)
```

`LOW` and `HIGH` are collapsed to the same rank. "Worst" here means *abnormal in either
direction*, which is the right reading for a shift table and the wrong one for a directional
parameter — a haemoglobin analysis wants low to be worse than high, and the same `NRIND` scale
would then need a different ordering.

So the ordering is a property of **this analysis**, not of the `NRIND` concept. An ordering
declared on the concept — which the original suggestion below argued for, on the grounds that
RECIST ranking is a property of the response scale — would not capture it, and would give the
wrong answer if it were taken as authoritative.

Both cases are real. RECIST `CR ≺ PR ≺ SD ≺ PD ≺ NE` genuinely is a property of the scale;
`LOW = HIGH` genuinely is a property of one table. A fix has to allow the ordering to be
declared on the concept *and* overridden at the point of use, which is a larger design question
than the original suggestion implied.

## Suggestion

**As amended.** An ordering declared on the concept or parameter, with a per-transformation
override — so `best` and `worst` resolve against a stated ranking, the common ranking lives in
one place, and an analysis that needs a different one says so explicitly rather than silently
depending on the implementation.

The original suggestion was: *"Either a `direction` configuration on `M.RecordSelection` for
the numeric case, or — better, since it generalises — an ordering declared on the concept or
the parameter … RECIST response ordering is a property of the response scale, not of any one
analysis, which argues for carrying it with the concept."* The first half stands. The second
half is right for RECIST and wrong as a general rule, for the reason above.

Drafted as Issue 5 in [upstream-issues.md](../archive/upstream-issues.md), third in the suggested filing
order — real and demonstrable, but the fix involves a design choice, unlike
[F08](F08-no-risk-difference.md). The amendment above makes that design choice larger, and the
issue text was updated to match: **it must not be filed proposing concept-level ordering as a
complete fix.**

Closely related, and possibly the same issue: [F09](F09-record-selection-has-no-tiebreak.md),
which concerns what the ordering *is* rather than which direction it runs, on the same method.
