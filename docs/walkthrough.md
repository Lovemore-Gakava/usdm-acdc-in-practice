# Hands-on walkthrough — drive one endpoint through the builder yourself

Phase 2, stage **P4** (`NORTH.md`). Written 2026-09-19 from what was actually clicked on the
two endpoints, including the places that caught me. Budget about forty-five minutes for the
laboratory endpoint end to end; the vital-signs MMRM is a second pass of the same steps plus one
extra.

Everything below runs on the **aligned study** — the USDM generated from the M11 protocol under
phase 2 — and on TORIVA's real datasets. You will see the number the repository reports
(`endpoints/01-simple-lab-cfb/results.json`) come out of the browser.

## 0. Before you open the browser (once per clone)

```
git config core.hooksPath .githooks
git -C upstream/analysis-concepts config core.autocrlf false
git -C upstream/analysis-concepts checkout -- ac-dc-app/r/acdc_engine.R
pip install pyarrow pyreadstat
```

The second and third lines matter on Windows: with `autocrlf=true` the engine's R source is
checked out with CRLF and step 8 fails to parse it (`unexpected invalid token`).

**Data.** TORIVA ships parquet; the builder wants `.xpt`. From a checkout of
`OpenTrialReporting/torivumab-nsclc-301` at `8534339d`:

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

- **Arms** — *Torivumab + Chemotherapy* and *Placebo + Chemotherapy*, as the corrected
  protocol names them (D14, P6); the source protocol said monotherapy, and the data agrees.
- **Schedule of Activities** — *13 activities · 39 encounters*. This tab was empty for the
  whole of phase 1; the schedule was generated from the protocol's two assessment tables.

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

*What you should see:* Torivumab − Placebo on ALT change from baseline at C2D1 = **−1.830
(SE 1.768, n = 432)**. Compare it with `endpoints/01-simple-lab-cfb/comparison.md`: the same
model on TORIVA's own `CHG` and `BASE` gives −0.893, and the whole difference is the baseline
row the engine picks.

## The second pass: vital signs by MMRM

Same steps, with these differences:

- Step 2: tick **END-S5-VS**. Step 3: Parameter `Systolic Blood Pressure`; tick **MMRM
  method**; leave AnalysisVisit's value **blank** — MMRM takes every visit. Step 4: **Change
  From Baseline MMRM Primary Analysis**. Step 6: link **SYSBP** on the three measure nodes.
- Data: convert `advs.parquet`, restricted to `AVISIT` in Baseline, C1D15, C2D1 … C6D1 — an
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

  Then Execute; the fit takes one to two minutes and the page freezes while it runs. Expect **+1.38 (SE 1.93)** at C2D1 against a reference of +1.95 — same mechanism.

## What to notice

Sixteen decisions in the second pass, none of them statistical, ten of them repeats. The
number comes out; the reason it differs from the trial's own is the same on both endpoints.
That is the thing the whole traverse exists to show, and it is more convincing when the
click that causes it is your own.
