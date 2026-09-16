# F11 — The model names `ANL01FL` and nothing produces it

**Status: new.** Found while mapping the lab tier. Verified at upstream `739344c`.

## Claim

`M.RecordSelection`'s output description names `ANL01FL` as a thing it is for. No
transformation produces one. Five of its six selection rules are used by nothing, and the rule
TORIVA actually needs reaches across derivations in a way no method can express.

## Evidence

### The model names the artefact

`M.RecordSelection`'s single output class:

```json
{ "class": "computed_value", "role_name": "flag", "dataType": "code",
  "description": "Indicator marking selected record(s) ('Y' on selected, blank otherwise).
                  In ADaM context: ABLFL for baseline, ANL01FL for analysis records, etc.",
  "statistics": ["value"], "dimensions": ["partition"] }
```

Both flags are named. Only one is built: the sole transformation using `M.RecordSelection` in
the entire library is `T.BaselineSelection`.

### Five of six selection rules have no worked example

`selection_rule` offers `last_non_missing`, `first_non_missing`, `worst`, `best`,
`closest_to_target`, `all_matching`. `T.BaselineSelection` configures `last_non_missing`.
Since it is the only consumer, **the other five are exercised by nothing in the library.**

That sharpens [F07](F07-ordering-is-unstated.md), which observed there is no worked example
pinning what `best` means. The gap is wider than `best`: `closest_to_target` — the rule an
analysis-record flag needs — has no example either, and `target_value` is a lone `decimal`
configuration with no indication of how it interacts with `time_order` or with window targets.

### The rule TORIVA needs is conditioned on another derivation

SAP §12.2 defines one `ANL01FL` rule for every windowed BDS dataset, implemented once as
`flag_anl01()`:

> exactly one record per `USUBJID × PARAMCD × AVISIT` is flagged `ANL01FL = 'Y'`. Where more
> than one assessment windows into the same visit … the record **closest to the visit target
> day** wins (ties → the later `ADT`); **inside the `Baseline` visit the `ABLFL = 'Y'` record
> wins**, so the baseline analysis value agrees with `BASE`.

Three separate problems, in one sentence of SAP:

1. **`closest_to_target` needs the window's target day.** That value lives in
   `M.WindowedVisitAssignment`'s `windows` array, inside a different method's configuration.
   `M.RecordSelection.target_value` is a single `decimal` — one constant for the whole
   selection, where what is needed is per-visit, and already stated elsewhere. Nothing connects
   the two. See [F10](F10-visit-windows-are-enumerated-not-generated.md).
2. **The tie-break is unstatable.** [F09](F09-record-selection-has-no-tiebreak.md).
3. **The `Baseline` exception is a predicate over two variables** — *if `AVISIT` is Baseline,
   select where `ABLFL = 'Y'`; otherwise select closest to target.* `selection_rule` is one
   enum value for the whole transformation. There is no conditional form, and
   [F06](F06-no-general-predicate.md) establishes that no method carries a predicate relating
   two variables. The condition additionally references the **output of another derivation**
   (`ABLFL`, produced by `T.BaselineSelection`), so even a conditional selection rule would
   need to name a sibling derivation's result.

Point 3 is the substantive one. Chain position already carries meaning the entries do not
([F03](F03-chain-position-carries-meaning.md)); here a chain would need to carry a
*dependency* — one derivation's selection rule conditioned on another's output — and the
transformation model has bindings for inputs and outputs but no way to say "this rule defers to
that flag".

## Why it matters more than a missing library entry

`ANL01FL` is not a niche flag. SAP §12.2 applies the same rule to ADLB, ADVS, ADRS and ADTR —
four of TORIVA's datasets — and "one analysis record per subject per parameter per visit" is
the precondition for every by-visit summary, every shift table and every MMRM in the study.
`T.CFB_MMRM_Primary` and `T.CFB_ANCOVA` both exist upstream and both silently assume it has
already happened.

So this sits in the same position as `T.OS_LogRank` in [F01](F01-no-tte-derivation-transformations.md):
the analysis transformation exists and consumes a derived input that nothing upstream derives.
The difference is that the TTE gap is acknowledged as a gap, whereas `ANL01FL` is named in the
model's own output description as though it were covered.

## Scope

The simple part is a missing `T.` entry — `T.AnalysisRecordSelection` configured
`selection_rule: closest_to_target`, which is ordinary library work and would give the five
unused rules their first worked example.

That entry would still not express TORIVA's rule, because of points 1–3. An honest upstream
issue reports the missing entry *and* asks how the baseline exception is meant to be modelled,
rather than proposing an entry that only covers the easy half.

## Reproduce

```
python -c "
import json
lib=json.load(open('upstream/analysis-concepts/lib/transformations/ACDC_Transformation_Library_v06.json',encoding='utf-8'))
ts=lib['derivationTransformations']+lib['analysisTransformations']
users=[t['oid'] for t in ts if t.get('usesMethod')=='M.RecordSelection']
print('transformations using M.RecordSelection:', users)
for t in ts:
    if t['oid'] in users:
        print(t['oid'], [c for c in t['methodConfigurations'] if c['configurationName']=='selection_rule'])
"
```

Expected at `739344c`: `['T.BaselineSelection']` and `selection_rule: last_non_missing`.
