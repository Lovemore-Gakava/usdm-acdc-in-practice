# ⚠️ FICTIONAL EDUCATIONAL PROTOCOL — NOT FOR REGULATORY USE

**Derived excerpt of a fictional protocol, restructured for educational purposes only.**
Derived from **TORIVA-LUNG 301** (`OpenTrialReporting/torivumab-nsclc-301` at `a806630`, re-pinned 2026-09-20 after #27;
CC BY 4.0). See [`README.md`](README.md).

---

# 8.4.2 Vital Signs

*M11 element `Vital Signs` (`C154628`), Required, data type Text. Added 2026-09-19 for the
second endpoint — systolic blood pressure, change from baseline.*

> **This section can be assembled from the protocol only in part**, and that is the finding.
> M11's guidance for the element is *"Include any specific instructions for the collection and
> interpretation of vital signs."* The source protocol supplies **when** vital signs are taken
> and **which** are taken, and no instructions for collection or interpretation — no position,
> rest period, cuff, repeat rule, or criterion for a clinically significant value. Both halves
> the protocol does supply are moved here verbatim; the missing half is left missing. See
> [`../protocol-to-m11.md`](../protocol-to-m11.md) §8.4.2.

## Schedule

*Source: protocol §7.2 Safety Assessment Schedule, the `Vital signs` row, moved unchanged.*

| Assessment | Screening | Cycle 1 Day 1 | Day 1 Each Subsequent Cycle | EOT | 30-day Safety | 90-day Safety |
|---|---|---|---|---|---|---|
| Vital signs | ✓ | Pre/post-infusion | Pre/post-infusion | ✓ | ✓ | — |

## Measurements

*Source: protocol data-domain table (synopsis line 808), moved unchanged.*

| Vital Signs | BP, HR, temperature, weight, height | VS |
|---|---|---|

The systolic component of *BP* is the measurement this project's second endpoint carries.
Its Biomedical Concept is `SYSBP` (`C25298`), attached to the scheduled assessment above.

## Instructions for collection and interpretation

**Now in the source — §7.2 *Vital signs procedure (G6)* at `a806630` (#27, PR #34), moved verbatim:**

> Blood pressure, heart rate, respiratory rate, temperature and weight are measured pre-dose on Day 1 of each cycle, and again post-infusion on dosing days, after the patient has been seated at rest for at least 5 minutes. Site standard calibrated equipment is used; the same method and arm are used for a given patient throughout. Height is measured at screening only.

The analysis is now SAP §5.7: change from baseline at C1D1, C4D1 and EOT, and weight-change categories, safety population, descriptive. This project's MMRM and ANCOVA remain demonstration analyses (S2). The paragraph this project supplied under P6 follows as the record.

**Supplied under P6 (2026-09-20) — G6.** Blood pressure and heart rate are measured after the
participant has rested for at least five minutes in a seated (or, if necessary, supine) position,
using the same arm and the same position throughout the trial. On infusion days, vital signs are
taken within 60 minutes before the start of the infusion and 30 to 60 minutes after its end.
Temperature and respiratory rate are recorded at the same times. Weight is recorded at each
scheduled visit; height at screening only. Any abnormality the investigator judges clinically
significant is recorded as an adverse event. The analysis is descriptive by visit (§3.2.5);
this project's MMRM and ANCOVA on systolic blood pressure are demonstration analyses (gap
register S2). This is standard first-line NSCLC trial text and matches the source's
*"Pre/post-infusion"* schedule cells; it is this project's wording, marked as such, because the
source gives the schedule only.

**As originally recorded — not supplied by the source protocol.** Nothing in §7 SAFETY ASSESSMENTS, the SoA or the
data-domain table describes how vital signs are to be measured or read. The SAP does not fill
this either: it lists `ADVS` among the required datasets (synopsis line 841) and specifies no
vital-signs analysis, which is the laboratory situation (D11) again.

## M11 conformance of this section

| M11 asks for | Status |
|---|---|
| Schedule of collection | ✅ moved from §7.2 |
| Measurements collected | ✅ moved from the data-domain table |
| Instructions for collection and interpretation | ✅ in the source at `a806630` (§7.2, G6); supplied under P6 before that |

One Required element, all three parts from the source at `a806630`.
