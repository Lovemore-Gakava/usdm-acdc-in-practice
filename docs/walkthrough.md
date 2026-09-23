# Hands-on walkthrough — drive one endpoint through the builder yourself

Phase 2, stage **P4** (`NORTH.md`). Written 2026-09-19 from what was actually clicked on the
two endpoints, including the places that caught me; revised 2026-09-20 after TORIVA issues #27 and
#53 changed the source and its data (P7). Budget about forty-five minutes for the
laboratory endpoint end to end; the vital-signs MMRM is a second pass of the same steps plus one
extra.

Everything below runs on the **aligned study** — the USDM generated from the M11 protocol, itself
restructured from TORIVA's synopsis at the pinned commit — and on TORIVA's real datasets, regenerated
under #27. You will see the number the repository reports (`endpoints/01-simple-lab-cfb/results.json`,
`p7_rerun_a806630`) come out of the browser.

**A recording of the lab endpoint, start to finish:** [`media/walkthrough-lab-endpoint.gif`](media/walkthrough-lab-endpoint.gif)
(50 frames, 10 MB, no sound; recorded 2026-09-22 on the data at `a806630`). It shows the study card,
the Objectives tab and the endpoint tick, step 3 with the concept category and the four Smart Phrases
ticked, then steps 3 to 7 as the saved chain fills them, and step 8 configured, executed, and its result:
429 rows, contrast 1.2757. Two honest limits: the typing at step 3 and the node clicks at step 6 are not
in it — the saved chain was loaded at that point, so those frames show the outcome rather than the
keystrokes — and the browser window changed size part-way, so the later frames are smaller. Native
dialogs (the xpt upload) cannot be recorded and were done behind the page.

## 0. Before you open the browser

**The short way** (added 2026-09-20): one command does everything in this section except the two
once-per-clone git settings —

```
python tools/walkthrough.py serve
```

While it runs, **this guide is served as a page at `http://localhost:8080/walkthrough`** — open it in
a second tab beside the app. Without the server, `python tools/walkthrough.py html` writes the same
page as a file you can open directly.

It checks that your TORIVA checkout is at the pin, converts ADSL, ADLB and the induction-window
ADVS to `.xpt`, stages the study, the three saved chains and the M.MMRM implementation into the
app, serves it at `http://localhost:8080/ac-dc-app/index.html`, and on Ctrl-C removes everything it
staged so the submodule is clean again. The page it serves carries a small overlay of its own —
a *(no filter)* entry in every slice dropdown, the M.MMRM implementation registered, the `mmrm`
package installed once the engine is up — so every step below is done on the page, none in the
browser console. The upstream app has none of that; the guide says at each point what the
overlay supplied. About a minute before the URL answers, most of it the
ADLB conversion. `stage` and `clean` are the two halves on their own; if the server was killed
rather than stopped, run `clean`. The command refuses to start while something else holds port
8080, and says which process.

> **If you see "Failed to load data — Failed to fetch"** on a page served by upstream's
> `python ac-dc-app/serve.py`, that is the server, not the app: it is the single-threaded
> `HTTPServer` with a listen backlog of five, and the app fires about twenty-two fetches at
> once on load, some of which are dropped (seen on Windows, 2026-09-20; the first version of
> this script did the same, because it launched `serve.py`). `walkthrough.py serve` serves the
> same directory with the same no-cache headers from the standard library's threading server. The staged files are at `ac-dc-app/data/toriva/` for step 8's
upload dialog.

**The long way**, kept as the record of what the command does (once per clone for the first block):

```
git config core.hooksPath .githooks
git -C upstream/analysis-concepts config core.autocrlf false
git -C upstream/analysis-concepts checkout -- ac-dc-app/r/acdc_engine.R
pip install pyarrow pyreadstat
```

The second and third lines matter on Windows: with `autocrlf=true` the engine's R source is
checked out with CRLF and step 8 fails to parse it (`unexpected invalid token`).

**Check the pin first.** `python tools/check_alignment.py --require-data` should print `PASS documents pin`
with the commit `study/source-refs.md` names (`0f78331` at the time of writing). If it says WARN, your
TORIVA checkout is not at the pin and the numbers below will not be yours.

**Data.** TORIVA ships parquet; the builder wants `.xpt`. From the checkout of
`OpenTrialReporting/torivumab-nsclc-301` at the pin (the datasets are those regenerated under #27 at
`a806630`; #53 changed documents only):

```python
import pyarrow.parquet as pq, pyreadstat
for name in ("adsl", "adlb"):
    df = pq.ParquetFile(f"<toriva>/datasets/adam/{name}.parquet").read().to_pandas()
    for c in df.columns:
        if str(df[c].dtype) in ("object", "str", "string"):
            df[c] = df[c].astype(str).where(df[c].notna(), None)
    pyreadstat.write_xport(df, f"{name}.xpt", file_format_version=5, table_name=name.upper())
```

**Stage the study into the app** (a throwaway edit inside the submodule — revert it after):

```
cd upstream/analysis-concepts
cp ../../study/usdm/toriva-lung-301.usdm.json ac-dc-app/data/usdm/
```

and add a line `{ "file": "toriva-lung-301.usdm.json" }` to `ac-dc-app/data/usdm/studies.json`.
Then `python ac-dc-app/serve.py` and open `http://localhost:8080/ac-dc-app/index.html`.

When you are done: `git checkout -- ac-dc-app/data/usdm/studies.json` and delete the copied
file, so the submodule is clean at `739344c`.

## 1. Select Study

Three cards. Click **TORIVA-LUNG 301**. The card says *2 Arms · 6 Objectives · 7 Endpoints*.

*What you are looking at:* the USDM file, parsed. The rationale paragraph on the next page is
the generator's own provenance note — it names `tools/m11_to_usdm.py`.

## 2. Study Overview

Tabs across the top. Two to look at:

- **Arms** — *Torivumab + Chemotherapy* and *Placebo + Chemotherapy*, as the source protocol now
  states (D14: it said monotherapy until #27 corrected it; this project had corrected it under P6
  the day before). The notes on each arm carry that history.
- **Schedule of Activities** — *13 activities · 39 encounters*. This tab was empty for the
  whole of phase 1; the schedule was generated from the protocol's two assessment tables.
  Clicking a concept opens its panel. **Its *Reference* link opens the concept's SDTM dataset
  specialization in the CDISC Library — if you gave the server a key.** Without one, the link goes
  to the Library API directly and answers 401 (`Access denied due to missing subscription key`).
  To make it work:

  1. Sign in at [library.cdisc.org](https://library.cdisc.org) (a free account) and copy your **API
     key** from your account page.
  2. Save it once, as the only line of a file named `.cdisc-api-key` in the repository root (the
     file is git-ignored) or in your home directory. Then start the server as usual:

     ```
     python tools/walkthrough.py serve
     ```

     `stage` reports *CDISC_API_KEY set: 6 concept references routed through /cdisc-library/*. (An
     environment variable `CDISC_API_KEY` works too and takes precedence, if you prefer that.)
     The server forwards those requests to the Library with the key; the fragment in the
     repository is not changed, only the staged copy.
  3. Click **Reference** again: the specialization opens in a new tab as a page — the domain,
     source and package, the parent biomedical concept as a link, and a table of the variables
     with their roles, codelists, assigned terms and relationships. A *raw JSON* link at the top
     gives the document as the Library sent it. (Until 2026-09-23 the tab showed the raw JSON;
     LG's verdict: *not pretty*. The page is the walkthrough server's rendering.) (Until 2026-09-20 the
  fragment carried a relative path copied from the pilot, which landed on this server's 404
  page — that is what "reviewing the BC" ran into. The pilot's own fragment still does the same
  for 32 of its 182 concepts.) The seven laboratory concepts and SYSBP link to their SDTM
  dataset specializations where the pilot's fragment gave the identifier; creatinine and
  neutrophils have none, and say so in their notes.

Then **Objectives & Endpoints**: tick **END-S5-LAB** (under OBJ-S5). One endpoint selected.
Click **Specify Endpoints →**.

## 3. Endpoint — what is measured

- **Concept category:** *Change (Comparison)*. Data type stays *Quantity*.
- The **Smart Phrases** panel appears on the right. Tick **Population**, **Treatment grouping**,
  **Timepoint**, and **ANCOVA method**.
- Two small dropdowns inside the **Parameter** and **Timepoint** rows of the Smart Phrases panel
  choose the *form* of the dimension. Set **Parameter (DC, label form — PARAM-equivalent)** and
  **AnalysisVisit (DC, analysis-derived visit)**. **Do not tick the Parameter box** for this: it
  stays unticked, its dropdown works anyway, and the Parameter dimension is in the endpoint's data
  cube whether or not the box is ticked (checked on the page 2026-09-23, after LG asked). The
  Timepoint box is one of the four you ticked above, so its dropdown is in a ticked row.

  > **Why this matters.** The engine filters on dimension names as literal columns of the
  > data. The OC forms (`Observation.Identification.Topic`, `Visit`) have no column in ADaM; the
  > DC forms are `PARAM` and `AVISIT`. On the first pass this was learned at step 8, after two
  > failed runs.

- **Dimension Values:** Parameter → type `Alanine Aminotransferase` (the label, not `ALT`);
  Population → *SAF*; Treatment → *Torivumab + Chemotherapy vs Placebo + Chemotherapy*;
  AnalysisVisit → pick **Cycle 2 Day 1** from its dropdown; **Visit** (the free-text box labelled
  *VISIT/VISITNUM*) → type `C2D1`. A dimension left empty here gets no row in step 8's slices
  table, so this is the only place the collected-visit slice can be created (LG's run, 2026-09-23:
  no Visit box filled, no Visit row at step 8, 1.585 on 434 rows instead of the number below).

  > **Two names for one visit.** The AnalysisVisit dropdown lists the study's encounters by the
  > label the protocol gives them, *Cycle 2 Day 1*, because the fragment's schedule was generated
  > from the protocol. The data's analysis-visit code is the SAP's, `C2D1`. `C2D1` is not offered
  > here, and *Cycle 2 Day 1* matches nothing in the data, so at step 8 you will re-pick the value
  > from the data's own list (item 5 there). The recorded chain carries `C2D1` because it was
  > authored in phase 1, when the fragment had no encounters and the value was typed. *Added
  > 2026-09-23 after LG found the dropdown had no `C2D1`.*

The composed phrase at the bottom should read *change from baseline in Alanine
Aminotransferase in the SAF population comparing … at C2D1 using analysis of covariance …*.

## 4. Analysis — how it is analysed

Tick **Change From Baseline ANCOVA** in the templates panel. The card shows the bindings:
response `CHG (Change)`, covariate `AVAL @ Parameter=Alanine Aminotransferase,
AnalysisVisit=Baseline`, fixed effect `TRTP (Treatment)`, and the model expression
`CHG ~ AVAL@Parameter_baseline + TRTP`. Type III, alpha 0.05.

> If the page goes blank here, you have hit V1: a binding declared by category rather than by
> concept was left unresolved on selection. Reload and select the template again; if it
> persists, this is the one place the guide cannot get you through the UI — see
> `endpoints/04-vitals-cfb-mmrm/log.md` V1 for the two-line console fix.

## 5. Summary

One card: *Change from baseline in Alanine Aminotransferase at C2D1*. Note **0 With Estimand**
— the card reads the chain's own estimand field, not the USDM's E6. Carry on.

## 6. Derivations — how the number is made

A pipeline graph. `T.ChangeFromBaseline` has already been chosen for `CHG` (the only
candidate). Three measure slots show ● — minuend, subtrahend, covariate. Click each, and in
the panel on the right scroll to the **bottom** of the nine templates and pick
**`AVAL/AVALC/BASE (Measure) (raw)` — Use source data directly**. Nine wrong options sit above
the right one; this is L2.

Click the **TRTA/TRTP (Treatment)** node and **Confirm**.

**Link the BC.** Click each of the three measure nodes again; a list of the study's eight
Biomedical Concepts appears. Tick **ALT Alanine Aminotransferase** on each. (The picker offers
all eight regardless of which the endpoint names — L5.)

Every node now shows ✓. Click **Save** in the header if you want the chain as a file — it is
what `chain.json` is.

## 7. eSAP Builder

Five tabs: SAP Document, ADaM Datasets, ADaM Spec, JSON, Define-XML. In the SAP Document,
§5.1.1.2 *Main Analytical Approach* shows END-S5-LAB with *1 analysis*. In the JSON tab the
estimand's `analysisPopulation` is `SAF` and `interventions` are both arms — supplied by the
chain's dimension values, not by the USDM's estimand (L6).

## 8. Execute

1. **Initialize WebR Engine.** About thirty seconds; the page may freeze while it installs
   `haven`.
2. **Upload .xpt files** — `adsl.xpt` and `adlb.xpt`. The 45 MB file takes ten to twenty
   seconds and the page freezes again.
3. **Source dataset:** `adlb`.
4. In the **Resolved bindings** table (the upper one), two dropdowns in the *Implementation
   Variable* column:
   - row **covariate / Measure**: change `AVAL` to **`BASE`**. The default `AVAL` is the C2D1
     value — the response's own minuend — and run 3 of the first phase was fitted that way.
   - row **fixed_effect / Treatment**: change `TRTP` to **`TRT01P`**.
5. In the **Resolved slices** table (the lower one):
   - row **endpoint / Population**: variable `ITTFL` → **`SAFFL`**, value `SAF` → **`Y`** (the
     default matches nothing).
   - row **endpoint / AnalysisVisit**: value → **`C2D1`**, from the data's list. The step-3 value,
     *Cycle 2 Day 1*, is the protocol's label and matches no row; the console log would show
     `Filter: AnalysisVisit == Cycle 2 Day 1 → 0 rows`.
   - row **endpoint / Visit**: value → **`C2D1`**. This is the *collected* visit (`VISIT`) beside the
     analysis visit (`AVISIT`) the endpoint already carries. The recorded run had both. Without it
     the cube keeps seven unscheduled draws that the SAP's visit windows assign to C2D1, and the
     answer is 1.585 (SE 2.194) on 434 rows instead of the number below. *Added 2026-09-22 after
     LG's run came out at 1.585: the guide had promised a number without naming the slice that
     produces it.*
   - row **endpoint / Treatment**: variable → **`TRT01P`**, value → **`(no filter — keep all
     values)`**, the first entry in the dropdown. The step-3 value is a contrast label, not a data
     value; any of the app's own three entries keeps one arm and the run fails with *"contrasts
     can be applied only to factors with 2 or more levels"*. The engine treats an empty value as
     no filter, and that entry sets one.

     > **That entry is not the app's.** The upstream page offers no way to clear a slice; the
     > walkthrough server adds the option to every slice-value dropdown when it serves the page
     > (an overlay script; the submodule is untouched). If you serve the app any other way, the
     > equivalent is the browser console: `const r = window.appState.endpointResults.Endpoint_SAFETY_LAB;
     > r.sliceOverrides = r.sliceOverrides || {}; r.sliceOverrides['endpoint|Treatment'] = { variable: 'TRT01P', value: '' };`
     > *History: the guide first said "leave the value blank", written from an automated run that
     > set the state directly; LG found on 2026-09-22 that there was no blank to leave, the console
     > line was the fix for a day, and the overlay replaced it the same evening.*
6. **Execute.** About twenty seconds. The console log in the result should show four `Filter:`
   lines — Parameter, `SAFFL == Y`, `Visit == C2D1`, `AnalysisVisit == C2D1` — and no Treatment
   line; 429 rows in the cube, 427 in the model. The result: contrasts, LS means, type-3 tests,
   fit statistics. The engine reports the contrast as placebo minus torivumab, so it shows
   **+1.276**; the guide's *torivumab minus placebo* below is the same number with the sign
   reversed.

*What you should see* (on the data regenerated under #27): Torivumab − Placebo on ALT change from
baseline at C2D1 = **−1.276 (SE 2.215, n = 429)**. On the data before #27 (`8534339d`) it was −1.830
(SE 1.768, n = 432). Compare it with `endpoints/01-simple-lab-cfb/comparison.md`, section *At `a806630`*:
the same model on TORIVA's own `CHG`, `BASE` and `ANL01FL` gives **−1.305 (SE 1.607)**, and the
difference is the baseline row the engine picks — first row in the Baseline window rather than the
`ABLFL` row — for 72% of subjects. Before #27 the reference was −0.893 and the share 70%.

## The second pass: vital signs by MMRM

Same steps, with these differences:

- Step 2: tick **END-S5-VS**. Step 3: Parameter `Systolic Blood Pressure`; tick **MMRM
  method**; leave AnalysisVisit's value **blank** — MMRM takes every visit. Step 4: **Change
  From Baseline MMRM Primary Analysis**. Step 6: link **SYSBP** on the three measure nodes.
- Data: convert `advs.parquet`, restricted to `AVISIT` in Baseline, C2D1 … C6D1 (C1D15 existed only before #27) — an
  unstructured covariance over forty visits is not a fit anyone runs, and the cube's visit
  dimension cannot express a set.
- Upstream ships no R implementation for `M.MMRM`; the one this project wrote is
  `endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json`. **Served by the walkthrough server, it is
  registered for you**: a status box at the bottom right says *M.MMRM implementation registered*
  when the app loads, and *mmrm package installed* about half a minute after you initialise the
  WebR engine (the engine does not act on an implementation's `packages` list, so the overlay
  runs `webr::install("mmrm")` for you). Wait for the second message before Execute.

  Served any other way, the two console lines are: `window.appState.methodImplementationCatalog.implementations['M.MMRM'] = [await (await fetch('/ac-dc-app/data/toriva/r_impl_mmrm.json')).json()]`
  and, after the engine is initialised, `await (await import('/ac-dc-app/js/utils/webr-engine.js')).executeR('webr::install("mmrm")')`.

  Then Execute; the fit takes one to two minutes and the page freezes while it runs. Expect **−4.44 (SE 1.91)** at C2D1 (torivumab − placebo) against a reference of −1.80 on the data at `a806630`; it was +1.38 against +1.95 before #27 — same mechanism, new data. Five visits now: the C1D15 visit no longer exists (D17).

## What to notice

Sixteen decisions in the second pass, none of them statistical, ten of them repeats. The
number comes out; the reason it differs from the trial's own is the same on both endpoints, and it
survived a regeneration of the data: new numbers on 2026-09-20, the same 70-odd per cent of
subjects with a different baseline row.
That is the thing the whole traverse exists to show, and it is more convincing when the
click that causes it is your own.
