# ⚠️ FICTIONAL EDUCATIONAL PROTOCOL — NOT FOR REGULATORY USE

**Derived excerpt of a fictional protocol, restructured for educational purposes only.**
Derived from **TORIVA-LUNG 301** (`OpenTrialReporting/torivumab-nsclc-301` at `8534339d`,
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

**Not supplied by the source protocol.** Nothing in §7 SAFETY ASSESSMENTS, the SoA or the
data-domain table describes how vital signs are to be measured or read. The SAP does not fill
this either: it lists `ADVS` among the required datasets (synopsis line 841) and specifies no
vital-signs analysis, which is the laboratory situation (D11) again.

## M11 conformance of this section

| M11 asks for | Status |
|---|---|
| Schedule of collection | ✅ moved from §7.2 |
| Measurements collected | ✅ moved from the data-domain table |
| Instructions for collection and interpretation | ❌ absent from the source; not invented |

One Required element, supplied in part.
