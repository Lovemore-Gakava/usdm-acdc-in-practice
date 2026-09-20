# Alignment report — protocol ↔ USDM ↔ SAP excerpt ↔ built ADaM

Written by `tools/check_alignment.py` (phase 2, stage P3), which takes [`gap-register.md`](gap-register.md)
as its checklist. Re-run it to regenerate this file. `PASS` — a fix-here promise kept; `FAIL` — one not
kept; `WARN` — the data diverging from the corrected documents, or an upstream-only divergence, confirmed against the data; `INFO` — worth knowing; `SKIP` —
data not present.

**36 pass, 0 fail, 0 warn, 4 info, 0 skip.** P6 decisions (as the source now carries them, a806630): 6/6 pass — D14 PASS, D15 PASS, D11/G7 PASS, G2 PASS, G6 PASS, G5 PASS. Data layer: TORIVA ADaM checked.

| Verdict | Item | Layer | Detail |
|---|---|---|---|
| INFO | ADLB parameters without a BC | data | ['ALB', 'K', 'PLAT', 'SODIUM', 'WBC'] — collected and analysed by TORIVA, not carried by this project's USDM |
| INFO | AVISIT beyond cycle 35 | data | 12 analysis-visit labels lie beyond the protocol's 35-cycle maximum (up to C47D1); the SAP's windowing assigns post-treatment assessments to cycle windows — treatment itself runs at most 739 days, 35.2 cycles |
| INFO | D3 | data | RSEVAL present |
| INFO | SoA↔AVISIT | data | after translation, 37 of 49 analysis-visit labels name a protocol encounter; unmatched: []; beyond cycle 35: 12 |
| PASS | BC↔ADLB | data | lab BC codes in ADLB PARAMCD: ['ALP', 'ALT', 'AST', 'BILI', 'CREAT', 'HGB', 'NEUT'] |
| PASS | BC↔ADVS | data | SYSBP in ADVS PARAMCD |
| PASS | D1 | data | ADTTE OS/PFS/PFSINV start at RANDDT for every record, no ITT subject without a value, AVALU = ['DAYS'] as the ADaM spec declares |
| PASS | D14 | data | ADSL TRT01P values ['Placebo + Chemotherapy', 'Torivumab + Chemotherapy'] == the corrected protocol's arms ['Placebo + Chemotherapy', 'Torivumab + Chemotherapy'] |
| PASS | D15 | data | ADSL arm counts {'Placebo + Chemotherapy': 150, 'Torivumab + Chemotherapy': 300} — 2:1, as the protocol states |
| PASS | D16 | data | imaging after month 12 is 12-weekly, as the protocol states |
| PASS | D17 | data | no C1D15 in the data |
| PASS | D7 | data | EFFFL now present in ADRS — register row D7 is stale |
| PASS | D8 | data | ADLB carries NRIND, not ANRIND/BNRIND, as recorded |
| PASS | D9 | data | BTOXGR absent from ADLB, as recorded |
| PASS | D11 | documents | §3.2.5 transcribes SAP v0.3 §5.6/§5.7 (reference-range shift, worst CTCAE grade, values by visit) and section 10 says the source now specifies it |
| PASS | D13 | documents | §3.2.2's Population-level Summary row names a risk difference |
| PASS | D14 | documents | the source states the combination (title page carries its title); §3.0 and section 04 record it as resolved upstream; USDM arms ['Torivumab + Chemotherapy', 'Placebo + Chemotherapy']; backbone intervention present; no 'ground truth' rule |
| PASS | D15 | documents | USDM design notes say 2:1; sections 01, 04, 10 carry the D15 note, now as resolved upstream |
| PASS | G1 | documents | USDM estimands 6; §3 population-level summaries 10 |
| PASS | G2 | documents | title page carries the source's 12 countries and 15 sites (synopsis table at the pin) and still supplies the approval date, marked |
| PASS | G3 | documents | title page records EudraCT as unmapped against M11's EU CT Number |
| PASS | G4 | documents | all lab BCs named in §12.1 |
| PASS | G5 | documents | §12.1 carries the source's §7.2 laboratory-source paragraph verbatim (present at the pin) |
| PASS | G6 | documents | §8.4.2 carries the source's §7.2 vital-signs procedure verbatim (present at the pin) |
| PASS | G7 | documents | §3.2.5 transcribes SAP v0.3 §5.6/§5.7 (reference-range shift, worst CTCAE grade, values by visit) and section 10 says the source now specifies it |
| PASS | G8 | documents | coverage.json covers sections ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'] |
| PASS | G9 | documents | section 08 supplies §8.2 from the source's own documents, marked, with the 28-day window and the 72-hour pregnancy-test rule |
| PASS | S1 | documents | section 10 states the analyses added by this project (S1–S3) as demonstration analyses, not the sponsor's |
| PASS | S2 | documents | section 10 states the analyses added by this project (S1–S3) as demonstration analyses, not the sponsor's |
| PASS | S3 | documents | section 10 states the analyses added by this project (S1–S3) as demonstration analyses, not the sponsor's |
| PASS | USDM generated | documents | fragment names its generator and carries a schedule |
| PASS | USDM↔protocol:END-DCR | documents | endpoint text present in the M11 protocol, all 106 characters |
| PASS | USDM↔protocol:END-DOR | documents | endpoint text present in the M11 protocol, all 124 characters |
| PASS | USDM↔protocol:END-ORR | documents | endpoint text present in the M11 protocol, all 168 characters |
| PASS | USDM↔protocol:END-OS | documents | endpoint text present in the M11 protocol, all 143 characters |
| PASS | USDM↔protocol:END-PFS | documents | endpoint text present in the M11 protocol, all 229 characters |
| PASS | USDM↔protocol:END-S5-LAB | documents | endpoint text present in the M11 protocol, all 263 characters |
| PASS | USDM↔protocol:END-S5-VS | documents | endpoint text present in the M11 protocol, all 35 characters |
| PASS | USDM↔protocol:END-S5-VS cites §8.4.2 | documents | yes |
| PASS | pin | documents | source-refs pins a8066307; the checkout is at a8066307 |
