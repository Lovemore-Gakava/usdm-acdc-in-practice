# F06 — No general predicate exists over more than one variable

**Status: new.** Found while mapping PFS on paper. This is what blocks the complex tier.

## The hypothesis it disproves

Specification §5.3 proposed that the FDA 2018 censoring hierarchy is

> Expressible in principle as nested `M.ConditionalValue` over `M.RecordSelection`, at roughly
> the depth of the ADAS-Cog chain.

It is not. `M.ConditionalValue` is not a general conditional.

## Evidence

`M.ConditionalValue`'s predicate is hardwired to missingness. It takes no condition
configuration at all:

```json
"description": "Per-row conditional. If the input value is NA (missing), output the
                alternate value; else output the configured base value (default 0).",
"formula": { "generic_expression": "result := IF(IS_NA(<value>), <alternate>, <base>)" },
"configurations": [
  { "name": "base", "dataType": "decimal", "defaultValue": 0,
    "description": "Value emitted when the input is NOT missing" }
],
"input_roles": [
  { "name": "value",     "dataType": "decimal", "description": "Per-row value tested for missingness (NA)" },
  { "name": "alternate", "dataType": "decimal", "description": "Per-row replacement value used when value is NA" }
]
```

The only predicate it can express is `IS_NA(value)`. It cannot express *PD date ≤ data
cut-off*, or *therapy start < PD date*, or any other branch in the hierarchy.

The two methods that *do* carry a predicate are both confined to a single input:

| Method | Formula | Predicate reach |
|---|---|---|
| `M.ThresholdCompare` | `result := IF(<value> <operator> <threshold>, <true_value>, <false_value>)` | one input vs a **constant** `threshold` (`decimal`) |
| `M.Categorization` | `result := CASE WHEN <conditions> THEN <categories> ELSE <default_category> END` | `conditions` is a free-text string over the single `value` input |

Every one of the three declares exactly one `value` input role. A predicate relating **two
variables** — which is what every branch of the censoring hierarchy is — has nowhere to live.

`M.Categorization.conditions` is additionally typed `string`, with an example
(`'value < 30, value < 70, value >= 70'`) rather than a grammar. Conditions are opaque text:
not parseable, not checkable, and outside the reach of any signature — a governance problem
for Part B independent of this one.

## The four blockers, in full

Mapping PFS against SAP §4.2 / §13.5 turns up four, of which the predicate gap is the first.

**B1 — No multi-variable predicate.** Above. Blocks every branch of the hierarchy.

**B2 — Date-typed values have no home.** `M.RecordSelection.value`, `M.Aggregation.value`,
`M.Categorization.value` and `M.ThresholdCompare.value` are all `dataType: "decimal"`.
The only `date`-typed roles in the whole method library are `M.DateDifference.start_date`
and `.end_date`. "Earliest BICR PD date" and "last adequate assessment date" are
date-valued selections with no type-correct method. They can be done by encoding dates as
numbers, which discards the type distinction the schema otherwise maintains.

**B3 — One decision, four columns, no coordination.** See
[F01](F01-no-tte-derivation-transformations.md). `AVAL`, `CNSR`, `ADT` and `EVNTDESC` are
four projections of one resolution; the model gives one output slot per transformation.

**B4 — No sequence or gap operator.** SAP §4.2 censors at the last adequate assessment
before *≥2 consecutive missed scheduled assessments*. `M.WindowLookup` (`window_func`,
`offset`, `order_by`) can reach a neighbouring **row that exists**. Detecting a *missing*
scheduled visit requires comparing actual assessments against the planned visit calendar —
a second input, and a sequence comparison. Neither is expressible.

## Incidental: `M.RecordSelection` output is internally inconsistent

Its formula emits a flag:

```
<flag> := IF(<selection_rule>(<value>, <time_order>) OVER (<partition>+), 'Y', '')
```

while its `output_specification` declares a `computed_value` with statistic `value`. A
consumer binding to the declared output gets a value; a consumer reading the formula gets
`'Y'`/`''`. Minor, and worth raising alongside the rest.

## Disposition

This is the negative result the complex tier existed to produce. Per the method, a negative
result at the complex tier is a finding rather than a failure — but it lands earlier than
expected, on paper, before any authoring. See
[endpoints/03-complex-pfs/mapping.md](../../endpoints/03-complex-pfs/mapping.md).

Proposed upstream as an issue, with the PFS chain as the motivating case. See
[upstream-issues.md](upstream-issues.md).
