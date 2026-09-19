# TORIVA-LUNG 301, restructured to ICH M11

`NORTH.md` **stage 0b**, in progress. Stage 0 mapped the protocol against M11 and found the
estimands in the wrong document; this restructures it so they are in the right one.

**A derived work.** Until 2026-09-16 TORIVA was referenced and never reproduced. These files
restructure its protocol synopsis and SAP into M11 form — a derivative of a CC BY 4.0 work,
permitted with attribution, which each file carries along with the source's *FICTIONAL — NOT
FOR REGULATORY USE* banner.

| Section | State |
|---|---|
| [Title Page](section-00-title-page.md) | **done** |
| [§3 Objectives, Endpoints and Estimands](section-03-objectives-endpoints.md) | **done** |
| [§12.1 Clinical Laboratory Tests](section-12-01-clinical-laboratory-tests.md) | **done** |
| `study/usdm/` regenerated from these | **done** |

**Stage 0b complete.**

## What regeneration actually bought

`study/usdm/toriva-lung-301.usdm.json` went from **one `Estimand` to six**. In stage 1 only OS
could be authored, and its description had to say *"sourced from the SAP, not the protocol"*.
Now every objective has an estimand whose `populationSummary`, `analysisPopulationId` and
`intercurrentEvents` derive from M11 protocol §3.1.1/§3.2.x, and two further
`AnalysisPopulation` objects — Response Evaluable and Confirmed Responders — became derivable
because §3 names the populations per estimand.

That is the whole argument for doing 0b before 1 rather than after: USDM's `Estimand` class has
a natural source only once the protocol carries the estimand. Verified by loading the
regenerated fragment in `ac-dc-app` — study listed, all six endpoints rendered under their
objectives — and the submodule reverted afterwards.

**Still absent, and correctly so:** no laboratory estimand (D11). `Estimand_E6` carries the AE
summaries and states in its own `populationSummary` that no laboratory summary is specified in
either source document.

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

**Twenty-five required elements** *(thirty until the 2026-09-18 review — M11 makes the secondary population Optional)* that the source protocol omitted — Population, Treatment,
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

## Added 2026-09-19 — second endpoint

`section-08-04-02-vital-signs.md` — M11 §8.4.2, one Required element, supplied in part: the schedule and the list of measurements are moved from protocol §7.2 and the data-domain table; the collection and interpretation instructions the element asks for are absent from the source and left absent. Its BC (`SYSBP`, `C25298`) and endpoint `END-S5-VS` were added to the USDM fragment from it.
