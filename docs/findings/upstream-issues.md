# Drafts for `cdisc-org/analysis-concepts` issues

Against `739344c` (2026-06-17). Not yet filed.

Originally two issues were planned (specification §12): the unused `censoring` role, and the
missing time-to-event transformations. There are now five, three of them from mapping endpoints
on paper rather than from inspecting the libraries. **The first does not survive verification** — see
[F02](F02-time-event-role-collision.md); there is no `censoring` role. It is replaced below
by the role-collision issue, which is the defensible part of the same concern.

**Issues 3 and 5 were both rewritten on 2026-09-16**, after the lab tier disproved a premise in
each. Issue 3 previously asserted that every derivation method declares exactly one output
class, which is false — `M.UnitConversion` and `M.WindowedVisitAssignment` declare two and
three ([F01](F01-no-tte-derivation-transformations.md)). Issue 5 previously proposed
concept-level ordering as the fix, which one of the study's own tables contradicts
([F07](F07-ordering-is-unstated.md)). Both would have been filed telling the maintainers
something untrue about their own library.

## The state of the upstream repository, checked 2026-09-16

This replaces an earlier note that said to check the `estimands_01` branch and issue #11 before
filing. Both were checked; here is what is there.

| | |
|---|---|
| `main` | **Has not moved since 2026-06-17** — the pinned commit `739344c` is the tip. Every finding here is against current `main` |
| `estimands_01` | Active, and well past the commits F02 cites. Now carries a large `smartphrase/` subtree, merged through PR #14 |
| Issue #11 | **Closed** (2026-08-19), with #12 and #13 |
| Open issues | **One**: #9, *"Smartphrase: demonstrate SAP ↔ AC/DC model linkage (PoC for the working group)"* |
| Issues ever opened | **Four**, all by the same maintainer (`metadatadriven`) |

**Nothing here is duplicated by that work.** The branch adds *smartphrases* — estimand and
intercurrent-event language — not methods. There is no `risk_difference`, no multi-variable
predicate, no declared ordering anywhere on it.

Three things follow that should shape how these are filed.

**1. The tracker is very small.** Four issues in the repository's lifetime, one open, one active
maintainer. Filing five at once would more than double its lifetime volume and would read as an
audit rather than a contribution. **File one, wait, and see how it is received.**

**2. State requirements, not solutions.** Issue #9's body carries a rework note from the
maintainer:

> The original body specified solution choices … before the requirements were stated, and the
> first round of work on branch `smartphrase_01` followed those choices in the wrong direction.
> This body now states **requirements only**; solution de…

Every draft below leads with a **Suggestion**. That is the shape the maintainer has explicitly
said sent work in the wrong direction on their own issue. The suggestions should move to the
end, be marked as optional, or come out.

**3. They are about to hit Issue 2 themselves.** `estimands_01` imports a RECIST best-overall-
response table from the PrE0102 SAP (`smartphrase/SAP/15-appendix5-best-overall-response.md`) —
Target × Non-Target × New Lesions → Overall Response, a multi-variable classification — as
source text to ground smartphrases against. Issue 2 is well timed, and can cite their own
document.

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

## Issue 3 — No time-to-event derivation transformations, and no settled shape for one

**Type:** transformation library gap
**Depends on:** Issue 2

The transformation library holds 14 derivation transformations. None produces `AVAL` or
`CNSR` — the strings `CNSR`, `censor` and `AVAL` do not appear in
`ACDC_Transformation_Library_v06.json` at all. `T.OS_LogRank` binds `time` (concept
`TimeToEvent`) and `event` (concept `Flag`) as **inputs**, so the survival chain begins
already derived, with nothing upstream deriving it.

The methods to close this look present at first — `M.DateDifference`, `M.RecordSelection`,
`M.Aggregation` — but two questions sit behind them:

1. **Predicates.** Issue 2. The hierarchy cannot be expressed.
2. **Output shape.** `AVAL`, `CNSR`, `ADT` and `EVNTDESC` are four projections of a *single*
   censoring resolution. Deriving them as four independent transformations would leave nothing
   in the metadata requiring them to agree — an `AVAL` from the PD date paired with `CNSR = 1`
   is individually well-formed and jointly wrong.

   The library already has two ways of emitting coordinated outputs from one derivation, so
   this may be a question about which to use rather than a gap. `M.WindowedVisitAssignment`
   declares three output classes (`analysisVisit`, `analysisVisitNumber`, `analysisDay`) and
   `T.DeriveAnalysisVisit` binds all three from a single windowing decision. `T.UnitConversion`
   emits two **facets of one `Measure`** — `result.value` as a `measure` and `result.unit` as
   an `attribute`, the latter noted as *"propagated so downstream derivations/analyses can read
   the Measure's unit without re-reading config."*

   What has no precedent is a derivation emitting several coordinated outputs that are each a
   `measure` in their own right: thirteen derivation transformations emit exactly one measure
   binding and `T.DeriveAnalysisVisit` emits none.

**Question for maintainers, before proposing entries.** Is the `T.UnitConversion` facet pattern
the intended shape here — one `Measure` for the time-to-event, with `CNSR`, `ADT` and
`EVNTDESC` as facets or attributes of it — or should a TTE derivation emit four coordinated
measures, which would be new? We would rather follow the existing convention than invent one.

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

### The term already ships in this repository

`neo4j/data/metadata/stato/stato.owl` carries:

```
http://purl.obolibrary.org/obo/STATO_0000424   rdfs:label "risk difference"
http://purl.obolibrary.org/obo/STATO_0000626   rdfs:label "relative risk difference"
```

and methods are already coded against that system — `M.CMH` carries
`{ "system": "http://purl.obolibrary.org/obo/stato", "code": "STATO_0000074" }`. So the
vocabulary entry has an obvious coding and needs no new ontology work.

### It also bears on work in progress

The `estimands_01` branch adds `SP_SUMMARY_MEASURE` — `role: "summary_measure"`,
`phrase_template: "summarised as {summary}"` — giving the estimand's population-level summary a
phrase slot. For the study we mapped, the value that slot needs to name is a statistic the
vocabulary cannot express.

**Suggestion.** Add a difference-of-proportions statistic to the vocabulary, coded
`STATO_0000424`, and either extend `M.CMH`'s `association_measures` output class or add a
companion method for the stratified difference. This looks like the smallest and most
self-contained of the gaps reported here.

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

There is also no worked example of any kind: `T.BaselineSelection` is the only transformation
in the library that uses `M.RecordSelection`, and it configures `last_non_missing`. Five of the
six selection rules are exercised by nothing.

**Suggestion.** An ordering declared on the concept or parameter, **with a per-transformation
override.** Both halves are needed, and we found the second the hard way.

RECIST response ordering (`CR ≺ PR ≺ SD ≺ PD ≺ NE`) is a property of the response scale, which
argues for carrying it with the concept. But a laboratory shift table in the same study ranks
its reference-range indicator `LOW = HIGH > NORMAL` — collapsing the two abnormal directions,
because for that table "worst" means *abnormal either way*. A directional parameter in the same
dataset would need low to outrank high. That ordering belongs to the analysis, not to the
scale, so concept-level declaration alone would be authoritative and wrong.

A `direction` configuration would cover the simple numeric case but neither of these.

---

## Candidates, not yet drafted

Three findings from the lab tier are real and verified but not written up as issues here, so
the count above stays at five. Each needs a decision before drafting:

| Finding | Why not drafted yet |
|---|---|
| [F09](F09-record-selection-has-no-tiebreak.md) — no tie-break, and `time_order` unbound by every transformation | Probably belongs *inside* Issue 5 rather than beside it: same method, and both are "the ordering is unstated". It also carries a separable conformance defect — three transformations omit a role their method marks `required: true` — which may be worth reporting on its own, since it suggests nothing validates transformations against their methods |
| [F10](F10-visit-windows-are-enumerated-not-generated.md) — windows enumerated not generated; nothing escapes windowing; `windows` has no item schema and `tieBreak` no enum | Four fixes of very different sizes bundled in one finding. Needs splitting before filing — the `tieBreak` enum is a one-line fix and the generated-windows question is a design discussion |
| [F11](F11-analysis-record-flag-has-no-transformation.md) — `ANL01FL` is named in `M.RecordSelection`'s output description and produced by nothing | Overlaps Issue 2: the rule TORIVA needs is conditional on another derivation's output, which is the predicate gap again. The missing `T.` entry is ordinary library work and could be contributed rather than filed |
| [F12](F12-baseline-flag-and-baseline-value-are-disconnected.md) — the baseline flag and the baseline value are disconnected | The **strongest candidate after Issue 4**, and the only finding here produced by running their own application. It is concrete, reproducible in four clicks, and lands on change from baseline — the simplest derivation they ship. Not drafted yet because it bundles three things: the flag/value disconnect, the visit-based vs date-based mismatch, and the fact that concept-string matching makes every `Flag` interchangeable (so the builder offers a baseline flag to resolve a log-rank event indicator). The last of those may deserve to be the issue |

## Suggested filing order

Five issues at once is a lot to arrive with — and against a four-issue tracker with one active
maintainer, it is far too many. **File Issue 4 alone, then stop and wait.** The order below
applies only if and when that one is well received.

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
