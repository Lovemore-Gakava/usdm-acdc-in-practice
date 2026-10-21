# Decisions

How the project got where it is: every dated decision, in the order it was taken.

Split out of `NORTH.md` on 2026-09-26. NORTH had grown to 352 lines carrying 27 dated
markers, so the document that is supposed to say *where we are going* could only be read
by wading through *how we got here*. The two are different genres and now live apart:
**NORTH holds the destination, the scoreboards and the test; this file holds the history.**

Nothing here was rewritten in the move. The repository's rule is that corrections stay
visible rather than being deleted, and this is where they stay visible. Where a decision
was later revised, both are here, in order.

Scoreboards are in [`NORTH.md`](../NORTH.md) — they are computed from the filesystem by
`tools/check_consistency.py` and cannot be stated by hand.

---

## The finish line, and how it moved

Done means all nine green, on at least one endpoint. Nothing else counts as finishing.

**Reached 2026-09-17, on laboratory change from baseline.**

**Decided 2026-09-18: write the explanation.** LG asked for the plain-language walkthrough as a
vignette, which is the second of the four options that were on the table (freeze; write the
explanation; re-author the lab tier cleanly; a second endpoint). It is the *explain* half of the
destination, and it is written: [`docs/vignette.md`](vignette.md).

**Decided 2026-09-19: a second endpoint.** Systolic blood pressure, change from baseline, by
MMRM — chosen because it is new on three axes at once (a vital-signs BC, the ADVS dataset, and
`M.MMRM` with every visit as the repeated factor) and because it composes: `T.CFB_MMRM_Primary`
exists in the library. Its finish line is the second table below; the checker scores it from
`endpoints/04-vitals-cfb-mmrm/`, M11 §8.4.2 and BC `C25298` only, so it cannot inherit the
lab tier's rows.

*(scoreboard in [`NORTH.md`](../NORTH.md))*

This table is **verified against the filesystem** by `tools/check_consistency.py`, which the
pre-commit hook runs. It cannot quietly say ✓ for something that has not happened, and the
scoreboard prints on every commit.

### Endpoint 2 — systolic blood pressure, change from baseline, MMRM

*(scoreboard in [`NORTH.md`](../NORTH.md))*

Stage 0 for this endpoint is M11 **§8.4.2 Vital Signs** — one Required element, mapped in
`study/m11/protocol-to-m11.md` on 2026-09-19: TORIVA supplies the schedule and the list of
measurements, and no text of collection procedures. Stage 0b is a `section-08-04-02-vital-signs.md`
under `study/m11/protocol/` and the USDM regenerated to cite it; stage 1 is the BC `C25298` in
the fragment; stages 2–7 live in `endpoints/04-vitals-cfb-mmrm/`. The reference for stage 7 is
an MMRM fitted in local R (`mmrm` 4.6), since Python has no equivalent.

**Reached 2026-09-19, the same day.** Stages 2–5 in the builder with the lab tier's lessons
applied up front. Stage 6 stalled on `No R implementation available for M.MMRM` — upstream
ships the template and the method and nothing to run it with — and LG asked why one could not
be written. One was: [`endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json`](../endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json),
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
> on the way (D1–D18, the missing M11 estimand elements, the vital-signs procedures) fixed in
> this repository's derived M11 protocol, the whole protocol digitised to USDM *by generation*
> rather than by hand, the protocol, SAP, USDM and ADaM specifications checked against each other
> by a tool, and a hands-on walkthrough so the traverse can be driven, not watched.

Two scoping decisions, LG's: the gaps are fixed **here, in the derived work** — TORIVA upstream
stays as it is and nothing is filed; and the **walkthrough is a stage**, not an extra. A third,
2026-09-20, revised the first: *fix here* had meant the derived documents follow the built data;
it now means **the documents are made correct and the data is what diverges** (P6, below).

*(scoreboard in [`NORTH.md`](../NORTH.md))*

What makes each row green, as the checker computes it: **P0** `study/gap-register.md` naming
every D-item in `source-refs.md` with a disposition; **P1** `study/m11/protocol/coverage.json`
listing all fourteen M11 sections with a status; **P2** the USDM fragment carrying activities
and a schedule of activities and naming `tools/m11_to_usdm.py` as its generator; **P3**
`tools/check_alignment.py` exiting 0 *with the data layer run* — on a clone without TORIVA the row
is red, by LG's decision of 2026-09-20 (review-sheet 4c); **P4** `docs/walkthrough.md`; **P5** every
`endpoints/*/results.json` carrying the aligned fragment's `usdm_sha256` — or, since the second re-pin of
2026-09-20, the hash of the content a chain binds to (`usdm_exec_sha256`), so a provenance-only change
to the fragment does not stale the runs; **P6** the alignment
tool reporting all six P6 decisions as PASS on its `P6 decisions: n/6` line; **P7** `study/source-refs.md`
pinning the commit the TORIVA checkout is at, the alignment tool at 0 warn with the data layer, and every
`endpoints/*/results.json` carrying a run stamped with that pin.

The test still applies, with the stage numbers now P0–P7. The two endpoint scoreboards stay as
they are: green, and the record of the first phase.

**Reached 2026-09-19, the day it was decided.** P0 the register (15 discrepancies — D15, the 2:1
versus 1:1 randomisation, found reading the synopsis whole; 8 M11 gaps; 3 analyses this project
supplied; 4 exclusions). P1 eleven sections moved by `tools/m11_restructure.py`, 795 source lines (803 until the 2026-09-20 moves; one blank line and one duplicated line fewer),
every absent element recorded. P2 the USDM generated by `tools/m11_to_usdm.py` — a schedule of
activities at last (13 activities × 39 encounters), arms named as the data names them. P3
`tools/check_alignment.py`, which on its first run found five of seven endpoint texts written
rather than moved, and now passes with five known upstream divergences confirmed against the
data. P4 the walkthrough. P5 all three runs repeated on the generated fragment: **identical to
the last decimal** — the lab ANCOVA, the vitals MMRM at every visit, the vitals ANCOVA — which
is what "aligned" has to mean for an execution: the study description changed, the number did
not, and every results file now carries the fragment's hash.

**P7, added 2026-09-20 — re-pinned to the corrected source.** TORIVA issue #27 closed the day it
was filed: eighteen PRs, a signed decision memo, the data regenerated 2:1 through raw → SDTM → ADaM
→ TFL. The re-pin to `a806630` is a stage because everything below P1 rests on the source: the section
map was remapped block by block (842 lines moved, verified verbatim), what P6 supplied and the source now
carries (D14, D11/G7, G5, G6, G2's countries and sites) was retired in place with the P6 text kept as the
record, the D1 check was rewritten to test the time origin and the spec's storage unit after TORIVA showed
the units test was a false positive, and both endpoints were re-run on the regenerated data the same day — new numbers, each reproduced outside
the engine by its own selection (lab −1.276 against a reference of −1.305; MMRM at C2D1 −4.44 against −1.80),
the baseline-row divergence intact at 72% and 71%. One new discrepancy, D18: the synopsis was amended in place with no version bump. Green when the pin matches
the checkout, the alignment tool reports 0 warn, and the results files carry the pin. **Re-pinned again the same
evening to `0f78331`** after TORIVA #53 (D18) closed: Protocol v1.2, an Amendment 1 history row, the SAP's reference
updated. Documents only — the datasets did not change, so the P7 runs stand, and the checker accepts a run
stamped with an earlier commit when the datasets are unchanged since. The derived title page now carries the
version, date and amendment elements from the source; D18 is resolved upstream.

**Filed at TORIVA, 2026-09-20.** LG asked whether the gaps and the data regeneration could be raised on
the TORIVA repository, saw the draft, and said yes: [issue #27](https://github.com/OpenTrialReporting/torivumab-nsclc-301/issues/27), labelled qc/validation/sdtm/adam,
following TORIVA's own #22. The first thing filed anywhere from this project, and LG's decision on the
record. `cdisc-org/analysis-concepts` is untouched; the M.MMRM package stays prepared, not filed. D18, found at the P7
re-pin, followed the same pattern the same evening: [issue #53](https://github.com/OpenTrialReporting/torivumab-nsclc-301/issues/53), on LG's yes to a draft shown first.

**P6, added 2026-09-20 — the documents made correct.** Reviewing item 1 of the phase-2 sheet, LG
withdrew the rule phase 2 had run on: *"my assertion of let's follow what is in the data is
flawed. We should ensure the documents are correct."* Protocol first, SAP after it, programs and
data regenerated to follow — later, in TORIVA. Six decisions, each taken after a statement of
standard practice: **D14** the design is the combination (torivumab or placebo *plus* platinum
chemotherapy) — the protocol is corrected to the SAP, because a placebo-alone first-line control
does not exist; **D15** 2:1 stands as the protocol says and the data's 1:1 is flagged; **D11/G7**
the laboratory analysis is specified as descriptive (values and change by visit, reference-range
shift, worst CTCAE grade) and this project's ANCOVA/MMRM become demonstration analyses, marked;
**G2** countries and site count from the trial's records, approval date = the version date;
**G6** a standard vital-signs procedure paragraph, marked; **G5** central laboratory, marked.
Everything supplied is marked *supplied under P6*; nothing supplied is a design choice presented
as the source's. Regenerating the fragment changed its hash, so P5 went red; both endpoints were re-run on the
corrected fragment the same day and every number was identical (`p6_rerun` in each
`results.json`, with the design note the app loaded recorded beside the run). P5 is green again.

**Decided 2026-09-19, after phase 2 — two things.** (1) LG reviews phase 2:
[`docs/archive/review-sheet-phase2.md`](archive/review-sheet-phase2.md), claims with falsifiers, the
mechanical ones already run; the one that changes the most if disagreed is whether the built
data is the right ground truth for D14/D15. (2) The `M.MMRM` implementation is **offered to
`cdisc-org/analysis-concepts`** — prepared as [`docs/contribution-mmrm.md`](contribution-mmrm.md),
filed only by LG, under LG's name. This is a contribution of working code and does not reopen
the parked issues, which stay parked.

---

## The route — what each stage turned out to mean

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
[`study/m11/protocol-to-m11.md`](../study/m11/protocol-to-m11.md). The headline: **M11 §3.1.1
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
[`study/usdm/README.md`](../study/usdm/README.md).

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

---

## How this went wrong before, in one paragraph

`docs/specification.md` §2 set the objective as *"an artefact that answers: if we adopted this,
what would actually happen, and what would it cost?"* — an adoption-decision frame. That is not
the destination above, and no document in the repository said so. Twenty commits then executed
the written objective faithfully: thirteen findings, five issue drafts, a review plan, and
**1,985 lines of critique against 1,185 lines of framework work**, with stages 1, 2, 5 and 6
never started. Nothing was individually wrong. The compass was.

---

## Phase 3 — the guide

**Decided 2026-09-26 by LG**, after a discussion of why the repository is hard to onboard to:
it bundles decisions, workarounds and the iterative nature of the process. The conclusion was
two audiences, one repository — *"users can see the clean product in the showroom, but can also
step into the factory"* — with the guide published as a site.

Three scoping decisions, LG's: **published as a site from this repository**, not a second repo,
so how the material was produced stays attached to it; **the audience is anyone in pharma, with
or without CDISC knowledge**; and **more endpoints over time**, starting with the two that are
green.

Two decisions taken in the same conversation about how to write it:

**No glossary chapter.** The first draft of the finish line had one. LG: it would be too heavy —
link to the sources and explain only what is needed to follow the flow. G3 became *no term used
without a one-line gloss or a link*, enforced from `docs/guide/terms.yml`, which is minutes per
term rather than a chapter.

**Quarto, not the repository's own renderer.** The first recommendation was to extend
`walkthrough.py`'s renderer, which owes nothing to any dependency. LG: *"people pay attention to
nice layout and presentation."* That changes the answer — hand-writing CSS and navigation is not
the work. The earlier objection to Quarto was the 888 KB of vendored Bootstrap it produced when
it rendered the README; that is answered by never committing the build, and publishing from an
Action instead.

**G0 is first deliberately.** The anti-drift checker is the mechanism, not the polish: written
before the prose, the prose can never get ahead of the facts. Written last it would mean
retro-fitting every figure in the guide, which is how F02 came to assert a premise that had
never been true. A guide that says *"you get −1.276"* is wrong the next time TORIVA is re-pinned,
and TORIVA was re-pinned twice in one day on 2026-09-20.

**G4 is written to extend.** It scores from whatever is in `endpoints/` with a result, so adding
a third endpoint turns the row red on its own and says what is owed — rather than depending on
someone remembering.

**What stays in.** The guide shows the divergences, not just the successes. Stage 7 for the lab
tier is *"we got −1.276, TORIVA's own `CHG` gives −1.305, and 72% of subjects have a different
baseline row."* A teaching guide that hides that is a sales document; one that explains it is the
best lesson in the project.

**The guide does not audit the study (2026-09-26, LG).** The stage 0 chapter named the source
study's missing required elements, and G6 was scoped as a chapter about what the conversion
found wrong with it. Both are withdrawn.

LG's reason is a maintenance one and better than the editorial one: *"this is likely to cause a
drift when I update TORIVA."* A guide that pins the study's current state goes stale every time
the study improves — and it has improved twice already, through issues #27 and #53. Beyond that,
a chapter cataloguing a study's defects is the same drift `CLAUDE.md` names, aimed at a new
target, in the one artefact meant to teach rather than assess.

Two classes were separated in the process, because they look alike and are not:

- **Document-quality findings** — a required element absent, a variable the SAP names that the
  data does not carry — belong to the study. They are already in `study/gap-register.md` and
  were filed upstream. The guide links to the factory; it does not recite it.
- **Methodological divergences** — the stage 7 baseline-row disagreement, where the engine and a
  programmer's datasets disagree about what "baseline" means — stay in, prominently. That is not
  an audit finding; it would happen on any study, and it is the strongest lesson in the book.

Stage 0 is now generic: what typically goes wrong when digitising *a* protocol — misplacement
read as absence, the urge to fix while mapping, the same element disagreeing across synopsis and
body, and selective reading. G6 becomes the feedback loop rather than the defect list: attempting
the conversion surfaces what prose hides, raising it improves the source. The two closed issues
stay as its evidence, since a closed issue is a permanent fact and cannot go stale.

**The guide teaches; the factory keeps the record (2026-10-02, LG).** After driving the lab
endpoint through the application by hand, LG: *"what I am struggling with at the moment is lack
of clarity of BC/AC/DC in the guide. There is a lot of selections without clarity of why and
where these concepts are coming from"*, and then: *"the guide is littered with decisions from
toriva. A guide should show implementation and also a teaching guide — not too much on this went
wrong and we did this, not an app with text of all the workarounds that were done in the study."*

Two changes to the chapters, both from that:

- **Every choice is shown with its list and its reason.** The documents chapter now says where
  each kind of concept is published and separates concept, method and template; stages 2 to 4
  each carry a table of what was chosen for the worked example, from what, and why. The stage 3
  chapter had defined a derivation concept as "a step that computes", which is the template, not
  the concept; corrected. The worked example's parameter, visit and model are stated as this
  project's demonstration choice (gap register S1), which the guide had not said anywhere.
- **"What to look out for" is checks, not a history.** The run-by-run narrative, the workaround
  detail and the factory's decision codes came out of the chapter bodies; *Step into the factory*
  still points at the logs that hold them. G1 still scores the fourth heading, so it stays — as
  what to check before moving on.

This narrows *What stays in* above rather than reversing it: the stage 7 baseline divergence
stays, and still opens the book. What went is the per-stage account of how this traverse got
there. The walkthrough (`docs/walkthrough.md`) is not changed by this.

---

## The guide is not published yet (2026-09-26, LG)

The book was published to GitHub Pages on 2026-09-26 and taken down within minutes, on LG's
*"I do not want the site to be public"* — then *"yet"*, so this is a pause and not a reversal.

Sequence, for the record: Pages was enabled at LG's instruction to publish, the site went live,
G7 was marked green after the URL was verified to serve, and the site was deleted on LG's next
message. The Pages site is gone at the API; GitHub's CDN served cached copies for some minutes
after, which is expected behaviour and was watched rather than assumed.

The exposure was a matter of minutes, on a URL with no inbound links. A new URL is unlikely to
have been crawled in that window, but it cannot be ruled out.

**What was kept.** The workflow, the colophon, the checks that gate a publish. Republishing is
enabling Pages and re-running the workflow — one step, whenever LG wants it. Nothing about the
book changed.

**What was corrected.** The README no longer advertises a published site and explains how to
render locally instead; the colophon no longer says "before publication"; G7 is red again. The
checker would have caught the first of those on the next commit, and the scoreboard is the
reason the row could not quietly stay green.

**The lesson, which is mine rather than LG's.** "Publish the site" was an explicit instruction
and I flagged the private-repository implication before acting — but I flagged it and then acted
in the same breath, having already been told that LG's review was the gate. An instruction to
publish and a standing gate should have been reconciled with LG, not by me. Enabling Pages is
not reversible in the way a commit is: the content was public, however briefly.

---

## The repository is public and the guide is published (2026-10-21, LG)

LG's decision, given at the start of the session: *"now we are going to make this repo public
and publish the site."* The sequence was prepared and shown first, and the two irreversible
steps — the repository's visibility and enabling Pages — were taken only on LG's confirmation,
which is the reconciliation the 2026-09-26 entry says was owed.

Before the switch: no key file or credential is tracked or was ever committed (`git ls-files`
and `git log --diff-filter=A` over the whole history); the study it reproduces,
TORIVA-LUNG 301, is already public under CC BY 4.0; the guide's build job had been green on
every push since the pause. What the public tree now shows that a reader of the site will not
see is the working record — the findings, the archive, the reversed decisions — which is the
*factory* half of the 2026-09-26 Phase 3 decision and is there on purpose.

G7 goes green on the README's link to the site, which is checked, and the row stays green only
while the deploy job stays enabled: the pause of 2026-09-26 shows what the red looks like.
