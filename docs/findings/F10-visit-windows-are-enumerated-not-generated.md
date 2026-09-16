# F10 — Visit windows must be enumerated, and nothing may escape windowing

**Status: new.** Found while mapping the lab tier. Verified at upstream `739344c`.

## Claim

`M.WindowedVisitAssignment` takes an explicit array of windows. It cannot express a window
*rule*, cannot express an open-ended schedule, and offers no way for a record to keep its
collected visit instead of being windowed. Its `windows` array has no declared item schema and
its `tieBreak` has no declared value set.

## Evidence

The method's whole configurable surface is three entries:

```json
"configurations": [
  { "name": "referenceBC", "dataType": "code" },
  { "name": "windows",     "dataType": "object[]",
    "description": "Scheduled visit windows: array of { label, visitNumber, dayMin, dayMax, targetDay }. dayMin/dayMax=null means unbounded." },
  { "name": "tieBreak",    "dataType": "code", "defaultValue": "closest-to-target-then-earliest",
    "description": "Tie-break rule when multiple windows match the day." }
]
```

with the formula

```
analysisVisit := FIND WINDOW(<windows>) MATCHING <day>
default:        analysisVisit := window.label WHERE day ∈ [window.dayMin, window.dayMax],
                tie-break closest(|day-targetDay|) then min(visitNumber)
```

and a single required input role, `day` (`decimal`, `single`).

### 1. The window rule cannot be stated, only its expansion

SAP §12.2 defines TORIVA's windows as a **nearest-target partition**: every analysis visit has
a protocol target day, and *"the boundary between two consecutive visits is the midpoint
between their targets, giving a complete, gap-free, non-overlapping window per visit."* The
windows are generated — `crf/analysis_visit_windows.csv` is produced by
`programs/adam/_build_visit_windows.R`.

`dayMin`/`dayMax` can of course be precomputed and pasted in, so the *result* is expressible.
What is not expressible is the rule, and the rule is what stays correct when a target day
moves. A study that shifts C3D1 by three days must recompute two boundaries and re-author both
neighbouring windows; nothing in the metadata records that they were derived, or from what.

### 2. Open-ended schedules cannot be enumerated

TORIVA's maintenance visits are `MAINT_CmD1` at target day `1 + (5 + m)·21`, for unbounded `m`
(SAP §12.2). An array has to stop somewhere, so the authored window list is truncated at
whatever `m` the current data reaches — which makes the metadata a function of the data it is
supposed to describe. Re-running on a later cut with a longer-surviving subject silently drops
records into no window.

### 3. Nothing may escape windowing

SAP §12.2 is explicit: *"Event-driven visits (`EOT`, `FU1`, `FU2`) are **not** day-windowed —
they are determined by protocol role and keep their collected label and SDTM `VISITNUM`."*

The formula windows every record by `day`. There is no predicate, no scope configuration and
no exemption role. The only inputs are `day` (required) and `partition` (optional, and
documented as *"Not used by the default template"*). A record whose analysis visit is
determined by protocol role rather than by study day cannot be represented.

This is not exotic. End-of-treatment and follow-up visits appear on essentially every oncology
trial, and they are exactly the visits whose timing is unpredictable — which is why they are
not windowed.

### 4. `windows` has no item schema, and `tieBreak` no value set

`windows` is `dataType: "object[]"`. The shape `{ label, visitNumber, dayMin, dayMax,
targetDay }` appears **only in the free-text `description`**. There is no `itemSchema`, no
`$ref`, nothing machine-readable. A window array is therefore unvalidatable, unparseable, and
outside the reach of any signature — the same defect [F06](F06-no-general-predicate.md) records
incidentally for `M.Categorization.conditions`, which is typed `string` with an example rather
than a grammar. Two of the most configuration-heavy methods in the library carry their real
contract in prose.

`tieBreak` is `dataType: "code"` with a default and **no `enumValues` and no codelist
reference**. TORIVA needs ties broken to the *later* `ADT` (SAP §12.2: *"the record closest to
the visit target day wins (ties → the later `ADT`)"*); the shipped default is
`closest-to-target-then-earliest`. Whether `closest-to-target-then-latest` is an accepted value
is not stated anywhere. Compare `M.CoxPH.ties` and `M.Rounding.method`, both of which declare
closed enums for exactly this kind of choice — see [F09](F09-record-selection-has-no-tiebreak.md).

## What this is not

It is not a claim that the ADAS-Cog case is wrongly modelled. The shipped default windows
(`≤1` Baseline, `2–84` Week 8, `85–140` Week 16, `>140` Week 24) are a fixed four-visit
schedule that an enumerated array fits perfectly, and for that study the design is right.

The finding is about what happens at the next study along: a Q3W schedule with an open-ended
maintenance phase and three event-driven visits is ordinary, and three of its four
characteristics are outside the model.

## Scope

Ranked by cost to fix:

| | Issue | Fix |
|---|---|---|
| Smallest | `tieBreak` has no declared values | Add an enum, as `M.CoxPH.ties` has |
| Small | `windows` has no item schema | Add one; the shape is already written in the description |
| Medium | No escape from day-windowing | A scope or exemption configuration, or a `collected_visit` passthrough |
| Largest | Windows enumerated, not generated | A target-day list plus a partition rule — which would also solve the open-ended case |

The last of these is the one that matters, and it is also the one that would shrink the
authored artefact most: TORIVA's TREATMENT stream is a dozen-plus windows today, all derivable
from a target list and one sentence of rule.

## Reproduce

```
python -c "
import json,glob
for f in glob.glob('upstream/analysis-concepts/lib/methods/**/*.json', recursive=True):
    d=json.load(open(f,encoding='utf-8'))
    for m in (d if isinstance(d,list) else [d]):
        if isinstance(m,dict) and m.get('oid')=='M.WindowedVisitAssignment':
            print(json.dumps(m['configurations'],indent=1)); print(m['input_roles'])
"
```
