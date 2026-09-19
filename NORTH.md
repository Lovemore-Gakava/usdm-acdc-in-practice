# NORTH — what this project is for

Read this before starting any piece of work. It is the only document that says what "done"
means; everything else describes how.

---

## Destination

> **Understand USDM and ICH M11, and the AC/DC/BC framework, well enough to explain and
> demonstrate them — by structuring one protocol and taking one endpoint the whole way
> through.**

*Revised 2026-09-16.* The first version said "USDM v4 and the AC/DC/BC framework" and omitted
ICH M11 — the **M11** in what the field calls USDM11. The omission had already cost something:
work that would have advanced the M11 half was turned away by the test in §The test, because
the destination it was tested against was missing that half.

## Finish line

Done means all nine green, on at least one endpoint. Nothing else counts as finishing.

**Reached 2026-09-17, on laboratory change from baseline.**

**Decided 2026-09-18: write the explanation.** LG asked for the plain-language walkthrough as a
vignette, which is the second of the four options that were on the table (freeze; write the
explanation; re-author the lab tier cleanly; a second endpoint). It is the *explain* half of the
destination, and it is written: [`docs/vignette.md`](docs/vignette.md).

**Decided 2026-09-19: a second endpoint.** Systolic blood pressure, change from baseline, by
MMRM — chosen because it is new on three axes at once (a vital-signs BC, the ADVS dataset, and
`M.MMRM` with every visit as the repeated factor) and because it composes: `T.CFB_MMRM_Primary`
exists in the library. Its finish line is the second table below; the checker scores it from
`endpoints/04-vitals-cfb-mmrm/`, M11 §8.4.2 and BC `C25298` only, so it cannot inherit the
lab tier's rows.

<!-- north:status -->

| # | Stage | Status |
|---|---|---|
| 0 | Protocol mapped to ICH M11 elements | ✓ |
| 0b | Protocol restructured to M11, USDM regenerated from it | ✓ |
| 1 | USDM fragments hand-authored | ✓ |
| 2 | BC linked on the chain's terminals | ✓ |
| 3 | DC — derivation authored | ✓ |
| 4 | AC — analysis bound | ✓ |
| 5 | eSAP generated | ✓ |
| 6 | Executed, a real result produced | ✓ |
| 7 | Compared against built ADaM | ✓ |

<!-- /north:status -->

This table is **verified against the filesystem** by `tools/check_consistency.py`, which the
pre-commit hook runs. It cannot quietly say ✓ for something that has not happened, and the
scoreboard prints on every commit.

### Endpoint 2 — systolic blood pressure, change from baseline, MMRM

<!-- north:status:vitals -->

| # | Stage | Status |
|---|---|---|
| 0 | Protocol mapped to ICH M11 elements | ✓ |
| 0b | Protocol restructured to M11, USDM regenerated from it | ✓ |
| 1 | USDM fragments hand-authored | ✓ |
| 2 | BC linked on the chain's terminals | ✓ |
| 3 | DC — derivation authored | ✓ |
| 4 | AC — analysis bound | ✓ |
| 5 | eSAP generated | ✓ |
| 6 | Executed, a real result produced | ✓ |
| 7 | Compared against built ADaM | ✓ |

<!-- /north:status:vitals -->

Stage 0 for this endpoint is M11 **§8.4.2 Vital Signs** — one Required element, mapped in
`study/m11/protocol-to-m11.md` on 2026-09-19: TORIVA supplies the schedule and the list of
measurements, and no text of collection procedures. Stage 0b is a `section-08-04-02-vital-signs.md`
under `study/m11/protocol/` and the USDM regenerated to cite it; stage 1 is the BC `C25298` in
the fragment; stages 2–7 live in `endpoints/04-vitals-cfb-mmrm/`. The reference for stage 7 is
an MMRM fitted in local R (`mmrm` 4.6), since Python has no equivalent.

**Reached 2026-09-19, the same day.** Stages 2–5 in the builder with the lab tier's lessons
applied up front. Stage 6 stalled on `No R implementation available for M.MMRM` — upstream
ships the template and the method and nothing to run it with — and LG asked why one could not
be written. One was: [`endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json`](endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json),
injected into the running app, `mmrm` in WebR. Both the MMRM and the ANCOVA companion executed
and both are **reproduced exactly** by refits outside the engine. Against TORIVA's own `CHG` and
`BASE` they diverge for the lab tier's reason — the engine's baseline is the first row in the
Baseline window, TORIVA's is the `ABLFL` row, 74% of subjects differ — and under MMRM that error
enters every visit: residual variance up a third, AIC 760 worse. Two endpoints, two domains,
two analyses, one mechanism.

## Phase 2 — fix the study, digitise the protocol, verify alignment

**Decided 2026-09-19 by LG**, after both endpoints reached the finish line. A different
destination from the one above, so it gets its own finish line and its own scoreboard:

> **Make TORIVA's study documents right and digital, and show that they agree** — the gaps found
> on the way (D1–D15, the missing M11 estimand elements, the vital-signs procedures) fixed in
> this repository's derived M11 protocol, the whole protocol digitised to USDM *by generation*
> rather than by hand, the protocol, SAP, USDM and ADaM specifications checked against each other
> by a tool, and a hands-on walkthrough so the traverse can be driven, not watched.

Two scoping decisions, LG's: the gaps are fixed **here, in the derived work** — TORIVA upstream
stays as it is and nothing is filed; and the **walkthrough is a stage**, not an extra.

<!-- north:status:phase2 -->

| # | Stage | Status |
|---|---|---|
| P0 | Gap register — every discrepancy with a disposition | ✓ |
| P1 | Protocol fully M11 — all 14 sections covered | ✓ |
| P2 | USDM generated from it, with the schedule of activities | ✓ |
| P3 | Alignment verified by a tool | ✓ |
| P4 | Hands-on walkthrough written | ✓ |
| P5 | Both endpoints re-run on the aligned study | ✓ |

<!-- /north:status:phase2 -->

What makes each row green, as the checker computes it: **P0** `study/gap-register.md` naming
every D-item in `source-refs.md` with a disposition; **P1** `study/m11/protocol/coverage.json`
listing all fourteen M11 sections with a status; **P2** the USDM fragment carrying activities
and a schedule of activities and naming `tools/m11_to_usdm.py` as its generator; **P3**
`tools/check_alignment.py` existing and exiting 0; **P4** `docs/walkthrough.md`; **P5** every
`endpoints/*/results.json` carrying the aligned fragment's `usdm_sha256`.

The test still applies, with the stage numbers now P0–P5. The two endpoint scoreboards stay as
they are: green, and the record of the first phase.

**Reached 2026-09-19, the day it was decided.** P0 the register (15 discrepancies — D15, the 2:1
versus 1:1 randomisation, found reading the synopsis whole; 8 M11 gaps; 3 analyses this project
supplied; 4 exclusions). P1 eleven sections moved by `tools/m11_restructure.py`, 803 source lines,
every absent element recorded. P2 the USDM generated by `tools/m11_to_usdm.py` — a schedule of
activities at last (13 activities × 39 encounters), arms named as the data names them. P3
`tools/check_alignment.py`, which on its first run found five of seven endpoint texts written
rather than moved, and now passes with five known upstream divergences confirmed against the
data. P4 the walkthrough. P5 all three runs repeated on the generated fragment: **identical to
the last decimal** — the lab ANCOVA, the vitals MMRM at every visit, the vitals ANCOVA — which
is what "aligned" has to mean for an execution: the study description changed, the number did
not, and every results file now carries the fragment's hash.

## The route

All four remaining stages run on **one endpoint — laboratory change from baseline**, which is
the only tier that composes. Not on three endpoints. One, all the way.

**Stage 0b — protocol restructured to M11, USDM regenerated from it.** Added 2026-09-16 at
LG's direction. Stage 0 mapped the protocol and found the estimands in the wrong document;
0b moves them. Scoped to the same sections, and **done means both halves** — a restructured
protocol *and* `study/usdm/` regenerated from it, because a restructured section nothing
consumes leaves stage 1's fragment still transcribed from prose.

**Done 2026-09-16.** §3 carries all thirty previously-missing required estimand elements;
the title page and §12.1 are restructured with their gaps recorded rather than filled; and
`study/usdm/` is **regenerated from** the M11 protocol. The payoff is concrete: the USDM
fragment went from **one estimand to six**, because M11 §3 supplies what SAP §13 held and the
protocol had omitted.

**Stage 0 — protocol mapped to ICH M11 elements. Done 2026-09-16.**
[`study/m11/protocol-to-m11.md`](study/m11/protocol-to-m11.md). The headline: **M11 §3.1.1
requires the estimand in the protocol** — five of its seven required elements are ICH E9(R1)
estimand attributes — and TORIVA defers all five to the SAP, failing twenty-five required elements
across six objectives *(thirty until the 2026-09-18 review: M11 makes the secondary population
Optional)*. That independently confirms, and makes countable, what stage 1 found
from the USDM side. Everything M11 wants exists somewhere in TORIVA's document set; none of it
is missing, all of it is misplaced.

The original scoping note follows. The
merged electronic M11 is 303 data elements, 216 of them Required, across 14 sections, each
carrying a CDISC code (`study/source-refs.md`). TORIVA's protocol is **not** M11-structured, so
this is a genuine mapping rather than a re-format, and it is the "M11" half of USDM11.

Scoped to the sections that feed the endpoint being carried — Title Page, §3 objectives and
endpoints, §8.4.4 clinical laboratory assessments — **not** all 216 required elements. A full
protocol digitisation remains a non-goal (`docs/specification.md` §13). First action: map
TORIVA's synopsis sections onto M11 element names, and record which required elements the
protocol does not supply, because that is the interesting half.

It sits before stage 1 logically: the USDM fragment should be a *product* of the M11 mapping
rather than transcribed from prose. Stage 1 was done first, in the other order, and that is
recorded rather than hidden — redoing it is not required, but stage 0 should say where the two
disagree.

**Stage 1 — USDM fragments hand-authored. Done 2026-09-16.**
`study/usdm/toriva-lung-301.usdm.json` — six objectives, six endpoints, seven laboratory BCs,
arms, population and one estimand. Loaded in the app and rendered. What was learned about USDM
v4's shape, and the one honest compromise in it, are in
[`study/usdm/README.md`](study/usdm/README.md).

**Stage 2 — BC linked. Done 2026-09-16.** All three measure terminals of the lab chain carry
the seven TORIVA laboratory BCs. The chain was **re-authored against TORIVA** rather than the
CDISC Pilot, which also retires caveat L1 in `endpoints/01-simple-lab-cfb/log.md`.

Found on the way, by experiment rather than by reading: **the builder ignores USDM's
`Endpoint.biomedicalConceptIds`.** Injecting a study BC deliberately *not* linked to the
endpoint, it was still offered in the terminal picker. So the USDM endpoint→BC join authored in
stages 1 and 0b is not consumed by the chain; terminal-level `linkedBCIds` is an independent,
second join.

**Stage 5 — eSAP generated. Done 2026-09-17.** `endpoints/01-simple-lab-cfb/esap.json` — an
eSAP instance against `study_esap.schema.json`, generated by step 7 from the lab chain with
TORIVA loaded.

Where it sits: the eSAP is the **last artefact of the builder's specification layer and the
input to execution**. Steps 3, 4 and 6 author one endpoint's chain — BC → DC → AC; step 7 puts
that chain into a study-level document bound to USDM's objectives, endpoints and estimands;
step 8 runs it. It is not a fourth concept beside BC, DC and AC. It is the container the chain
goes into. Step 7 renders it five ways from the same state — a fourteen-section SAP document,
ADaM Datasets, an ADaM Spec, the eSAP JSON, and a Define-XML.

What was learned about how the eSAP is built: its estimand is **assembled from two places**.

| E9(R1) attribute | Read from |
|---|---|
| Population-level summary | USDM `Estimand`, matched on `variableOfInterestId` |
| Intercurrent events | USDM `Estimand` |
| Analysis population | the chain's `Population` dimension value |
| Treatment | the chain's `Treatment` dimension value |
| Variable of interest | the endpoint |

The chain reached stage 4 with `dimensionValues: {}`, so the first eSAP carried
`AnalysisPopulation_unknown` and `Intervention_unspecified`. Adding the Population and Treatment
dimensions in step 3 and setting them to `SAF` and the two arms resolved both. So to get a
complete estimand out of step 7, the chain has to carry those two dimensions — USDM's own
`Estimand.analysisPopulationId` is not what step 7 reads for them. Same shape as stage 2's
`Endpoint.biomedicalConceptIds`: the USDM join and the chain's join are separate, and the chain's
is the one the builder uses.

**Stage 6 — executed. Done 2026-09-17.** `endpoints/01-simple-lab-cfb/results.json` — the
lab chain run in step 8 via WebR against TORIVA's ADLB (136,242 rows, converted to `.xpt`).
**The first number this repository has produced:** an ANCOVA of ALT change from baseline at
C2D1, torivumab − placebo = −1.830 (SE 1.768, n = 432). Three runs are kept because each is a
different authoring state; the eleven execution decisions are L7 in the tier's log.

What was learned: step 8 needs real data in the browser and it needs the chain's dimensions in
their **DC forms** — `Parameter`, `AnalysisVisit` — because the engine filters on dimension names
as literal columns of a concept-keyed frame, and the OC forms have no column in ADaM. The
builder's own tooltip says this; the chain reached stage 4 without it.

**Stage 7 — compared against built ADaM. Done 2026-09-17**, this time on a result.
`endpoints/01-simple-lab-cfb/comparison.md`. The executed number does not match the same model on
TORIVA's `CHG` and `BASE` (−0.893, SE 1.385), and every run is **reproduced to four decimals**
once the engine's selection is known. The gap has two halves: authoring — the covariate had
resolved to the C2D1 value, the cube to collected `VISIT` — both fixable in the builder; and the
baseline row, which the engine takes as the first at `AVISIT = Baseline` and TORIVA takes by
`ABLFL`. **303 of 432 subjects (70.1%) differ** — the 71% the paper comparison predicted, now
measured — and that half alone is worth 0.86 on the treatment difference.

> **Was ✓, then ✗, now ✓.** Green from 2026-09-16 on a comparison of definitions; red on
> 2026-09-17 when the checker began requiring stage 6 first; green again the same day on a
> comparison of results.

Findings encountered on the way are recorded in two paragraphs and left alone. They are not
progress.

## The test

Applied to any proposed piece of work, **before starting it**:

> ### Which numbered stage does this advance?

**No number → it does not get done.** It goes in an appendix, or nowhere.

The test is deliberately harder to satisfy than "is this useful?" — nearly anything can be
argued useful. A stage number is a fact.

## This project is not

Naming these because the project drifted into all three once, and the drift was invisible while
it happened.

- **An audit of `cdisc-org/analysis-concepts`.** Their repository is the thing being learned,
  not the thing being assessed.
- **A governance or tooling product.** Part B of the specification is deferred and stays
  deferred until the finish line is green.
- **A critique.** Findings are a **by-product**: recorded when they block a stage, never
  pursued for their own sake, never the measure of progress.

## How this went wrong before, in one paragraph

`docs/specification.md` §2 set the objective as *"an artefact that answers: if we adopted this,
what would actually happen, and what would it cost?"* — an adoption-decision frame. That is not
the destination above, and no document in the repository said so. Twenty commits then executed
the written objective faithfully: thirteen findings, five issue drafts, a review plan, and
**1,985 lines of critique against 1,185 lines of framework work**, with stages 1, 2, 5 and 6
never started. Nothing was individually wrong. The compass was.

## Standing questions

Asked at the start of a session, and before any new artefact:

1. Which stage does this advance?
2. What did I learn about **the framework** — not about its gaps — from the last piece of work?
3. Is the findings count growing faster than the stage count?

If (2) is answered three times running with "that it cannot do X", the project has drifted
again.
