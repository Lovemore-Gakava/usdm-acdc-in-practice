# TORIVA-LUNG 301 → ICH M11

`NORTH.md` **stage 0**. Mapped 2026-09-16 against the merged electronic M11 v0.17.0
(`study/source-refs.md`).

TORIVA's protocol is **not** M11-structured, so this is a mapping, not a re-format. Scoped to
the sections that feed the endpoint being carried: **Title Page**, **§3 objectives and
endpoints**, **§8.4.4 / §12.1 clinical laboratory**. That is 83 of M11's 303 elements, 40 of
them Required.

Full protocol digitisation remains a non-goal (`docs/specification.md` §13).

---

## The headline: M11 requires the estimand in the protocol

M11 **§3.1.1 Primary Objective** has seven Required elements. Five are ICH E9(R1) estimand
attributes:

| M11 element | CDISC code | TORIVA protocol |
|---|---|---|
| Primary Objective | `C85826` | §2.1 ✅ |
| Endpoint | `C25212` | §6 endpoint definitions ✅ |
| **Population** | `C70833` | ❌ **absent from the protocol** |
| **Treatment** | `C49236` | ❌ **absent** |
| **Population-level Summary** | `C188853` | ❌ **absent** |
| **Intercurrent Event Strategy** | `C188857` | ❌ **absent** |
| **Description of Intercurrent Event** | `C188856` | ❌ **absent** |

The same five exist under **§3.2.1** for each secondary objective and **§3.3.1** for exploratory —
but not all of them Required there.

> **Corrected 2026-09-18, on review (review-sheet item 2b).** The merged spec's own element pages
> give `secondary_population` the status **Optional**, and `exploratory_population` and
> `exploratory_intercurrent_event_strategy` likewise. So §3.1.1 carries five Required estimand
> attributes, **§3.2.1 carries four**, and §3.3.1 three. Two smaller things from the same pages:
> the per-objective scoping *is* the spec's (cardinality *"3.2.X where X is a unique number"*),
> and `secondary_description_of_intercurrent_event` carries no CDISC code on its page.
>
> **Whether deferral to the SAP could satisfy these elements** was the one judgement left to LG,
> and LG's answer (2026-09-18) closes it: the SAP is written after the protocol, so a Required
> protocol element cannot be met by pointing at it. *Fails* is the right word.

All five exist — in **SAP §13**. In the protocol the words *"intercurrent"* and
*"population-level summary"* each occur exactly once, both inside a single row of a
deliverables table, naming what the SAP must define rather than defining it. Synopsis line 834
lists
*"Define estimands per ICH E9(R1): target population, variable, population-level summary,
intercurrent event handling strategy … for OS, PFS, ORR separately"* as an **SAP deliverable**.

So TORIVA's protocol fails M11 §3 on **five required elements for the primary objective and four
for each of five secondary objectives — twenty-five required elements** *(originally stated as
thirty; see the correction above)*, all of which the sponsor has written, in the wrong document
for M11.

**This independently confirms what the USDM side showed.** `study/usdm/README.md` recorded that
`Estimand` is the one USDM class the protocol could not supply. M11 says the same thing from
the other direction and makes it countable. Two models, arrived at separately, both expect the
estimand in the protocol; one study puts it in the SAP.

That is the single most useful thing this mapping produced, and it is a property of **document
structure**, not of either standard.

---

## Title Page — 58 elements, 24 Required

TORIVA supplies most of it, which is unsurprising: a title page is a title page.

| M11 element | Req | TORIVA | Value |
|---|---|---|---|
| Full Title | ✔ | ✅ | "A Randomised, Double-Blind, Placebo-Controlled, Phase 3 Study of Torivumab…" |
| Sponsor Protocol Identifier | ✔ | ✅ | `SIMULATED-TORIVUMAB-2026` |
| Sponsor Name | ✔ | ✅ | Celindra Therapeutics |
| Sponsor Legal Address | ✔ | ✅ | 1 Innovation Drive, Suite 400, Cambridge, MA 02139, USA |
| Trial Phase | ✔ | ✅ | Phase 3 → `C15602` |
| Country / Region / Site Identifier | ✔ | ❌ | synopsis is global; no country list |
| Sponsor Approval Date *(+ 2 location elements)* | ✔ | ❌ | not in the synopsis |
| Original Protocol Indicator | ✔ | ⚠️ | inferable — Version 1.0, no amendments — but not stated as such |
| Amendment Identifier / Scope / Summary / Details | ✔ | n/a | conditional on an amendment existing; none |
| Primary + Secondary Reason for Amendment *(+ 2 "Other")* | ✔ | n/a | as above |
| Substantial Impact Safety / Data *(+ 2 explanations)* | ✔ | n/a | as above |
| Trial Acronym | opt | ✅ | TORIVA-LUNG 301 |
| Trial Short Title | opt | ✅ | TORIVA-LUNG 301 |
| Version Number / Version Date | opt | ✅ | 1.0 / 22 March 2026 |
| NCT Number | opt | ✅ | NCT99999999 *(fictional)* |
| FDA IND Number | opt | ✅ | IND-SIM-2026-99999 *(fictional)* |
| EU CT Number | opt | ⚠️ | EudraCT `9999-999999-99` given — **EudraCT is not EU CT**, see below |
| Proprietary / Nonproprietary Names | opt | ⚠️ | "Torivumab" given without distinguishing the two |
| Sponsor Confidentiality Statement | opt | ❌ | §9.4 is *"Data Privacy and Confidentiality"* — a data-protection section (M11 §11.8), not a title-page statement |
| Medical Expert Contact Info | opt | ✅ | Medical Monitor block |
| Sponsor Signatory *(+ 2 location elements)* | opt | ❌ | — |
| Device/Local/Co-Sponsor elements, IDE, NMPA, jRCT, WHO-UTN | opt | n/a | not applicable to this trial |

**Required and genuinely missing: 6** — the three Country/Region/Site identifiers and the three
Sponsor Approval Date elements. Eleven further Required elements are amendment-conditional and
correctly absent from an unamended v1.0 protocol.

### Two things the mapping exposed that reading the protocol did not

**EudraCT ≠ EU CT Number.** M11 has `EU CT Number` (`C218684`), the CTIS identifier that
replaced EudraCT under EU CTR 536/2014. TORIVA gives a EudraCT number. Mapping it to
`EU CT Number` would be wrong; M11 has no EudraCT element at all. The honest mapping is
*unmapped*, and the protocol is carrying a retired identifier.

**M11 splits identity three ways.** `Full Title`, `Trial Short Title` and `Trial Acronym` are
separate elements. TORIVA gives "Short Title: TORIVA-LUNG 301" and no acronym, so the same
string has to serve both — which is how a mapping surfaces an ambiguity that prose hides.

---

## §8.4.4 Clinical Laboratory Assessments — 1 Required

| M11 element | Req | TORIVA |
|---|---|---|
| Clinical Laboratory Assessments (`C218774`) | ✔ | ⚠️ **partial** |

§7.2's Safety Assessment Schedule is a matrix of assessment × visit with ticks — Haematology,
Chemistry (LFTs, creatinine), Thyroid, Cortisol, Urinalysis. It carries **timing** but no
narrative describing the assessments, and the protocol itself flags the gap:

> *"Full Schedule of Assessments (SoA) to be presented as a formal table in the final protocol
> body. The above is a synopsis-level summary."*

## §12.1 Clinical Laboratory Tests — 1 Required

| M11 element | Req | TORIVA |
|---|---|---|
| Clinical Laboratory Tests (`C25294`) | ✔ | ❌ **absent** |

No panel-level list of analytes anywhere in the protocol — and checking each of the seven
parameters the AC/DC chain uses shows why "absent" needed care:

| Parameter | In the protocol? | Where, and for what purpose |
|---|---|---|
| AST, ALT | yes | §5 eligibility (*"AST and ALT ≤2.5 × ULN"*) and the irAE management table at line 549 |
| Bilirubin | yes | §5 eligibility (*"Total bilirubin ≤1.5 × ULN"*) |
| Creatinine | yes | §5 eligibility (*"Serum creatinine ≤1.5 × ULN"*); "Chemistry (LFTs, creatinine)" in the §7.2 schedule |
| Haemoglobin | yes | §5 eligibility (*"Haemoglobin ≥90 g/L"*) |
| Neutrophils | yes | §5 eligibility, as ANC (*"ANC ≥1.5 × 10⁹/L"*) |
| **ALP** | **no** | appears nowhere — its nine apparent hits are all the word *alpha* |

So six of seven appear, **every one of them as an eligibility threshold or an AE-management
rule** — never as a laboratory test to be collected and analysed. That is a different purpose,
and M11 §12.1 asks for the latter. ALP is absent entirely.

The seven parameters the chain actually uses come from `programming-specs/ADLB-spec.md`, a
**downstream programming document**.

That matters for this project specifically. `study/usdm/toriva-lung-301.usdm.json` authors
those seven as `BiomedicalConcept`s. M11 says the protocol should have specified them at §12.1
and it does not, so the USDM BCs are sourced from a programming spec. Recorded, not hidden.

---

## Where this disagrees with stage 1

Stage 1 authored the USDM fragment before this mapping existed, in the wrong order. Checking
one against the other:

| | |
|---|---|
| Objectives, endpoints, arms, phase, population | **agree** — both from protocol §2, §6, title page |
| `Estimand_E1` in the USDM fragment | **both flag it**: sourced from SAP §13 because the protocol omits it. M11 §3.1.1 now says *how much* is omitted — five required elements per objective |
| The seven laboratory BCs | **stage 0 sharpens it.** Stage 1 said only that TORIVA has no lab estimand. M11 §12.1 adds that the protocol should have listed the tests and does not — so the BCs rest on a programming spec |

**No contradiction, and no rework needed.** Stage 0 makes two things quantitative that stage 1
could only gesture at.

---

## What M11 conformance would actually require

Not attempted — it is beyond the destination — but worth stating so the scale is honest:

- **30 estimand elements** across six objectives, which exist in SAP §13 and would move to
  protocol §3
- **6 title-page elements** — country/region/site, sponsor approval date and its locations
- **1 analyte list** at §12.1, which exists in the ADLB programming spec
- the EudraCT → EU CT correction

Every one of these already exists *somewhere* in TORIVA's document set. **None is missing
information; all are misplaced information.** That is the most transferable observation here:
M11 conformance for a study like this is largely a question of which document holds what, not
of writing anything new.

## Method note

M11 element names, Required/Optional status, data types and CDISC codes were parsed from the
merged electronic spec's 303 element pages rather than read off a PDF — see
`study/source-refs.md`. TORIVA's content was read from
`protocol/synopsis.md` at commit `8534339d`; every ✅ above is a quotation or a direct
reference, and every ❌ is an absence checked by search, not an assumption.
