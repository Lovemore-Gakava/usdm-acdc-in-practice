# Gap register — everything found wrong in TORIVA's documents, with a disposition

Phase 2, stage **P0** (`NORTH.md`). Written 2026-09-19. One list of every gap this project
found in TORIVA-LUNG 301's document set — the eighteen discrepancies in
[`source-refs.md`](source-refs.md), the ICH M11 elements the protocol does not supply, and the
things the SAP never specified — each with a **disposition** that says where, if anywhere, it is
fixed. The dispositions are LG's decision of 2026-09-19: fixes are made **here, in the derived
M11 work**; TORIVA upstream is not changed and nothing is filed.

Dispositions used:

| Disposition | Meaning |
|---|---|
| **fix here** | corrected in this repository's derived protocol, SAP excerpt or USDM, with the correction marked |
| **sponsor decision** | the source does not contain the information and inventing it would make the document conformant and untrue; recorded as absent |
| **upstream only** | a defect in TORIVA's programming specs or data that a derived protocol cannot fix; carried into the alignment check (P3) as a known divergence |
| **resolved** | already fixed by phase 1 (stage 0b), verified by the checker |
| **not a study gap** | found on the way but belongs to the framework or to this project, not to TORIVA; excluded |

## Re-pinned to `a806630`, 2026-09-20

TORIVA issue #27 closed the same day it was filed: eighteen PRs, the data regenerated. Every row below
now says where it stands at `a806630`; the alignment tool passes with **0 warn**. What P6 supplied and the
source now carries (D14, D11/G7, G5, G6, G2's countries and sites) is retired in the derived sections and
kept as the record. D18 was found at the re-pin.

## Filed upstream, 2026-09-20

Every *upstream only* row below, and the documents-first rule, went to TORIVA as one issue by LG's
decision: [https://github.com/OpenTrialReporting/torivumab-nsclc-301/issues/27](https://github.com/OpenTrialReporting/torivumab-nsclc-301/issues/27). D14's data needs no change; D15, D16, D17, D1, D3, D7, D8, D9 are the
regeneration list. The alignment tool's WARNs are the acceptance test the issue names.

## Rule change under P6 (2026-09-20)

Phase 2's rule — *fix here means the derived work follows the built data* — was withdrawn by LG
on 2026-09-20, reviewing item 1 of the phase-2 sheet: **the documents are what get corrected;
programs and data are regenerated to follow them, later, in TORIVA.** The rows below were
re-taken under that rule. A row that changed keeps its earlier disposition, struck through.

## A. The eighteen discrepancies (D1–D18)

| ID | Area | Gap, in one line | Disposition | Action, and where |
|---|---|---|---|---|
| D1 | PFS | SAP time origin `RANDDT` and months; ADTTE built from `TRTSDT` in days | **resolved upstream at `a806630`** (#27, 2026-09-20; ~~upstream only~~) — upstream only | data/program diverges from SAP; P3 flags it. The derived SAP excerpt keeps `RANDDT` |
| D2 | PFS | SAP cites `admiral::derive_param_tte()`; code v0.3 uses explicit logic | **resolved upstream at `a806630`** (#27) — upstream only | documentation drift in the SAP; no protocol content |
| D3 | ORR | SAP specifies the BICR reader; ADRS derives from the Investigator reader | **resolved upstream at `a806630`** (#27, 2026-09-20; ~~upstream only~~) — upstream only | data diverges from SAP; P3 flags. Protocol §3 (E3) keeps BICR, as the source says |
| D4 | ORR | E3 population Response Evaluable; ADRS denominator is ITT | **resolved upstream at `a806630`** (#27) — upstream only | P3 flags; §3.2.2 keeps Response Evaluable |
| D5 | ORR | Two confirmation rules — SAP vs ADRS code | **resolved upstream at `a806630`** (#27) — upstream only | P3 flags; the SAP rule is the one in §3 |
| D6 | ORR | SAP names `admiralonco` functions; code is hand-written | **resolved upstream at `a806630`** (#27) — upstream only | documentation drift |
| D7 | ORR | `EFFFL` required by SAP and never built | **resolved upstream at `a806630`** (#27, 2026-09-20; ~~upstream only~~) — upstream only | P3 flags; the derived USDM's `RESPEVAL` population cites the protocol definition (§8.2), not the flag |
| D8 | Lab | `ADLB-spec` derives `ANRIND`/`BNRIND`; built ADLB renames `LBNRIND` | **resolved upstream at `a806630`** (#27, 2026-09-20; ~~upstream only~~) — upstream only | spec/program divergence; P3 flags |
| D9 | Lab | `ADLB-spec` lists `BTOXGR`; not built | **resolved upstream at `a806630`** (#27, 2026-09-20; ~~upstream only~~) — upstream only | as D8 |
| D10 | Lab | SAP §14 points at `tfl/TFL-SHELLS.md`, which does not exist | **resolved upstream at `a806630`** (#27) — upstream only | documentation gap |
| D11 | Lab | SAP specifies **no laboratory analysis**; two lab tables were built anyway | **resolved upstream at `a806630`** (SAP v0.3 §5.6/§5.7). Before: fix here — the analysis specified (P6; ~~sponsor decision + fix here as a stated choice~~) | §3.2.5 now specifies the descriptive laboratory summary (values and change by visit; reference-range shift; worst CTCAE grade with a grade ≥3 listing), safety population, which is what T-LB-01/02 built without a specification. This project's change-from-baseline models are demonstration analyses, marked (S1–S3). Whether TORIVA's SAP adopts this is the sponsor's, later |
| D12 | Lab | `ADLB-spec` header says v0.1 DRAFT; its change log says v0.3 | **resolved upstream at `a806630`** (#27) — upstream only | minor |
| D13 | ORR | SAP asks for a stratified MH **risk difference**; the named estimator returns an **odds ratio** | **resolved upstream at `a806630`** (#27) — fix here | the derived SAP excerpt for E3 states the risk difference and notes the estimator mismatch; P3 checks §3.2.2's Population-level Summary says "risk difference" |
| D14 | Design | Protocol: torivumab **monotherapy** vs placebo; SAP §13.2 and the built data (`TRT01P` = "Torivumab + Chemotherapy"): combination with carboplatin/pemetrexed | **resolved upstream at `a806630`** (#27, PR #33) — the source now states the combination; the P6 correction is retired and recorded. Before: fix here — the protocol corrected to the SAP (P6; ~~the data as ground truth~~) | A placebo-alone control does not exist in first-line NSCLC; the SAP, the blinding design and the data all describe an add-on. Title page, §3.0, §1.4, §4 and §6 corrected; the USDM's arms follow the corrected protocol. That the data agrees is incidental, not the reason. Sample-size benchmarking against monotherapy trials becomes a rationale gap in §10, noted |
| D15 | Design | Protocol says 2:1 randomisation (300:150); the shipped data is 1:1 (225:225), by TORIVA's own header note; the sample-size arithmetic was not re-derived | **resolved upstream at `a806630`** (#27, PR #50: data regenerated 2:1). Before: the protocol stands; upstream only for the data (P6; ~~fix here, 1:1 as ground truth~~) | 2:1 is what the protocol specifies and what §8.1's arithmetic was derived for. The USDM says 2:1; P3 reports the data's 1:1 as a divergence (WARN), to be regenerated in TORIVA |
| D16 | Schedule | Protocol §6.1: imaging Q6W for 12 months then Q12W; the data images Q6W throughout, to week 120 | **resolved upstream at `a806630`** (#27, 2026-09-20; ~~upstream only~~) — upstream only (P6 rule: the protocol stands, the data diverges) | `tools/check_alignment.py` reports it as WARN D16 from ADTR's `AVISIT` spacing after month 12. To be regenerated in TORIVA. Found 2026-09-20 during LG's review of item 3 |
| D17 | Schedule | Protocol §7.2 has no Cycle 1 Day 15 visit; the data has `C1D15` for nearly every subject | **resolved upstream at `a806630`** (#27, 2026-09-20; ~~upstream only~~) — upstream only (P6 rule) | WARN D17 in the alignment report. The USDM's schedule follows the protocol and has no C1D15 encounter; this project's MMRM (S2/S3) used the data's C1D15 as an induction visit, which is now recorded as a data-defined visit. Found 2026-09-20 |
| D18 | Document control | The synopsis at `a806630` is substantively amended (title, design, §3.5, §5.1, §7.2, §8.1, #27 notes) yet still states *Protocol Version 1.0, 22 March 2026*, and its document history ends at v1.1 (identifiers only) | **resolved upstream at `0f78331`** (#53 → PR #54, 2026-09-20; ~~upstream only~~) | found at the re-pin, 2026-09-20. M11 §12.3 Prior Protocol Amendments cannot be populated from it; the derived title page says so. A version/date bump and a history row are the fix. **Filed as [#53](https://github.com/OpenTrialReporting/torivumab-nsclc-301/issues/53)** on LG's yes to a draft shown first, 2026-09-20. Fixed the same evening: title page v1.2, 20 September 2026, Document History row for Amendment 1, SAP protocol reference updated. The derived title page now carries the version and the amendment elements from the source |

## B. ICH M11 elements the source protocol does not supply

| ID | M11 section | Gap | Disposition | Action |
|---|---|---|---|---|
| G1 | §3.1.1, §3.2.1 | 25 Required estimand elements (five per primary, four per secondary objective) held in SAP §13, not the protocol | **resolved** | moved by stage 0b into `protocol/section-03-objectives-endpoints.md`; the checker verifies the section and the USDM regenerated from it |
| G2 | Title page | Country/Region, Site, and the three Sponsor Approval Date elements — absent | **countries and sites now in the source at `a806630`** (synopsis table, 12 countries / 15 sites); approval date still supplied here. Before: fix here, supplied and marked (P6; ~~sponsor decision~~) | countries and site count from the trial's records (facts, not design); approval date = the v1.0 version date, stated as such; the two *Location* elements still absent. `section-00-title-page.md` |
| G3 | Title page | EudraCT number where M11 expects the EU CT number | **fix here** | corrected in `section-00-title-page.md` with the source value kept beside it |
| G4 | §12.1 | No analyte list in the protocol; the derived section sourced it from the ADaM programming spec | **fix here, marked** | already done and marked as backwards-sourced; stays marked. P3 checks the seven BCs in the USDM appear in §12.1 |
| G5 | §12.1 | Reference-range source and central-vs-local laboratory — absent from protocol and SAP | **now in the source at `a806630`** (§7.2, G5). Before: fix here, supplied and marked (P6; ~~sponsor decision~~) | central laboratory for analysed panels; local permitted for clinical management only. `section-12-01-clinical-laboratory-tests.md` |
| G6 | §8.4.2 | Vital-signs collection and interpretation procedures — absent | **now in the source at `a806630`** (§7.2, G6). Before: fix here, supplied and marked (P6; ~~sponsor decision~~) | standard procedure paragraph in `section-08-04-02-vital-signs.md` |
| G7 | §3.2.5 | No Population-level Summary for laboratory evaluations (the M11 side of D11) | **now in the source at `a806630`** (SAP §5.6/§5.7). Before: fix here, supplied and marked (P6; ~~sponsor decision~~) | descriptive summary specified in §3.2.5; S1–S3 remain demonstration analyses |
| G8 | all other sections | Eleven of fourteen M11 sections not yet restructured — eligibility, interventions, schedule of activities, statistics, and the rest | **fix here** | this is stage **P1**; `coverage.json` will carry the status of each |
| G9 | §8.2 | Screening/Baseline Assessments and Procedures (Required) — the source has no such section: the screening window sits in the §6.1 imaging table, the procedures only as the Screening column of §7.2 and in TORIVA's CRF strategy | **fix here, supplied and marked** (added 2026-09-20 on LG's decision, after the review's 2c search found where the content was) | supplied in section 08 as an §8.2 paragraph assembled from the source's own documents — window from synopsis §6.1, pregnancy-test timing from §4.1, procedure list from the §7.2 Screening column and the CRF strategy's Screening visit. Not in TORIVA issue #27; it is an assembly of what TORIVA already says, not a correction |

## C. Things the SAP never specified, which this project supplied

| ID | Gap | Disposition | Action |
|---|---|---|---|
| S1 | No laboratory analysis (D11): the lab endpoint's ANCOVA is this project's | **demonstration analysis, marked** (P6; was *fix here as a stated choice*) | not the specified laboratory analysis (§3.2.5, descriptive); section 10 says so |
| S2 | No vital-signs analysis: the MMRM and ANCOVA on SYSBP are this project's | **demonstration analyses, marked** (P6; was *fix here as a stated choice*) | the specified vital-signs analysis is descriptive by visit (§3.2.5, §8.4.2); section 10 says so |
| S3 | The induction-visit window for the MMRM (V-D14) | **fix here as a stated choice** | stated in the same section |

## D. Found on the way, not TORIVA's — excluded

| ID | What | Why excluded |
|---|---|---|
| X1 | The engine's baseline is the first row in the Baseline window; TORIVA's is the `ABLFL` row (70% / 74% of subjects) | the framework's rule, not a gap in the study; F11/F12 |
| X2 | `M.MMRM` had no R implementation | framework; V4/V5 |
| X3 | Category-declared bindings left unresolved on the selection path | framework; V1 |
| X4 | The two-rows-at-Baseline situation itself — screening and C1D1 pre-dose both windowed into Baseline | **not a gap**: SAP §12.2 and §12.3 specify it and the built data follows them exactly |

## What P3 will check

The alignment tool (stage P3) takes this register as its list: every row with disposition
**fix here** must be verifiable in the files named in its Action column, and every **upstream
only** row must be reported as a known divergence between the SAP excerpt and the built data
rather than silently passing.
