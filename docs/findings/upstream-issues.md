# Drafts for `cdisc-org/analysis-concepts` issues

Against `739344c` (2026-06-17). Not yet filed.

Originally two issues were planned (specification §12): the unused `censoring` role, and the
missing time-to-event transformations. There are now five, three of them from mapping endpoints
on paper rather than from inspecting the libraries. **The first does not survive verification** — see
[F02](F02-time-event-role-collision.md); there is no `censoring` role. It is replaced below
by the role-collision issue, which is the defensible part of the same concern.

**All five issues were restructured on 2026-09-16 to lead with the requirement**, after reading
issue #9 on the upstream tracker (see the repository-state section below): its body records the
maintainer rejecting an issue that *"specified solution choices before the requirements were
stated"*, and noting that the first round of work followed those choices in the wrong direction.

Each now runs: **the requirement** - what a study needs to be able to say - then **what the
libraries provide today**, then a **solution space that is deliberately not chosen**. Where we
noticed a gap only because of our own tooling (Issue 1) or are unsure the gap is one the project
accepts as in scope (Issue 2), that is said in the issue rather than left for the maintainer to
infer.

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

## Issue 1 — A method's inputs cannot be interpreted without reading its formula string

**Scope:** method metadata
**Motivating case:** the three survival methods

### The requirement

A method's `input_roles` should carry enough information for a consumer to know what each input
*is*. Anything reading the library programmatically — a catalogue, a validator, a duplicate
check, a diff between two versions of an entry — works from the structured fields, because the
formula is a string written for a human and for the execution layer.

Where two inputs of the same method mean different things, the metadata should say so.

### What the libraries provide today

`M.KaplanMeier`, `M.CoxPH` and `M.LogRankTest` each declare `time` and `event` with
`statisticalRole: "response"`, identical `dataType` and identical `cardinality`. The distinction
is carried only by position in `formula.generic_expression`:

```
Surv(<time>, <event>) ~ <fixed_effect>
```

For execution this is unambiguous and works. For anything reasoning over the structured fields
the two inputs are interchangeable: swapping them produces metadata that is byte-identical and
an analysis that is nonsense.

### Why we ran into it

We are building a content-addressable signature over methods, to detect near-duplicate entries
across catalogues and to decide whether a change between two versions of an entry is breaking.
The three survival methods are the case where that signature cannot separate two entries that
differ in meaning.

**That is our use case, not necessarily yours** — and it is the honest reason we noticed. If the
position-in-formula convention is considered sufficient, this is a non-issue, and we would
rather be told so than have it changed on our account.

### Solution space — deliberately not chosen

If it is worth addressing at all:

- a `StatisticalRole` value distinguishing the event indicator from the time response;
- a flag or qualifier on the input role itself;
- something outside `statisticalRole` entirely, if that enum is meant to describe a slot's
  position in a model rather than its meaning.

Small precedent for the first: the enum already carries `offset`, which no method in the library
uses.

---

## Issue 2 — Derivations that branch on a relation between two variables cannot be expressed

**Scope:** derivation methods
**Motivating cases:** three endpoints on one oncology trial

### The requirement

Much of what a SAP specifies as a derivation is a decision comparing **two variables**. Three
examples, from three different endpoints of the study we mapped:

| Endpoint | The rule | The comparison |
|---|---|---|
| PFS | FDA 2018 censoring hierarchy | *therapy start < PD date*; *PD date ≤ data cut-off* |
| ORR | RECIST confirmation | *second assessment ≥ 28 days after the first*, and *no worse* |
| Laboratory | shift table | *baseline indicator* against *worst post-baseline indicator* |

These are not exotic. They are the ordinary content of oncology SAPs, and a chain that cannot
state them has to hand the decision to code outside the model — which is the opacity a
declarative concept model exists to remove.

### What the libraries provide today

Three methods carry a conditional, and each confines it to a single input:

| Method | Predicate | Reach |
|---|---|---|
| `M.ConditionalValue` | `IF(IS_NA(<value>), <alternate>, <base>)` | missingness only; no condition configuration exists |
| `M.ThresholdCompare` | `IF(<value> <operator> <threshold>, ...)` | one input against a **constant** |
| `M.Categorization` | `CASE WHEN <conditions> ...` | free-text `string` over the single `value` input |

Each declares exactly one `value` input role. None can reference a second variable.

On the study we mapped this blocks every censoring hierarchy, and with it all six ADTTE
parameters (OS, OSWOT, PFS, PFSINV, DOR, TTR); it blocks ORR's confirmation rule; and it blocks
the laboratory shift table.

**Related, and possibly the same issue.** `M.Categorization.conditions` is typed `string` with
an example rather than a grammar, so even where a single-variable condition fits it is not
parseable or checkable by anything.

### Worth saying plainly

This is the largest of the gaps we are reporting and the one where we are least sure what the
right answer looks like. There may be a deliberate reason predicates are constrained — keeping
methods executable in WebR, or keeping the model declarative rather than drifting toward a
general expression language. If so, we would like to know where the intended boundary is, since
that determines whether a study like this one is in scope for the framework at all.

### Solution space — deliberately not chosen

- a derivation method taking two (or n) value inputs plus a comparison operator — effectively
  `M.ThresholdCompare` with the threshold promoted from a configuration to an input role;
- a grammar for `M.Categorization.conditions`, making the existing free-text field checkable and
  letting it name more than one input;
- an explicit statement that multi-variable predicates are out of scope, which is a useful
  answer too.

---

## Issue 3 — A survival endpoint's chain has to begin already derived

**Scope:** transformation library, and a modelling question behind it
**Depends on:** Issue 2
**Motivating case:** PFS on a Phase 3 oncology trial

### The requirement

A study with a time-to-event endpoint needs the chain to start where the data starts. The
analysis consumes a time and an event indicator; something has to derive them from the collected
assessment and death dates, and that derivation — the censoring rule — is usually the most
contested paragraph in the SAP and the one most worth making declarative.

### What the libraries provide today

The chain begins after that step. `T.OS_LogRank` binds `time` (concept `TimeToEvent`) and
`event` (concept `Flag`) as **inputs**, and nothing upstream produces either. Of the 14
derivation transformations none produces `AVAL` or `CNSR`; the strings `CNSR`, `censor` and
`AVAL` do not appear in `ACDC_Transformation_Library_v06.json` at all. Counting measure-role
inputs against what the derivations can output, `TimeToEvent` is demanded by `T.OS_LogRank` and
produced by nothing.

### The question we would rather ask than answer

The methods look present — `M.DateDifference`, `M.RecordSelection`, `M.Aggregation` — and two
things sit behind them. The first is Issue 2: the hierarchy itself cannot be expressed.

The second is a modelling question, and it is why this is a question rather than a proposal.
`AVAL`, `CNSR`, `ADT` and `EVNTDESC` are four projections of a **single** censoring resolution.
Derived as four independent transformations, nothing in the metadata would require them to
agree — an `AVAL` taken from the PD date paired with `CNSR = 1` is individually well-formed and
jointly wrong.

The library already has two ways of emitting coordinated outputs from one derivation:

- `M.WindowedVisitAssignment` declares three output classes — `analysisVisit`,
  `analysisVisitNumber`, `analysisDay` — and `T.DeriveAnalysisVisit` binds all three from a
  single windowing decision;
- `T.UnitConversion` emits two **facets of one `Measure`**: `result.value` as a `measure` and
  `result.unit` as an `attribute`, the latter noted as *"propagated so downstream
  derivations/analyses can read the Measure's unit without re-reading config."*

What has no precedent is a derivation emitting several coordinated outputs that are each a
`measure` in their own right — thirteen derivation transformations emit exactly one measure
binding, and `T.DeriveAnalysisVisit` emits none.

**So: is the `T.UnitConversion` facet pattern the intended shape** — one `Measure` for the
time-to-event, with `CNSR`, `ADT` and `EVNTDESC` as facets or attributes of it — **or should a
TTE derivation emit four coordinated measures, which would be new?** We would rather follow an
existing convention than invent one.

### Offer

We have the PFS chain mapped on paper against a public simulated study, and are happy to
contribute the `T.` entries once the shape is settled and Issue 2 is resolved.

---

## Issue 4 — An estimand's population-level summary cannot always be expressed

**Scope:** estimand summary measures, for binary endpoints
**Motivating case:** objective response rate on a Phase 3 oncology trial

### The requirement

ICH E9(R1) makes the **population-level summary** one of the five attributes of an estimand,
alongside population, variable, treatment and intercurrent-event handling. An eSAP that binds
to USDM `Estimand` as a first-class class should therefore be able to state that attribute for
the estimands a study actually specifies.

For a binary endpoint, the summary a protocol specifies is commonly a **difference of
proportions** — a risk difference, usually Mantel–Haenszel and stratified, with a confidence
interval. On the study we mapped, that is what the SAP specifies for ORR in both §5.3 and
§13.6: *"Stratified Mantel–Haenszel risk difference (torivumab − placebo) with 95% CI; strata =
histology × region."*

We could not express it.

### What the libraries provide today

`M.CMH` declares three output classes:

| Output class | Statistics |
|---|---|
| `test_result` | `chi_squared`, `p_value`, `df` |
| `association_measures` | `odds_ratio`, `CI_lower`, `CI_upper` |
| `homogeneity_test` | `chi_squared`, `p_value`, `df` |

The association measure is an odds ratio. The proportion-related entries in
`model/method/statistics_vocabulary.json` are `proportion`, `pct`, `cumulative_pct`,
`odds_ratio` and `n_risk`. Searching `lib/` and `model/` for `risk_difference`,
`rate_difference` and equivalents returns nothing.

`M.Proportion` covers the per-arm side well — `proportion`, `pct`, `CI_lower`, `CI_upper`, with
a `ci_method` configuration offering `exact_clopper_pearson`, `wilson`, `wald`, `agresti_coull`
and `jeffreys`. It does not contrast groups.

### Why the odds ratio is not a substitute

Reporting an odds ratio where the estimand specifies a risk difference is not an approximation
of the same quantity — for a common binary outcome the two diverge substantially, and under
ICH E9(R1) the summary measure is part of what the estimand *is*. An author who substitutes has
answered a different question, and nothing in the metadata records that they did.

That is the part we think is interesting for this framework specifically. Since the model binds
to `Estimand` directly, an estimand whose declared summary has no expressible statistic looks
like something the model could **detect and report**, rather than something an author works
around silently at authoring time.

### Two things that may make this cheaper than it looks

Offered as information, not as a proposal.

**The term already ships here.** `neo4j/data/metadata/stato/stato.owl` carries
`STATO_0000424 "risk difference"` (and `STATO_0000626 "relative risk difference"`), and methods
are already coded against that system — `M.CMH` carries
`{ "system": "http://purl.obolibrary.org/obo/stato", "code": "STATO_0000074" }`.

**It touches work in progress.** The `estimands_01` branch adds `SP_SUMMARY_MEASURE`
(`role: "summary_measure"`, `phrase_template: "summarised as {summary}"`), giving the
population-level summary a phrase slot. For the study we mapped, the value that slot needs to
name is a statistic the vocabulary cannot currently express.

### Solution space — deliberately not chosen

There is more than one reasonable shape and we would rather not presume which:

- a statistic added to the vocabulary, with `M.CMH`'s `association_measures` extended;
- a companion method for the stratified difference of proportions;
- something else entirely, if summary measures are meant to be modelled differently from test
  results.

We are happy to contribute the entry once the shape is settled, and happy to be told this is
already planned.

### Related, minor

Neither `M.CMH` nor `M.Proportion` has a transformation entry. The only responder analysis
transformation is `T.Responder_ChiSq`, which uses `M.ChiSquaredTest` and binds `response` to
concept `Flag` as an input — the same already-derived shape as `T.OS_LogRank` in Issue 3.
Mentioned only because it came up while mapping the same endpoint.

---

## Issue 5 — `best` and `worst` selection cannot be resolved from the metadata

**Scope:** method semantics
**Motivating cases:** RECIST best overall response, and a laboratory shift table

### The requirement

A selection rule has to be resolvable from what is written down. Given a transformation
configured to select the `best` record in a partition, a reader — human or machine — should be
able to determine which record that is without knowing what the analysis was for.

### What the libraries provide today

`M.RecordSelection.selection_rule` offers:

```json
"enumValues": ["last_non_missing", "first_non_missing", "worst", "best",
               "closest_to_target", "all_matching"]
```

Four of these are fully determined by the data and the configuration. `best` and `worst` are
not, and nothing in the method, the transformation library or the statistics vocabulary supplies
the missing ordering.

1. **For a decimal**, `best` may be the maximum or the minimum — the minimum for tumour
   shrinkage, the maximum for a response rate. There is no direction configuration, and the
   formula `<flag> := IF(<selection_rule>(<value>, <time_order>) OVER (<partition>+), 'Y', '')`
   does not supply one.
2. **For an ordinal code** it is undefined entirely. RECIST 1.1 ranks CR ≺ PR ≺ SD ≺ PD ≺ NE. That
   ordering is standard and clinical and appears nowhere in the model. The `value` input role is
   `dataType: "decimal"`, so a response code is not a valid input at all — yet `best` over
   response codes is the most common use of best-record selection in oncology.

There is also no worked example of any kind: `T.BaselineSelection` is the only transformation in
the library that uses `M.RecordSelection`, and it configures `last_non_missing`. Five of the six
selection rules are exercised by nothing.

The practical effect: best overall response composes as a single configured
`M.RecordSelection`, which is a genuinely good outcome — but two chains built that way, one
ranking CR best and one ranking CR worst, are identical in metadata and produce opposite
results.

### One case that constrains the answer

We initially assumed the ordering belongs on the concept, since RECIST ranking is a property of
the response scale rather than of any one analysis. A second endpoint in the same study
contradicted that.

The laboratory shift table selects the worst post-baseline reference-range indicator and ranks
it `LOW = HIGH > NORMAL` — collapsing the two abnormal directions, because for that table
"worst" means *abnormal in either direction*. A directional parameter in the same dataset would
need low to outrank high. That ordering belongs to the analysis, not to the scale.

So concept-level declaration alone would be authoritative and wrong for the second case, and
per-use declaration alone loses the shared ranking that makes the first case worth stating once.

### Solution space — deliberately not chosen

- an ordering declared on the concept or parameter, with a per-transformation override;
- a `direction` configuration on `M.RecordSelection`, which covers the numeric case and neither
  of the two above;
- widening `value` beyond `decimal`, without which the ordinal case cannot be represented at all
  regardless of where the ordering lives.

The first two are not exclusive. We do not have a view on which layer should own it.

---

## Candidates, not yet drafted

Three findings from the lab tier are real and verified but not written up as issues here, so
the count above stays at five. Each needs a decision before drafting:

| Finding | Why not drafted yet |
|---|---|
| [F09](F09-record-selection-has-no-tiebreak.md) — no tie-break, and `time_order` unbound by every transformation | Probably belongs *inside* Issue 5 rather than beside it: same method, and both are "the ordering is unstated". It also carries a separable conformance defect — three transformations omit a role their method marks `required: true` — which may be worth reporting on its own, since it suggests nothing validates transformations against their methods |
| [F10](F10-visit-windows-are-enumerated-not-generated.md) — windows enumerated not generated; nothing escapes windowing; `windows` has no item schema and `tieBreak` no enum | Four fixes of very different sizes bundled in one finding. Needs splitting before filing — the `tieBreak` enum is a one-line fix and the generated-windows question is a design discussion |
| [F11](F11-analysis-record-flag-has-no-transformation.md) — `ANL01FL` is named in `M.RecordSelection`'s output description and produced by nothing | Overlaps Issue 2: the rule TORIVA needs is conditional on another derivation's output, which is the predicate gap again. The missing `T.` entry is ordinary library work and could be contributed rather than filed |
| [F13](F13-authoring-surface-is-narrower-than-the-model.md) — 65% of methods have no transformation; templates cannot be created or reconfigured | **Probably should not be filed as an issue at all.** For a reference implementation, six generic derivation entries plus one worked example is a reasonable scope, and saying so as a defect would read as criticising the project for not being a product. The filable part is narrow and concrete: specific missing entries (`M.Categorization`, `M.Proportion`, `M.CMH`, `M.DateDifference`, `M.PercentChange`), which this project could contribute rather than request. The builder limits are worth raising as a **question about intended scope**, not a bug |
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
