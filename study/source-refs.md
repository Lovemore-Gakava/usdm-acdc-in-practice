# Source references

TORIVA-LUNG 301 is **referenced by commit, not vendored**. It is ~81 MB and read-only input.

| | |
|---|---|
| Repository | `OpenTrialReporting/torivumab-nsclc-301` |
| Commit | `0f78331b5b0c5e1af12cc429bfba090a978879ac` — re-pinned 2026-09-20 after issue #53 closed (Protocol v1.2). Before: `a8066307b976351b53a9ffa447a69047306e4cb9` after #27 (P7, same day), `8534339d95d6e1709f5def1e715a9b0c8cc06fe8` (2026-07-29) through P6. Datasets unchanged between the last two |
| Date | 2026-07-29 |
| Branch | `main` |

To work with it without a full clone:

```
git clone --filter=blob:none --no-checkout \
    https://github.com/OpenTrialReporting/torivumab-nsclc-301.git toriva
cd toriva
git sparse-checkout init --no-cone
git sparse-checkout set /sap/SAP.md /protocol/synopsis.md \
    /programming-specs/ADTTE-spec.md /programming-specs/ADRS-spec.md \
    /programming-specs/ADLB-spec.md
git checkout main
```

**On Git Bash for Windows**, prefix the `sparse-checkout set` with `MSYS_NO_PATHCONV=1`. MSYS
rewrites each leading-slash pattern into a Windows path — `/sap/SAP.md` becomes
`C:/Program Files/Git/sap/SAP.md` — and the checkout silently produces an empty working tree
with no error. Verified while fetching the sources for the lab tier.

## Sections used

| Tier | SAP | Programming spec | ADaM target |
|---|---|---|---|
| Simple — lab CFB | §12.3 (baseline definition), §12.2 (analysis visits) | `ADLB-spec.md` | ADLB |
| Moderate — ORR | §4.3 (derivation), §5.3 (statistical methods), §3 (populations), §13.6 (estimand E3 / E3a) | `ADRS-spec.md` v0.3 | ADRS `PARAMCD = "CBOR"`, `AVALC`, `RSPFL`; ADSL `ORRFL` |
| Complex — PFS | §4.2, §13.5 (estimand E2 / E2a) | `ADTTE-spec.md` | ADTTE `PARAMCD = "PFS"` |

SAP is 626 lines with nine estimands (E1, E1a, E1b, E2, E2a, E3, E3a, E4, E5) in an explicit
ICH E9(R1) table at §13.

## Ground truth

Built ADaM as parquet, 450 subjects: `datasets/adam/adtte.parquet`,
`onco_phase3_solid/adam/adtte.parquet`. ADTTE expects 2,377 records across OS, OSWOT, PFS,
PFSINV, TTR (450 each) plus DOR restricted to confirmed responders.

Reading these needs `pyarrow`, which is not a dependency of anything else here. It is only
required at step 3 of the method (`comparison.md`), not before.

**First read 2026-09-16.** `datasets/adam/adlb.parquet` — 136,242 rows, 37 columns, matching
`ADLB-spec.md`'s header count exactly. See `endpoints/01-simple-lab-cfb/comparison.md` and
`tools/check_baseline_ambiguity.py`. Note that `pyarrow.dataset` is blocked by Application
Control on this machine, so `pq.read_table` fails; `pq.ParquetFile(...).read()` works and is
what the tool uses.

## Known discrepancies inside the source

**Status at `a806630` (2026-09-20):** the first seventeen (D1 to D17) resolved by TORIVA issue #27 (the register says how, row by row); D18 found at the re-pin, filed as TORIVA [#53](https://github.com/OpenTrialReporting/torivumab-nsclc-301/issues/53), **resolved at `0f78331`** (PR #54: Protocol v1.2, 20 September 2026, with the Amendment 1 history row).

Recorded during the paper mappings; to be resolved against built ADaM at comparison time, not
here. D1 and D2 came from PFS — see
[endpoints/03-complex-pfs/mapping.md](../endpoints/03-complex-pfs/mapping.md). D3–D7 came from
ORR — see [endpoints/02-moderate-orr/mapping.md](../endpoints/02-moderate-orr/mapping.md).
D8–D12 came from the lab tier — see
[endpoints/01-simple-lab-cfb/mapping.md](../endpoints/01-simple-lab-cfb/mapping.md).

| ID | Endpoint | SAP says | Built spec says |
|---|---|---|---|
| **D1** | PFS | Time origin `RANDDT`; §13.5 says months | `STARTDT` = `TRTSDT`; `AVALU` = DAYS |
| **D2** | PFS | `admiral::derive_param_tte()` (§4.2, §13.5) | v0.3: stale `derive_param_tte()` references removed, code uses explicit logic |
| **D3** | ORR | **BICR** reader (`RSEVAL = "INDEPENDENT ASSESSOR"`), §4.3 and §13.6 | ADRS derives OVR/BOR/CBOR from the **Investigator** reader; ~10% discordance |
| **D4** | ORR | E3 population = Response Evaluable; ITT is the E3a sensitivity | ORR denominator is all ITT — the sensitivity estimand is what was built |
| **D5** | ORR | Confirmation = *"a second CR or PR ≥28 days later with no intervening PD"* | *"a confirmatory OVR of equal-or-better ≥28 days later"* — different rule, and no intervening-PD clause |
| **D6** | ORR | `admiralonco::derive_param_bor()` / `derive_param_confirmed_bor()` | Both hand-coded in `adrs.R`, not `admiralonco` |
| **D7** | ORR | `EFFFL = "Y"` on ADRS, required in §3, §13.6 twice (~440 subjects) | **`EFFFL` does not exist.** ADRS carries 18 variables; the string is absent from the spec |
| **D8** | Lab | `ADLB-spec.md` #24/#25: `BNRIND`/`ANRIND` derived L/N/H from `AVAL`/`BASE` vs `ANRLO`/`ANRHI` | **Neither exists.** Built ADLB renames the SDTM predecessor (`adlb.R:53`, `NRIND = LBNRIND`); the shift table uses that one column for both ends |
| **D9** | Lab | `ADLB-spec.md` #27: `BTOXGR`, baseline toxicity grade; named in the T-LB-02 cross-reference | **Does not exist.** `adlb.R` selects `ATOXGR`, `ATOXGRN` only |
| **D10** | Lab | SAP §14: TFL crosswalk *"to be completed in `tfl/TFL-SHELLS.md`"* | That file does not exist at `8534339d`. Three lab TFL programs exist and ran |
| **D11** | Lab | SAP §4 and §5 specify **no laboratory analysis**; ADLB appears only in §12.2/§12.3/§7 conventions | T-LB-01 and T-LB-02 were built. Their only specification is a shell cross-reference in `ADLB-spec.md`; the authoritative rule lives in the R program |
| **D12** | Lab | `ADLB-spec.md` header: *"Spec version 0.1 DRAFT"* | Its own change log records v0.3 (2026-07-24). Minor |
| **D14** | Design | Protocol title, §2.1 and IMP describe torivumab **monotherapy** versus placebo in PD-L1 TPS ≥50% — no chemotherapy anywhere (0 mentions of carboplatin, pemetrexed or "chemotherapy backbone") | SAP §13.2's Treatment attribute specifies torivumab **+ carboplatin AUC5 + pemetrexed** versus placebo + identical backbone. Two different trials. Found by the M11 restructure, which forces Treatment into the protocol where it sits next to the title |
| **D15** | Design | Protocol: **2:1** randomisation, 450 = 300 : 150 (synopsis table, §3.1, §8.1) | The source's own header: shipped data generated **1:1 (225 : 225)** by `programs/raw/01_demographics.R`; *"the sample-size arithmetic … was not re-derived for 1:1"*. Found 2026-09-19 reading the synopsis whole for P1 |
| **D13** | ORR | SAP §5.3 and §13.6: population-level summary is a **stratified MH risk difference** | §13.6's estimator is `stats::mantelhaen.test()`, which returns a common **odds ratio**, not a risk difference. The SAP specifies one statistic and names a tool that produces another |
| **D16** | Schedule | Protocol §6.1: imaging **every 6 weeks for the first 12 months, every 12 weeks from month 12** | ADTR `AVISIT` runs `TUMOR_ASSESS_WK6` … `WK120` at **6-week spacing throughout**; there is no 12-weekly phase (17 subjects still imaged at week 120). Found 2026-09-20 laying the generated schedule beside the data (review-sheet 3b) |
| **D17** | Schedule | Protocol §7.2: assessments at Screening, Cycle 1 Day 1, Day 1 of each subsequent cycle, EOT, 30- and 90-day follow-up — **no Day 15 visit** | ADVS and ADLB carry a **`C1D15`** visit for 446 of 449 subjects, defined by TORIVA's visit-window build (`programs/adam/_build_visit_windows.R`), not by the protocol. This project's MMRM used it as an induction visit (S3). Found 2026-09-20 (review-sheet 3b) |
| **D18** | Document control | Protocol synopsis: *Version 1.0, 22 March 2026*; history ends at v1.1 (30 March 2026, identifiers only) | At `a806630` the synopsis is substantively amended by #27 (title, design, §3.5, §5.1, §7.2, §8.1) with no version bump, date change or history row |

D4 and D7 are the same defect from two directions: **estimand E3 is not implementable against
the built ADaM as specified.** What was built is E3a.

D2 and D6 are the same pattern on two endpoints: the SAP delegates a derivation to a named
library function, the implementation diverges, and the SAP is not updated. That opacity is
what a declarative concept model is meant to remove.

**D13 is the same substitution that [F08](../docs/findings/F08-no-risk-difference.md) reports
upstream.** TORIVA's SAP asks for a Mantel–Haenszel risk difference and reaches for a function
that yields an odds ratio; the AC/DC framework offers `M.CMH`, which yields an odds ratio, and
no risk difference at all. That the same slip appears independently on both sides is the
argument for F08 rather than against it: if a statistician writing the SAP and a framework
designing a method library both reach for the odds ratio when the estimand says risk
difference, that is precisely the substitution a declarative model should be able to catch.
Found 2026-09-16 while re-verifying F08's premise before filing.

**D11 is that pattern taken one step further, and the sharpest of the thirteen.** The SAP does
not delegate the lab analyses — it never specifies them. T-LB-01 and T-LB-02 were built, ran
and produced output, and the authoritative statement of what they compute is the R program
that computes it. For a project about making analysis derivation declarative, the lab tier's
lesson is that the derivation the concept model captures cleanly is in the SAP, and the
analysis it cannot capture is not in the SAP at all.

## ICH M11

Referenced, **not vendored**. The resource repository carries **no licence file**, and the
specification itself is ICH's under its own terms, so nothing from it is copied into this
repository.

| | |
|---|---|
| Resource index | `data4knowledge/usdm_m11_resources` (public, no licence declared) |
| Artefact used | `documents/downloads/m11_specification_v0-17-0.zip` — the merged *electronic* M11 |
| Retrieved | 2026-09-16 |
| Form | HTML, one page per data element, plus `element_index.html` |

**What it contains**, established by parsing it into a scratch working copy:

| | |
|---|---|
| Data elements | **303** |
| Required / Optional | **216 / 87** |
| Carrying a CDISC C-code | 294 of 303 |
| Top-level sections | 14 (Title Page, 1 Synopsis … 12 Appendices) |
| Data types | Text 230, Valid Value 44, Number 7, Date 3, the rest mixed |

Each element page carries Name, Original Name, Section, Status, Data Type, Cardinality,
Conformance, Guidance, and a Definition with a CDISC code — `arm_name` is `C93729`, for example.

**The element pages do not reference USDM.** The bridge between the two is the CDISC code plus
class correspondence, which is what makes an M11 → USDM mapping an exercise rather than a
lookup.

To reproduce the working copy:

```
curl -sL -o m11.zip https://raw.githubusercontent.com/data4knowledge/usdm_m11_resources/main/documents/downloads/m11_specification_v0-17-0.zip
```

Also in that repository and not yet used: `usdm_m11_classes.pdf` (a USDM ↔ M11 class
infographic), the USDM handbook, and `Protocol2USDM` under Tools.

## Upstream

| | |
|---|---|
| Repository | `cdisc-org/analysis-concepts` |
| Commit | `739344ca31203bb502efeee2b855286e17977be6` |
| Date | 2026-06-17 |
| Submodule path | `upstream/analysis-concepts` |

Schema versions at that commit: `acdc_methods` 0.8.0, `acdc_transformations` 0.1.0,
transformation library 0.6. Contents: 60 methods, 25 transformations (14 derivation,
11 analysis).

Branch worth watching: `estimands_01` (Stuart Malcolm, 2026-08-14, unmerged) — ICH E9(R1)
strategy smartphrases and an estimands/ICE implementation plan for issue #11. It touches the
same survival bindings as F02 and F06.
