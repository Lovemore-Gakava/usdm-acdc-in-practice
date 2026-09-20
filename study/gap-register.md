# Gap register — everything found wrong in TORIVA's documents, with a disposition

Phase 2, stage **P0** (`NORTH.md`). Written 2026-09-19. One list of every gap this project
found in TORIVA-LUNG 301's document set — the seventeen discrepancies in
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

## Rule change under P6 (2026-09-20)

Phase 2's rule — *fix here means the derived work follows the built data* — was withdrawn by LG
on 2026-09-20, reviewing item 1 of the phase-2 sheet: **the documents are what get corrected;
programs and data are regenerated to follow them, later, in TORIVA.** The rows below were
re-taken under that rule. A row that changed keeps its earlier disposition, struck through.

## A. The seventeen discrepancies (D1–D17)

| ID | Area | Gap, in one line | Disposition | Action, and where |
|---|---|---|---|---|
| D1 | PFS | SAP time origin `RANDDT` and months; ADTTE built from `TRTSDT` in days | **upstream only** | data/program diverges from SAP; P3 flags it. The derived SAP excerpt keeps `RANDDT` |
| D2 | PFS | SAP cites `admiral::derive_param_tte()`; code v0.3 uses explicit logic | **upstream only** | documentation drift in the SAP; no protocol content |
| D3 | ORR | SAP specifies the BICR reader; ADRS derives from the Investigator reader | **upstream only** | data diverges from SAP; P3 flags. Protocol §3 (E3) keeps BICR, as the source says |
| D4 | ORR | E3 population Response Evaluable; ADRS denominator is ITT | **upstream only** | P3 flags; §3.2.2 keeps Response Evaluable |
| D5 | ORR | Two confirmation rules — SAP vs ADRS code | **upstream only** | P3 flags; the SAP rule is the one in §3 |
| D6 | ORR | SAP names `admiralonco` functions; code is hand-written | **upstream only** | documentation drift |
| D7 | ORR | `EFFFL` required by SAP and never built | **upstream only** | P3 flags; the derived USDM's `RESPEVAL` population cites the protocol definition (§8.2), not the flag |
| D8 | Lab | `ADLB-spec` derives `ANRIND`/`BNRIND`; built ADLB renames `LBNRIND` | **upstream only** | spec/program divergence; P3 flags |
| D9 | Lab | `ADLB-spec` lists `BTOXGR`; not built | **upstream only** | as D8 |
| D10 | Lab | SAP §14 points at `tfl/TFL-SHELLS.md`, which does not exist | **upstream only** | documentation gap |
| D11 | Lab | SAP specifies **no laboratory analysis**; two lab tables were built anyway | **fix here — the analysis specified** (P6; ~~sponsor decision + fix here as a stated choice~~) | §3.2.5 now specifies the descriptive laboratory summary (values and change by visit; reference-range shift; worst CTCAE grade with a grade ≥3 listing), safety population, which is what T-LB-01/02 built without a specification. This project's change-from-baseline models are demonstration analyses, marked (S1–S3). Whether TORIVA's SAP adopts this is the sponsor's, later |
| D12 | Lab | `ADLB-spec` header says v0.1 DRAFT; its change log says v0.3 | **upstream only** | minor |
| D13 | ORR | SAP asks for a stratified MH **risk difference**; the named estimator returns an **odds ratio** | **fix here** | the derived SAP excerpt for E3 states the risk difference and notes the estimator mismatch; P3 checks §3.2.2's Population-level Summary says "risk difference" |
| D14 | Design | Protocol: torivumab **monotherapy** vs placebo; SAP §13.2 and the built data (`TRT01P` = "Torivumab + Chemotherapy"): combination with carboplatin/pemetrexed | **fix here — the protocol corrected to the SAP** (P6; ~~the data as ground truth~~) | A placebo-alone control does not exist in first-line NSCLC; the SAP, the blinding design and the data all describe an add-on. Title page, §3.0, §1.4, §4 and §6 corrected; the USDM's arms follow the corrected protocol. That the data agrees is incidental, not the reason. Sample-size benchmarking against monotherapy trials becomes a rationale gap in §10, noted |
| D15 | Design | Protocol says 2:1 randomisation (300:150); the shipped data is 1:1 (225:225), by TORIVA's own header note; the sample-size arithmetic was not re-derived | **the protocol stands; upstream only for the data** (P6; ~~fix here, 1:1 as ground truth~~) | 2:1 is what the protocol specifies and what §8.1's arithmetic was derived for. The USDM says 2:1; P3 reports the data's 1:1 as a divergence (WARN), to be regenerated in TORIVA |
| D16 | Schedule | Protocol §6.1: imaging Q6W for 12 months then Q12W; the data images Q6W throughout, to week 120 | **upstream only** (P6 rule: the protocol stands, the data diverges) | `tools/check_alignment.py` reports it as WARN D16 from ADTR's `AVISIT` spacing after month 12. To be regenerated in TORIVA. Found 2026-09-20 during LG's review of item 3 |
| D17 | Schedule | Protocol §7.2 has no Cycle 1 Day 15 visit; the data has `C1D15` for nearly every subject | **upstream only** (P6 rule) | WARN D17 in the alignment report. The USDM's schedule follows the protocol and has no C1D15 encounter; this project's MMRM (S2/S3) used the data's C1D15 as an induction visit, which is now recorded as a data-defined visit. Found 2026-09-20 |

## B. ICH M11 elements the source protocol does not supply

| ID | M11 section | Gap | Disposition | Action |
|---|---|---|---|---|
| G1 | §3.1.1, §3.2.1 | 25 Required estimand elements (five per primary, four per secondary objective) held in SAP §13, not the protocol | **resolved** | moved by stage 0b into `protocol/section-03-objectives-endpoints.md`; the checker verifies the section and the USDM regenerated from it |
| G2 | Title page | Country/Region, Site, and the three Sponsor Approval Date elements — absent | **fix here, supplied and marked** (P6; ~~sponsor decision~~) | countries and site count from the trial's records (facts, not design); approval date = the v1.0 version date, stated as such; the two *Location* elements still absent. `section-00-title-page.md` |
| G3 | Title page | EudraCT number where M11 expects the EU CT number | **fix here** | corrected in `section-00-title-page.md` with the source value kept beside it |
| G4 | §12.1 | No analyte list in the protocol; the derived section sourced it from the ADaM programming spec | **fix here, marked** | already done and marked as backwards-sourced; stays marked. P3 checks the seven BCs in the USDM appear in §12.1 |
| G5 | §12.1 | Reference-range source and central-vs-local laboratory — absent from protocol and SAP | **fix here, supplied and marked** (P6; ~~sponsor decision~~) | central laboratory for analysed panels; local permitted for clinical management only. `section-12-01-clinical-laboratory-tests.md` |
| G6 | §8.4.2 | Vital-signs collection and interpretation procedures — absent | **fix here, supplied and marked** (P6; ~~sponsor decision~~) | standard procedure paragraph in `section-08-04-02-vital-signs.md` |
| G7 | §3.2.5 | No Population-level Summary for laboratory evaluations (the M11 side of D11) | **fix here, supplied and marked** (P6; ~~sponsor decision~~) | descriptive summary specified in §3.2.5; S1–S3 remain demonstration analyses |
| G8 | all other sections | Eleven of fourteen M11 sections not yet restructured — eligibility, interventions, schedule of activities, statistics, and the rest | **fix here** | this is stage **P1**; `coverage.json` will carry the status of each |

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
