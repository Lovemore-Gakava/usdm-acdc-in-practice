# ⚠️ FICTIONAL EDUCATIONAL PROTOCOL — NOT FOR REGULATORY USE

**This is a derived excerpt of a completely fictional protocol, restructured for educational
purposes only. DO NOT submit to any regulatory authority. All identifiers below are fictional
and non-functional. Celindra Therapeutics and torivumab are fictional.**

Derived from **TORIVA-LUNG 301** (`OpenTrialReporting/torivumab-nsclc-301` at `8534339d`,
CC BY 4.0). See [`README.md`](README.md).

---

# Title Page

M11's Title Page section carries 58 elements, 24 of them Required. Of those 24, eleven are
amendment-conditional and correctly absent from an unamended v1.0 protocol.

## Supplied by the source

| M11 element | Code | Value |
|---|---|---|
| Full Title | `C132346` | A Randomised, Double-Blind, Placebo-Controlled, Phase 3 Study of Torivumab (Anti-PD-L1 Monoclonal Antibody) versus Placebo as First-Line Treatment in Patients with Advanced or Metastatic Non-Small Cell Lung Cancer with PD-L1 Tumour Proportion Score ≥50% and No EGFR or ALK Genomic Tumour Aberrations |
| Trial Short Title | `C94105` | TORIVA-LUNG 301 |
| Trial Acronym | `C94108` | TORIVA-LUNG 301 — **see note 2** |
| Sponsor Protocol Identifier | `C132351` | SIMULATED-TORIVUMAB-2026 *(fictional)* |
| Sponsor Name | `C222495` | Celindra Therapeutics *(fictional)* |
| Sponsor Legal Address | `C222495` | 1 Innovation Drive, Suite 400, Cambridge, MA 02139, USA *(fictional)* |
| Trial Phase | `C48281` | Phase 3 → `C15602` "Phase III Trial" |
| Version Number | `C181232` | 1.0 |
| Version Date | `C93813` | 22 March 2026 |
| Original Protocol Indicator | `C218672` | Yes — v1.0, no amendments. **Inferred**, see note 3 |
| **Region Identifier** | `C20108` | North America / Europe / Asia-Pacific *(protocol §8.2 stratification: "Geographic region (North America / Europe / Asia-Pacific)")* |
| NCT Number | `C172240` | NCT99999999 *(fictional)* |
| FDA IND Number | `C218685` | IND-SIM-2026-99999 *(fictional)* |
| Medical Expert Contact Info | `C218693` | Dr. James Okafor, MD, PhD, Senior Medical Director, Oncology *(fictional)* |
| Nonproprietary Names | `C97054` | torivumab — **see note 4** |

## Required, and not supplied by the source

Recorded as absent. **Not invented** — a fabricated country list or approval date would make the
document conformant and untrue, and the gaps are the point of the exercise.

| M11 element | Code | Why absent |
|---|---|---|
| Country Identifier | `C20108` | The protocol enumerates no countries. §5.2 refers to the "enrolling jurisdiction" and defers the detail to a *"country-specific protocol appendix"* that does not exist in the source |
| Site Identifier | `C20108` | No site list anywhere in the source |
| Sponsor Approval Date | `C132352` | Absent — zero occurrences of "approval date" in the protocol |
| Sponsor Approval Date Location | `C132352` | As above |
| State location where sponsor approval information is held | `C132352` | As above |

**Region is supplied and country is not**, which is worth noticing: the source knows its regions
because they are a randomisation stratum, and that is an *analysis* need. Nothing in the source
needed a country list, so nothing recorded one.

## Amendment elements — not applicable

Eleven Required elements apply only to an amended protocol: Amendment Identifier, Scope,
Summary, Details; Primary and Secondary Reason for Amendment and their two "Other" free-text
partners; Substantial Impact Safety and Data with their two explanations. This is v1.0.

## Notes on the mapping

**1 — EudraCT is not EU CT.** The source gives *"EudraCT Number: 9999-999999-99"*. M11 has
`EU CT Number` (`C218684`) — the CTIS identifier that replaced EudraCT under EU CTR 536/2014 —
and **no EudraCT element at all**. The honest mapping is therefore *unmapped*: the value is left
off this title page rather than entered against an element it does not correspond to. The source
protocol is carrying a retired identifier.

**2 — Short title and acronym are one string.** M11 separates `Full Title`, `Trial Short Title`
and `Trial Acronym`. The source gives *"Short Title: TORIVA-LUNG 301"* and no acronym, so one
string serves two elements. Recorded rather than resolved; a real sponsor would choose.

**3 — `Original Protocol Indicator` is inferred.** The source states Version 1.0 with no
amendment history, which entails it, but never asserts it. M11 makes it an explicit Required
element. Marked inferred rather than sourced.

**4 — Proprietary and nonproprietary names are not distinguished.** The source gives
"Torivumab" and "Torivumab 200 mg/10 mL concentrate for solution for infusion". Since the drug
is fictional and no trade name appears, "torivumab" is mapped to `Nonproprietary Names` only,
and `Proprietary Names` is left empty rather than duplicated.

## Conformance

| | |
|---|---|
| Required elements applicable to a v1.0 protocol | 13 |
| Supplied | **8** |
| Absent in the source | **5** — Country, Site, and the three Sponsor Approval Date elements |
| Required but amendment-conditional, correctly absent | 11 |
| Optional elements supplied | 7 |
| Optional elements deliberately left unmapped | 1 — EudraCT, see note 1 |
