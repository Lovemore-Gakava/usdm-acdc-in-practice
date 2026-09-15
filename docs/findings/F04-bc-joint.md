# F04 — The BC joint is annotated, not resolved

**Status: retired.** The claim does not hold at `739344c`. It is resolved.

## What was originally claimed

> In the upstream worked scenario, `linkedBCIds` is empty and the connection to Biomedical
> Concepts exists only as prose in `note` fields. Everything above that joint is
> machine-traceable; the last hop is not.

## What is actually true

In the worked derivation scenario
(`ac-dc-app/data/study_ac_spec/Scenario 2_cdisc-pilot-lzzt-merged.study-instance-adas-cog-with-derivation.json`),
every terminal that should carry a BC link does:

| # | `concept` | `roleLabel` | `linkedBCIds` |
|---|---|---|---|
| 0 | Subject | dimension | — |
| 1 | Parameter | dimension | — |
| 2 | Treatment | dimension | — |
| 3 | Visit | dimension | — |
| 4 | **Measure** | measure | **11 ids** |
| 5 | **Measure** | measure | **11 ids** |
| 6 | **Measure** | measure | **11 ids** |
| 7 | **Measure** | measure | **11 ids** |
| 8 | **Measure** | measure | **11 ids** |

The eleven ids (`BiomedicalConcept_315`, `_316`, `_318`, …) are the eleven ADAS-Cog items.
The four terminals with no BC link are **dimensions** — Subject, Parameter, Treatment, Visit —
which are structural and have no biomedical concept to link to. That is correct, not missing.

Scenario 3 (`unit_conversion_mean`) likewise resolves its measure terminals
(`BiomedicalConcept_23`, `BiomedicalConcept_5`). Only Scenario 1, which is analysis-only
and has no derivation chain, has none.

The mechanism is fully implemented in the application, not merely declared: the derivation
pipeline writes to it (`js/views/derivation-pipeline.js:1430-1434`), the USDM parser resolves
BC names through it (`js/utils/usdm-parser.js:289-291, 349-351, 435-437`), and the phrase
engine gates a `hasLinkedBCs` predicate on it (`js/utils/phrase-engine.js:81`).

## Where the original claim came from

The endpoint-level `linkedBCIds` **is** `[]` in Scenario 2:

```
/endpointSpecs/Endpoint_1                       linkedBCIds: []
/endpointSpecs/Endpoint_1/confirmedTerminals[4] linkedBCIds: [11 ids]
```

Reading only the endpoint level gives the original conclusion. BC linkage is attached at
terminal level — the leaves of the derivation chain, where it belongs, since an endpoint
with nine derivation steps has no single BC.

Separately, `note` fields do carry prose (see [F03](F03-chain-position-carries-meaning.md)),
which is a real problem — but it is about transformation provenance, not the BC joint.

## Disposition

Retired. Not filed upstream. F03 carries the surviving part of the concern.
