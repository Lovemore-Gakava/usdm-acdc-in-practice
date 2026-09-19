# Vital signs change from baseline — comparison against built ADaM

Step 3 of the method, and `NORTH.md` **stage 7** for the second endpoint. Written 2026-09-19 on
executed results, as the lab tier's was on the 17th.

Ground truth: TORIVA-LUNG 301 at `8534339d`, `datasets/adam/advs.parquet` — 52,920 rows,
30 columns — restricted to Baseline and the induction visits C1D15–C6D1 (23,793 rows) and
converted to `.xpt` for the builder. Both executed runs and both references are in
[`results.json`](results.json); the authoring is in [`log.md`](log.md).

## The analyses compared

Two chains on one endpoint, `END-S5-VS`, systolic blood pressure, safety population:

- **MMRM** — `T.CFB_MMRM_Primary`, every induction visit as the repeated factor, unstructured
  covariance, REML, Kenward–Roger. Executed with the `M.MMRM` implementation this project wrote
  ([`r_impl_mmrm.json`](r_impl_mmrm.json)), because upstream ships none (log V4).
- **ANCOVA** — `T.CFB_ANCOVA` at C2D1, the companion chain, executed with upstream's own
  `M.ANCOVA` implementation.

The SAP specifies no vital-signs analysis, so the references are the same models fitted to
TORIVA's own `CHG` and `BASE` — ANCOVA in Python, MMRM in local R with the `mmrm` package —
on `ANL01FL = "Y"` records.

## The numbers

Torivumab − placebo, mmHg. Engine figures are the sign-reversed `(Placebo) − (Torivumab)`
contrasts the engine reports.

| Visit | Engine MMRM | Replica of the engine's selection, R | Reference MMRM, R | Engine ANCOVA | Reference ANCOVA |
|---|---|---|---|---|---|
| C1D15 | +0.04 (1.87) | +0.04 (1.87) | +0.70 (1.37) | | |
| **C2D1** | **+1.38 (1.93)** | +1.38 (1.93) | **+1.95 (1.38)** | **+1.39 (1.94)** | **+1.96 (1.39)** |
| C3D1 | −1.17 (1.84) | −1.17 (1.84) | −0.66 (1.35) | | |
| C4D1 | −0.31 (1.84) | −0.31 (1.84) | +0.14 (1.39) | | |
| C5D1 | −3.43 (1.91) | −3.43 (1.91) | −2.99 (1.38) | | |
| C6D1 | +1.07 (1.88) | +1.07 (1.88) | +1.51 (1.44) | | |
| n | 2,605 rows / 446 subjects | 2,605 / 446 | 2,605 / 446 | 446 | 446 |
| AIC | 22,065.1 | 22,065.1 | 21,303.5 | | |

**Both engine runs are reproduced exactly** — the MMRM at every visit, to three decimals and to
the AIC; the ANCOVA to four decimals (+1.3862, SE 1.9375, LS means −1.393 / −2.779) — by
refitting outside the engine with its selection rule. Neither matches the reference.

## Divergence 1 — the baseline row, again. **Model limitation.**

The engine's baseline is the **first** row at `AVISIT = "Baseline"` per subject; TORIVA's is
the `ABLFL = "Y"` row. In ADVS they differ for **332 of 446 subjects (74%)**, because screening
and Cycle 1 Day 1 pre-dose both window into Baseline and the engine takes whichever comes
first. That is the same rule the lab tier found (70.1% there), now on a second domain and a
second analysis.

Its effect is larger under MMRM than under ANCOVA at a single visit, because the wrong baseline
enters the response at *every* visit: the engine's residual variance is about a third higher
(SEs 1.84–1.93 against 1.35–1.44), the AIC is 760 worse, and each visit's contrast moves by
0.4–0.7. No conclusion changes — the largest engine contrast, C5D1 at −3.43, has p = 0.07 in
the engine and 0.03 in the reference — but the direction of the error is not random: with the
first row as baseline, the covariate `BASE` (TORIVA's) no longer matches the response's
subtrahend, and the baseline slope collapses from −0.96 to −0.23.

Nothing in the authoring can fix this. The chain states the baseline *visit*; which record in it
is not expressible (F12), and `ANL01FL`, which would resolve it, is not derivable (F11).

## Divergence 2 — what the implementation had to decide. **Authoring — ours.**

Three rules live in `r_impl_mmrm.json` that an MMRM needs and the framework's data layer does
not supply:

| Rule | Why | Where the reference did the same |
|---|---|---|
| One row per subject and visit, first kept | `mmrm` refuses duplicate time points; `lm` had taken the first silently | `!duplicated` in the R script |
| Drop the visit at which every subject's change is zero | a change-from-baseline model has no baseline row; the endpoint slice has no visit filter and cannot say "≠ Baseline" | the reference's visit list excludes Baseline |
| Copy response and covariate to syntactic names | `mmrm` cannot parse the engine's `__col_*` derived column in a formula | not needed |

Each is a decision an implementation should not have to make. The first two are the same
two-rows-at-Baseline problem arriving through the execution layer instead of the data layer.

## Divergence 3 — the visit window. **Authoring — ours, recorded.**

The uploaded ADVS was cut to Baseline plus six induction visits (V-D14). The full dataset has
some forty analysis visits including thirty maintenance cycles, and an unstructured covariance
over forty visits is not a fit anyone runs. The cube's visit dimension can hold one value, not
a set, so the window had to be applied to the data before upload. The reference uses the same
window.

## Non-divergence — the parts that agree

| Check | Result |
|---|---|
| Rows at C2D1, engine vs reference | 446 = 446 — ADVS has no duplicate draws at post-baseline visits, so `ANL01FL` changes nothing here |
| Subjects in the MMRM | 446 = 446 |
| The DC dimension forms | `Parameter == "Systolic Blood Pressure"` and `AnalysisVisit == "C2D1"` filtered as authored — no skipped constraints this time |
| Engine MMRM vs replica | identical at every visit; AIC identical |
| Engine ANCOVA vs replica | identical to four decimals |

## Classification

| # | Divergence | Class |
|---|---|---|
| 1 | Baseline = first row in the window, not `ABLFL` — 74% of subjects, residual variance up a third under MMRM | **Model limitation** (F12, F11) |
| 2 | Three rules an MMRM needs that had to be written into the implementation | **Authoring (this project's)** |
| 3 | Induction-visit window applied before upload | **Authoring (this project's), recorded** |

No authoring errors of the lab tier's kind: the covariate was `BASE` and the visit dimension the
DC form from the start, which is what a second pass is for.

## Reproduce

```
pip install pyarrow pyreadstat
Rscript -e 'install.packages(c("mmrm","emmeans","arrow"))'
```

`results.json` carries both engine consoles with their filter counts, and both references with
their scripts' selection rules in `log.md` V5; the Python ANCOVA reference is the same refit as
the lab tier's, on `advs.parquet`.
