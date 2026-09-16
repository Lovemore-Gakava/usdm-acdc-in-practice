# TORIVA-LUNG 301, restructured to ICH M11

`NORTH.md` **stage 0b**, in progress. Stage 0 mapped the protocol against M11 and found the
estimands in the wrong document; this restructures it so they are in the right one.

**A derived work.** Until 2026-09-16 TORIVA was referenced and never reproduced. These files
restructure its protocol synopsis and SAP into M11 form — a derivative of a CC BY 4.0 work,
permitted with attribution, which each file carries along with the source's *FICTIONAL — NOT
FOR REGULATORY USE* banner.

| Section | State |
|---|---|
| [§3 Objectives, Endpoints and Estimands](section-03-objectives-endpoints.md) | **done** |
| Title page — the 6 missing Required elements | not started |
| §12.1 Clinical Laboratory Tests | not started |
| `study/usdm/` regenerated from these | not started |

Stage 0b is not green until all four are done. A restructured section that nothing downstream
consumes would leave the USDM fragment still transcribed from prose, which is the thing 0b
exists to fix.

## The rule this follows

**Move, do not write.** Every estimand attribute in §3 is transcribed from SAP §13.2–§13.7 and
cited to its section in the row that carries it. Nothing is composed to fill an M11 slot.

Where the source has nothing, the derived document **says so**:

- **No laboratory estimand.** The source specifies three safety estimands, all adverse-event
  based (SAP §13.7). The laboratory endpoint this project carries through the AC/DC chain has
  no estimand in either document. §3.2.5 records the absence rather than inventing a summary.
  Discrepancy **D11**.
- **No exploratory estimands.** SAP §2.3 makes exploratory analyses hypothesis-generating with
  no formal α. M11 §3.3.1 asks for six elements each; §3.3 supplies three and says why.

An M11-conformant document could have been produced by writing the missing pieces. It would
have been a fiction about what the sponsor specified, and the gaps are the interesting part.

## What §3 achieved

**Thirty required elements** that the source protocol omitted — Population, Treatment,
Population-level Summary, Intercurrent Event Strategy and Description of Intercurrent Event,
across six objectives — are now present in the protocol, where M11 §3.1.1 and §3.2.1 require
them. All thirty existed in SAP §13 already.

## What the restructure found: D14

The protocol's title, §2.1 and IMP describe torivumab **monotherapy** versus placebo in PD-L1
TPS ≥50%. The word *carboplatin* appears zero times in the protocol; so does *pemetrexed*; so
does *chemotherapy backbone*.

SAP §13.2's **Treatment** attribute specifies *"Torivumab 200 mg IV Q3W + chemotherapy backbone
(carboplatin AUC5 + pemetrexed 500 mg/m² IV Q3W)"* versus *"Placebo IV Q3W + identical
chemotherapy backbone"*.

Those are two different trials — a KEYNOTE-024-shaped monotherapy study and a
KEYNOTE-189-shaped combination study. Recorded as **D14** and carried forward as written;
reconciling it would mean choosing which document is right, which is not this project's call.

**This is the clearest argument for M11's structure that the project has produced.** While
`Treatment` lives in the SAP and the indication lives in the protocol title, nothing puts them
on the same page and the contradiction survives. M11 requires `Treatment` as a protocol element
in §3, one screen from the title — at which point it is unmissable. The standard did not detect
the error; **the standard's structure made it impossible to miss.**

## Method

M11 element names, Required/Optional status and CDISC codes come from the merged electronic
M11 v0.17.0 (`study/source-refs.md`). Source content is TORIVA at commit `8534339d`:
`protocol/synopsis.md` §2, §6, §7 and `sap/SAP.md` §3, §13. Every row cites the section it came
from, so the restructure can be checked against the source without trusting this document.
