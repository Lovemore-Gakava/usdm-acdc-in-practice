# ⚠️ FICTIONAL EDUCATIONAL PROTOCOL — NOT FOR REGULATORY USE

**This is a derived excerpt of a completely fictional protocol, restructured for educational
purposes only. DO NOT submit to any regulatory authority. All identifiers below are fictional
and non-functional. Celindra Therapeutics and torivumab are fictional.**

Derived from **TORIVA-LUNG 301** (`OpenTrialReporting/torivumab-nsclc-301` at `a806630`, re-pinned 2026-09-20 after #27;
CC BY 4.0). See [`README.md`](README.md).

---

# Title Page

M11's Title Page section carries 58 elements, 24 of them Required. Of those 24, eleven are
amendment-conditional and correctly absent from an unamended v1.0 protocol.

## Supplied by the source

| M11 element | Code | Value |
|---|---|---|
| Full Title | `C132346` | A Randomised, Double-Blind, Placebo-Controlled, Phase 3 Study of Torivumab (Anti-PD-L1 Monoclonal Antibody) plus Platinum-Pemetrexed Chemotherapy versus Placebo plus Platinum-Pemetrexed Chemotherapy as First-Line Treatment in Patients with Advanced or Metastatic Non-Small Cell Lung Cancer with PD-L1 Tumour Proportion Score ≥50% and No EGFR or ALK Genomic Tumour Aberrations — *the source's own title at `a806630` (#27, D14); at `8534339d` it said versus placebo, monotherapy* |
| Trial Short Title | `C94105` | TORIVA-LUNG 301 |
| Trial Acronym | `C94108` | TORIVA-LUNG 301 — **see note 2** |
| Sponsor Protocol Identifier | `C132351` | SIMULATED-TORIVUMAB-2026 *(fictional)* |
| Sponsor Name | `C222495` | Celindra Therapeutics *(fictional)* |
| Sponsor Legal Address | `C222495` | 1 Innovation Drive, Suite 400, Cambridge, MA 02139, USA *(fictional)* |
| Trial Phase | `C48281` | Phase 3 → `C15602` "Phase III Trial" |
| Version Number | `C181232` | 1.2 *(at `0f78331`; 1.0 through `a806630` — D18)* |
| Version Date | `C93813` | 20 September 2026 *(at `0f78331`; 22 March 2026 through `a806630`)* |
| Original Protocol Indicator | `C218672` | **No** — v1.2 is Amendment 1 (Document History at `0f78331`). *Yes, inferred, through `a806630` — see note 3* |
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
| Country Identifier | `C20108` | *(at `8534339d`)* The protocol enumerates no countries. §5.2 refers to the "enrolling jurisdiction" and defers the detail to a *"country-specific protocol appendix"* that does not exist in the source |
| Site Identifier | `C20108` | *(at `8534339d`)* No site list anywhere in the source |
| Sponsor Approval Date | `C132352` | Absent — zero occurrences of "approval date" in the protocol |
| Sponsor Approval Date Location | `C132352` | As above |
| State location where sponsor approval information is held | `C132352` | As above |

**Region is supplied and country is not**, which is worth noticing: the source knows its regions
because they are a randomisation stratum, and that is an *analysis* need. Nothing in the source
needed a country list, so nothing recorded one.

## Amendment elements — applicable since v1.2 (`0f78331`, 2026-09-20)

Eleven Required elements apply only to an amended protocol. Through `a806630` this was v1.0 and they
were correctly absent; at `0f78331` the source is v1.2, *Amendment 1*, and its Document History row
is the only source for them. Populated from that row; what the row does not say is recorded absent.

| M11 element | Value | Source |
|---|---|---|
| Amendment Identifier | Amendment 1 | Document History, v1.2 row |
| Amendment Scope | Global (no country- or site-specific scope is stated) | inferred from the absence of any scope statement; marked |
| Amendment Summary | Comparator corrected from placebo monotherapy to placebo plus platinum-pemetrexed chemotherapy; sites and countries stated; central laboratory, reference ranges and vital-signs procedure added; laboratory and vital-signs analyses specified; header note on the 1:1 → 2:1 regeneration, Q12W imaging and the removed Cycle 1 Day 15 visit; sample-size arithmetic unchanged | Document History, v1.2 row |
| Amendment Details | the row itself, moved verbatim into §12.3 | Document History |
| Primary Reason for Amendment | *Other* — corrections found by the ICH M11 / USDM cross-check (issue #27); M11's reason codelist has no value for "the design description was wrong" | Document History; the *Other* text is the row's own wording |
| Secondary Reason for Amendment | absent — the row gives one reason | — |
| Substantial Impact — Safety; Substantial Impact — Data | absent — not stated in the source | — |

## Notes on the mapping

**1 — EudraCT is not EU CT.** The source gives *"EudraCT Number: 9999-999999-99"*. M11 has
`EU CT Number` (`C218684`) — the CTIS identifier that replaced EudraCT under EU CTR 536/2014 —
and **no EudraCT element at all**. The honest mapping is therefore *unmapped*: the value is left
off this title page rather than entered against an element it does not correspond to. The source
protocol is carrying a retired identifier.

**2 — Short title and acronym are one string.** M11 separates `Full Title`, `Trial Short Title`
and `Trial Acronym`. The source gives *"Short Title: TORIVA-LUNG 301"* and no acronym, so one
string serves two elements. Recorded rather than resolved; a real sponsor would choose.

**3 — `Original Protocol Indicator`.** Through `a806630` the source stated Version 1.0 with no
amendment history, which entailed *Yes* without asserting it, and the indicator was marked
inferred. At `0f78331` the source is v1.2 with an Amendment 1 row, so the indicator is *No*, sourced.

**4 — Proprietary and nonproprietary names are not distinguished.** The source gives
"Torivumab" and "Torivumab 200 mg/10 mL concentrate for solution for infusion". Since the drug
is fictional and no trade name appears, "torivumab" is mapped to `Nonproprietary Names` only,
and `Proprietary Names` is left empty rather than duplicated.

## Conformance

| | |
|---|---|
| Required elements applicable to a v1.0 protocol (through `a806630`) / to v1.2 (at `0f78331`) | 13 / 24 |
| Supplied | **8** by the source at `8534339d`; **10** at `a806630` (Country and Site now in its synopsis table); **1** still supplied here (Sponsor Approval Date) |
| Absent in the source | **5** — Country, Site, and the three Sponsor Approval Date elements. Country and Site now in the source (#27); Approval Date supplied here; the two *Location* elements still absent |
| Amendment-conditional Required elements | 11 — correctly absent through `a806630`; at `0f78331`: 5 supplied from the Document History row (Identifier, Scope inferred, Summary, Details, Primary Reason as *Other*), 6 absent in the source (Secondary Reason and its text, the two Substantial Impact indicators and their explanations) |
| Optional elements supplied | 7 |
| Optional elements deliberately left unmapped | 1 — EudraCT, see note 1 |

## Corrected and supplied under P6 (2026-09-20) — and what the source now carries (`a806630`, #27)

Phase 2, stage P6 supplied three elements and corrected one; TORIVA issue #27 then put most of
it into the source itself. Each row says where the content stands now.

| M11 element | Now | Source of the content |
|---|---|---|
| **Full Title** | the combination, as in the table above | **now the source's** (`a806630`, PR #33). Under P6 this project corrected it to the SAP; the correction is retired and this row is its record |
| **Country Identifier** | Australia, Canada, France, Germany, Italy, Japan, Netherlands, Poland, Republic of Korea, Spain, United Kingdom, United States of America — **12** | **now the source's** synopsis table (*Countries / Sites*). The P6 list had 13, from ADSL at `8534339d`, which included Brazil; the regenerated data (#42, sites kept inside the three stratification regions) has 12, and the synopsis states 12 |
| **Site Identifier** | 15 investigational sites | **now the source's** synopsis table |
| **Sponsor Approval Date** | 20 September 2026 | **still supplied here**: the version date of protocol v1.2 (at `0f78331`; 22 March 2026 while the source was v1.0), taken as the approval date. The source still carries no approval date |
| Sponsor Approval Date Location; State location where held | still absent | no source, and inventing one would be a design choice |

*Supplied under P6 (2026-09-20, LG's decision), not by the source protocol — now only the Sponsor
Approval Date.* Dispositions: [`../../gap-register.md`](../../gap-register.md) D14, G2.

**D18, found at the re-pin — resolved.** At `a806630` the synopsis was substantively amended and still
said *Version 1.0, 22 March 2026*, with a history ending at v1.1. Filed as TORIVA #53; fixed in PR #54
(`0f78331`): Protocol v1.2, 20 September 2026, an Amendment 1 history row, and the SAP's protocol
reference updated. The version rows above, §12.3 and the amendment elements now come from the source.
