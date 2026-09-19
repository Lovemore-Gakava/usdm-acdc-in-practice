# Contribution package — an R implementation for `M.MMRM`, offered to `cdisc-org/analysis-concepts`

**Decided 2026-09-19 by LG:** offer the implementation upstream. **Prepared here, not filed.**
Nothing leaves this repository until LG files it, under LG's name. This is a contribution of
working code, which is a different thing from the five parked issue drafts; the rule that those
are not filed stands.

## What is offered

One entry for `lib/method_implementations/r_implementations.json`, in the registry's own shape
(`methodOid`, `language`, `packages`, `function`, `callTemplate`, `outputMapping`,
`documentation`, `notes`), for the method the library ships with a template
(`T.CFB_MMRM_Primary`) and a definition (`lib/methods/analyses/M.MMRM.json`) but no
implementation in either the R or the SAS registry at `739344c`.

The entry is [`../endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json`](../endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json).
For upstream, its `$comment` and the project-specific sentences in `notes` come out; the
three rules stay, because they are what the entry does.

## What it does

`mmrm::mmrm` on the engine's cube: fixed effects baseline covariate, treatment, visit and
treatment-by-visit; within-subject covariance over visits from the `covariance_structure`
configuration (`UN` → `us`, `CS` → `cs`, `AR1` → `ar1`, `TOEP` → `toep`, `CSH` → `csh`,
`ARH1` → `ar1h`); `estimation_method` REML or ML; `df_method` Kenward–Roger or Satterthwaite.
LS means and pairwise contrasts at each visit via `emmeans`; type-3 tests via
`emmeans::joint_tests`; fit statistics; the estimated covariance matrix flattened to
`covariance_parameters`. All six of the method's output classes are populated.

Verified: on TORIVA-LUNG 301's ADVS (446 subjects, six induction visits, systolic blood
pressure) the engine's result is identical at every visit and in AIC to the same model fitted
in local R 4.6 with `mmrm` — `endpoints/04-vitals-cfb-mmrm/comparison.md`.

## Three rules the entry carries, and why — the part a reviewer should look at

The engine's cube is not what `mmrm` expects, in three ways an ANCOVA never exposed:

1. **One row per subject and visit.** The endpoint slice has no visit filter, so the cube carries
   every Baseline-window row — two per subject for most subjects. `lm` took the first silently;
   `mmrm` refuses duplicate time points. The entry keeps the first, which is the engine's own
   convention (`!duplicated` on join keys) elsewhere. *This is a convention, not a statistical
   choice, and the reviewer may prefer the engine to resolve it upstream of any method.*
2. **No baseline row in a change-from-baseline model.** The slice cannot say `≠ Baseline`. The
   entry drops the visit at which every subject's change is zero — the baseline visit by
   construction. *Same comment: better solved in the cube than in a method.*
3. **Syntactic names.** The engine's derived response is `__col_<transformation>_Change_0`, which
   `mmrm`'s formula parser does not accept. The entry copies response and covariate to
   syntactic names before the fit.

And one thing the engine would have to do for the entry to run unattended: **install the
packages an implementation declares.** The `packages` list is not acted on; a fresh WebR session
reports *"there is no package called 'mmrm'"* until `webr::install("mmrm")` is run.

## A second, separate observation the contribution would carry — V1

Selecting an analysis template whose bindings are declared by **concept category**
(`T.CFB_MMRM_Primary`: `repeated_factor` → `VisitDimension`, `constraint` → `ParameterDimension`;
`T.CFB_ANCOVA`'s two constraints likewise) copies them into the endpoint's analysis with
`concept` undefined, and every subsequent render of step 4 throws in `resolveRoleNames`
(`transformation-linker.js:733`). The resolution rule exists — `buildPipelineGraph`'s
`resolveBindingConcept`, from the endpoint's `dimensionCategoryPicks` — on the pipeline path and
not on the selection path. Applying it at selection fixes both templates. Two lines; recorded in
`endpoints/04-vitals-cfb-mmrm/log.md` V1. Worth offering with the entry, because without it the
entry cannot be reached through the UI.

## What LG decides before filing

- The **form**: a pull request adding the entry (and, if wanted, the V1 change), or an issue
  offering it. Check upstream's contribution guidance first; at `739344c` the repository carries
  no `CONTRIBUTING.md` (verified 2026-09-19).
- The **licence line**: upstream is MIT and CC BY 4.0; the entry can carry either.
- The **name** it goes under, and the wording of the three-rules paragraph, which is the part
  that invites discussion.

## What is not offered

The findings. The five drafted issues stay parked. This package is an implementation and a fix
that makes it reachable, offered because they run — not an assessment of the library.
