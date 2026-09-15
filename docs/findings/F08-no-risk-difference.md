# F08 — No difference-of-proportions statistic exists

**Status: new.** Found while mapping ORR on paper. Blocks estimand E3's population-level summary.

## Claim

The framework cannot express a risk difference. TORIVA's ORR estimand requires one.

## Evidence

SAP §5.3 and §13.6 both specify the ORR population-level summary as a **stratified
Mantel–Haenszel risk difference** (torivumab − placebo) with 95% CI, strata = histology × region.

`M.CMH` declares three output classes:

| Output class | Statistics |
|---|---|
| `test_result` | `chi_squared`, `p_value`, `df` |
| `association_measures` | `odds_ratio`, `CI_lower`, `CI_upper` |
| `homogeneity_test` | `chi_squared`, `p_value`, `df` |

It yields an odds ratio. There is no risk difference.

Nor is the statistic available elsewhere. The proportion-related entries in
`model/method/statistics_vocabulary.json` are:

```
odds_ratio, n_risk, pct_missing, proportion, pct, cumulative_pct
```

No difference of proportions, no risk difference, no rate difference. Searching the whole of
`lib/` and `model/` for `risk_difference`, `rate_difference`, `prop_diff` and equivalents
returns nothing.

`M.Proportion` produces `proportion`, `pct`, `CI_lower`, `CI_upper` **per group** — the per-arm
summary, correctly, with a `ci_method` configuration covering Clopper–Pearson and Wilson. It
does not contrast groups.

## Why substituting the odds ratio is not a workaround

ICH E9(R1) makes the population-level summary an attribute of the estimand, alongside
population, variable, treatment and intercurrent-event handling. Reporting an odds ratio where
the estimand specifies a risk difference does not approximate the estimand — it answers a
different question, and for a common binary outcome the two diverge substantially.

The framework binds to USDM `Estimand` as a first-class class. An estimand whose declared
summary measure has no expressible statistic is a gap the model should be able to detect and
report, rather than one an author works around silently at authoring time.

## Scope

Narrower than [F06](F06-no-general-predicate.md), and cleanly fixable: this is a missing
statistic and a missing method, not a missing capability in the model. `M.CMH`'s output classes
would take an additional statistic, or a companion method for the stratified difference of
proportions would cover it.

But it is worth noting that binary endpoints with a risk-difference summary are routine, and
ORR is the second of two endpoints mapped here to hit a gap on its **analysis** side — which the
specification's ladder expected to be the settled half.

## Disposition

Drafted as Issue 4 in [upstream-issues.md](upstream-issues.md), and recommended as the **first**
to file: it is the smallest of the five, verifiable in a single file, and the fix is obvious.

## Related

There is also no transformation entry for `M.CMH` or `M.Proportion`. The only responder
analysis transformation is `T.Responder_ChiSq`, which uses `M.ChiSquaredTest` and binds
`response` to concept `Flag` as an input — the same already-derived shape as `T.OS_LogRank`
([F01](F01-no-tte-derivation-transformations.md)). That is ordinary library work rather than a
model gap, since the methods exist.
