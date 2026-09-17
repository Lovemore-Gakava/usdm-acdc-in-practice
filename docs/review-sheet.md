# Review sheet — three claims to check before stage 5

Written 2026-09-17, for LG, to be worked through offline.

This is **not** [`review-plan.md`](review-plan.md), which is parked. That plan is ordered by
filing risk — its Tier 1 is titled *"blocks filing Issue 4"* — and since nothing is being filed,
three of its four *"what only a human can do"* judgements no longer apply. Only one survives:
**is the clinical or statistical reading right?**

So this sheet drops the five upstream issues entirely and asks that question of the **stage
work** instead. The selection rule was: *which claim, if wrong, costs a stage that is green or
one that is about to be attempted?*

Three qualified. **Item 1 was withdrawn the same day** — see its banner; the selection rule let
in a framework-adequacy question, which is the drift this project guards against. Items 2 and 3
stand, protect stages 0, 0b and 1, and gate nothing: neither blocks stage 5.

**How to use it.** Each item states the claim so it can be disagreed with, then lists what would
*falsify* it. Read for the falsifiers, not for general plausibility — §3 of the review plan
explains why that distinction has already mattered here five times. Record a verdict at the
bottom.

---

## 1. The baseline result — `endpoints/01-simple-lab-cfb/comparison.md`

> # ⏸ WITHDRAWN — 2026-09-17, the day it was written
>
> **LG: *"why are we comparing against the SAP again?"*** Because this item had drifted. It asks
> whether the concept model can express what the SAP specifies — the framework-adequacy question,
> in a repository whose README had been restructured hours earlier to remove exactly that frame.
>
> Falsifiers **1a** and **1d** were checked before it was withdrawn, and both results stand:
>
> - **1a does not fire.** In all 3,832 pairs the two Baseline rows are identical on `PARAM`,
>   `PARAMCD`, `AVALU`, `LBCAT`, `ANRLO`, `ANRHI` and `DTYPE`, and differ on `LBSEQ`, `LBDTC`,
>   `ADT`, `ADY`, `VISIT`, `VISITNUM`, `ABLFL`, `ANL01FL`. Two draws, not a unit variant, a second
>   parameter or an imputed record. Collected `VISIT` is `('C1D1','SCREENING')` in 3,832 of 3,832.
> - **1b's quotations verify verbatim.** SAP §12.2 and §12.3, including *"The selection is
>   date-based, not visit-based"*.
> - **1d: the sheet described the statistic wrongly.** 21.3% is the median across all 3,832
>   ambiguous groups, not across the 3,710 that differ — that figure is 22.2%. Across all 5,400
>   subject × parameter groups it is 9.8%. `comparison.md` uses the first and does not say so.
>
> **The question this item was trying to answer belongs to stage 6.** Once the chain executes it
> computes a `BASE`; whether that matches TORIVA's is then arithmetic, needing nobody's
> adjudication. Carried forward as a thing to look at in stage 6's output, not as a verdict.

**Priority: highest.** It is the only claim in this repository checked against data, it is what
stage 7 asserts, and stage 6's number will be read against it.

> **The claim.** `AnalysisVisit = Baseline` is not a key. It selects **two** records in 3,832 of
> 5,400 subject × parameter groups (71%), those two differ in value in 96.8% of cases, and the
> concept model has no way to choose between them — because the flag that disambiguates them
> (`ABLFL`) is derivable only as a `Flag`, which can never resolve a `Measure` dependency. A chain
> that passes the builder therefore computes a `BASE` differing from TORIVA's by a **median
> 21.3%**.

**Needs:** you, twice over — as someone who has used the builder, and as the author of TORIVA's
programming specs (`study/README.md` already flags that as a bias risk).

### What would falsify it

| # | Falsifier | Why it is live |
|---|---|---|
| 1a | **The grouping key is wrong.** If the two rows at `AVISIT='Baseline'` are distinguished by something other than draw — a unit variant, a second `PARAMCD`, a repeat assay — then "two candidate records" is an artefact of the read, not a property of the data | This is failure mode **B** in review-plan §3: one level of a structure read, a conclusion drawn about another. It has produced two real errors here. The script groups on `USUBJID × PARAMCD`; the finding rests on collected `VISIT` being `('C1D1','SCREENING')` in all 3,832 |
| 1b | **SAP §12.2 is misread.** The claim takes §12.2 to mean *"inside the `Baseline` visit the `ABLFL='Y'` record wins"* and §12.3's definition to be **date-based** (last non-missing on or before `TRTSDT`). If the operative rule is something else, the whole divergence dissolves | You wrote these specs. Nothing else in the repository can check this |
| 1c | **There is a route through the model I did not find.** The claim is that no derivation template can produce a `Measure` representing the baseline value. `log.md` D7 records the ten options actually offered — LOCF, seven ADAS-Cog helpers, a unit conversion, and `(raw)` | Failure mode **A**: three findings went wrong inferring app behaviour from library JSON. This one *was* checked in the app, which is why it is credible — but it was checked once, by me |
| 1d | **The 21.3% is the wrong statistic.** It is the median absolute relative difference across the 3,710 groups where the two candidates differ — not across all 5,400 | If the intended denominator is all groups, the headline number is smaller |

### Re-run

```
git -C <toriva> sparse-checkout add /datasets/adam/adlb.parquet
python tools/check_baseline_ambiguity.py --adlb <toriva>/datasets/adam/adlb.parquet
```

Re-running catches **1a** and **1d**. It cannot catch **1b** or **1c** — which is the point of
review-plan §3.

---

## 2. The M11 estimand claim — `study/m11/protocol-to-m11.md`

**Priority: second.** It is the headline of stage 0 *and* the entire justification for stage 0b
rewriting protocol §3. If it is wrong, a protocol section was restructured for nothing.

> **The claim.** M11 §3.1.1 Primary Objective has seven Required elements, five of which are ICH
> E9(R1) estimand attributes — Population `C70833`, Treatment `C49236`, Population-level Summary
> `C188853`, Intercurrent Event Strategy `C188857`, Description of Intercurrent Event `C188856`.
> The same five repeat under §3.2.1 per secondary objective. TORIVA supplies none of them in the
> protocol, so it **fails 30 required elements across six objectives**.

**Needs:** a regulatory reading of M11. The consistency checker counts elements; it cannot tell
you whether "Required" means what I took it to mean.

### What would falsify it

| # | Falsifier | Why it is live |
|---|---|---|
| 2a | **Incorporation by reference satisfies the element.** If M11 permits a protocol to cite the SAP for the estimand attributes, TORIVA does not *fail* — it under-specifies, which is a much weaker claim and would not have justified stage 0b | This is the central judgement. I asserted strict requirement from the element's `Required` flag alone |
| 2b | **"Required" is conditional or differently scoped.** If the five are required once per protocol rather than once per objective, the count is **5**, not 30. If they are required only when §3.1.1 is populated at all, the framing changes again | The multiplication 6 × 5 = 30 is mine, not M11's |
| 2c | **The six objectives are not all §3.1.1/§3.2.1.** The doc notes §3.3.1 exploratory carries **6** Required rather than 7. If any of TORIVA's six sit under §3.3.1, the five do not all repeat and the arithmetic is wrong | Checkable by anyone against `section-03-objectives-endpoints.md`. One primary + five secondary is the assumption |
| 2d | **The element parse is wrong.** Names, Required status and CDISC codes were parsed from the merged electronic M11 v0.17.0 — see the Method note at the foot of the file | Mechanical, and the cheapest thing here to spot-check: pick two codes and confirm them |

---

## 3. The layering claim — `study/usdm/README.md`

**Priority: third, and shortest.** Ten minutes. It is the conceptual spine everything else
assumes: *protocol + CDISC Library → USDM; SAP → DC/AC.*

> **The claim.** USDM is a study-definition model, so the protocol is its source — objectives,
> endpoints, arms, population, BCs. The SAP feeds only DC and AC. **Estimand content is the one
> exception**, and TORIVA misplaces it into SAP §13.

### What would falsify it

| # | Falsifier | Why it is live |
|---|---|---|
| 3a | **`ITT` and `SAF` are not protocol-native either.** The claim now rests on exactly this split: `RESPEVAL` and `RESPONDER` came through the estimand's Population attribute, `ITT` and `SAF` from the protocol. **If TORIVA's protocol does not define its analysis sets, and those two also came from SAP §13.1, the exception is not estimand content — it is analysis-set content generally**, and the layering needs restating | **This is the one genuinely open question on the sheet.** TORIVA is referenced, not vendored, and the sections restructured under stage 0b do not include a populations section, so it was not checked. It needs the protocol open |
| 3b | **A further class needs the SAP.** The claim is a universal over USDM classes but was tested against the handful the fragment authors. `activities`, `scheduleTimelines` and `encounters` are deliberately absent | A universal claim from a partial fragment. Worth one sceptical pass |

**Already corrected here, 2026-09-17:** this section said *"one exception: the `Estimand` class"*
and named `Estimand_E1` the single displaced object. Two of the four `AnalysisPopulation` objects
cite SAP §13.6/§13.7, so the exception is one category wider than stated. The correction is in
place and is the reason 3a is now the sharp question rather than a general one.

---

## Verdicts

| Item | Verdict | Date | Notes |
|---|---|---|---|
| 1 — baseline result (falsifiers 1a–1d) | | | |
| 2 — M11 estimand claim (2a–2d) | | | |
| 3 — layering (3a–3b) | | | |

Use **holds / narrower than stated / wrong**. "Narrower than stated" is the most likely outcome
and has been the right verdict five times already — record *how much* narrower, in the source
file, rather than deleting the claim.

**If item 1 does not hold**, stage 7 comes down and `NORTH.md`'s status table should stop
claiming it. **If item 2 does not hold**, stage 0's headline needs restating; stage 0b's
restructure stands either way, since the M11 sections are correct regardless of whether the
omission counts as a failure.

## What this sheet deliberately leaves out

- **The five upstream issues.** Parked. Reviewing them to a filing standard buys a decision
  already made.
- **F06 and F13** — the two most interesting findings. Neither gates stage 5 or 6: F06 blocks
  PFS, F13 blocks ORR, and neither tier is being carried.
- **F04.** Retired. Read the disposition, not the finding.
- Everything else in review-plan §9, which still holds.
