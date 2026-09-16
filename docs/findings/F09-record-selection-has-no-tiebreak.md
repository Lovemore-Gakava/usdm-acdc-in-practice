# F09 — Record selection carries no tie-break, and no transformation binds its ordering

**Status: new.** Found while mapping the lab tier. Verified at upstream `739344c`.

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

### No transformation binds `time_order`

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

## Scope: this is two findings wearing one coat

They are worth separating before anything is filed.

1. **A missing capability.** No composite sort key and no tie-break, so a deterministic
   selection rule cannot be stated. This needs a schema change — `cardinality: "multiple"` on
   `time_order`, or a tie-break configuration, or both.
2. **A conformance defect.** Three transformations omit a role their method marks
   `required: true`. That needs no schema change, only correction — and it suggests nothing
   validates transformations against the methods they use, which is itself worth reporting.

The second is the cheaper and more certain of the two.

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

Expected at `739344c`: the three lines quoted above.
