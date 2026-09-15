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

## Sections used

| Tier | SAP | Programming spec | ADaM target |
|---|---|---|---|
| Simple — lab CFB | §12.3 (baseline definition), §12.2 (analysis visits) | `ADLB-spec.md` | ADLB |
| Moderate — ORR | §4.3, §13.6 (estimand E3 / E3a) | `ADRS-spec.md` | ADRS `PARAMCD = "CBOR"`; ADSL `ORRFL` |
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

Recorded during the PFS mapping; to be resolved against built ADaM at comparison time.
See [endpoints/03-complex-pfs/mapping.md](../endpoints/03-complex-pfs/mapping.md), D1 and D2.

- **D1** — SAP §4.2 gives the PFS time origin as `RANDDT`; `ADTTE-spec.md` uses `TRTSDT`.
  SAP §13.5 says months, ADTTE stores days.
- **D2** — SAP §4.2 and §13.5 specify `admiral::derive_param_tte()`; `ADTTE-spec.md` v0.3
  records that stale `derive_param_tte()` references were removed and the code uses explicit
  logic. The SAP was not updated.

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
