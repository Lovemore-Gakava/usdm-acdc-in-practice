# Alignment report — protocol ↔ USDM ↔ SAP excerpt ↔ built ADaM

Written by `tools/check_alignment.py` (phase 2, stage P3), which takes [`gap-register.md`](gap-register.md)
as its checklist. Re-run it to regenerate this file. `PASS` — a fix-here promise kept; `FAIL` — one not
kept; `WARN` — the data diverging from the corrected documents, or an upstream-only divergence, confirmed against the data; `INFO` — worth knowing; `SKIP` —
data not present.

**27 pass, 0 fail, 8 warn, 3 info, 0 skip.** P6 decisions: 6/6 pass — D14 PASS, D15 PASS, D11/G7 PASS, G2 PASS, G6 PASS, G5 PASS. Data layer: TORIVA ADaM checked.

| Verdict | Item | Layer | Detail |
|---|---|---|---|
| WARN | D1 | data | ADTTE AVALU = ['DAYS']; SAP says months |
| WARN | D15 | data | ADSL arm counts {'Torivumab + Chemotherapy': 225, 'Placebo + Chemotherapy': 225} — 1:1; the protocol says 2:1 — the data diverges from the documents, to be regenerated upstream |
| WARN | D16 | data | ADTR imaging visits after month 12 are 6-weekly (weeks 60–120); protocol §6.1 says every 12 weeks from month 12 — the data diverges from the documents |
| WARN | D17 | data | ADVS/ADLB carry a C1D15 visit for nearly every subject; the protocol §7.2 has no Day 15 visit — the data diverges from the documents |
| WARN | D3 | data | ADRS carries no RSEVAL column — reader cannot be told from the data; the SAP's BICR reader stands as recorded |
| WARN | D7 | data | EFFFL absent from ADRS, as recorded |
| WARN | D8 | data | ADLB carries NRIND, not ANRIND/BNRIND, as recorded |
| WARN | D9 | data | BTOXGR absent from ADLB, as recorded |
| INFO | ADLB parameters without a BC | data | ['ALB', 'K', 'PLAT', 'SODIUM', 'WBC'] — collected and analysed by TORIVA, not carried by this project's USDM |
| INFO | AVISIT beyond cycle 35 | data | 13 analysis-visit labels lie beyond the protocol's 35-cycle maximum (up to C48D1); the SAP's windowing assigns post-treatment assessments to cycle windows — treatment itself runs at most 738 days, 35.1 cycles |
| INFO | SoA↔AVISIT | data | after translation, 37 of 51 analysis-visit labels name a protocol encounter; unmatched: ['C1D15']; beyond cycle 35: 13 |
| PASS | BC↔ADLB | data | lab BC codes in ADLB PARAMCD: ['ALP', 'ALT', 'AST', 'BILI', 'CREAT', 'HGB', 'NEUT'] |
| PASS | BC↔ADVS | data | SYSBP in ADVS PARAMCD |
| PASS | D14 | data | ADSL TRT01P values ['Placebo + Chemotherapy', 'Torivumab + Chemotherapy'] == the corrected protocol's arms ['Placebo + Chemotherapy', 'Torivumab + Chemotherapy'] |
| PASS | D11 | documents | §3.2.5 specifies the descriptive laboratory summary (values by visit, reference-range shift, worst CTCAE grade) and section 10 restates it |
| PASS | D13 | documents | §3.2.2 Population-level Summary names a risk difference |
| PASS | D14 | documents | title, §3.0 and section 04 corrected to the combination; USDM arms ['Torivumab + Chemotherapy', 'Placebo + Chemotherapy'] per the corrected protocol; backbone intervention present; no 'ground truth' rule in the fragment |
| PASS | D15 | documents | USDM design notes say 2:1, the protocol's ratio; sections 01, 04, 10 carry the D15 note |
| PASS | G1 | documents | USDM estimands 6; §3 population-level summaries 10 |
| PASS | G2 | documents | title page supplies 13 countries, 15 sites and the approval date, marked as supplied under P6 |
| PASS | G3 | documents | title page carries the EU CT number correction |
| PASS | G4 | documents | all lab BCs named in §12.1 |
| PASS | G5 | documents | §12.1 states a central laboratory with central reference ranges, marked as supplied under P6 |
| PASS | G6 | documents | §8.4.2 supplies the collection procedure, marked as supplied under P6 |
| PASS | G7 | documents | §3.2.5 specifies the descriptive laboratory summary (values by visit, reference-range shift, worst CTCAE grade) and section 10 restates it |
| PASS | G8 | documents | coverage.json covers sections ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'] |
| PASS | S1 | documents | section 10 states the analyses added by this project (S1–S3) as demonstration analyses, not the sponsor's |
| PASS | S2 | documents | section 10 states the analyses added by this project (S1–S3) as demonstration analyses, not the sponsor's |
| PASS | S3 | documents | section 10 states the analyses added by this project (S1–S3) as demonstration analyses, not the sponsor's |
| PASS | USDM generated | documents | fragment names its generator and carries a schedule |
| PASS | USDM↔protocol:END-DCR | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-DOR | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-ORR | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-OS | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-PFS | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-S5-LAB | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-S5-VS | documents | endpoint text present in the M11 protocol |
| PASS | USDM↔protocol:END-S5-VS cites §8.4.2 | documents | yes |
