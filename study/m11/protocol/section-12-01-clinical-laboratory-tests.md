# ⚠️ FICTIONAL EDUCATIONAL PROTOCOL — NOT FOR REGULATORY USE

**Derived excerpt of a fictional protocol, restructured for educational purposes only.**
Derived from **TORIVA-LUNG 301** (`OpenTrialReporting/torivumab-nsclc-301` at `a806630`, re-pinned 2026-09-20 after #27;
CC BY 4.0). See [`README.md`](README.md).

---

# 12.1 Clinical Laboratory Tests

*M11 element `Clinical Laboratory Tests` (`C25294`), Required.*

> **This section could not be assembled from the protocol alone**, and that is the finding.
> Stage 0 established that the source protocol has no panel-level list of analytes anywhere.
> Six of the seven parameters this project's AC/DC chain uses *do* appear in it — every one as
> an **eligibility threshold** or an **AE-management rule**, never as a test to be collected
> and analysed. The seventh, ALP, appears nowhere. See
> [`../protocol-to-m11.md`](../protocol-to-m11.md).
>
> The panel names below come from the protocol. **The analyte detail comes from
> `programming-specs/ADLB-spec.md`, a downstream programming document**, and each row says so.
> Sourcing a Required protocol element from a programming specification is backwards, and is
> recorded rather than concealed.

## Panels and schedule

*Source: protocol §7.2 Safety Assessment Schedule.*

| Panel | Screening | C1D1 | Each subsequent cycle D1 | EOT | 30-day | 90-day |
|---|---|---|---|---|---|---|
| Haematology | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Chemistry (LFTs, creatinine) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Thyroid function (TSH, fT4) | ✓ | — | C3, C5, then Q12 weeks | ✓ | ✓ | — |
| Cortisol (AM) | ✓ | — | If clinically indicated | — | — | — |
| Urinalysis | ✓ | — | C3, C5, then Q6 cycles | ✓ | — | — |

The source annotates this table: *"Full Schedule of Assessments (SoA) to be presented as a
formal table in the final protocol body. The above is a synopsis-level summary."*

## Analytes

| Analyte | Panel | In the protocol? | Where, and for what purpose |
|---|---|---|---|
| ALT — Alanine Aminotransferase | Chemistry | yes | §5.1 eligibility (*"AST and ALT ≤2.5 × ULN"*); irAE management table |
| AST — Aspartate Aminotransferase | Chemistry | yes | as ALT |
| **ALP — Alkaline Phosphatase** | Chemistry | **no** | absent entirely — its apparent hits are all the word *alpha* |
| BILI — Total Bilirubin | Chemistry | yes | §5.1 eligibility (*"Total bilirubin ≤1.5 × ULN"*) |
| CREAT — Creatinine | Chemistry | yes | §5.1 eligibility (*"Serum creatinine ≤1.5 × ULN"*); named in the §7.2 schedule |
| HGB — Haemoglobin | Haematology | yes | §5.1 eligibility (*"Haemoglobin ≥90 g/L"*) |
| NEUT — Neutrophils | Haematology | yes | §5.1 eligibility, as ANC (*"ANC ≥1.5 × 10⁹/L"*) |

**Analyte identity and toxicity grading below are from `ADLB-spec.md`, not the protocol.**

| Analyte | CTCAE v5.0 grading thresholds *(ADLB-spec.md)* |
|---|---|
| ALT, AST | >ULN–3× / >3–5× / >5–20× / >20× |
| ALP | >ULN–2.5× / >2.5–5× / >5–20× / >20× |
| BILI | >ULN–1.5× / >1.5–3× / >3–10× / >10× |
| CREAT | >ULN–1.5× / >1.5–3× / >3–6× / >6× |
| HGB | ≥LLN = 0 / <LLN–10.0 = 1 / <10.0–8.0 = 2 / <8.0 = 3 (g/dL; no lab-based Grade 4 for anaemia) |
| NEUT | ≥LLN / <LLN–1.5 / <1.5–1.0 / <1.0–0.5 / <0.5 |

`ADLB-spec.md` records that HGB grading previously used g/L thresholds (100/80/65) against
g/dL data, which graded every low haemoglobin as Grade 4, and that this was corrected. A
grading threshold whose unit was wrong is exactly the kind of thing a protocol §12.1 exists to
pin down, and this protocol has no §12.1.

## Reference ranges and laboratory

**Now in the source — §7.2 *Laboratory source and reference ranges (G5)* at `a806630` (#27, PR #34), moved verbatim:**

> Haematology, chemistry, thyroid function, cortisol and urinalysis are analysed at a **central** laboratory, whose reference ranges are the source of the reference-range category for each result. Local laboratory testing is permitted for clinical management of the patient only, and local results are not used in the analysis. PD-L1 TPS is determined centrally by 22C3 pharmDx IHC, where the central result governs eligibility. CTCAE v5.0 grading is applied to laboratory values programmatically during analysis, not at the site.

The decision this project took under P6 follows as the record; the source now says the same.

**Supplied under P6 (2026-09-20) — G5.** The haematology and chemistry panels analysed in this
trial are performed by a **central laboratory**, and reference-range indicators use the central
laboratory's ranges. Local laboratory testing is permitted where a result is needed for urgent
clinical management, but local results are not used for analysis. Rationale: the source already
mandates a central laboratory for PD-L1 (§5.1), and the trial's records carry one reference range
per analyte, which is consistent only with one laboratory. Practice varies on this point; the
decision is LG's and is marked as this project's.

**As originally recorded.** Not specified. The source's ADLB carries `ANRLO`/`ANRHI` taken from SDTM `LB.LBSTNRLO` /
`LBSTNRHI` — that is, from the **collecting laboratory**, per record. The protocol states no
central-laboratory requirement for safety labs. Contrast §5.1, which does require a *"certified
central laboratory"* for PD-L1 determination and states that the central result governs
eligibility: the source is explicit about central testing where it matters for eligibility and
silent where it matters for safety analysis.

## Conformance

| | |
|---|---|
| M11 Required element | `Clinical Laboratory Tests` `C25294` |
| Assembled | **partially, and from the wrong document** |
| From the protocol | panel names and collection schedule (§7.2) |
| From a programming spec | the seven analytes, their identities, and CTCAE grading |
| Absent from both at `8534339d`, supplied under P6, in the source at `a806630` (§7.2, G5) | reference-range source; central versus local laboratory for safety analytes |
