# Drafts for `cdisc-org/analysis-concepts` issues

Against `739344c` (2026-06-17). Not yet filed.

Originally two issues were planned (specification §12): the unused `censoring` role, and the
missing time-to-event transformations. There are now five, three of them from mapping endpoints
on paper rather than from inspecting the libraries. **The first does not survive verification** — see
[F02](F02-time-event-role-collision.md); there is no `censoring` role. It is replaced below
by the role-collision issue, which is the defensible part of the same concern.

Before filing, check the `estimands_01` branch (Stuart Malcolm, 2026-08-14, unmerged at the
pinned commit) and issue #11 — that work covers ICH E9(R1) strategies and touches the same
survival bindings, so some of this may already be in flight.

---

## Issue 1 — `time` and `event` are indistinguishable in method metadata

**Type:** metadata / schema

`M.KaplanMeier`, `M.CoxPH` and `M.LogRankTest` each declare `time` and `event` with
`statisticalRole: "response"`. The distinction is carried only by position in
`formula.generic_expression` — `Surv(<time>, <event>) ~ <fixed_effect>`.

This works for execution. It does not work for any tooling that reasons over roles: two
inputs with identical `statisticalRole`, `dataType` and `cardinality` are interchangeable as
far as the metadata is concerned, so swapping them yields an identical signature and a
nonsense analysis.

Concretely, this blocks content-addressable identity for survival methods — the basis for
duplicate detection and for versioning against a breaking-change rule.

**Suggestion.** Either add a value to the `StatisticalRole` enum distinguishing the event
indicator from the time response, or mark the distinction on the input role itself. The enum
already carries `offset`, which no method uses, so there is precedent for roles that describe
a slot's meaning rather than its model position.

---

## Issue 2 — Derivation methods cannot express a predicate over two variables

**Type:** method library gap
**Motivating case:** FDA 2018 censoring hierarchy for PFS

Three methods carry a conditional:

| Method | Predicate |
|---|---|
| `M.ConditionalValue` | hardwired: `IF(IS_NA(<value>), <alternate>, <base>)`, no condition configuration |
| `M.ThresholdCompare` | one input against a **constant** `threshold` (`decimal`) |
| `M.Categorization` | `conditions`, a free-text `string` over the single `value` input |

Each declares exactly one `value` input role. A predicate relating two variables — *PD date
≤ data cut-off*, *therapy start < PD date* — cannot be expressed by any of them.

This blocks any censoring hierarchy, and with it all six ADTTE parameters (OS, OSWOT, PFS,
PFSINV, DOR, TTR) on a standard oncology trial.

Related: `M.Categorization.conditions` is typed `string` with an example rather than a
grammar, so conditions are not parseable or checkable even where they fit.

**Suggestion.** A derivation method taking two (or n) value inputs plus a comparison
operator — effectively `M.ThresholdCompare` with the threshold as an input role rather than
a configuration — would unblock most of the hierarchy.

---

## Issue 3 — No time-to-event derivation transformations, and the output shape may not admit them

**Type:** transformation library gap
**Depends on:** Issue 2

The transformation library holds 14 derivation transformations. None produces `AVAL` or
`CNSR` — the strings `CNSR`, `censor` and `AVAL` do not appear in
`ACDC_Transformation_Library_v06.json` at all. `T.OS_LogRank` binds `time` (concept
`TimeToEvent`) and `event` (concept `Flag`) as **inputs**, so the survival chain begins
already derived, with nothing upstream deriving it.

The methods to close this look present at first — `M.DateDifference`, `M.RecordSelection`,
`M.Aggregation` — but two structural issues sit behind them:

1. **Predicates.** Issue 2. The hierarchy cannot be expressed.
2. **Output cardinality.** Every derivation method declares exactly one `computed_value`
   output class, and all 14 derivation transformations emit at most one output measure
   binding. `AVAL`, `CNSR`, `ADT` and `EVNTDESC` are four projections of a *single* censoring
   resolution. Deriving them as four independent transformations leaves nothing in the
   metadata requiring them to agree — an `AVAL` from the PD date paired with `CNSR = 1` is
   individually well-formed and jointly wrong.

**Question for maintainers, before proposing entries.** Is a transformation intended to be
able to emit multiple coordinated output measures, or is a TTE derivation meant to be
modelled some other way — for example as one transformation per column sharing a slice key?
The answer determines whether this is a library gap or a model gap.

We have the PFS chain mapped against a public simulated study and are happy to contribute
the `T.` entries once the shape is settled.

---

## Issue 4 — No difference-of-proportions statistic exists

**Type:** statistics vocabulary / method gap
**Motivating case:** ORR with a Mantel–Haenszel risk difference summary

`M.CMH` declares three output classes:

| Output class | Statistics |
|---|---|
| `test_result` | `chi_squared`, `p_value`, `df` |
| `association_measures` | `odds_ratio`, `CI_lower`, `CI_upper` |
| `homogeneity_test` | `chi_squared`, `p_value`, `df` |

It yields an odds ratio. There is no risk difference, and no other method supplies one. The
proportion-related entries in `model/method/statistics_vocabulary.json` are `proportion`, `pct`,
`cumulative_pct`, `odds_ratio` and `n_risk` — no difference of proportions, no risk difference,
no rate difference.

A stratified Mantel–Haenszel **risk difference** with 95% CI is a routine population-level
summary for a binary endpoint, and it is what the study we mapped specifies for objective
response rate. Reporting the odds ratio instead is not an approximation: under ICH E9(R1) the
population-level summary is an attribute of the estimand, so the two answer different questions.
Since the framework binds to USDM `Estimand` as a first-class class, this is arguably something
the model should be able to detect and report rather than something an author silently works
around.

`M.Proportion` covers the per-arm side well — `proportion`, `pct`, `CI_lower`, `CI_upper`, with a
`ci_method` configuration offering `exact_clopper_pearson`, `wilson`, `wald`, `agresti_coull` and
`jeffreys`. It simply does not contrast groups.

**Suggestion.** Add a difference-of-proportions statistic to the vocabulary and either extend
`M.CMH`'s `association_measures` output class or add a companion method for the stratified
difference. This looks like the smallest and most self-contained of the gaps reported here.

**Related, minor:** neither `M.CMH` nor `M.Proportion` has a transformation entry. The only
responder analysis transformation is `T.Responder_ChiSq`, which uses `M.ChiSquaredTest` and binds
`response` to concept `Flag` as an input — the same already-derived shape as `T.OS_LogRank` in
Issue 3. That is ordinary library work rather than a model gap, since the methods exist.

---

## Issue 5 — `best` and `worst` presuppose an ordering that is never declared

**Type:** method semantics
**Motivating case:** RECIST 1.1 best overall response

`M.RecordSelection.selection_rule` offers:

```json
"enumValues": ["last_non_missing", "first_non_missing", "worst", "best",
               "closest_to_target", "all_matching"]
```

Four of these are fully determined by the data and configuration. `best` and `worst` are not,
and nothing in the method, the transformation library or the statistics vocabulary supplies the
missing ordering:

1. **For a decimal**, `best` may be the maximum or the minimum — the minimum for tumour
   shrinkage, the maximum for a response rate. There is no direction configuration, and the
   formula `<flag> := IF(<selection_rule>(<value>, <time_order>) OVER (<partition>+), 'Y', '')`
   does not supply one.
2. **For an ordinal code** it is undefined entirely. RECIST 1.1 ranks CR ≺ PR ≺ SD ≺ PD ≺ NE.
   That ordering is standard and clinical and appears nowhere in the model. The `value` input
   role is `dataType: "decimal"`, so a response code is not a valid input at all — yet `best`
   over response codes is the most common use of best-record selection in oncology.

No derivation transformation upstream uses `selection_rule: best`, so there is also no worked
example that would pin the semantics by demonstration.

The practical effect: best overall response composes as a single configured `M.RecordSelection`,
which is a genuinely good outcome — but two chains built that way, one ranking CR best and one
ranking CR worst, are identical in metadata and produce opposite results.

**Suggestion.** Either a `direction` configuration on `M.RecordSelection` for the numeric case,
or — better, because it generalises — an ordering declared on the concept or parameter, so that
`best` resolves against a stated ranking. RECIST response ordering is a property of the response
scale rather than of any one analysis, which argues for carrying it with the concept.

---

## Suggested filing order

Five issues at once is a lot to arrive with. If they are filed in stages:

| Order | Issue | Why |
|---|---|---|
| 1 | **4** — no risk difference | Smallest, most concrete, verifiable in one file, and the fix is obvious. The best opener |
| 2 | **1** — time/event role collision | Also concrete and narrow; the `offset` precedent makes the suggestion easy to act on |
| 3 | **5** — undeclared ordering | Real and demonstrable, but the fix involves a design choice |
| 4 | **2** — no multi-variable predicate | The largest capability gap. Worth filing once the smaller ones have established the work is real |
| 5 | **3** — TTE transformations | Depends on 2, and opens with a question rather than a proposal |

---

## Not filed

**The BC joint** ([F04](F04-bc-joint.md)) — originally thought unresolved. It is resolved;
`linkedBCIds` is populated on every measure terminal of the worked derivation scenario.
Withdrawn.

**`offset` is declared and unused** ([F02](F02-time-event-role-collision.md)) — true, but an
unused enum value with no consumer is not worth an issue on its own. Mentioned in Issue 1 as
precedent instead.
