# One endpoint, the whole way through — in plain terms

A walkthrough of what this repository did, written for someone who has not read the rest of it.
Everything technical is linked; nothing here needs it.

## The three letters

CDISC's AC/DC framework describes a clinical analysis in three layers, each a kind of "concept":

- **BC — Biomedical Concept.** *What was measured.* A lab test, with its name, its code and its
  units. Alanine aminotransferase, in U/L, is a BC.
- **DC — Derivation Concept.** *How a number is made from what was measured.* "This visit's
  value minus the baseline value" is a DC.
- **AC — Analysis Concept.** *How the derived numbers are analysed.* "Compare the two treatment
  arms with an ANCOVA, adjusting for baseline" is an AC.

Two more terms come up. **USDM** is CDISC's standard file describing a study — its objectives,
endpoints, arms, populations — so that software can read it. **ICH M11** is the harmonised
template for how a clinical protocol should be structured; in this project it is the source the
USDM file was generated from. The field calls the pair *USDM11*.

## The tool

CDISC ships a small web app, `ac-dc-app`, inside its
[`analysis-concepts`](https://github.com/cdisc-org/analysis-concepts) repository. This project
keeps a pinned, read-only copy of that repository under `upstream/` and never edits it. The app
is one web page with an eight-step sidebar. You start at the top and work down; the sidebar
ticks each step as you complete it.

| Step | What you do | Which layer |
|---|---|---|
| 1 Select Study | Pick a study — the app reads its USDM file | USDM |
| 2 Study Overview | See its objectives, endpoints and arms | USDM |
| 3 Endpoint | Pick one endpoint and say what is measured, for whom, and when | **BC** attaches here |
| 4 Analysis | Choose the analysis from a menu | **AC** |
| 5 Summary | One card per endpoint, reviewing the choices | — |
| 6 Derivations | Say how the number is made — value minus baseline | **DC** |
| 7 eSAP Builder | The app writes out a statistical analysis plan from steps 1–6 | the plan |
| 8 Execute | Upload the data and run it, in R inside the browser | the result |

Steps 1–7 are *specification*: describing an analysis without any data. Step 8 is *execution*:
the only step that touches data. It asks for the analysis datasets as `.xpt` files (a standard
format for clinical data), loads them into R running in the browser, applies the derivation from
step 6 and the analysis from step 4, and returns numbers.

## What this project did with it

The rule was one protocol and one endpoint, every step, ending in a number that could be
checked. The study is [TORIVA-LUNG 301](https://github.com/OpenTrialReporting/torivumab-nsclc-301),
a simulated Phase 3 lung-cancer trial chosen because its protocol, statistical analysis plan and
built analysis datasets all exist and are public.

**Before the app — the M11 half.** TORIVA's protocol was mapped onto the ICH M11 template
([`study/m11/protocol-to-m11.md`](../study/m11/protocol-to-m11.md)) and three sections were
restructured to it ([`study/m11/protocol/`](../study/m11/protocol/)). The point of doing this
first is that M11 puts the *estimand* — the precise question the trial answers — into the
protocol, and TORIVA had left it in the statistical plan. From the restructured protocol a USDM
file was written ([`study/usdm/`](../study/usdm/)), and that is the file step 1 reads.

**Steps 1–4.** The app loaded TORIVA and showed its six objectives and six endpoints. The
laboratory endpoint was chosen; the seven lab tests it covers were linked as BCs; the analysis
"change from baseline, ANCOVA" was selected from the menu. The saved chain is
[`endpoints/01-simple-lab-cfb/chain.json`](../endpoints/01-simple-lab-cfb/chain.json).

**Step 6.** The derivation "value minus baseline" was chosen for it — automatically, because it
was the only candidate.

**Step 7.** The app generated the plan: [`esap.json`](../endpoints/01-simple-lab-cfb/esap.json).
One thing learned here: the plan's estimand is assembled from two places. The study file supplies
half of it; the chain has to supply the other half — the analysis population and the treatment —
even when the study file already holds the answer.

**Step 8.** TORIVA's lab dataset (136,242 rows) was converted to `.xpt` and uploaded, and the
chain was run. It took eleven further decisions to make the chain describe the data — which
column is the treatment, which flag is the safety population, which of two forms of "visit" to
use — none of them statistical. Then it produced a number:

> Change from baseline in ALT at Cycle 2 Day 1, safety population, torivumab minus placebo:
> **−1.83 (standard error 1.77, n = 432).**

The runs and their logs are in [`results.json`](../endpoints/01-simple-lab-cfb/results.json).

**The check.** The same analysis was fitted directly to TORIVA's own datasets, which already
carry a change-from-baseline column computed by the trial's programmers. That gives −0.89. The
two do not agree, and [`comparison.md`](../endpoints/01-simple-lab-cfb/comparison.md) accounts
for the whole difference: the app's number is reproduced to four decimal places once you know
exactly which rows it selected. Part of the gap was authoring choices that could be corrected in
the app. The rest is one rule: for 70% of subjects there are *two* readings in the baseline
window, the trial's programmers pick one by a flag, and the app picks whichever comes first.

Neither number is statistically significant here, so the conclusion does not change. What the
exercise shows is where each kind of decision lives — in the protocol, in the study file, in the
chain, or only in the data — and that a chain can look complete at step 7 and still need a
dozen decisions at step 8.

## Where things are

| | |
|---|---|
| The destination and the nine stages | [`NORTH.md`](../NORTH.md) |
| The protocol mapped and restructured to M11 | [`study/m11/`](../study/m11/) |
| The USDM file, and what was learned writing it | [`study/usdm/README.md`](../study/usdm/README.md) |
| The chain, plan, result and comparison | [`endpoints/01-simple-lab-cfb/`](../endpoints/01-simple-lab-cfb/) |
| Every decision the authoring needed | [`log.md`](../endpoints/01-simple-lab-cfb/log.md) |
| Notes on where the framework's limits were met | [`docs/findings/`](findings/README.md) |
