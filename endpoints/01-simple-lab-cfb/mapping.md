# Laboratory change from baseline — chain mapped on paper

Step 1 of the method: map the chain against the SAP text **before** opening the builder.
Nothing was authored before this document was written.

**Sources.** TORIVA-LUNG 301 at `8534339d`: SAP §12.2 (analysis visits), §12.3 (baseline
definition), §7 (missing data), §4.6 and §5.5 (safety endpoints and methods), §14 (TFL
crosswalk); `programming-specs/ADLB-spec.md`; and — for ground truth on what was actually
built — `programs/adam/adlb.R` and `programs/tfl/t_lb_01_shift.R`. Upstream at `739344c`.

**Verdict: it composes, and what it composes is not what the study analyses.**

The derivation chain the specification predicted — baseline selection, then change from
baseline — does compose, with three qualifications. But **the SAP specifies no laboratory
analysis at all**, so nothing consumes `CHG`. The lab analyses that TORIVA actually built are
a shift table and a CTCAE grade table, neither of which reads `CHG`, and the shift table does
**not** compose: it hits F06 and F07, the same two walls as ORR and PFS.

This is a third kind of result. PFS found the framework's expressive limit; ORR found it
again on a second endpoint. The simple tier finds a **scope boundary** instead — the part of
the flow that works is not attached to anything, and the part that is attached does not work.

---

## What the SAP asks for

Nothing. That is the finding, and it took reading the whole SAP to be sure of it.

`ADLB` appears in the 626-line SAP exactly six times, all in data-handling conventions:

| Line | Section | What it says |
|---|---|---|
| 348 | §12.2 | `AVISIT`/`AVISITN` are populated on ADLB |
| 362 | §12.2 | ADLB follows the TREATMENT windowing stream |
| 392 | §12.2 | `ANL01FL` uses one rule across ADLB, ADVS, ADRS, ADTR |
| 435–436 | §12.2 | SDTM `VISIT` retained alongside `AVISIT` in ADLB |
| 444 | §12.3 | Baseline is the last non-missing value on or before `TRTSDT` |

§7 adds one row — *"Baseline lab values: last non-missing pre-treatment value per PARAMCD.
No imputation beyond that."*

There is no lab endpoint in §4 and no lab method in §5. §4.6 (Safety, S5) is adverse events
only — TEAE, SAE, irAE, AESI, Grade ≥3 AE — and §5.5 summarises those by SOC and PT. §14, the
crosswalk to TFL shells, reads *"To be completed in `tfl/TFL-SHELLS.md`"*, and **that file does
not exist** at the pinned commit.

So `CHG` and `PCHG` are derived by a blanket convention in §12.3 that applies to every by-visit
BDS dataset, and no analysis in the study reads them.

The lab analyses that do exist are specified only in `ADLB-spec.md`'s shell cross-reference and
implemented in `programs/tfl/`:

| Shell | Program | Consumes |
|---|---|---|
| T-LB-01 | `t_lb_01_shift.R` | `ABLFL`, `NRIND`, `PARAMCD`, `TRT01A` |
| T-LB-02 | `t_lb_02_g3_plus.R` | `ATOXGR`, `PARAMCD` |

Neither reads `CHG`, `PCHG` or `BASE`.

---

## Chain A — the derivation the specification predicted

Specification §4.1: *"BC → `T.BaselineSelection` → `T.ChangeFromBaseline` → descriptive or
ANCOVA. Both transformations exist upstream. Expected to work with no new authoring."*

| # | Step | Method / transformation | Composes? |
|---|---|---|---|
| 1 | Per-record lab value `AVAL` | from BC / SDTM `LB` | input, not derived here |
| 2 | Analysis visit `AVISIT`/`AVISITN` | `T.DeriveAnalysisVisit` | **Partly** — B8 |
| 3 | One analysis record per visit (`ANL01FL`) | `M.RecordSelection`, `closest_to_target` | **Partly** — B10 |
| 4 | Baseline flag `ABLFL` | `T.BaselineSelection` | **Yes**, with B7 and a question |
| 5 | `BASE` onto every record | `T.ChangeFromBaseline`'s `parameter_baseline` slice | **Yes** |
| 6 | `CHG` = `AVAL` − `BASE` | `T.ChangeFromBaseline` | **Yes** |
| 7 | `PCHG` = 100 × `CHG` / `BASE` | `M.PercentChange` exists; no `T.` entry | **Partly** — B9 |
| 8 | An analysis consuming `CHG` | — | **Does not exist in the study** |

Four of eight compose outright, three partly, and the eighth has nothing to bind to.

### What composes, and it is worth naming

`T.BaselineSelection` is configured `selection_rule: last_non_missing`, `scope: pre_treatment`,
`cardinality: single`, `reference_event: first_dose`. TORIVA's §12.3 baseline is *the last
non-missing analysis value on or before the date of first study treatment, per subject ×
parameter, exactly one record*. Those line up field for field, including `reference_event` —
whose description names the randomisation date as the alternative, so the model represents the
choice §12.3 is making rather than assuming it. This is the framework working as advertised.

`T.ChangeFromBaseline` is a closer fit than expected, and for an interesting reason. It binds
its subtrahend through a slice:

```json
"slices": [{ "name": "parameter_baseline",
             "constraints": [{ "concept": "Parameter",     "value": "{parameter}" },
                             { "concept": "AnalysisVisit", "value": "{baseline_visit}" }] }]
```

It reaches the baseline value by **`AnalysisVisit`**, not by the baseline *flag*. That only
works if the baseline record is identifiable as a visit — and TORIVA independently does exactly
that: `apply_baseline_visit()` forces `AVISIT = "Baseline"`, `AVISITN = 0` onto the `ABLFL = "Y"`
record *regardless of the window its `ADY` falls in* (`adlb.R` §6b, SAP §12.3). Two
implementations arrived at the same requirement independently, which is mild evidence the
model has this joint right.

Worth noting for the tier's original purpose: this chain exercises `ParameterDimension` across
many lab parameters, which the ADAS-Cog control does not.

---

## Chain B — the analysis TORIVA actually built

T-LB-01, baseline → worst post-baseline shift, per parameter per arm, Safety population.

| # | Step | Method | Composes? |
|---|---|---|---|
| 1 | `NRIND` per record | SDTM `LB.LBNRIND` predecessor | input — see D8 |
| 2 | Baseline `NRIND` | `T.BaselineSelection` then read `NRIND` | **Yes** |
| 3 | Worst post-baseline `NRIND` | `M.RecordSelection`, `selection_rule: worst` | **No** — B5 |
| 4 | Classify (baseline, worst) into four shift categories | — | **No** — B1 |
| 5 | Count per parameter × arm × category | `M.Count` / `T.Count_Measure` | **Yes** |
| 6 | Denominator per parameter × arm | `M.Count` | **Yes** |

Three of six.

---

## The blockers

**B1 — the shift classification is a two-variable predicate.** *(F06, unchanged.)*
`t_lb_01_shift.R` classifies with

```r
classify <- function(bn, wn) {
  bn_a <- bn != "NORMAL"; wn_a <- wn != "NORMAL"
  case_when(!bn_a & !wn_a ~ "NORMAL → NORMAL",  !bn_a &  wn_a ~ "NORMAL → ABNORMAL",
             bn_a & !wn_a ~ "ABNORMAL → NORMAL", bn_a &  wn_a ~ "ABNORMAL → ABNORMAL")
}
```

Every arm of that `case_when` relates **two** variables. `M.ConditionalValue` tests only
`IS_NA`; `M.ThresholdCompare` compares one input against a constant; `M.Categorization` takes
free-text conditions over a single `value`. Not expressible — the third endpoint in a row to
hit this, and the first where it blocks a *safety* analysis rather than an efficacy one.

**B5 — `worst` presupposes an ordering, and here the ordering is study-specific.** *(F07,
strengthened.)* The program supplies its own ranking:

```r
nrind_order <- c("LOW" = 1, "HIGH" = 1, "NORMAL" = 0)
```

`LOW` and `HIGH` are collapsed to the same rank, so "worst" means "abnormal in either
direction". That is a defensible reading for a shift table and a wrong one for a directional
parameter. F07 argued that `best`/`worst` presuppose an ordering the metadata does not carry;
this is a case where the ordering is not merely undeclared but **analysis-specific** — it is
not a property of the `NRIND` scale, it is a property of *this table*. An ordering carried on
the concept, which F07 proposed as the better fix, would not capture it. That is an argument
against F07's own suggestion and belongs in the issue.

**B7 — record selection has no tie-break.** SAP §12.3 and `adlb.R` both break baseline ties by
the SDTM sequence number: `order = exprs(ADT, LBSEQ)`, `mode = "last"`. `M.RecordSelection`
carries `selection_rule`, `scope`, `cardinality`, `reference_event` and `target_value` — and no
secondary sort key. Its formula references a bare `<time_order>` with nothing configuring it.
Two draws on the same date are ordered by nothing the metadata states, so a chain that is
correct and a chain that silently picks the other record are identical in metadata. Same
species as F07, on a different configuration.

**B8 — visit windows must be enumerated, and TORIVA's are generated.** SAP §12.2 defines a
**nearest-target partition**: each visit has a protocol target day, and *"the boundary between
two consecutive visits is the midpoint between their targets"*. Windows are therefore derived
from targets, and `crf/analysis_visit_windows.csv` is generated by a script.
`M.WindowedVisitAssignment.windows` is an explicit `object[]` of
`{label, visitNumber, dayMin, dayMax, targetDay}`. The midpoints can be precomputed and pasted
in, so this is expressible — but the *rule* is not, only its expansion, and the expansion is
the thing that goes stale when a target day moves.

Two harder parts:

- The maintenance schedule is **open-ended** — `MAINT_CmD1` at target `1 + (5 + m)·21` for
  unbounded `m`. An enumerated array has to be truncated at whatever `m` the data happens to
  reach.
- **Event-driven visits escape windowing entirely.** §12.2: *"`EOT`, `FU1`, `FU2` are not
  day-windowed — they are determined by protocol role and keep their collected label and SDTM
  `VISITNUM`."* `M.WindowedVisitAssignment`'s formula is
  `analysisVisit := FIND WINDOW(<windows>) MATCHING <day>` — every record is windowed by day.
  There is no mechanism for "this record keeps its collected visit".

Also minor: `tieBreak` is `dataType: "code"` with default `closest-to-target-then-earliest` and
**no enum and no codelist**. TORIVA needs ties broken to the *later* `ADT` (§12.2, and
`ADLB-spec.md` #28). Whether `closest-to-target-then-latest` is an accepted code is unstated —
the permitted values of the configuration are not declared anywhere.

**B9 — no percent-change transformation.** `M.PercentChange` exists, with
`result := 100 * (<post> - <pre>) / <pre>` and roles `pre`/`post`, both `decimal`. There is no
`T.` entry wrapping it: the 14 derivation transformations include `T.ChangeFromBaseline` and no
percent-change counterpart. Ordinary library work, not a model gap — the same shape as the
missing `M.CMH` and `M.Proportion` entries noted in F08.

**B10 — `ANL01FL` has no transformation, and its rule reaches across derivations.** Selecting
one analysis record per `USUBJID × PARAMCD × AVISIT` is `M.RecordSelection` with
`closest_to_target`, which exists. But SAP §12.2 adds: *"inside the `Baseline` visit the
`ABLFL = 'Y'` record wins, so the baseline analysis value agrees with `BASE`."* That is a
selection rule conditioned on **the output of a different derivation**. Expressing it needs
either a predicate over two variables (B1 again) or an ordering of derivations that the chain
model would have to make explicit.

### One question for the builder, not a blocker

`T.BaselineSelection` binds `VisitDimension` as a `partition` input alongside `Subject` and
`ParameterDimension`. TORIVA's baseline is emphatically **not** partitioned by visit — SAP
§12.3: *"The selection is date-based, not visit-based: the reference value is whichever
assessment is last before treatment — a Screening draw *or* a Cycle 1 Day 1 pre-dose draw —
regardless of the collected `VISIT`."* Partitioning by visit would yield one baseline per
visit, where P21 AD0154 requires exactly one per subject × parameter.

Whether a binding can simply be left unbound at authoring time is not something the paper
mapping can settle — it is the first thing to find out in the builder, and it is recorded here
so the answer is not back-filled as though it had been obvious.

---

## Discrepancies in the source study

Five more, none resolved here. Resolving them by inspection before authoring would contaminate
step 3. Recorded for `comparison.md` alongside the seven from the PFS and ORR mappings.

**D8 — `ANRIND` and `BNRIND` do not exist.** `ADLB-spec.md` lists both as derived: #25
`ANRIND` *"L/N/H based on AVAL vs ANRLO/ANRHI"* and #24 `BNRIND` *"L/N/H based on BASE vs
ANRLO/ANRHI"*. Built ADLB carries neither. It carries a single `NRIND`, assigned straight from
the SDTM predecessor (`adlb.R:53`, `NRIND = LBNRIND`), and `t_lb_01_shift.R` uses that one
column for both ends of the shift. The spec describes a derivation; the code does a rename.

Worth noting for this project specifically: the derivation the spec *describes* — classify a
value against a lower and an upper limit, both per-record variables — is itself B1. Had it been
implemented as specified, the shift table would have hit the predicate gap twice.

**D9 — `BTOXGR` does not exist.** `ADLB-spec.md` #27 lists it, and the T-LB-02 shell
cross-reference names it. `adlb.R`'s final `select()` carries `ATOXGR` and `ATOXGRN` and no
baseline toxicity grade.

**D10 — the TFL crosswalk was never written.** SAP §14: *"To be completed in
`tfl/TFL-SHELLS.md`."* At `8534339d` the `tfl/` directory holds `.gitkeep`, `TFL-OUTPUTS.docx`,
`TFL-OUTPUTS.html`, `figures/` and `tables/` — no shells document. Yet
`programs/tfl/t_lb_01_shift.R`, `t_lb_02_g3_plus.R` and `l_lb_01_g3_plus.R` all exist and ran.

**D11 — the lab analyses are unspecified in the SAP.** The consequence of D10 and of §4/§5
carrying no lab endpoint or method. T-LB-01 and T-LB-02 are specified only in a programming
spec's shell cross-reference table. This is the same pattern as D2 and D6 — the SAP delegating
and the implementation diverging — but one step further: here the SAP never specified the
analysis in the first place, and the authoritative statement of what the shift table *is* lives
in the R program that produces it.

For a project about making analysis derivation declarative and traceable, D11 is the most
pointed of the eleven. The baseline convention that the concept model captures cleanly is in
the SAP; the analysis that the concept model cannot capture is not.

**D12 — `ADLB-spec.md` is internally inconsistent about its own version.** The header reads
*"Spec version | 0.1 DRAFT"*; the change log records 0.1 (2026-04-25), 0.2 (undated, unfilled)
and 0.3 (2026-07-24). Minor, and mechanical.

---

## What this means for the tier

The specification gave the simple tier a clear job: *"its value is precisely that it is
shallow — it shows the flow does not impose machinery where none is needed, which is the first
objection the framework will attract."*

It does that, and the result is more interesting than a pass. Chain A is genuinely shallow:
`T.BaselineSelection` and `T.ChangeFromBaseline` are configured, not authored, and the
`parameter_baseline` slice turns out to encode a joint TORIVA arrives at independently. The
framework does not impose machinery here.

But the tier also shows something the ladder was not built to test. The endpoint that composes
is **not analysed**, and the analysis that exists does not compose. A coverage view built on
this study would show a complete, well-formed chain for lab change from baseline feeding
nothing, and no chain at all for the two lab tables that were actually produced. That is worth
more to the snapshot than a clean pass would have been, and it sharpens what
`snapshot/index.html` has to show: chain completeness and *analysis binding* are different
axes, and a chain can be complete on one while empty on the other.

**Recommended next step.** Author Chain A steps 4, 5 and 6 — the part that composes and is
specified in the SAP — and record the cost. Skip steps 2, 3 and 7 for a first pass: each is a
partial blocker (B8, B10, B9) and none is needed to produce `CHG` against the built column.
Compare `CHG` and `BASE` against `adlb.parquet` at step 3, which is a real ground-truth check
even though no TFL consumes those columns.

Do **not** author Chain B. Steps 3 and 4 are F07 and F06, and a shift table with the
classification hand-waved would be exactly the "complete-looking" artefact specification §6.2
rules out.

## Addendum — what the builder showed (2026-09-16)

The paper mapping above was written first, per the method. `ac-dc-app` was then served and
driven far enough to check one specific question, and it contradicted part of the mapping.

**Route taken.** CDISC Pilot study → endpoint **END5, *"Laboratory evaluations (Change from
Baseline)"*** — which is a shipped endpoint of the Pilot study, so this is the lab tier's own
shape — → concept category `Change (Comparison)` → analysis template *Change From Baseline
ANCOVA* → derivation pipeline.

**`T.BaselineSelection` is not offered to resolve the baseline value, and cannot be.**

The pipeline asks the author to resolve `AVAL/AVALC/BASE (Measure)` for the `subtrahend` of
`T.ChangeFromBaseline`, and offers **nine** templates:

```
LOCF Imputation · ADAS-Cog Item Max Score · ADAS-Cog Per-Item Missing-Capacity Contribution ·
ADAS-Cog Missing Scale Capacity · ADAS-Cog Scoreable Fraction · ADAS-Cog Sum of Available Item
Scores · ADAS-Cog Non-Missing Item Count · ADAS-Cog (11) Total Score · Unit Conversion
```

`T.BaselineSelection` is absent, and the reason is structural: its output binding is
`concept: "Flag"`, so it produces `ABLFL`, not a `Measure`. It can never satisfy a dependency
that needs the baseline *value*.

**So the baseline flag and the baseline value are independent derivations.** The value is
reached entirely through `T.ChangeFromBaseline`'s slice, which the panel renders as

```
inherited slice: parameter_baseline — scopes this subtree's inputs
  Parameter      {parameter}
  AnalysisVisit  Baseline
```

— by *visit label*, never by the flag. Nothing in the metadata requires the record `ABLFL`
marks to be the record `BASE` is taken from.

**This corrects the mapping above**, which listed step 4 (`ABLFL` via `T.BaselineSelection`)
and step 5 (`BASE` via the slice) as consecutive steps of one chain and called the slice's
reliance on `AnalysisVisit` an elegant joint. They are not consecutive: they are two chains
that never meet. The observation that TORIVA's `apply_baseline_visit()` independently forces
`AVISIT = "Baseline"` onto the `ABLFL` record still stands, and is now more pointed — that
line of R is the *only* thing making the flag and the value agree, and its equivalent is
exactly what the concept model does not carry.

This is the same shape as F01's `AVAL`/`CNSR` concern and
[F11](../../docs/findings/F11-analysis-record-flag-has-no-transformation.md)'s `ANL01FL`
concern: several projections of one decision, with nothing tying them together. On the tier
that was supposed to be trivial.

**It also revises the tier's verdict slightly.** Chain A step 4 does not feed step 5, so the
"4 of 8 compose outright" count stands only if step 4 is read as producing `ABLFL` for its own
sake — which is what ADLB does, and what T-LB-01 consumes. Change from baseline needs only
steps 5 and 6.

## New findings

B1 and B5 are F06 and F07, confirmed on a third endpoint. B5 is **strengthened in a way that
bears on F07's proposed fix**: the `LOW`/`HIGH` collapse is an ordering belonging to one
analysis, not to the concept, so declaring an ordering on the concept would not capture it.
That should be added to F07 and to upstream Issue 5 before it is filed.

**B11 — the baseline flag and the baseline value are disconnected.** *New, from the builder.*
Written up as [F12](../../docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md),
which adds the matching mechanism (`findDerivationsForConcept`, exact equality on output
concept), the visit-based/date-based mismatch against SAP §12.3, and two incidentals — every
`Flag` being interchangeable, and three demanded concepts having no producer.

B7, B8 and B10 are new and belong in `docs/findings/`:

- **B7** — `M.RecordSelection` has no tie-break or secondary sort key.
- **B8** — visit windows must be enumerated rather than generated, cannot be open-ended, and
  event-driven visits have no escape from day-windowing. `tieBreak` has no declared value set.
- **B10** — no `ANL01FL`-equivalent transformation, and the rule reaches across derivations.

B9 is ordinary library work and does not need a finding — it belongs as a note on whichever
issue covers the missing `T.` entries, alongside F08's `M.CMH` observation.
