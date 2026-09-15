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
specific factual claims about a third party's public repository, three of which are drafted as
issues to be filed publicly. **Read §7 before filing anything.**

---

## 2. AI Model

| Property | Value |
|---|---|
| **Model** | `claude-opus-5[1m]` (Opus 5, 1M context) |
| **Interface** | Claude Code CLI |
| **Role** | Repository scaffolding; verification of inherited findings against pinned commits; drafting all finding write-ups, the PFS paper mapping, and the upstream issue drafts |
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
| `README.md` | Pre-existing; Findings, Structure and Status sections rewritten this session | LG, then AI | Not yet |
| `docs/findings/F01`–`F06`, `README.md`, `upstream-issues.md` | This session | AI | Not yet |
| `docs/method.md` | This session | AI | Not yet |
| `study/README.md`, `study/source-refs.md` | This session | AI | Not yet |
| `endpoints/03-complex-pfs/mapping.md` | This session | AI | Not yet |
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
`input_roles` and `output_specification` fragments from `lib/methods/**`; `bindings` and
`methodConfigurations` fragments from `lib/transformations/ACDC_Transformation_Library_v06.json`;
`confirmedTerminals` structure from the Scenario 2 study instance; and short line-referenced
excerpts from `ac-dc-app/js/**`. All are quoted for analysis and identified by file path.

Also referenced, and **not** at the pinned commit: branch `estimands_01`, commits `505ef1a`
and `8d03732` (Stuart Malcolm, 2026-08-14, unmerged). Cited in F02 and `upstream-issues.md`.

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
§13.5 and §13.6 (estimands E2 and E3 attribute tables), and `programming-specs/ADTTE-spec.md`
(parameter table, key derivation notes, `STARTDT`/`AVAL`/`CNSR` definitions). Quoted as short
excerpts for analysis; the study is not redistributed.

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
the four-step method, the Part B design, and findings F01–F05 as originally stated.

**It is also the single largest source of corrected claims.** Four of its six §5 subsections
did not survive verification. See §17 of that document for the table.

### 3.4 Direct observation of the running application

F05 rests partly on running `ac-dc-app` against the shipped CDISC Pilot study in Chrome on
2026-09-15 and reading the rendered UI. Observations: eight numbered workflow steps plus a
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

Outcome of that pass, and the reason §7.1 matters:

| | |
|---|---|
| Confirmed as stated | F01, F03 |
| Premise false, consequence intact | F02 |
| Retired | F04 |
| Overstated, restated | F05 |
| Found during verification | F06 |

---

## 5. What is inference, not measurement

The distinction matters most where a finding drives an upstream issue. The following are the
AI's reasoning from verified facts, not themselves verified:

| Claim | Status |
|---|---|
| Time/event role collision *matters* because it breaks content-addressable identity | Inference. The role duplication is verified; the consequence for signatures is argued |
| The TTE gap is a **model** gap rather than a library gap (F01, B3) | Inference from output-cardinality counts. `upstream-issues.md` Issue 3 deliberately puts this to maintainers as a question rather than asserting it |
| PFS "does not compose" | Inference from four verified primitives. No authoring was attempted, by design — the method requires paper mapping first. A sufficiently inventive encoding may exist; none is obvious |
| ORR will hit F06 "less severely" at the BOR confirmation step | **Speculation.** Not mapped. Flagged as the next thing to do |
| `M.RecordSelection`'s formula/output mismatch is a defect | Inference. Both fragments are quoted; that they conflict is an argument |
| The `responseCodes` / `sdtmDatasetSpecialization` split is a constraint on §11 | Inference from counts across the two shipped files |
| Authoring-cost figures | **None exist.** No tier has been authored. The specification's "nine nested derivation steps" for ADAS-Cog is LG's pre-existing figure, not measured here |

---

## 6. Relationship to other documents

| Document | Relationship |
|---|---|
| `docs/specification.md` | The plan. Partly superseded — §5 carries a disposition table, §17 v0.4 the corrections |
| `docs/method.md` | How the findings were verified, and why that step exists |
| `docs/findings/` | The findings themselves, each with its evidence |
| `study/source-refs.md` | Pinned commits, sparse-checkout recipe, and the two discrepancies found inside TORIVA |
| `endpoints/03-complex-pfs/mapping.md` | Step 1 of the method for the complex tier |
| TORIVA `sap/SAP-PROVENANCE.md` | Provenance of the source SAP. Relevant to §3.2 |

---

## 7. Limitations and open provenance items

**7.1 Nothing here has been human-reviewed.** The findings assert errors in a third party's
public repository and three are drafted as public issues. F02 and F04 as *originally* written
would both have been wrong; they were caught by verification, which is evidence the method
works and equally evidence that confident-sounding claims in this repository can be wrong.
Review before filing.

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

**7.4 The `LICENSE` copyright line was asserted, not confirmed.** It reads
`Copyright (c) 2026 Lovemore Gakava`, chosen by the AI from the git config and the TORIVA spec
authorship. Confirm the correct holder — an employer may have a claim.

**7.5 `tools/acdc_divergence.py` has a stale cross-reference.** Its docstring says it
*"Implements sections 4.1-4.4 of the Concept Spine specification"*; the signature design is at
§9.1–§9.4 of the current specification. Pre-existing, not introduced here. Its behaviour was
verified against the pinned commit; only the citation is wrong.

**7.6 The ADaM comparison has not been run.** `pyarrow` is not installed and no parquet has
been read. Every claim about TORIVA derives from its markdown specifications, not its data.
Discrepancies D1 and D2 in `study/source-refs.md` are recorded as **open** precisely because
resolving them by inspection before authoring would contaminate step 3 of the method.

**7.7 Only one endpoint has been mapped.** The simple and moderate tiers are untouched.

---

## 8. Change log

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-09-15 | AI (`claude-opus-5[1m]`), unreviewed | Initial record. Covers repository creation, the F01–F06 verification pass, the §15.2 correction, and the provenance defect at §7.2 |
