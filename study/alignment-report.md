# Alignment report — protocol ↔ USDM ↔ SAP excerpt ↔ built ADaM

Written by `tools/check_alignment.py` (phase 2, stage P3), which takes [`gap-register.md`](gap-register.md)
as its checklist. Re-run it to regenerate this file. `PASS` — a fix-here promise kept; `FAIL` — one not
kept; `WARN` — an upstream-only divergence confirmed against the data; `INFO` — worth knowing; `SKIP` —
data not present.

**24 pass, 0 fail, 5 warn, 2 info, 0 skip.** Data layer: TORIVA ADaM checked.

| Verdict | Item | Layer | Detail |
|---|---|---|---|
| WARN | D1 | data | ADTTE AVALU = ['DAYS']; SAP says months |
| WARN | D3 | data | ADRS carries no RSEVAL column — reader cannot be told from the data; the SAP's BICR reader stands as recorded |
| WARN | D7 | data | EFFFL absent from ADRS, as recorded |
| WARN | D8 | data | ADLB carries NRIND, not ANRIND/BNRIND, as recorded |
| WARN | D9 | data | BTOXGR absent from ADLB, as recorded |
| INFO | ADLB parameters without a BC | data | ['ALB', 'K', 'PLAT', 'SODIUM', 'WBC'] — collected and analysed by TORIVA, not carried by this project's USDM |
| INFO | SoA↔AVISIT | data | analysis visits not named as protocol encounters: ['Baseline', 'C1D15', 'MAINT_C10D1', 'MAINT_C11D1', 'MAINT_C12D1', 'MAINT_C13D1']… — the SAP's windowed labels (Baseline, MAINT_CnD1, UNSCHEDULED) versus the protocol's cycle visits (Cycle 7+ are 'maintenance' in the SAP, 'Day 1 each subsequent cycle' in the protocol) |
| PASS | BC↔ADLB | data | lab BC codes in ADLB PARAMCD: ['ALP', 'ALT', 'AST', 'BILI', 'CREAT', 'HGB', 'NEUT'] |
| PASS | BC↔ADVS | data | SYSBP in ADVS PARAMCD |
| PASS | D14 | data | ADSL TRT01P values ['Placebo + Chemotherapy', 'Torivumab + Chemotherapy'] == USDM arms |
| PASS | D15 | data | ADSL arm counts {'Torivumab + Chemotherapy': 225, 'Placebo + Chemotherapy': 225} — 1:1 |
| PASS | D11 | documents | section 10 states the analyses added by this project (S1–S3) as not the sponsor's |
| PASS | D13 | documents | §3.2.2 Population-level Summary names a risk difference |
| PASS | D14 | documents | USDM arms ['Torivumab + Chemotherapy', 'Placebo + Chemotherapy']; section 04 notes D14: True; backbone intervention: True |
| PASS | D15 | documents | USDM design notes say 1:1; sections 01, 04, 10 carry the D15 note |
| PASS | G1 | documents | USDM estimands 6; §3 population-level summaries 9 |
| PASS | G3 | documents | title page carries the EU CT number correction |
| PASS | G4 | documents | all lab BCs named in §12.1 |
| PASS | G8 | documents | coverage.json covers sections ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'] |
| PASS | S1 | documents | section 10 states the analyses added by this project (S1–S3) as not the sponsor's |
| PASS | S2 | documents | section 10 states the analyses added by this project (S1–S3) as not the sponsor's |
| PASS | S3 | documents | section 10 states the analyses added by this project (S1–S3) as not the sponsor's |
| PASS | USDM generated | documents | fragment names its generator and carries a schedule |
| PASS | USDM↔protocol:END-DCR | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-DOR | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-ORR | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-OS | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-PFS | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-S5-LAB | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-S5-VS | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-S5-VS cites §8.4.2 | documents | yes |
