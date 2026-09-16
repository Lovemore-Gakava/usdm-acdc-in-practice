# usdm-acdc-in-practice

USDM v4.0 and the CDISC AC/DC framework — BC to DC to AC — applied end to end on a simulated Phase 3 oncology trial.

---

## What this is

CDISC's [`cdisc-org/analysis-concepts`](https://github.com/cdisc-org/analysis-concepts) implements the AC/DC framework: an Observation / Derivation / Analysis Concept model, 60 methods, a transformation library, an eSAP model and a working browser-based builder with in-browser R execution.

This repository does not reimplement any of that. It takes three real endpoints of graded complexity through the full chain and records what the process actually costs — what is automated, what a human authors, and where it strains.

The source study is [TORIVA-LUNG 301](https://github.com/OpenTrialReporting/torivumab-nsclc-301), a simulated Phase 3 NSCLC trial with a fictional sponsor. It was chosen because it is the only available source where protocol, SAP, programming specs and built ADaM all exist, are internally consistent, and carry no confidentiality constraint. That last point matters: without built ADaM there is no ground truth, and without ground truth the exercise only demonstrates internal coherence.

## Findings

These came out of applying the framework, and are the most reusable part of this repository.
Each is written up in `docs/findings/`, with the commands and output that establish it.

Every finding was re-verified against the pinned upstream commit before being written up.
**Two of the five original findings did not survive that check, and one was retired outright** —
including one of the two that was slated to be filed as an upstream issue. See
[`docs/method.md`](docs/method.md) for why that step exists.

| ID | Claim | Status at `739344c` |
|---|---|---|
| [F01](docs/findings/F01-no-tte-derivation-transformations.md) | No time-to-event derivation transformations exist | **Confirmed** |
| [F02](docs/findings/F02-time-event-role-collision.md) | The `censoring` statistical role is declared and unused | **Corrected** |
| [F03](docs/findings/F03-chain-position-carries-meaning.md) | Chain position carries meaning that individual entries do not | **Confirmed, stronger** |
| [F04](docs/findings/F04-bc-joint.md) | The BC joint is annotated, not resolved | **Retired** |
| [F05](docs/findings/F05-no-analysis-coverage-view.md) | No study-level view exists | **Restated** |
| [F06](docs/findings/F06-no-general-predicate.md) | No general predicate exists over more than one variable | **New** |
| [F07](docs/findings/F07-ordering-is-unstated.md) | `best`/`worst` presuppose an ordering the metadata does not carry | **New** |
| [F08](docs/findings/F08-no-risk-difference.md) | No difference-of-proportions statistic exists | **New** |

**F01 — No time-to-event derivation transformations exist.** Confirmed. The strings `CNSR`,
`censor` and `AVAL` appear nowhere in the transformation library. `T.OS_LogRank` binds time and
event as inputs, so the survival chain begins already derived. The gap is wider than "author
three or four new `T.` entries", because of F06 and because each derivation transformation emits
a single output measure while a TTE derivation must emit four coordinated ones.

**F02 — Time and event are indistinguishable in method metadata.** *The premise was wrong.*
There is no `censoring` value in `StatisticalRole` and there never has been — `git log -S`
over the schema returns nothing. The role actually declared and unused is `offset`. The
consequence stands and is the part that matters: `M.KaplanMeier`, `M.CoxPH` and `M.LogRankTest`
each declare `time` and `event` as two `response` roles, so any signature over input roles
treats them as interchangeable.

**F03 — Chain position carries meaning that individual entries do not.** Confirmed, and stronger
than stated. `T.ADAS_SumAvailableScores` and `T.ADAS_MissingScaleCapacity` differ in exactly one
field: the free-text `note` on an input binding. Every machine-readable field is identical, so no
signature over structured fields can separate them.

**F04 — The BC joint is annotated, not resolved.** *Retired.* In the worked derivation scenario
all five `Measure` terminals carry 11 `linkedBCIds` each. The four terminals without links are
dimensions — Subject, Parameter, Treatment, Visit — which have no BC to link to. The endpoint-level
`linkedBCIds` is empty, which is where the original reading came from; linkage lives at terminal
level, which is the right place for it.

**F05 — No analysis-coverage view exists.** *Restated.* `js/views/study-overview.js` does exist and
does show objectives and endpoints. What it carries is a checkbox per endpoint, feeding endpoint
selection into the eSAP builder. It holds no authoring state: no chain status, no shared
derivations, no coverage. The gap is narrower than claimed and sharper.

**F06 — No general predicate exists over more than one variable.** *New, and it blocks the complex
tier.* `M.ConditionalValue` is not a general conditional — its predicate is hardwired to
`IF(IS_NA(value), alternate, base)`. `M.ThresholdCompare` compares one input to a constant.
`M.Categorization` takes free-text conditions over a single `value` input. So the specification's
hypothesis that the FDA 2018 censoring hierarchy composes as nested `M.ConditionalValue` over
`M.RecordSelection` is **false on paper**, before any authoring. Confirmed independently on ORR,
whose confirmation rule is a two-record predicate — so this is a general derivation gap, not a
time-to-event one.

**F07 — `best` and `worst` presuppose an ordering the metadata does not carry.** *New.*
`M.RecordSelection.selection_rule` offers `best`, and nothing says what best means — not for a
decimal (maximum or minimum?) and not at all for an ordinal code like RECIST response
(CR ≺ PR ≺ SD ≺ PD ≺ NE). Best overall response composes syntactically while the semantics that
make it correct sit outside the model.

**F08 — No difference-of-proportions statistic exists.** *New.* TORIVA's ORR estimand specifies a
stratified Mantel–Haenszel **risk difference**. `M.CMH` yields an odds ratio, and the statistics
vocabulary carries no difference statistic at all. Under ICH E9(R1) the population-level summary
is part of the estimand, so substituting the odds ratio answers a different question.

Five issues are drafted for upstream, with a suggested filing order — Issue 4 (no risk
difference) is the recommended opener, being the smallest and most concrete. See
`docs/findings/upstream-issues.md`. None has been filed, and none has been human-reviewed.

## The endpoint ladder

| Tier | Endpoint | Estimand | Expectation |
|---|---|---|---|
| Simple | Laboratory change from baseline | — | Works with no new authoring. `T.BaselineSelection` and `T.ChangeFromBaseline` exist |
| Moderate | Objective response rate | E3 / E3a | **Mapped. Half composes** — selection and per-arm summary fit; confirmation rule and risk difference do not |
| Complex | Progression-free survival | E2 / E2a | **Mapped. Does not compose** — one of nine steps. Found the limit earlier than expected |

The simple tier matters *because* it is shallow — it shows the framework does not impose machinery where none is needed. The complex tier is a stress test, and a negative result there is a finding rather than a failure.

The CDISC Pilot's ADAS-Cog endpoint is retained as a control, since it is already worked upstream. When something breaks, it distinguishes a broken flow from a broken endpoint.

**Out of scope:** adverse events (a different shape — event observations, counts, OCCDS rather than BDS) and the remaining five ADTTE parameters.

## Method

Each endpoint follows the same four steps, and the directory structure enforces the order:

1. **`mapping.md`** — map the chain on paper against the SAP text, before opening the builder. If it does not compose on paper, that is the finding. Doing this after authoring makes a negative result uninterpretable.
2. **`chain.json`** — the authored eSAP scenario.
3. **`comparison.md`** — output against the built ADaM, with each divergence classified as model limitation, specification ambiguity, or authoring error.
4. **`log.md`** — elapsed time and every point where a decision was needed.

Step 4 is the point. One ADAS-Cog endpoint took nine nested derivation steps, manually assembled. A real study has ten to fifty analysis-relevant endpoints. Whether that scales is an empirical question, and the authoring cost per tier is the answer.

## Repository structure

```
.
├── README.md
├── LICENSE                          MIT
├── .gitmodules
├── upstream/
│   └── analysis-concepts/           submodule, pinned at 739344c
├── docs/
│   ├── specification.md             full spec and plan
│   ├── method.md                    how the findings were verified
│   └── findings/
│       ├── README.md                index and status of F01–F08
│       ├── F01 … F08                one file each, with evidence
│       └── upstream-issues.md       drafts for cdisc-org issues
├── study/
│   ├── README.md                    why TORIVA, what is used
│   ├── source-refs.md               pinned commit + SAP/spec section refs
│   └── usdm/                        hand-authored USDM fragments
├── endpoints/
│   ├── 01-simple-lab-cfb/           mapping.md, chain.json,
│   ├── 02-moderate-orr/             comparison.md, log.md
│   └── 03-complex-pfs/              mapping.md written — chain blocked, see F06
├── transformations/
│   └── proposed/                    new T. entries — the TTE gap (F01)
├── .githooks/
│   └── pre-commit                   runs the consistency check
├── tools/
│   ├── acdc_divergence.py           signature and divergence detection
│   └── check_consistency.py         documents vs. filesystem
└── snapshot/
    └── index.html                   static coverage view
```

Two deliberate choices:

**Upstream is a pinned submodule, not a copy.** Copying is easier in the moment and strands the repository on a divergent snapshot within two releases.

**TORIVA is referenced by commit, not vendored.** It is 81 MB and read-only input. `study/source-refs.md` pins the commit and points at the specific SAP sections and spec files used, so the work is reproducible without duplicating the study.

## Status

The specification is complete and the findings are verified against pinned commits.

| | |
|---|---|
| Findings F01–F08 | Written up with evidence. F02 corrected, F04 retired, F05 restated; F06–F08 new, from paper mapping |
| Upstream issues | Five drafted with a suggested filing order, none filed |
| Complex tier (PFS) | `mapping.md` written. **Does not compose on paper** — F06. Steps 2–4 blocked |
| Moderate tier (ORR) | `mapping.md` written. **Half composes** — 6 of 11 steps. Partial authoring recommended |
| Simple tier (lab CFB) | Not started. Both transformations exist; expected to work |
| Snapshot | Not started |

`tools/acdc_divergence.py` is usable for methods and **not** trustworthy for transformations —
it reports one transformation cluster at `739344c`, and that cluster is the F03 false positive.

Seven discrepancies inside TORIVA itself have surfaced from mapping (D1–D7), including one that
makes estimand E3 unimplementable as specified: `EFFFL` does not exist on ADRS. All are recorded
in `study/source-refs.md` and left unresolved, so as not to contaminate the step-3 comparison.

Next: author the simple tier to calibrate the effort measurement, then author ORR's composable
steps (2, 3, 7, 8, 9) for the first real cost figure. PFS cannot be authored until F06 is
resolved upstream or a documented workaround is accepted.

## Provenance

Substantially all prose in this repository was drafted by an AI model in a single session on
2026-09-15 and **has not yet been human-reviewed**. Five findings are drafted as issues to be
filed publicly against `cdisc-org/analysis-concepts`; two of the five inherited findings were
wrong as originally written and were caught only by verification. Read
[`PROVENANCE.md`](PROVENANCE.md) before filing anything, and [`docs/method.md`](docs/method.md)
for how claims were checked.

Content based on [CDISC Analysis Concepts (GitHub)](https://github.com/cdisc-org/analysis-concepts)
used under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) license.

## Licence

MIT. Upstream `cdisc-org/analysis-concepts` is MIT and CC-BY-4.0; TORIVA-LUNG 301 is referenced, not redistributed.

CDISC Library content is not included. The upstream cache is gitignored by design and each developer regenerates it with their own API key.
