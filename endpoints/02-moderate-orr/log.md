# ORR — authoring log

Step 4 of the method, reporting on an attempt at step 2.

**Authored 2026-09-16** against `ac-dc-app` at upstream `739344c`. Result:
[`chain.json`](chain.json) — which contains **no derivation at all**.

---

## Headline

The mapping recommended authoring ORR's five composable steps — 2, 3, 7, 8, 9. **None of them
can be authored.** Not because the methods cannot express them, which was the paper finding,
but because the builder authors from *transformation templates* and no template exists for any
of the five.

This is a different failure from PFS, and the mapping did not anticipate it. PFS does not
compose because the **methods** cannot express the censoring hierarchy (F06). ORR's five steps
compose at method level exactly as the mapping said — and are still unauthorable, because the
**transformation library** has no entry wrapping those methods and the application provides no
way to create one.

---

## Why each step could not be authored

| Step | Method | Transformation entries wrapping it | Authorable? |
|---|---|---|---|
| 2 — best overall response | `M.RecordSelection` | `T.BaselineSelection` only, fixed at `last_non_missing` / `pre_treatment` | **No** |
| 3 — SD qualifies at ≥8 weeks | `M.ThresholdCompare` | `T.ADAS_ScoreableCheck` only, fixed at *"≥ 8 of 11 items"* | **No** |
| 7 — `RSPFL` ← CBOR ∈ {CR, PR} | `M.Categorization` | **none** | **No** |
| 8 — per-arm proportion, Clopper–Pearson CI | `M.Proportion` | **none** | **No** |
| 9 — Wilson CI sensitivity | `M.Proportion` | **none** | **No** |
| 10 — stratified CMH | `M.CMH` | **none** | **No** |

Three of the six methods have no transformation at all. The other two have exactly one entry
each, configured for a different purpose.

### The configurations are not editable

The obvious workaround is to take `T.BaselineSelection` — the one `M.RecordSelection` entry —
and change `selection_rule` from `last_non_missing` to `best`, and `scope` from `pre_treatment`
to `post_baseline`. That would be semantic abuse, since the entry would keep the oid
`T.BaselineSelection` and the description *"Identify the baseline record per subject per
parameter"* while computing best overall response. It is also **not possible**:

- In the derivation pipeline (step 6), the selected-derivation panel shows Name, OID, Method,
  Output, Description and Bindings. There is no configuration editor. The strings
  `selection_rule`, `last_non_missing`, `post_baseline` and `pre_treatment` appear nowhere in
  the rendered page.
- Step 4 (Analysis) *does* render method configurations — `endpoint-how.js` builds them from
  `getMethodConfigurations` with `methodConfigOverrides` — but only for the **analysis**
  transformation. With `T.Responder_ChiSq` selected, the single configuration offered is the
  chi-squared continuity correction (`none` / `yates`). The derivation's configurations are not
  exposed there either.

So a shipped transformation's method configuration is fixed at authoring time.

### And no transformation can be created

`ac-dc-app` loads `ACDC_Transformation_Library_v06.json` read-only via `data-loader.js:56` and
never writes to it. There is no create, add, or new-transformation affordance anywhere in
`ac-dc-app/js/`. An author can select from the 25 shipped transformations and nothing else.

---

## What *was* authored, and why it is worth keeping

The only chain the builder will produce for an ORR-shaped endpoint:

```
Responder Analysis Chi-Square  (T.Responder_ChiSq / M.ChiSquaredTest)
  └── AVALC/xxxFL (Flag)  —  response  —  (raw), source data
      TRTA/TRTP (Treatment) — fixed_effect
      USUBJID (Subject) — partition
      Observation.Identification.Topic — constraint
      VISIT/VISITNUM (Visit) — constraint
```

`derivationChain: []`. `selectedDerivations: {}`. Five terminals confirmed, **zero derivations**.

The responder flag — the entire substance of ORR, the thing SAP §4.3 spends a paragraph
defining — is declared as source data that arrives already computed.

And the analysis is one the SAP does not ask for. SAP §5.3 specifies a stratified CMH test, a
Mantel–Haenszel risk difference and Clopper–Pearson per-arm proportions. What was authored is
an unstratified chi-squared test, because it is the only responder analysis in the library
([F08](../../docs/findings/F08-no-risk-difference.md)).

This is kept because it is the honest answer to *"what would actually happen?"*: an author
following the builder to completion on ORR produces a valid, complete-looking artefact that
declares away the derivation and answers a different statistical question.

---

## Decision points

Seven. Far fewer than the lab tier's eleven — not because ORR is simpler, but because there
was almost nothing to decide.

| # | Decision | Options | Chosen | Determined by the SAP? |
|---|---|---|---|---|
| D1 | Study | 1 selectable | CDISC Pilot | n/a — TORIVA not loadable |
| D2 | Endpoint | 11 | END6, as an ORR-shaped stand-in | n/a — the Pilot has no response-rate endpoint |
| D3 | Concept category | 29 | `Flag (Classification)` | **no** |
| D4 | Data type | 6 | `Quantity` (default, left) | **no** — see L2 |
| D5 | Analysis template | 2 | `Responder Analysis Chi-Square` | **no** — the SAP asks for CMH |
| D6 | Resolve the responder flag | 2 templates + `(raw)` | `(raw)` | **no** — neither template is a responder flag |
| D7–D9 | Confirm Treatment / Topic / Visit terminals | confirm | confirmed | yes |

**Five of seven decisions are not determined by the SAP**, against four of eleven on the lab
tier. The proportion is worse, and the reason is that the SAP's actual requirements had no
representation to choose.

---

## Where it strained

### L1 — the builder offered a log-rank test for a responder endpoint

With concept category `Flag (Classification)`, step 4 offered two analysis templates:
**Overall Survival Log-Rank Test** and **Responder Analysis Chi-Square**. The first is offered
because `T.OS_LogRank` binds its `event` role to concept `Flag`, and matching is by concept
string.

This is the incidental recorded in
[F12](../../docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md) — *"every
`Flag` is interchangeable"* — appearing in the shipped UI on a second, independent path. F12
predicted it from the library; here it was observed.

### L2 — `dataType` stayed `Quantity` for a `Flag` endpoint

Selecting concept category `Flag (Classification)` left the data-type selector at its default
`Quantity`, and the chain completed and serialised that way. `chain.json` records
`"conceptCategory":"Flag","dataType":"Quantity"` while the resolved binding for the same slot
carries `"requiredValueType":"CodeableConcept"`. Nothing reconciled or flagged the two.

Not pursued — it does not block anything — but a responder flag typed as a quantity is the kind
of thing a conformance check should catch, and none did.

### L3 — Baseline Selection was offered, and accepted, as the responder flag

Before settling on `(raw)`, `Baseline Selection` was attached to the `response` slot. The
builder accepted it without warning, rendered the tree as resolved (`✓`), and would have
serialised it. A chain claiming to compute a responder rate from
*"the baseline record per subject per parameter"* is well-formed as far as the model is
concerned.

It was removed before serialising. That it was possible is the finding.

### L4 — the paper mapping's recommendation was wrong, and the mapping could not have known

The ORR mapping's closing recommendation reads: *"Author steps 2, 3, 7, 8 and 9 against the ITT
denominator — which is what exists (D4, D7) — and record the time."*

None of those five is authorable. The mapping was correct that the **methods** compose and
wrong to infer that the **chain** could therefore be built, because step 1 works from the method
and transformation libraries while step 2 works from what the builder exposes. That gap between
the two is now the clearest argument for the method's insistence that both steps happen.

---

## What this tier cost

**Zero authoring, zero derivations, seven decisions, five of them unguided — and an artefact
that answers a different question from the estimand.**

## What it says about scale

The lab tier suggested the mechanical cost is low and the risk is silent incorrectness (L4
there). ORR sharpens that: for anything beyond the three or four derivations the library
happens to ship, the mechanical cost is not low or high — **the work cannot be started**.

The specification's §6.1 question — whether ten to fifty endpoints can go through this —
does not reach a cost answer on this tier. The answer is that one endpoint of the three
attempted can be authored as specified, and that one is wrong by a median 21% on its baseline
(see [`../01-simple-lab-cfb/comparison.md`](../01-simple-lab-cfb/comparison.md)).

Steps 3 and 4 of the method are **not** attempted for ORR. There is no derivation to compare
against built ADaM, so a `comparison.md` would have nothing in it that
[`mapping.md`](mapping.md) and this log do not already record.
