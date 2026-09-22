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
staged so the submodule is clean again. About a minute before the URL answers, most of it the
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
  3. Click **Reference** again: the specialization's JSON opens in the new tab. (Until 2026-09-20 the
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
- Two small dropdowns inside the Parameter and Timepoint phrases choose the *form* of the
  dimension. Set **Parameter (DC, label form)** and **AnalysisVisit (DC, analysis-derived visit)**.

  > **Why this matters.** The engine filters on dimension names as literal columns of the
  > data. The OC forms (`Observation.Identification.Topic`, `Visit`) have no column in ADaM; the
  > DC forms are `PARAM` and `AVISIT`. On the first pass this was learned at step 8, after two
  > failed runs.

- **Dimension Values:** Parameter → type `Alanine Aminotransferase` (the label, not `ALT`);
  Population → *SAF*; Treatment → *Torivumab + Chemotherapy vs Placebo + Chemotherapy*;
  AnalysisVisit → type `C2D1`.

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
4. In the resolved-bindings table: **Treatment → `TRT01P`**; **Measure (the covariate) →
   `BASE`**. The default `AVAL` is the C2D1 value — the response's own minuend — and run 3 of
   the first phase was fitted that way.
5. In the resolved-slices table: **Population → variable `SAFFL`, value `Y`** (the default is
   `ITTFL = SAF`, which matches nothing). **Treatment → leave the value blank** — the step 3
   value is a contrast label, not a data value, and a blank means no filter.
6. **Execute.** About a minute. The result: contrasts, LS means, type-3 tests, fit statistics.

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
- Step 8 will say **`No R implementation available for M.MMRM`**. Upstream ships none. The
  one this project wrote is `endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json`; to use it, open
  the browser console on step 8 and run:

  ```js
  const impl = await (await fetch('/ac-dc-app/data/toriva/r_impl_mmrm.json')).json();
  window.appState.methodImplementationCatalog.implementations['M.MMRM'] = [impl];
  ```

  (after copying that file into `ac-dc-app/data/toriva/` so the page can fetch it). The `mmrm`
  package must also be installed in the WebR session — once per page load — which the engine
  does not do from the implementation's `packages` list. In the same console:

  ```js
  const eng = await import('/ac-dc-app/js/utils/webr-engine.js');
  await eng.executeR('webr::install("mmrm")');   // about half a minute
  ```

  Then Execute; the fit takes one to two minutes and the page freezes while it runs. Expect **−4.44 (SE 1.91)** at C2D1 (torivumab − placebo) against a reference of −1.80 on the data at `a806630`; it was +1.38 against +1.95 before #27 — same mechanism, new data. Five visits now: the C1D15 visit no longer exists (D17).

## What to notice

Sixteen decisions in the second pass, none of them statistical, ten of them repeats. The
number comes out; the reason it differs from the trial's own is the same on both endpoints, and it
survived a regeneration of the data: new numbers on 2026-09-20, the same 70-odd per cent of
subjects with a different baseline row.
That is the thing the whole traverse exists to show, and it is more convincing when the
click that causes it is your own.
