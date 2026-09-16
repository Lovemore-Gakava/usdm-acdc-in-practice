# ⚠️ FICTIONAL EDUCATIONAL PROTOCOL — NOT FOR REGULATORY USE

**This is a derived excerpt of a completely fictional protocol, restructured for educational
purposes only. DO NOT submit to any regulatory authority. Celindra Therapeutics, torivumab and
all trial details are fictional; all identifiers are non-functional.**

Derived from **TORIVA-LUNG 301** (`OpenTrialReporting/torivumab-nsclc-301` at `8534339d`,
CC BY 4.0) by restructuring its protocol synopsis and SAP to **ICH M11** section 3. See
[`../protocol-to-m11.md`](../protocol-to-m11.md) for the mapping this implements and
[`README.md`](README.md) for what was moved and what was invented.

---

# 3. Trial Objectives, Endpoints and Estimands

> **M11 conformance note.** M11 §3.1.1 and §3.2.1 require, per objective: Objective, Endpoint,
> Population, Treatment, Population-level Summary, Intercurrent Event Strategy, and Description
> of Intercurrent Event. In the source study the last five live in **SAP §13** and the protocol
> defers them (synopsis line 834). This section places them where M11 requires them. **No
> content is invented** — every estimand attribute below is transcribed from SAP §13.2–§13.7,
> cited per row.

## 3.0 Treatment (shared across all estimands)

*M11 `Treatment` (`C49236`). Source: SAP §13.2.*

| Arm | Specification |
|---|---|
| Experimental | Torivumab 200 mg IV Q3W + chemotherapy backbone (carboplatin AUC5 + pemetrexed 500 mg/m² IV Q3W) for up to 6 induction cycles, then pemetrexed maintenance Q3W until PD/toxicity/withdrawal (max 35 cycles total) |
| Control | Placebo IV Q3W + identical chemotherapy backbone, same duration rules |

> **Unresolved in the source.** SAP §13.2 specifies a chemotherapy backbone for both arms. The
> protocol synopsis title and §2.1 describe torivumab **versus placebo** as first-line
> monotherapy in PD-L1 TPS ≥50%, with no backbone. These are different trials. Carried forward
> as written and recorded as **D14** in `study/source-refs.md`; not reconciled here, because
> reconciling it would mean choosing which document is right.

## 3.1 Primary Objective and Estimand

### 3.1.1 Primary Objective 1

| M11 element | Value |
|---|---|
| **Primary Objective** `C85826` | To evaluate the effect of torivumab 200 mg Q3W versus placebo on Overall Survival (OS) in patients with previously untreated advanced or metastatic NSCLC with PD-L1 TPS ≥50% and no EGFR or ALK genomic tumour aberrations. *(protocol §2.1)* |
| **Endpoint** `C25212` | Time from randomisation to death from any cause. Patients not known to have died at data cut-off will be censored at the date last known alive. *(protocol §6)* |
| **Population** `C70833` | All randomised subjects (ITT; `ITTFL = "Y"`) with treatment-naïve metastatic NSCLC, PD-L1 TPS ≥50%, no sensitising EGFR mutations or ALK rearrangements, ECOG PS 0–1. *(SAP §13.4)* |
| **Treatment** `C49236` | As §3.0. *(SAP §13.4 → §13.2)* |
| **Population-level Summary** `C188853` | Stratified hazard ratio (torivumab / placebo) with 95% CI; strata = histology (squamous/non-squamous) × region (NA/EU/APAC). Supplementary KM medians and 12/18/24-month survival probabilities per arm. *(SAP §13.4)* |
| **Intercurrent Event Strategy** `C188857` | Treatment policy for all intercurrent events. *(SAP §13.4)* |
| **Description of Intercurrent Event** `C188856` | Treatment discontinuation (any reason); initiation of subsequent anti-cancer therapy; palliative care. Death is the event, not an intercurrent event. Withdrawal of survival consent → censor at withdrawal date. *(SAP §13.4, §13.3)* |

## 3.2 Secondary Objectives and Estimands

### 3.2.1 Secondary Objective 1 — Progression-Free Survival

| M11 element | Value |
|---|---|
| **Secondary Objective** `C85827` | To compare Progression-Free Survival (PFS) between the torivumab and placebo arms as assessed by blinded independent central review (BICR) per RECIST 1.1. *(protocol §2.2)* |
| **Secondary Endpoint** `C25212` | Time from randomisation to the first documented disease progression per RECIST 1.1 (BICR) or death from any cause, whichever occurs first. Patients without progression or death are censored at the last adequate tumour assessment. *(protocol §6)* |
| **Secondary Population** `C70833` | ITT. *(SAP §13.5)* |
| **Secondary Treatment** `C49236` | As §3.0. |
| **Secondary Population-level Summary** `C188853` | Stratified hazard ratio with 95% CI; strata as §3.1.1. *(SAP §13.5)* |
| **Secondary Intercurrent Event Strategy** `C188857` | Treatment policy for treatment discontinuation. **Hypothetical** for subsequent anti-cancer therapy, for ≥2 consecutive missed scheduled tumour assessments, and for no post-baseline assessment. *(SAP §13.3)* |
| **Secondary Description of Intercurrent Event** | Subsequent anti-cancer therapy → censor at last adequate assessment before therapy. ≥2 consecutive missed scheduled assessments → censor at last adequate assessment before the gap. No post-baseline assessment → censor at randomisation. Withdrawal of consent → censor at last adequate assessment. *(SAP §13.3)* |

### 3.2.2 Secondary Objective 2 — Objective Response Rate

| M11 element | Value |
|---|---|
| **Secondary Objective** `C85827` | To compare the Objective Response Rate (ORR) (complete response [CR] + partial response [PR]) between treatment arms per RECIST 1.1 by BICR. *(protocol §2.2)* |
| **Secondary Endpoint** `C25212` | Proportion of patients with best overall response of CR or PR. Confirmation requires a second CR or PR at a subsequent assessment ≥28 days later with no intervening PD. *(protocol §6; SAP §4.3)* |
| **Secondary Population** `C70833` | Response Evaluable — ITT with ≥1 post-baseline tumour assessment, or clinical progression before first assessment (`EFFFL = "Y"` on ADRS). *(SAP §13.6)* |
| **Secondary Treatment** `C49236` | As §3.0. |
| **Secondary Population-level Summary** `C188853` | Stratified Mantel–Haenszel **risk difference** (torivumab − placebo) with 95% CI; strata = histology × region. Supplementary per-arm Clopper–Pearson exact 95% CI for the proportion. *(SAP §13.6)* |
| **Secondary Intercurrent Event Strategy** `C188857` | **Composite** — the intercurrent event is incorporated into the variable by counting the subject as a non-responder. *(SAP §13.6)* |
| **Secondary Description of Intercurrent Event** | No post-baseline assessment → non-responder. Treatment discontinuation before adequate assessment → non-responder. Subsequent anti-cancer therapy before adequate assessment → non-responder (pre-specified to avoid attribution bias). Death before first response assessment → non-responder. *(SAP §13.6, §13.3)* |

### 3.2.3 Secondary Objective 3 — Duration of Response

| M11 element | Value |
|---|---|
| **Secondary Objective** `C85827` | To evaluate the Duration of Response (DoR) in responders in each treatment arm. *(protocol §2.2)* |
| **Secondary Endpoint** `C25212` | Time from first documented CR or PR to first documented disease progression or death from any cause, in responding patients. *(protocol §6)* |
| **Secondary Population** `C70833` | Confirmed responders only (subset of Response Evaluable). *(SAP §13.7)* |
| **Secondary Treatment** `C49236` | As §3.0. |
| **Secondary Population-level Summary** `C188853` | Kaplan–Meier median per arm with 95% CI. No formal between-arm hypothesis test; descriptive / hypothesis-generating. *(SAP §13.7)* |
| **Secondary Intercurrent Event Strategy** `C188857` | As PFS — **hypothetical** for subsequent therapy and for missed assessments. *(SAP §13.7, §13.3)* |
| **Secondary Description of Intercurrent Event** | Subsequent anti-cancer therapy and ≥2 consecutive missed assessments → censor as for PFS. Withdrawal of consent → censor at withdrawal. *(SAP §13.3)* |

### 3.2.4 Secondary Objective 4 — Disease Control Rate

| M11 element | Value |
|---|---|
| **Secondary Objective** `C85827` | To compare the Disease Control Rate (DCR) (CR + PR + stable disease [SD]) between treatment arms. *(protocol §2.2)* |
| **Secondary Endpoint** `C25212` | Proportion of patients with best overall response of CR, PR, or SD maintained ≥8 weeks from randomisation. *(protocol §6)* |
| **Secondary Population** `C70833` | Response Evaluable, as §3.2.2. *(SAP §13.7)* |
| **Secondary Treatment** `C49236` | As §3.0. |
| **Secondary Population-level Summary** `C188853` | Same structure as ORR — stratified Mantel–Haenszel risk difference with 95% CI. *(SAP §13.7)* |
| **Secondary Intercurrent Event Strategy** `C188857` | **Composite**, as ORR. *(SAP §13.7)* |
| **Secondary Description of Intercurrent Event** | As §3.2.2. *(SAP §13.7, §13.3)* |

### 3.2.5 Secondary Objective 5 — Safety and Tolerability

| M11 element | Value |
|---|---|
| **Secondary Objective** `C85827` | To characterise the safety and tolerability of torivumab relative to placebo, including the incidence, severity, and management of adverse events (AEs), serious adverse events (SAEs), immune-related adverse events (irAEs), and adverse events of special interest (AESIs). *(protocol §2.2)* |
| **Secondary Endpoint** `C25212` | Incidence and severity of TEAEs, SAEs, irAEs and AESIs; exposure-adjusted event rates. **Clinical laboratory evaluations** — haematology and chemistry parameters — are collected per §7.2 and analysed as change from baseline and as shifts in reference-range indicator. *(protocol §2.2, §7.2)* |
| **Secondary Population** `C70833` | Safety — all subjects receiving ≥1 dose, analysed by actual arm received. *(SAP §3)* |
| **Secondary Treatment** `C49236` | As §3.0, by actual treatment received. |
| **Secondary Population-level Summary** `C188853` | Descriptive. n (%) per arm for incidence; events per 100 patient-years for exposure-adjusted rates; KM for irAE time-to-onset and time-to-resolution. *(SAP §13.7)* |
| **Secondary Intercurrent Event Strategy** `C188857` | **Treatment policy** for TEAE incidence. **While-on-treatment** for exposure-adjusted rates (person-time = `TRTEDT − TRTSDT + 1`). *(SAP §13.7)* |
| **Secondary Description of Intercurrent Event** | Treatment discontinuation; initiation of new anti-cancer therapy, after which AE collection ceases (90-day window or new therapy, whichever first, per protocol §7.1). *(SAP §13.7, protocol §7.1)* |

> **The laboratory gap, stated rather than filled.** M11 requires a Population-level Summary for
> every objective. The source study specifies **three safety estimands, all adverse-event
> based** (SAP §13.7) and **none for laboratory data** — ADLB appears only in data-handling
> conventions. The summary above is therefore complete for AEs and **absent for laboratory
> evaluations**, which is the honest state of the source and is recorded as **D11**. The
> laboratory endpoint this project carries through the AC/DC chain has no estimand in either
> document, and this restructure does not invent one.

## 3.3 Exploratory Objectives

*Carried from protocol §2.3 without estimands. M11 §3.3.1 requires six elements per exploratory
objective; SAP §2.3 states that exploratory analyses are hypothesis-generating with no formal α
and defines no estimands, so Population-level Summary and Intercurrent Event Strategy are
**absent by design of the source** rather than omitted here.*

1. Patient-Reported Outcomes (EORTC QLQ-C30, QLQ-LC13, EQ-5D-5L).
2. PD-L1 TPS (continuous) and TMB versus efficacy outcomes.
3. Pharmacokinetic parameters of torivumab.
4. Anti-drug antibodies.
5. Efficacy by histological subtype and geographic region.

---

## M11 conformance of this section

| M11 section | Required elements | Supplied here | Absent, and why |
|---|---|---|---|
| §3.1.1 Primary Objective | 7 | **7** | — |
| §3.2.1 Secondary Objective ×5 | 7 each | **7 each** | — |
| §3.3.1 Exploratory Objective ×5 | 6 each | 3 each | source defines no exploratory estimands |

**Thirty required elements that the source protocol omitted are now present**, all transcribed
from SAP §13 rather than written. Two absences remain and are properties of the source, not of
this restructure: no laboratory estimand (D11), and no exploratory estimands.
