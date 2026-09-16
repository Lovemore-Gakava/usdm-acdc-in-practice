# F09 — Record selection carries no tie-break, and no transformation binds its ordering

**Status: new, and corrected twice on the day it was written.** Found while mapping the lab
tier, verified at upstream `739344c`. Two successive framings of its second half were wrong,
both corrected on 2026-09-16 — the second only after the application was actually served and
driven. **The core capability claim has survived both corrections unchanged.** Read
*Corrections* before citing anything here.

## Claim

**`M.RecordSelection` orders records by a single required `time_order` role and offers no
tie-break**, so an ordering that needs a composite key cannot be stated. `T.BaselineSelection`
supplies no ordering at all.

Two subsidiary claims made earlier were wrong and are withdrawn below.

## Evidence

### The ordering role is single, required, and numeric

```json
"input_roles": [
  { "name": "value",      "dataType": "decimal", "required": true, "cardinality": "single" },
  { "name": "partition",  "dataType": "code",    "required": true, "cardinality": "multiple" },
  { "name": "time_order", "dataType": "decimal", "required": true, "cardinality": "single",
    "description": "Variable defining temporal ordering within partition (e.g. visit number, analysis date)" }
]
```

`cardinality: "single"`. A composite sort key cannot be expressed. TORIVA's baseline is
`order = exprs(ADT, LBSEQ), mode = "last"` (`programs/adam/adlb.R`, SAP §12.3: ties *"broken by
the SDTM sequence number"*) — two keys, and the second exists precisely because the first is not
unique. Two lab draws on the same date are a routine occurrence, not an edge case.

### There is no tie-break configuration

`M.RecordSelection`'s five configurations are `selection_rule`, `scope`, `cardinality`,
`reference_event`, `target_value`. None concerns ties.

This is not a library-wide omission. Tie-handling is declared, with a closed enum, wherever
else it arises:

| Method | Configuration | Declared values |
|---|---|---|
| `M.CoxPH` | `ties` | `efron`, `breslow`, `exact` |
| `M.Rounding` | `method` | `half_up`, `half_even`, `half_down`, `floor`, `ceiling` |
| `M.WindowedVisitAssignment` | `tieBreak` | **none declared** — see [F10](F10-visit-windows-are-enumerated-not-generated.md) |
| `M.RecordSelection` | — | **no such configuration** |

So the library knows how to declare a tie rule and does so twice. The two places where
*record and visit selection* need one are the two places it is missing or undeclared.

### No transformation binds `time_order` by that name

The string `time_order` occurs in exactly two files at `739344c`:

```
lib/methods/derivations/M.ImputedValue_LOCF.json   5
lib/methods/derivations/M.RecordSelection.json     3
```

Nowhere else. Not in the transformation library, not in `ac-dc-app/js/**`, not in any study
instance or scenario.

**Read this carefully — it is not the same as "no ordering is supplied".** `T.LOCF_Imputation`
binds an ordering to the visit dimension under the role name `order`; see *Corrections (b)*.
That is a role-name mismatch, and a different, smaller finding. `T.BaselineSelection` supplies
no ordering under any name, which is the case that matters here.

Counting required input roles against the bindings that supply them, across all 25
transformations:

```
T.BaselineSelection    uses M.RecordSelection      UNBOUND required role(s): ['time_order']
T.LOCF_Imputation      uses M.ImputedValue_LOCF    UNBOUND required role(s): ['time_order']
T.PeakConcentration    uses M.Maximum              UNBOUND required role(s): ['response']
```

`T.BaselineSelection` binds `value`, `flag` (output) and `partition` three times (Subject,
ParameterDimension, VisitDimension) — and no ordering role of any name.

The consequence for the lab tier is concrete. `T.BaselineSelection` is configured
`selection_rule: last_non_missing`, `scope: pre_treatment`, `reference_event: first_dose` —
which matches SAP §12.3 field for field — and **last by what** is supplied by neither the
configuration nor a binding. `last_non_missing` over an unbound ordering is not a definition.

## Corrections

### Second correction — after running the application

`ac-dc-app` was served and driven on 2026-09-16: CDISC Pilot study, endpoint END5
*"Laboratory evaluations (Change from Baseline)"*, concept category `Change (Comparison)`,
analysis template *Change From Baseline ANCOVA*, then the derivation pipeline. Three things
were observed that the source read had got wrong or missed.

**(a) The derivation pipeline's binding panel does have an add control.** Selecting the
`T.LOCF_Imputation` node shows a `BINDINGS` panel listing `value`, `partition` ×2, `order` and
the `result` output, with a **`+ Add binding...`** dropdown beneath. The earlier claim that a
role is unbindable because no add control exists is **withdrawn for this view**. (It remains
accurate for `transformation-config.js`'s `renderInteractiveBindings`, where `canAdd` is gated
on cardinality — verified by calling that function directly against the real library.)

**(b) The ordering is bound in `T.LOCF_Imputation` — under a name its method does not declare.**

| | |
|---|---|
| `M.ImputedValue_LOCF` required roles | `value`, `partition`, **`time_order`** |
| `T.LOCF_Imputation` input bindings | `value:Measure`, `partition:Subject`, `partition:ParameterDimension`, **`order:VisitDimension`** |

So the ordering *is* supplied — bound to the visit dimension — but as `order`, which the method
does not declare. The claim "no transformation binds `time_order`" is literally true and
materially misleading: the real defect there is a **role-name mismatch between a transformation
and its method**, not a missing ordering. That is a smaller and more precise finding, and it is
what should be reported.

`T.BaselineSelection` is different and the original reading holds: it binds
`value`, `flag`, and `partition` three times, and supplies **no ordering under any name**.

**(c) The add control offers concepts, not roles.** The `+ Add binding...` dropdown lists
`Measure`, `Change`, `Flag`, `Subject`, `Timing`, `Parameter`, `AnalysisVisit`, `Treatment`
and so on — the concept vocabulary. An author picks *what* to bind, not *which method role* it
fills. So an author cannot deliberately supply a named role the transformation omits, which is
the point the withdrawn claim was reaching for, arrived at properly.

### First correction — the conformance-defect framing

The first version called the unbound roles a **conformance defect** and inferred that nothing
validates transformations against the methods they use. Both were wrong, and the error is worth
recording because it is the same error F05 made — reading the JSON and not the application.

**Library entries are templates, not complete instances.** `js/views/transformation-config.js`
builds its binding editor by iterating `method.input_roles` (line 482) and grouping the
transformation's bindings under them, so a role the library entry does not bind is *expected* to
be completed by the author. `T.BaselineSelection` omitting `time_order` is an unfilled slot by
design, not a malformed entry.

**And there is a validator, just a late and advisory one.** `js/utils/define-xml-generator.js`
(line 705) tests the resolved call template for leftover placeholders and emits a note:

```js
if (/<[a-z_]+>/i.test(text)) {
  note('arm', `${arOID} ProgrammingCode`, 'some role/config placeholders unresolved (missing binding or config default)');
}
```

So the original second claim is withdrawn.

### What the two views do

Confirmed by direct call against the real library, and by running the app:

- **`transformation-config.js`** builds its panel from `method.input_roles`, so an unbound role
  renders as a header. For `T.BaselineSelection` + `M.RecordSelection` the emitted markup for
  the ordering role is, in full:

  ```html
  <div class="binding-role-header">
    <span class="binding-role-name">time_order</span>
    <span class="binding-role-cardinality">(single, required)</span>
  </div>
  ```

  Zero binding rows, and no add control, because `canAdd` requires `multiple` or
  `single_or_multiple` (line 540).

- **`derivation-pipeline.js`** builds its panel from the transformation's `bindings`
  (`renderBindingsSections`, line 796), so a role with no binding does not appear — but the
  panel carries its own `+ Add binding...` control, which is concept-driven rather than
  role-driven.

Neither view lets an author say "this role is the ordering".

## Scope

Three separable things, only the first of which is a capability gap:

1. **No composite sort key and no tie-break** (`cardinality: "single"`, no tie configuration),
   so a deterministic ordering cannot be stated. TORIVA's `(ADT, LBSEQ)` is unexpressible.
   Needs a schema change: `cardinality: "multiple"` on `time_order`, or a tie-break
   configuration, or both. **This is the finding.**
2. **`T.LOCF_Imputation` binds `order` where its method declares `time_order`** — a role-name
   mismatch between a transformation and the method it uses. A one-word fix, and a reason to
   ask whether anything checks role names across that join.
3. **`T.BaselineSelection` supplies no ordering at all**, so `last_non_missing` is configured
   against an unstated order. Library content, not a model gap.

## Relation to other findings

Same species as [F07](F07-ordering-is-unstated.md): the structure is present and the
information that makes it deterministic is not. F07 concerns *which direction* an ordering
runs; F09 concerns *what the ordering is at all*, and whether ties within it are resolved.
Both sit on `M.RecordSelection`, and a single issue could reasonably carry them.

For Part B, it is the same signature problem in a third place. Two chains selecting different
records — one ordering by date, one by date then sequence — are identical in metadata, because
neither states its ordering.

## Reproduce

```
python - <<'EOF'
import json, glob
methods = {}
for f in glob.glob("upstream/analysis-concepts/lib/methods/**/*.json", recursive=True):
    d = json.load(open(f, encoding="utf-8"))
    for m in (d if isinstance(d, list) else [d]):
        if isinstance(m, dict) and m.get("oid"): methods[m["oid"]] = m
lib = json.load(open("upstream/analysis-concepts/lib/transformations/"
                     "ACDC_Transformation_Library_v06.json", encoding="utf-8"))
for t in lib["derivationTransformations"] + lib["analysisTransformations"]:
    meth = methods.get(t.get("usesMethod"))
    if not meth: continue
    req = {r["name"] for r in meth.get("input_roles", []) if r.get("required")}
    bound = {b.get("methodRole") for b in t["bindings"] if b.get("direction") == "input"}
    if req - bound:
        print(t["oid"], "->", t["usesMethod"], "unbound:", sorted(req - bound))
EOF
```

Expected at `739344c`: the three lines quoted above. And for the absence:

```
grep -rc "time_order" --include=*.json --include=*.js upstream/analysis-concepts/ | grep -v ":0"
```

Expected: only `M.ImputedValue_LOCF.json` and `M.RecordSelection.json`.
