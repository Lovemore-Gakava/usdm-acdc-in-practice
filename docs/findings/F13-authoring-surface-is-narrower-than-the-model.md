# F13 — The authoring surface is far narrower than the model

**Status: new.** Found by attempting to author ORR on 2026-09-16. Verified at upstream
`739344c`, in the libraries and in the running application.

## Claim

A chain is authored from **transformation templates**, not from methods. Sixty-five percent of
methods have no template, a shipped template's method configuration cannot be edited, and no
template can be created. So a method existing does not mean a chain using it can be built —
and every previous finding here that concluded "the method exists, so this composes" was
measuring the wrong surface.

## Evidence

### 1. Two thirds of the method library is unreachable

| | |
|---|---|
| Methods | 60 |
| Transformations | 25 |
| Distinct methods wrapped by at least one transformation | **21** |
| **Methods with no transformation at all** | **39 (65%)** |

By method type: 28 of 39 analysis methods (72%) and 11 of 21 derivation methods (52%) have no
transformation.

The unwrapped derivation methods are:

```
M.Categorization   M.DateDifference   M.Imputation        M.ImputedValue_BOCF
M.ImputedValue_Mean  M.ImputedValue_Median  M.ImputedValue_WOCF  M.ImputedValue_Zero
M.PercentChange    M.Rounding         M.WindowLookup
```

### 2. What wrapping exists is mostly one endpoint's scaffolding

Of the 25 transformations, **8 are ADAS-Cog-specific** — 32% of the library, and **57% of the
14 derivation transformations**:

```
T.ADAS_ItemMaxScore  T.ADAS_MissingContribution  T.ADAS_MissingScaleCapacity
T.ADAS_ScoreableFraction  T.ADAS_SumAvailableScores  T.ADAS_NonMissingCount
T.ADAS_ScoreableCheck  T.ADAS_Cog_11_TotalScore
```

The generic derivation library — everything reusable across studies — is **six entries**:

```
T.BaselineSelection  T.ChangeFromBaseline  T.LOCF_Imputation
T.PeakConcentration  T.UnitConversion      T.DeriveAnalysisVisit
```

`M.Aggregation` is wrapped four times and `M.Maximum` twice; every other wrapped method is
wrapped once. So the shape of the library is one worked example plus six general entries.

### 3. A shipped template's configuration cannot be edited

This is what makes the gap binding rather than merely inconvenient. `T.BaselineSelection`
configures `M.RecordSelection` with `selection_rule: last_non_missing`, `scope: pre_treatment`.
The same method offers `best` and `post_baseline`, which is exactly ORR's step 2. An author
cannot get there:

- **Derivation pipeline (step 6).** The selected-derivation panel renders Name, OID, Method,
  Output, Description and Bindings. Verified live: the strings `selection_rule`,
  `last_non_missing`, `pre_treatment` and `post_baseline` appear **nowhere** in the rendered
  page with `T.BaselineSelection` selected.
- **Analysis (step 4).** This view *does* render method configurations —
  `endpoint-how.js:124`, `getMethodConfigurations(method, transform, userConfigOverrides)` —
  but it is inside `analyses.map(...)`, where `transform = getTransformationByOid(analysis.transformationOid)`
  and `method = activeMethodMap[analysis.transformationOid]`. **Only analysis transformations
  are passed.** Verified live: with `T.Responder_ChiSq` selected, the single configuration
  offered is the chi-squared continuity correction (`none` / `yates`).

A derivation's method configuration is therefore not editable anywhere in the builder.

### 4. No template can be created

`ac-dc-app/js/data-loader.js:56` fetches `ACDC_Transformation_Library_v06.json` and nothing
writes to it. There is no create, add, or new-transformation affordance anywhere under
`ac-dc-app/js/`; `instance-serializer.js` only records the library file as a `$reference`. An
author selects from the 25 shipped entries or does not proceed.

## What this does to the three tiers

The ladder was scored on paper against the **method** library. Re-scored against the
**authoring** surface:

| Tier | Composes on paper | Authorable | Why the difference |
|---|---|---|---|
| Simple — lab CFB | yes | **yes** | `T.BaselineSelection`, `T.ChangeFromBaseline` and `T.DeriveAnalysisVisit` are three of the six generic entries. `M.PercentChange` (step 7) is not wrapped, so `PCHG` drops out |
| Moderate — ORR | 6 of 11 steps | **none of the 5 recommended** | `M.Categorization`, `M.Proportion`, `M.CMH` unwrapped; `M.RecordSelection` and `M.ThresholdCompare` wrapped once each, fixed elsewhere |
| Complex — PFS | 1 of 9 steps | **none** | The one composing step was `AVAL = ADT − STARTDT` via `M.DateDifference` — **which has no transformation** |

**PFS goes from one of nine to zero of nine.** The single step the complex tier had was
unauthorable, and neither the mapping nor F01 noticed, because both were reading the method
library.

The lab tier is authorable only because it happens to need three of the six generic entries —
which is also why the specification predicted it would work.

## Why this matters more than a missing library entry

Every finding here that reasoned *"the method exists, so this composes"* was measuring the
method library. That is the right surface for asking **can the model express this**, and the
wrong one for asking **can a chain be built**. The two answers differ on two of three tiers.

It also changes what the gaps cost. A missing method is a model limitation and needs a design
change ([F06](F06-no-general-predicate.md), [F08](F08-no-risk-difference.md)). A missing
*transformation* over an existing method is ordinary content work — the kind this project
offered to contribute in `upstream-issues.md` Issue 3. But content work an author cannot do
themselves, in a builder that cannot create or reconfigure a template, is not a small gap from
the author's side. It is a hard stop.

And the ratio is the point. Six generic derivation entries against 21 derivation methods is not
a library with holes in it; it is a worked example with a few reusable pieces extracted. That is
entirely reasonable for a reference implementation — **and it is not what the ladder was
scored against.**

## Scope

Not a defect in any one entry. Three separable asks, smallest first:

1. **Expose method configurations for derivations**, as step 4 already does for analyses. This
   alone would make ORR's step 2 authorable from `T.BaselineSelection`, though at the cost of
   an entry whose oid and description say baseline while it computes best overall response —
   which argues for 2.
2. **Allow a transformation to be authored**, or at least cloned-and-reconfigured, so the
   authored instance carries its own identity rather than overloading a shipped one.
3. **Fill the obvious library gaps** — `M.Categorization`, `M.Proportion`, `M.CMH`,
   `M.DateDifference`, `M.PercentChange` are all methods a routine study needs and none has an
   entry.

The third is contributable by outsiders; the first two are not.

## Relation to other findings

[F11](F11-analysis-record-flag-has-no-transformation.md) is the single-entry version of this —
`ANL01FL` named in a method's output description and produced by nothing.
[F08](F08-no-risk-difference.md) noted in passing that neither `M.CMH` nor `M.Proportion` has a
transformation. F13 is what those two are instances of, with the count.

It also bears on [F01](F01-no-tte-derivation-transformations.md): the TTE gap is usually stated
as "no `T.` entry produces `AVAL`/`CNSR`", which is true and is a specific case of a general
pattern — 65% of methods have no `T.` entry.

## Reproduce

```
python -c "
import json,glob
from collections import Counter
m={}
for f in glob.glob('upstream/analysis-concepts/lib/methods/**/*.json',recursive=True):
    d=json.load(open(f,encoding='utf-8'))
    for x in (d if isinstance(d,list) else [d]):
        if isinstance(x,dict) and x.get('oid'): m[x['oid']]=x
lib=json.load(open('upstream/analysis-concepts/lib/transformations/ACDC_Transformation_Library_v06.json',encoding='utf-8'))
ts=lib['derivationTransformations']+lib['analysisTransformations']
w=Counter(t.get('usesMethod') for t in ts)
un=[o for o in m if o not in w]
print('methods',len(m),'transformations',len(ts),'wrapped',len(w),'unwrapped',len(un))
print('unwrapped derivations:',sorted(o for o in un if m[o].get('type')=='derivation'))
print('ADAS share:',sum(1 for t in ts if t['oid'].startswith('T.ADAS')),'of',len(ts))
"
```

Expected at `739344c`: 60 methods, 25 transformations, 21 wrapped, 39 unwrapped; eleven
unwrapped derivation methods including `M.DateDifference` and `M.Categorization`; 8 of 25
ADAS-specific.

The application claims in §3 and §4 were checked by serving `ac-dc-app` and driving it, not by
reading alone — see `endpoints/02-moderate-orr/log.md`.
