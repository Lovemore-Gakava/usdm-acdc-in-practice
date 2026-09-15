# Drafts for `cdisc-org/analysis-concepts` issues

Against `739344c` (2026-06-17). Not yet filed.

Originally two issues were planned (specification §12): the unused `censoring` role, and the
missing time-to-event transformations. **The first does not survive verification** — see
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

## Not filed

**The BC joint** ([F04](F04-bc-joint.md)) — originally thought unresolved. It is resolved;
`linkedBCIds` is populated on every measure terminal of the worked derivation scenario.
Withdrawn.

**`offset` is declared and unused** ([F02](F02-time-event-role-collision.md)) — true, but an
unused enum value with no consumer is not worth an issue on its own. Mentioned in Issue 1 as
precedent instead.
