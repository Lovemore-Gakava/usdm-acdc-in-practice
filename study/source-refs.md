# Source references

TORIVA-LUNG 301 is **referenced by commit, not vendored**. It is ~81 MB and read-only input.

| | |
|---|---|
| Repository | `OpenTrialReporting/torivumab-nsclc-301` |
| Commit | `8534339d95d6e1709f5def1e715a9b0c8cc06fe8` |
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

## Known discrepancies inside the source

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

D4 and D7 are the same defect from two directions: **estimand E3 is not implementable against
the built ADaM as specified.** What was built is E3a.

D2 and D6 are the same pattern on two endpoints: the SAP delegates a derivation to a named
library function, the implementation diverges, and the SAP is not updated. That opacity is
what a declarative concept model is meant to remove.

**D11 is that pattern taken one step further, and the sharpest of the twelve.** The SAP does
not delegate the lab analyses — it never specifies them. T-LB-01 and T-LB-02 were built, ran
and produced output, and the authoritative statement of what they compute is the R program
that computes it. For a project about making analysis derivation declarative, the lab tier's
lesson is that the derivation the concept model captures cleanly is in the SAP, and the
analysis it cannot capture is not in the SAP at all.

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
