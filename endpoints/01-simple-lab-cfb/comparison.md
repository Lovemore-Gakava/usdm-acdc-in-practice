# Lab change from baseline — comparison against built ADaM

Step 3 of the method, and `NORTH.md` **stage 7**. Rewritten 2026-09-17 once stage 6 had run:
this now compares an **executed result** against TORIVA's built ADLB, not a definition against a
specification.

Ground truth: TORIVA-LUNG 301 at `8534339d`, `datasets/adam/adlb.parquet` — 136,242 rows,
37 columns, converted to `adlb.xpt` for the builder. The executed runs are in
[`results.json`](results.json); the authoring decisions that produced them are L7 in
[`log.md`](log.md).

> **Updated 2026-09-17.** Until today this file compared *definitions* — the chain had never
> run — and said so in its scope limit. Stage 7 was marked green on that weaker reading and was
> taken back to red on 2026-09-17 (`NORTH.md`). Divergence 1 below is the same question that
> file asked on paper, now answered in numbers. Divergences 2 and 3 (specification errors D8, D9)
> are unchanged and kept at the end.

---

## The analysis compared

One ANCOVA, chosen because it is the simplest thing the chain can express and TORIVA's data can
answer: **change from baseline in ALT at analysis visit C2D1, safety population, adjusted for
baseline, torivumab vs placebo.** TORIVA's SAP specifies no laboratory analysis (D11), so the
reference is not a TORIVA table; it is the same model fitted to TORIVA's own `CHG` and `BASE`.

| | n | Torivumab − Placebo | SE | p |
|---|---|---|---|---|
| **Reference A** — TORIVA `CHG ~ BASE + TRT01P`, `AVISIT = C2D1`, `SAFFL = Y`, `ANL01FL = Y` | 432 | **−0.893** | 1.385 | — |
| Reference B — as A, every `AVISIT = C2D1` row (no `ANL01FL`) | 439 | −0.446 | 1.377 | — |
| **Engine run 1** — chain as authored through stage 4 | 432 | +0.381 | 0.495 | 0.44 |
| **Engine run 3** — dimensions switched to their DC forms | 432 | −1.025 | 1.282 | 0.42 |
| **Engine run 4** — as 3, covariate bound to `BASE` | 432 | **−1.830** | 1.768 | 0.30 |

None of the three runs reproduces the reference. Every one of them is **reproduced exactly**, to
four decimals, by a Python refit once the engine's actual data selection is known — so the gap
is not noise and not the arithmetic. It is three authoring choices and one selection rule.

## Divergence 1 — what the engine actually computed. **Authoring, then model limitation.**

Runs 3 and 4 were reproduced by refitting on the parquet with these rules
(`results.json` carries the engine console that establishes each one):

| | Engine | TORIVA |
|---|---|---|
| Rows in the cube | collected `VISIT == "C2D1"` — 435 rows, 432 with a baseline | `AVISIT == "C2D1"` — 442 rows |
| Response | `AVAL − AVAL(baseline)`, recomputed by the derivation | `CHG` |
| Baseline row | **first** row at `AVISIT == "Baseline"` per subject, in file order (`!duplicated(join_keys)`) | the `ABLFL = "Y"` row |
| Covariate, run 3 | `AVAL` **at C2D1** — the response's own minuend | `BASE` |
| Covariate, run 4 | `BASE` | `BASE` |
| Analysis-record flag | not applied | `ANL01FL = "Y"` |

**The baseline row is the whole of the remaining gap.** In the executed cube, **303 of 432
subjects (70.1%)** have an engine baseline that is not TORIVA's `BASE`, because their screening
draw and their Cycle 1 Day 1 pre-dose draw both window into the Baseline visit and the engine
takes whichever comes first. That is the 71% this file predicted on paper on 2026-09-16, now
measured in the result. Substituting the `ABLFL` row for the first row, and changing nothing
else, moves run 4 from −1.830 to −0.969 — within 0.08 of Reference A; what is left is
`ANL01FL` and the visit column.

Classification follows the method's three classes:

| Cause | Class | Fixable in the builder? |
|---|---|---|
| Covariate resolved to `AVAL`, not the baseline (run 3) | **Authoring error** — `BASE` was in the step 8 dropdown; the default was `AVAL`, and `execute_cube` skips the baseline join when the chosen column already exists | Yes — run 4 |
| Cube on collected `VISIT`, not `AVISIT` | **Authoring error** — the Timepoint dimension added in step 3 maps to `VISIT`; the DC form `AnalysisVisit` maps to `AVISIT` | Yes |
| Baseline = first row at `AVISIT = Baseline` | **Model limitation** — the chain can state the visit but not *which record in it*; TORIVA's rule is a flag ([F12](../../docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md)) | No |
| `ANL01FL` not applied | **Model limitation** — nothing produces it ([F11](../../docs/findings/F11-analysis-record-flag-has-no-transformation.md)) | No |

Run 1 is kept in `results.json` but not classified: two of its slice constraints were skipped
with a warning in the console (`Visit == Baseline` matched no rows because the dimension was the
OC form; `Observation.Identification.Topic` was not a column), the baseline join then used all
136,242 rows, and the run reported **complete**. It is the chain as it left stage 4.

## What this changes

Two things the definitional comparison could not say.

**The executed number is deterministic and explainable.** Three runs, three different answers,
each reproduced to four decimals from the console's own account of the selection. Nothing in
the divergence is opaque.

**The remaining gap has a size.** The model-limitation half — first row versus `ABLFL` row —
is worth **0.86** on a difference whose SE is 1.4, on 70% of subjects. On this endpoint it does
not change the conclusion (nothing here is significant). It is the number the paper comparison
could only predict.

---

## Divergence 2 — `ANRIND` and `BNRIND` do not exist. **Specification error. D8 confirmed.**

`ADLB-spec.md` lists #24 `BNRIND` and #25 `ANRIND` as derived L/N/H from `AVAL`/`BASE` against
`ANRLO`/`ANRHI`. The built dataset carries neither:

```
ANRIND present: False
BNRIND present: False
NRIND  present: True
```

`NRIND` is the SDTM predecessor renamed (`adlb.R:53`, `NRIND = LBNRIND`). The spec describes a
derivation; the code performs a rename. D8 is confirmed **against the data**, not just against
the spec, and closed.

Relevant to this project: had the spec's derivation been implemented, it would have needed a
predicate over a value and two per-record bounds — [F06](../../docs/findings/F06-no-general-predicate.md).

## Divergence 3 — `BTOXGR` does not exist. **Specification error. D9 confirmed.**

`ADLB-spec.md` #27 lists it and the T-LB-02 cross-reference names it. The data carries
`ATOXGR` and `ATOXGRN` and no baseline toxicity grade. Confirmed and closed.

## Non-divergence — the parts that agree

Recorded because a comparison that only lists failures is not a comparison.

| Check | Result |
|---|---|
| Record count vs `ADLB-spec.md` header (136,242) | **exact** |
| `CHG = AVAL − BASE` | holds on **135,421 / 135,421** rows carrying `CHG` |
| `BASE` = `AVAL` of the `ABLFL` record | holds on all 5,357 groups with a baseline |
| Groups with >1 `ABLFL='Y'` (P21 AD0154) | **0** |
| Groups with no `ABLFL` | 43 — consistent with SAP §12.3's retained-but-excluded rule |
| `ABLFL` and `ANL01FL` agreeing inside the baseline visit | **3,832 / 3,832** |

TORIVA's ADLB is internally consistent on every rule its SAP states. The divergence is not
between the SAP and the code; it is between the SAP and **what the concept model can say**.

---

## Reproduce

```
pip install pyarrow pyreadstat
git -C <toriva> sparse-checkout add /datasets/adam/adlb.parquet /datasets/adam/adsl.parquet
python tools/check_baseline_ambiguity.py --adlb <toriva>/datasets/adam/adlb.parquet
```

The engine runs are reproduced by the refits described in Divergence 1; the console for each
run, with the filter row counts, is in `results.json`.

## At `a806630` — the regenerated data (P7, 2026-09-20)

TORIVA issue #27 regenerated the data: 2:1 (300 : 150), no Cycle 1 Day 15 visit, time origin at
randomisation, `ANRIND`/`BNRIND`/`BTOXGR` in ADLB. The chain was executed again on it (`p7_rerun_a806630`
in `results.json`). New data, new numbers — and the same mechanism.

| | n | Placebo − torivumab | SE |
|---|---|---|---|
| **Reference A** — TORIVA `CHG ~ BASE + TRT01P`, `AVISIT = C2D1`, `SAFFL = Y`, `ANL01FL = Y` | 427 | **1.305** | 1.607 |
| **Engine** — the run-4 authoring, covariate `BASE` | 429 | **1.276** | 2.215 |
| Replica of the engine's selection outside the engine (first Baseline row, first C2D1 row, `BASE`) | 427 | 1.276 | 2.215 |

The engine is reproduced to four decimals by its own selection. The gap to the reference is the
baseline row again: **293 of 427 subjects (68.6%)** carry an engine baseline that is not
TORIVA's `BASE`, because the engine takes the first row in the Baseline window and TORIVA the
`ABLFL` row. At `8534339d` it was 70.1%. The regeneration changed the sign and the size of the
contrast (the data is simulated) and left the divergence untouched, which is the point: it is the
selection rule, not the data.
