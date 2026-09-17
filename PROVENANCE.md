# PROVENANCE.md — Development Record
# usdm-acdc-in-practice

Follows the convention used by the source study's own `SAP-PROVENANCE.md` and
`ADAM-PROVENANCE.md`.

---

## 1. Disclosure

This repository analyses two external repositories and records findings about them. It
contains **no clinical data**, real or synthetic. The study it references is fully synthetic
with a fictional sponsor and drug.

Substantially all prose in this repository was **drafted by an AI model** in a single session
on 2026-09-15 and has **not yet been reviewed line by line by a human**. The findings make
specific factual claims about a third party's public repository, five of which are drafted as
issues to be filed publicly. **Read §7 before filing anything.**

---

## 2. AI Model

| Property | Value |
|---|---|
| **Model** | `claude-opus-5[1m]` (Opus 5, 1M context) |
| **Interface** | Claude Code CLI |
| **Role** | Repository scaffolding; verification of inherited findings against pinned commits; drafting all finding write-ups, the PFS and ORR paper mappings, and the upstream issue drafts |
| **Human oversight** | Lovemore Gakava — authorised the work with "lets go with your recommendations"; directed the §15.2 correction and challenged the unverified launch claim |
| **Session date** | 2026-09-15 |
| **Review status** | **Not yet reviewed.** No finding has been independently confirmed by a human |

### Division of labour

| Artefact | Origin | Drafted by | Reviewed by |
|---|---|---|---|
| `docs/specification.md` (was `usdm-concept-spine-spec.md`) | Pre-existing, on disk at session start | LG (v0.1–v0.3) | LG |
| — its §5 disposition table and §17 v0.4 entry | This session | AI | Not yet |
| — its §15 actions 1 and 2 | This session, at LG's explicit direction | AI | LG directed, did not review text |
| `tools/acdc_divergence.py` | Pre-existing, on disk at session start | LG | LG |
| — its docstring §9 cross-reference | 2026-09-16 | AI | Not yet — see §7.5 |
| `tools/check_consistency.py`, `.githooks/pre-commit` | 2026-09-16 | AI | Not yet |
| `README.md` | Pre-existing; restructured 2026-09-17 so the findings sit after the stage work rather than second, per NORTH.md's "findings are a by-product" | LG, then AI | Not yet |
| `docs/findings/F01`–`F08`, `docs/findings/README.md`, `upstream-issues.md` | This session | AI | Not yet |
| `docs/findings/F09`–`F13`; F01, F07 and F09 amendments; Issues 3 and 5 rewritten | 2026-09-16 | AI | Not yet |
| `docs/review-plan.md` | 2026-09-16 | AI | Not yet — and it is the document that ends that |
| `NORTH.md` | 2026-09-16 | Destination sentence: **LG**. Finish line, test and prose: AI | Destination confirmed by LG |
| `study/usdm/toriva-lung-301.usdm.json`, `study/usdm/README.md` | 2026-09-16 | AI, from TORIVA's protocol synopsis and SAP §2 | Not yet |
| `study/m11/protocol-to-m11.md` | 2026-09-16 | AI, from the merged electronic ICH M11 v0.17.0 and TORIVA's protocol synopsis | Not yet |
| `study/m11/protocol/section-00-title-page.md`, `study/m11/protocol/section-03-objectives-endpoints.md`, `study/m11/protocol/section-12-01-clinical-laboratory-tests.md`, `study/m11/protocol/README.md` | 2026-09-16 | AI. **A derived work** — TORIVA's protocol §2/§6 and SAP §13 restructured to M11 §3. No estimand content invented; every attribute transcribed and cited | Not yet |
| `CLAUDE.md` | 2026-09-16 | AI | Not yet |
| — Issues 1–5 restructured requirement-first | 2026-09-16 | AI | Not yet — Issue 4 is a Tier 1 item, the rest Tier 2 |
| `docs/method.md` | This session | AI | Not yet |
| `study/README.md`, `study/source-refs.md` | This session | AI | Not yet |
| `docs/review-sheet.md` | 2026-09-17 | AI, at LG's request. Three claims from the stage work with their falsifiers; supersedes `review-plan.md` for what is in scope | Not yet |
| `endpoints/03-complex-pfs/mapping.md` | This session | AI | Not yet |
| `endpoints/02-moderate-orr/mapping.md` | This session, after this record was first written | AI | Not yet |
| `endpoints/01-simple-lab-cfb/mapping.md` | 2026-09-16 | AI | Not yet |
| `endpoints/01-simple-lab-cfb/chain.json` | 2026-09-16 | Authored in `ac-dc-app` by AI; serialised by the application | Not yet |
| `endpoints/01-simple-lab-cfb/comparison.md`, `log.md` | 2026-09-16 | AI | Not yet |
| `endpoints/02-moderate-orr/chain.json` | 2026-09-16 | Authored in `ac-dc-app` by AI; serialised by the application | Not yet |
| `endpoints/02-moderate-orr/log.md` | 2026-09-16 | AI | Not yet |
| `tools/check_baseline_ambiguity.py` | 2026-09-16 | AI | Not yet |
| `LICENSE`, `.gitignore`, `.gitmodules` | This session | AI | Not yet — see §7.4 |

---

## 3. Primary sources

Everything asserted in this repository derives from one of four sources. Nothing derives from
model recall about CDISC standards; where a claim could not be tied to a command against a
pinned commit, it is marked as inference in §5.

### 3.1 `cdisc-org/analysis-concepts` — the framework under analysis

| | |
|---|---|
| Commit | `739344ca31203bb502efeee2b855286e17977be6` (2026-06-17) |
| Included as | git submodule at `upstream/analysis-concepts`, read-only |
| Licence | MIT (code and scripts); CC-BY-4.0 (content — documentation, model files) |

Upstream's README §Re-use prescribes an attribution string, reproduced here as required:

> Content based on [CDISC Analysis Concepts (GitHub)](https://github.com/cdisc-org/analysis-concepts)
> used under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) license.

Material quoted from it in this repository: `StatisticalRole` enum and `InputRole` definitions
from `model/method/acdc_methods.schema.json`; `formula.generic_expression`, `configurations`,
`input_roles` and `output_specification` fragments from `lib/methods/**`; the proportion-related
entries of `model/method/statistics_vocabulary.json`; `bindings` and
`methodConfigurations` fragments from `lib/transformations/ACDC_Transformation_Library_v06.json`;
`confirmedTerminals` structure from the Scenario 2 study instance; and short line-referenced
excerpts from `ac-dc-app/js/**`. All are quoted for analysis and identified by file path.

F09 additionally quotes **application source** — the binding-editor gate in
`ac-dc-app/js/views/transformation-config.js`, the binding renderer in
`js/views/derivation-pipeline.js`, and the unresolved-placeholder note in
`js/utils/define-xml-generator.js` — each by file and line.

Also referenced, and **not** at the pinned commit: branch `estimands_01`. F02 cites commits
`505ef1a` and `8d03732` (Stuart Malcolm, 2026-08-14); **the branch has since moved well past
them**, merging PR #14. Re-checked 2026-09-16, when `upstream-issues.md` also gained the
repository-state table: `main` static since 2026-06-17, issues #11–#13 closed, #9 open, four
issues in the repository's lifetime. Those are observations of a live third-party tracker via
`gh issue list` and are true as at that date, not at a pinned commit.

### 3.2 TORIVA-LUNG 301 — the source study

| | |
|---|---|
| Repository | `OpenTrialReporting/torivumab-nsclc-301` |
| Commit | `8534339d95d6e1709f5def1e715a9b0c8cc06fe8` (2026-07-29) |
| Included as | **not included.** Referenced by commit; read in a scratch clone |
| Licence | CC BY 4.0. *"Synthetic data — educational use only."* |

Its README carries an explicit disclaimer, which governs how its content may be used here:

> **FICTIONAL EDUCATIONAL DOCUMENT — NOT FOR REGULATORY USE.** All identifiers, patient data,
> drug names, and results are completely synthetic. Celindra Therapeutics and torivumab are
> fictional.

Material quoted in this repository: SAP §4.2 (PFS definition, derivation and censoring rules),
§4.3 (ORR and the confirmation rule), §5.3 (ORR statistical methods), §3 (populations),
§13.5 and §13.6 (estimands E2 and E3 / E3a attribute tables); `programming-specs/ADTTE-spec.md`
(parameter table, key derivation notes, `STARTDT`/`AVAL`/`CNSR` definitions); and
`programming-specs/ADRS-spec.md` v0.3 (reader selection, denominator, confirmation rule,
estimator notes, variable list); and `programming-specs/ADLB-spec.md` (variable table, baseline
and windowing notes, shell cross-reference).

The lab tier additionally quotes **source code**, which earlier tiers did not: the baseline and
`ANL01FL` derivation block and the final `select()` of `programs/adam/adlb.R`, and the
`nrind_order` vector and `classify()` function of `programs/tfl/t_lb_01_shift.R`. These are
short excerpts identified by file and line, quoted for analysis under the study's CC BY 4.0
licence; the study is not redistributed.

**Its data was read for the first time on 2026-09-16** — `datasets/adam/adlb.parquet`, in a
scratch clone. Only aggregate counts and distributions are reported in this repository; no
subject-level values are reproduced, and the parquet is not vendored. The study is synthetic
with a fictional sponsor, so this raises no confidentiality question, but the same discipline
would apply if it were not.

**A derived work now lives here.** Until 2026-09-16 TORIVA was referenced and never
reproduced. `study/m11/protocol/` breaks that: it restructures TORIVA's protocol and SAP
content into ICH M11 form, which is a **derivative** of a CC BY 4.0 work. Permitted with
attribution, which the file carries, along with the source's "FICTIONAL — NOT FOR REGULATORY
USE" banner. It is a restructuring, not a rewrite: every estimand attribute is transcribed from
SAP §13 and cited to its section, and where the source has nothing — the laboratory estimand —
the derived document says so rather than filling the gap.

**Material caveat on "ground truth."** `study/README.md` and the specification both justify
choosing TORIVA on the basis that built ADaM provides ground truth. TORIVA's own
`sap/SAP-PROVENANCE.md` records that its SAP was drafted with AI assistance
(`anthropic/claude-sonnet-4-6`, Cowork) under LG's review, and is *"not intended for regulatory
submission"* and has *"not been reviewed by a regulatory authority."* The ADaM is real code
that really ran, so it remains a genuine check on whether a chain reproduces a built result —
but the *specification* it was built from is AI-drafted, human-reviewed, and synthetic. It is
ground truth for "does the concept model reproduce this pipeline," not for "does the concept
model reproduce regulatory-grade practice." The repository should not claim the latter.

### 3.3 The pre-existing specification

`docs/specification.md` (v0.3, formerly `usdm-concept-spine-spec.md`) was on disk at session
start, alongside the original `README.md` and `tools/acdc_divergence.py`, all timestamped
2026-09-15 16:46. Authored by LG before this session. It is the source of the endpoint ladder,
the four-step method, the Part B design, and findings F01–F05 as originally stated. <!-- consistency:ignore -->

**It is also the single largest source of corrected claims.** Four of its six §5 subsections
did not survive verification. See §17 of that document for the table.

### 3.4 Direct observation of the running application

Two sessions of direct observation, both against the shipped CDISC Pilot study in Chrome.

**2026-09-16**, for F09 and the lab tier's addendum: endpoint END5 *"Laboratory evaluations
(Change from Baseline)"*, concept category `Change (Comparison)`, analysis template *Change From
Baseline ANCOVA*, then the derivation pipeline. Observed: the subtrahend dependency offers nine
templates and `T.BaselineSelection` is not among them; the `parameter_baseline` slice panel
reads `Parameter {parameter}` / `AnalysisVisit Baseline`; `T.LOCF_Imputation`'s binding panel
lists `value`, `partition` ×2, `order` and a `+ Add binding...` control whose options are
concepts rather than roles; the string `time_order` appears nowhere in the rendered page.
`transformation-config.js`'s `renderInteractiveBindings` was additionally called directly
against the real library via the page context, returning a bare header for `time_order` with no
binding rows and no add control.

**2026-09-15**, for F05: running `ac-dc-app` and reading the rendered UI. Observations: eight numbered workflow steps plus a
Configuration entry; six tabs on Study Overview; the SoA matrix rendering 42 activities and 12
encounters on the default `studies.json`; each endpoint row rendering as a checkbox with ID,
badge and text under a "No endpoints selected" counter; no console errors or warnings on a
tracked reload.

---

## 4. What was verified by command, and how

Every finding was re-checked against the pinned commits rather than carried forward. The
commands are recorded in each finding file. Classes of evidence used:

| Claim type | Method | Example |
|---|---|---|
| Model **shape** | Read the schema at the pinned commit, cite `$defs` name and path | `StatisticalRole` enum (F02) |
| Library **contents** | Count or string-frequency, reproducible by a quoted command | `CNSR`/`AVAL` occurrences = 0 (F01) |
| **History** | `git log -S` over the submodule, distinguishing *removed* from *never present* | `censoring` never existed (F02) |
| **Application** behaviour | File and line citation, plus direct observation in-browser | `linkedBCIds` writes (F04), tab count (F05) |
| **Tool** output | `tools/acdc_divergence.py` run against the submodule | cluster counts (F03) |

Outcome of that pass over the five findings inherited from the specification, and the reason
§7.1 matters:

| | |
|---|---|
| Confirmed as stated | F01, F03 |
| Premise false, consequence intact | F02 |
| Retired | F04 |
| Overstated, restated | F05 |
| Found during verification | F06 |

F07 and F08 came later and by a different route: neither was inherited, and neither came from
inspecting the libraries. Both fell out of mapping ORR on paper (step 1 of the method) and were
then verified against the pinned commit by the same classes of evidence above — `M.RecordSelection`'s
`selection_rule` enum and `value` dataType for F07, `M.CMH`'s output classes and the contents of
`statistics_vocabulary.json` for F08. F09–F11 arrived the same way from the lab tier, and rest
on counts over `lib/methods/**` and `lib/transformations/**` that each file records a command for.

**Verification is not a single pass, and the first pass missed things.** Mapping the lab tier
disproved a premise in F01 and a proposed fix in F07, both of which had survived the original
check and both of which had been carried into upstream issue drafts:

| | |
|---|---|
| F01 | Asserted every derivation method declares exactly one `computed_value` output class. Two declare more — `M.UnitConversion` (2) and `M.WindowedVisitAssignment` (3) — and the latter belongs to `T.DeriveAnalysisVisit`, which F01 itself cites. Issue 3 rewritten |
| F07 | Proposed declaring the `best`/`worst` ordering on the concept. TORIVA's own shift table ranks `LOW = HIGH > NORMAL`, an ordering belonging to one analysis rather than to the scale. Issue 5 rewritten |

| F09 | Called three unbound `required` roles a conformance defect and inferred that nothing validates transformations against their methods. Both wrong: the binding editor iterates `method.input_roles`, so library entries are templates the author completes, and `define-xml-generator.js:705` does detect unresolved placeholders. The capability gap it reports is unaffected |

That is five findings now whose premise or fix did not survive — F01, F02, F04, F07, F09 — four
of them drafted for public filing. §7.1 should be read with that number in mind.

**A pattern across three of the five.** F04, F05 and F09 all went wrong the same way: a claim
about the *application* inferred from reading *library JSON*. F05 was corrected by serving the
app; F04 by reading the scenario file properly; F09 by reading the view source — **and that
reading was itself wrong**, corrected only when the app was served on 2026-09-16.

Anything this repository says about what an author can or cannot do in the builder is
unverified until the app has been run. Running it is cheap and has never yet been uninformative:
this session it overturned two of F09's three UI claims and produced a new observation about the
lab chain (B11) that no amount of reading had surfaced.

---

## 5. What is inference, not measurement

The distinction matters most where a finding drives an upstream issue. The following are the
AI's reasoning from verified facts, not themselves verified:

| Claim | Status |
|---|---|
| Time/event role collision *matters* because it breaks content-addressable identity | Inference. The role duplication is verified; the consequence for signatures is argued |
| The TTE gap is a **model** gap rather than a library gap (F01, B3) | Inference from output-cardinality counts. `upstream-issues.md` Issue 3 deliberately puts this to maintainers as a question rather than asserting it |
| PFS "does not compose" | Inference from four verified primitives. No authoring was attempted, by design — the method requires paper mapping first. A sufficiently inventive encoding may exist; none is obvious |
| ORR will hit F06 "less severely" at the BOR confirmation step | **Disproved.** Recorded here as speculation before ORR was mapped; the mapping shows ORR hits the same blocker on its *primary* derivation. The prediction is left visible in `endpoints/03-complex-pfs/mapping.md` rather than deleted |
| The SAP specifies no laboratory analysis | Established by exhaustive search, not inference: `ADLB` occurs six times in the 626-line SAP, all in §12.2/§12.3, plus one §7 row. That the *absence* is a defect rather than a scoping decision is the inference (D11) |
| The lab tier "composes, and is not analysed" | Inference of the same kind as the PFS and ORR rows. What is verified: the transformations and their configurations, and that no lab TFL reads `CHG`/`PCHG`/`BASE` |
| F12's core — `T.BaselineSelection` cannot resolve a `Measure` dependency | **Observed and verified.** Seen in the running builder, and independently derivable from `findDerivationsForConcept` plus the output-concept counts. Not inference |
| ORR "half composes" — 6 of 11 steps | Inference of the same kind as the PFS row. The primitives and their configurations are verified; that the remaining five steps have no encoding is argued, not proven |
| Reporting an odds ratio where the estimand specifies a risk difference "answers a different question" (F08) | Inference. The absence of a difference-of-proportions statistic is verified by search; that the substitution is not an approximation is a reading of ICH E9(R1) |
| `best` being undeclared "produces opposite results" for two identical chains (F07) | Inference. The enum value, the absent direction configuration and the `decimal` dataType are verified; the consequence is argued |
| ORR's five composable steps are unauthorable (F13) | **Observed**, by driving the builder, and corroborated by counting transformation entries per method and by the absence of any add-transformation affordance in `ac-dc-app/js/`. The inference is only that no other route exists — the app was exercised on one endpoint shape, not exhaustively |
| PFS drops from one composable step to zero authorable (F13) | **Inference, not observed.** `M.DateDifference` having no transformation entry is verified by count; that PFS's step 8 is therefore unauthorable follows, but PFS was never opened in the builder |
| F12's consequence — that `ABLFL` and `BASE` may therefore disagree | **No longer inference. Demonstrated.** `AnalysisVisit = Baseline` selects two records for 3,832 of 5,400 subject × parameter groups in `adlb.parquet`, differing in value in 96.8% of them, with a median 21.3% relative error in `BASE` if the non-flagged candidate is taken. Supersedes the row below, which was written before the data was read |
| ~~F12's consequence — inference, untested against data~~ | Superseded 2026-09-16 by the row above |
| `M.RecordSelection`'s formula/output mismatch is a defect | Inference. Both fragments are quoted; that they conflict is an argument |
| ~~Three transformations leaving a `required: true` role unbound means nothing validates transformations against their methods (F09)~~ | **Withdrawn 2026-09-16.** False: `define-xml-generator.js:705` detects unresolved placeholders, and the binding editor iterates `method.input_roles`, so library entries are templates by design |
| `time_order` cannot be bound through the builder's UI (F09, as corrected) | **Inference from source, not observation.** The `canAdd` gate and the derivation-pipeline renderer are quoted by line; that an author therefore has no way to supply an ordering has **not** been confirmed by running the app, and F05 is the precedent for that distinction mattering |
| `T.UnitConversion`'s facet pattern is "close to what a TTE derivation needs" (F01, as corrected) | Inference. The two facet bindings are quoted verbatim; that they are the right model for `AVAL`/`CNSR` is exactly what Issue 3 now asks maintainers rather than asserting |
| An enumerated window array makes metadata "a function of the data it describes" (F10) | Inference from the open-ended maintenance schedule in SAP §12.2. No run was attempted against a longer data cut |
| The `responseCodes` / `sdtmDatasetSpecialization` split is a constraint on §11 | Inference from counts across the two shipped files |
| Authoring-cost figures | **None exist.** No tier has been authored. The specification's "nine nested derivation steps" for ADAS-Cog is LG's pre-existing figure, not measured here |

---

## 6. Relationship to other documents

| Document | Relationship |
|---|---|
| `docs/specification.md` | The plan. Partly superseded — §5 carries a disposition table, §17 v0.4 the corrections |
| [`NORTH.md`](NORTH.md) | **The destination.** What "done" means, the eight-stage finish line, and the test every piece of work must pass. Read before anything else; everything below describes *how*, this says *what for* |
| `CLAUDE.md` | Working rules for an AI collaborator, pointing at `NORTH.md`. Loaded automatically at session start |
| `docs/method.md` | How the findings were verified, and why that step exists |
| `docs/review-plan.md` | What a human must review, in what order, and what to skip. **Nothing here is reviewed until its sign-off table is filled in** |
| `tools/check_consistency.py` | Enforces the counted claims in this record against the filesystem |
| `tools/check_baseline_ambiguity.py` | Tests F12 against built ADaM; reproduces every figure in the lab tier's `comparison.md` |
| `endpoints/01-simple-lab-cfb/` | The only tier with all four method steps complete |
| `docs/findings/` | The findings themselves, each with its evidence |
| `study/source-refs.md` | Pinned commits, sparse-checkout recipe, and the fourteen discrepancies found inside TORIVA (D1–D14) |
| `endpoints/03-complex-pfs/mapping.md` | Step 1 of the method for the complex tier |
| `endpoints/02-moderate-orr/mapping.md` | Step 1 of the method for the moderate tier; source of F07, F08 and D3–D7 |
| `endpoints/01-simple-lab-cfb/mapping.md` | Step 1 of the method for the simple tier; source of D8–D12, and of B11 → F12 |
| TORIVA `sap/SAP-PROVENANCE.md` | Provenance of the source SAP. Relevant to §3.2 |

---

## 7. Limitations and open provenance items

**7.1 Nothing here has been human-reviewed.** The findings assert errors in a third party's
public repository and five were drafted as public issues — **now parked, and not being filed**
(`docs/findings/upstream-issues.md`). The warning below stands as a statement about this
repository's reliability, not as a gate on a pending action.

**Five findings have now had a premise or a proposed fix disproved — F01, F02, F04, F07 and
F09.** Two were caught in the original verification pass; three survived it and were caught
later by unrelated work, which means the pass is necessary and not sufficient.

F09 is the sharpest warning of the five: it was written, verified, committed and **corrected
twice on the same day**. Its first wrong half inferred application behaviour from library JSON —
the identical mistake F05 made. Its first *correction* did the same thing again, and two of its
three parts were overturned when the application was finally served and driven. Only the core
capability claim survived both passes. Each of the five was wrong in a way a maintainer would
have seen immediately, because each concerned their own library.

That this keeps happening is evidence the verification step works and equally evidence that
confident-sounding claims in this repository can be wrong. **Review before filing** — `docs/review-plan.md` says what that means
in practice, tiered so that filing Issue 4 needs about two hours rather than a full pass.

**7.2 Generated output was committed in error.** `README.html` and `README_files/` (888 KB)
are Quarto 1.10.18 output produced outside this session at 18:04 on 2026-09-15. They were
swept into commit `031b9c8` by a `git add -A` and were never inspected before committing.
They vendor third-party libraries — Bootstrap, Popper, Tippy, clipboard.js, anchor.js — each
under its own licence, with no attribution recorded, in a repository whose stated design is to
reference rather than vendor. The render is also stale: it predates the §15.2 and F05
corrections. Untracked in a follow-up commit and added to `.gitignore`; the files remain on
disk. Recover with `git revert` if the render was meant to be published.

**7.3 The source SAP is AI-drafted.** See §3.2. This does not invalidate the ADaM comparison
but it bounds what the comparison demonstrates.

**7.4 The `LICENSE` copyright line was asserted, then confirmed.** It reads
`Copyright (c) 2026 Lovemore Gakava`, originally chosen by the AI from the git config and the
TORIVA spec authorship. LG confirmed on 2026-09-15 that this is a personal repository.
Resolved.

**7.5 `tools/acdc_divergence.py` had a stale cross-reference. Resolved.** Its docstring said it
*"Implements sections 4.1-4.4 of the Concept Spine specification"*; the signature design is at
§9.1–§9.4. Pre-existing, not introduced by the 2026-09-15 session. Corrected on 2026-09-16 to
cite §9.1–§9.4 and name the file. Only the citation was ever wrong; the behaviour was verified
against the pinned commit — see §7.8.

**7.6 The ADaM comparison has now been run, for one tier. Resolved in part.** `pyarrow` 25.0.1
was installed on 2026-09-16 and `datasets/adam/adlb.parquet` read — 136,242 rows, matching
`ADLB-spec.md`'s header exactly. This closed **D8 and D9 against the data** (`ANRIND`, `BNRIND`
and `BTOXGR` are absent) and produced the repository's first empirical result: the concept
model's baseline slice selects two records for 71% of subject × parameter groups, which differ
in value 96.8% of the time. See `endpoints/01-simple-lab-cfb/comparison.md`.

**It remains unrun for ORR and PFS**, and every claim about those two still derives from
TORIVA's markdown, not its data.
Discrepancies D1–D14 in `study/source-refs.md` are recorded as **open** precisely because
resolving them by inspection before authoring would contaminate step 3 of the method. D7 and
D11 are the sharpest — `EFFFL` does not exist on ADRS, so estimand E3 is not implementable
against the built ADaM as specified; and the SAP specifies no laboratory analysis at all, so
the only statement of what the two built lab tables compute is the R program that computes
them. D8–D12 are the first discrepancies here established partly from **source code**
(`programs/adam/adlb.R`, `programs/tfl/t_lb_01_shift.R`) rather than from specification prose,
which is a stronger class of evidence than the earlier seven rest on — but still not the built
data.

**7.7 All three endpoints are mapped; one is authored end to end and one was attempted.** The
lab tier completed steps 2, 3 and 4 on 2026-09-16, and was then **re-authored against TORIVA**
the same day once `study/usdm/` existed, with BCs linked (`NORTH.md` stage 2). **ORR completed
steps 2 and 4** and stopped there — the chain the builder will produce contains no derivation,
so there is nothing to compare against built ADaM. PFS remains at step 1.

Since the destination was rewritten, the endpoint ladder is **no longer the unit of progress**.
`NORTH.md`'s nine stages are, and the ladder's three tiers now serve it: the lab tier is the
endpoint being carried through, and ORR and PFS are the evidence for why it is that one.

ORR's result corrected its own mapping. The mapping recommended authoring five steps; none is
authorable, because no transformation wraps `M.Categorization`, `M.Proportion` or `M.CMH`, a
shipped template's method configuration is not editable in the builder, and no template can be
created. That was invisible from the libraries and is the clearest case so far for the method
keeping steps 1 and 2 distinct.

There is now a **structural** cost figure for one tier — zero new authoring, eleven decision
points, four of them not determined by the source SAP — but still no wall-clock figure, and
per §7.9 this process cannot honestly produce one. See
`endpoints/01-simple-lab-cfb/log.md`.

Two caveats travel with that figure. The chain was authored against the **CDISC Pilot's** END5,
not TORIVA, because TORIVA USDM fragments do not exist (specification §15.3); the endpoint shape
is right and the identifiers are not. And step 3 is consequently a comparison of *definitions*
against built ADaM, not a numeric diff of the authored chain's output.

**7.8 The submodule was uninitialised until 2026-09-16, and the tool output now reproduces.**
The 2026-09-15 session left `upstream/analysis-concepts` registered but not checked out, so
`docs/method.md`'s reproduce block would not have run for a reader following it. Initialised at
the pinned commit `739344c` on 2026-09-16 and `tools/acdc_divergence.py --compare-naive` run
against it. Every figure `docs/method.md` predicts holds: 60 methods, 25 transformations,
29/60 carrying no STATO coding; 2 method clusters on the full signature
(`M.ImputedValue_Mean`/`_Median`, `M.CumulativeCount`/`M.CumulativeFrequency`) and 3 on the
naive signature, the largest covering 18 entries; 1 transformation cluster. That cluster is
`T.ADAS_MissingScaleCapacity` + `T.ADAS_SumAvailableScores` at hash `152b97e6efa9` — the F03
false positive, matching the hash quoted in that finding — and the loose signature additionally
pulls in `T.ADAS_NonMissingCount`, also as F03 states.

This is the first claim in the repository confirmed by re-running rather than by re-reading.
It bears only on F03 and on the tool's behaviour; **it is not human review**, and every other
finding remains unreviewed per §7.1.

**7.9 The authoring-cost measurement, as specified, cannot be produced by this process.**
Specification §6.1 makes the cost per tier Part A's most valuable output, and the method's step
2 defines it operationally: *"Author each tier in the eSAP builder, recording elapsed time and
every point where a decision was needed."*

The elapsed time of an AI model hand-writing a scenario file is not a measurement of anything a
sponsor would plan against. It is not a statistician's time, it is not wizard time, and it does
not scale the way either does. Recording it as though it were the §6.1 figure would produce a
number that looks like evidence and is not — the failure mode this repository exists to avoid.

Two things can honestly be produced, and neither is a substitute for a timed human session:

- **Decision points**, which step 2 already asks for. Every place the SAP underdetermines the
  chain and an author must choose — the unbound `VisitDimension` on `T.BaselineSelection`, the
  undeclared `tieBreak` code, whether an enumerated window array is truncated — is countable,
  reproducible, and independent of who is authoring.
- **Structural cost**: transformations instantiated, bindings resolved, configurations set,
  and how many of those are forced by the SAP versus chosen by the author.

Both are properties of the chain rather than of the person, which makes them comparable across
tiers — the comparison §6.1 actually wants. Neither answers "how many hours". That question
needs a statistician in the builder with a stopwatch, and this repository should say so rather
than emit a proxy.

The three paper mappings already yield the decision-point count without any authoring, which is
worth noting: for PFS it is moot (nothing composes), for ORR and the lab tier it is small and
recorded in each `mapping.md`.

---

## 8. Change log

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-09-15 | AI (`claude-opus-5[1m]`), unreviewed | Initial record. Covers repository creation, the F01–F06 verification pass, the §15.2 correction, and the provenance defect at §7.2 |
| 0.2 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | Reconciled against work that landed **after** v0.1 was written. v0.1 was committed at 18:33 on 2026-09-15; the ORR mapping, F07, F08 and discrepancies D3–D7 landed between 18:37 and 18:52 in the same session and were never recorded here. Updated: issue count three → five (§1, §7.1); F01–F06 → F01–F08 and the ORR mapping added to the division of labour (§2); ORR source sections and `ADRS-spec.md` added to quoted material (§3.2); `statistics_vocabulary.json` added (§3.1); §4 scoped to the inherited five with F07/F08's provenance stated separately; the ORR "less severely" row in §5 marked **disproved** and three new inference rows added; §6 given the ORR mapping row; §7.6 D1–D2 → D1–D7; §7.7 corrected from one endpoint to two |
| 0.3 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | Initialised the `upstream/analysis-concepts` submodule at the pinned commit, which the 2026-09-15 session had registered but never checked out, and reproduced `docs/method.md`'s expected tool output against it (§7.8, new). Corrected the stale §9 cross-reference in `tools/acdc_divergence.py`'s docstring and marked §7.5 resolved |
| 0.4 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | Simple tier mapped on paper (`endpoints/01-simple-lab-cfb/mapping.md`), completing step 1 for the ladder. Five discrepancies added (D8–D12), the first established partly from TORIVA's **source code** rather than its specification prose. §7.7 rewritten: all three endpoints mapped, none authored, still no cost figure. §7.9 added — the cost measurement as specified in §6.1 cannot honestly be produced by this process, and what can be produced instead |
| 0.5 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | F09, F10 and F11 written up from the lab tier's B7, B8 and B10, each verified against `739344c` with a reproduce command. **F01 corrected** — its output-cardinality argument was false; `M.UnitConversion` and `M.WindowedVisitAssignment` declare two and three output classes. **F07 amended** — the lab shift table contradicts its concept-level-ordering fix. Upstream Issues 3 and 5 rewritten accordingly; F09–F11 recorded as candidates, not drafts, so the issue count stays at five. §4, §5, §7.1 and `docs/method.md` updated with the running tally of four disproved premises or fixes |
| 0.6 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | Three checks run before any filing. **Issue 4's premise verified** against SAP §5.3 and §13.6 verbatim, and strengthened: `risk difference` already ships in upstream's own STATO copy as `STATO_0000424`, and `estimands_01` is adding `SP_SUMMARY_MEASURE` for exactly the summary that has no statistic. **Upstream state checked** — `main` static since 2026-06-17, issue #11 closed, four issues in the tracker's lifetime, one active maintainer; nothing here is duplicated, and the filing recommendation is now Issue 4 alone. **F09 corrected the same day it was written** — its conformance-defect framing withdrawn; the capability gap stands and its UI consequence is recorded as an unverified source read. D13 added. Tallies in §4, §7.1 and `docs/method.md` raised to five, with the application-from-JSON hazard named |
| 0.7 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | `ac-dc-app` served and driven to settle F09's UI claims. **Two of the three were wrong**: the derivation pipeline does carry a `+ Add binding...` control, and `T.LOCF_Imputation` does supply an ordering — bound as `order`, a role name `M.ImputedValue_LOCF` does not declare, which is a smaller and more precise defect than "no transformation binds it". F09 corrected a second time; only its core capability claim (single-cardinality `time_order`, no tie-break) survived both passes. New observation recorded as B11 in the lab mapping: `T.BaselineSelection` outputs a `Flag` and is therefore **not** among the nine templates offered to resolve `T.ChangeFromBaseline`'s subtrahend, so the baseline flag and the baseline value are independent derivations. §3.4 now records both observation sessions |
| 0.8 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | B11 written up as **F12** — the baseline flag and the baseline value are disconnected. The first finding here **produced** by running the builder rather than corrected by it: `T.BaselineSelection` outputs a `Flag`, and `findDerivationsForConcept` matches on exact output-concept equality, so it can never resolve the `Measure` `T.ChangeFromBaseline` needs. Carries the visit-based/date-based mismatch against SAP §12.3, and two incidentals — every `Flag` being interchangeable (so the builder offers the baseline flag for a log-rank event indicator, F02 arriving operationally), and `Observation`/`Timing`/`TimeToEvent` being demanded by transformations that nothing can satisfy, which restates F01 structurally |
| 0.9 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | **Lab tier authored end to end** — the first tier to complete steps 2, 3 and 4, and the first time any claim here has been checked against data. `chain.json` authored in `ac-dc-app` and serialised by the application; `comparison.md` against `adlb.parquet`; `log.md` recording eleven decision points and zero new authoring. D8 and D9 **closed against the data**. F12's consequence moved from inference to demonstrated: the model's baseline slice selects two records for 71% of subject × parameter groups, differing in value 96.8% of the time, median 21.3% error in `BASE`. `tools/check_baseline_ambiguity.py` added and reproduces every figure. §7.6 and §7.7 rewritten |
| 1.0 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | **ORR authored — or rather, found unauthorable.** Its five composable steps have no transformation template (`M.Categorization`, `M.Proportion` and `M.CMH` have none at all; `M.RecordSelection` and `M.ThresholdCompare` have one each, fixed at other purposes), a shipped template's method configuration is not editable anywhere in the builder, and no template can be created — the library is fetched read-only and no add-transformation affordance exists. `chain.json` records what the builder does produce: `T.Responder_ChiSq` with `derivationChain: []`, the responder flag declared as source data, and an unstratified chi-squared test the SAP does not ask for. The mapping's closing recommendation is struck through and superseded. Also observed live: the builder offers **Overall Survival Log-Rank Test** for a `Flag` endpoint, and accepted **Baseline Selection** as the responder flag — F12's Flag-interchangeability incidental, on two independent paths |
| 1.1 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | **F13 written up** — the authoring surface is far narrower than the model. 39 of 60 methods (65%) have no transformation; 8 of 25 transformations are ADAS-Cog scaffolding, leaving six generic derivation entries; a shipped template's method configuration is not editable anywhere in the builder (verified in code at `endpoint-how.js:124`, which only ever receives analysis transformations, and live in step 6); and no template can be created. **This re-scores the ladder**: PFS drops from one composable step to zero authorable, because its one step needed `M.DateDifference`, which has no entry — recorded as a correction on the PFS mapping. `docs/method.md` gains a *Two libraries, two questions* section, since conflating the method and transformation surfaces produced wrong conclusions on two of three tiers. F13 is recorded in `upstream-issues.md` as probably **not** filable as written |
| 1.2 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | `docs/review-plan.md` added. Tiers the review by exposure rather than by artefact: Tier 1 is Issue 4 and its evidence chain only (~2 hours) and is the sole gate on public filing; Tiers 2–4 follow only if more is to be filed. Organised around the **five ways this repository has actually been wrong** — application behaviour inferred from JSON, one structural level read for another, method surface confused with authoring surface, a fix broken by a counter-example in the same study, and history asserted without `git log -S` — rather than around generic re-reading. Names which claims need a statistician, which need oncology knowledge, and which need someone who has used the app; and says explicitly what **not** to review. Carries a sign-off table; §7.1 is not to be softened until Tier 1 is signed |
| 1.3 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | **Issue 4 restructured to lead with the requirement**, the review plan's Tier 1 item. It now opens with ICH E9(R1) making the population-level summary an estimand attribute and the SAP specifying a stratified MH risk difference, states what the libraries provide, argues why the odds ratio is not a substitute, offers the STATO term and the `SP_SUMMARY_MEASURE` overlap as information rather than proposal, and closes with *Solution space — deliberately not chosen*, listing three shapes without picking one and offering to contribute once settled. Written after upstream issue #9, whose body records the maintainer rejecting an issue that specified solution choices before requirements. **Issues 1, 2, 3 and 5 still lead with a Suggestion** and are noted as needing the same treatment |
| 1.4 | 2026-09-16 | AI (`claude-opus-5[1m]`), unreviewed | Issues 1, 2, 3 and 5 restructured requirement-first, matching Issue 4. All five now run: the requirement, what the libraries provide today, then a solution space deliberately not chosen. Two gained an explicit admission rather than leaving the maintainer to infer it — **Issue 1** states that the gap was noticed because of this project's own signature tooling and invites being told the position-in-formula convention is sufficient; **Issue 2** states we are unsure whether multi-variable predicates are excluded by design and asks where the intended boundary is. **Issue 5** gained the counter-example that constrains its own fix (the shift table's `LOW = HIGH > NORMAL`), so the suggestion no longer proposes concept-level ordering alone. No factual claim was changed in any of the four |
