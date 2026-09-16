# ORR — chain mapped on paper

Step 1 of the method: map the chain against the SAP text **before** opening the builder.
Nothing was authored before this document was written.

**Sources.** TORIVA-LUNG 301 at `8534339d`: SAP §4.3 (endpoint derivation), §5.3 (statistical
methods), §13.6 (estimands E3 / E3a), §3 (populations), `programming-specs/ADRS-spec.md` v0.3.
Upstream at `739344c`.

**Verdict: it half composes.** The selection primitives fit better than expected and the
per-arm summary fits exactly. The confirmation rule and the population-level summary do not.

The specification's ladder expected ORR to be *"analysis side exists, confirmed BOR derivation
is the work."* That is half right and half backwards: part of the derivation composes cleanly,
and it is the **analysis** side that turns out to be missing a piece.

The PFS mapping speculated that ORR would hit the predicate gap *"less severely."* **That was
wrong.** It is the same blocker, F06/B1, and here it sits on the primary derivation.

---

## What the SAP asks for

SAP §4.3, ORR (Secondary S2), estimand E3:

- **BOR (unconfirmed):** best RECIST 1.1 response across post-baseline assessments, BICR reader
- **Confirmed BOR:** a second CR or PR at a subsequent assessment **≥28 days later** with **no intervening PD**
- **ORR flag:** 1 if confirmed BOR ∈ {CR, PR}, else 0
- **Population:** Response Evaluable (`EFFFL = "Y"` on ADRS); E3a switches the denominator to ITT
- **Intercurrent events:** composite — no post-baseline assessment, discontinuation before adequate assessment, and subsequent therapy before adequate assessment all count as **non-responder**
- **Population-level summary (§5.3, §13.6):** stratified **Mantel–Haenszel risk difference** with 95% CI, strata = histology × region; per-arm proportions with Clopper–Pearson exact 95% CI; Wilson score CI as sensitivity

Target: ADRS `PARAMCD = "CBOR"`, `AVALC`, `RSPFL`; ADSL `ORRFL`.

## The chain as it would have to be built

| # | Step | Method | Composes? |
|---|---|---|---|
| 1 | Per-visit overall response (OVR) | from BC / source records | inputs, not derived here |
| 2 | Best response across post-baseline visits | `M.RecordSelection` — `selection_rule: best`, `scope: post_baseline`, partition Subject | **Yes**, with a caveat — B5 |
| 3 | SD qualifies only if ≥8 weeks (`ADY ≥ 57`) | `M.ThresholdCompare` — `operator: >=`, `threshold: 57` | **Yes** |
| 4 | Confirmatory response ≥28 days later, equal-or-better | — | **No** — B1 |
| 5 | No intervening PD between the two | — | **No** — B4 |
| 6 | Composite ICE → non-responder | `M.ConditionalValue` (`IS_NA` → non-responder) | **Partly** — see below |
| 7 | `RSPFL` ← CBOR ∈ {CR, PR} | `M.Categorization` | **Yes** |
| 8 | Per-arm proportion, Clopper–Pearson 95% CI | `M.Proportion` — `ci_method: exact_clopper_pearson` | **Yes** |
| 9 | Wilson CI sensitivity | `M.Proportion` — `ci_method: wilson` | **Yes** |
| 10 | Stratified CMH test | `M.CMH` — response / fixed_effect / strata | **Yes** as a method; no `T.` entry |
| 11 | Stratified MH **risk difference** with 95% CI | — | **No** — B6 |

Six of eleven compose. Two of the three failures are new.

## What composes, and it is worth naming

`M.RecordSelection.selection_rule` carries `enumValues: [last_non_missing, first_non_missing,
worst, best, closest_to_target, all_matching]` and `scope` carries `[pre_treatment,
post_baseline, on_treatment, all, custom]`. **Unconfirmed BOR is a single configured
`M.RecordSelection`** — `best` over `post_baseline`, partitioned by Subject. That is the
framework working exactly as advertised, and it is a real positive result for the tier.

`M.Proportion` is a closer fit still. Its `ci_method` configuration is
`[exact_clopper_pearson, wilson, wald, agresti_coull, jeffreys]`, defaulting to
`exact_clopper_pearson`. SAP §5.3 asks for Clopper–Pearson primary and Wilson as sensitivity —
both are configuration values on one method, so the primary and its sensitivity differ by a
single configured field. That is precisely the reuse the concept model exists to make visible.

## The blockers

**B1 — the confirmation rule is a two-record predicate.** *(F06, unchanged)* Confirmation pairs
a CR/PR at one assessment with another at a later one, requiring `date₂ − date₁ ≥ 28` **and**
`rank₂ ≤ rank₁`. Both relate two variables. `M.ConditionalValue` tests only `IS_NA`;
`M.ThresholdCompare` compares one input against a constant; `M.Categorization` takes conditions
over a single `value`. Not expressible. This is the same wall PFS hit, on ORR's primary
derivation.

**B4 — "no intervening PD" is a range predicate.** *(F06, unchanged)* It quantifies over records
*between* two dates. `M.WindowLookup` reaches a neighbouring row by `offset`; it cannot express
"no record in this interval satisfies P".

**B5 — `best` presupposes an ordering the metadata does not carry.** *(new)* `selection_rule:
best` is available, but `M.RecordSelection.value` is `dataType: "decimal"` and RECIST response
is an ordinal **code** (CR ≺ PR ≺ SD ≺ PD ≺ NE). Nothing in the method, the transformation
library or the schema says what "best" means — not for a code, and not for a decimal either,
where best could be highest or lowest depending on the measure. The ordering is real, it is
clinical, and it lives entirely outside the model. Step 2 composes *syntactically* while the
semantics that make it correct are unstated.

This is the same species as F03: the structure is present and the meaning that distinguishes it
is not. Here it is not even in a `note`.

**B6 — no risk difference statistic exists.** *(new)* SAP §5.3 and §13.6 both specify the
population-level summary as a **stratified Mantel–Haenszel risk difference** with 95% CI.
`M.CMH` declares three output classes — `test_result` (`chi_squared`, `p_value`, `df`),
`association_measures` (`odds_ratio`, `CI_lower`, `CI_upper`) and `homogeneity_test`. It yields
an **odds ratio**, not a risk difference.

Nor is the statistic available anywhere else. `model/method/statistics_vocabulary.json` carries
`proportion`, `pct`, `cumulative_pct`, `odds_ratio`, `n_risk` — and no difference-of-proportions
statistic at all. Grepping the whole of `lib/` and `model/` for `risk_difference`,
`rate_difference` or equivalents returns nothing.

So the estimand's declared population-level summary cannot be expressed. Substituting the odds
ratio is not a workaround: it is a different estimand attribute, and ICH E9(R1) treats the
population-level summary as part of the estimand's definition.

**Also: `M.CMH` and `M.Proportion` have no transformation entries.** The only responder analysis
transformation is `T.Responder_ChiSq`, which uses `M.ChiSquaredTest` and binds `response` to
concept `Flag` as an input — the same shape as `T.OS_LogRank`, with the derivation assumed
already done. A stratified CMH analysis transformation would have to be authored. That is
ordinary library work, not a model gap, and unlike the TTE case the method it needs exists.

**Partly: the composite ICE strategy.** "No post-baseline assessment ⇒ non-responder" is a
missingness test, which is exactly what `M.ConditionalValue` does — the one case where its
hardwired `IS_NA` predicate is the right predicate. The other two composite branches
(discontinuation before adequate assessment; subsequent therapy before adequate assessment)
are two-variable date comparisons and fall to B1.

## Discrepancies in the source study

Five, all in ORR's chain, and none resolved here. Resolving them by inspection before authoring
would contaminate step 3. Recorded for `comparison.md` alongside PFS's D1 and D2.

**D3 — reader.** SAP §4.3 and §13.6 both specify **BICR** (`RSEVAL = "INDEPENDENT ASSESSOR"`).
`ADRS-spec.md` says ADRS derives OVR/BOR/CBOR from the **Investigator** reader *"to preserve the
established response semantics,"* noting *"A future SAP amendment can switch ADRS to BICR."*
BICR/Investigator discordance is ~10%. The built ADaM answers a different question from the one
the SAP asks.

**D4 — denominator.** SAP §13.6 gives E3 the Response Evaluable population and E3a the ITT
denominator as its sensitivity. `ADRS-spec.md` states the ORR denominator is *"All ITT subjects
(ITTFL = "Y"), including those with no post-baseline assessment."* The built dataset implements
the sensitivity estimand as the primary.

**D5 — confirmation rule.** SAP §4.3: *"a second CR or PR at a subsequent assessment ≥28 days
later with no intervening PD."* `ADRS-spec.md`: *"CR/PR require a confirmatory OVR of
equal-or-better ≥28 days later."* Two differences. *Equal-or-better* is not *a second CR or PR* —
under the SAP a CR may be confirmed by a PR, under the spec it may not. And the **no intervening
PD** clause is absent from the spec entirely.

**D6 — estimator.** SAP §4.3 specifies `admiralonco::derive_param_bor()` and
`derive_param_confirmed_bor()`. `ADRS-spec.md` v0.3 records both as *"hand-coded in `adrs.R`
(not `admiralonco`)."* The same pattern as D2 on ADTTE: the SAP delegates to a named library
function and the implementation diverged without the SAP being updated.

**D7 — `EFFFL` does not exist.** The SAP requires it in three places: §3's populations table
(*"`EFFFL = "Y"` on ADRS (not ADSL)"*, ~440 subjects), §13.6's E3 population, and §13.6's E3a
contrast. ADRS carries eighteen variables and `EFFFL` is not among them; the string does not
appear in `ADRS-spec.md` at all.

**Estimand E3 is therefore not implementable against the built ADaM as specified.** What was
built is E3a. D4 and D7 are the same defect seen from two directions.

## What this means for the tier

The moderate tier does what the ladder wanted of it: it separates what the framework handles
from what it does not, with enough of each to be informative.

Authoring is worth attempting here, unlike PFS. Steps 2, 3, 7, 8, 9 compose and would give the
first real authoring-cost measurement — including the E3/E3a pair, where two estimands differ by
one configured field, which is the clearest available demonstration of one derivation serving
two estimands.

What cannot be authored is the confirmation rule (B1, B4) and the risk difference (B6). The
honest form of the tier is a **partial chain**: author what composes, mark the confirmation step
as blocked, and record the cost of what was authored. That is more useful than either a complete
chain that quietly substitutes an odds ratio or an abandoned tier.

**Recommended next step.** ~~Author steps 2, 3, 7, 8 and 9 against the ITT denominator — which is
what exists (D4, D7) — and record the time.~~ **Superseded — see the addendum below.** None of
the five is authorable. Do **not** silently adopt the Investigator reader to match the built
ADaM; D3 remains open and would have gone into `comparison.md`, which is not written because
there is no derivation to compare.

## Addendum — what authoring showed (2026-09-16)

**The recommendation below was wrong, and is superseded by [`log.md`](log.md).**

It reads: *"Author steps 2, 3, 7, 8 and 9 … and record the time."* None of those five can be
authored. The mapping established that the **methods** compose, and inferred that the chain
could therefore be built. It cannot: the builder authors from **transformation templates**, and

| Method | Transformation entries |
|---|---|
| `M.Categorization` (step 7) | **none** |
| `M.Proportion` (steps 8, 9) | **none** |
| `M.CMH` (step 10) | **none** |
| `M.RecordSelection` (step 2) | `T.BaselineSelection` only, fixed at `last_non_missing` / `pre_treatment` |
| `M.ThresholdCompare` (step 3) | `T.ADAS_ScoreableCheck` only, fixed at *"≥ 8 of 11 items"* |

A shipped transformation's method configuration is not editable in the builder — the derivation
pipeline shows bindings only, and step 4's configuration panel covers the analysis
transformation alone. And no transformation can be created: the library is fetched read-only
and there is no add-transformation affordance in `ac-dc-app/js/`.

So ORR fails **differently from PFS**. PFS does not compose because the methods cannot express
the censoring hierarchy (F06). ORR's steps compose at method level exactly as mapped, and are
still unauthorable because nothing wraps those methods and nothing can be authored to.

What the builder does produce for an ORR-shaped endpoint is in [`chain.json`](chain.json):
`T.Responder_ChiSq` with `derivationChain: []` — the responder flag declared as source data,
and an unstratified chi-squared test the SAP does not ask for.

**This is the clearest argument yet for the method keeping steps 1 and 2 separate.** Step 1
works from the method and transformation libraries; step 2 works from what the application
exposes. The gap between them was invisible on paper and is the whole result of this tier.

## New findings

B5 and B6 are new and belong in `docs/findings/`. B1 and B4 are F06, confirmed on a second
endpoint, which strengthens it: the predicate gap is not a time-to-event problem, it is a
general derivation problem that TTE happened to surface first.
