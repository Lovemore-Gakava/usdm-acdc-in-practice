# F09 — Record selection carries no tie-break, and no transformation binds its ordering

**Status: new, and already corrected once.** Found while mapping the lab tier, verified at
upstream `739344c`. **The original framing of the second half was wrong** — it called the
unbound roles a conformance defect, which misreads how the library and the builder divide the
work. Corrected 2026-09-16, the same day it was written. The capability claim is unchanged and
the practical consequence is worse than first stated; see *What the unbound roles actually
mean*.

## Claim

`M.RecordSelection` orders records by a single required `time_order` role and offers no
tie-break. No transformation in the library binds that role at all, although the schema marks
it required and the method's formula depends on it.

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

### No transformation binds `time_order`, and nothing in the repository mentions it

The string `time_order` occurs in exactly two files at `739344c`:

```
lib/methods/derivations/M.ImputedValue_LOCF.json   5
lib/methods/derivations/M.RecordSelection.json     3
```

Nowhere else. Not in the transformation library, not in `ac-dc-app/js/**`, not in any study
instance or scenario.

Counting required input roles against the bindings that supply them, across all 25
transformations:

```
T.BaselineSelection    uses M.RecordSelection      UNBOUND required role(s): ['time_order']
T.LOCF_Imputation      uses M.ImputedValue_LOCF    UNBOUND required role(s): ['time_order']
T.PeakConcentration    uses M.Maximum              UNBOUND required role(s): ['response']
```

`T.BaselineSelection` binds `value`, and `partition` three times (Subject, ParameterDimension,
VisitDimension). It does not bind `time_order`. Neither does any other entry in the library:
no transformation binds that role anywhere, though two methods require it.

The consequence for the lab tier is concrete. `T.BaselineSelection` is configured
`selection_rule: last_non_missing`, `scope: pre_treatment`, `reference_event: first_dose` —
which matches SAP §12.3 field for field — and **last by what** is supplied by neither the
configuration nor a binding. `last_non_missing` over an unbound ordering is not a definition.

## What the unbound roles actually mean

The first version of this finding called the three unbound roles a **conformance defect**, and
inferred that nothing validates transformations against the methods they use. Both were wrong,
and the error is worth recording because it is the same error F05 made — reading the JSON and
not the application.

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

### The consequence is worse than the withdrawn claim

Having looked at how the author would actually fill the slot, it appears they cannot.

- **In the analysis-transformation editor**, the "+ Add Binding" control is gated on
  `canAdd = role.cardinality === 'multiple' || role.cardinality === 'single_or_multiple'`
  (`transformation-config.js:540`). `time_order` is `cardinality: "single"`, so `canAdd` is
  false. With no template binding to render and no add control, the role emits a header —
  `time_order (single, required)` — and nothing beneath it.
- **In the derivation-pipeline editor**, which is the view `T.BaselineSelection` belongs to,
  `renderBindingsSections` (`derivation-pipeline.js:796`) iterates the transformation's
  `bindings` array rather than the method's roles. A role with no binding does not render at
  all. The author is never shown that an ordering is required.

If that reading is right, `last_non_missing` is authored against an ordering that is neither
declared in the library, supplied by configuration, nor reachable through the UI — and the only
signal is a note in generated Define-XML, after the fact.

### This is a code read, not a run

**It has not been confirmed in the running application.** F05 is the precedent: that finding was
overstated for exactly this reason and only corrected by serving `ac-dc-app` and looking. The
same must be done here before any of this is filed — serve the app, open a derivation chain on
`T.BaselineSelection`, and see what the binding panel offers.

Until then, treat the UI paragraphs above as an argued reading of the source, and the
`time_order`/tie-break capability gap below as the verified part.

## Scope

The verified capability gap is one thing and needs a schema change: no composite sort key
(`cardinality: "single"`) and no tie-break configuration, so a deterministic selection rule
cannot be stated. `cardinality: "multiple"` on `time_order`, or a tie-break configuration, or
both.

Whether the authoring path can supply an ordering at all is a second question, open pending the
check above.

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
