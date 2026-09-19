# Vital signs change from baseline (MMRM) — paper mapping

Step 1 of the method, for the second endpoint. Written 2026-09-19 from the transformation
library at upstream `739344c` — `lib/transformations/ACDC_Transformation_Library_v06.json` —
before the analysis was selected in the builder. The lab tier's lesson applies: step 1 reads the
*transformation* library, not the method library, because only what has a template can be
authored (F13).

## The endpoint

`END-S5-VS` — vital signs, under the safety objective OBJ-S5, added to the USDM fragment from
the restructured M11 §8.4.2 ([`../../study/m11/protocol/section-08-04-02-vital-signs.md`](../../study/m11/protocol/section-08-04-02-vital-signs.md)).
The parameter carried is **systolic blood pressure**, BC `C25298`. The SAP specifies no
vital-signs analysis, so the analysis is this project's choice, made for what it exercises:
**change from baseline by MMRM**, every post-baseline visit as the repeated factor.

## The chain on paper

`T.CFB_MMRM_Primary` — *Change From Baseline MMRM Primary Analysis*, method `M.MMRM`:

| Role | Concept | Slice | Note |
|---|---|---|---|
| response | `Change` | endpoint | derived by `T.ChangeFromBaseline` (the one candidate; auto-selected, as L3) |
| covariate | `Measure` | `parameter_baseline` | `ParameterDimension = {parameter}`, `VisitDimension = {baseline_visit}` — the same slice as the ANCOVA, so the same two-rows-at-Baseline question: 340 of 450 subjects for SYSBP |
| repeated_factor | *by category:* `VisitDimension` | — | no concept in the library; resolved from the endpoint's category pick |
| fixed_effect | `Treatment` | — | |
| repeated_subject | `Subject` | — | |
| constraint | *by category:* `ParameterDimension` | — | likewise resolved from the pick |

Method configuration shipped with the template: covariance `UN`, estimation `REML`, degrees of
freedom `KR`. Outputs: LS means and contrasts indexed by treatment × visit, type-3 tests, fit
statistics, covariance parameters.

**Composes on paper**, with one derivation and no new authoring — the lab tier's shape with the
visit dimension promoted from a slice value to a model factor.

## What is expected to differ from the lab tier

- **No single visit is chosen** (the lab tier's D21). MMRM takes every post-baseline visit;
  the decision that replaces it is which visits count and the covariance structure.
- **Two bindings are declared by category rather than by concept** — `repeated_factor` and
  `constraint`. Whether the builder resolves them from the step 3 picks is a step 4 question.
- **The DC dimension forms are chosen up front** — `Parameter (DC)`, `AnalysisVisit (DC)` —
  because stage 6 of the lab tier showed the engine filters on dimension names as literal
  columns and the OC forms have no column in ADaM.
- **The covariate is `BASE` from the start** (the lab tier's D22).

## Reference for stage 7

The same model fitted to TORIVA's own `CHG` and `BASE` in ADVS, with `mmrm::mmrm` in local
R 4.6 — Python has no MMRM. Fixed effects `TRT01P × AVISIT + BASE`, unstructured covariance
by `AVISIT` within `USUBJID`, REML, Kenward–Roger; LS means and the treatment contrast at each
visit via `emmeans`. `ANL01FL = 'Y'` rows, and a second fit without it, as for the lab tier.
